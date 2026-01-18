# Phase 10: Material ID Prediction Model Training - Research

**Researched:** 2026-01-18
**Domain:** Multi-label classification, quantity regression, scikit-learn ML
**Confidence:** HIGH

## Summary

This phase involves building a multi-label classification model to predict which material IDs appear in a roofing quote, followed by per-material quantity regressors. The research confirms scikit-learn's `OneVsRestClassifier` with `MultiLabelBinarizer` is the standard approach for the multi-label ID selection problem, while `MultiOutputRegressor` or individual regressors per material handle quantity prediction.

Key findings from data analysis:
- **Zero overlap** in top 20 materials between Bardeaux and Elastomere categories - job_category is the strongest feature
- **62% of materials are rare** (< 10 uses) - must filter these from training or handle with fallback rules
- **495 strong co-occurrence rules** with P(Y|X) > 0.7 - valuable for post-processing
- **82 chimney-triggered materials** and **54 skylight-triggered materials** identified

**Primary recommendation:** Use scikit-learn's `OneVsRestClassifier` with `RandomForestClassifier` (class_weight='balanced') as base estimator for material ID selection. Train quantity regressors only for materials with >= 50 samples. Use co-occurrence rules and feature triggers as post-processing boosters.

## Standard Stack

The established libraries/tools for this domain:

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| scikit-learn | 1.8.x | Multi-label classification, regression | De facto ML standard, matches existing codebase |
| joblib | 1.3.x | Model serialization | scikit-learn's recommended persistence |
| numpy | 1.24.x | Numerical operations | Already in codebase |
| pandas | 2.x | Data manipulation | Already in codebase |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| scipy | 1.11.x | Sparse matrices | If memory optimization needed for binarizer |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| OneVsRestClassifier | ClassifierChain | ClassifierChain captures label correlations but adds complexity; co-occurrence rules achieve similar effect simpler |
| RandomForest base | GradientBoosting base | GB may be slightly more accurate but slower; RF is more parallelizable |
| Individual regressors | MultiOutputRegressor | MultiOutputRegressor is cleaner API but individual gives more control |

**Installation:**
```bash
pip install scikit-learn==1.8.0 joblib==1.3.2 numpy pandas
```

## Architecture Patterns

### Recommended Project Structure
```
backend/app/
├── services/
│   ├── material_predictor.py    # Main prediction service (like predictor.py)
│   └── material_trainer.py      # Training script (run offline)
├── models/
│   ├── material_selector.pkl    # MultiLabelBinarizer + OneVsRestClassifier
│   ├── quantity_regressors.pkl  # Dict of {material_id: regressor}
│   ├── cooccurrence_rules.json  # P(Y|X) > 0.7 rules
│   └── feature_triggers.json    # Chimney/skylight material mappings
├── routers/
│   └── estimate.py              # Add /estimate/materials endpoint
└── schemas/
    └── materials.py             # MaterialPredictionRequest/Response
```

### Pattern 1: Multi-Label Classification with OneVsRestClassifier
**What:** Transforms multi-label problem into N independent binary classifiers
**When to use:** When labels are largely independent (category separation validates this)
**Example:**
```python
# Source: https://scikit-learn.org/stable/modules/multiclass.html
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.multiclass import OneVsRestClassifier
from sklearn.ensemble import RandomForestClassifier

# Transform labels to binary indicator matrix
mlb = MultiLabelBinarizer()
y_binary = mlb.fit_transform(material_ids_list)  # shape: (n_samples, n_classes)

# Train one classifier per label
clf = OneVsRestClassifier(
    RandomForestClassifier(
        n_estimators=100,
        class_weight='balanced',  # Handle imbalance
        random_state=42,
        n_jobs=-1
    )
)
clf.fit(X, y_binary)

# Predict probabilities, threshold for selection
probs = clf.predict_proba(X_test)
predictions = (probs > 0.3).astype(int)  # Tune threshold per-class
material_ids = mlb.inverse_transform(predictions)
```

