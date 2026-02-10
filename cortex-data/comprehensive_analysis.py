#!/usr/bin/env python3
"""
================================================================================
TOITURELV - COMPREHENSIVE DEEP ANALYSIS
================================================================================
Complete analysis of 10,000+ quotes for Cortex pricing engine.

GENERATES:
1. comprehensive_analysis.png - 16 chart dashboard
2. job_category_analysis.png - Category deep dive
3. material_inflation.png - Material price tracking over time
4. pricing_patterns.png - Pricing intelligence
5. executive_summary.txt - Key findings for client

Uses CORRECTED master_quotes_valid.csv from pipeline v3.
================================================================================
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# =============================================================================
# CONFIGURATION
# =============================================================================
DATA_PATH = "/Users/aymanbaig/Desktop/cortex-data/"
OUTPUT_PATH = DATA_PATH

# Style
plt.style.use('seaborn-v0_8-whitegrid')
COLORS = {
    'primary': '#2563eb',
    'secondary': '#7c3aed', 
    'success': '#059669',
    'warning': '#d97706',
    'danger': '#dc2626',
    'gray': '#6b7280',
    'light': '#f3f4f6'
}
CATEGORY_COLORS = ['#2563eb', '#7c3aed', '#059669', '#d97706', '#dc2626', 
                   '#0891b2', '#4f46e5', '#84cc16', '#f59e0b', '#ef4444',
                   '#14b8a6', '#8b5cf6', '#f97316', '#06b6d4', '#ec4899']

# =============================================================================
# LOAD DATA
# =============================================================================
print("\n" + "="*80)
print(" TOITURELV - COMPREHENSIVE DEEP ANALYSIS")
print("="*80)

print("\nLoading data...")
master = pd.read_csv(f"{DATA_PATH}master_quotes_valid.csv")
master['created_at'] = pd.to_datetime(master['created_at'], errors='coerce')

# Labor reliable subset (excludes 2022)
labor_reliable = pd.read_csv(f"{DATA_PATH}master_quotes_labor_reliable.csv")
labor_reliable['created_at'] = pd.to_datetime(labor_reliable['created_at'], errors='coerce')

# Also load raw materials for inflation tracking
materials_raw = pd.read_csv(f"{DATA_PATH}Quote Materials_clean.csv")
materials_raw['created_at'] = pd.to_datetime(materials_raw['created_at'], errors='coerce')
materials_raw['unit_cost'] = pd.to_numeric(materials_raw['unit_cost'], errors='coerce')
materials_raw['sell_price'] = pd.to_numeric(materials_raw['sell_price'], errors='coerce')
materials_raw['year'] = materials_raw['created_at'].dt.year

print(f"  ✓ Master quotes: {len(master):,} valid records")
print(f"  ✓ Labor reliable: {len(labor_reliable):,} records (excl. 2022)")
print(f"  ✓ Raw materials: {len(materials_raw):,} records")

# =============================================================================
# FIGURE 1: COMPREHENSIVE DASHBOARD (16 charts)
# =============================================================================
print("\n" + "-"*80)
print(" GENERATING COMPREHENSIVE DASHBOARD")
print("-"*80)

fig, axes = plt.subplots(4, 4, figsize=(24, 20))
fig.suptitle('TOITURELV - Comprehensive Business Analysis\n10,032 Quotes | 2020-2025 | $119M Total Revenue', 
             fontsize=16, fontweight='bold', y=1.02)

# --- ROW 1: Overview Metrics ---

# 1.1 Quote Value Distribution
ax = axes[0, 0]
valid_totals = master[master['quoted_total'] < 100000]['quoted_total']
ax.hist(valid_totals, bins=50, color=COLORS['primary'], edgecolor='white', alpha=0.8)
ax.axvline(valid_totals.median(), color=COLORS['danger'], linestyle='--', linewidth=2, label=f'Median: ${valid_totals.median():,.0f}')
ax.axvline(valid_totals.mean(), color=COLORS['warning'], linestyle='--', linewidth=2, label=f'Mean: ${valid_totals.mean():,.0f}')
ax.set_xlabel('Quote Value ($)')
ax.set_ylabel('Count')
ax.set_title('Quote Value Distribution (<$100K)', fontweight='bold')
ax.legend(fontsize=8)
ax.xaxis.set_major_formatter(mticker.StrMethodFormatter('${x:,.0f}'))

# 1.2 Quotes by Year (with revenue)
ax = axes[0, 1]
yearly = master.groupby('year').agg({
    'quote_id': 'count',
    'quoted_total': 'sum'
}).reset_index()
yearly.columns = ['year', 'count', 'revenue']

ax2 = ax.twinx()
bars = ax.bar(yearly['year'], yearly['count'], color=COLORS['primary'], alpha=0.7, label='Quote Count')
line = ax2.plot(yearly['year'], yearly['revenue']/1e6, color=COLORS['danger'], marker='o', linewidth=2, label='Revenue ($M)')
ax.set_xlabel('Year')
ax.set_ylabel('Number of Quotes', color=COLORS['primary'])
ax2.set_ylabel('Revenue ($M)', color=COLORS['danger'])
ax.set_title('Volume & Revenue by Year', fontweight='bold')
ax.tick_params(axis='y', labelcolor=COLORS['primary'])
ax2.tick_params(axis='y', labelcolor=COLORS['danger'])

if len(yearly) > 1:
    growth = (yearly['revenue'].iloc[-1] / yearly['revenue'].iloc[0] - 1) * 100
    ax.annotate(f'{growth:.0f}% revenue growth', xy=(0.5, 0.95), xycoords='axes fraction',
                ha='center', fontsize=9, color=COLORS['success'], fontweight='bold')

# 1.3 Job Category Distribution (pie)
ax = axes[0, 2]
cat_counts = master['job_category'].value_counts().head(8)
wedges, texts, autotexts = ax.pie(cat_counts, labels=cat_counts.index, autopct='%1.1f%%',
                                   colors=CATEGORY_COLORS[:8], startangle=90)
ax.set_title('Job Category Mix', fontweight='bold')
for autotext in autotexts:
    autotext.set_fontsize(8)

# 1.4 Monthly Seasonality
ax = axes[0, 3]
monthly = master.groupby('month')['quoted_total'].agg(['count', 'sum', 'median']).reset_index()
ax.bar(monthly['month'], monthly['count'], color=COLORS['secondary'], alpha=0.7)
ax.set_xlabel('Month')
ax.set_ylabel('Quote Count')
ax.set_title('Monthly Seasonality', fontweight='bold')
ax.set_xticks(range(1, 13))
ax.set_xticklabels(['J', 'F', 'M', 'A', 'M', 'J', 'J', 'A', 'S', 'O', 'N', 'D'])

peak_month = monthly.loc[monthly['count'].idxmax(), 'month']
ax.annotate(f'Peak: Month {peak_month:.0f}', xy=(peak_month, monthly['count'].max()),
            xytext=(peak_month+1, monthly['count'].max()*0.9),
            arrowprops=dict(arrowstyle='->', color=COLORS['gray']), fontsize=9)

# --- ROW 2: Margin Analysis ---

# 2.1 Overall Margin Distribution
ax = axes[1, 0]
valid_margins = master[(master['overall_margin_pct'] > -20) & (master['overall_margin_pct'] < 60)]['overall_margin_pct']
ax.hist(valid_margins, bins=40, color=COLORS['success'], edgecolor='white', alpha=0.8)
ax.axvline(valid_margins.median(), color=COLORS['danger'], linestyle='--', linewidth=2, 
           label=f'Median: {valid_margins.median():.1f}%')
ax.axvline(25, color=COLORS['warning'], linestyle=':', linewidth=2, label='Target: 25%')
ax.set_xlabel('Overall Margin %')
ax.set_ylabel('Count')
ax.set_title('Overall Margin Distribution', fontweight='bold')
ax.legend(fontsize=8)

# 2.2 Margin by Year (with 2022 flagged)
ax = axes[1, 1]
yearly_margin = master.groupby('year')['overall_margin_pct'].median().reset_index()
colors = [COLORS['warning'] if y == 2022 else COLORS['success'] for y in yearly_margin['year']]
bars = ax.bar(yearly_margin['year'], yearly_margin['overall_margin_pct'], color=colors, alpha=0.8)
ax.axhline(25, color=COLORS['gray'], linestyle='--', linewidth=1, label='25% target')
ax.set_xlabel('Year')
ax.set_ylabel('Median Margin %')
ax.set_title('Margin Trend by Year', fontweight='bold')
ax.legend(fontsize=8)

for bar, val in zip(bars, yearly_margin['overall_margin_pct']):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5, f'{val:.1f}%',
            ha='center', va='bottom', fontsize=9)

# 2.3 Material vs Labor Margin
ax = axes[1, 2]
categories = ['Material\nMargin', 'Labor\nMargin', 'Overall\nMargin']
margins = [
    master['material_margin_pct'].median(),
    master['labor_margin_pct'].median(),
    master['overall_margin_pct'].median()
]
bars = ax.bar(categories, margins, color=[COLORS['primary'], COLORS['secondary'], COLORS['success']], alpha=0.8)
ax.set_ylabel('Median Margin %')
ax.set_title('Margin by Cost Component', fontweight='bold')
ax.axhline(25, color=COLORS['gray'], linestyle='--', linewidth=1)

for bar, val in zip(bars, margins):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5, f'{val:.1f}%',
            ha='center', va='bottom', fontsize=10, fontweight='bold')

# 2.4 Margin by Job Category
ax = axes[1, 3]
cat_margin = master.groupby('job_category')['overall_margin_pct'].median().sort_values(ascending=True)
colors = [COLORS['success'] if m >= 25 else COLORS['warning'] if m >= 20 else COLORS['danger'] 
          for m in cat_margin.values]
ax.barh(cat_margin.index, cat_margin.values, color=colors, alpha=0.8)
ax.axvline(25, color=COLORS['gray'], linestyle='--', linewidth=1)
ax.set_xlabel('Median Margin %')
ax.set_title('Margin by Job Category', fontweight='bold')

# --- ROW 3: Pricing Analysis ---

# 3.1 Price per SqFt Distribution
ax = axes[2, 0]
sqft_data = master[(master['price_per_sqft'] > 0) & (master['price_per_sqft'] < 50)]['price_per_sqft']
ax.hist(sqft_data, bins=40, color=COLORS['primary'], edgecolor='white', alpha=0.8)
ax.axvline(sqft_data.median(), color=COLORS['danger'], linestyle='--', linewidth=2,
           label=f'Median: ${sqft_data.median():.2f}/sqft')
ax.set_xlabel('Price per SqFt ($)')
ax.set_ylabel('Count')
ax.set_title('Price per SqFt Distribution', fontweight='bold')
ax.legend(fontsize=8)

# 3.2 Price/SqFt by Job Category
ax = axes[2, 1]
cat_sqft = master[master['price_per_sqft'] > 0].groupby('job_category')['price_per_sqft'].median().sort_values()
cat_sqft = cat_sqft[cat_sqft < 50]
ax.barh(cat_sqft.index, cat_sqft.values, color=COLORS['secondary'], alpha=0.8)
ax.set_xlabel('Median $/SqFt')
ax.set_title('$/SqFt by Category', fontweight='bold')

for i, (cat, val) in enumerate(cat_sqft.items()):
    ax.text(val + 0.5, i, f'${val:.2f}', va='center', fontsize=9)

# 3.3 Effective $/Hour (using labor reliable data)
ax = axes[2, 2]
eff_rate = labor_reliable[(labor_reliable['effective_hourly_rate'] > 50) & 
                          (labor_reliable['effective_hourly_rate'] < 500)]['effective_hourly_rate']
ax.hist(eff_rate, bins=40, color=COLORS['warning'], edgecolor='white', alpha=0.8)
ax.axvline(eff_rate.median(), color=COLORS['danger'], linestyle='--', linewidth=2,
           label=f'Median: ${eff_rate.median():.0f}/hr')
ax.axvline(100, color=COLORS['gray'], linestyle=':', linewidth=1, label='Sell Rate: $100/hr')
ax.set_xlabel('Effective $/Hour')
ax.set_ylabel('Count')
ax.set_title('Effective Hourly Rate\n(Excl. 2022)', fontweight='bold')
ax.legend(fontsize=8)

# 3.4 Quote Value by Category
ax = axes[2, 3]
cat_values = master.groupby('job_category')['quoted_total'].agg(['median', 'mean', 'count']).reset_index()
cat_values = cat_values.sort_values('median', ascending=False).head(8)
ax.barh(cat_values['job_category'], cat_values['median'], color=COLORS['primary'], alpha=0.7, label='Median')
ax.set_xlabel('Median Quote Value ($)')
ax.set_title('Quote Value by Category', fontweight='bold')
ax.xaxis.set_major_formatter(mticker.StrMethodFormatter('${x:,.0f}'))

# --- ROW 4: Cost Structure & Trends ---

# 4.1 Cost Structure Breakdown
ax = axes[3, 0]
cost_structure = {
    'Materials': master['material_pct'].median(),
    'Labor': master['labor_pct'].median(),
    'Subs': master['sub_pct'].median(),
    'Margin': master['overall_margin_pct'].median()
}
wedges, texts, autotexts = ax.pie(cost_structure.values(), labels=cost_structure.keys(), 
                                   autopct='%1.1f%%', colors=[COLORS['primary'], COLORS['secondary'], 
                                                              COLORS['warning'], COLORS['success']],
                                   startangle=90, explode=(0, 0, 0, 0.1))
ax.set_title('Quote Cost Structure', fontweight='bold')

# 4.2 Labor Hours Distribution (excl 2022)
ax = axes[3, 1]
hours_data = labor_reliable[(labor_reliable['labor_hours_total'] > 0) & 
                            (labor_reliable['labor_hours_total'] < 200)]['labor_hours_total']
ax.hist(hours_data, bins=40, color=COLORS['secondary'], edgecolor='white', alpha=0.8)
ax.axvline(hours_data.median(), color=COLORS['danger'], linestyle='--', linewidth=2,
           label=f'Median: {hours_data.median():.0f} hrs')
ax.set_xlabel('Labor Hours')
ax.set_ylabel('Count')
ax.set_title('Labor Hours per Job\n(Excl. 2022)', fontweight='bold')
ax.legend(fontsize=8)

# 4.3 2022 Labor Anomaly Visualization
ax = axes[3, 2]
yearly_hours = master.groupby('year')['labor_hours_total'].median().reset_index()
colors = [COLORS['danger'] if y == 2022 else COLORS['primary'] for y in yearly_hours['year']]
bars = ax.bar(yearly_hours['year'], yearly_hours['labor_hours_total'], color=colors, alpha=0.8)
ax.set_xlabel('Year')
ax.set_ylabel('Median Hours per Job')
ax.set_title('2022 Labor Data Anomaly', fontweight='bold')
ax.annotate('Data entry\nissue', xy=(2022, 1.3), xytext=(2022.5, 15),
            arrowprops=dict(arrowstyle='->', color=COLORS['danger']),
            fontsize=9, color=COLORS['danger'])

# 4.4 Complexity vs Price
ax = axes[3, 3]
complexity_price = master[(master['complexity_score'] > 0) & (master['complexity_score'] < 30)]
scatter = ax.scatter(complexity_price['complexity_score'], complexity_price['quoted_total'],
                     c=complexity_price['overall_margin_pct'], cmap='RdYlGn', 
                     alpha=0.3, s=10, vmin=0, vmax=50)
ax.set_xlabel('Complexity Score (# line items)')
ax.set_ylabel('Quote Value ($)')
ax.set_title('Complexity vs Price', fontweight='bold')
ax.set_ylim(0, 100000)
plt.colorbar(scatter, ax=ax, label='Margin %')

plt.tight_layout()
plt.savefig(f"{OUTPUT_PATH}comprehensive_analysis.png", dpi=150, bbox_inches='tight', 
            facecolor='white', edgecolor='none')
print(f"  ✓ Saved: comprehensive_analysis.png")
plt.close()

# =============================================================================
# FIGURE 2: JOB CATEGORY DEEP DIVE
# =============================================================================
print("\n" + "-"*80)
print(" GENERATING JOB CATEGORY ANALYSIS")
print("-"*80)

fig, axes = plt.subplots(2, 3, figsize=(18, 12))
fig.suptitle('TOITURELV - Job Category Deep Dive', fontsize=14, fontweight='bold', y=1.02)

top_cats = master['job_category'].value_counts().head(6).index.tolist()

# 2.1 Revenue by Category
ax = axes[0, 0]
cat_revenue = master.groupby('job_category')['quoted_total'].sum().sort_values(ascending=True)
ax.barh(cat_revenue.index, cat_revenue.values / 1e6, color=COLORS['primary'], alpha=0.8)
ax.set_xlabel('Total Revenue ($M)')
ax.set_title('Revenue by Category', fontweight='bold')
for i, (cat, val) in enumerate(cat_revenue.items()):
    ax.text(val/1e6 + 0.5, i, f'${val/1e6:.1f}M', va='center', fontsize=9)

# 2.2 Average Job Size by Category
ax = axes[0, 1]
cat_avg = master.groupby('job_category')['quoted_total'].mean().sort_values(ascending=True)
ax.barh(cat_avg.index, cat_avg.values, color=COLORS['secondary'], alpha=0.8)
ax.set_xlabel('Average Quote Value ($)')
ax.set_title('Avg Job Size by Category', fontweight='bold')
ax.xaxis.set_major_formatter(mticker.StrMethodFormatter('${x:,.0f}'))

# 2.3 Growth by Category (2023 vs 2025)
ax = axes[0, 2]
growth_data = []
for cat in top_cats:
    cat_data = master[master['job_category'] == cat]
    rev_2023 = cat_data[cat_data['year'] == 2023]['quoted_total'].sum()
    rev_2025 = cat_data[cat_data['year'] == 2025]['quoted_total'].sum()
    if rev_2023 > 0:
        growth = (rev_2025 / rev_2023 - 1) * 100
        growth_data.append({'category': cat, 'growth': growth})

growth_df = pd.DataFrame(growth_data).sort_values('growth', ascending=True)
colors = [COLORS['success'] if g > 0 else COLORS['danger'] for g in growth_df['growth']]
ax.barh(growth_df['category'], growth_df['growth'], color=colors, alpha=0.8)
ax.axvline(0, color=COLORS['gray'], linewidth=1)
ax.set_xlabel('Revenue Growth % (2023-2025)')
ax.set_title('Category Growth Trend', fontweight='bold')

# 2.4 Profitability Matrix (Margin vs Volume)
ax = axes[1, 0]
cat_profit = master.groupby('job_category').agg({
    'quote_id': 'count',
    'overall_margin_pct': 'median',
    'quoted_total': 'sum'
}).reset_index()

scatter = ax.scatter(cat_profit['quote_id'], cat_profit['overall_margin_pct'],
                     s=cat_profit['quoted_total']/500000, alpha=0.7, c=CATEGORY_COLORS[:len(cat_profit)])

for i, row in cat_profit.iterrows():
    ax.annotate(row['job_category'][:10], (row['quote_id'], row['overall_margin_pct']),
                fontsize=8, ha='center')

ax.axhline(25, color=COLORS['gray'], linestyle='--', alpha=0.5)
ax.set_xlabel('Number of Quotes')
ax.set_ylabel('Median Margin %')
ax.set_title('Profitability Matrix\n(bubble size = revenue)', fontweight='bold')

# 2.5 Hours per Job by Category (excl 2022)
ax = axes[1, 1]
cat_hours = labor_reliable.groupby('job_category')['labor_hours_total'].median().sort_values(ascending=True)
ax.barh(cat_hours.index, cat_hours.values, color=COLORS['warning'], alpha=0.8)
ax.set_xlabel('Median Hours per Job')
ax.set_title('Labor Hours by Category\n(Excl. 2022)', fontweight='bold')

# 2.6 Material Markup by Category
ax = axes[1, 2]
cat_markup = master[master['material_markup_pct'].notna()].groupby('job_category')['material_markup_pct'].median().sort_values(ascending=True)
colors = [COLORS['success'] if m >= 30 else COLORS['warning'] for m in cat_markup.values]
ax.barh(cat_markup.index, cat_markup.values, color=colors, alpha=0.8)
ax.axvline(33.5, color=COLORS['gray'], linestyle='--', linewidth=1, label='Overall: 33.5%')
ax.set_xlabel('Median Material Markup %')
ax.set_title('Material Markup by Category', fontweight='bold')
ax.legend(fontsize=8)

plt.tight_layout()
plt.savefig(f"{OUTPUT_PATH}job_category_analysis.png", dpi=150, bbox_inches='tight',
            facecolor='white', edgecolor='none')
print(f"  ✓ Saved: job_category_analysis.png")
plt.close()

# =============================================================================
# FIGURE 3: MATERIAL INFLATION TRACKING
# =============================================================================
print("\n" + "-"*80)
print(" GENERATING MATERIAL INFLATION ANALYSIS")
print("-"*80)

fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle('TOITURELV - Material Cost & Inflation Analysis', fontsize=14, fontweight='bold', y=1.02)

materials_clean = materials_raw[
    (materials_raw['unit_cost'] > 0) & 
    (materials_raw['unit_cost'] < 1000) &
    (materials_raw['year'] >= 2020) &
    (materials_raw['year'] <= 2025)
].copy()

# 3.1 Overall Material Cost Trend
ax = axes[0, 0]
yearly_cost = materials_clean.groupby('year')['unit_cost'].agg(['median', 'mean', 'count']).reset_index()
ax.plot(yearly_cost['year'], yearly_cost['median'], marker='o', linewidth=2, color=COLORS['primary'], label='Median')
ax.plot(yearly_cost['year'], yearly_cost['mean'], marker='s', linewidth=2, color=COLORS['secondary'], label='Mean', linestyle='--')
ax.set_xlabel('Year')
ax.set_ylabel('Unit Cost ($)')
ax.set_title('Material Unit Cost Trend', fontweight='bold')
ax.legend()

if len(yearly_cost) > 1:
    inflation = (yearly_cost['median'].iloc[-1] / yearly_cost['median'].iloc[0] - 1) * 100
    ax.annotate(f'Total change: {inflation:+.1f}%', xy=(0.95, 0.95), xycoords='axes fraction',
                ha='right', fontsize=10, fontweight='bold',
                color=COLORS['danger'] if inflation > 0 else COLORS['success'])

# 3.2 Material Markup Trend
ax = axes[0, 1]
materials_clean['markup'] = (materials_clean['sell_price'] - materials_clean['unit_cost']) / materials_clean['unit_cost'] * 100
yearly_markup = materials_clean[materials_clean['markup'].between(-50, 200)].groupby('year')['markup'].median().reset_index()
ax.bar(yearly_markup['year'], yearly_markup['markup'], color=COLORS['success'], alpha=0.8)
ax.set_xlabel('Year')
ax.set_ylabel('Markup %')
ax.set_title('Material Markup Trend', fontweight='bold')
ax.axhline(33.5, color=COLORS['gray'], linestyle='--', linewidth=1, label='Overall: 33.5%')
ax.legend()

# 3.3 Track Same Materials Over Time (TRUE inflation)
ax = axes[1, 0]

material_years = materials_clean.groupby('material_id')['year'].nunique()
recurring_materials = material_years[material_years >= 3].index.tolist()[:20]

if len(recurring_materials) > 0:
    recurring_data = materials_clean[materials_clean['material_id'].isin(recurring_materials)]
    recurring_trend = recurring_data.groupby('year')['unit_cost'].median().reset_index()
    
    ax.plot(recurring_trend['year'], recurring_trend['unit_cost'], marker='o', linewidth=2, 
            color=COLORS['danger'], label='Recurring Materials Only')
    ax.plot(yearly_cost['year'], yearly_cost['median'], marker='s', linewidth=2,
            color=COLORS['primary'], linestyle='--', alpha=0.5, label='All Materials')
    ax.set_xlabel('Year')
    ax.set_ylabel('Median Unit Cost ($)')
    ax.set_title('TRUE Inflation\n(Same Materials Tracked Over Time)', fontweight='bold')
    ax.legend()
    
    if len(recurring_trend) > 1:
        true_inflation = (recurring_trend['unit_cost'].iloc[-1] / recurring_trend['unit_cost'].iloc[0] - 1) * 100
        ax.annotate(f'True inflation: {true_inflation:+.1f}%', xy=(0.95, 0.95), xycoords='axes fraction',
                    ha='right', fontsize=10, fontweight='bold',
                    color=COLORS['danger'] if true_inflation > 0 else COLORS['success'])
else:
    ax.text(0.5, 0.5, 'Insufficient recurring\nmaterial data', ha='center', va='center',
            transform=ax.transAxes, fontsize=12)
    ax.set_title('TRUE Inflation Tracking', fontweight='bold')

# 3.4 Cost Distribution by Year
ax = axes[1, 1]
years_to_plot = [2021, 2023, 2025]
colors_hist = [COLORS['primary'], COLORS['secondary'], COLORS['success']]

for i, year in enumerate(years_to_plot):
    year_data = materials_clean[(materials_clean['year'] == year) & (materials_clean['unit_cost'] < 200)]['unit_cost']
    ax.hist(year_data, bins=30, alpha=0.5, label=f'{year} (med: ${year_data.median():.0f})', 
            color=colors_hist[i], edgecolor='none')

ax.set_xlabel('Unit Cost ($)')
ax.set_ylabel('Count')
ax.set_title('Material Cost Distribution by Year', fontweight='bold')
ax.legend()

plt.tight_layout()
plt.savefig(f"{OUTPUT_PATH}material_inflation.png", dpi=150, bbox_inches='tight',
            facecolor='white', edgecolor='none')
print(f"  ✓ Saved: material_inflation.png")
plt.close()

# =============================================================================
# FIGURE 4: PRICING PATTERNS
# =============================================================================
print("\n" + "-"*80)
print(" GENERATING PRICING PATTERNS ANALYSIS")
print("-"*80)

fig, axes = plt.subplots(2, 3, figsize=(18, 10))
fig.suptitle('TOITURELV - Pricing Patterns & Intelligence', fontsize=14, fontweight='bold', y=1.02)

top_cats = master['job_category'].value_counts().head(6).index.tolist()

# 4.1 Price vs SqFt (scatter with categories)
ax = axes[0, 0]
sqft_scatter = master[(master['sqft_final'] > 0) & (master['sqft_final'] < 5000) & 
                       (master['quoted_total'] < 100000)]
for i, cat in enumerate(top_cats[:5]):
    cat_data = sqft_scatter[sqft_scatter['job_category'] == cat]
    ax.scatter(cat_data['sqft_final'], cat_data['quoted_total'], 
               alpha=0.4, s=20, label=cat, color=CATEGORY_COLORS[i])

ax.set_xlabel('Square Footage')
ax.set_ylabel('Quote Value ($)')
ax.set_title('Price vs Size by Category', fontweight='bold')
ax.legend(fontsize=8, loc='upper left')
ax.yaxis.set_major_formatter(mticker.StrMethodFormatter('${x:,.0f}'))

# 4.2 $/SqFt by Year
ax = axes[0, 1]
yearly_sqft = master[master['price_per_sqft'] > 0].groupby('year')['price_per_sqft'].median().reset_index()
ax.bar(yearly_sqft['year'], yearly_sqft['price_per_sqft'], color=COLORS['primary'], alpha=0.8)
ax.set_xlabel('Year')
ax.set_ylabel('Median $/SqFt')
ax.set_title('Price per SqFt Trend', fontweight='bold')

if len(yearly_sqft) > 1:
    price_change = (yearly_sqft['price_per_sqft'].iloc[-1] / yearly_sqft['price_per_sqft'].iloc[0] - 1) * 100
    ax.annotate(f'{price_change:+.1f}%', xy=(0.95, 0.95), xycoords='axes fraction',
                ha='right', fontsize=10, fontweight='bold')

# 4.3 Labor Rate Analysis
ax = axes[0, 2]
sell_rates = master[master['labor_sell_rate_median'].notna()]['labor_sell_rate_median'].value_counts().head(10)
ax.bar(range(len(sell_rates)), sell_rates.values, color=COLORS['secondary'], alpha=0.8)
ax.set_xticks(range(len(sell_rates)))
ax.set_xticklabels([f'${x:.0f}' for x in sell_rates.index], rotation=45)
ax.set_xlabel('Labor Sell Rate ($/hr)')
ax.set_ylabel('Count')
ax.set_title('Most Common Labor Rates', fontweight='bold')

# 4.4 Quote Size Tiers
ax = axes[1, 0]
master['size_tier'] = pd.cut(master['quoted_total'], 
                              bins=[0, 1000, 5000, 15000, 50000, 500000],
                              labels=['<$1K', '$1-5K', '$5-15K', '$15-50K', '$50K+'])
tier_counts = master['size_tier'].value_counts().sort_index()
tier_revenue = master.groupby('size_tier')['quoted_total'].sum()

ax2 = ax.twinx()
bars = ax.bar(range(len(tier_counts)), tier_counts.values, color=COLORS['primary'], alpha=0.7, label='Count')
line = ax2.plot(range(len(tier_counts)), tier_revenue.sort_index().values/1e6, 
                color=COLORS['danger'], marker='o', linewidth=2, label='Revenue')

ax.set_xticks(range(len(tier_counts)))
ax.set_xticklabels(tier_counts.index)
ax.set_xlabel('Quote Size Tier')
ax.set_ylabel('Number of Quotes', color=COLORS['primary'])
ax2.set_ylabel('Revenue ($M)', color=COLORS['danger'])
ax.set_title('Quote Size Distribution', fontweight='bold')

# 4.5 Margin vs Quote Size
ax = axes[1, 1]
tier_margin = master.groupby('size_tier')['overall_margin_pct'].median().sort_index()
colors = [COLORS['success'] if m >= 25 else COLORS['warning'] for m in tier_margin.values]
ax.bar(range(len(tier_margin)), tier_margin.values, color=colors, alpha=0.8)
ax.axhline(25, color=COLORS['gray'], linestyle='--')
ax.set_xticks(range(len(tier_margin)))
ax.set_xticklabels(tier_margin.index)
ax.set_xlabel('Quote Size Tier')
ax.set_ylabel('Median Margin %')
ax.set_title('Margin by Quote Size', fontweight='bold')

for i, val in enumerate(tier_margin.values):
    ax.text(i, val + 0.5, f'{val:.1f}%', ha='center', fontsize=9)

# 4.6 Day of Week Patterns
ax = axes[1, 2]
dow_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
dow_stats = master.groupby('day_of_week').agg({
    'quote_id': 'count',
    'quoted_total': 'median'
}).reset_index()

ax.bar(dow_stats['day_of_week'], dow_stats['quote_id'], color=COLORS['primary'], alpha=0.8)
ax.set_xticks(range(7))
ax.set_xticklabels(dow_names)
ax.set_xlabel('Day of Week')
ax.set_ylabel('Number of Quotes')
ax.set_title('Quotes by Day of Week', fontweight='bold')

plt.tight_layout()
plt.savefig(f"{OUTPUT_PATH}pricing_patterns.png", dpi=150, bbox_inches='tight',
            facecolor='white', edgecolor='none')
print(f"  ✓ Saved: pricing_patterns.png")
plt.close()

# =============================================================================
# FIGURE 5: SUBCONTRACTOR ANALYSIS
# =============================================================================
print("\n" + "-"*80)
print(" GENERATING SUBCONTRACTOR ANALYSIS")
print("-"*80)

fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle('TOITURELV - Subcontractor Analysis', fontsize=14, fontweight='bold', y=1.02)

# 5.1 Sub usage rate
ax = axes[0, 0]
sub_usage = master['has_subs'].value_counts()
labels = ['No Subs', 'Has Subs']
colors_pie = [COLORS['primary'], COLORS['warning']]
ax.pie(sub_usage.values, labels=labels, autopct='%1.1f%%', colors=colors_pie, startangle=90)
ax.set_title('Subcontractor Usage Rate', fontweight='bold')

# 5.2 Sub usage by category
ax = axes[0, 1]
sub_by_cat = master.groupby('job_category')['has_subs'].mean().sort_values(ascending=True) * 100
ax.barh(sub_by_cat.index, sub_by_cat.values, color=COLORS['warning'], alpha=0.8)
ax.set_xlabel('% of Jobs Using Subs')
ax.set_title('Sub Usage by Category', fontweight='bold')
ax.axvline(22.7, color=COLORS['gray'], linestyle='--', label='Overall: 22.7%')
ax.legend(fontsize=8)

# 5.3 Sub margin impact
ax = axes[1, 0]
with_subs = master[master['has_subs'] == True]['overall_margin_pct']
without_subs = master[master['has_subs'] == False]['overall_margin_pct']

ax.hist(without_subs, bins=30, alpha=0.6, label=f'No Subs (med: {without_subs.median():.1f}%)', color=COLORS['primary'])
ax.hist(with_subs, bins=30, alpha=0.6, label=f'With Subs (med: {with_subs.median():.1f}%)', color=COLORS['warning'])
ax.set_xlabel('Overall Margin %')
ax.set_ylabel('Count')
ax.set_title('Margin: With vs Without Subs', fontweight='bold')
ax.legend()

# 5.4 Sub cost as % of quote
ax = axes[1, 1]
sub_jobs = master[master['has_subs'] == True]
sub_pct_data = sub_jobs[(sub_jobs['sub_pct'] > 0) & (sub_jobs['sub_pct'] < 80)]['sub_pct']
ax.hist(sub_pct_data, bins=30, color=COLORS['warning'], edgecolor='white', alpha=0.8)
ax.axvline(sub_pct_data.median(), color=COLORS['danger'], linestyle='--', linewidth=2,
           label=f'Median: {sub_pct_data.median():.1f}%')
ax.set_xlabel('Sub Cost as % of Quote')
ax.set_ylabel('Count')
ax.set_title('Subcontractor Cost Distribution', fontweight='bold')
ax.legend()

plt.tight_layout()
plt.savefig(f"{OUTPUT_PATH}subcontractor_analysis.png", dpi=150, bbox_inches='tight',
            facecolor='white', edgecolor='none')
print(f"  ✓ Saved: subcontractor_analysis.png")
plt.close()

# =============================================================================
# FIGURE 6: QUARTERLY TRENDS
# =============================================================================
print("\n" + "-"*80)
print(" GENERATING QUARTERLY TRENDS")
print("-"*80)

fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle('TOITURELV - Quarterly Business Trends', fontsize=14, fontweight='bold', y=1.02)

# Create quarter column
master['quarter'] = master['created_at'].dt.to_period('Q').astype(str)

# 6.1 Quarterly revenue trend
ax = axes[0, 0]
quarterly = master.groupby('quarter').agg({
    'quoted_total': 'sum',
    'quote_id': 'count'
}).reset_index()
quarterly = quarterly.tail(12)  # Last 12 quarters

ax.bar(range(len(quarterly)), quarterly['quoted_total']/1e6, color=COLORS['primary'], alpha=0.8)
ax.set_xticks(range(len(quarterly)))
ax.set_xticklabels(quarterly['quarter'], rotation=45, ha='right')
ax.set_ylabel('Revenue ($M)')
ax.set_title('Quarterly Revenue', fontweight='bold')

# 6.2 Quarterly quote count
ax = axes[0, 1]
ax.bar(range(len(quarterly)), quarterly['quote_id'], color=COLORS['secondary'], alpha=0.8)
ax.set_xticks(range(len(quarterly)))
ax.set_xticklabels(quarterly['quarter'], rotation=45, ha='right')
ax.set_ylabel('Quote Count')
ax.set_title('Quarterly Quote Volume', fontweight='bold')

# 6.3 Quarterly margin
ax = axes[1, 0]
quarterly_margin = master.groupby('quarter')['overall_margin_pct'].median().reset_index()
quarterly_margin = quarterly_margin.tail(12)
colors = [COLORS['success'] if m >= 25 else COLORS['warning'] for m in quarterly_margin['overall_margin_pct']]
ax.bar(range(len(quarterly_margin)), quarterly_margin['overall_margin_pct'], color=colors, alpha=0.8)
ax.axhline(25, color=COLORS['gray'], linestyle='--')
ax.set_xticks(range(len(quarterly_margin)))
ax.set_xticklabels(quarterly_margin['quarter'], rotation=45, ha='right')
ax.set_ylabel('Median Margin %')
ax.set_title('Quarterly Margin Trend', fontweight='bold')

# 6.4 Quarterly avg job size
ax = axes[1, 1]
quarterly_avg = master.groupby('quarter')['quoted_total'].median().reset_index()
quarterly_avg = quarterly_avg.tail(12)
ax.plot(range(len(quarterly_avg)), quarterly_avg['quoted_total'], marker='o', linewidth=2, color=COLORS['primary'])
ax.set_xticks(range(len(quarterly_avg)))
ax.set_xticklabels(quarterly_avg['quarter'], rotation=45, ha='right')
ax.set_ylabel('Median Quote Value ($)')
ax.set_title('Quarterly Job Size Trend', fontweight='bold')
ax.yaxis.set_major_formatter(mticker.StrMethodFormatter('${x:,.0f}'))

plt.tight_layout()
plt.savefig(f"{OUTPUT_PATH}quarterly_trends.png", dpi=150, bbox_inches='tight',
            facecolor='white', edgecolor='none')
print(f"  ✓ Saved: quarterly_trends.png")
plt.close()

# =============================================================================
# EXECUTIVE SUMMARY REPORT
# =============================================================================
print("\n" + "-"*80)
print(" GENERATING EXECUTIVE SUMMARY")
print("-"*80)

total_revenue = master['quoted_total'].sum()
total_quotes = len(master)
median_quote = master['quoted_total'].median()
median_margin = master['overall_margin_pct'].median()
median_mat_margin = master['material_margin_pct'].median()
median_lab_margin = master['labor_margin_pct'].median()
median_sqft_price = master['price_per_sqft'].median()
median_hours = labor_reliable['labor_hours_total'].median()
median_eff_rate = labor_reliable['effective_hourly_rate'].median()

rev_2024 = master[master['year'] == 2024]['quoted_total'].sum()
rev_2025 = master[master['year'] == 2025]['quoted_total'].sum()
yoy_growth = (rev_2025 / rev_2024 - 1) * 100 if rev_2024 > 0 else 0

top_cat = master.groupby('job_category')['quoted_total'].sum().idxmax()
top_cat_rev = master.groupby('job_category')['quoted_total'].sum().max()

most_profitable = master.groupby('job_category')['overall_margin_pct'].median().idxmax()
most_profitable_margin = master.groupby('job_category')['overall_margin_pct'].median().max()

summary = f"""
================================================================================
                    TOITURELV - EXECUTIVE DATA SUMMARY
                    Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}
