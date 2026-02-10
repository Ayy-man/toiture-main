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
print("CORTEX MODEL V2 - TWO-STAGE APPROACH")
print("="*70)

df = pd.read_csv('master_quotes_valid.csv')
print(f"\nLoaded {len(df):,} quotes")

# ==========================================================================
# STEP 1: NORMALIZE
# ==========================================================================
print("\n[1/7] NORMALIZING...")
inflation = {2020: 1.97, 2021: 1.52, 2022: 1.36, 2023: 1.06, 2024: 1.06, 2025: 1.00}
for col in ['quoted_total', 'material_cost_total', 'labor_cost_total']:
    df[f'{col}_norm'] = df.apply(lambda r: r[col] * inflation.get(r['year'], 1.0), axis=1)
print("   Done")

# ==========================================================================
# STEP 2: PREPARE DATA
# ==========================================================================
print("\n[2/7] PREPARING DATA...")

model_df = df[
    (df['sqft_final'].notna()) & 
    (df['sqft_final'] > 100) & 
    (df['sqft_final'] < 10000) &
    (df['quoted_total_norm'] > 1000) &
    (df['quoted_total_norm'] < 200000) &
    (df['material_cost_total_norm'] > 0) &
    (df['labor_hours_total'] > 0)
].copy()

print(f"   Valid records: {len(model_df):,}")

# Encode category
le_cat = LabelEncoder()
model_df['cat_enc'] = le_cat.fit_transform(model_df['job_category'].fillna('Other'))

# Additional features
model_df['has_subs'] = (model_df['sub_cost_total'] > 0).astype(int)
model_df['log_sqft'] = np.log1p(model_df['sqft_final'])

# Features
features = ['sqft_final', 'cat_enc', 'has_subs', 'material_line_count', 'labor_line_count']
X = model_df[features].fillna(0)

# ==========================================================================
# STEP 3: TRAIN MATERIAL COST MODEL
# ==========================================================================
print("\n[3/7] TRAINING MATERIAL COST MODEL...")

y_mat = model_df['material_cost_total_norm']
X_train, X_test, y_mat_train, y_mat_test = train_test_split(X, y_mat, test_size=0.2, random_state=42)

mat_model = GradientBoostingRegressor(n_estimators=150, max_depth=5, random_state=42, learning_rate=0.1)
mat_model.fit(X_train, y_mat_train)
mat_pred = mat_model.predict(X_test)
mat_r2 = r2_score(y_mat_test, mat_pred)
mat_mae = mean_absolute_error(y_mat_test, mat_pred)
print(f"   R² = {mat_r2:.3f} | MAE = ${mat_mae:,.0f}")

# ==========================================================================
# STEP 4: TRAIN LABOR HOURS MODEL
# ==========================================================================
print("\n[4/7] TRAINING LABOR HOURS MODEL...")

y_labor = model_df['labor_hours_total']
_, _, y_labor_train, y_labor_test = train_test_split(X, y_labor, test_size=0.2, random_state=42)

labor_model = GradientBoostingRegressor(n_estimators=150, max_depth=5, random_state=42, learning_rate=0.1)
labor_model.fit(X_train, y_labor_train)
labor_pred = labor_model.predict(X_test)
labor_r2 = r2_score(y_labor_test, labor_pred)
labor_mae = mean_absolute_error(y_labor_test, labor_pred)
print(f"   R² = {labor_r2:.3f} | MAE = {labor_mae:.1f} hours")

# ==========================================================================
# STEP 5: CALCULATE MARKUP TABLES
# ==========================================================================
print("\n[5/7] CALCULATING MARKUP TABLES...")

# Material markup by category
mat_markup = model_df.groupby('job_category').apply(
    lambda x: (x['material_sell_total'].sum() / x['material_cost_total'].sum() - 1) 
    if x['material_cost_total'].sum() > 0 else 0.25
).to_dict()

