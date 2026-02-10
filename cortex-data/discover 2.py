#!/usr/bin/env python3
import os
import pandas as pd

FILES = [
    ('Quotes Data Export.csv', 37),      # 36 fields + 1 header row
    ('Quote Materials.csv', 18),          # adjust after first run if wrong
    ('Quote Lines.csv', 20),
    ('Quote Time Lines.csv', 16),
    ('Quote Sub Lines.csv', 14),
    ('Quote Companies.csv', 8),
]

def parse_transposed(filepath, rows_per_block):
    print(f"  Reading...")
    try:
        df = pd.read_csv(filepath, encoding='utf-8', header=None, low_memory=False)
    except:
        df = pd.read_csv(filepath, encoding='latin-1', header=None, low_memory=False)
    
    print(f"  Raw: {df.shape[0]} rows x {df.shape[1]} cols")
    
    # Get field names from first block (column A, skip row 0 which is "Column")
    field_names = df.iloc[1:rows_per_block, 0].tolist()
    print(f"  Fields: {len(field_names)}")
    
    all_records = []
    num_blocks = df.shape[0] // rows_per_block
    
    for block in range(num_blocks):
        start_row = block * rows_per_block
        
        # Each value column (skip column A which has field names)
        for col in range(1, df.shape[1]):
            record = {}
            for i, field in enumerate(field_names):
                val = df.iloc[start_row + 1 + i, col]
                record[str(field).strip()] = val
            
            # Skip empty records
            if record.get('id') and pd.notna(record.get('id')):
                all_records.append(record)
        
        if (block + 1) % 25 == 0:
            print(f"    Block {block + 1}/{num_blocks}, {len(all_records):,} records...")
    
    result = pd.DataFrame(all_records)
    print(f"  ✓ Extracted: {len(result):,} records")
    return result

def analyze(df, name):
    print(f"\n{'='*60}")
    print(f" {name}: {len(df):,} RECORDS")
    print(f"{'='*60}")
    
    for col in list(df.columns)[:20]:
        series = df[col]
        nulls = series.isna().sum() + (series == '').sum()
        null_pct = round(nulls / len(series) * 100, 1)
        
        non_null = series.dropna()
        non_null = non_null[non_null != '']
        
        if len(non_null) == 0:
            print(f"  {col}: [EMPTY]")
            continue
        
        # Try numeric
        nums = pd.to_numeric(non_null, errors='coerce').dropna()
        if len(nums) > len(non_null) * 0.5:
            print(f"  {col}: {nums.min():,.2f} to {nums.max():,.2f} | avg {nums.mean():,.2f} | {null_pct}% null")
        else:
            samples = [str(v)[:35] for v in non_null.head(2)]
            print(f"  {col}: {samples} | {null_pct}% null")

def main():
    print("\n" + "="*60)
    print(" C-CUBE DISCOVERY v3")
    print("="*60)
    
    folder = os.path.dirname(os.path.abspath(__file__))
    
    for fname, rows_per_block in FILES:
        path = os.path.join(folder, fname)
        if not os.path.exists(path):
            print(f"\n⚠️  Not found: {fname}")
            continue
        
        size = os.path.getsize(path) / (1024*1024)
        print(f"\n📄 {fname} ({size:.1f} MB)")
        
        df = parse_transposed(path, rows_per_block)
        analyze(df, fname)
        
        # Save clean CSV
        clean = fname.replace('.csv', '_clean.csv')
        df.to_csv(os.path.join(folder, clean), index=False)
        print(f"  💾 Saved: {clean}")

if __name__ == '__main__':
    main()