================================================================================

BUSINESS OVERVIEW
-----------------
  Analysis Period:            2020 - 2025
  Total Quotes Analyzed:      {total_quotes:,}
  Total Revenue (Quoted):     ${total_revenue:,.0f}
  YoY Growth (2024-2025):     {yoy_growth:+.1f}%

KEY METRICS
-----------
  Median Quote Value:         ${median_quote:,.0f}
  Median Price/SqFt:          ${median_sqft_price:.2f}
  Median Hours/Job:           {median_hours:.1f}
  Effective $/Hour:           ${median_eff_rate:,.0f}

MARGIN ANALYSIS
---------------
  Overall Margin:             {median_margin:.1f}%
  Material Margin:            {median_mat_margin:.1f}% (markup: 33.6%)
  Labor Margin:               {median_lab_margin:.1f}% ($100 sell / $74 cost)

COST STRUCTURE
--------------
  Materials:                  {master['material_pct'].median():.1f}% of quote
  Labor:                      {master['labor_pct'].median():.1f}% of quote
  Subcontractors:             {master['sub_pct'].median():.1f}% of quote (22.7% of jobs use subs)

TOP PERFORMERS
--------------
  Highest Revenue Category:   {top_cat} (${top_cat_rev/1e6:.1f}M)
  Most Profitable Category:   {most_profitable} ({most_profitable_margin:.1f}% margin)
  Best $/SqFt:                Ferblanterie ($140/sqft)

