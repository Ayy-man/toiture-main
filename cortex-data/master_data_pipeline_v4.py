#!/usr/bin/env python3
"""
TOITURELV - MASTER DATA PIPELINE v4
Fixed French number parsing for sqft extraction
"""

import pandas as pd
import numpy as np
import re
import sys
import warnings
warnings.filterwarnings('ignore')

# Force unbuffered output
def log(msg):
    print(msg)
    sys.stdout.flush()

DATA_PATH = "/Users/aymanbaig/Desktop/cortex-data/"
OUTPUT_PATH = DATA_PATH

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def parse_french_number(num_str):
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

def extract_pitch(text):
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
    if pd.isna(text):
        return None
    text = str(text).lower()
    for pattern in [r'(\d)\s*couches?', r'(\d)\s*layers?', r'enlever\s*(\d)', r'remove\s*(\d)']:
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
    if pd.isna(name):
        return None, None
    match = re.match(r'^(\d{2})([A-Z]{2})', str(name))
    if match:
        return match.group(1), match.group(2)
    return None, None

def flag_anomalies(row):
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

log("\n" + "="*70)
log(" TOITURELV - MASTER DATA PIPELINE v4")
log(" Fixed French number parsing for sqft extraction")
log("="*70)

# STEP 1: LOAD DATA (with progress)
log("\n[1/14] Loading data files...")

log("  → Loading Quotes Data Export_clean.csv (83MB)...")
quotes = pd.read_csv(f"{DATA_PATH}Quotes Data Export_clean.csv")
log(f"     ✓ Quotes: {len(quotes):,} rows")

log("  → Loading Quote Materials_clean.csv (9MB)...")
materials = pd.read_csv(f"{DATA_PATH}Quote Materials_clean.csv", engine='python', on_bad_lines='skip')
log(f"     ✓ Materials: {len(materials):,} rows")

log("  → Loading Quote Lines_clean.csv (50MB)...")
lines = pd.read_csv(f"{DATA_PATH}Quote Lines_clean.csv")
log(f"     ✓ Lines: {len(lines):,} rows")

log("  → Loading Quote Time Lines_clean.csv (1MB)...")
time_lines = pd.read_csv(f"{DATA_PATH}Quote Time Lines_clean.csv")
log(f"     ✓ Time Lines: {len(time_lines):,} rows")

log("  → Loading Quote Sub Lines_clean.csv (<1MB)...")
sub_lines = pd.read_csv(f"{DATA_PATH}Quote Sub Lines_clean.csv")
log(f"     ✓ Sub Lines: {len(sub_lines):,} rows")

log("  ✓ All data loaded!")

# STEP 2: TYPE CONVERSIONS
log("\n[2/14] Converting types...")
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

materials['quote_id'] = pd.to_numeric(materials['quote_id'], errors='coerce')
materials['quantity'] = pd.to_numeric(materials['quantity'], errors='coerce')
materials['unit_cost'] = pd.to_numeric(materials['unit_cost'], errors='coerce')
materials['sell_price'] = pd.to_numeric(materials['sell_price'], errors='coerce')
materials['total'] = pd.to_numeric(materials['total'], errors='coerce')

lines['id'] = pd.to_numeric(lines['id'], errors='coerce')
lines['quote_id'] = pd.to_numeric(lines['quote_id'], errors='coerce')

time_lines['quote_id'] = pd.to_numeric(time_lines['quote_id'], errors='coerce')
time_lines['quantity'] = pd.to_numeric(time_lines['quantity'], errors='coerce')
time_lines['unit_price'] = pd.to_numeric(time_lines['unit_price'], errors='coerce')
time_lines['unit_cost'] = pd.to_numeric(time_lines['unit_cost'], errors='coerce')
time_lines = time_lines.rename(columns={'quantity': 'hours', 'unit_price': 'sell_rate', 'unit_cost': 'cost_rate'})

sub_lines['quote_id'] = pd.to_numeric(sub_lines['quote_id'], errors='coerce')
sub_lines['cost'] = pd.to_numeric(sub_lines['cost'], errors='coerce')
sub_lines['price'] = pd.to_numeric(sub_lines['price'], errors='coerce')
sub_lines = sub_lines.rename(columns={'price': 'sell_price'})
log("  ✓ Done")

