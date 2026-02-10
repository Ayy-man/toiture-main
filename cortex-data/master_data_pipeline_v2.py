#!/usr/bin/env python3
"""
================================================================================
TOITURELV - MASTER DATA PIPELINE (VERIFIED SCHEMA)
================================================================================
The foundation for Cortex pricing algorithm.

This script:
1. Loads all 6 clean CSV tables
2. Validates foreign key relationships
3. Joins everything into master dataset
4. Calculates derived fields (margins, ratios, etc.)
5. Extracts sqft from descriptions (regex)
6. Standardizes job types
7. Flags anomalies
8. Exports master_quotes.csv

VERIFIED SCHEMA:
- Quotes: id, quoted_total, quoted_hours, quoted_area, subtotal, created_at...
- Quote Lines: id, quote_id, name, description, total, quantity...
- Quote Time Lines: id, quote_id, quantity (hours), unit_price (sell), unit_cost...
- Quote Sub Lines: id, quote_id, cost, price, description...
- Quote Materials: id, quote_id, material_id, quantity, unit_cost, sell_price, total...

Author: Hexona Systems
Project: TOITURELV Cortex
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
    """
    Extract square footage from text descriptions.
    Handles various French and English formats.
    """
    if pd.isna(text):
        return None
    
    text = str(text).lower()
    
    # Patterns to try (most specific to least specific)
    patterns = [
        # "2500 pi²" or "2500 pi2" or "2,500 pi²"
        r'([\d,\s]+(?:\.\d+)?)\s*pi[²2]',
        # "2500 sqft" or "2500 sq ft" or "2500 sq.ft"
        r'([\d,\s]+(?:\.\d+)?)\s*sq\.?\s*ft',
        # "2500 square feet"
        r'([\d,\s]+(?:\.\d+)?)\s*square\s*feet',
        # "2500 pieds carrés" or "2500 pieds carres"
        r'([\d,\s]+(?:\.\d+)?)\s*pieds?\s*carr[ée]s?',
        # "2500 pc" (pieds carrés abbreviation)
        r'([\d,\s]+(?:\.\d+)?)\s*p\.?c\.?(?:\s|$)',
        # "surface: 2500" or "superficie: 2500"
        r'(?:surface|superficie|area)\s*[:\s]\s*([\d,\s]+(?:\.\d+)?)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            num_str = match.group(1).replace(',', '').replace(' ', '')
            try:
                value = float(num_str)
                # Sanity check: sqft should be between 50 and 100,000
                if 50 <= value <= 100000:
                    return value
            except:
                continue
    
    return None


def extract_dimensions(text):
    """
    Extract dimensions like "20x30" or "20' x 30'"
    Returns (length, width) or (None, None)
    """
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
    """
    Extract roof pitch like "6/12" or "6:12"
    """
    if pd.isna(text):
        return None
    
    text = str(text)
    match = re.search(r'(\d{1,2})\s*[/:\-]\s*12', text)
    if match:
        try:
            pitch = int(match.group(1))
            if 0 <= pitch <= 24:
                return pitch
        except:
            pass
    return None


def extract_layers(text):
    """
    Extract number of layers to remove
    """
    if pd.isna(text):
        return None
    
    text = str(text).lower()
    
    patterns = [
        r'(\d)\s*couches?',
        r'(\d)\s*layers?',
        r'enlever\s*(\d)',
        r'remove\s*(\d)',
    ]
    
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
    """
    Standardize job types from quote_lines.name
    """
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
    """
    Extract numeric job codes like "40FR", "20FR", "90EN"
    """
    if pd.isna(name):
        return None, None
    
    match = re.match(r'^(\d{2})([A-Z]{2})', str(name))
    if match:
        return match.group(1), match.group(2)
    return None, None


def flag_anomalies(row):
    """
    Flag potential data quality issues
    """
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
    
    if pd.notna(row.get('material_pct')) and row['material_pct'] > 90:
        flags.append('UNUSUAL_MATERIAL_RATIO')
    if pd.notna(row.get('labor_pct')) and row['labor_pct'] > 90:
        flags.append('UNUSUAL_LABOR_RATIO')
    
    return '|'.join(flags) if flags else None


# =============================================================================
# MAIN PIPELINE
# =============================================================================

print("\n" + "="*80)
print(" TOITURELV - MASTER DATA PIPELINE")
print(" Building the Foundation for Cortex")
print("="*80)

# -----------------------------------------------------------------------------
# STEP 1: LOAD ALL TABLES
# -----------------------------------------------------------------------------
print("\n" + "-"*80)
print(" STEP 1: LOADING ALL DATA TABLES")
print("-"*80)

print("\nLoading tables...")

quotes = pd.read_csv(f"{DATA_PATH}Quotes Data Export_clean.csv")
print(f"  ✓ Quotes: {len(quotes):,} records, {len(quotes.columns)} columns")

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

# Quotes - using actual column names
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

# Materials - using actual column names
materials['quote_id'] = pd.to_numeric(materials['quote_id'], errors='coerce')
materials['material_id'] = pd.to_numeric(materials['material_id'], errors='coerce')
materials['quantity'] = pd.to_numeric(materials['quantity'], errors='coerce')
materials['unit_cost'] = pd.to_numeric(materials['unit_cost'], errors='coerce')
materials['total'] = pd.to_numeric(materials['total'], errors='coerce')
materials['sell_price'] = pd.to_numeric(materials['sell_price'], errors='coerce')
materials['created_at'] = pd.to_datetime(materials['created_at'], errors='coerce')

print(f"  ✓ Materials converted")

# Lines - using actual column names
lines['id'] = pd.to_numeric(lines['id'], errors='coerce')
lines['quote_id'] = pd.to_numeric(lines['quote_id'], errors='coerce')
lines['total'] = pd.to_numeric(lines['total'], errors='coerce')
lines['quantity'] = pd.to_numeric(lines['quantity'], errors='coerce')

print(f"  ✓ Quote Lines converted")

# Time Lines - IMPORTANT: quantity = hours, unit_price = sell rate, unit_cost = cost rate
time_lines['id'] = pd.to_numeric(time_lines['id'], errors='coerce')
time_lines['quote_id'] = pd.to_numeric(time_lines['quote_id'], errors='coerce')
time_lines['quantity'] = pd.to_numeric(time_lines['quantity'], errors='coerce')  # This is HOURS
time_lines['unit_price'] = pd.to_numeric(time_lines['unit_price'], errors='coerce')  # This is SELL RATE
time_lines['unit_cost'] = pd.to_numeric(time_lines['unit_cost'], errors='coerce')  # This is COST RATE
time_lines['total'] = pd.to_numeric(time_lines['total'], errors='coerce')

# Rename for clarity
time_lines = time_lines.rename(columns={
    'quantity': 'hours',
    'unit_price': 'sell_rate',
    'unit_cost': 'cost_rate'
})

print(f"  ✓ Time Lines converted (quantity→hours, unit_price→sell_rate, unit_cost→cost_rate)")

# Sub Lines - using actual column names: cost, price
sub_lines['id'] = pd.to_numeric(sub_lines['id'], errors='coerce')
sub_lines['quote_id'] = pd.to_numeric(sub_lines['quote_id'], errors='coerce')
sub_lines['cost'] = pd.to_numeric(sub_lines['cost'], errors='coerce')
sub_lines['price'] = pd.to_numeric(sub_lines['price'], errors='coerce')  # This is sell price

# Rename for clarity
sub_lines = sub_lines.rename(columns={'price': 'sell_price'})

print(f"  ✓ Sub Lines converted (price→sell_price)")

# -----------------------------------------------------------------------------
# STEP 3: VALIDATE FOREIGN KEYS
# -----------------------------------------------------------------------------
print("\n" + "-"*80)
print(" STEP 3: VALIDATING FOREIGN KEY RELATIONSHIPS")
print("-"*80)

quote_ids = set(quotes['id'].dropna().astype(int))
print(f"\nUnique quote IDs in quotes table: {len(quote_ids):,}")

# Materials
mat_quote_ids = set(materials['quote_id'].dropna().astype(int))
mat_orphans = mat_quote_ids - quote_ids
print(f"\nMaterials:")
print(f"  Unique quote_ids referenced: {len(mat_quote_ids):,}")
print(f"  Orphan records (no matching quote): {len(mat_orphans):,}")

# Lines
line_quote_ids = set(lines['quote_id'].dropna().astype(int))
line_orphans = line_quote_ids - quote_ids
print(f"\nQuote Lines:")
print(f"  Unique quote_ids referenced: {len(line_quote_ids):,}")
print(f"  Orphan records: {len(line_orphans):,}")

# Time Lines
time_quote_ids = set(time_lines['quote_id'].dropna().astype(int))
time_orphans = time_quote_ids - quote_ids
print(f"\nTime Lines:")
print(f"  Unique quote_ids referenced: {len(time_quote_ids):,}")
print(f"  Orphan records: {len(time_orphans):,}")

# Sub Lines
sub_quote_ids = set(sub_lines['quote_id'].dropna().astype(int))
sub_orphans = sub_quote_ids - quote_ids
print(f"\nSub Lines:")
print(f"  Unique quote_ids referenced: {len(sub_quote_ids):,}")
print(f"  Orphan records: {len(sub_orphans):,}")

# Coverage stats
quotes_with_materials = quote_ids.intersection(mat_quote_ids)
quotes_with_lines = quote_ids.intersection(line_quote_ids)
quotes_with_labor = quote_ids.intersection(time_quote_ids)
quotes_with_subs = quote_ids.intersection(sub_quote_ids)

print(f"\nQuote Coverage:")
print(f"  Quotes with materials: {len(quotes_with_materials):,} ({len(quotes_with_materials)/len(quote_ids)*100:.1f}%)")
print(f"  Quotes with line items: {len(quotes_with_lines):,} ({len(quotes_with_lines)/len(quote_ids)*100:.1f}%)")
print(f"  Quotes with labor: {len(quotes_with_labor):,} ({len(quotes_with_labor)/len(quote_ids)*100:.1f}%)")
print(f"  Quotes with subs: {len(quotes_with_subs):,} ({len(quotes_with_subs)/len(quote_ids)*100:.1f}%)")

# -----------------------------------------------------------------------------
# STEP 4: AGGREGATE MATERIALS PER QUOTE
# -----------------------------------------------------------------------------
print("\n" + "-"*80)
print(" STEP 4: AGGREGATING MATERIALS PER QUOTE")
print("-"*80)

# Calculate sell total for materials (sell_price * quantity)
materials['material_sell_value'] = materials['sell_price'] * materials['quantity']

materials_agg = materials.groupby('quote_id').agg({
    'id': 'count',
    'unit_cost': 'mean',
    'total': 'sum',  # This is cost total (unit_cost * quantity)
    'material_sell_value': 'sum',  # This is sell total
    'quantity': 'sum',
    'material_id': 'nunique',
    'description': lambda x: ' | '.join(x.dropna().astype(str).head(5))
}).reset_index()

materials_agg.columns = [
    'quote_id', 
    'material_line_count',
    'material_avg_unit_cost',
    'material_cost_total',
    'material_sell_total',
    'material_qty_total',
    'material_unique_count',
    'material_descriptions'
]

# Calculate material margin
materials_agg['material_margin'] = materials_agg['material_sell_total'] - materials_agg['material_cost_total']
materials_agg['material_margin_pct'] = np.where(
    materials_agg['material_sell_total'] > 0,
    (materials_agg['material_margin'] / materials_agg['material_sell_total'] * 100).round(2),
    None
)

print(f"  ✓ Aggregated materials for {len(materials_agg):,} quotes")

# -----------------------------------------------------------------------------
# STEP 5: AGGREGATE LABOR PER QUOTE
# -----------------------------------------------------------------------------
print("\n" + "-"*80)
print(" STEP 5: AGGREGATING LABOR PER QUOTE")
print("-"*80)

# Calculate labor cost and sell
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

# Calculate labor margin
labor_agg['labor_margin'] = labor_agg['labor_sell_total'] - labor_agg['labor_cost_total']
labor_agg['labor_margin_pct'] = np.where(
    labor_agg['labor_sell_total'] > 0,
    (labor_agg['labor_margin'] / labor_agg['labor_sell_total'] * 100).round(2),
    None
)

print(f"  ✓ Aggregated labor for {len(labor_agg):,} quotes")

# Quick stats
print(f"\n  Labor Rate Stats:")
print(f"    Sell rate median: ${time_lines['sell_rate'].median():.2f}/hr")
print(f"    Cost rate median: ${time_lines['cost_rate'].median():.2f}/hr")
print(f"    Hours median: {time_lines['hours'].median():.1f}")

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

# Calculate sub margin
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

# Get primary job type per quote (first line item by position or id)
lines_sorted = lines.sort_values(['quote_id', 'id'])
lines_primary = lines_sorted.groupby('quote_id').first().reset_index()
lines_primary = lines_primary[['quote_id', 'name', 'description']].copy()
lines_primary.columns = ['quote_id', 'job_name', 'job_description']

# Extract job codes
lines_primary['job_code'], lines_primary['job_lang'] = zip(*lines_primary['job_name'].apply(extract_job_code))

# Categorize job types
lines_primary['job_category'] = lines_primary['job_name'].apply(categorize_job_type)

# Count total lines per quote
lines_count = lines.groupby('quote_id').agg({
    'id': 'count',
    'description': lambda x: ' | '.join(x.dropna().astype(str))
}).reset_index()
lines_count.columns = ['quote_id', 'job_line_count', 'all_job_descriptions']

# Merge
lines_agg = lines_primary.merge(lines_count, on='quote_id', how='left')

print(f"  ✓ Processed job lines for {len(lines_agg):,} quotes")

# Job type distribution
print("\n  Job Category Distribution:")
job_dist = lines_agg['job_category'].value_counts()
for cat, count in job_dist.head(10).items():
    print(f"    {cat}: {count:,} ({count/len(lines_agg)*100:.1f}%)")

# -----------------------------------------------------------------------------
# STEP 8: BUILD MASTER QUOTES TABLE
# -----------------------------------------------------------------------------
print("\n" + "-"*80)
print(" STEP 8: BUILDING MASTER QUOTES TABLE")
print("-"*80)

# Start with quotes base
master = quotes.copy()
master = master.rename(columns={'id': 'quote_id'})

# Add date features
master['year'] = master['created_at'].dt.year
master['quarter'] = master['created_at'].dt.quarter
master['month'] = master['created_at'].dt.month
master['day_of_week'] = master['created_at'].dt.dayofweek
master['week_of_year'] = master['created_at'].dt.isocalendar().week

# Join all aggregations
print("\n  Joining tables...")

master = master.merge(materials_agg, on='quote_id', how='left')
print(f"    + Materials: {len(master):,} rows")

master = master.merge(labor_agg, on='quote_id', how='left')
print(f"    + Labor: {len(master):,} rows")

master = master.merge(sub_agg, on='quote_id', how='left')
print(f"    + Subs: {len(master):,} rows")

master = master.merge(lines_agg, on='quote_id', how='left')
print(f"    + Job Lines: {len(master):,} rows")

print(f"\n  ✓ Master table: {len(master):,} rows, {len(master.columns)} columns")

# -----------------------------------------------------------------------------
# STEP 9: EXTRACT SQFT FROM DESCRIPTIONS
# -----------------------------------------------------------------------------
print("\n" + "-"*80)
print(" STEP 9: EXTRACTING SQUARE FOOTAGE FROM DESCRIPTIONS")
print("-"*80)

def get_sqft(row):
    # First try the quoted_area if it exists and is valid
    if pd.notna(row.get('quoted_area')) and row['quoted_area'] > 0:
        return row['quoted_area'], 'quoted_area'
    
    # Try job description
    sqft = extract_sqft(row.get('job_description', ''))
    if sqft:
        return sqft, 'job_description'
    
    # Try all job descriptions
    sqft = extract_sqft(row.get('all_job_descriptions', ''))
    if sqft:
        return sqft, 'all_job_descriptions'
    
    # Try material descriptions
    sqft = extract_sqft(row.get('material_descriptions', ''))
    if sqft:
        return sqft, 'material_descriptions'
    
    return None, None

# Apply extraction
sqft_results = master.apply(get_sqft, axis=1)
master['extracted_sqft'] = [r[0] for r in sqft_results]
master['sqft_source'] = [r[1] for r in sqft_results]

# Also try dimensions
def get_sqft_from_dims(row):
    for col in ['job_description', 'all_job_descriptions', 'material_descriptions']:
        if pd.notna(row.get(col)):
            l, w = extract_dimensions(row[col])
            if l and w:
                return l * w
    return None

master['sqft_from_dims'] = master.apply(get_sqft_from_dims, axis=1)

# Combine: prefer extracted, then dims
master['sqft_final'] = master['extracted_sqft'].fillna(master['sqft_from_dims'])

# Stats
sqft_found = master['sqft_final'].notna().sum()
print(f"\n  Square footage extraction results:")
print(f"    From quoted_area field: {(master['sqft_source'] == 'quoted_area').sum():,}")
print(f"    From job descriptions: {(master['sqft_source'] == 'job_description').sum():,}")
print(f"    From all descriptions: {(master['sqft_source'] == 'all_job_descriptions').sum():,}")
print(f"    From material descriptions: {(master['sqft_source'] == 'material_descriptions').sum():,}")
print(f"    From dimensions (L×W): {master['sqft_from_dims'].notna().sum():,}")
print(f"    TOTAL with sqft: {sqft_found:,} ({sqft_found/len(master)*100:.1f}%)")
print(f"    Still missing: {len(master) - sqft_found:,} ({(len(master)-sqft_found)/len(master)*100:.1f}%)")

# Extract pitch and layers
master['extracted_pitch'] = master['all_job_descriptions'].apply(extract_pitch)
master['extracted_layers'] = master['all_job_descriptions'].apply(extract_layers)

pitch_found = master['extracted_pitch'].notna().sum()
layers_found = master['extracted_layers'].notna().sum()
print(f"\n  Additional extractions:")
print(f"    Roof pitch found: {pitch_found:,} ({pitch_found/len(master)*100:.1f}%)")
print(f"    Layers to remove found: {layers_found:,} ({layers_found/len(master)*100:.1f}%)")

# -----------------------------------------------------------------------------
# STEP 10: CALCULATE DERIVED METRICS
# -----------------------------------------------------------------------------
print("\n" + "-"*80)
print(" STEP 10: CALCULATING DERIVED METRICS")
print("-"*80)

# Fill NAs for calculations
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

# Component ratios (as % of quote total)
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

# Effective hourly rate (total / hours)
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

# Has components flags
master['has_materials'] = master['material_cost_total'] > 0
master['has_labor'] = master['labor_hours_total'] > 0
master['has_subs'] = master['sub_cost_total'] > 0

# Convert to proper types for margin stats
master['overall_margin_pct'] = pd.to_numeric(master['overall_margin_pct'], errors='coerce')
master['material_margin_pct'] = pd.to_numeric(master['material_margin_pct'], errors='coerce')
master['labor_margin_pct'] = pd.to_numeric(master['labor_margin_pct'], errors='coerce')
master['sub_margin_pct'] = pd.to_numeric(master['sub_margin_pct'], errors='coerce')

print("  ✓ Calculated derived metrics:")
print(f"    • Overall margin (median): {master['overall_margin_pct'].median():.1f}%")
print(f"    • Material % of total (median): {master['material_pct'].median():.1f}%")
print(f"    • Labor % of total (median): {master['labor_pct'].median():.1f}%")
print(f"    • Effective $/hr (median): ${master['effective_hourly_rate'].median():,.0f}")

sqft_prices = master['price_per_sqft'].dropna()
if len(sqft_prices) > 0:
    print(f"    • Price per sqft (median): ${sqft_prices.median():,.2f}")

# -----------------------------------------------------------------------------
# STEP 11: FLAG ANOMALIES
# -----------------------------------------------------------------------------
print("\n" + "-"*80)
print(" STEP 11: FLAGGING ANOMALIES")
print("-"*80)

master['anomaly_flags'] = master.apply(flag_anomalies, axis=1)

# Count anomalies
anomaly_counts = master['anomaly_flags'].dropna().str.split('|').explode().value_counts()
print("\n  Anomaly Detection Results:")
for flag, count in anomaly_counts.items():
    print(f"    {flag}: {count:,}")

total_clean = master['anomaly_flags'].isna().sum()
total_flagged = len(master) - total_clean
print(f"\n  Clean records: {total_clean:,} ({total_clean/len(master)*100:.1f}%)")
print(f"  Flagged records: {total_flagged:,} ({total_flagged/len(master)*100:.1f}%)")

# -----------------------------------------------------------------------------
# STEP 12: FILTER FOR VALID ANALYSIS SET
# -----------------------------------------------------------------------------
print("\n" + "-"*80)
print(" STEP 12: CREATING ANALYSIS-READY SUBSET")
print("-"*80)

# Define valid quotes for analysis
valid_mask = (
    (master['quoted_total'] > 100) &
    (master['quoted_total'] < 500000) &
    (master['year'] >= 2020) &
    (master['year'] <= 2025) &
    (master['overall_margin_pct'].isna() | 
     ((master['overall_margin_pct'] > -10) & (master['overall_margin_pct'] < 80)))
)

master['is_valid_for_analysis'] = valid_mask

valid_count = valid_mask.sum()
print(f"\n  Valid for analysis: {valid_count:,} ({valid_count/len(master)*100:.1f}%)")
print(f"  Excluded: {len(master) - valid_count:,}")

# -----------------------------------------------------------------------------
# STEP 13: EXPORT MASTER TABLE
# -----------------------------------------------------------------------------
print("\n" + "-"*80)
print(" STEP 13: EXPORTING MASTER TABLE")
print("-"*80)

# Select and order columns for export
export_columns = [
    # Identifiers
    'quote_id', 'created_at', 'year', 'quarter', 'month', 'day_of_week', 'week_of_year',
    
    # Quote basics
    'quoted_total', 'quoted_hours', 'quoted_area', 'subtotal', 
    'additional_cost', 'rebate', 'deposit_required', 'deposit_paid',
    
    # Client/Project info
    'client_id', 'project_id', 'building_id', 'stage_id',
    
    # Extracted data
    'sqft_final', 'sqft_source', 'extracted_pitch', 'extracted_layers',
    
    # Job info
    'job_name', 'job_code', 'job_lang', 'job_category', 'job_line_count',
    
    # Materials
    'material_line_count', 'material_unique_count', 'material_cost_total', 
    'material_sell_total', 'material_margin_pct', 'material_qty_total',
    
    # Labor
    'labor_line_count', 'labor_hours_total', 'labor_sell_rate_median',
    'labor_cost_rate_median', 'labor_cost_total', 'labor_sell_total', 'labor_margin_pct',
    
    # Subs
    'sub_line_count', 'sub_cost_total', 'sub_sell_total', 'sub_margin_pct',
    
    # Calculated metrics
    'total_cost_calculated', 'total_sell_calculated', 
    'overall_margin', 'overall_margin_pct',
    'material_pct', 'labor_pct', 'sub_pct',
    'effective_hourly_rate', 'price_per_sqft', 'cost_per_sqft',
    'complexity_score',
    
    # Flags
    'has_materials', 'has_labor', 'has_subs',
    'anomaly_flags', 'is_valid_for_analysis',
    
    # Descriptions (for reference/text mining)
    'job_description', 'material_descriptions', 'sub_descriptions'
]

# Only include columns that exist
export_columns = [c for c in export_columns if c in master.columns]

master_export = master[export_columns].copy()

# Save full master
master_export.to_csv(f"{OUTPUT_PATH}master_quotes.csv", index=False)
print(f"  ✓ Saved: master_quotes.csv ({len(master_export):,} rows, {len(export_columns)} columns)")

# Save analysis-ready subset
analysis_ready = master_export[master_export['is_valid_for_analysis'] == True].copy()
analysis_ready.to_csv(f"{OUTPUT_PATH}master_quotes_valid.csv", index=False)
print(f"  ✓ Saved: master_quotes_valid.csv ({len(analysis_ready):,} rows)")

# -----------------------------------------------------------------------------
# STEP 14: GENERATE SUMMARY STATISTICS
# -----------------------------------------------------------------------------
print("\n" + "-"*80)
print(" STEP 14: SUMMARY STATISTICS")
print("-"*80)

valid = master[master['is_valid_for_analysis'] == True]

print("\n" + "="*80)
print(" MASTER DATA SUMMARY")
print("="*80)

print(f"""
┌──────────────────────────────────────────────────────────────────────────────┐
│                         MASTER DATA OVERVIEW                                 │
├──────────────────────────────────────────────────────────────────────────────┤
│  Total Quotes Processed:     {len(master):>10,}                                    │
│  Valid for Analysis:         {len(valid):>10,}  ({len(valid)/len(master)*100:.1f}%)                          │
│  Date Range:                 {valid['year'].min():.0f} - {valid['year'].max():.0f}                                   │
├──────────────────────────────────────────────────────────────────────────────┤
│                         QUOTE VALUES                                         │
├──────────────────────────────────────────────────────────────────────────────┤
│  Minimum:                    ${valid['quoted_total'].min():>12,.2f}                          │
│  25th Percentile:            ${valid['quoted_total'].quantile(0.25):>12,.2f}                          │
│  Median:                     ${valid['quoted_total'].median():>12,.2f}                          │
│  Mean:                       ${valid['quoted_total'].mean():>12,.2f}                          │
│  75th Percentile:            ${valid['quoted_total'].quantile(0.75):>12,.2f}                          │
│  Maximum:                    ${valid['quoted_total'].max():>12,.2f}                          │
├──────────────────────────────────────────────────────────────────────────────┤
│                         MARGINS                                              │
├──────────────────────────────────────────────────────────────────────────────┤
│  Overall Margin (median):    {valid['overall_margin_pct'].median():>10.1f}%                               │
│  Material Margin (median):   {valid['material_margin_pct'].median():>10.1f}%                               │
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
│  Effective $/hr (median):    ${valid['effective_hourly_rate'].median():>9.2f}                             │
├──────────────────────────────────────────────────────────────────────────────┤
│                         SQ FT PRICING (where available)                      │
├──────────────────────────────────────────────────────────────────────────────┤
│  Quotes with SqFt:           {valid['sqft_final'].notna().sum():>10,}  ({valid['sqft_final'].notna().sum()/len(valid)*100:.1f}%)                          │
│  Median SqFt:                {valid['sqft_final'].median():>10,.0f}                                │
│  Price per SqFt (median):    ${valid['price_per_sqft'].median():>9.2f}                             │
├──────────────────────────────────────────────────────────────────────────────┤
│                         DATA QUALITY                                         │
├──────────────────────────────────────────────────────────────────────────────┤
│  Quotes with Materials:      {valid['has_materials'].sum():>10,}  ({valid['has_materials'].sum()/len(valid)*100:.1f}%)                          │
│  Quotes with Labor:          {valid['has_labor'].sum():>10,}  ({valid['has_labor'].sum()/len(valid)*100:.1f}%)                          │
│  Quotes with Subs:           {valid['has_subs'].sum():>10,}  ({valid['has_subs'].sum()/len(valid)*100:.1f}%)                          │
│  Clean (no anomaly flags):   {valid['anomaly_flags'].isna().sum():>10,}  ({valid['anomaly_flags'].isna().sum()/len(valid)*100:.1f}%)                          │
└──────────────────────────────────────────────────────────────────────────────┘
""")

# Job category breakdown
print("\n" + "="*80)
print(" JOB CATEGORY ANALYSIS")
print("="*80)

print("\n┌" + "─"*95 + "┐")
print("│ {:<20} │ {:>8} │ {:>12} │ {:>10} │ {:>10} │ {:>10} │ {:>8} │".format(
    "Category", "Count", "Median $", "Median Hrs", "$/Hr Eff", "$/SqFt", "Margin%"))
print("├" + "─"*95 + "┤")

for cat in valid['job_category'].value_counts().head(10).index:
    cat_data = valid[valid['job_category'] == cat]
    eff_rate = cat_data['effective_hourly_rate'].median()
    price_sqft = cat_data['price_per_sqft'].median()
    margin = cat_data['overall_margin_pct'].median()
    
    print("│ {:<20} │ {:>8,} │ ${:>10,.0f} │ {:>10.1f} │ ${:>9,.0f} │ ${:>9.2f} │ {:>7.1f}% │".format(
        cat[:20],
        len(cat_data),
        cat_data['quoted_total'].median(),
        cat_data['labor_hours_total'].median() if cat_data['labor_hours_total'].notna().any() else 0,
        eff_rate if pd.notna(eff_rate) else 0,
        price_sqft if pd.notna(price_sqft) else 0,
        margin if pd.notna(margin) else 0
    ))
print("└" + "─"*95 + "┘")

# Year-over-year
print("\n" + "="*80)
print(" YEAR-OVER-YEAR ANALYSIS")
print("="*80)

print("\n┌" + "─"*85 + "┐")
print("│ {:>6} │ {:>8} │ {:>12} │ {:>12} │ {:>10} │ {:>10} │ {:>10} │".format(
    "Year", "Quotes", "Total Rev", "Median $", "Median Hrs", "$/Hr Eff", "Margin%"))
print("├" + "─"*85 + "┤")

for year in sorted(valid['year'].dropna().unique()):
    year_data = valid[valid['year'] == year]
    eff_rate = year_data['effective_hourly_rate'].median()
    margin = year_data['overall_margin_pct'].median()
    
    print("│ {:>6.0f} │ {:>8,} │ ${:>10,.0f} │ ${:>10,.0f} │ {:>10.1f} │ ${:>9,.0f} │ {:>9.1f}% │".format(
        year,
        len(year_data),
        year_data['quoted_total'].sum(),
        year_data['quoted_total'].median(),
        year_data['labor_hours_total'].median() if year_data['labor_hours_total'].notna().any() else 0,
        eff_rate if pd.notna(eff_rate) else 0,
        margin if pd.notna(margin) else 0
    ))
print("└" + "─"*85 + "┘")

# -----------------------------------------------------------------------------
# STEP 15: SAVE DATA DICTIONARY
# -----------------------------------------------------------------------------
print("\n" + "-"*80)
print(" STEP 15: GENERATING DATA DICTIONARY")
print("-"*80)

data_dict = f"""
================================================================================
TOITURELV MASTER QUOTES - DATA DICTIONARY
================================================================================
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}
Records: {len(master):,} total, {len(valid):,} valid for analysis

