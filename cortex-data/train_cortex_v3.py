import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_absolute_error, r2_score
import joblib
import json
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

print("="*70)
print("CORTEX V3 - PER-CATEGORY MODELS + MORE FEATURES")
print("="*70)

df = pd.read_csv('master_quotes_valid.csv')
print(f"\nLoaded {len(df):,} quotes")

# Normalize
inflation = {2020: 1.97, 2021: 1.52, 2022: 1.36, 2023: 1.06, 2024: 1.06, 2025: 1.00}
df['price_norm'] = df.apply(lambda r: r['quoted_total'] * inflation.get(r['year'], 1.0), axis=1)

# Filter
model_df = df[
    (df['sqft_final'].notna()) & 
    (df['sqft_final'] > 100) & 
    (df['sqft_final'] < 10000) &
    (df['price_norm'] > 500) &
    (df['price_norm'] < 150000)
].copy()

print(f"Valid records: {len(model_df):,}")

# Features - use everything useful
model_df['has_subs'] = (model_df['sub_cost_total'] > 0).astype(int)
model_df['has_materials'] = (model_df['material_line_count'] > 0).astype(int)
model_df['sqft_log'] = np.log1p(model_df['sqft_final'])

features = ['sqft_final', 'material_line_count', 'labor_line_count', 'has_subs', 'complexity_score']

# ==========================================================================
# TRAIN PER-CATEGORY MODELS
# ==========================================================================
print("\n" + "="*70)
print("TRAINING PER-CATEGORY MODELS")
print("="*70)

categories = ['Bardeaux', 'Élastomère', 'Other', 'Service Call']
models = {}
results = []

for cat in categories:
    cat_df = model_df[model_df['job_category'] == cat]
    
    if len(cat_df) < 50:
        print(f"\n{cat}: Skipped (only {len(cat_df)} records)")
        continue
    
    X = cat_df[features].fillna(0)
    y = cat_df['price_norm']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    model = GradientBoostingRegressor(
        n_estimators=150, 
        max_depth=5, 
        learning_rate=0.1,
        min_samples_leaf=5,
        random_state=42
    )
    model.fit(X_train, y_train)
    
    pred = model.predict(X_test)
    r2 = r2_score(y_test, pred)
    mae = mean_absolute_error(y_test, pred)
    pct20 = (np.abs(pred - y_test.values) / y_test.values <= 0.20).mean() * 100
    
    models[cat] = {
        'model': model,
        'r2': r2,
        'mae': mae,
        'pct20': pct20,
        'n_train': len(X_train),
        'n_test': len(X_test),
        'feature_importance': dict(zip(features, model.feature_importances_))
    }
    
    results.append({
        'category': cat,
        'n': len(cat_df),
        'r2': r2,
        'mae': mae,
        'pct20': pct20
    })
    
    print(f"\n{cat} ({len(cat_df)} records):")
    print(f"   R² = {r2:.3f} | MAE = ${mae:,.0f} | ±20% = {pct20:.0f}%")
    print(f"   Top features: ", end="")
    top_feat = sorted(zip(features, model.feature_importances_), key=lambda x: -x[1])[:3]
    print(", ".join([f"{f}:{v:.0%}" for f,v in top_feat]))

# ==========================================================================
# TRAIN GLOBAL FALLBACK MODEL
# ==========================================================================
print("\n" + "="*70)
print("TRAINING GLOBAL FALLBACK MODEL")
print("="*70)

le_cat = LabelEncoder()
model_df['cat_enc'] = le_cat.fit_transform(model_df['job_category'].fillna('Other'))

global_features = features + ['cat_enc']
X_all = model_df[global_features].fillna(0)
y_all = model_df['price_norm']

X_train, X_test, y_train, y_test = train_test_split(X_all, y_all, test_size=0.2, random_state=42)

global_model = GradientBoostingRegressor(
    n_estimators=200, 
    max_depth=6, 
    learning_rate=0.1,
    min_samples_leaf=5,
    random_state=42
)
global_model.fit(X_train, y_train)

global_pred = global_model.predict(X_test)
global_r2 = r2_score(y_test, global_pred)
global_mae = mean_absolute_error(y_test, global_pred)
global_pct20 = (np.abs(global_pred - y_test.values) / y_test.values <= 0.20).mean() * 100

print(f"\nGlobal Model:")
print(f"   R² = {global_r2:.3f} | MAE = ${global_mae:,.0f} | ±20% = {global_pct20:.0f}%")

# ==========================================================================
# COMPARISON SUMMARY
# ==========================================================================
print("\n" + "="*70)
print("RESULTS SUMMARY")
print("="*70)

results_df = pd.DataFrame(results)
print("\nPer-Category Models:")
print(results_df.to_string(index=False))

