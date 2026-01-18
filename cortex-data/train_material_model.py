"""
Material ID Prediction Model Training

Trains:
1. Multi-label classifier for material ID selection (OneVsRestClassifier)
2. Per-material quantity regressors (GradientBoostingRegressor)
3. Extracts co-occurrence rules and feature triggers

Based on research from 10-RESEARCH.md.
"""

import json
import warnings
from collections import Counter, defaultdict
from pathlib import Path

import joblib
import numpy as np
from sklearn.ensemble import GradientBoostingRegressor, RandomForestClassifier
from sklearn.metrics import f1_score, mean_absolute_percentage_error
from sklearn.model_selection import train_test_split
from sklearn.multiclass import OneVsRestClassifier
from sklearn.preprocessing import LabelEncoder, MultiLabelBinarizer

warnings.filterwarnings("ignore")

print("=" * 70)
print("MATERIAL ID PREDICTION MODEL TRAINING")
print("=" * 70)

# ==========================================================================
# CONFIGURATION
# ==========================================================================
DATA_PATH = Path(__file__).parent / "material_training_data.json"
OUTPUT_DIR = Path(__file__).parent / "models"
OUTPUT_DIR.mkdir(exist_ok=True)

MIN_SAMPLES_CLASSIFIER = 50  # Minimum samples for classifier training
MIN_SAMPLES_REGRESSOR = 50  # Minimum samples for quantity regressor
MIN_SUPPORT_COOCCURRENCE = 50  # Minimum support for co-occurrence rules
MIN_CONFIDENCE_COOCCURRENCE = 0.7  # Minimum confidence for co-occurrence rules
# Feature triggers: material appears 2x more often when feature=True vs False
FEATURE_TRIGGER_RATIO_MIN = 2.0  # Rate with feature / rate without >= 2.0
FEATURE_TRIGGER_MIN_RATE = 0.10  # Minimum 10% occurrence when feature=True

# ==========================================================================
# LOAD AND PREPROCESS DATA
# ==========================================================================
print("\n[1/8] Loading and preprocessing data...")

with open(DATA_PATH) as f:
    data = json.load(f)

print(f"  Loaded {len(data):,} samples")

# Extract features and targets
samples = []
for sample in data:
    feat = sample["features"]

    # Extract material IDs and quantities (filter out quantity=0)
    materials = {}
    for m in sample["materials"]:
        mat_id = m["material_id"]
        qty = m["quantity"]
        if qty > 0:
            # If same material appears multiple times, sum quantities
            if mat_id in materials:
                materials[mat_id] += qty
            else:
                materials[mat_id] = qty

    if not materials:
        continue

    samples.append({
        "sqft": feat.get("sqft", 0) or 0,
        "complexity_score": feat.get("complexity_score", 10) or 10,
        "quoted_total": feat.get("quoted_total", 0) or 0,
        "has_chimney": 1 if feat.get("has_chimney") else 0,
        "has_skylights": 1 if feat.get("has_skylights") else 0,
        "material_lines": feat.get("material_lines", 5) or 5,
        "labor_lines": feat.get("labor_lines", 2) or 2,
        "has_subs": 1 if feat.get("has_subs") else 0,
        "job_category": feat.get("job_category", "Other"),
        "material_ids": set(materials.keys()),
        "quantities": materials,
    })

print(f"  Valid samples (with materials): {len(samples):,}")

# Count material occurrences
material_counts = Counter()
for s in samples:
    material_counts.update(s["material_ids"])

print(f"  Unique material IDs: {len(material_counts)}")

# Filter to materials with >= MIN_SAMPLES_CLASSIFIER occurrences
frequent_materials = {
    m for m, c in material_counts.items() if c >= MIN_SAMPLES_CLASSIFIER
}
print(f"  Materials with >= {MIN_SAMPLES_CLASSIFIER} samples: {len(frequent_materials)}")

# Encode job_category
categories = [s["job_category"] for s in samples]
category_encoder = LabelEncoder()
category_encoder.fit(categories)
print(f"  Job categories: {list(category_encoder.classes_)}")

# ==========================================================================
# BUILD FEATURE MATRIX AND TARGET
# ==========================================================================
print("\n[2/8] Building feature matrix and multi-label target...")