# STEP 3: AGGREGATE MATERIALS
log("\n[3/14] Aggregating materials...")
materials['material_cost_calc'] = materials['unit_cost'] * materials['quantity']
materials_agg = materials.groupby('quote_id').agg({
    'id': 'count',
    'material_cost_calc': 'sum',
    'total': 'sum',
    'quantity': 'sum',
    'material_id': 'nunique',
    'description': lambda x: ' | '.join(x.dropna().astype(str).head(5))
}).reset_index()
materials_agg.columns = ['quote_id', 'material_line_count', 'material_cost_total', 'material_sell_total', 'material_qty_total', 'material_unique_count', 'material_descriptions']
materials_agg['material_margin_pct'] = np.where(materials_agg['material_sell_total'] > 0, ((materials_agg['material_sell_total'] - materials_agg['material_cost_total']) / materials_agg['material_sell_total'] * 100).round(2), None)
materials_agg['material_markup_pct'] = np.where(materials_agg['material_cost_total'] > 0, ((materials_agg['material_sell_total'] - materials_agg['material_cost_total']) / materials_agg['material_cost_total'] * 100).round(2), None)
log(f"  ✓ Materials: {len(materials_agg):,} quotes")

# STEP 4: AGGREGATE LABOR
log("\n[4/14] Aggregating labor...")
time_lines['labor_cost'] = time_lines['hours'] * time_lines['cost_rate']
time_lines['labor_sell'] = time_lines['hours'] * time_lines['sell_rate']
labor_agg = time_lines.groupby('quote_id').agg({
    'id': 'count',
    'hours': 'sum',
    'sell_rate': 'median',
    'cost_rate': 'median',
    'labor_cost': 'sum',
    'labor_sell': 'sum'
}).reset_index()
labor_agg.columns = ['quote_id', 'labor_line_count', 'labor_hours_total', 'labor_sell_rate_median', 'labor_cost_rate_median', 'labor_cost_total', 'labor_sell_total']
labor_agg['labor_margin_pct'] = np.where(labor_agg['labor_sell_total'] > 0, ((labor_agg['labor_sell_total'] - labor_agg['labor_cost_total']) / labor_agg['labor_sell_total'] * 100).round(2), None)
log(f"  ✓ Labor: {len(labor_agg):,} quotes")

# STEP 5: AGGREGATE SUBS
log("\n[5/14] Aggregating subcontractors...")
sub_agg = sub_lines.groupby('quote_id').agg({
    'id': 'count',
    'cost': 'sum',
    'sell_price': 'sum',
    'description': lambda x: ' | '.join(x.dropna().astype(str).head(3))
}).reset_index()
sub_agg.columns = ['quote_id', 'sub_line_count', 'sub_cost_total', 'sub_sell_total', 'sub_descriptions']
sub_agg['sub_margin_pct'] = np.where(sub_agg['sub_sell_total'] > 0, ((sub_agg['sub_sell_total'] - sub_agg['sub_cost_total']) / sub_agg['sub_sell_total'] * 100).round(2), None)
log(f"  ✓ Subs: {len(sub_agg):,} quotes")

# STEP 6: PROCESS LINES
log("\n[6/14] Processing job lines...")
lines_sorted = lines.sort_values(['quote_id', 'id'])
lines_primary = lines_sorted.groupby('quote_id').first().reset_index()[['quote_id', 'name', 'description']]
lines_primary.columns = ['quote_id', 'job_name', 'job_description']
lines_primary['job_code'], lines_primary['job_lang'] = zip(*lines_primary['job_name'].apply(extract_job_code))
lines_primary['job_category'] = lines_primary['job_name'].apply(categorize_job_type)
lines_count = lines.groupby('quote_id').agg({'id': 'count', 'description': lambda x: ' | '.join(x.dropna().astype(str))}).reset_index()
lines_count.columns = ['quote_id', 'job_line_count', 'all_job_descriptions']
lines_agg = lines_primary.merge(lines_count, on='quote_id', how='left')
log(f"  ✓ Lines: {len(lines_agg):,} quotes")

# STEP 7: BUILD MASTER
log("\n[7/14] Building master table...")
master = quotes.rename(columns={'id': 'quote_id'}).copy()
master['year'] = master['created_at'].dt.year
master['quarter'] = master['created_at'].dt.quarter
master['month'] = master['created_at'].dt.month
master['day_of_week'] = master['created_at'].dt.dayofweek
master['week_of_year'] = master['created_at'].dt.isocalendar().week
master = master.merge(materials_agg, on='quote_id', how='left')
master = master.merge(labor_agg, on='quote_id', how='left')
master = master.merge(sub_agg, on='quote_id', how='left')
master = master.merge(lines_agg, on='quote_id', how='left')
log(f"  ✓ Master: {len(master):,} rows, {len(master.columns)} columns")