# Labor rate by category ($/hr sell)
labor_rate = model_df.groupby('job_category').apply(
    lambda x: x['labor_sell_total'].sum() / x['labor_hours_total'].sum()
    if x['labor_hours_total'].sum() > 0 else 120
).to_dict()

print("   Material markups:")
for cat, markup in sorted(mat_markup.items(), key=lambda x: -x[1])[:5]:
    print(f"      {cat}: {markup*100:.0f}%")

print("   Labor rates ($/hr):")
for cat, rate in sorted(labor_rate.items(), key=lambda x: -x[1])[:5]:
    print(f"      {cat}: ${rate:.0f}")

# ==========================================================================
# STEP 6: TEST COMBINED PREDICTION
# ==========================================================================
print("\n[6/7] TESTING COMBINED PREDICTIONS...")

# Get test set category names
test_idx = X_test.index
test_cats = model_df.loc[test_idx, 'job_category']

# Predict material cost and labor hours
pred_mat_cost = mat_model.predict(X_test)
pred_labor_hrs = labor_model.predict(X_test)

# Apply markups
final_predictions = []
for i, (mat_cost, labor_hrs, cat) in enumerate(zip(pred_mat_cost, pred_labor_hrs, test_cats)):
    mat_sell = mat_cost * (1 + mat_markup.get(cat, 0.25))
    labor_sell = labor_hrs * labor_rate.get(cat, 120)
    total = mat_sell + labor_sell
    final_predictions.append(total)

final_predictions = np.array(final_predictions)
y_actual = model_df.loc[test_idx, 'quoted_total_norm'].values

# Metrics
combined_r2 = r2_score(y_actual, final_predictions)
combined_mae = mean_absolute_error(y_actual, final_predictions)
pct_within_20 = (np.abs(final_predictions - y_actual) / y_actual <= 0.20).mean() * 100

print(f"   Combined R² = {combined_r2:.3f}")
print(f"   Combined MAE = ${combined_mae:,.0f}")
print(f"   Within ±20% = {pct_within_20:.0f}%")

# Compare to single-stage
print("\n   Comparison:")
single_model = GradientBoostingRegressor(n_estimators=100, max_depth=4, random_state=42)
single_model.fit(X_train, model_df.loc[X_train.index, 'quoted_total_norm'])
single_pred = single_model.predict(X_test)
single_r2 = r2_score(y_actual, single_pred)
single_mae = mean_absolute_error(y_actual, single_pred)
single_20 = (np.abs(single_pred - y_actual) / y_actual <= 0.20).mean() * 100

print(f"   Single-stage:  R²={single_r2:.3f} | MAE=${single_mae:,.0f} | ±20%={single_20:.0f}%")
print(f"   Two-stage:     R²={combined_r2:.3f} | MAE=${combined_mae:,.0f} | ±20%={pct_within_20:.0f}%")

# ==========================================================================
# STEP 7: SAVE & CHART
# ==========================================================================
print("\n[7/7] SAVING...")

joblib.dump(mat_model, 'cortex_material_model.pkl')
joblib.dump(labor_model, 'cortex_labor_model.pkl')
joblib.dump(le_cat, 'category_encoder_v2.pkl')

config = {
    'features': features,
    'category_mapping': {c: int(i) for c, i in zip(le_cat.classes_, range(len(le_cat.classes_)))},
    'material_markup': {k: float(v) for k, v in mat_markup.items()},
    'labor_rate': {k: float(v) for k, v in labor_rate.items()},
    'inflation_factors': inflation,
    'metrics': {
        'material_model_r2': float(mat_r2),
        'labor_model_r2': float(labor_r2),
        'combined_r2': float(combined_r2),
        'combined_mae': float(combined_mae),
        'within_20pct': float(pct_within_20)
    }
}
with open('cortex_config_v2.json', 'w') as f:
    json.dump(config, f, indent=2)

print("   Saved models and config")

# Charts
fig, axes = plt.subplots(2, 3, figsize=(16, 10))
fig.suptitle('CORTEX V2 - TWO-STAGE MODEL', fontsize=14, fontweight='bold')

