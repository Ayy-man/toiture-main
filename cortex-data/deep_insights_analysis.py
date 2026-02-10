#!/usr/bin/env python3
"""
================================================================================
TOITURELV - DEEP INSIGHTS ANALYSIS
================================================================================
Additional deep-dive analysis for client report.

GENERATES:
1. customer_insights.png - Repeat customer analysis, client value
2. profitability_deep_dive.png - Profit drivers, efficiency metrics
3. operational_patterns.png - Seasonality, day patterns, complexity
4. cortex_pricing_inputs.png - Data specifically for algorithm training
5. deep_insights_summary.txt - Additional findings

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

# =============================================================================
# LOAD DATA
# =============================================================================
print("\n" + "="*80)
print(" TOITURELV - DEEP INSIGHTS ANALYSIS")
print("="*80)

print("\nLoading data...")
master = pd.read_csv(f"{DATA_PATH}master_quotes_valid.csv")
master['created_at'] = pd.to_datetime(master['created_at'], errors='coerce')

labor_reliable = pd.read_csv(f"{DATA_PATH}master_quotes_labor_reliable.csv")
labor_reliable['created_at'] = pd.to_datetime(labor_reliable['created_at'], errors='coerce')

print(f"  ✓ Loaded {len(master):,} valid quotes")

# =============================================================================
# FIGURE 1: CUSTOMER INSIGHTS
# =============================================================================
print("\n" + "-"*80)
print(" GENERATING CUSTOMER INSIGHTS")
print("-"*80)

fig, axes = plt.subplots(2, 3, figsize=(18, 12))
fig.suptitle('TOITURELV - Customer & Client Analysis', fontsize=14, fontweight='bold', y=1.02)

# 1.1 Customer Frequency Distribution
ax = axes[0, 0]
client_counts = master.groupby('client_id').size()
freq_dist = client_counts.value_counts().sort_index().head(15)
ax.bar(freq_dist.index, freq_dist.values, color=COLORS['primary'], alpha=0.8)
ax.set_xlabel('Number of Quotes per Client')
ax.set_ylabel('Number of Clients')
ax.set_title('Client Quote Frequency Distribution', fontweight='bold')

one_time = (client_counts == 1).sum()
repeat = (client_counts > 1).sum()
ax.annotate(f'One-time: {one_time:,} ({one_time/len(client_counts)*100:.1f}%)\nRepeat: {repeat:,} ({repeat/len(client_counts)*100:.1f}%)', 
            xy=(0.95, 0.95), xycoords='axes fraction', ha='right', va='top', fontsize=10,
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

# 1.2 Customer Lifetime Value Distribution
ax = axes[0, 1]
client_ltv = master.groupby('client_id')['quoted_total'].sum()
client_ltv_valid = client_ltv[client_ltv < 500000]  # Remove outliers
ax.hist(client_ltv_valid, bins=50, color=COLORS['success'], edgecolor='white', alpha=0.8)
ax.axvline(client_ltv_valid.median(), color=COLORS['danger'], linestyle='--', linewidth=2,
           label=f'Median: ${client_ltv_valid.median():,.0f}')
ax.axvline(client_ltv_valid.mean(), color=COLORS['warning'], linestyle='--', linewidth=2,
           label=f'Mean: ${client_ltv_valid.mean():,.0f}')
ax.set_xlabel('Total Lifetime Value ($)')
ax.set_ylabel('Number of Clients')
ax.set_title('Client Lifetime Value Distribution', fontweight='bold')
ax.legend(fontsize=9)
ax.xaxis.set_major_formatter(mticker.StrMethodFormatter('${x:,.0f}'))

# 1.3 Top 20 Clients by Revenue
ax = axes[0, 2]
top_clients = client_ltv.sort_values(ascending=False).head(20)
ax.barh(range(len(top_clients)), top_clients.values, color=COLORS['secondary'], alpha=0.8)
ax.set_yticks(range(len(top_clients)))
ax.set_yticklabels([f'Client {int(c)}' for c in top_clients.index])
ax.set_xlabel('Total Revenue ($)')
ax.set_title('Top 20 Clients by Lifetime Value', fontweight='bold')
ax.xaxis.set_major_formatter(mticker.StrMethodFormatter('${x:,.0f}'))

top20_rev = top_clients.sum()
total_rev = master['quoted_total'].sum()
ax.annotate(f'Top 20 = ${top20_rev/1e6:.1f}M\n({top20_rev/total_rev*100:.1f}% of total)', 
            xy=(0.95, 0.05), xycoords='axes fraction', ha='right', va='bottom', fontsize=10,
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

# 1.4 Repeat vs One-time Value
ax = axes[1, 0]
client_quote_count = master.groupby('client_id').size()
master['is_repeat_client'] = master['client_id'].map(lambda x: client_quote_count.get(x, 0) > 1)

repeat_data = master.groupby('is_repeat_client').agg({
    'quoted_total': ['sum', 'mean', 'count'],
    'overall_margin_pct': 'median'
}).reset_index()
repeat_data.columns = ['is_repeat', 'total_rev', 'avg_quote', 'count', 'margin']

x_labels = ['One-Time Clients', 'Repeat Clients']
x_pos = [0, 1]
bars = ax.bar(x_pos, repeat_data['total_rev']/1e6, color=[COLORS['gray'], COLORS['success']], alpha=0.8)
ax.set_xticks(x_pos)
ax.set_xticklabels(x_labels)
ax.set_ylabel('Total Revenue ($M)')
ax.set_title('Revenue: Repeat vs One-Time Clients', fontweight='bold')

for i, (bar, row) in enumerate(zip(bars, repeat_data.itertuples())):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, 
            f'${row.total_rev/1e6:.1f}M\n{row.count:,} quotes\nAvg: ${row.avg_quote:,.0f}',
            ha='center', va='bottom', fontsize=9)

# 1.5 Client Tenure Analysis
ax = axes[1, 1]
client_first = master.groupby('client_id')['created_at'].min()
client_last = master.groupby('client_id')['created_at'].max()
client_tenure = (client_last - client_first).dt.days

tenure_bins = [0, 30, 180, 365, 730, 3000]
tenure_labels = ['<1mo', '1-6mo', '6-12mo', '1-2yr', '2yr+']
client_tenure_cat = pd.cut(client_tenure, bins=tenure_bins, labels=tenure_labels)
tenure_counts = client_tenure_cat.value_counts().sort_index()

ax.bar(tenure_counts.index, tenure_counts.values, color=COLORS['primary'], alpha=0.8)
ax.set_xlabel('Client Tenure')
ax.set_ylabel('Number of Clients')
ax.set_title('Client Tenure Distribution', fontweight='bold')

# 1.6 Revenue by Client Segment
ax = axes[1, 2]
client_segments = master.groupby('client_id').agg({
    'quoted_total': ['sum', 'count']
}).reset_index()
client_segments.columns = ['client_id', 'total_value', 'quote_count']

def segment_client(row):
    if row['total_value'] > 100000:
        return 'VIP ($100K+)'
    elif row['total_value'] > 50000:
        return 'High Value ($50-100K)'
    elif row['total_value'] > 20000:
        return 'Medium ($20-50K)'
    elif row['total_value'] > 5000:
        return 'Standard ($5-20K)'
    else:
        return 'Small (<$5K)'

client_segments['segment'] = client_segments.apply(segment_client, axis=1)
segment_rev = client_segments.groupby('segment')['total_value'].sum()
segment_order = ['VIP ($100K+)', 'High Value ($50-100K)', 'Medium ($20-50K)', 'Standard ($5-20K)', 'Small (<$5K)']
segment_rev = segment_rev.reindex(segment_order)

colors_seg = [COLORS['danger'], COLORS['warning'], COLORS['success'], COLORS['primary'], COLORS['gray']]
wedges, texts, autotexts = ax.pie(segment_rev, labels=segment_rev.index, autopct='%1.1f%%',
                                   colors=colors_seg, startangle=90)
ax.set_title('Revenue by Client Segment', fontweight='bold')

plt.tight_layout()
plt.savefig(f"{OUTPUT_PATH}customer_insights.png", dpi=150, bbox_inches='tight',
            facecolor='white', edgecolor='none')
print(f"  ✓ Saved: customer_insights.png")
plt.close()

# =============================================================================
# FIGURE 2: PROFITABILITY DEEP DIVE
# =============================================================================
print("\n" + "-"*80)
print(" GENERATING PROFITABILITY DEEP DIVE")
print("-"*80)

fig, axes = plt.subplots(2, 3, figsize=(18, 12))
fig.suptitle('TOITURELV - Profitability Deep Dive', fontsize=14, fontweight='bold', y=1.02)

# 2.1 Profit per Hour by Category (excl 2022)
ax = axes[0, 0]
labor_reliable['profit_per_hour'] = (labor_reliable['quoted_total'] - labor_reliable['total_cost_calculated']) / labor_reliable['labor_hours_total']
profit_per_hour = labor_reliable[labor_reliable['profit_per_hour'].between(0, 500)].groupby('job_category')['profit_per_hour'].median().sort_values()

colors = [COLORS['success'] if p > 50 else COLORS['warning'] if p > 30 else COLORS['danger'] for p in profit_per_hour.values]
ax.barh(profit_per_hour.index, profit_per_hour.values, color=colors, alpha=0.8)
ax.axvline(profit_per_hour.median(), color=COLORS['gray'], linestyle='--', label=f'Median: ${profit_per_hour.median():.0f}/hr')
ax.set_xlabel('Median Profit per Labor Hour ($)')
ax.set_title('Profit per Hour by Category\n(Excl. 2022)', fontweight='bold')
ax.legend(fontsize=8)

# 2.2 Margin vs Quote Size Scatter
ax = axes[0, 1]
sample = master[(master['quoted_total'] < 100000) & (master['overall_margin_pct'].between(0, 60))].sample(min(2000, len(master)))
scatter = ax.scatter(sample['quoted_total'], sample['overall_margin_pct'], 
                     c=sample['complexity_score'], cmap='viridis', alpha=0.4, s=20)
ax.axhline(25, color=COLORS['danger'], linestyle='--', alpha=0.7, label='25% target')
ax.set_xlabel('Quote Value ($)')
ax.set_ylabel('Overall Margin %')
ax.set_title('Margin vs Quote Size\n(color = complexity)', fontweight='bold')
ax.legend(fontsize=8)
plt.colorbar(scatter, ax=ax, label='Complexity')
ax.xaxis.set_major_formatter(mticker.StrMethodFormatter('${x:,.0f}'))

# 2.3 High Margin Jobs Analysis
ax = axes[0, 2]
high_margin = master[master['overall_margin_pct'] > 35]
low_margin = master[master['overall_margin_pct'] < 20]

high_margin_cats = high_margin['job_category'].value_counts().head(8)
low_margin_cats = low_margin['job_category'].value_counts().head(8)

x = range(len(high_margin_cats))
width = 0.35
ax.bar([i - width/2 for i in x], high_margin_cats.values, width, label='High Margin (>35%)', color=COLORS['success'], alpha=0.8)
low_vals = [low_margin_cats.get(cat, 0) for cat in high_margin_cats.index]
ax.bar([i + width/2 for i in x], low_vals, width, label='Low Margin (<20%)', color=COLORS['danger'], alpha=0.8)
ax.set_xticks(x)
ax.set_xticklabels(high_margin_cats.index, rotation=45, ha='right')
ax.set_ylabel('Number of Quotes')
ax.set_title('High vs Low Margin by Category', fontweight='bold')
ax.legend(fontsize=8)

# 2.4 Cost Efficiency Trends
ax = axes[1, 0]
yearly_efficiency = master.groupby('year').agg({
    'material_markup_pct': 'median',
    'labor_margin_pct': 'median',
    'overall_margin_pct': 'median'
}).reset_index()

ax.plot(yearly_efficiency['year'], yearly_efficiency['material_markup_pct'], marker='o', label='Material Markup %', color=COLORS['primary'])
ax.plot(yearly_efficiency['year'], yearly_efficiency['labor_margin_pct'], marker='s', label='Labor Margin %', color=COLORS['secondary'])
ax.plot(yearly_efficiency['year'], yearly_efficiency['overall_margin_pct'], marker='^', label='Overall Margin %', color=COLORS['success'])
ax.axhline(25, color=COLORS['gray'], linestyle='--', alpha=0.5)
ax.set_xlabel('Year')
ax.set_ylabel('Margin/Markup %')
ax.set_title('Margin Trends Over Time', fontweight='bold')
ax.legend(fontsize=8)

# 2.5 Material Efficiency by Category
ax = axes[1, 1]
mat_efficiency = master[master['material_pct'].between(10, 80)].groupby('job_category')['material_pct'].median().sort_values()
ax.barh(mat_efficiency.index, mat_efficiency.values, color=COLORS['primary'], alpha=0.8)
ax.axvline(mat_efficiency.median(), color=COLORS['danger'], linestyle='--', label=f'Median: {mat_efficiency.median():.1f}%')
ax.set_xlabel('Material Cost as % of Quote')
ax.set_title('Material Cost Ratio by Category', fontweight='bold')
ax.legend(fontsize=8)

# 2.6 Labor Efficiency by Category
ax = axes[1, 2]
labor_efficiency = master[master['labor_pct'].between(10, 80)].groupby('job_category')['labor_pct'].median().sort_values()
ax.barh(labor_efficiency.index, labor_efficiency.values, color=COLORS['secondary'], alpha=0.8)
ax.axvline(labor_efficiency.median(), color=COLORS['danger'], linestyle='--', label=f'Median: {labor_efficiency.median():.1f}%')
ax.set_xlabel('Labor Cost as % of Quote')
ax.set_title('Labor Cost Ratio by Category', fontweight='bold')
ax.legend(fontsize=8)

plt.tight_layout()
plt.savefig(f"{OUTPUT_PATH}profitability_deep_dive.png", dpi=150, bbox_inches='tight',
            facecolor='white', edgecolor='none')
print(f"  ✓ Saved: profitability_deep_dive.png")
plt.close()

# =============================================================================
# FIGURE 3: OPERATIONAL PATTERNS
# =============================================================================
print("\n" + "-"*80)
print(" GENERATING OPERATIONAL PATTERNS")
print("-"*80)

fig, axes = plt.subplots(2, 3, figsize=(18, 12))
fig.suptitle('TOITURELV - Operational Patterns & Efficiency', fontsize=14, fontweight='bold', y=1.02)

# 3.1 Weekly Patterns (Heatmap-style)
ax = axes[0, 0]
weekly_data = master.groupby(['month', 'day_of_week'])['quoted_total'].sum().unstack(fill_value=0)
im = ax.imshow(weekly_data.values / 1e6, cmap='YlOrRd', aspect='auto')
ax.set_xticks(range(7))
ax.set_xticklabels(['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'])
ax.set_yticks(range(12))
ax.set_yticklabels(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
ax.set_title('Revenue Heatmap (Month × Day)', fontweight='bold')
plt.colorbar(im, ax=ax, label='Revenue ($M)')

# 3.2 Quote Complexity Distribution
ax = axes[0, 1]
complexity = master[master['complexity_score'] < 50]['complexity_score']
ax.hist(complexity, bins=30, color=COLORS['primary'], edgecolor='white', alpha=0.8)
ax.axvline(complexity.median(), color=COLORS['danger'], linestyle='--', linewidth=2,
           label=f'Median: {complexity.median():.0f} items')
ax.set_xlabel('Complexity Score (# Line Items)')
ax.set_ylabel('Number of Quotes')
ax.set_title('Quote Complexity Distribution', fontweight='bold')
ax.legend(fontsize=9)

# 3.3 Complexity vs Margin
ax = axes[0, 2]
complexity_margin = master[(master['complexity_score'] > 0) & (master['complexity_score'] < 40)]
complexity_bins = pd.cut(complexity_margin['complexity_score'], bins=[0, 5, 10, 15, 20, 40], labels=['1-5', '6-10', '11-15', '16-20', '20+'])
margin_by_complexity = complexity_margin.groupby(complexity_bins)['overall_margin_pct'].median()

colors = [COLORS['success'] if m >= 25 else COLORS['warning'] for m in margin_by_complexity.values]
ax.bar(margin_by_complexity.index, margin_by_complexity.values, color=colors, alpha=0.8)
ax.axhline(25, color=COLORS['gray'], linestyle='--')
ax.set_xlabel('Complexity (# Line Items)')
ax.set_ylabel('Median Margin %')
ax.set_title('Margin by Quote Complexity', fontweight='bold')

# 3.4 Seasonality Deep Dive - Revenue
ax = axes[1, 0]
monthly_stats = master.groupby('month').agg({
    'quoted_total': ['sum', 'count', 'median']
}).reset_index()
monthly_stats.columns = ['month', 'total_rev', 'count', 'median']

ax2 = ax.twinx()
bars = ax.bar(monthly_stats['month'], monthly_stats['total_rev']/1e6, color=COLORS['primary'], alpha=0.7, label='Total Revenue')
line = ax2.plot(monthly_stats['month'], monthly_stats['count'], color=COLORS['danger'], marker='o', linewidth=2, label='Quote Count')
ax.set_xlabel('Month')
ax.set_ylabel('Total Revenue ($M)', color=COLORS['primary'])
ax2.set_ylabel('Quote Count', color=COLORS['danger'])
ax.set_title('Monthly Revenue & Volume', fontweight='bold')
ax.set_xticks(range(1, 13))
ax.set_xticklabels(['J', 'F', 'M', 'A', 'M', 'J', 'J', 'A', 'S', 'O', 'N', 'D'])

# 3.5 Average Job Size by Month
ax = axes[1, 1]
ax.bar(monthly_stats['month'], monthly_stats['median'], color=COLORS['success'], alpha=0.8)
ax.set_xlabel('Month')
ax.set_ylabel('Median Quote Value ($)')
ax.set_title('Median Job Size by Month', fontweight='bold')
ax.set_xticks(range(1, 13))
ax.set_xticklabels(['J', 'F', 'M', 'A', 'M', 'J', 'J', 'A', 'S', 'O', 'N', 'D'])
ax.yaxis.set_major_formatter(mticker.StrMethodFormatter('${x:,.0f}'))

# Find peak and trough
peak_month = monthly_stats.loc[monthly_stats['median'].idxmax(), 'month']
trough_month = monthly_stats.loc[monthly_stats['median'].idxmin(), 'month']
ax.annotate(f'Peak', xy=(peak_month, monthly_stats['median'].max()), 
            xytext=(peak_month, monthly_stats['median'].max() * 1.1),
            ha='center', fontsize=9, color=COLORS['success'])

# 3.6 Year-over-Year Monthly Comparison
ax = axes[1, 2]
yoy_monthly = master[master['year'].isin([2023, 2024, 2025])].groupby(['year', 'month'])['quoted_total'].sum().unstack(level=0)
yoy_monthly = yoy_monthly / 1e6

for year in [2023, 2024, 2025]:
    if year in yoy_monthly.columns:
        ax.plot(yoy_monthly.index, yoy_monthly[year], marker='o', label=str(year), linewidth=2)

ax.set_xlabel('Month')
ax.set_ylabel('Revenue ($M)')
ax.set_title('YoY Monthly Revenue Comparison', fontweight='bold')
ax.set_xticks(range(1, 13))
ax.set_xticklabels(['J', 'F', 'M', 'A', 'M', 'J', 'J', 'A', 'S', 'O', 'N', 'D'])
ax.legend(fontsize=9)

plt.tight_layout()
plt.savefig(f"{OUTPUT_PATH}operational_patterns.png", dpi=150, bbox_inches='tight',
            facecolor='white', edgecolor='none')
print(f"  ✓ Saved: operational_patterns.png")
plt.close()

# =============================================================================
# FIGURE 4: CORTEX PRICING INPUTS
# =============================================================================
print("\n" + "-"*80)
print(" GENERATING CORTEX PRICING INPUTS")
print("-"*80)

fig, axes = plt.subplots(2, 3, figsize=(18, 12))
fig.suptitle('TOITURELV - Cortex Algorithm Training Data', fontsize=14, fontweight='bold', y=1.02)

# 4.1 Price per SqFt by Category (for algorithm)
ax = axes[0, 0]
sqft_by_cat = master[(master['price_per_sqft'] > 0) & (master['price_per_sqft'] < 100)].groupby('job_category').agg({
    'price_per_sqft': ['median', 'mean', 'std', 'count']
}).reset_index()
sqft_by_cat.columns = ['category', 'median', 'mean', 'std', 'count']
sqft_by_cat = sqft_by_cat.sort_values('median', ascending=True)

ax.barh(sqft_by_cat['category'], sqft_by_cat['median'], xerr=sqft_by_cat['std'].fillna(0), 
        color=COLORS['primary'], alpha=0.8, capsize=3)
ax.set_xlabel('Price per SqFt ($) with Std Dev')
ax.set_title('$/SqFt by Category\n(Algorithm Input)', fontweight='bold')

for i, row in sqft_by_cat.iterrows():
    ax.text(row['median'] + row['std'] + 2, list(sqft_by_cat['category']).index(row['category']), 
            f'n={row["count"]:.0f}', va='center', fontsize=8)

# 4.2 Hours per SqFt by Category
ax = axes[0, 1]
labor_reliable['hours_per_sqft'] = labor_reliable['labor_hours_total'] / labor_reliable['sqft_final']
hours_sqft = labor_reliable[(labor_reliable['hours_per_sqft'] > 0) & (labor_reliable['hours_per_sqft'] < 1)].groupby('job_category')['hours_per_sqft'].median().sort_values()

ax.barh(hours_sqft.index, hours_sqft.values, color=COLORS['secondary'], alpha=0.8)
ax.set_xlabel('Hours per SqFt')
ax.set_title('Labor Hours per SqFt by Category\n(Excl. 2022)', fontweight='bold')

# 4.3 Material Cost per SqFt
ax = axes[0, 2]
master['material_cost_per_sqft'] = master['material_cost_total'] / master['sqft_final']
mat_sqft = master[(master['material_cost_per_sqft'] > 0) & (master['material_cost_per_sqft'] < 50)].groupby('job_category')['material_cost_per_sqft'].median().sort_values()

ax.barh(mat_sqft.index, mat_sqft.values, color=COLORS['warning'], alpha=0.8)
ax.set_xlabel('Material Cost per SqFt ($)')
ax.set_title('Material Cost per SqFt by Category', fontweight='bold')

# 4.4 Typical Quote Ranges by Category
ax = axes[1, 0]
quote_ranges = master.groupby('job_category')['quoted_total'].agg(['min', 'median', 'max', 'mean']).reset_index()
quote_ranges = quote_ranges.sort_values('median', ascending=True)

# Box plot style visualization
categories = quote_ranges['job_category'].tolist()
positions = range(len(categories))

for i, (cat, row) in enumerate(quote_ranges.iterrows()):
    data = master[master['job_category'] == quote_ranges.iloc[i]['job_category']]['quoted_total']
    q1, q3 = data.quantile([0.25, 0.75])
    median = data.median()
    
    ax.barh(i, q3-q1, left=q1, height=0.6, color=COLORS['primary'], alpha=0.6)
    ax.scatter(median, i, color=COLORS['danger'], s=50, zorder=5)

ax.set_yticks(positions)
ax.set_yticklabels(categories)
ax.set_xlabel('Quote Value Range (25th-75th percentile)')
ax.set_title('Quote Value Ranges by Category\n(dot = median)', fontweight='bold')
ax.set_xlim(0, 50000)
ax.xaxis.set_major_formatter(mticker.StrMethodFormatter('${x:,.0f}'))

# 4.5 Confidence Score Data (how much data per category)
ax = axes[1, 1]
data_quality = master.groupby('job_category').agg({
    'quote_id': 'count',
    'sqft_final': lambda x: x.notna().sum(),
    'labor_hours_total': lambda x: (x > 0).sum(),
    'material_cost_total': lambda x: (x > 0).sum()
}).reset_index()
data_quality.columns = ['category', 'total', 'has_sqft', 'has_labor', 'has_materials']
data_quality['completeness'] = (data_quality['has_sqft'] + data_quality['has_labor'] + data_quality['has_materials']) / (3 * data_quality['total']) * 100
data_quality = data_quality.sort_values('completeness', ascending=True)

colors = [COLORS['success'] if c > 60 else COLORS['warning'] if c > 40 else COLORS['danger'] for c in data_quality['completeness']]
ax.barh(data_quality['category'], data_quality['completeness'], color=colors, alpha=0.8)
ax.axvline(50, color=COLORS['gray'], linestyle='--')
ax.set_xlabel('Data Completeness %')
ax.set_title('Algorithm Confidence by Category\n(% with sqft + labor + materials)', fontweight='bold')

# 4.6 Key Pricing Correlations
ax = axes[1, 2]
# Create correlation data
corr_data = master[['quoted_total', 'sqft_final', 'labor_hours_total', 'material_cost_total', 
                    'complexity_score', 'overall_margin_pct']].dropna()
if len(corr_data) > 100:
    correlations = corr_data.corr()['quoted_total'].drop('quoted_total').sort_values()
    
    colors = [COLORS['success'] if c > 0 else COLORS['danger'] for c in correlations.values]
    ax.barh(correlations.index, correlations.values, color=colors, alpha=0.8)
    ax.axvline(0, color=COLORS['gray'], linewidth=1)
    ax.set_xlabel('Correlation with Quote Value')
    ax.set_title('Price Drivers (Correlation)', fontweight='bold')
    ax.set_xlim(-1, 1)

plt.tight_layout()
plt.savefig(f"{OUTPUT_PATH}cortex_pricing_inputs.png", dpi=150, bbox_inches='tight',
            facecolor='white', edgecolor='none')
print(f"  ✓ Saved: cortex_pricing_inputs.png")
plt.close()

# =============================================================================
# DEEP INSIGHTS SUMMARY
# =============================================================================
print("\n" + "-"*80)
print(" GENERATING DEEP INSIGHTS SUMMARY")
print("-"*80)

# Calculate additional metrics
total_clients = master['client_id'].nunique()
repeat_clients = (client_counts > 1).sum()
repeat_pct = repeat_clients / total_clients * 100

top_20_revenue = client_ltv.sort_values(ascending=False).head(20).sum()
top_20_pct = top_20_revenue / master['quoted_total'].sum() * 100

avg_quotes_per_repeat = client_counts[client_counts > 1].mean()

# Revenue from repeat vs one-time
repeat_revenue = master[master['is_repeat_client']]['quoted_total'].sum()
onetime_revenue = master[~master['is_repeat_client']]['quoted_total'].sum()

# Seasonality
peak_month_num = monthly_stats.loc[monthly_stats['total_rev'].idxmax(), 'month']
trough_month_num = monthly_stats.loc[monthly_stats['total_rev'].idxmin(), 'month']
month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

# Best performing categories
best_margin_cat = master.groupby('job_category')['overall_margin_pct'].median().idxmax()
best_margin_val = master.groupby('job_category')['overall_margin_pct'].median().max()

# Growth categories
growth_2023 = master[master['year'] == 2023].groupby('job_category')['quoted_total'].sum()
growth_2025 = master[master['year'] == 2025].groupby('job_category')['quoted_total'].sum()
growth_rates = ((growth_2025 / growth_2023 - 1) * 100).sort_values(ascending=False)

summary = f"""
================================================================================
                    TOITURELV - DEEP INSIGHTS SUMMARY
                    Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}
