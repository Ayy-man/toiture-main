#!/usr/bin/env python3
"""Analyze material line items for quantity prediction feasibility"""
import pandas as pd
import numpy as np

DATA_PATH = "/Users/aymanbaig/Desktop/cortex-data/"
materials = pd.read_csv(f"{DATA_PATH}Quote Materials_clean.csv")

print("="*60)
print("MATERIAL LINE ITEM ANALYSIS")
print("="*60)
print(f"Total line items: {len(materials):,}")
print(f"Unique material_ids: {materials['material_id'].nunique():,}")
print(f"Unique quotes: {materials['quote_id'].nunique():,}")

print("\n" + "="*60)
print("TOP 20 MOST COMMON MATERIALS")
print("="*60)
top_materials = materials.groupby('material_id').agg({
    'id': 'count',
    'description': 'first',
    'quantity': 'mean',
    'unit_cost': 'mean',
    'sell_price': 'mean'
}).sort_values('id', ascending=False).head(20)
top_materials.columns = ['count', 'description', 'avg_qty', 'avg_unit_cost', 'avg_sell_price']
top_materials['avg_markup'] = ((top_materials['avg_sell_price'] - top_materials['avg_unit_cost']) / top_materials['avg_unit_cost'] * 100).round(1)

for mid, row in top_materials.iterrows():
    desc = str(row['description'])[:50] if pd.notna(row['description']) else 'No desc'
    print(f"\nID {mid}: {row['count']:,} uses")
    print(f"  {desc}")
    print(f"  Qty: {row['avg_qty']:.1f}, Cost: ${row['avg_unit_cost']:.2f}, Sell: ${row['avg_sell_price']:.2f}, Markup: {row['avg_markup']:.1f}%")

print("\n" + "="*60)
print("UNIT COST CONSISTENCY")
print("="*60)
cost_variance = materials.groupby('material_id').agg({
    'unit_cost': ['mean', 'std', 'count']
}).reset_index()
cost_variance.columns = ['material_id', 'mean_cost', 'std_cost', 'count']
cost_variance = cost_variance[cost_variance['count'] >= 10]
cost_variance['cv'] = (cost_variance['std_cost'] / cost_variance['mean_cost'] * 100).round(1)

print(f"Materials used 10+ times: {len(cost_variance)}")
print(f"Avg coefficient of variation: {cost_variance['cv'].mean():.1f}%")
print(f"Stable (CV < 10%): {(cost_variance['cv'] < 10).sum()}")
print(f"Unstable (CV > 50%): {(cost_variance['cv'] > 50).sum()}")

print("\n" + "="*60)
print("PRICE TRENDS (top 3 materials)")
print("="*60)
materials['year'] = pd.to_datetime(materials['created_at']).dt.year
for i, (mid, row) in enumerate(top_materials.head(3).iterrows()):
    mat_data = materials[materials['material_id'] == mid]
    yearly = mat_data.groupby('year')['unit_cost'].agg(['mean', 'count'])
    desc = str(row['description'])[:40] if pd.notna(row['description']) else 'No desc'
    print(f"\n{i+1}. ID {mid}: {desc}")
    print(yearly.round(2))

print("\n" + "="*60)
print("QUANTITY vs SQFT CORRELATION")
print("="*60)
master = pd.read_csv(f"{DATA_PATH}master_quotes_valid.csv")
master_sqft = master[master['sqft_final'].notna()][['quote_id', 'sqft_final']]
mat_with_sqft = materials.merge(master_sqft, on='quote_id', how='inner')
print(f"Material lines with sqft: {len(mat_with_sqft):,}")

print("\nQuantity vs Sqft correlation per material:")
for mid, row in top_materials.head(10).iterrows():
    mat_data = mat_with_sqft[mat_with_sqft['material_id'] == mid]
    if len(mat_data) > 30:
        corr = mat_data['quantity'].corr(mat_data['sqft_final'])
        desc = str(row['description'])[:30] if pd.notna(row['description']) else 'No desc'
        flag = "✓ USEFUL" if abs(corr) > 0.5 else ""
        print(f"  ID {mid}: r={corr:.3f} (n={len(mat_data)}) {flag}")

print("\n" + "="*60)
print("QUANTITY DISTRIBUTION")
print("="*60)
print(f"Min: {materials['quantity'].min():.1f}")
print(f"Max: {materials['quantity'].max():.1f}")
print(f"Median: {materials['quantity'].median():.1f}")
print(f"Zeros: {(materials['quantity'] == 0).sum()} ({(materials['quantity'] == 0).sum()/len(materials)*100:.1f}%)")

print("\n✅ DONE")