# 1. Material cost prediction
ax = axes[0, 0]
ax.scatter(y_mat_test, mat_pred, alpha=0.4, s=15, c='#3498db')
ax.plot([0, 50000], [0, 50000], 'r--', lw=2)
ax.set_xlabel('Actual Material Cost'); ax.set_ylabel('Predicted')
ax.set_title(f'Stage 1a: Material Cost | R²={mat_r2:.3f}')
ax.set_xlim(0, 50000); ax.set_ylim(0, 50000)

# 2. Labor hours prediction
ax = axes[0, 1]
ax.scatter(y_labor_test, labor_pred, alpha=0.4, s=15, c='#2ecc71')
ax.plot([0, 200], [0, 200], 'r--', lw=2)
ax.set_xlabel('Actual Labor Hours'); ax.set_ylabel('Predicted')
ax.set_title(f'Stage 1b: Labor Hours | R²={labor_r2:.3f}')
ax.set_xlim(0, 200); ax.set_ylim(0, 200)

# 3. Combined prediction
ax = axes[0, 2]
ax.scatter(y_actual, final_predictions, alpha=0.4, s=15, c='#9b59b6')
ax.plot([0, 80000], [0, 80000], 'r--', lw=2)
ax.set_xlabel('Actual Total'); ax.set_ylabel('Predicted')
ax.set_title(f'Combined: Final Quote | R²={combined_r2:.3f}')
ax.set_xlim(0, 80000); ax.set_ylim(0, 80000)

# 4. Error comparison
ax = axes[1, 0]
residuals_single = y_actual - single_pred
residuals_two = y_actual - final_predictions
ax.hist(residuals_single, bins=40, alpha=0.5, label=f'Single (MAE=${single_mae:,.0f})', color='red')
ax.hist(residuals_two, bins=40, alpha=0.5, label=f'Two-stage (MAE=${combined_mae:,.0f})', color='green')
ax.axvline(x=0, color='black', linestyle='--')
ax.set_xlabel('Error ($CAD)'); ax.legend()
ax.set_title('Error Distribution Comparison')

# 5. Feature importance (material model)
ax = axes[1, 1]
imp = mat_model.feature_importances_
ax.barh(features, imp, color='#e67e22')
ax.set_xlabel('Importance')
ax.set_title('Feature Importance (Material Cost)')

# 6. Markup by category
ax = axes[1, 2]
top_cats = ['Bardeaux', 'Élastomère', 'Other', 'Service Call', 'Ferblanterie']
markups = [mat_markup.get(c, 0)*100 for c in top_cats]
rates = [labor_rate.get(c, 0) for c in top_cats]
x = np.arange(len(top_cats))
ax.bar(x - 0.2, markups, 0.4, label='Material Markup %', color='#3498db')
ax2 = ax.twinx()
ax2.bar(x + 0.2, rates, 0.4, label='Labor $/hr', color='#e74c3c')
ax.set_xticks(x); ax.set_xticklabels(top_cats, rotation=45, ha='right')
ax.set_ylabel('Markup %', color='#3498db')
ax2.set_ylabel('$/hr', color='#e74c3c')
ax.set_title('Markup & Rate by Category')
ax.legend(loc='upper left'); ax2.legend(loc='upper right')

plt.tight_layout()
plt.savefig('cortex_v2_analysis.png', dpi=150, bbox_inches='tight')
print("   Saved cortex_v2_analysis.png")

print("\n" + "="*70)
print("DONE - V2 Two-Stage Model")
print("="*70)
print(f"""
IMPROVEMENT:
   Single-stage: R²={single_r2:.3f} | MAE=${single_mae:,.0f} | ±20%={single_20:.0f}%
   Two-stage:    R²={combined_r2:.3f} | MAE=${combined_mae:,.0f} | ±20%={pct_within_20:.0f}%

Test: python3 predict_cortex_v2.py 1500 Bardeaux
""")