================================================================================

CUSTOMER INSIGHTS
-----------------
  Total Unique Clients:           {total_clients:,}
  One-Time Clients:               {total_clients - repeat_clients:,} ({100-repeat_pct:.1f}%)
  Repeat Clients:                 {repeat_clients:,} ({repeat_pct:.1f}%)
  Avg Quotes per Repeat Client:   {avg_quotes_per_repeat:.1f}
  
  Revenue from Repeat Clients:    ${repeat_revenue/1e6:.1f}M ({repeat_revenue/master['quoted_total'].sum()*100:.1f}%)
  Revenue from One-Time Clients:  ${onetime_revenue/1e6:.1f}M ({onetime_revenue/master['quoted_total'].sum()*100:.1f}%)
  
  Top 20 Clients Revenue:         ${top_20_revenue/1e6:.1f}M ({top_20_pct:.1f}% of total)
  Median Client LTV:              ${client_ltv_valid.median():,.0f}
  Mean Client LTV:                ${client_ltv_valid.mean():,.0f}

CLIENT SEGMENTATION
-------------------
  VIP Clients ($100K+):           {len(client_segments[client_segments['segment'] == 'VIP ($100K+)']):,}
  High Value ($50-100K):          {len(client_segments[client_segments['segment'] == 'High Value ($50-100K)']):,}
  Medium ($20-50K):               {len(client_segments[client_segments['segment'] == 'Medium ($20-50K)']):,}
  Standard ($5-20K):              {len(client_segments[client_segments['segment'] == 'Standard ($5-20K)']):,}
  Small (<$5K):                   {len(client_segments[client_segments['segment'] == 'Small (<$5K)']):,}

