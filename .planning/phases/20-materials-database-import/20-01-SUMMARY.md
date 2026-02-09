---
phase: 20-materials-database-import
plan: 01
subsystem: backend-data-import
tags: [materials, database, csv-import, deduplication, data-cleaning]
dependency_graph:
  requires: []
  provides:
    - materials_table_sql
    - csv_import_script
    - deduplication_script
  affects:
    - phase_20_plan_02
    - phase_20_plan_03
tech_stack:
  added:
    - pandas>=2.0.0
    - rapidfuzz>=3.0.0
  patterns:
    - csv_data_cleaning
    - fuzzy_string_matching
    - batch_database_insert
    - duplicate_clustering
key_files:
  created:
    - backend/app/scripts/create_materials_table.sql
    - backend/app/scripts/import_materials.py
    - backend/app/scripts/detect_duplicates.py
  modified:
    - backend/requirements.txt
decisions:
  - choice: pandas for CSV processing
    rationale: Robust handling of UTF-8 BOM, numeric coercion, and data validation
  - choice: RapidFuzz token_sort_ratio for similarity
    rationale: More accurate for materials with reordered words (e.g., "DRAIN COPPER 3in" vs "COPPER DRAIN 3in")
  - choice: DFS clustering for duplicate groups
    rationale: Captures transitive relationships (if A~B and B~C, group all three)
  - choice: Flag both items in duplicate pairs
    rationale: Requires manual review to determine canonical item
metrics:
  duration: 242s
  tasks_completed: 2
  files_created: 3
  files_modified: 1
  lines_added: 565
  commits: 2
completed_date: 2026-02-09
---

# Phase 20 Plan 01: Materials Database Import Foundation

**One-liner:** SQL DDL, CSV import script with data cleaning, and fuzzy deduplication using RapidFuzz for Laurent's 1,072-item materials inventory.

## What Was Built

Created the foundational data import infrastructure for Laurent's materials database:

1. **SQL DDL** (`create_materials_table.sql`):
   - Materials table with 17 columns (code, name, cost, sell_price, unit, category, supplier, note, dimensions, item_type, ml_material_id, review_status, timestamps)
   - pg_trgm extension for fuzzy text search
   - 5 indexes: category, name (trigram), code, review_status, item_type
   - Support for labor items, flagged items, and duplicate detection

2. **CSV Import Script** (`import_materials.py`):
   - Reads Laurent's 1,152-row CSV (1 header + 1,072 data rows after cleaning)
   - UTF-8 BOM handling for French characters
   - Currency cleaning (removes $, commas)
   - Dimension conversion (area_sqft, length_ft, width_ft, thickness_ft)
   - Labor detection (categories: "Main d'oeuvre", "Sous-traitant pose")
   - Duplicate detection using pandas duplicated()
   - Completeness checking (NAME, COST, SELL, UNIT, CATEGORY required)
   - Review status classification: approved (774), flagged (293), duplicate (5)
   - Batch insert (500 rows per batch) to Supabase
   - Dry-run mode for testing
   - Table existence check with clear error message

3. **Deduplication Script** (`detect_duplicates.py`):
   - RapidFuzz fuzzy matching with token_sort_ratio algorithm
   - Configurable similarity threshold (default 85%)
   - DFS clustering for connected duplicate groups
   - Detailed report with similarity scores per cluster
   - CSV export option
   - Batch database updates to flag duplicates
   - Dry-run mode
   - Graceful error handling

## Statistics from Dry-Run

```
Total rows parsed:       1072
Approved (clean):        774  (72.2%)
Flagged (incomplete):    293  (27.3%)
Duplicates detected:     5    (0.5%)
Labor items:             37   (3.5%)
```