### Pattern 2: Per-Material Quantity Regressors
**What:** Train separate regressor for each material to predict quantity
**When to use:** When materials have different quantity distributions (confirmed: some have mean=1, others mean=50+)
**Example:**
```python
# Source: Existing codebase pattern from train_cortex_v4.py
from sklearn.ensemble import GradientBoostingRegressor
import joblib

quantity_models = {}
for material_id in materials_with_enough_samples:
    # Filter training data for this material
    mask = y_binary[:, material_id_idx] == 1
    X_mat = X[mask]
    y_qty = quantities[mask, material_id_idx]

    if len(X_mat) >= 50:  # Minimum samples threshold
        model = GradientBoostingRegressor(
            n_estimators=100,
            max_depth=4,
            learning_rate=0.1,
            random_state=42
        )
        model.fit(X_mat, y_qty)
        quantity_models[material_id] = model

joblib.dump(quantity_models, 'quantity_regressors.pkl')
```

### Pattern 3: Lazy Loading Service (Follows Existing Predictor Pattern)
**What:** Load models on first use, not at startup
**When to use:** Railway deployment with memory constraints
**Example:**
```python
# Source: backend/app/services/predictor.py
import gc
from pathlib import Path
import joblib

_models: dict = {}
_loaded: bool = False
MODEL_DIR = Path(__file__).parent.parent / "models"

def _ensure_models_loaded() -> None:
    global _loaded
    if _loaded:
        return

    _models["selector"] = joblib.load(MODEL_DIR / "material_selector.pkl")
    _models["binarizer"] = joblib.load(MODEL_DIR / "material_binarizer.pkl")
    _models["quantity"] = joblib.load(MODEL_DIR / "quantity_regressors.pkl")

    with open(MODEL_DIR / "cooccurrence_rules.json") as f:
        _models["rules"] = json.load(f)

    gc.collect()
    _loaded = True
```

### Pattern 4: Co-occurrence Rule Post-Processing
**What:** Boost predictions using association rules
**When to use:** When strong material pairs exist (495 rules with P(Y|X) > 0.7 found)
**Example:**
```python
def apply_cooccurrence_rules(predicted_ids: list, rules: dict, threshold=0.7):
    """Add materials that co-occur with predicted ones."""
    boosted = set(predicted_ids)
    for rule in rules:
        if rule['antecedent'] in boosted and rule['confidence'] >= threshold:
            boosted.add(rule['consequent'])
    return list(boosted)
```

### Anti-Patterns to Avoid
- **Training on rare classes:** Don't train classifiers for materials with < 10 samples - use fallback rules instead
- **Single global threshold:** Don't use 0.5 for all classes - tune per-class thresholds on validation set
- **Ignoring category:** Don't train single model - category has 100% coverage and zero top-20 overlap between Bardeaux/Elastomere
- **Loading all models at startup:** Follow existing lazy loading pattern to avoid Railway memory issues

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Multi-label encoding | Custom binary matrix | MultiLabelBinarizer | Handles inverse transform, sparse support |
| Binary classifier per label | Manual loops | OneVsRestClassifier | Parallel training, clean API |
| Class imbalance | Manual SMOTE | class_weight='balanced' | Built into RF/GB, no data augmentation needed |
| Model persistence | Custom pickle | joblib.dump/load | Optimized for numpy arrays, memory mapping |
| F1 micro calculation | Manual precision/recall | f1_score(average='micro') | Handles edge cases, zero_division param |
| Feature encoding | Manual one-hot | LabelEncoder (already in codebase) | Consistent with existing train_cortex_v4.py |

**Key insight:** scikit-learn provides complete multi-label classification infrastructure. The main custom work is: (1) filtering rare classes, (2) co-occurrence rule extraction, (3) feature trigger mapping.

## Common Pitfalls

### Pitfall 1: Training on All 849 Materials
**What goes wrong:** Model tries to learn rare materials (62% have < 10 samples), leading to poor generalization
**Why it happens:** Intuition says "more classes = better coverage"
**How to avoid:** Filter to materials with >= 50 samples for reliable training (this covers 143 materials with 8.1% coverage). Use co-occurrence rules for the rest.
**Warning signs:** Very low per-class F1 scores, model predicts only common materials

### Pitfall 2: Using 0.5 Threshold for All Classes
**What goes wrong:** Imbalanced classes need different thresholds - rare materials need lower threshold to be predicted
**Why it happens:** Default behavior of predict() uses 0.5
**How to avoid:** Use predict_proba() and tune threshold per class using validation set
**Warning signs:** Precision-recall tradeoff very uneven across classes