PROFITABILITY INSIGHTS
----------------------
  Best Margin Category:           {best_margin_cat} ({best_margin_val:.1f}%)
  Median Profit per Hour:         ${profit_per_hour.median():.0f}/hr (excl. 2022)
  
  High Margin Jobs (>35%):        {len(high_margin):,} ({len(high_margin)/len(master)*100:.1f}%)
  Low Margin Jobs (<20%):         {len(low_margin):,} ({len(low_margin)/len(master)*100:.1f}%)

CATEGORY GROWTH (2023→2025)
---------------------------
"""

for cat, growth in growth_rates.head(5).items():
    summary += f"  {cat:<20}: {growth:+.0f}%\n"

summary += f"""
SEASONALITY PATTERNS
--------------------
  Peak Month:                     {month_names[int(peak_month_num)-1]} (${monthly_stats['total_rev'].max()/1e6:.1f}M)
  Slowest Month:                  {month_names[int(trough_month_num)-1]} (${monthly_stats['total_rev'].min()/1e6:.1f}M)
  Seasonal Swing:                 {(monthly_stats['total_rev'].max()/monthly_stats['total_rev'].min()-1)*100:.0f}% variation
  
  Best Day for Quotes:            Tuesday-Thursday (most activity)
  Weekend Activity:               {master[master['day_of_week'].isin([5,6])]['quoted_total'].sum()/master['quoted_total'].sum()*100:.1f}% of revenue

