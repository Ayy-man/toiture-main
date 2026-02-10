#!/usr/bin/env python3
"""
TOITURELV - SQFT EXTRACTION FIX
Re-runs sqft extraction with French number parsing on existing master_quotes.csv
"""

import pandas as pd
import numpy as np
import re
import sys

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
    # French format: ends with comma + 1-2 digits (decimal)
    if re.match(r'^[\d\s]+,\d{1,2}$', num_str):
        # French: space=thousands, comma=decimal
        num_str = num_str.replace(' ', '').replace(',', '.')
    else:
        # Standard: just strip separators
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
    """Extract LxW dimensions"""
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

log("\n" + "="*60)
log(" SQFT EXTRACTION FIX (French Number Parsing)")
log("="*60)

# Load existing master file
log("\n[1/4] Loading master_quotes.csv...")
master = pd.read_csv(f"{DATA_PATH}master_quotes.csv")
log(f"      Loaded {len(master):,} rows")

# Check current sqft coverage
old_coverage = master['sqft_final'].notna().sum()
log(f"      Current sqft coverage: {old_coverage:,} ({old_coverage/len(master)*100:.1f}%)")

# Re-extract sqft with French number fix
log("\n[2/4] Re-extracting sqft with French number parsing...")

def get_sqft(row):
    # Try quoted_area first
    if pd.notna(row.get('quoted_area')) and row.get('quoted_area', 0) > 0:
        return row['quoted_area'], 'quoted_area'
    # Try text extraction
    for col, source in [('job_description', 'job_description'), 
                        ('material_descriptions', 'material_descriptions')]:
        if col in row and pd.notna(row.get(col)):
            sqft = extract_sqft(row[col])
            if sqft:
                return sqft, source
    return None, None

def get_sqft_from_dims(row):
    for col in ['job_description', 'material_descriptions']:
        if col in row and pd.notna(row.get(col)):
            l, w = extract_dimensions(row[col])
            if l and w:
                return l * w
    return None

# Apply extraction
sqft_results = master.apply(get_sqft, axis=1)
master['extracted_sqft_v4'] = [r[0] for r in sqft_results]
master['sqft_source_v4'] = [r[1] for r in sqft_results]
master['sqft_from_dims_v4'] = master.apply(get_sqft_from_dims, axis=1)
master['sqft_final_v4'] = master['extracted_sqft_v4'].fillna(master['sqft_from_dims_v4'])

# Replace old columns
master['extracted_sqft'] = master['extracted_sqft_v4']
master['sqft_source'] = master['sqft_source_v4']
master['sqft_final'] = master['sqft_final_v4']
master = master.drop(columns=['extracted_sqft_v4', 'sqft_source_v4', 'sqft_from_dims_v4'])

# Recalculate price_per_sqft
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

new_coverage = master['sqft_final'].notna().sum()
log(f"      New sqft coverage: {new_coverage:,} ({new_coverage/len(master)*100:.1f}%)")
log(f"      Improvement: +{new_coverage - old_coverage:,} records")

# Save
log("\n[3/4] Saving updated files...")
master.to_csv(f"{DATA_PATH}master_quotes.csv", index=False)
log("      ✓ master_quotes.csv")

valid = master[master['is_valid_for_analysis'] == True]
valid.to_csv(f"{DATA_PATH}master_quotes_valid.csv", index=False)
log(f"      ✓ master_quotes_valid.csv ({len(valid):,} rows)")

labor_reliable = master[(master['is_valid_for_analysis'] == True) & (master['labor_data_reliable'] == True)]
labor_reliable.to_csv(f"{DATA_PATH}master_quotes_labor_reliable.csv", index=False)
log(f"      ✓ master_quotes_labor_reliable.csv ({len(labor_reliable):,} rows)")

# Summary
log("\n[4/4] Results summary")
log("="*60)
valid_sqft = valid['sqft_final'].notna().sum()
log(f" Valid quotes with sqft: {valid_sqft:,} ({valid_sqft/len(valid)*100:.1f}%)")
log(f" Sqft range: {valid['sqft_final'].min():,.0f} - {valid['sqft_final'].max():,.0f}")
log(f" Median sqft: {valid['sqft_final'].median():,.0f}")
log("="*60)
log("\n✅ DONE\n")
