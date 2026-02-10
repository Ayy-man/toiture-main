import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_absolute_error, r2_score
import joblib
import json
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

print("="*70)
print("CORTEX MODEL TRAINING")
print("="*70)

df = pd.read_csv('master_quotes_valid.csv')
print(f"\nLoaded {len(df):,} quotes")

print("\n[1/6] NORMALIZING TO 2025 DOLLARS...")
inflation_factors = {2020: 1.97, 2021: 1.52, 2022: 1.36, 2023: 1.06, 2024: 1.06, 2025: 1.00}
df['quoted_total_normalized'] = df.apply(lambda row: row['quoted_total'] * inflation_factors.get(row['year'], 1.0), axis=1)
print("   Done")

print("\n[2/6] PREPARING DATA...")
model_df = df[(df['sqft_final'].notna()) & (df['sqft_final'] > 0) & (df['sqft_final'] < 10000) & (df['quoted_total_normalized'] < 200000)].copy()
model_df['has_subs'] = (model_df['sub_cost_total'] > 0).astype(int)
le_category = LabelEncoder()
model_df['job_category_encoded'] = le_category.fit_transform(model_df['job_category'].fillna('Other'))
print(f"   {len(model_df):,} valid records")

features = ['sqft_final', 'job_category_encoded', 'has_subs']
X = model_df[features]
y = model_df['quoted_total_normalized']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print("\n[3/6] TRAINING MODELS...")
lr = LinearRegression()
lr.fit(X_train, y_train)
lr_pred = lr.predict(X_test)
lr_mae, lr_r2 = mean_absolute_error(y_test, lr_pred), r2_score(y_test, lr_pred)

gb = GradientBoostingRegressor(n_estimators=100, max_depth=4, random_state=42)
gb.fit(X_train, y_train)
gb_pred = gb.predict(X_test)
gb_mae, gb_r2 = mean_absolute_error(y_test, gb_pred), r2_score(y_test, gb_pred)

print(f"   Linear:   MAE=${lr_mae:,.0f}  R²={lr_r2:.3f}")
print(f"   Boosting: MAE=${gb_mae:,.0f}  R²={gb_r2:.3f}")

if gb_r2 > lr_r2 + 0.02:
    best_model, best_name, best_pred, best_mae, best_r2 = gb, "GradientBoosting", gb_pred, gb_mae, gb_r2
else:
    best_model, best_name, best_pred, best_mae, best_r2 = lr, "LinearRegression", lr_pred, lr_mae, lr_r2
print(f"   Winner: {best_name}")

print("\n[4/6] BUILDING BALLPARK TABLE...")
def size_bucket(sqft):
    if sqft < 800: return 'Small'
    elif sqft < 2000: return 'Medium'
    return 'Large'
model_df['size_bucket'] = model_df['sqft_final'].apply(size_bucket)
percentile_table = []
for cat in model_df['job_category'].unique():
    for size in ['Small', 'Medium', 'Large']:
        subset = model_df[(model_df['job_category']==cat) & (model_df['size_bucket']==size)]
        if len(subset) >= 5:
            percentile_table.append({'job_category': cat, 'size_bucket': size, 'count': len(subset),
                'p25': int(subset['quoted_total_normalized'].quantile(0.25)),
                'p50': int(subset['quoted_total_normalized'].quantile(0.50)),
                'p75': int(subset['quoted_total_normalized'].quantile(0.75))})
percentile_df = pd.DataFrame(percentile_table)
print(f"   {len(percentile_df)} combos")

print("\n[5/6] SAVING FILES...")
joblib.dump(best_model, 'cortex_model.pkl')
joblib.dump(le_category, 'category_encoder.pkl')
percentile_df.to_csv('model_b_percentiles.csv', index=False)
config = {'model_type': best_name, 'features': features, 
    'category_mapping': {c: int(i) for c, i in zip(le_category.classes_, range(len(le_category.classes_)))},
    'inflation_factors': inflation_factors, 'metrics': {'mae': float(best_mae), 'r2': float(best_r2)}, 'currency': 'CAD'}
with open('cortex_config.json', 'w') as f:
    json.dump(config, f, indent=2)
print("   Done")

print("\n[6/6] GENERATING CHART...")
fig, axes = plt.subplots(2, 2, figsize=(12, 10))
fig.suptitle('CORTEX MODEL ANALYSIS', fontsize=14, fontweight='bold')

axes[0,0].scatter(y_test, best_pred, alpha=0.5, s=20, c='#2ecc71')
axes[0,0].plot([0, 80000], [0, 80000], 'r--', lw=2)
axes[0,0].set_xlabel('Actual ($CAD)'); axes[0,0].set_ylabel('Predicted ($CAD)')
axes[0,0].set_title(f'Actual vs Predicted | R²={best_r2:.3f}')
axes[0,0].set_xlim(0, 80000); axes[0,0].set_ylim(0, 80000)

residuals = y_test.values - best_pred
axes[0,1].hist(residuals, bins=40, color='#3498db', edgecolor='white')
axes[0,1].axvline(x=0, color='red', linestyle='--', lw=2)
axes[0,1].set_xlabel('Error ($CAD)'); axes[0,1].set_title(f'Error Distribution | MAE=${best_mae:,.0f}')

importance = gb.feature_importances_ if best_name == "GradientBoosting" else np.abs(lr.coef_) / np.sum(np.abs(lr.coef_))
axes[1,0].barh(features, importance, color='#9b59b6')
axes[1,0].set_xlabel('Importance'); axes[1,0].set_title('Feature Importance')

top_cats = ['Bardeaux', 'Élastomère', 'Other', 'Service Call']
cat_medians = [model_df[model_df['job_category']==c]['quoted_total_normalized'].median() for c in top_cats]
axes[1,1].bar(top_cats, cat_medians, color='#e67e22')
axes[1,1].set_ylabel('Median ($CAD)'); axes[1,1].set_title('Price by Category')
plt.setp(axes[1,1].xaxis.get_majorticklabels(), rotation=45, ha='right')

plt.tight_layout()
plt.savefig('cortex_model_analysis.png', dpi=150, bbox_inches='tight')
print("   Saved cortex_model_analysis.png")

print("\n" + "="*70)
print("DONE")
print("="*70)
pct = (np.abs(residuals) / y_test.values <= 0.20).mean() * 100
print(f"\nModel: {best_name}\nMAE: ${best_mae:,.0f}\nR²: {best_r2:.3f}\nWithin ±20%: {pct:.0f}%")
print("\nTest: python3 predict_cortex.py 1500 Bardeaux")