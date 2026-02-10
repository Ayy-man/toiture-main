#!/usr/bin/env python3
"""
TOITURELV - MASTER DATA PIPELINE v4 (Fixed)
- Skips broken Quote Materials_clean.csv
- Uses existing v3 master_quotes.csv for material aggregations
- Re-processes Quote Lines for all_job_descriptions
- Applies French number parsing fix for sqft extraction
"""

import pandas as pd
import numpy as np
import re
import sys
import warnings
warnings.filterwarnings('ignore')

def log(msg):
    print(msg)
    sys.stdout.flush()

DATA_PATH = "/Users/aymanbaig/Desktop/cortex-data/"

# =============================================================================
# FRENCH NUMBER PARSING (v4 FIX)
# =============================================================================

def parse_french_number(num_str):
    """Handle French formatting: 1 000,00 or 1350,00"""
    if not num_str:
        return None
    num_str = str(num_str).strip()
    if re.match(r'^[\d\s]+,\d{1,2}$', num_str):
        num_str = num_str.replace(' ', '').replace(',', '.')
    else:
        num_str = num_str.replace(',', '').replace(' ', '')
    try:
        return float(num_str)
    except:
        return None

def extract_sqft(text):
    """Extract square footage with French number support"""
    if pd.isna(text):
        return None
    text = str(text).lower()
    patterns = [
        r'([\d\s,]+(?:,\d{1,2})?)\s*pi[²2]',
        r'([\d\s,]+(?:,\d{1,2})?)\s*sq\.?\s*ft',
        r'([\d\s,]+(?:,\d{1,2})?)\s*square\s*feet',
        r'([\d\s,]+(?:,\d{1,2})?)\s*pieds?\s*carr[ée]s?',
        r'([\d\s,]+(?:,\d{1,2})?)\s*p\.?c\.?(?:\s|$)',
        r'(?:surface|superficie|area)\s*[:\s]\s*([\d\s,]+(?:,\d{1,2})?)',
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            value = parse_french_number(match.group(1))
            if value and 50 <= value <= 100000:
                return value
    return None

def extract_dimensions(text):
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

# =============================================================================
# MAIN
# =============================================================================

log("\n" + "="*70)
log(" TOITURELV - MASTER DATA PIPELINE v4 (Fixed)")
log(" Skips broken Materials file, applies French sqft fix")
log("="*70)

# STEP 1: Load existing v3 master (has all material aggregations)
log("\n[1/6] Loading existing master_quotes.csv from v3...")
master = pd.read_csv(f"{DATA_PATH}master_quotes.csv")

# Remove any duplicate columns from failed fix script
cols_to_drop = [c for c in master.columns if c.endswith('_v4') or c == 'extracted_sqft']
if cols_to_drop:
    master = master.drop(columns=cols_to_drop, errors='ignore')
    log(f"      Cleaned up {len(cols_to_drop)} duplicate columns")

log(f"      Loaded {len(master):,} rows")
old_sqft = master['sqft_final'].notna().sum()
log(f"      Current sqft coverage: {old_sqft:,} ({old_sqft/len(master)*100:.1f}%)")

# STEP 2: Load Quote Lines to rebuild all_job_descriptions
log("\n[2/6] Loading Quote Lines for text extraction...")
lines = pd.read_csv(f"{DATA_PATH}Quote Lines_clean.csv")
lines['quote_id'] = pd.to_numeric(lines['quote_id'], errors='coerce')
log(f"      Loaded {len(lines):,} lines")

# Build all_job_descriptions by concatenating all descriptions per quote
log("\n[3/6] Building combined job descriptions...")
lines_text = lines.groupby('quote_id').agg({
    'description': lambda x: ' | '.join(x.dropna().astype(str))
}).reset_index()
lines_text.columns = ['quote_id', 'all_job_descriptions']
log(f"      Built descriptions for {len(lines_text):,} quotes")

# Merge back to master
master = master.merge(lines_text, on='quote_id', how='left')

# STEP 4: Re-extract sqft with French number fix
log("\n[4/6] Re-extracting sqft with French number parsing...")

def get_sqft(row):
    # Try quoted_area first
    if pd.notna(row.get('quoted_area')) and row.get('quoted_area', 0) > 0:
        return row['quoted_area'], 'quoted_area'
    # Try text extraction from multiple sources
    for col, source in [
        ('job_description', 'job_description'),
        ('all_job_descriptions', 'all_job_descriptions'),
        ('material_descriptions', 'material_descriptions')
    ]:
        if col in row.index and pd.notna(row.get(col)):
            sqft = extract_sqft(row[col])
            if sqft:
                return sqft, source
    return None, None

def get_sqft_from_dims(row):
    for col in ['job_description', 'all_job_descriptions', 'material_descriptions']:
        if col in row.index and pd.notna(row.get(col)):
            l, w = extract_dimensions(row[col])
            if l and w:
                return l * w
    return None

sqft_results = master.apply(get_sqft, axis=1)
master['sqft_final'] = [r[0] for r in sqft_results]
master['sqft_source'] = [r[1] for r in sqft_results]
sqft_dims = master.apply(get_sqft_from_dims, axis=1)
master['sqft_final'] = master['sqft_final'].fillna(sqft_dims)

new_sqft = master['sqft_final'].notna().sum()
log(f"      New sqft coverage: {new_sqft:,} ({new_sqft/len(master)*100:.1f}%)")
log(f"      Change: {new_sqft - old_sqft:+,} records")

# STEP 5: Recalculate price_per_sqft
log("\n[5/6] Recalculating derived metrics...")
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

# STEP 6: Export
log("\n[6/6] Saving files...")

# Define export columns (exclude all_job_descriptions - too large)
export_columns = [
    'quote_id', 'created_at', 'year', 'quarter', 'month', 'day_of_week', 'week_of_year',
    'quoted_total', 'quoted_hours', 'quoted_area', 'subtotal', 'additional_cost', 'rebate',
    'deposit_required', 'deposit_paid', 'client_id', 'project_id', 'building_id', 'stage_id',
    'sqft_final', 'sqft_source', 'extracted_pitch', 'extracted_layers',
    'job_name', 'job_code', 'job_lang', 'job_category', 'job_line_count',
    'material_line_count', 'material_unique_count', 'material_cost_total', 'material_sell_total',
    'material_margin_pct', 'material_markup_pct', 'material_qty_total',
    'labor_line_count', 'labor_hours_total', 'labor_sell_rate_median', 'labor_cost_rate_median',
    'labor_cost_total', 'labor_sell_total', 'labor_margin_pct',
    'sub_line_count', 'sub_cost_total', 'sub_sell_total', 'sub_margin_pct',
    'total_cost_calculated', 'total_sell_calculated', 'overall_margin', 'overall_margin_pct',
    'material_pct', 'labor_pct', 'sub_pct', 'effective_hourly_rate',
    'price_per_sqft', 'cost_per_sqft', 'complexity_score',
    'has_materials', 'has_labor', 'has_subs',
    'anomaly_flags', 'is_valid_for_analysis', 'labor_data_reliable',
    'job_description', 'material_descriptions', 'sub_descriptions'
]
export_columns = [c for c in export_columns if c in master.columns]
master_export = master[export_columns].copy()

master_export.to_csv(f"{DATA_PATH}master_quotes.csv", index=False)
log(f"      ✓ master_quotes.csv ({len(master_export):,} rows)")

valid = master_export[master_export['is_valid_for_analysis'] == True]
valid.to_csv(f"{DATA_PATH}master_quotes_valid.csv", index=False)
log(f"      ✓ master_quotes_valid.csv ({len(valid):,} rows)")

labor_reliable = master_export[
    (master_export['is_valid_for_analysis'] == True) & 
    (master_export['labor_data_reliable'] == True)
]
labor_reliable.to_csv(f"{DATA_PATH}master_quotes_labor_reliable.csv", index=False)
log(f"      ✓ master_quotes_labor_reliable.csv ({len(labor_reliable):,} rows)")

# Summary
log("\n" + "="*70)
log(" RESULTS SUMMARY")
log("="*70)
valid_data = master[master['is_valid_for_analysis'] == True]
sqft_valid = valid_data['sqft_final'].notna().sum()
log(f"""
 Total quotes:        {len(master):,}
 Valid for analysis:  {len(valid_data):,}
 With sqft data:      {sqft_valid:,} ({sqft_valid/len(valid_data)*100:.1f}%)
 
 Sqft source breakdown:""")
for source, count in valid_data['sqft_source'].value_counts().items():
    log(f"   {source:<25} {count:,}")
log(f"""
 Sqft range:          {valid_data['sqft_final'].min():,.0f} - {valid_data['sqft_final'].max():,.0f}
 Median sqft:         {valid_data['sqft_final'].median():,.0f}
""")
log("="*70)
log("\n✅ PIPELINE v4 COMPLETE\n")
