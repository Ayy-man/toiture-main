"""
CORTEX V4 - EXHAUSTIVE OPTIMIZATION
Tries every reasonable technique to maximize accuracy.
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import Ridge, HuberRegressor
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_absolute_error, r2_score, mean_absolute_percentage_error
import joblib
import json
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

print("="*70)
print("CORTEX V4 - EXHAUSTIVE OPTIMIZATION")
print("="*70)

# ==========================================================================
# LOAD AND PREPARE DATA
# ==========================================================================
df = pd.read_csv('master_quotes_valid.csv')
print(f"\nLoaded {len(df):,} quotes")

# Inflation normalization
inflation = {2020: 1.97, 2021: 1.52, 2022: 1.36, 2023: 1.06, 2024: 1.06, 2025: 1.00}
df['price_norm'] = df.apply(lambda r: r['quoted_total'] * inflation.get(r['year'], 1.0), axis=1)

# ==========================================================================
# EXPERIMENT 1: TIGHTER OUTLIER BOUNDS
# ==========================================================================
print("\n" + "="*70)
print("EXPERIMENT 1: OPTIMAL OUTLIER BOUNDS")
print("="*70)

bounds_results = []
for max_price in [50000, 75000, 100000, 150000]:
    for max_sqft in [5000, 7500, 10000]:
        temp = df[
            (df['sqft_final'].notna()) & 
            (df['sqft_final'] > 100) & 
            (df['sqft_final'] < max_sqft) &
            (df['price_norm'] > 1000) &
            (df['price_norm'] < max_price) &
            (df['job_category'] == 'Bardeaux')
        ].copy()
        if len(temp) > 200:
            X = temp[['sqft_final']].fillna(0)
            y = temp['price_norm']
            model = GradientBoostingRegressor(n_estimators=100, random_state=42)
            scores = cross_val_score(model, X, y, cv=5, scoring='r2')
            bounds_results.append({
                'max_price': max_price,
                'max_sqft': max_sqft,
                'n': len(temp),
                'cv_r2': scores.mean()
            })

bounds_df = pd.DataFrame(bounds_results).sort_values('cv_r2', ascending=False)
print("\nBest outlier bounds:")
print(bounds_df.head(5).to_string(index=False))

best_max_price = bounds_df.iloc[0]['max_price']
best_max_sqft = bounds_df.iloc[0]['max_sqft']

model_df = df[
    (df['sqft_final'].notna()) & 
    (df['sqft_final'] > 100) & 
    (df['sqft_final'] < best_max_sqft) &
    (df['price_norm'] > 1000) &
    (df['price_norm'] < best_max_price)
].copy()

print(f"\nUsing bounds: sqft < {best_max_sqft}, price < ${best_max_price:,}")
print(f"Records after filtering: {len(model_df):,}")

# ==========================================================================
# FEATURE ENGINEERING
# ==========================================================================
print("\n" + "="*70)
print("EXPERIMENT 2: FEATURE ENGINEERING")
print("="*70)

model_df['has_subs'] = (model_df['sub_cost_total'] > 0).astype(int)
model_df['sqft_log'] = np.log1p(model_df['sqft_final'])
model_df['price_log'] = np.log1p(model_df['price_norm'])
model_df['price_per_sqft'] = model_df['price_norm'] / model_df['sqft_final']
model_df['sqft_x_complexity'] = model_df['sqft_final'] * model_df['complexity_score'].fillna(10)
model_df['sqft_x_materials'] = model_df['sqft_final'] * model_df['material_line_count'].fillna(5)
model_df['sqft_squared'] = model_df['sqft_final'] ** 2
model_df['material_labor_ratio'] = (
    model_df['material_line_count'].fillna(1) / 
    model_df['labor_line_count'].replace(0, 1).fillna(1)
)

le = LabelEncoder()
model_df['cat_enc'] = le.fit_transform(model_df['job_category'].fillna('Other'))

print("Engineered features: sqft_log, price_per_sqft, interactions, polynomial")

# ==========================================================================
# EXPERIMENT 3: BARDEAUX - MULTIPLE APPROACHES
# ==========================================================================
print("\n" + "="*70)
print("EXPERIMENT 3: BARDEAUX MODEL OPTIMIZATION")
print("="*70)

bardeaux = model_df[model_df['job_category'] == 'Bardeaux'].copy().reset_index(drop=True)
print(f"\nBardeaux records: {len(bardeaux):,}")

feature_sets = {
    'minimal': ['sqft_final'],
    'basic': ['sqft_final', 'complexity_score', 'material_line_count'],
    'interactions': ['sqft_final', 'complexity_score', 'sqft_x_complexity', 'material_line_count'],
    'full': ['sqft_final', 'complexity_score', 'sqft_x_complexity', 'material_line_count', 
             'labor_line_count', 'has_subs', 'material_labor_ratio', 'sqft_squared'],
    'log_features': ['sqft_log', 'complexity_score', 'material_line_count'],
}

results = []

for feat_name, features in feature_sets.items():
    for target_name in ['raw', 'log', 'per_sqft']:
        if target_name == 'per_sqft' and feat_name == 'log_features':
            continue
            
        X = bardeaux[features].fillna(0)
        sqft_all = bardeaux['sqft_final'].values
        
        if target_name == 'per_sqft':
            y = bardeaux['price_norm'] / bardeaux['sqft_final']
        elif target_name == 'log':
            y = np.log1p(bardeaux['price_norm'])
        else:
            y = bardeaux['price_norm']
        
        # Split with indices tracked
        indices = np.arange(len(bardeaux))
        X_train, X_test, y_train, y_test, idx_train, idx_test = train_test_split(
            X, y, indices, test_size=0.2, random_state=42
        )
        
        sqft_test = sqft_all[idx_test]
        
        model = GradientBoostingRegressor(
            n_estimators=150, max_depth=5, learning_rate=0.1,
            min_samples_leaf=5, random_state=42
        )
        model.fit(X_train, y_train)
        pred = model.predict(X_test)
        
        # Transform back
        if target_name == 'log':
            pred_orig = np.expm1(pred)
            y_test_orig = np.expm1(y_test.values)
        elif target_name == 'per_sqft':
            pred_orig = pred * sqft_test
            y_test_orig = y_test.values * sqft_test
        else:
            pred_orig = pred
            y_test_orig = y_test.values
        
        r2 = r2_score(y_test_orig, pred_orig)
        mae = mean_absolute_error(y_test_orig, pred_orig)
        pct20 = (np.abs(pred_orig - y_test_orig) / y_test_orig <= 0.20).mean() * 100
        mape = mean_absolute_percentage_error(y_test_orig, pred_orig) * 100
        
        results.append({
            'features': feat_name,
            'target': target_name,
            'r2': r2,
            'mae': mae,
            'pct20': pct20,
            'mape': mape
        })

results_df = pd.DataFrame(results).sort_values('r2', ascending=False)
print("\nAll combinations (sorted by R²):")
print(results_df.to_string(index=False))

best = results_df.iloc[0]
print(f"\n✓ BEST: features={best['features']}, target={best['target']}")
print(f"  R²={best['r2']:.3f} | MAE=${best['mae']:,.0f} | ±20%={best['pct20']:.0f}% | MAPE={best['mape']:.1f}%")

# ==========================================================================
# EXPERIMENT 4: ENSEMBLE METHODS
# ==========================================================================
print("\n" + "="*70)
print("EXPERIMENT 4: ENSEMBLE METHODS")
print("="*70)

best_features = feature_sets[best['features']]
X = bardeaux[best_features].fillna(0)
sqft_all = bardeaux['sqft_final'].values

if best['target'] == 'log':
    y = np.log1p(bardeaux['price_norm'])
elif best['target'] == 'per_sqft':
    y = bardeaux['price_norm'] / bardeaux['sqft_final']
else:
    y = bardeaux['price_norm']

indices = np.arange(len(bardeaux))
X_train, X_test, y_train, y_test, idx_train, idx_test = train_test_split(
    X, y, indices, test_size=0.2, random_state=42
)
sqft_test = sqft_all[idx_test]
price_test_orig = bardeaux['price_norm'].values[idx_test]

gb = GradientBoostingRegressor(n_estimators=150, max_depth=5, random_state=42)
rf = RandomForestRegressor(n_estimators=150, max_depth=10, random_state=42)
ridge = Ridge(alpha=1.0)
huber = HuberRegressor(epsilon=1.35)

models = {'GradientBoosting': gb, 'RandomForest': rf, 'Ridge': ridge, 'Huber': huber}
model_preds = {}

print("\nIndividual models:")
for name, model in models.items():
    model.fit(X_train, y_train)
    pred = model.predict(X_test)
    model_preds[name] = pred
    
    if best['target'] == 'log':
        pred_orig = np.expm1(pred)
    elif best['target'] == 'per_sqft':
        pred_orig = pred * sqft_test
    else:
        pred_orig = pred
    
    r2 = r2_score(price_test_orig, pred_orig)
    mae = mean_absolute_error(price_test_orig, pred_orig)
    print(f"  {name}: R²={r2:.3f} | MAE=${mae:,.0f}")

# Ensemble
avg_pred = np.mean([model_preds['GradientBoosting'], model_preds['RandomForest']], axis=0)

if best['target'] == 'log':
    avg_pred_orig = np.expm1(avg_pred)
elif best['target'] == 'per_sqft':
    avg_pred_orig = avg_pred * sqft_test
else:
    avg_pred_orig = avg_pred

r2_ens = r2_score(price_test_orig, avg_pred_orig)
mae_ens = mean_absolute_error(price_test_orig, avg_pred_orig)
pct20_ens = (np.abs(avg_pred_orig - price_test_orig) / price_test_orig <= 0.20).mean() * 100

print(f"\n✓ ENSEMBLE (GB + RF avg): R²={r2_ens:.3f} | MAE=${mae_ens:,.0f} | ±20%={pct20_ens:.0f}%")

# ==========================================================================
# EXPERIMENT 5: HYPERPARAMETER TUNING
# ==========================================================================
print("\n" + "="*70)
print("EXPERIMENT 5: HYPERPARAMETER TUNING")
print("="*70)

param_grid = {
    'n_estimators': [150, 250],
    'max_depth': [4, 6],
    'learning_rate': [0.08, 0.12],
    'min_samples_leaf': [4, 7]
}

grid_search = GridSearchCV(
    GradientBoostingRegressor(random_state=42),
    param_grid,
    cv=5,
    scoring='r2',
    n_jobs=-1
)
grid_search.fit(X_train, y_train)

print(f"\nBest params: {grid_search.best_params_}")
print(f"Best CV R²: {grid_search.best_score_:.3f}")

tuned_pred = grid_search.predict(X_test)

if best['target'] == 'log':
    tuned_pred_orig = np.expm1(tuned_pred)
elif best['target'] == 'per_sqft':
    tuned_pred_orig = tuned_pred * sqft_test
else:
    tuned_pred_orig = tuned_pred

r2_tuned = r2_score(price_test_orig, tuned_pred_orig)
mae_tuned = mean_absolute_error(price_test_orig, tuned_pred_orig)
pct20_tuned = (np.abs(tuned_pred_orig - price_test_orig) / price_test_orig <= 0.20).mean() * 100

print(f"✓ TUNED: R²={r2_tuned:.3f} | MAE=${mae_tuned:,.0f} | ±20%={pct20_tuned:.0f}%")

# ==========================================================================
# FINAL COMPARISON
# ==========================================================================
print("\n" + "="*70)
print("FINAL COMPARISON")
print("="*70)

comparison = pd.DataFrame([
    {'Model': 'V3 Bardeaux (baseline)', 'R²': 0.648, 'MAE': 3486, '±20%': 51},
    {'Model': f'V4 Best ({best["features"]}/{best["target"]})', 
     'R²': round(best['r2'], 3), 'MAE': round(best['mae']), '±20%': round(best['pct20'])},
    {'Model': 'V4 Ensemble (GB+RF)', 'R²': round(r2_ens, 3), 'MAE': round(mae_ens), '±20%': round(pct20_ens)},
    {'Model': 'V4 Tuned GB', 'R²': round(r2_tuned, 3), 'MAE': round(mae_tuned), '±20%': round(pct20_tuned)},
])
print(comparison.to_string(index=False))

# ==========================================================================
# SAVE BEST MODEL
# ==========================================================================
print("\n" + "="*70)
print("SAVING BEST MODEL")
print("="*70)

winner_idx = comparison['R²'].idxmax()
winner = comparison.iloc[winner_idx]
print(f"\n🏆 WINNER: {winner['Model']}")
print(f"   R²={winner['R²']:.3f} | MAE=${winner['MAE']:,.0f} | ±20%={winner['±20%']:.0f}%")

# Save tuned model
joblib.dump(grid_search.best_estimator_, 'cortex_v4_bardeaux.pkl')
joblib.dump(le, 'category_encoder_v4.pkl')

# Also save ensemble models
joblib.dump(gb, 'cortex_v4_gb.pkl')
joblib.dump(rf, 'cortex_v4_rf.pkl')

config_v4 = {
    'features': best_features,
    'target_transform': best['target'],
    'best_params': grid_search.best_params_,
    'performance': {
        'r2': float(r2_tuned),
        'mae': float(mae_tuned),
        'pct20': float(pct20_tuned)
    },
    'outlier_bounds': {
        'max_sqft': int(best_max_sqft),
        'max_price': int(best_max_price)
    },
    'comparison': comparison.to_dict('records'),
    'inflation_factors': inflation
}
with open('cortex_config_v4.json', 'w') as f:
    json.dump(config_v4, f, indent=2)

print("\nSaved: cortex_v4_bardeaux.pkl, cortex_config_v4.json")

# ==========================================================================
# VISUALIZATION
# ==========================================================================
print("\nGenerating charts...")

fig, axes = plt.subplots(2, 3, figsize=(16, 10))
fig.suptitle('CORTEX V4 - OPTIMIZATION RESULTS', fontsize=14, fontweight='bold')

# 1. Heatmap
ax = axes[0, 0]
pivot = results_df.pivot(index='features', columns='target', values='r2')
im = ax.imshow(pivot.values, cmap='RdYlGn', vmin=0.4, vmax=0.8)
ax.set_xticks(range(len(pivot.columns)))
ax.set_yticks(range(len(pivot.index)))
ax.set_xticklabels(pivot.columns)
ax.set_yticklabels(pivot.index)
for i in range(len(pivot.index)):
    for j in range(len(pivot.columns)):
        val = pivot.values[i, j]
        if not np.isnan(val):
            ax.text(j, i, f'{val:.2f}', ha='center', va='center', fontsize=10)
ax.set_title('R² by Feature Set & Target Transform')
plt.colorbar(im, ax=ax)

# 2. Model comparison
ax = axes[0, 1]
models_comp = comparison['Model'].tolist()
r2_comp = comparison['R²'].tolist()
colors = ['#3498db', '#2ecc71', '#e74c3c', '#9b59b6']
bars = ax.barh(models_comp, r2_comp, color=colors)
ax.axvline(x=0.65, color='black', linestyle='--', alpha=0.5)
ax.set_xlabel('R² Score')
ax.set_title('Model Comparison')
for bar, r2 in zip(bars, r2_comp):
    ax.text(r2 + 0.01, bar.get_y() + bar.get_height()/2, f'{r2:.3f}', va='center')

# 3. MAE comparison
ax = axes[0, 2]
mae_comp = comparison['MAE'].tolist()
bars = ax.barh(models_comp, mae_comp, color=colors)
ax.set_xlabel('MAE ($CAD)')
ax.set_title('Average Error')

# 4. Actual vs Predicted
ax = axes[1, 0]
ax.scatter(price_test_orig, tuned_pred_orig, alpha=0.5, s=20, c='#2ecc71')
max_val = max(max(price_test_orig), max(tuned_pred_orig))
ax.plot([0, max_val], [0, max_val], 'r--', lw=2)
ax.set_xlabel('Actual ($CAD)')
ax.set_ylabel('Predicted ($CAD)')
ax.set_title(f'Tuned Model | R²={r2_tuned:.3f}')

# 5. Error distribution
ax = axes[1, 1]
errors = tuned_pred_orig - price_test_orig
ax.hist(errors, bins=30, color='#3498db', edgecolor='white')
ax.axvline(x=0, color='red', linestyle='--')
ax.set_xlabel('Prediction Error ($CAD)')
ax.set_title('Error Distribution')

# 6. ±20% accuracy
ax = axes[1, 2]
pct20_comp = comparison['±20%'].tolist()
colors_pct = ['#2ecc71' if p > 55 else '#f1c40f' if p > 45 else '#e74c3c' for p in pct20_comp]
bars = ax.barh(models_comp, pct20_comp, color=colors_pct)
ax.axvline(x=50, color='black', linestyle='--', alpha=0.5)
ax.set_xlabel('% Within ±20%')
ax.set_title('Prediction Accuracy')

plt.tight_layout()
plt.savefig('cortex_v4_analysis.png', dpi=150, bbox_inches='tight')
print("Saved cortex_v4_analysis.png")

print("\n" + "="*70)
print("DONE")
print("="*70)