# STEP 8: EXTRACT SQFT (v4 FIX)
log("\n[8/14] Extracting sqft (v4 French number fix)...")

def get_sqft(row):
    if pd.notna(row.get('quoted_area')) and row['quoted_area'] > 0:
        return row['quoted_area'], 'quoted_area'
    for col, source in [('job_description', 'job_description'), ('all_job_descriptions', 'all_job_descriptions'), ('material_descriptions', 'material_descriptions')]:
        sqft = extract_sqft(row.get(col, ''))
        if sqft:
            return sqft, source
    return None, None

def get_sqft_from_dims(row):
    for col in ['job_description', 'all_job_descriptions', 'material_descriptions']:
        if pd.notna(row.get(col)):
            l, w = extract_dimensions(row[col])
            if l and w:
                return l * w
    return None

log("  → Extracting from descriptions (this takes ~30 sec)...")
sqft_results = master.apply(get_sqft, axis=1)
master['extracted_sqft'] = [r[0] for r in sqft_results]
master['sqft_source'] = [r[1] for r in sqft_results]
master['sqft_from_dims'] = master.apply(get_sqft_from_dims, axis=1)
master['sqft_final'] = master['extracted_sqft'].fillna(master['sqft_from_dims'])
master['extracted_pitch'] = master['all_job_descriptions'].apply(extract_pitch)
master['extracted_layers'] = master['all_job_descriptions'].apply(extract_layers)

sqft_found = master['sqft_final'].notna().sum()
log(f"  ✓ SqFt found: {sqft_found:,} ({sqft_found/len(master)*100:.1f}%)")

# STEP 9: DERIVED METRICS
log("\n[9/14] Calculating derived metrics...")
for col in ['material_cost_total', 'material_sell_total', 'labor_cost_total', 'labor_sell_total', 'sub_cost_total', 'sub_sell_total', 'labor_hours_total']:
    master[col] = master[col].fillna(0)

master['total_cost_calculated'] = master['material_cost_total'] + master['labor_cost_total'] + master['sub_cost_total']
master['total_sell_calculated'] = master['material_sell_total'] + master['labor_sell_total'] + master['sub_sell_total']
master['overall_margin'] = master['quoted_total'] - master['total_cost_calculated']
master['overall_margin_pct'] = np.where(master['quoted_total'] > 0, (master['overall_margin'] / master['quoted_total'] * 100).round(2), None)
master['material_pct'] = np.where(master['quoted_total'] > 0, (master['material_sell_total'] / master['quoted_total'] * 100).round(2), None)
master['labor_pct'] = np.where(master['quoted_total'] > 0, (master['labor_sell_total'] / master['quoted_total'] * 100).round(2), None)
master['sub_pct'] = np.where(master['quoted_total'] > 0, (master['sub_sell_total'] / master['quoted_total'] * 100).round(2), None)
master['effective_hourly_rate'] = np.where(master['labor_hours_total'] > 0, (master['quoted_total'] / master['labor_hours_total']).round(2), None)
master['price_per_sqft'] = np.where((master['sqft_final'].notna()) & (master['sqft_final'] > 0), (master['quoted_total'] / master['sqft_final']).round(2), None)
master['cost_per_sqft'] = np.where((master['sqft_final'].notna()) & (master['sqft_final'] > 0), (master['total_cost_calculated'] / master['sqft_final']).round(2), None)
master['complexity_score'] = master['material_line_count'].fillna(0) + master['job_line_count'].fillna(0) + master['labor_line_count'].fillna(0) + master['sub_line_count'].fillna(0)
master['has_materials'] = master['material_cost_total'] > 0
master['has_labor'] = master['labor_hours_total'] > 0
master['has_subs'] = master['sub_cost_total'] > 0

for col in ['overall_margin_pct', 'material_margin_pct', 'labor_margin_pct', 'sub_margin_pct', 'material_markup_pct']:
    if col in master.columns:
        master[col] = pd.to_numeric(master[col], errors='coerce')
log("  ✓ Done")