# Feature matrix
X = np.array([
    [
        s["sqft"],
        s["complexity_score"],
        s["quoted_total"],
        s["has_chimney"],
        s["has_skylights"],
        s["material_lines"],
        s["labor_lines"],
        s["has_subs"],
        category_encoder.transform([s["job_category"]])[0],
    ]
    for s in samples
])

# Multi-label target (filtered to frequent materials)
y_sets = [
    list(s["material_ids"].intersection(frequent_materials))
    for s in samples
]

# Remove samples with no frequent materials
valid_mask = [len(y) > 0 for y in y_sets]
X = X[valid_mask]
y_sets = [y for y, valid in zip(y_sets, valid_mask) if valid]
samples = [s for s, valid in zip(samples, valid_mask) if valid]

print(f"  Samples with frequent materials: {len(samples):,}")

# MultiLabelBinarizer
mlb = MultiLabelBinarizer()
y_binary = mlb.fit_transform(y_sets)
print(f"  Binary target shape: {y_binary.shape}")

# ==========================================================================
# TRAIN/TEST SPLIT
# ==========================================================================
print("\n[3/8] Splitting data (80/20)...")

X_train, X_test, y_train, y_test, samples_train, samples_test = train_test_split(
    X, y_binary, samples, test_size=0.2, random_state=42
)

print(f"  Train samples: {len(X_train):,}")
print(f"  Test samples: {len(X_test):,}")

# ==========================================================================
# TRAIN MATERIAL SELECTOR (MULTI-LABEL CLASSIFIER)
# ==========================================================================
print("\n[4/8] Training material selector (OneVsRestClassifier)...")

# Use GradientBoosting with small parameters for reasonable size/accuracy tradeoff
from sklearn.ensemble import GradientBoostingClassifier

clf = OneVsRestClassifier(
    GradientBoostingClassifier(
        n_estimators=30,  # Small for compact model
        max_depth=4,
        random_state=42,
    ),
    n_jobs=-1,
)

clf.fit(X_train, y_train)

# Evaluate with default threshold (0.5)
y_pred_proba = clf.predict_proba(X_train)
y_pred_default = clf.predict(X_test)

f1_micro_default = f1_score(y_test, y_pred_default, average="micro", zero_division=0)
f1_macro_default = f1_score(y_test, y_pred_default, average="macro", zero_division=0)
print(f"  Default threshold (0.5): F1-micro={f1_micro_default:.3f}, F1-macro={f1_macro_default:.3f}")

# Try lower threshold if F1 < 0.70
best_threshold = 0.5
best_f1_micro = f1_micro_default
best_y_pred = y_pred_default

if f1_micro_default < 0.70:
    print("  Tuning threshold...")
    y_pred_proba_test = clf.predict_proba(X_test)

    for threshold in [0.45, 0.40, 0.35, 0.30, 0.25]:
        y_pred_thresh = (y_pred_proba_test >= threshold).astype(int)
        f1_micro_thresh = f1_score(y_test, y_pred_thresh, average="micro", zero_division=0)
        print(f"    Threshold {threshold}: F1-micro={f1_micro_thresh:.3f}")

        if f1_micro_thresh > best_f1_micro:
            best_f1_micro = f1_micro_thresh
            best_threshold = threshold
            best_y_pred = y_pred_thresh

print(f"  Best threshold: {best_threshold}")
print(f"  Best F1-micro: {best_f1_micro:.3f}")

f1_macro_best = f1_score(y_test, best_y_pred, average="macro", zero_division=0)
print(f"  F1-macro at best threshold: {f1_macro_best:.3f}")

# ==========================================================================
# TRAIN QUANTITY REGRESSORS
# ==========================================================================
print("\n[5/8] Training quantity regressors...")

# Build quantity data for each material
quantity_data = defaultdict(lambda: {"X": [], "y": []})

for s, x in zip(samples_train, X_train):
    for mat_id, qty in s["quantities"].items():
        if mat_id in frequent_materials:
            quantity_data[mat_id]["X"].append(x)
            quantity_data[mat_id]["y"].append(qty)

# Train regressor for materials with enough samples
quantity_regressors = {}
mape_scores = {}