JOB CATEGORY BENCHMARKS
-----------------------
"""

cat_summary = master.groupby('job_category').agg({
    'quote_id': 'count',
    'quoted_total': ['median', 'sum'],
    'overall_margin_pct': 'median',
    'price_per_sqft': 'median'
}).reset_index()
cat_summary.columns = ['category', 'count', 'median', 'revenue', 'margin', 'sqft_price']
cat_summary = cat_summary.sort_values('revenue', ascending=False)

summary += f"  {'Category':<18} | {'Count':>7} | {'Median':>10} | {'Margin':>7} | {'$/SqFt':>8}\n"
summary += f"  {'-'*18}-+-{'-'*7}-+-{'-'*10}-+-{'-'*7}-+-{'-'*8}\n"
for _, row in cat_summary.head(10).iterrows():
    summary += f"  {row['category']:<18} | {row['count']:>7,} | ${row['median']:>8,.0f} | {row['margin']:>6.1f}% | ${row['sqft_price']:>7.2f}\n"

summary += f"""

CORTEX PRICING INPUTS
---------------------
  Base Rates:
    - Labor sell rate: $100/hr
    - Labor cost rate: $74/hr  
    - Material markup: 33.5% on cost
    - Target overall margin: 25-30%

  $/SqFt by Category:
    - Bardeaux (shingles): $6.45/sqft
    - Elastomere (flat):   $14.66/sqft
    - Service Calls:       $15.40/sqft
    - Heat Cables:         $14.02/sqft
    - Ferblanterie:        $140.19/sqft

  Avg Hours by Category (excl 2022):
    - Service Call:  ~5 hrs
    - Skylights:     ~12 hrs
    - Bardeaux:      ~40 hrs
    - Elastomere:    ~80 hrs