print(f"\nGlobal Fallback: R²={global_r2:.3f} | MAE=${global_mae:,.0f} | ±20%={global_pct20:.0f}%")

# Best approach
best_cat_r2 = results_df['r2'].mean()
print(f"\nAvg Per-Category R²: {best_cat_r2:.3f}")
print(f"Global R²: {global_r2:.3f}")

if best_cat_r2 > global_r2:
    print("\n✓ Per-category models WIN - use specialized models")
    use_per_cat = True
else:
    print("\n✓ Global model WINS - use single model")
    use_per_cat = False

# ==========================================================================
# SAVE
# ==========================================================================
print("\n" + "="*70)
print("SAVING")
print("="*70)

# Save per-category models
for cat, data in models.items():
    safe_name = cat.replace(' ', '_').replace('é', 'e')
    joblib.dump(data['model'], f'cortex_model_{safe_name}.pkl')
    print(f"   Saved cortex_model_{safe_name}.pkl")

# Save global model
joblib.dump(global_model, 'cortex_model_global.pkl')
joblib.dump(le_cat, 'category_encoder_v3.pkl')

# Config
config = {
    'features': features,
    'global_features': global_features,
    'category_mapping': {c: int(i) for c, i in zip(le_cat.classes_, range(len(le_cat.classes_)))},
    'per_category_models': {cat: {'r2': d['r2'], 'mae': d['mae'], 'pct20': d['pct20']} for cat, d in models.items()},
    'global_model': {'r2': global_r2, 'mae': global_mae, 'pct20': global_pct20},
    'use_per_category': use_per_cat,
    'inflation_factors': inflation
}
with open('cortex_config_v3.json', 'w') as f:
    json.dump(config, f, indent=2)

# ==========================================================================
# CHARTS
# ==========================================================================
print("\nGenerating charts...")

fig, axes = plt.subplots(2, 3, figsize=(16, 10))
fig.suptitle('CORTEX V3 - PER-CATEGORY MODELS', fontsize=14, fontweight='bold')

# 1. R² by category
ax = axes[0, 0]
cats = results_df['category'].tolist() + ['Global']
r2s = results_df['r2'].tolist() + [global_r2]
colors = ['#2ecc71' if r > 0.6 else '#f1c40f' if r > 0.4 else '#e74c3c' for r in r2s]
ax.barh(cats, r2s, color=colors)
ax.axvline(x=0.5, color='black', linestyle='--', alpha=0.5)
ax.set_xlabel('R² Score')
ax.set_title('Model Accuracy by Category')
for i, r in enumerate(r2s):
    ax.text(r + 0.02, i, f'{r:.2f}', va='center')

# 2. MAE by category
ax = axes[0, 1]
maes = results_df['mae'].tolist() + [global_mae]
ax.barh(cats, maes, color='#3498db')
ax.set_xlabel('MAE ($CAD)')
ax.set_title('Average Error by Category')
for i, m in enumerate(maes):
    ax.text(m + 100, i, f'${m:,.0f}', va='center')

# 3. Sample size
ax = axes[0, 2]
ns = results_df['n'].tolist() + [len(model_df)]
ax.barh(cats, ns, color='#9b59b6')
ax.set_xlabel('Sample Size')
ax.set_title('Training Data by Category')

# 4. Actual vs Predicted (Global)
ax = axes[1, 0]
ax.scatter(y_test, global_pred, alpha=0.4, s=15, c='#2ecc71')
ax.plot([0, 80000], [0, 80000], 'r--', lw=2)
ax.set_xlabel('Actual ($CAD)'); ax.set_ylabel('Predicted ($CAD)')
ax.set_title(f'Global Model | R²={global_r2:.3f}')
ax.set_xlim(0, 80000); ax.set_ylim(0, 80000)

# 5. Feature importance (Global)
ax = axes[1, 1]
imp = global_model.feature_importances_
ax.barh(global_features, imp, color='#e67e22')
ax.set_xlabel('Importance')
ax.set_title('Feature Importance (Global)')

# 6. ±20% accuracy
ax = axes[1, 2]
pct20s = results_df['pct20'].tolist() + [global_pct20]
colors = ['#2ecc71' if p > 50 else '#f1c40f' if p > 35 else '#e74c3c' for p in pct20s]
ax.barh(cats, pct20s, color=colors)
ax.axvline(x=50, color='black', linestyle='--', alpha=0.5, label='50% target')
ax.set_xlabel('% Within ±20%')
ax.set_title('Prediction Accuracy')
ax.legend()

plt.tight_layout()
plt.savefig('cortex_v3_analysis.png', dpi=150, bbox_inches='tight')
print("   Saved cortex_v3_analysis.png")

print("\n" + "="*70)
print("DONE")
print("="*70)