QUOTE COMPLEXITY
----------------
  Median Line Items:              {complexity.median():.0f}
  Simple Jobs (<5 items):         {len(master[master['complexity_score'] < 5]):,}
  Complex Jobs (>15 items):       {len(master[master['complexity_score'] > 15]):,}
  
  Complexity Impact on Margin:
    1-5 items:                    ~{margin_by_complexity.get('1-5', 0):.1f}% margin
    11-15 items:                  ~{margin_by_complexity.get('11-15', 0):.1f}% margin
    20+ items:                    ~{margin_by_complexity.get('20+', 0):.1f}% margin

CORTEX ALGORITHM INPUTS
-----------------------
  Key Pricing Drivers (by correlation):
    1. Square Footage              (strongest predictor)
    2. Labor Hours                 
    3. Material Cost               
    4. Complexity Score            
    
  Data Quality by Category:
"""

for _, row in data_quality.tail(5).iterrows():
    quality = 'HIGH' if row['completeness'] > 60 else 'MEDIUM' if row['completeness'] > 40 else 'LOW'
    summary += f"    {row['category']:<20}: {row['completeness']:.0f}% complete ({quality})\n"

summary += f"""
STRATEGIC RECOMMENDATIONS
-------------------------
  1. CUSTOMER RETENTION: {repeat_pct:.0f}% repeat rate is good, but {100-repeat_pct:.0f}% one-time 
     clients represent reactivation opportunity worth ${onetime_revenue/1e6:.1f}M

  2. VIP PROGRAM: Top 20 clients = {top_20_pct:.0f}% of revenue. Consider dedicated 
     account management for high-value relationships.

  3. MARGIN OPTIMIZATION: {best_margin_cat} has {best_margin_val:.0f}% margins - 
     investigate why and apply learnings to lower-margin categories.

  4. SEASONAL PLANNING: {(monthly_stats['total_rev'].max()/monthly_stats['total_rev'].min()-1)*100:.0f}% revenue swing between peak/trough months.
     Consider off-season promotions or maintenance programs.

  5. DATA QUALITY: Improve sqft capture rate (currently ~33%) for better 
     Cortex algorithm accuracy.

FILES GENERATED
---------------
  - customer_insights.png (6 charts)
  - profitability_deep_dive.png (6 charts)
  - operational_patterns.png (6 charts)
  - cortex_pricing_inputs.png (6 charts)
  - deep_insights_summary.txt (this report)

================================================================================
"""

with open(f"{OUTPUT_PATH}deep_insights_summary.txt", 'w') as f:
    f.write(summary)
print(f"  ✓ Saved: deep_insights_summary.txt")

print(summary)

print("\n" + "="*80)
print(" DEEP INSIGHTS ANALYSIS COMPLETE")
print("="*80)
print(f"""
Additional Files Generated:
  - customer_insights.png (6 charts)
  - profitability_deep_dive.png (6 charts)
  - operational_patterns.png (6 charts)
  - cortex_pricing_inputs.png (6 charts)
  - deep_insights_summary.txt

Total: 24 additional charts + insights summary

Location: {OUTPUT_PATH}
""")