# STEP 10: FLAGS
log("\n[10/14] Flagging anomalies...")
master['anomaly_flags'] = master.apply(flag_anomalies, axis=1)
log("  ✓ Done")

# STEP 11: VALID SUBSET
log("\n[11/14] Creating valid subset...")
valid_mask = (
    (master['quoted_total'] > 100) &
    (master['quoted_total'] < 500000) &
    (master['year'] >= 2020) &
    (master['year'] <= 2025) &
    (master['overall_margin_pct'].isna() | ((master['overall_margin_pct'] > -10) & (master['overall_margin_pct'] < 80)))
)
master['is_valid_for_analysis'] = valid_mask
master['labor_data_reliable'] = master['year'] != 2022
log(f"  ✓ Valid: {valid_mask.sum():,} ({valid_mask.sum()/len(master)*100:.1f}%)")

# STEP 12: EXPORT
log("\n[12/14] Exporting CSV files...")
export_columns = [
    'quote_id', 'created_at', 'year', 'quarter', 'month', 'day_of_week', 'week_of_year',
    'quoted_total', 'quoted_hours', 'quoted_area', 'subtotal', 'additional_cost', 'rebate', 'deposit_required', 'deposit_paid',
    'client_id', 'project_id', 'building_id', 'stage_id',
    'sqft_final', 'sqft_source', 'extracted_pitch', 'extracted_layers',
    'job_name', 'job_code', 'job_lang', 'job_category', 'job_line_count',
    'material_line_count', 'material_unique_count', 'material_cost_total', 'material_sell_total', 'material_margin_pct', 'material_markup_pct', 'material_qty_total',
    'labor_line_count', 'labor_hours_total', 'labor_sell_rate_median', 'labor_cost_rate_median', 'labor_cost_total', 'labor_sell_total', 'labor_margin_pct',
    'sub_line_count', 'sub_cost_total', 'sub_sell_total', 'sub_margin_pct',
    'total_cost_calculated', 'total_sell_calculated', 'overall_margin', 'overall_margin_pct',
    'material_pct', 'labor_pct', 'sub_pct', 'effective_hourly_rate', 'price_per_sqft', 'cost_per_sqft',
    'complexity_score', 'has_materials', 'has_labor', 'has_subs',
    'anomaly_flags', 'is_valid_for_analysis', 'labor_data_reliable',
    'job_description', 'material_descriptions', 'sub_descriptions'
]
export_columns = [c for c in export_columns if c in master.columns]
master_export = master[export_columns].copy()

log("  → Saving master_quotes.csv...")
master_export.to_csv(f"{OUTPUT_PATH}master_quotes.csv", index=False)
log(f"     ✓ {len(master_export):,} rows")

analysis_ready = master_export[master_export['is_valid_for_analysis'] == True].copy()
log("  → Saving master_quotes_valid.csv...")
analysis_ready.to_csv(f"{OUTPUT_PATH}master_quotes_valid.csv", index=False)
log(f"     ✓ {len(analysis_ready):,} rows")

labor_reliable = master_export[(master_export['is_valid_for_analysis'] == True) & (master_export['labor_data_reliable'] == True)].copy()
log("  → Saving master_quotes_labor_reliable.csv...")
labor_reliable.to_csv(f"{OUTPUT_PATH}master_quotes_labor_reliable.csv", index=False)
log(f"     ✓ {len(labor_reliable):,} rows")

# STEP 13: SUMMARY
log("\n[13/14] Results summary...")
valid = master[master['is_valid_for_analysis'] == True]
sqft_valid = valid['sqft_final'].notna().sum()

log(f"""
{'='*60}
 SQFT EXTRACTION RESULTS (v4)
{'='*60}
 Valid quotes:     {len(valid):,}
 With sqft:        {sqft_valid:,} ({sqft_valid/len(valid)*100:.1f}%)
{'='*60}
 Source breakdown:""")
for source, count in valid['sqft_source'].value_counts().items():
    log(f"   {source:<25} {count:,}")
log(f"""{'='*60}
 Sqft range:       {valid['sqft_final'].min():,.0f} - {valid['sqft_final'].max():,.0f}
 Median:           {valid['sqft_final'].median():,.0f} sqft
{'='*60}
""")

# STEP 14: DONE
log("\n[14/14] ✅ PIPELINE v4 COMPLETE")
log("""
Files saved:
  • master_quotes.csv
  • master_quotes_valid.csv  
  • master_quotes_labor_reliable.csv
""")