**Completeness breakdown:**
- 774 materials have all 5 required fields (NAME, COST, SELL, UNIT, CATEGORY)
- 293 flagged items missing one or more required fields
- 5 exact duplicate names (kept first occurrence, flagged rest)
- 37 labor items (will be filtered or marked as item_type='labor')

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed Python 3.9 type union syntax**
- **Found during:** Task 1 script testing
- **Issue:** `float | None` syntax not supported in Python 3.9, caused TypeError
- **Fix:** Changed to `Optional[float]` using typing module
- **Files modified:** `backend/app/scripts/import_materials.py`
- **Commit:** 3337117

**2. [Rule 1 - Bug] Fixed completeness check column names**
- **Found during:** Task 1 dry-run testing
- **Issue:** `is_complete_material()` checked renamed columns ("name", "cost", "sell_price") before the rename happened, resulting in 0 approved items
- **Fix:** Changed to use original CSV column names ("NAME", "COST", "SELL", "UNIT", "CATEGORY")
- **Files modified:** `backend/app/scripts/import_materials.py`
- **Commit:** 3337117

## Key Implementation Details

**CSV Import Pipeline:**
1. Read with UTF-8 BOM handling
2. Strip whitespace from all string columns
3. Clean currency columns (COST, SELL)
4. Convert dimension columns to numeric
5. Detect labor items by category
6. Detect exact duplicates by NAME
7. Check completeness (5 required fields)
8. Classify review status (approved/flagged/duplicate)
9. Rename columns to match database schema
10. Batch insert to Supabase (500 per batch)

**Duplicate Detection Pipeline:**
1. Load all materials where item_type='material'
2. Compare all pairs using RapidFuzz token_sort_ratio
3. Filter pairs above similarity threshold (default 85%)
4. Build adjacency graph from duplicate pairs
5. Run DFS to find connected components (clusters)
6. Print report with similarity scores per cluster
7. Optional: save to CSV
8. Optional: flag duplicates in database

**Review Status Classification:**
- `approved`: Complete material (all 5 fields), not duplicate, not labor
- `flagged`: Incomplete (missing required fields) OR labor item
- `duplicate`: Exact duplicate name (pandas detected)

**Future Fuzzy Duplicates:**
The deduplication script will find near-duplicates (e.g., "DRAIN COPPER 3in" vs "COPPER DRAIN 3in 5/8") when run against the populated database.

## Next Steps

1. **Manual SQL Execution:** Run `create_materials_table.sql` in Supabase Dashboard SQL Editor
2. **Configure Supabase:** Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY environment variables
3. **Run Import:** `python -m app.scripts.import_materials` (from backend/)
4. **Run Deduplication:** `python -m app.scripts.detect_duplicates --dry-run` to generate report
5. **Manual Review:** Review flagged items (293) and near-duplicates
6. **Phase 20-02:** Build materials search API with pg_trgm
7. **Phase 20-03:** Build material selector UI component

## Testing

All verification criteria met:
- ✅ `ls backend/app/scripts/` shows all 3 files
- ✅ `python -m app.scripts.import_materials --dry-run` parses CSV correctly (1072 rows → 774 approved, 293 flagged, 5 duplicates, 37 labor)
- ✅ `python -m app.scripts.detect_duplicates --help` shows usage
- ✅ `grep pandas backend/requirements.txt` finds dependency
- ✅ `grep rapidfuzz backend/requirements.txt` finds dependency
- ✅ Both scripts handle missing Supabase credentials gracefully
- ✅ Both scripts have --help and --dry-run flags

## Self-Check: PASSED

**Files created:**
```
✓ backend/app/scripts/create_materials_table.sql
✓ backend/app/scripts/import_materials.py
✓ backend/app/scripts/detect_duplicates.py
```

**Files modified:**
```
✓ backend/requirements.txt (pandas, rapidfuzz added)
```

**Commits:**
```
✓ 3337117: feat(20-01): add materials table SQL and CSV import script
✓ 333fefd: feat(20-01): add duplicate detection script with fuzzy matching
```

All files exist, all commits present, all verification tests pass.