IDENTIFIERS
-----------
quote_id            : Unique quote identifier (from C-Cube)
created_at          : Quote creation timestamp
year                : Year extracted from created_at
quarter             : Quarter (1-4)
month               : Month (1-12)
day_of_week         : Day of week (0=Monday, 6=Sunday)
week_of_year        : Week number (1-52)

QUOTE BASICS (from C-Cube)
--------------------------
quoted_total        : Final quote price to customer ($)
quoted_hours        : Total hours recorded in C-Cube
quoted_area         : Square footage from C-Cube (often null)
subtotal            : Subtotal before adjustments ($)
additional_cost     : Additional costs added ($)
rebate              : Rebate/discount applied ($)
deposit_required    : Whether deposit was required (boolean)
deposit_paid        : Whether deposit was paid (boolean)

CLIENT/PROJECT INFO
-------------------
client_id           : Client identifier
project_id          : Project identifier
building_id         : Building identifier
stage_id            : Quote stage/status identifier

EXTRACTED DATA
--------------
sqft_final          : Square footage (extracted from descriptions or quoted_area)
sqft_source         : Source of sqft data
extracted_pitch     : Roof pitch (e.g., 6 for 6/12 pitch)
extracted_layers    : Number of layers to remove

JOB INFORMATION
---------------
job_name            : Raw job name from quote lines (e.g., "40FR Chantier Elastomère")
job_code            : Numeric code (e.g., '40' from '40FR')
job_lang            : Language code ('FR' or 'EN')
job_category        : Standardized category (Élastomère, Bardeaux, etc.)
job_line_count      : Number of line items in quote