### Pitfall 3: Evaluating with Macro F1 Only
**What goes wrong:** Macro F1 weights all classes equally, making rare class performance dominate
**Why it happens:** Macro seems "fairer" than micro
**How to avoid:** Use micro F1 as primary metric (requirement: >= 70%), macro as secondary diagnostic
**Warning signs:** Micro and macro F1 differ significantly (indicates class imbalance issues)

### Pitfall 4: Ignoring Zero Quantities
**What goes wrong:** Data has some quantity=0 entries, MAPE blows up
**Why it happens:** MAPE divides by true value
**How to avoid:** Filter out zero quantities from regression training, or use MAE for those
**Warning signs:** MAPE is extremely high or inf

### Pitfall 5: Single Model for All Categories
**What goes wrong:** Model struggles because Bardeaux and Elastomere have zero overlap in top 20 materials
**Why it happens:** Assumption that one model fits all
**How to avoid:** Either (a) use category as strong feature, or (b) train separate models per category
**Warning signs:** Predictions include wrong-category materials

### Pitfall 6: Memory Issues on Railway
**What goes wrong:** All models loaded at startup exhaust Railway's memory
**Why it happens:** Eager loading pattern
**How to avoid:** Follow existing lazy loading pattern in predictor.py - load on first request
**Warning signs:** Deployment crashes, OOM errors

## Code Examples

Verified patterns from official sources and existing codebase:

### Feature Preparation
```python
# Consistent with existing codebase
def prepare_features(sample: dict) -> np.ndarray:
    """Extract features from training sample."""
    f = sample['features']
    return np.array([
        f.get('sqft', 0),
        f.get('complexity_score', 10),
        f.get('quoted_total', 0),
        1 if f.get('has_chimney') else 0,
        1 if f.get('has_skylights') else 0,
        f.get('material_lines', 5),
        f.get('labor_lines', 2),
        1 if f.get('has_subs') else 0,
        # Category encoded (already in codebase)
    ])
```

### Multi-Label F1 Calculation
```python
# Source: https://scikit-learn.org/stable/modules/generated/sklearn.metrics.f1_score.html
from sklearn.metrics import f1_score

# Micro F1 (requirement: >= 70%)
f1_micro = f1_score(y_true, y_pred, average='micro')

# Macro F1 (diagnostic)
f1_macro = f1_score(y_true, y_pred, average='macro')

# Per-class F1 (for debugging)
f1_per_class = f1_score(y_true, y_pred, average=None)
```

### MAPE Calculation
```python
# Source: https://scikit-learn.org/stable/modules/generated/sklearn.metrics.mean_absolute_percentage_error.html
from sklearn.metrics import mean_absolute_percentage_error

# Note: sklearn returns 0-1 range, multiply by 100 for percentage
mape = mean_absolute_percentage_error(y_true, y_pred) * 100
# Requirement: <= 30% for top 20 materials
```

### Co-occurrence Rule Extraction
```python
def extract_cooccurrence_rules(data: list, min_support=50, min_confidence=0.7):
    """Extract P(Y|X) > threshold rules."""
    from collections import Counter, defaultdict

    material_counts = Counter()
    cooccur = defaultdict(Counter)

    for sample in data:
        mats = list(set([m['material_id'] for m in sample['materials']]))
        material_counts.update(mats)
        for m1 in mats:
            for m2 in mats:
                if m1 != m2:
                    cooccur[m1][m2] += 1

    rules = []
    for m1, peers in cooccur.items():
        if material_counts[m1] < min_support:
            continue
        for m2, count in peers.items():
            confidence = count / material_counts[m1]
            if confidence >= min_confidence:
                rules.append({
                    'antecedent': m1,
                    'consequent': m2,
                    'confidence': round(confidence, 3),
                    'support': count
                })
    return rules
```