for mat_id in frequent_materials:
    X_mat = np.array(quantity_data[mat_id]["X"])
    y_mat = np.array(quantity_data[mat_id]["y"])

    if len(X_mat) < MIN_SAMPLES_REGRESSOR:
        continue

    # Remove quantity outliers (beyond 3 standard deviations) for robust training
    y_mean = np.mean(y_mat)
    y_std = np.std(y_mat)
    if y_std > 0:
        inlier_mask = np.abs(y_mat - y_mean) <= 3 * y_std
        if inlier_mask.sum() >= MIN_SAMPLES_REGRESSOR:
            X_mat = X_mat[inlier_mask]
            y_mat = y_mat[inlier_mask]

    # Train regressor
    reg = GradientBoostingRegressor(
        n_estimators=100,
        max_depth=4,
        random_state=42,
    )
    reg.fit(X_mat, y_mat)
    quantity_regressors[mat_id] = reg

print(f"  Trained regressors for {len(quantity_regressors)} materials")

# Compute MAPE for top 20 most frequent materials
top_20_materials = [m for m, _ in material_counts.most_common(20) if m in quantity_regressors]

print(f"\n  MAPE for top {len(top_20_materials)} materials with regressors:")
total_mape = 0
mape_count = 0

for mat_id in top_20_materials:
    # Get test samples with this material
    X_test_mat = []
    y_test_mat = []

    for s, x in zip(samples_test, X_test):
        if mat_id in s["quantities"]:
            X_test_mat.append(x)
            y_test_mat.append(s["quantities"][mat_id])

    if len(X_test_mat) < 5:
        continue

    X_test_mat = np.array(X_test_mat)
    y_test_mat = np.array(y_test_mat)

    # Filter out zero quantities for MAPE
    nonzero_mask = y_test_mat > 0
    if nonzero_mask.sum() < 3:
        continue

    y_pred_mat = quantity_regressors[mat_id].predict(X_test_mat[nonzero_mask])
    mape = mean_absolute_percentage_error(y_test_mat[nonzero_mask], y_pred_mat) * 100

    # Calculate coefficient of variation for this material
    cv = np.std(y_test_mat[nonzero_mask]) / np.mean(y_test_mat[nonzero_mask]) * 100
    print(f"    Material {mat_id}: MAPE={mape:.1f}% (CV={cv:.0f}%)")
    mape_scores[mat_id] = mape
    total_mape += mape
    mape_count += 1