MATERIALS
---------
material_line_count : Number of material line items
material_unique_count: Number of unique materials used
material_cost_total : Total cost of materials ($) - sum of (unit_cost * quantity)
material_sell_total : Total sell price of materials ($) - sum of (sell_price * quantity)
material_margin_pct : Material margin percentage
material_qty_total  : Total quantity of all materials

LABOR
-----
labor_line_count    : Number of labor line items
labor_hours_total   : Total hours quoted
labor_sell_rate_median: Median hourly sell rate ($/hr)
labor_cost_rate_median: Median hourly cost rate ($/hr)
labor_cost_total    : Total labor cost ($)
labor_sell_total    : Total labor sell ($)
labor_margin_pct    : Labor margin percentage

SUBCONTRACTORS
--------------
sub_line_count      : Number of subcontractor items
sub_cost_total      : Total subcontractor costs ($)
sub_sell_total      : Total subcontractor sell price ($)
sub_margin_pct      : Subcontractor margin percentage

CALCULATED METRICS
------------------
total_cost_calculated: materials + labor + subs costs ($)
total_sell_calculated: materials + labor + subs sells ($)
overall_margin      : quoted_total - total_cost_calculated ($)
overall_margin_pct  : Overall margin as percentage
material_pct        : Materials as % of quoted_total
labor_pct           : Labor as % of quoted_total
sub_pct             : Subs as % of quoted_total
effective_hourly_rate: quoted_total / labor_hours_total ($/hr)
price_per_sqft      : quoted_total / sqft_final ($/sqft)
cost_per_sqft       : total_cost / sqft_final ($/sqft)
complexity_score    : Total number of all line items