### FastAPI Endpoint Pattern
```python
# Source: backend/app/routers/estimate.py (existing pattern)
from fastapi import APIRouter, HTTPException
from app.services.material_predictor import predict_materials

router = APIRouter(tags=["estimate"])

@router.post("/estimate/materials")
def predict_materials_endpoint(request: MaterialEstimateRequest):
    """Predict material IDs and quantities for roofing job."""
    try:
        result = predict_materials(
            job_category=request.category,
            sqft=request.sqft,
            complexity=request.complexity,
            has_chimney=request.has_chimney,
            has_skylights=request.has_skylights,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Train all 849 classes | Filter to 50+ sample classes | Analysis finding | Reduces noise, improves F1 |
| Single threshold 0.5 | Per-class threshold tuning | Best practice | Better precision-recall balance |
| Global model | Category-aware (feature or split) | Data analysis | Zero overlap means category is critical |
| Eager model loading | Lazy loading | Existing codebase pattern | Railway memory compatibility |

**Deprecated/outdated:**
- MLSMOTE for multi-label oversampling: class_weight='balanced' in RandomForest is simpler and effective
- Hand-rolled co-occurrence: scipy or existing Counter-based extraction works well

## Open Questions

Things that couldn't be fully resolved:

1. **Optimal minimum sample threshold for quantity regressors**
   - What we know: 50+ samples gives reasonable regression accuracy
   - What's unclear: Whether 30 or 100 would be better
   - Recommendation: Start with 50, evaluate MAPE, adjust if needed

2. **Category-split vs category-feature approach**
   - What we know: Zero top-20 overlap suggests separation
   - What's unclear: Whether single model with category feature matches split model performance
   - Recommendation: Try category as feature first (simpler), split only if needed

3. **Threshold tuning strategy**
   - What we know: Per-class thresholds beat global 0.5
   - What's unclear: Best optimization target (F1? precision at fixed recall?)
   - Recommendation: Optimize for micro F1 >= 70% requirement

## Sources

### Primary (HIGH confidence)
- [scikit-learn 1.8.0 Multiclass/Multioutput docs](https://scikit-learn.org/stable/modules/multiclass.html) - OneVsRestClassifier, ClassifierChain, MultiOutputRegressor
- [scikit-learn Model Persistence](https://scikit-learn.org/stable/model_persistence.html) - joblib patterns, security notes
- [f1_score documentation](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.f1_score.html) - micro/macro averaging
- [mean_absolute_percentage_error](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.mean_absolute_percentage_error.html) - MAPE calculation

### Secondary (MEDIUM confidence)
- [Micro, Macro & Weighted Averages of F1 Score](https://towardsdatascience.com/micro-macro-weighted-averages-of-f1-score-clearly-explained-b603420b292f/) - Explanation of averaging methods
- [Multilabel classification using classifier chain](https://scikit-learn.org/stable/auto_examples/multioutput/plot_classifier_chain_yeast.html) - ClassifierChain example
- [RandomForestClassifier class_weight](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestClassifier.html) - balanced/balanced_subsample options

### Tertiary (LOW confidence)
- WebSearch results on multi-label imbalance - verified with official docs

### Codebase References (HIGH confidence)
- `/Users/aymanbaig/Desktop/Toiture-P1/backend/app/services/predictor.py` - Lazy loading pattern to follow
- `/Users/aymanbaig/Desktop/Toiture-P1/cortex-data/train_cortex_v4.py` - Training script patterns
- `/Users/aymanbaig/Desktop/Toiture-P1/cortex-data/material_training_data.json` - Training data (7,433 samples)

## Data Analysis Summary

Findings from analyzing `/Users/aymanbaig/Desktop/Toiture-P1/cortex-data/material_training_data.json`:

| Metric | Value |
|--------|-------|
| Total samples | 7,433 |
| Unique material IDs | 849 |
| Avg materials per quote | 9.8 |
| Materials with < 10 uses | 526 (62.0%) |
| Materials with 50+ uses | 143 (16.8%) |
| Top 20 Bardeaux/Elastomere overlap | 0 (zero!) |
| Quotes with chimney | 2,329 (31.3%) |
| Quotes with skylights | 1,959 (26.4%) |
| Strong co-occurrence rules (P > 0.7) | 495 |
| Chimney-triggered materials | 82 |
| Skylight-triggered materials | 54 |

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - scikit-learn patterns verified with official docs
- Architecture: HIGH - follows existing codebase patterns exactly
- Pitfalls: HIGH - derived from data analysis + official documentation
- Data analysis: HIGH - direct analysis of training data

**Research date:** 2026-01-18
**Valid until:** 2026-02-18 (30 days - stable scikit-learn ecosystem)