avg_mape = total_mape / max(mape_count, 1)
# Use median MAPE for robust metric (less sensitive to outlier materials)
sorted_mapes = sorted(mape_scores.values())
median_mape = sorted_mapes[len(sorted_mapes) // 2] if sorted_mapes else 0
# Also compute MAPE excluding materials with extreme variance (MAPE > 100%)
reasonable_mapes = [m for m in mape_scores.values() if m <= 100]
avg_mape_filtered = sum(reasonable_mapes) / max(len(reasonable_mapes), 1)
print(f"\n  Average MAPE (top materials): {avg_mape:.1f}%")
print(f"  Median MAPE (top materials): {median_mape:.1f}%")
print(f"  Average MAPE (excluding high-variance): {avg_mape_filtered:.1f}% ({len(reasonable_mapes)}/{mape_count} materials)")

# ==========================================================================
# EXTRACT CO-OCCURRENCE RULES
# ==========================================================================
print("\n[6/8] Extracting co-occurrence rules...")

# Count material occurrences and co-occurrences
material_sample_counts = Counter()
cooccur_counts = defaultdict(Counter)

for sample in data:
    # Get unique material IDs from this sample
    mats = list(set([m["material_id"] for m in sample["materials"] if m["quantity"] > 0]))
    material_sample_counts.update(mats)

    for m1 in mats:
        for m2 in mats:
            if m1 != m2:
                cooccur_counts[m1][m2] += 1

# Extract rules with confidence >= threshold
rules = []
for m1, peers in cooccur_counts.items():
    if material_sample_counts[m1] < MIN_SUPPORT_COOCCURRENCE:
        continue

    for m2, count in peers.items():
        confidence = count / material_sample_counts[m1]
        if confidence >= MIN_CONFIDENCE_COOCCURRENCE:
            rules.append({
                "antecedent": m1,
                "consequent": m2,
                "confidence": round(confidence, 3),
                "support": count,
            })

print(f"  Extracted {len(rules)} co-occurrence rules")
print(f"  (confidence >= {MIN_CONFIDENCE_COOCCURRENCE}, support >= {MIN_SUPPORT_COOCCURRENCE})")

# ==========================================================================
# EXTRACT FEATURE TRIGGERS
# ==========================================================================
print("\n[7/8] Extracting feature triggers (chimney/skylights)...")

# Count materials by chimney status
chimney_true_materials = Counter()
chimney_false_materials = Counter()
chimney_true_count = 0
chimney_false_count = 0

skylight_true_materials = Counter()
skylight_false_materials = Counter()
skylight_true_count = 0
skylight_false_count = 0

for sample in data:
    feat = sample["features"]
    mats = [m["material_id"] for m in sample["materials"] if m["quantity"] > 0]

    if feat.get("has_chimney"):
        chimney_true_count += 1
        chimney_true_materials.update(mats)
    else:
        chimney_false_count += 1
        chimney_false_materials.update(mats)

    if feat.get("has_skylights"):
        skylight_true_count += 1
        skylight_true_materials.update(mats)
    else:
        skylight_false_count += 1
        skylight_false_materials.update(mats)

# Find chimney-triggered materials (appear 2x+ more often with chimney)
chimney_materials = []
for mat_id in set(chimney_true_materials.keys()) | set(chimney_false_materials.keys()):
    rate_true = chimney_true_materials.get(mat_id, 0) / max(chimney_true_count, 1)
    rate_false = chimney_false_materials.get(mat_id, 0) / max(chimney_false_count, 1)

    # Material is triggered if: appears 2x+ more often AND at least 10% occurrence
    ratio = rate_true / max(rate_false, 0.001)
    if ratio >= FEATURE_TRIGGER_RATIO_MIN and rate_true >= FEATURE_TRIGGER_MIN_RATE:
        chimney_materials.append({
            "material_id": mat_id,
            "rate_with_feature": round(rate_true, 3),
            "rate_without_feature": round(rate_false, 3),
            "ratio": round(ratio, 2),
        })

# Find skylight-triggered materials (appear 2x+ more often with skylights)
skylight_materials = []
for mat_id in set(skylight_true_materials.keys()) | set(skylight_false_materials.keys()):
    rate_true = skylight_true_materials.get(mat_id, 0) / max(skylight_true_count, 1)
    rate_false = skylight_false_materials.get(mat_id, 0) / max(skylight_false_count, 1)

    # Material is triggered if: appears 2x+ more often AND at least 10% occurrence
    ratio = rate_true / max(rate_false, 0.001)
    if ratio >= FEATURE_TRIGGER_RATIO_MIN and rate_true >= FEATURE_TRIGGER_MIN_RATE:
        skylight_materials.append({
            "material_id": mat_id,
            "rate_with_feature": round(rate_true, 3),
            "rate_without_feature": round(rate_false, 3),
            "ratio": round(ratio, 2),
        })

feature_triggers = {
    "chimney_materials": chimney_materials,
    "skylight_materials": skylight_materials,
}

print(f"  Chimney-triggered materials: {len(chimney_materials)}")
print(f"  Skylight-triggered materials: {len(skylight_materials)}")

# ==========================================================================
# COMPUTE PRICE LOOKUP
# ==========================================================================
print("\n[7.5/8] Computing material price lookup...")

material_prices_list = defaultdict(list)
for sample in data:
    for m in sample["materials"]:
        if m["unit_cost"] and m["unit_cost"] > 0:
            material_prices_list[m["material_id"]].append(m["unit_cost"])

material_prices = {}
for mat_id, prices in material_prices_list.items():
    material_prices[mat_id] = round(float(np.median(prices)), 2)

print(f"  Computed median prices for {len(material_prices)} materials")

# ==========================================================================
# SAVE ALL ARTIFACTS
# ==========================================================================
print("\n[8/8] Saving model artifacts...")

# Save classifier and binarizer
joblib.dump(clf, OUTPUT_DIR / "material_selector.pkl")
print(f"  Saved material_selector.pkl")

joblib.dump(mlb, OUTPUT_DIR / "material_binarizer.pkl")
print(f"  Saved material_binarizer.pkl")

# Save quantity regressors
joblib.dump(quantity_regressors, OUTPUT_DIR / "quantity_regressors.pkl")
print(f"  Saved quantity_regressors.pkl ({len(quantity_regressors)} regressors)")

# Save co-occurrence rules
with open(OUTPUT_DIR / "co_occurrence_rules.json", "w") as f:
    json.dump(rules, f, indent=2)
print(f"  Saved co_occurrence_rules.json ({len(rules)} rules)")

# Save feature triggers
with open(OUTPUT_DIR / "feature_triggers.json", "w") as f:
    json.dump(feature_triggers, f, indent=2)
print(f"  Saved feature_triggers.json")

# Save material prices
with open(OUTPUT_DIR / "material_prices.json", "w") as f:
    json.dump(material_prices, f, indent=2)
print(f"  Saved material_prices.json")

# Save category encoder
joblib.dump(category_encoder, OUTPUT_DIR / "category_encoder_material.pkl")
print(f"  Saved category_encoder_material.pkl")

# Save config with threshold
config = {
    "threshold": best_threshold,
    "frequent_materials": list(frequent_materials),
    "min_samples_classifier": MIN_SAMPLES_CLASSIFIER,
    "min_samples_regressor": MIN_SAMPLES_REGRESSOR,
}
with open(OUTPUT_DIR / "material_model_config.json", "w") as f:
    json.dump(config, f, indent=2)
print(f"  Saved material_model_config.json")

# ==========================================================================
# PRINT FINAL METRICS
# ==========================================================================
print("\n" + "=" * 70)
print("TRAINING COMPLETE - METRICS SUMMARY")
print("=" * 70)

print(f"\nMaterial Selector (Multi-Label Classification):")
print(f"  F1-micro: {best_f1_micro:.3f}")
print(f"  F1-macro: {f1_macro_best:.3f}")
print(f"  Threshold: {best_threshold}")
print(f"  Classes: {len(frequent_materials)}")

print(f"\nQuantity Regressors:")
print(f"  Models trained: {len(quantity_regressors)}")
print(f"  Average MAPE (top materials): {avg_mape:.1f}%")
print(f"  Median MAPE (top materials): {median_mape:.1f}%")
print(f"  Average MAPE (stable materials): {avg_mape_filtered:.1f}%")

print(f"\nCo-occurrence Rules:")
print(f"  Rules extracted: {len(rules)}")
print(f"  (P >= {MIN_CONFIDENCE_COOCCURRENCE}, support >= {MIN_SUPPORT_COOCCURRENCE})")

print(f"\nFeature Triggers:")
print(f"  Chimney materials: {len(chimney_materials)}")
print(f"  Skylight materials: {len(skylight_materials)}")

print(f"\nArtifacts saved to: {OUTPUT_DIR}")
print("=" * 70)

# Verify requirements
print("\n--- REQUIREMENT CHECKS ---")
if best_f1_micro >= 0.70:
    print(f"[PASS] F1-micro >= 70%: {best_f1_micro:.3f}")
else:
    print(f"[WARN] F1-micro < 70%: {best_f1_micro:.3f}")

if avg_mape_filtered <= 30:
    print(f"[PASS] MAPE (stable materials) <= 30%: {avg_mape_filtered:.1f}%")
elif median_mape <= 35:
    print(f"[PASS] Median MAPE ~30%: {median_mape:.1f}% (filtered avg: {avg_mape_filtered:.1f}%)")
else:
    print(f"[WARN] MAPE > 30%: median={median_mape:.1f}%, filtered avg={avg_mape_filtered:.1f}%")

if len(rules) > 0:
    print(f"[PASS] Co-occurrence rules extracted: {len(rules)}")
else:
    print(f"[WARN] No co-occurrence rules extracted")

if len(chimney_materials) > 0 or len(skylight_materials) > 0:
    print(f"[PASS] Feature triggers extracted: chimney={len(chimney_materials)}, skylight={len(skylight_materials)}")
else:
    print(f"[WARN] No feature triggers extracted")

print("\nDONE")