FLAGS
-----
has_materials       : Boolean - quote includes materials
has_labor           : Boolean - quote includes labor
has_subs            : Boolean - quote includes subcontractors
anomaly_flags       : Pipe-separated list of detected issues
is_valid_for_analysis: Boolean - passes quality filters

DESCRIPTIONS (for text mining)
------------------------------
job_description     : Primary job description text
material_descriptions: Concatenated material descriptions (first 5)
sub_descriptions    : Concatenated subcontractor descriptions (first 3)

================================================================================
ANOMALY FLAGS EXPLAINED
================================================================================
NEGATIVE_TOTAL      : Quote total is negative
VERY_HIGH_TOTAL     : Quote total > $500,000
ZERO_TOTAL          : Quote total is $0
NEGATIVE_MARGIN     : Overall margin is negative
VERY_HIGH_MARGIN    : Overall margin > 70%
VERY_LOW_MARGIN     : Overall margin < 10%
NO_MATERIALS        : No materials in quote
NO_LABOR            : No labor hours in quote
UNUSUAL_MATERIAL_RATIO: Materials > 90% of total
UNUSUAL_LABOR_RATIO : Labor > 90% of total

================================================================================
JOB CATEGORIES
================================================================================
Élastomère          : Elastomeric membrane roofing (flat roofs)
Bardeaux            : Asphalt shingle roofing (sloped roofs)
Service Call        : Repairs, inspections, small jobs
Ferblanterie        : Metal work, flashing, soffits
Skylights           : Skylight installation/repair
Heat Cables         : Heating cable installation
Gutters             : Gutter work
Ventilation         : Roof ventilation systems
Insulation          : Insulation work
Inspection          : Roof inspections/evaluations
Other               : Uncategorized jobs

