# Coding Conventions

**Analysis Date:** 2026-01-18

## Naming Patterns

**Files:**
- snake_case for all Python files: `train_cortex_v4.py`, `master_data_pipeline_v3.py`
- Versioned suffixes common: `_v2.py`, `_v3.py`, `_v4.py`, `_fixed.py`
- Descriptive names: `comprehensive_analysis.py`, `validate_clients.py`

**Functions:**
- snake_case: `extract_sqft()`, `parse_french_number()`, `get_sqft_from_dims()`
- Verb-first naming: `predict()`, `analyze()`, `log()`, `categorize_job_type()`
- Short utility functions: `log(msg)` for print with flush

**Variables:**
- snake_case throughout: `model_df`, `best_max_price`, `cat_margin`
- DataFrame abbreviations: `df`, `master`, `bardeaux`
- Descriptive suffixes: `_clean`, `_valid`, `_normalized`, `_orig`

**Constants:**
- UPPER_CASE for constants: `DATA_PATH`, `OUTPUT_PATH`, `FILES`
- Dictionaries for config: `COLORS`, `CATEGORY_COLORS`, `inflation_factors`

## Code Style

**Formatting:**
- No automated formatter detected (no `.prettierrc`, `black.toml`, etc.)
- 4-space indentation (Python default)
- Line lengths vary, some exceed 100 characters
- Inconsistent spacing around operators

**Linting:**
- No linting configuration detected
- `warnings.filterwarnings('ignore')` used in all ML scripts
- Bare `except:` clauses present in some files

## Import Organization

**Order:**
1. Standard library: `sys`, `os`, `re`, `json`, `warnings`
2. Third-party: `pandas as pd`, `numpy as np`, `matplotlib.pyplot as plt`
3. Scikit-learn: `from sklearn.model_selection import train_test_split`
4. Project modules: None (scripts are standalone)

**Common Aliases:**
```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from datetime import datetime
```

**Path Configuration:**
- Hardcoded absolute paths: `DATA_PATH = "/Users/aymanbaig/Desktop/cortex-data/"`
- Pattern: Define `DATA_PATH` constant at top, use f-strings for file paths

## Error Handling

**Patterns:**
- Bare try/except for data parsing (silent failures):
```python
try:
    return float(num_str)
except:
    return None
```

- No explicit error handling in main script flows
- Data validation via filtering rather than exceptions

**Data Validation:**
- Filter invalid data rather than raise errors
- Use pandas conditions: `df[(df['col'] > 0) & (df['col'] < max_val)]`
- Return `None` for unparseable values

## Logging

**Framework:** Standard `print()` statements

**Patterns:**
- Progress indicators with separators:
```python
print("="*70)
print("SECTION TITLE")
print("="*70)
```

- Step numbering: `[1/6] STEP NAME...`
- Checkmarks for completion: `print(f"  ✓ Saved: {filename}")`
- Flush for real-time output: `sys.stdout.flush()`

**Helper Function:**
```python
def log(msg):
    print(msg)
    sys.stdout.flush()
```

## Comments

**When to Comment:**
- Module-level docstrings for purpose
- Section separators with `# ===...===`
- Inline comments for non-obvious calculations

**Docstring Style:**
```python
"""
TOITURELV - MASTER DATA PIPELINE v4 (Fixed)
- Skips broken Quote Materials_clean.csv
- Uses existing v3 master_quotes.csv for material aggregations
"""
```

**Function Docstrings:**
```python
def predict(sqft, category, material_lines=5, labor_lines=2, has_subs=0, complexity=10):
    """
    Predict quote price.

    Args:
        sqft: Square footage
        category: Job category (Bardeaux, Elastomere, Other, etc.)
    """
```

## Function Design

**Size:** Functions range from 5-50 lines; no strict limit enforced

**Parameters:**
- Positional for required params
- Default values for optional: `material_lines=5, labor_lines=2`
- No type hints in existing code

**Return Values:**
- Single values or tuples: `return sqft, 'source'`
- Dictionaries for complex returns:
```python
return {
    'estimate': prediction,
    'range_low': prediction * 0.80,
    'range_high': prediction * 1.20,
}
```
- `None` for failure cases

## Module Design

**Exports:** Not used (no `__init__.py` files)

**Barrel Files:** Not used

**Script Structure:**
1. Shebang: `#!/usr/bin/env python3`
2. Module docstring
3. Imports
4. Constants (`DATA_PATH`, `OUTPUT_PATH`)
5. Helper functions
6. Main logic (often not in `main()`)
7. `if __name__ == '__main__':` guard (inconsistent)

## Data Manipulation Patterns

**Pandas Conventions:**
```python
# Loading with error handling
df = pd.read_csv(f"{DATA_PATH}filename.csv")
df['date_col'] = pd.to_datetime(df['date_col'], errors='coerce')

# Filtering
valid = df[(df['col'] > 0) & (df['col'] < max_val)]

# Groupby patterns
results = df.groupby('category').agg({
    'col1': ['mean', 'median', 'count'],
    'col2': 'sum'
}).reset_index()

# Column renaming after groupby
df.columns = ['cat', 'mean', 'count']
```

**NumPy Conventions:**
```python
# Log transforms
df['log_col'] = np.log1p(df['col'])

# Inverse transforms
pred_orig = np.expm1(pred)

# Array operations
np.abs(errors) / y_values <= 0.20
```

## ML Model Conventions

**Training Pattern:**
```python
# Data prep
X = df[features].fillna(0)
y = df['target']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Model training
model = GradientBoostingRegressor(n_estimators=150, max_depth=5, random_state=42)
model.fit(X_train, y_train)
pred = model.predict(X_test)

# Evaluation
r2 = r2_score(y_test, pred)
mae = mean_absolute_error(y_test, pred)
```

**Model Persistence:**
```python
import joblib
joblib.dump(model, 'model_name.pkl')
model = joblib.load('model_name.pkl')
```

**Config Persistence:**
```python
import json
config = {'features': features, 'metrics': {'mae': mae, 'r2': r2}}
with open('config.json', 'w') as f:
    json.dump(config, f, indent=2)
```

## Visualization Conventions

**Matplotlib Setup:**
```python
plt.style.use('seaborn-v0_8-whitegrid')
fig, axes = plt.subplots(2, 3, figsize=(18, 12))
fig.suptitle('TITLE', fontsize=14, fontweight='bold', y=1.02)
```

**Saving Figures:**
```python
plt.tight_layout()
plt.savefig(f"{OUTPUT_PATH}filename.png", dpi=150, bbox_inches='tight',
            facecolor='white', edgecolor='none')
plt.close()
```

---

*Convention analysis: 2026-01-18*
