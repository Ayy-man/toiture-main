#!/usr/bin/env python3
"""
================================================================================
TOITURELV - MASTER DATA PIPELINE v3 (CORRECTED)
================================================================================
FIXES APPLIED:
1. Material cost = unit_cost × quantity (NOT the 'total' field)
2. Material sell = 'total' field (which = sell_price × quantity)
3. 2022 flagged for labor data quality issues

Verified field mappings:
- Materials: total = sell_price × quantity (99.6% match)
- Materials: markup median = 35%, margin median = 26%
- Time Lines: quantity = hours, unit_price = sell rate, unit_cost = cost rate
- 2022 has anomalous labor data (median 1.5 hrs vs normal 25-30 hrs)

================================================================================
"""

import pandas as pd
import numpy as np
import re
from datetime import datetime
from collections import Counter
import warnings
warnings.filterwarnings('ignore')

# =============================================================================
# CONFIGURATION
# =============================================================================
DATA_PATH = "/Users/aymanbaig/Desktop/cortex-data/"
OUTPUT_PATH = DATA_PATH

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def extract_sqft(text):
    """Extract square footage from text descriptions."""
    if pd.isna(text):
        return None
    
    text = str(text).lower()
    
    patterns = [
        r'([\d,\s]+(?:\.\d+)?)\s*pi[²2]',
        r'([\d,\s]+(?:\.\d+)?)\s*sq\.?\s*ft',
        r'([\d,\s]+(?:\.\d+)?)\s*square\s*feet',
        r'([\d,\s]+(?:\.\d+)?)\s*pieds?\s*carr[ée]s?',
        r'([\d,\s]+(?:\.\d+)?)\s*p\.?c\.?(?:\s|$)',
        r'(?:surface|superficie|area)\s*[:\s]\s*([\d,\s]+(?:\.\d+)?)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            num_str = match.group(1).replace(',', '').replace(' ', '')
            try:
                value = float(num_str)
                if 50 <= value <= 100000:
                    return value
            except:
                continue
    return None


def extract_dimensions(text):
    """Extract dimensions like 20x30."""
    if pd.isna(text):
        return None, None
    
    text = str(text).lower()
    patterns = [
        r"(\d+(?:\.\d+)?)\s*['\"]?\s*[xX×]\s*(\d+(?:\.\d+)?)\s*['\"]?",
        r"(\d+(?:\.\d+)?)\s*pi\.?\s*[xX×]\s*(\d+(?:\.\d+)?)\s*pi\.?",
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            try:
                l, w = float(match.group(1)), float(match.group(2))
                if 5 <= l <= 500 and 5 <= w <= 500:
                    return l, w
            except:
                continue
    return None, None


def extract_pitch(text):
    """Extract roof pitch like 6/12."""
    if pd.isna(text):
        return None
    match = re.search(r'(\d{1,2})\s*[/:\-]\s*12', str(text))
    if match:
        try:
            pitch = int(match.group(1))
            if 0 <= pitch <= 24:
                return pitch
        except:
            pass
    return None


def extract_layers(text):
    """Extract number of layers to remove."""
    if pd.isna(text):
        return None
    
    text = str(text).lower()
    patterns = [r'(\d)\s*couches?', r'(\d)\s*layers?', r'enlever\s*(\d)', r'remove\s*(\d)']
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            try:
                layers = int(match.group(1))
                if 1 <= layers <= 5:
                    return layers
            except:
                continue
    return None


def categorize_job_type(name):
    """Standardize job types."""
    if pd.isna(name):
        return 'Unknown'
    
    name_lower = str(name).lower()
    
    if any(x in name_lower for x in ['élastomère', 'elastomere', 'membrane']):
        return 'Élastomère'
    elif any(x in name_lower for x in ['bardeau', 'shingle', 'bardeaux']):
        return 'Bardeaux'
    elif any(x in name_lower for x in ['service', 'réparation', 'reparation', 'repair']):
        return 'Service Call'
    elif any(x in name_lower for x in ['ferblanterie', 'métal', 'metal', 'tôle', 'solin']):
        return 'Ferblanterie'
    elif any(x in name_lower for x in ['puits de lumière', 'skylight', 'velux']):
        return 'Skylights'
    elif any(x in name_lower for x in ['câble', 'cable', 'chauffant', 'heat']):
        return 'Heat Cables'
    elif any(x in name_lower for x in ['gouttière', 'gutter', 'gouttiere']):
        return 'Gutters'
    elif any(x in name_lower for x in ['ventilation', 'évent', 'event', 'vent']):
        return 'Ventilation'
    elif any(x in name_lower for x in ['isolation', 'insulation']):
        return 'Insulation'
    elif any(x in name_lower for x in ['inspection', 'évaluation', 'evaluation']):
        return 'Inspection'
    else:
        return 'Other'


def extract_job_code(name):
    """Extract numeric job codes like 40FR."""
    if pd.isna(name):
        return None, None
    match = re.match(r'^(\d{2})([A-Z]{2})', str(name))
    if match:
        return match.group(1), match.group(2)
    return None, None


def flag_anomalies(row):
    """Flag potential data quality issues."""
    flags = []
    
    if pd.notna(row.get('quoted_total')) and row['quoted_total'] < 0:
        flags.append('NEGATIVE_TOTAL')
    if pd.notna(row.get('quoted_total')) and row['quoted_total'] > 500000:
        flags.append('VERY_HIGH_TOTAL')
    if pd.notna(row.get('quoted_total')) and row['quoted_total'] == 0:
        flags.append('ZERO_TOTAL')
    
    if pd.notna(row.get('overall_margin_pct')):
        if row['overall_margin_pct'] < 0:
            flags.append('NEGATIVE_MARGIN')
        elif row['overall_margin_pct'] > 70:
            flags.append('VERY_HIGH_MARGIN')
        elif row['overall_margin_pct'] < 10:
            flags.append('VERY_LOW_MARGIN')
    
    if pd.isna(row.get('material_cost_total')) or row.get('material_cost_total', 0) == 0:
        flags.append('NO_MATERIALS')
    if pd.isna(row.get('labor_hours_total')) or row.get('labor_hours_total', 0) == 0:
        flags.append('NO_LABOR')
    
    # Flag 2022 labor data as unreliable
    if row.get('year') == 2022:
        flags.append('2022_LABOR_UNRELIABLE')
    
    if pd.notna(row.get('material_pct')) and row['material_pct'] > 90:
        flags.append('UNUSUAL_MATERIAL_RATIO')
    if pd.notna(row.get('labor_pct')) and row['labor_pct'] > 90:
        flags.append('UNUSUAL_LABOR_RATIO')
    
    return '|'.join(flags) if flags else None


# =============================================================================
# MAIN PIPELINE
# =============================================================================

print("\n" + "="*80)
print(" TOITURELV - MASTER DATA PIPELINE v3 (CORRECTED)")
print(" Fixed: Material cost/sell calculation, 2022 labor flag")
print("="*80)

# -----------------------------------------------------------------------------
# STEP 1: LOAD ALL TABLES
# -----------------------------------------------------------------------------
print("\n" + "-"*80)
print(" STEP 1: LOADING ALL DATA TABLES")
print("-"*80)

print("\nLoading tables...")

quotes = pd.read_csv(f"{DATA_PATH}Quotes Data Export_clean.csv")
print(f"  ✓ Quotes: {len(quotes):,} records")

materials = pd.read_csv(f"{DATA_PATH}Quote Materials_clean.csv")
print(f"  ✓ Materials: {len(materials):,} records")

lines = pd.read_csv(f"{DATA_PATH}Quote Lines_clean.csv")
print(f"  ✓ Quote Lines: {len(lines):,} records")

time_lines = pd.read_csv(f"{DATA_PATH}Quote Time Lines_clean.csv")
print(f"  ✓ Time Lines: {len(time_lines):,} records")

sub_lines = pd.read_csv(f"{DATA_PATH}Quote Sub Lines_clean.csv")
print(f"  ✓ Sub Lines: {len(sub_lines):,} records")

# -----------------------------------------------------------------------------
# STEP 2: DATA TYPE CONVERSIONS
# -----------------------------------------------------------------------------
print("\n" + "-"*80)
print(" STEP 2: DATA TYPE CONVERSIONS")
print("-"*80)

# Quotes
quotes['id'] = pd.to_numeric(quotes['id'], errors='coerce')
quotes['quoted_total'] = pd.to_numeric(quotes['quoted_total'], errors='coerce')
quotes['quoted_hours'] = pd.to_numeric(quotes['quoted_hours'], errors='coerce')
quotes['quoted_area'] = pd.to_numeric(quotes['quoted_area'], errors='coerce')
quotes['subtotal'] = pd.to_numeric(quotes['subtotal'], errors='coerce')
quotes['deposit_required'] = quotes['deposit_required'].astype(str).str.lower() == 'true'
quotes['deposit_paid'] = quotes['deposit_paid'].astype(str).str.lower() == 'true'
quotes['created_at'] = pd.to_datetime(quotes['created_at'], errors='coerce')
quotes['additional_cost'] = pd.to_numeric(quotes['additional_cost'], errors='coerce')
quotes['rebate'] = pd.to_numeric(quotes['rebate'], errors='coerce')
print(f"  ✓ Quotes converted")

# Materials
materials['quote_id'] = pd.to_numeric(materials['quote_id'], errors='coerce')
materials['material_id'] = pd.to_numeric(materials['material_id'], errors='coerce')
materials['quantity'] = pd.to_numeric(materials['quantity'], errors='coerce')
materials['unit_cost'] = pd.to_numeric(materials['unit_cost'], errors='coerce')
materials['sell_price'] = pd.to_numeric(materials['sell_price'], errors='coerce')
materials['total'] = pd.to_numeric(materials['total'], errors='coerce')  # This is SELL total
materials['created_at'] = pd.to_datetime(materials['created_at'], errors='coerce')
print(f"  ✓ Materials converted")

# Lines
lines['id'] = pd.to_numeric(lines['id'], errors='coerce')
lines['quote_id'] = pd.to_numeric(lines['quote_id'], errors='coerce')
lines['total'] = pd.to_numeric(lines['total'], errors='coerce')
lines['quantity'] = pd.to_numeric(lines['quantity'], errors='coerce')
print(f"  ✓ Quote Lines converted")

# Time Lines - quantity = hours, unit_price = sell rate, unit_cost = cost rate
time_lines['id'] = pd.to_numeric(time_lines['id'], errors='coerce')
time_lines['quote_id'] = pd.to_numeric(time_lines['quote_id'], errors='coerce')
time_lines['quantity'] = pd.to_numeric(time_lines['quantity'], errors='coerce')
time_lines['unit_price'] = pd.to_numeric(time_lines['unit_price'], errors='coerce')
time_lines['unit_cost'] = pd.to_numeric(time_lines['unit_cost'], errors='coerce')
time_lines['total'] = pd.to_numeric(time_lines['total'], errors='coerce')

time_lines = time_lines.rename(columns={
    'quantity': 'hours',
    'unit_price': 'sell_rate',
    'unit_cost': 'cost_rate'
})
print(f"  ✓ Time Lines converted")

# Sub Lines
sub_lines['id'] = pd.to_numeric(sub_lines['id'], errors='coerce')
sub_lines['quote_id'] = pd.to_numeric(sub_lines['quote_id'], errors='coerce')
sub_lines['cost'] = pd.to_numeric(sub_lines['cost'], errors='coerce')
sub_lines['price'] = pd.to_numeric(sub_lines['price'], errors='coerce')
sub_lines = sub_lines.rename(columns={'price': 'sell_price'})
print(f"  ✓ Sub Lines converted")

# -----------------------------------------------------------------------------
# STEP 3: VALIDATE FOREIGN KEYS
# -----------------------------------------------------------------------------
print("\n" + "-"*80)
print(" STEP 3: VALIDATING FOREIGN KEY RELATIONSHIPS")
print("-"*80)

quote_ids = set(quotes['id'].dropna().astype(int))
print(f"\nUnique quote IDs: {len(quote_ids):,}")

mat_quote_ids = set(materials['quote_id'].dropna().astype(int))
line_quote_ids = set(lines['quote_id'].dropna().astype(int))
time_quote_ids = set(time_lines['quote_id'].dropna().astype(int))
sub_quote_ids = set(sub_lines['quote_id'].dropna().astype(int))

print(f"\nQuote Coverage:")
print(f"  With materials: {len(quote_ids.intersection(mat_quote_ids)):,} ({len(quote_ids.intersection(mat_quote_ids))/len(quote_ids)*100:.1f}%)")
print(f"  With lines: {len(quote_ids.intersection(line_quote_ids)):,} ({len(quote_ids.intersection(line_quote_ids))/len(quote_ids)*100:.1f}%)")
print(f"  With labor: {len(quote_ids.intersection(time_quote_ids)):,} ({len(quote_ids.intersection(time_quote_ids))/len(quote_ids)*100:.1f}%)")
print(f"  With subs: {len(quote_ids.intersection(sub_quote_ids)):,} ({len(quote_ids.intersection(sub_quote_ids))/len(quote_ids)*100:.1f}%)")

# -----------------------------------------------------------------------------
# STEP 4: AGGREGATE MATERIALS PER QUOTE (CORRECTED)
# -----------------------------------------------------------------------------
print("\n" + "-"*80)
print(" STEP 4: AGGREGATING MATERIALS PER QUOTE (CORRECTED)")
print("-"*80)

# CORRECTED: 
# - material_cost_total = unit_cost × quantity (calculated)
# - material_sell_total = total field (which = sell_price × quantity)

materials['material_cost_calc'] = materials['unit_cost'] * materials['quantity']

materials_agg = materials.groupby('quote_id').agg({
    'id': 'count',
    'unit_cost': 'mean',
    'material_cost_calc': 'sum',  # CORRECT: cost = unit_cost × qty
    'total': 'sum',                # CORRECT: sell = total field (sell_price × qty)
    'quantity': 'sum',
    'material_id': 'nunique',
    'description': lambda x: ' | '.join(x.dropna().astype(str).head(5))
}).reset_index()

materials_agg.columns = [
    'quote_id', 
    'material_line_count',
    'material_avg_unit_cost',
    'material_cost_total',    # Now correctly = sum(unit_cost × qty)
    'material_sell_total',    # Now correctly = sum(total) = sum(sell_price × qty)
    'material_qty_total',
    'material_unique_count',
    'material_descriptions'
]

# Calculate material margin (CORRECTED)
materials_agg['material_margin'] = materials_agg['material_sell_total'] - materials_agg['material_cost_total']
materials_agg['material_margin_pct'] = np.where(
    materials_agg['material_sell_total'] > 0,
    (materials_agg['material_margin'] / materials_agg['material_sell_total'] * 100).round(2),
    None
)

# Calculate markup too
materials_agg['material_markup_pct'] = np.where(
    materials_agg['material_cost_total'] > 0,
    ((materials_agg['material_sell_total'] - materials_agg['material_cost_total']) / materials_agg['material_cost_total'] * 100).round(2),
    None
)

print(f"  ✓ Aggregated materials for {len(materials_agg):,} quotes")
print(f"\n  CORRECTED Material Margin Stats:")
print(f"    Median margin: {materials_agg['material_margin_pct'].median():.1f}%")
print(f"    Median markup: {materials_agg['material_markup_pct'].median():.1f}%")

# -----------------------------------------------------------------------------
# STEP 5: AGGREGATE LABOR PER QUOTE
# -----------------------------------------------------------------------------
print("\n" + "-"*80)
print(" STEP 5: AGGREGATING LABOR PER QUOTE")
print("-"*80)

time_lines['labor_cost'] = time_lines['hours'] * time_lines['cost_rate']
time_lines['labor_sell'] = time_lines['hours'] * time_lines['sell_rate']

labor_agg = time_lines.groupby('quote_id').agg({
    'id': 'count',
    'hours': 'sum',
    'sell_rate': 'median',
    'cost_rate': 'median',
    'labor_cost': 'sum',
    'labor_sell': 'sum',
    'total': 'sum'
}).reset_index()

labor_agg.columns = [
    'quote_id',
    'labor_line_count',
    'labor_hours_total',
    'labor_sell_rate_median',
    'labor_cost_rate_median',
    'labor_cost_total',
    'labor_sell_total',
    'labor_total_recorded'
]

labor_agg['labor_margin'] = labor_agg['labor_sell_total'] - labor_agg['labor_cost_total']
labor_agg['labor_margin_pct'] = np.where(
    labor_agg['labor_sell_total'] > 0,
    (labor_agg['labor_margin'] / labor_agg['labor_sell_total'] * 100).round(2),
    None
)

print(f"  ✓ Aggregated labor for {len(labor_agg):,} quotes")
print(f"\n  Labor Stats:")
print(f"    Median sell rate: ${time_lines['sell_rate'].median():.2f}/hr")
print(f"    Median cost rate: ${time_lines['cost_rate'].median():.2f}/hr")
print(f"    Median margin: {labor_agg['labor_margin_pct'].median():.1f}%")

# -----------------------------------------------------------------------------
# STEP 6: AGGREGATE SUBCONTRACTORS PER QUOTE
# -----------------------------------------------------------------------------
print("\n" + "-"*80)
print(" STEP 6: AGGREGATING SUBCONTRACTORS PER QUOTE")
print("-"*80)

sub_agg = sub_lines.groupby('quote_id').agg({
    'id': 'count',
    'cost': 'sum',
    'sell_price': 'sum',
    'description': lambda x: ' | '.join(x.dropna().astype(str).head(3))
}).reset_index()

sub_agg.columns = [
    'quote_id',
    'sub_line_count',
    'sub_cost_total',
    'sub_sell_total',
    'sub_descriptions'
]

sub_agg['sub_margin'] = sub_agg['sub_sell_total'] - sub_agg['sub_cost_total']
sub_agg['sub_margin_pct'] = np.where(
    sub_agg['sub_sell_total'] > 0,
    (sub_agg['sub_margin'] / sub_agg['sub_sell_total'] * 100).round(2),
    None
)

print(f"  ✓ Aggregated subs for {len(sub_agg):,} quotes")

# -----------------------------------------------------------------------------
# STEP 7: PROCESS QUOTE LINES (JOB TYPES)
# -----------------------------------------------------------------------------
print("\n" + "-"*80)
print(" STEP 7: PROCESSING QUOTE LINES (JOB TYPES)")
print("-"*80)

lines_sorted = lines.sort_values(['quote_id', 'id'])
lines_primary = lines_sorted.groupby('quote_id').first().reset_index()
lines_primary = lines_primary[['quote_id', 'name', 'description']].copy()
lines_primary.columns = ['quote_id', 'job_name', 'job_description']

lines_primary['job_code'], lines_primary['job_lang'] = zip(*lines_primary['job_name'].apply(extract_job_code))
lines_primary['job_category'] = lines_primary['job_name'].apply(categorize_job_type)

lines_count = lines.groupby('quote_id').agg({
    'id': 'count',
    'description': lambda x: ' | '.join(x.dropna().astype(str))
}).reset_index()
lines_count.columns = ['quote_id', 'job_line_count', 'all_job_descriptions']

lines_agg = lines_primary.merge(lines_count, on='quote_id', how='left')

print(f"  ✓ Processed job lines for {len(lines_agg):,} quotes")

job_dist = lines_agg['job_category'].value_counts()
print("\n  Job Category Distribution:")
for cat, count in job_dist.head(8).items():
    print(f"    {cat}: {count:,} ({count/len(lines_agg)*100:.1f}%)")

# -----------------------------------------------------------------------------
# STEP 8: BUILD MASTER QUOTES TABLE
# -----------------------------------------------------------------------------
print("\n" + "-"*80)
print(" STEP 8: BUILDING MASTER QUOTES TABLE")
print("-"*80)

master = quotes.copy()
master = master.rename(columns={'id': 'quote_id'})

master['year'] = master['created_at'].dt.year
master['quarter'] = master['created_at'].dt.quarter
master['month'] = master['created_at'].dt.month
master['day_of_week'] = master['created_at'].dt.dayofweek
master['week_of_year'] = master['created_at'].dt.isocalendar().week

print("\n  Joining tables...")
master = master.merge(materials_agg, on='quote_id', how='left')
master = master.merge(labor_agg, on='quote_id', how='left')
master = master.merge(sub_agg, on='quote_id', how='left')
master = master.merge(lines_agg, on='quote_id', how='left')

print(f"  ✓ Master table: {len(master):,} rows, {len(master.columns)} columns")

# -----------------------------------------------------------------------------
# STEP 9: EXTRACT SQFT FROM DESCRIPTIONS
# -----------------------------------------------------------------------------
print("\n" + "-"*80)
print(" STEP 9: EXTRACTING SQUARE FOOTAGE")
print("-"*80)

def get_sqft(row):
    if pd.notna(row.get('quoted_area')) and row['quoted_area'] > 0:
        return row['quoted_area'], 'quoted_area'
    
    for col, source in [('job_description', 'job_description'), 
                        ('all_job_descriptions', 'all_job_descriptions'),
                        ('material_descriptions', 'material_descriptions')]:
        sqft = extract_sqft(row.get(col, ''))
        if sqft:
            return sqft, source
    return None, None

sqft_results = master.apply(get_sqft, axis=1)
master['extracted_sqft'] = [r[0] for r in sqft_results]
master['sqft_source'] = [r[1] for r in sqft_results]

def get_sqft_from_dims(row):
    for col in ['job_description', 'all_job_descriptions', 'material_descriptions']:
        if pd.notna(row.get(col)):
            l, w = extract_dimensions(row[col])
            if l and w:
                return l * w
    return None

master['sqft_from_dims'] = master.apply(get_sqft_from_dims, axis=1)
master['sqft_final'] = master['extracted_sqft'].fillna(master['sqft_from_dims'])

master['extracted_pitch'] = master['all_job_descriptions'].apply(extract_pitch)
master['extracted_layers'] = master['all_job_descriptions'].apply(extract_layers)

sqft_found = master['sqft_final'].notna().sum()
print(f"  SqFt extracted: {sqft_found:,} ({sqft_found/len(master)*100:.1f}%)")

# -----------------------------------------------------------------------------
# STEP 10: CALCULATE DERIVED METRICS
# -----------------------------------------------------------------------------
print("\n" + "-"*80)
print(" STEP 10: CALCULATING DERIVED METRICS")
print("-"*80)

for col in ['material_cost_total', 'material_sell_total', 'labor_cost_total', 
            'labor_sell_total', 'sub_cost_total', 'sub_sell_total', 'labor_hours_total']:
    master[col] = master[col].fillna(0)

# Total costs and sells
master['total_cost_calculated'] = (master['material_cost_total'] + 
                                    master['labor_cost_total'] + 
                                    master['sub_cost_total'])

master['total_sell_calculated'] = (master['material_sell_total'] + 
                                    master['labor_sell_total'] + 
                                    master['sub_sell_total'])

# Overall margin
master['overall_margin'] = master['quoted_total'] - master['total_cost_calculated']
master['overall_margin_pct'] = np.where(
    master['quoted_total'] > 0,
    (master['overall_margin'] / master['quoted_total'] * 100).round(2),
    None
)

# Component ratios
master['material_pct'] = np.where(
    master['quoted_total'] > 0,
    (master['material_sell_total'] / master['quoted_total'] * 100).round(2),
    None
)
master['labor_pct'] = np.where(
    master['quoted_total'] > 0,
    (master['labor_sell_total'] / master['quoted_total'] * 100).round(2),
    None
)
master['sub_pct'] = np.where(
    master['quoted_total'] > 0,
    (master['sub_sell_total'] / master['quoted_total'] * 100).round(2),
    None
)

# Effective hourly rate
master['effective_hourly_rate'] = np.where(
    master['labor_hours_total'] > 0,
    (master['quoted_total'] / master['labor_hours_total']).round(2),
    None
)

# Per-sqft pricing
master['price_per_sqft'] = np.where(
    (master['sqft_final'].notna()) & (master['sqft_final'] > 0),
    (master['quoted_total'] / master['sqft_final']).round(2),
    None
)

master['cost_per_sqft'] = np.where(
    (master['sqft_final'].notna()) & (master['sqft_final'] > 0),
    (master['total_cost_calculated'] / master['sqft_final']).round(2),
    None
)

# Complexity score
master['complexity_score'] = (master['material_line_count'].fillna(0) + 
                               master['job_line_count'].fillna(0) + 
                               master['labor_line_count'].fillna(0) +
                               master['sub_line_count'].fillna(0))

# Flags
master['has_materials'] = master['material_cost_total'] > 0
master['has_labor'] = master['labor_hours_total'] > 0
master['has_subs'] = master['sub_cost_total'] > 0

# Convert margin columns to numeric
for col in ['overall_margin_pct', 'material_margin_pct', 'labor_margin_pct', 'sub_margin_pct', 'material_markup_pct']:
    if col in master.columns:
        master[col] = pd.to_numeric(master[col], errors='coerce')

print("  ✓ CORRECTED Metrics:")
print(f"    • Overall margin (median): {master['overall_margin_pct'].median():.1f}%")
print(f"    • Material margin (median): {master['material_margin_pct'].median():.1f}%")
print(f"    • Material markup (median): {master['material_markup_pct'].median():.1f}%")
print(f"    • Labor margin (median): {master['labor_margin_pct'].median():.1f}%")
print(f"    • Effective $/hr (median): ${master['effective_hourly_rate'].median():,.0f}")

# -----------------------------------------------------------------------------
# STEP 11: FLAG ANOMALIES
# -----------------------------------------------------------------------------
print("\n" + "-"*80)
print(" STEP 11: FLAGGING ANOMALIES (including 2022 labor issue)")
print("-"*80)

master['anomaly_flags'] = master.apply(flag_anomalies, axis=1)

anomaly_counts = master['anomaly_flags'].dropna().str.split('|').explode().value_counts()
print("\n  Anomaly Flags:")
for flag, count in anomaly_counts.head(10).items():
    print(f"    {flag}: {count:,}")

# -----------------------------------------------------------------------------
# STEP 12: FILTER FOR VALID ANALYSIS SET
# -----------------------------------------------------------------------------
print("\n" + "-"*80)
print(" STEP 12: CREATING ANALYSIS-READY SUBSET")
print("-"*80)

valid_mask = (
    (master['quoted_total'] > 100) &
    (master['quoted_total'] < 500000) &
    (master['year'] >= 2020) &
    (master['year'] <= 2025) &
    (master['overall_margin_pct'].isna() | 
     ((master['overall_margin_pct'] > -10) & (master['overall_margin_pct'] < 80)))
)

master['is_valid_for_analysis'] = valid_mask

# Additional flag for labor-reliable data (exclude 2022)
master['labor_data_reliable'] = master['year'] != 2022

valid_count = valid_mask.sum()
labor_reliable_count = (valid_mask & master['labor_data_reliable']).sum()
print(f"\n  Valid for analysis: {valid_count:,} ({valid_count/len(master)*100:.1f}%)")
print(f"  Valid + reliable labor (excl 2022): {labor_reliable_count:,}")

# -----------------------------------------------------------------------------
# STEP 13: EXPORT MASTER TABLE
# -----------------------------------------------------------------------------
print("\n" + "-"*80)
print(" STEP 13: EXPORTING MASTER TABLE")
print("-"*80)

export_columns = [
    'quote_id', 'created_at', 'year', 'quarter', 'month', 'day_of_week', 'week_of_year',
    'quoted_total', 'quoted_hours', 'quoted_area', 'subtotal', 
    'additional_cost', 'rebate', 'deposit_required', 'deposit_paid',
    'client_id', 'project_id', 'building_id', 'stage_id',
    'sqft_final', 'sqft_source', 'extracted_pitch', 'extracted_layers',
    'job_name', 'job_code', 'job_lang', 'job_category', 'job_line_count',
    'material_line_count', 'material_unique_count', 'material_cost_total', 
    'material_sell_total', 'material_margin_pct', 'material_markup_pct', 'material_qty_total',
    'labor_line_count', 'labor_hours_total', 'labor_sell_rate_median',
    'labor_cost_rate_median', 'labor_cost_total', 'labor_sell_total', 'labor_margin_pct',
    'sub_line_count', 'sub_cost_total', 'sub_sell_total', 'sub_margin_pct',
    'total_cost_calculated', 'total_sell_calculated', 
    'overall_margin', 'overall_margin_pct',
    'material_pct', 'labor_pct', 'sub_pct',
    'effective_hourly_rate', 'price_per_sqft', 'cost_per_sqft',
    'complexity_score',
    'has_materials', 'has_labor', 'has_subs',
    'anomaly_flags', 'is_valid_for_analysis', 'labor_data_reliable',
    'job_description', 'material_descriptions', 'sub_descriptions'
]

export_columns = [c for c in export_columns if c in master.columns]
master_export = master[export_columns].copy()

master_export.to_csv(f"{OUTPUT_PATH}master_quotes.csv", index=False)
print(f"  ✓ Saved: master_quotes.csv ({len(master_export):,} rows, {len(export_columns)} columns)")

analysis_ready = master_export[master_export['is_valid_for_analysis'] == True].copy()
analysis_ready.to_csv(f"{OUTPUT_PATH}master_quotes_valid.csv", index=False)
print(f"  ✓ Saved: master_quotes_valid.csv ({len(analysis_ready):,} rows)")

# Labor-reliable subset (excludes 2022)
labor_reliable = master_export[(master_export['is_valid_for_analysis'] == True) & 
                                (master_export['labor_data_reliable'] == True)].copy()
labor_reliable.to_csv(f"{OUTPUT_PATH}master_quotes_labor_reliable.csv", index=False)
print(f"  ✓ Saved: master_quotes_labor_reliable.csv ({len(labor_reliable):,} rows)")

# -----------------------------------------------------------------------------
# STEP 14: SUMMARY
# -----------------------------------------------------------------------------
print("\n" + "-"*80)
print(" STEP 14: CORRECTED SUMMARY STATISTICS")
print("-"*80)

valid = master[master['is_valid_for_analysis'] == True]

print(f"""
{'='*80}
 CORRECTED MASTER DATA SUMMARY
{'='*80}

┌──────────────────────────────────────────────────────────────────────────────┐
│                         OVERVIEW                                             │
├──────────────────────────────────────────────────────────────────────────────┤
│  Total Quotes:               {len(master):>10,}                                    │
│  Valid for Analysis:         {len(valid):>10,}  ({len(valid)/len(master)*100:.1f}%)                          │
│  Date Range:                 {valid['year'].min():.0f} - {valid['year'].max():.0f}                                   │
├──────────────────────────────────────────────────────────────────────────────┤
│                         QUOTE VALUES                                         │
├──────────────────────────────────────────────────────────────────────────────┤
│  Median:                     ${valid['quoted_total'].median():>12,.0f}                            │
│  Mean:                       ${valid['quoted_total'].mean():>12,.0f}                            │
│  Total Revenue (quoted):     ${valid['quoted_total'].sum():>12,.0f}                            │
├──────────────────────────────────────────────────────────────────────────────┤
│                    CORRECTED MARGINS                                         │
├──────────────────────────────────────────────────────────────────────────────┤
│  Overall Margin (median):    {valid['overall_margin_pct'].median():>10.1f}%                               │
│  Material MARGIN (median):   {valid['material_margin_pct'].median():>10.1f}%  ✓ FIXED (was 0%)             │
│  Material MARKUP (median):   {valid['material_markup_pct'].median():>10.1f}%                               │
│  Labor Margin (median):      {valid['labor_margin_pct'].median():>10.1f}%                               │
├──────────────────────────────────────────────────────────────────────────────┤
│                         COST STRUCTURE                                       │
├──────────────────────────────────────────────────────────────────────────────┤
│  Materials % of Total:       {valid['material_pct'].median():>10.1f}%                               │
│  Labor % of Total:           {valid['labor_pct'].median():>10.1f}%                               │
│  Subs % of Total:            {valid['sub_pct'].median():>10.1f}%                               │
├──────────────────────────────────────────────────────────────────────────────┤
│                         LABOR METRICS                                        │
├──────────────────────────────────────────────────────────────────────────────┤
│  Median Hours per Job:       {valid['labor_hours_total'].median():>10.1f}                                │
│  Median Sell Rate:           ${valid['labor_sell_rate_median'].median():>9.2f}/hr                          │
│  Median Cost Rate:           ${valid['labor_cost_rate_median'].median():>9.2f}/hr                          │
│  Effective $/hr (median):    ${valid['effective_hourly_rate'].median():>9,.0f}                             │
├──────────────────────────────────────────────────────────────────────────────┤
│                         DATA QUALITY NOTES                                   │
├──────────────────────────────────────────────────────────────────────────────┤
│  ⚠️  2022 labor data unreliable (median 1.5 hrs vs normal 25-30 hrs)        │
│  Use master_quotes_labor_reliable.csv for labor-based analysis              │
└──────────────────────────────────────────────────────────────────────────────┘
""")

# Year breakdown
print("\n" + "="*80)
print(" YEAR-OVER-YEAR (with 2022 labor flag)")
print("="*80)

print("\n┌" + "─"*95 + "┐")
print("│ {:>6} │ {:>8} │ {:>12} │ {:>12} │ {:>10} │ {:>10} │ {:>10} │ {:>8} │".format(
    "Year", "Quotes", "Total Rev", "Median $", "Med Hrs", "$/Hr Eff", "Margin%", "Labor?"))
print("├" + "─"*95 + "┤")

for year in sorted(valid['year'].dropna().unique()):
    year_data = valid[valid['year'] == year]
    labor_flag = "⚠️" if year == 2022 else "✓"
    
    eff_rate = year_data['effective_hourly_rate'].median()
    margin = year_data['overall_margin_pct'].median()
    hrs = year_data['labor_hours_total'].median()
    
    print("│ {:>6.0f} │ {:>8,} │ ${:>10,.0f} │ ${:>10,.0f} │ {:>10.1f} │ ${:>9,.0f} │ {:>9.1f}% │ {:>8} │".format(
        year,
        len(year_data),
        year_data['quoted_total'].sum(),
        year_data['quoted_total'].median(),
        hrs if pd.notna(hrs) else 0,
        eff_rate if pd.notna(eff_rate) else 0,
        margin if pd.notna(margin) else 0,
        labor_flag
    ))
print("└" + "─"*95 + "┘")

# Job categories
print("\n" + "="*80)
print(" JOB CATEGORY ANALYSIS")
print("="*80)

print("\n┌" + "─"*100 + "┐")
print("│ {:<20} │ {:>8} │ {:>10} │ {:>10} │ {:>10} │ {:>10} │ {:>10} │".format(
    "Category", "Count", "Median $", "Mat Margin", "Lab Margin", "Overall", "$/SqFt"))
print("├" + "─"*100 + "┤")

for cat in valid['job_category'].value_counts().head(10).index:
    cat_data = valid[valid['job_category'] == cat]
    
    mat_margin = cat_data['material_margin_pct'].median()
    lab_margin = cat_data['labor_margin_pct'].median()
    overall = cat_data['overall_margin_pct'].median()
    price_sqft = cat_data['price_per_sqft'].median()
    
    print("│ {:<20} │ {:>8,} │ ${:>9,.0f} │ {:>9.1f}% │ {:>9.1f}% │ {:>9.1f}% │ ${:>9.2f} │".format(
        cat[:20],
        len(cat_data),
        cat_data['quoted_total'].median(),
        mat_margin if pd.notna(mat_margin) else 0,
        lab_margin if pd.notna(lab_margin) else 0,
        overall if pd.notna(overall) else 0,
        price_sqft if pd.notna(price_sqft) else 0
    ))
print("└" + "─"*100 + "┘")

# -----------------------------------------------------------------------------
# COMPLETE
# -----------------------------------------------------------------------------
print("\n" + "="*80)
print(" ✅ MASTER DATA PIPELINE v3 COMPLETE (CORRECTED)")
print("="*80)
print(f"""
Files Generated:
  • master_quotes.csv               - Full dataset ({len(master):,} rows)
  • master_quotes_valid.csv         - Analysis-ready ({len(analysis_ready):,} rows)
  • master_quotes_labor_reliable.csv - Excludes 2022 ({len(labor_reliable):,} rows)

KEY CORRECTIONS:
  ✓ Material cost = unit_cost × quantity (not 'total' field)
  ✓ Material sell = 'total' field (which = sell_price × qty)
  ✓ Material margin now shows ~26% (was incorrectly 0%)
  ✓ 2022 flagged for unreliable labor data
  ✓ Added labor_data_reliable flag column

Next: Run comprehensive_analysis.py for full analysis with corrected data.
""")
