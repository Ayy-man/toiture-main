# Testing Patterns

**Analysis Date:** 2026-01-18

## Test Framework

**Runner:**
- No formal test framework detected
- No `pytest`, `unittest`, or other test runner configuration
- No `tests/` directory in current codebase

**Assertion Library:**
- Not applicable (no formal tests)

**Run Commands:**
```bash
# No test commands available
# Scripts are validated manually via execution
python3 cortex-data/train_cortex_v4.py
python3 cortex-data/predict_final.py 1500 Bardeaux
```

## Test File Organization

**Location:**
- No test files present
- Validation done inline within scripts

**Naming:**
- No test naming convention established

**Structure:**
- No formal test structure

## Current Validation Approach

**Manual Validation Pattern:**
Scripts include inline validation via print statements and visual inspection.

```python
# From train_cortex.py - inline validation
pct = (np.abs(residuals) / y_test.values <= 0.20).mean() * 100
print(f"Within +-20%: {pct:.0f}%")
print("\nTest: python3 predict_cortex.py 1500 Bardeaux")
```

**Cross-Validation in ML:**
```python
# From train_cortex_v4.py
from sklearn.model_selection import cross_val_score, GridSearchCV

scores = cross_val_score(model, X, y, cv=5, scoring='r2')
print(f"CV R²: {scores.mean():.3f}")
```

## Model Validation Patterns

**Train/Test Split:**
```python
from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)
```

**Metrics Evaluation:**
```python
from sklearn.metrics import mean_absolute_error, r2_score, mean_absolute_percentage_error

r2 = r2_score(y_test, pred)
mae = mean_absolute_error(y_test, pred)
mape = mean_absolute_percentage_error(y_test, pred) * 100
pct20 = (np.abs(pred - y_test) / y_test <= 0.20).mean() * 100
```

**Grid Search Validation:**
```python
from sklearn.model_selection import GridSearchCV

grid_search = GridSearchCV(
    GradientBoostingRegressor(random_state=42),
    param_grid,
    cv=5,
    scoring='r2',
    n_jobs=-1
)
grid_search.fit(X_train, y_train)
print(f"Best CV R²: {grid_search.best_score_:.3f}")
```

## Data Validation Patterns

**Input Validation:**
```python
# Range validation via filtering
model_df = df[
    (df['sqft_final'].notna()) &
    (df['sqft_final'] > 100) &
    (df['sqft_final'] < max_sqft) &
    (df['price_norm'] > 1000) &
    (df['price_norm'] < max_price)
].copy()
```

**Data Quality Checks:**
```python
# From validate_clients.py
print(f"Total quotes: {len(master):,}")
print(f"Unique client_ids: {master['client_id'].nunique():,}")

# Relationship checks
projects_per_client = master.groupby('client_id')['project_id'].nunique()
print(f"Projects per client - Min: {projects_per_client.min()}, Max: {projects_per_client.max()}")
```

**Anomaly Detection:**
```python
# From master_data_pipeline_v4.py
def flag_anomalies(row):
    flags = []
    if row['quoted_total'] < 100:
        flags.append('suspiciously_low')
    if row['overall_margin_pct'] < 0:
        flags.append('negative_margin')
    return '|'.join(flags) if flags else None
```

## Mocking

**Framework:** Not used

**Patterns:** Not applicable

**What to Mock:** Not defined

**What NOT to Mock:** Not defined

## Fixtures and Factories

**Test Data:**
- Real data used directly from CSV files
- No test fixtures or factories

**Location:**
- Data files in `/Users/aymanbaig/Desktop/cortex-data/`
- Clean versions: `*_clean.csv`
- Valid subset: `master_quotes_valid.csv`

## Coverage

**Requirements:** None enforced

**View Coverage:** Not available

## Test Types

**Unit Tests:**
- Not implemented

**Integration Tests:**
- Not implemented
- Manual end-to-end testing via CLI:
```bash
python3 predict_final.py 1500 Bardeaux
python3 predict_final.py 2000 Elastomere 8 3 0 15
```

**E2E Tests:**
- Not implemented
- Future spec mentions: `backend/tests/test_estimate.py` with 5 sample jobs

## Planned Testing (from TOITURELV-CORTEX-SPEC.md)

**Future Test Structure:**
```
backend/
├── tests/
│   ├── __init__.py
│   └── test_estimate.py     # 5 sample jobs
```

**Sample Test Cases (spec-defined):**
1. Standard Montreal Shingle, 1500 sqft, 6/12 - Expected: $12,000-$14,000
2. Complex Multi-Story, 2500 sqft, chimney, 8/12 - Expected: $18,000-$22,000
3. Rural Laval Metal Roof, 3000 sqft, 4/12 - Expected: $16,000-$19,000
4. Winter Emergency (January), 800 sqft, Elastomere - 12% seasonal premium
5. Edge Case: Odd geometry, 1200 sqft, flat roof + skylights - Low confidence

**Validation Gates (planned):**
- All 5 jobs return estimate within +-15% of expectations
- Confidence scores >0.90 for common jobs, <0.70 for edge cases
- Similar_cases always populated (never empty)
- Response time <5 seconds per request
- No API errors or timeouts

## Visualization-Based Validation

**Model Analysis Charts:**
Generated for visual inspection of model quality.

```python
# From train_cortex_v4.py
fig, axes = plt.subplots(2, 3, figsize=(16, 10))

# Actual vs Predicted scatter
ax.scatter(price_test_orig, tuned_pred_orig, alpha=0.5, s=20, c='#2ecc71')
ax.plot([0, max_val], [0, max_val], 'r--', lw=2)  # Perfect prediction line
ax.set_title(f'Tuned Model | R²={r2_tuned:.3f}')

# Error distribution histogram
ax.hist(errors, bins=30, color='#3498db', edgecolor='white')
ax.axvline(x=0, color='red', linestyle='--')

plt.savefig('cortex_v4_analysis.png', dpi=150, bbox_inches='tight')
```

**Output Files for Review:**
- `cortex_model_analysis.png` - Model performance charts
- `cortex_v4_analysis.png` - V4 optimization results
- `comprehensive_analysis.png` - 16-chart dashboard
- `executive_summary.txt` - Key findings

## Recommendations for Future Testing

**Immediate Needs:**
1. Add pytest with `pytest.ini` or `pyproject.toml`
2. Create `tests/` directory structure
3. Add test fixtures for sample data

**Test File Pattern to Implement:**
```python
# tests/test_predict.py
import pytest
from predict_final import predict

def test_bardeaux_standard():
    result = predict(1500, 'Bardeaux')
    assert 10000 < result['estimate'] < 20000
    assert result['confidence'] == 'HIGH'

def test_elastomere_estimate():
    result = predict(2000, 'Elastomere', material_lines=8)
    assert result['estimate'] > 0
    assert 'range_low' in result
    assert 'range_high' in result

def test_invalid_category():
    result = predict(1000, 'Unknown')
    assert result['confidence'] == 'LOW'
```

**Integration Test Pattern:**
```python
# tests/test_pipeline.py
import pandas as pd

def test_master_quotes_valid():
    df = pd.read_csv('master_quotes_valid.csv')
    assert len(df) > 0
    assert 'sqft_final' in df.columns
    assert 'quoted_total' in df.columns
    assert df['is_valid_for_analysis'].all()
```

---

*Testing analysis: 2026-01-18*