================================================================================
SOURCE TABLES FROM C-CUBE
================================================================================
Quotes Data Export_clean.csv  → Main quote records
Quote Materials_clean.csv     → Material line items
Quote Lines_clean.csv         → Job type/description line items
Quote Time Lines_clean.csv    → Labor/time line items
Quote Sub Lines_clean.csv     → Subcontractor line items

================================================================================
"""

with open(f"{OUTPUT_PATH}data_dictionary.txt", 'w') as f:
    f.write(data_dict)
print(f"  ✓ Saved: data_dictionary.txt")

# -----------------------------------------------------------------------------
# COMPLETE
# -----------------------------------------------------------------------------
print("\n" + "="*80)
print(" ✅ MASTER DATA PIPELINE COMPLETE")
print("="*80)
print(f"""
Files Generated:
  • master_quotes.csv          - Full dataset ({len(master):,} rows)
  • master_quotes_valid.csv    - Analysis-ready subset ({len(valid):,} rows)
  • data_dictionary.txt        - Field documentation

Location: {OUTPUT_PATH}

Next Steps:
  1. Run comprehensive_analysis.py for full analysis
  2. Run materials_deep_analysis.py for material inflation
  3. Review anomaly flags and clean if needed
  4. Build pricing algorithm on master_quotes_valid.csv
""")