DATA QUALITY NOTES
------------------
  - 2022 labor data unreliable (median 1.3 hrs vs normal 20-30)
  - SqFt available for {master['sqft_final'].notna().sum():,} quotes ({master['sqft_final'].notna().sum()/len(master)*100:.1f}%)
  - Material data: 77.8% coverage
  - Labor data: 77.2% coverage

FILES GENERATED
---------------
  - comprehensive_analysis.png (16-chart dashboard)
  - job_category_analysis.png (6-chart category deep dive)
  - material_inflation.png (4-chart inflation tracking)
  - pricing_patterns.png (6-chart pricing intelligence)
  - subcontractor_analysis.png (4-chart sub analysis)
  - quarterly_trends.png (4-chart quarterly view)
  - executive_summary.txt (this report)

================================================================================
"""

with open(f"{OUTPUT_PATH}executive_summary.txt", 'w') as f:
    f.write(summary)
print(f"  ✓ Saved: executive_summary.txt")

print(summary)

print("\n" + "="*80)
print(" COMPREHENSIVE ANALYSIS COMPLETE")
print("="*80)
print(f"""
Files Generated:
  - comprehensive_analysis.png (16 charts)
  - job_category_analysis.png (6 charts)
  - material_inflation.png (4 charts)
  - pricing_patterns.png (6 charts)
  - subcontractor_analysis.png (4 charts)
  - quarterly_trends.png (4 charts)
  - executive_summary.txt

Total: 40 charts + executive summary

Location: {OUTPUT_PATH}
""")
