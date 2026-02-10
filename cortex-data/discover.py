#!/usr/bin/env python3
import os
import pandas as pd

FILES = [
    'Quotes Data Export.csv',
    'Quote Materials.csv', 
    'Quote Lines.csv',
    'Quote Time Lines.csv',
    'Quote Sub Lines.csv',
    'Quote Companies.csv',
]

def parse_transposed(filepath):
    print(f"  Reading...")
    try:
        df = pd.read_csv(filepath, encoding='utf-8', header=None, low_memory=False)
    except:
        df = pd.read_csv(filepath, encoding='latin-1', header=None, low_memory=False)
    
    print(f"  Raw: {df.shape[0]} rows x {df.shape[1]} cols")
    
    # Auto-detect: find all rows where column A = "Column"
    col_a = df.iloc[:, 0].astype(str).str.strip().str.lower()
    block_starts = df[col_a == 'column'].index.tolist()
    
    if len(block_starts) < 2:
        print(f"  ⚠️ Could not detect block structure")
        return None
    
    rows_per_block = block_starts[1] - block_starts[0]
    print(f"  Detected: {len(block_starts)} blocks, {rows_per_block} rows each")
    
    # Field names from first block (row 1 to row N, column A)
    field_names = df.iloc[block_starts[0]+1 : block_starts[0]+rows_per_block, 0].tolist()
    field_names = [str(f).strip() for f in field_names]
    print(f"  Fields: {len(field_names)}")
    
    all_records = []
    
    for block_idx, start_row in enumerate(block_starts):
        # Each value column (skip column A)
        for col in range(1, df.shape[1]):
            record = {}
            for i, field in enumerate(field_names):
                if field and field.lower() != 'column':
                    val = df.iloc[start_row + 1 + i, col]
                    record[field] = val
            
            # Only add if has valid ID
            id_val = record.get('id')
            if id_val is not None and pd.notna(id_val) and str(id_val).strip():
                all_records.append(record)
        
        if (block_idx + 1) % 25 == 0:
            print(f"    Block {block_idx + 1}/{len(block_starts)}, {len(all_records):,} records...")
    
    result = pd.DataFrame(all_records)
    print(f"  ✓ Extracted: {len(result):,} records")
    return result

def analyze(df, name):
    print(f"\n{'='*60}")
    print(f" {name}: {len(df):,} RECORDS")
    print(f"{'='*60}")
    
    for col in list(df.columns)[:18]:
        series = df[col]
        nulls = series.isna().sum() + (series.astype(str) == '').sum()
        null_pct = round(nulls / len(series) * 100, 1) if len(series) > 0 else 0
        
        non_null = series.dropna()
        non_null = non_null[non_null.astype(str) != '']
        
        if len(non_null) == 0:
            print(f"  {col}: [EMPTY]")
            continue
        
        # Try numeric
        nums = pd.to_numeric(non_null, errors='coerce').dropna()
        if len(nums) > len(non_null) * 0.5:
            print(f"  {col}: {nums.min():,.2f} to {nums.max():,.2f} | avg {nums.mean():,.2f} | {null_pct}% null")
        else:
            samples = [str(v)[:40] for v in non_null.head(2)]
            print(f"  {col}: {samples} | {null_pct}% null")

def main():
    print("\n" + "="*60)
    print(" C-CUBE DISCOVERY v4 (auto-detect)")
    print("="*60)
    
    folder = os.path.dirname(os.path.abspath(__file__))
    
    for fname in FILES:
        path = os.path.join(folder, fname)
        if not os.path.exists(path):
            print(f"\n⚠️  Not found: {fname}")
            continue
        
        size = os.path.getsize(path) / (1024*1024)
        print(f"\n📄 {fname} ({size:.1f} MB)")
        
        df = parse_transposed(path)
        if df is not None and len(df) > 0:
            analyze(df, fname)
            
            clean = fname.replace('.csv', '_clean.csv')
            df.to_csv(os.path.join(folder, clean), index=False)
            print(f"  💾 Saved: {clean}")

if __name__ == '__main__':
    main()
