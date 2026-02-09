# Phase 20: Materials Database & Import - Research

**Researched:** February 9, 2026
**Domain:** Data migration, CSV import, database schema design, searchable UI components
**Confidence:** HIGH

## Summary

Phase 20 involves importing Laurent's 1,152-item materials CSV into Supabase PostgreSQL and building a searchable material selector UI to replace the manual "number of material lines" input. The CSV contains pricing data (COST/SELL), categories, supplier codes, and metadata. Current data quality analysis shows 813 complete items ready for import, with 259 items needing review due to missing categories (231 items) or prices (43 missing COST, 42 missing SELL). The existing material prediction system uses numeric material_ids (1-824) from CCube training data, requiring careful mapping between Laurent's new materials database and the ML model's existing IDs.

**Data Quality Summary:**
- Total items: 1,152 rows (1,072 data rows + 1 header)
- Complete items (NAME+COST+SELL+UNIT+CATEGORY): 813 (76%)
- Flagged for review: 259 (24%)
- Labor items incorrectly categorized as materials: 37 items
- Duplicate names: 4 items

**Primary recommendation:** Use Supabase Dashboard CSV import for initial load (handles up to 5,000 rows efficiently), implement a two-phase import strategy (clean items first, flagged items for manual review), build shadcn/ui Combobox for material selector with multi-select capability, and use RapidFuzz library for deduplication/similarity detection to map new materials to existing ML model IDs.

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Supabase | 2.27.0+ | PostgreSQL database, CSV import | Already integrated for feedback system, service role key configured |
| pandas | Latest | CSV parsing, data cleaning, validation | Industry standard for data manipulation in Python |
| RapidFuzz | Latest | Fuzzy string matching, deduplication | Fastest fuzzy matching library (C++ backend), successor to FuzzyWuzzy |
| shadcn/ui Combobox | v4 | Searchable dropdown UI | Official shadcn component, built on Radix Popover + Command |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| Pydantic | 2.x | Data validation for import script | Validate CSV data before DB insert |
| PostgreSQL COPY | Native | Bulk data import | Not available on Supabase (requires superuser), use Dashboard import instead |
| dedupe | Latest | ML-based deduplication | Only if RapidFuzz + manual review insufficient |
| react-hook-form | Already in use | Form state management | Material selector form integration |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Supabase Dashboard CSV import | Python psycopg2 bulk insert | Dashboard is simpler, handles JSON conversion automatically, psycopg2 requires custom error handling |
| RapidFuzz | TheFuzz (FuzzyWuzzy) | RapidFuzz is 2-10x faster due to C++ implementation |
| shadcn Combobox | Custom autocomplete | Combobox has keyboard nav, accessibility, WAI-ARIA built-in |
| Direct CSV import | Pandas cleaning + validation | Direct import risks data quality issues, cleaning ensures integrity |

**Installation:**
```bash
# Backend (Python)
pip install pandas rapidfuzz pydantic

# Frontend (already installed)
# shadcn/ui combobox uses existing dependencies
```

## Architecture Patterns

### Recommended Project Structure
```
backend/
├── app/
│   ├── models/
│   │   └── material_prices.json          # Existing 824 material IDs
│   ├── scripts/                          # NEW
│   │   ├── import_materials.py          # CSV import script
│   │   ├── map_materials_to_ml.py       # Map new IDs to ML IDs
│   │   └── detect_duplicates.py         # Fuzzy matching script
│   ├── routers/
│   │   └── materials.py                 # NEW: Material search endpoints
│   └── schemas/
│       └── materials.py                 # Existing, extend for DB models
frontend/
├── src/
│   ├── components/estimateur/
│   │   ├── material-selector.tsx        # NEW: Combobox component
│   │   └── materials-form.tsx           # Existing, update to use selector
│   └── lib/
│       └── api/materials.ts             # NEW: Material search API calls
cortex-data/
└── LV Material List.csv                 # Source data (1,152 rows)
```

### Pattern 1: Two-Phase Import Strategy
**What:** Import clean items first (813), flag problematic items (259) for manual review
**When to use:** When source data has known quality issues
**Example:**
```python
import pandas as pd
from typing import List, Tuple

def analyze_csv(csv_path: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Separate clean items from flagged items."""
    df = pd.read_csv(csv_path)

    # Clean items: have NAME, COST, SELL, UNIT, CATEGORY
    clean_mask = (
        df['NAME'].notna() & (df['NAME'] != '') &
        df['COST'].notna() & (df['COST'] != '') &
        df['SELL'].notna() & (df['SELL'] != '') &
        df['UNIT'].notna() & (df['UNIT'] != '') &
        df['CATEGORY'].notna() & (df['CATEGORY'] != '')
    )

    # Filter out labor items (not materials)
    labor_mask = df['CATEGORY'].isin(['Main d\'oeuvre', 'Sous-traitant pose'])

    clean_df = df[clean_mask & ~labor_mask]
    flagged_df = df[~clean_mask | labor_mask]

    return clean_df, flagged_df

# Source: Pandas data cleaning best practices
# https://www.kdnuggets.com/data-cleaning-with-pandas
```

### Pattern 2: Fuzzy Matching for Deduplication
**What:** Use RapidFuzz to detect similar material names, flag for manual review
**When to use:** Identifying potential duplicates with slight name variations
**Example:**
```python
from rapidfuzz import fuzz, process

def find_similar_materials(materials: List[str], threshold: int = 85) -> List[Tuple[str, str, int]]:
    """Find materials with similar names above threshold similarity."""
    duplicates = []

    for i, mat1 in enumerate(materials):
        # Compare against remaining items
        for mat2 in materials[i+1:]:
            similarity = fuzz.ratio(mat1, mat2)
            if similarity >= threshold:
                duplicates.append((mat1, mat2, similarity))

    return duplicates

# Example: "2025 - Bardeaux GAF Timberland" vs "Bardeaux GAF Timberland HD"
# Would return similarity score ~85-90

# Source: RapidFuzz documentation
# https://github.com/maxbachmann/RapidFuzz
```

### Pattern 3: Supabase Material Schema Design
**What:** Normalized schema with proper constraints and indexes
**When to use:** All material database implementations
**Example:**
```sql
-- Create materials table
CREATE TABLE materials (
    id BIGSERIAL PRIMARY KEY,
    code VARCHAR(100),                    -- Supplier code (e.g., "E400-BCN-MUREU35818")
    name TEXT NOT NULL,                   -- Material name
    cost DECIMAL(10, 2),                  -- Supplier cost (nullable for items under review)
    sell_price DECIMAL(10, 2),            -- Selling price (nullable for items under review)
    unit VARCHAR(50) NOT NULL,            -- Unit of measure (Unités, Rouleaux, etc.)
    category VARCHAR(100),                -- Category (nullable, 231 items missing)
    supplier VARCHAR(200),                -- Supplier name
    note TEXT,                            -- Additional notes
    area_sqft DECIMAL(10, 2),            -- Surface area in sqft (from "S en pi2")
    length_ft DECIMAL(10, 2),            -- Length in feet
    width_ft DECIMAL(10, 2),             -- Width in feet
    thickness_ft DECIMAL(10, 2),         -- Thickness in feet
    ml_material_id INTEGER,              -- Link to ML model material_id (nullable)
    review_status VARCHAR(20) DEFAULT 'approved', -- 'approved', 'flagged', 'duplicate'
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_materials_category ON materials(category);
CREATE INDEX idx_materials_name_trgm ON materials USING gin(name gin_trgm_ops); -- Full-text search
CREATE INDEX idx_materials_code ON materials(code) WHERE code IS NOT NULL;
CREATE INDEX idx_materials_ml_id ON materials(ml_material_id) WHERE ml_material_id IS NOT NULL;

-- Enable pg_trgm extension for fuzzy text search
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Source: PostgreSQL inventory best practices
-- https://www.linkedin.com/pulse/building-inventory-database-postgresql-ensuring-data-quality-torres
```

### Pattern 4: shadcn/ui Combobox for Material Selector
**What:** Searchable, keyboard-navigable material picker with multi-select
**When to use:** Replacing manual "material_lines" input with actual material selection
**Example:**
```typescript
"use client"

import * as React from "react"
import { Check, ChevronsUpDown } from "lucide-react"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
} from "@/components/ui/command"
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover"

interface Material {
  id: number
  name: string
  category: string
  sell_price: number
}

export function MaterialSelector({
  onSelect,
  materials,
}: {
  onSelect: (materials: Material[]) => void
  materials: Material[]
}) {
  const [open, setOpen] = React.useState(false)
  const [selected, setSelected] = React.useState<Material[]>([])

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <Button
          variant="outline"
          role="combobox"
          aria-expanded={open}
          className="w-full justify-between"
        >
          {selected.length > 0
            ? `${selected.length} matériaux sélectionnés`
            : "Sélectionner des matériaux..."}
          <ChevronsUpDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-[400px] p-0">
        <Command>
          <CommandInput placeholder="Rechercher un matériau..." />
          <CommandEmpty>Aucun matériau trouvé.</CommandEmpty>
          <CommandGroup className="max-h-64 overflow-auto">
            {materials.map((material) => (
              <CommandItem
                key={material.id}
                value={material.name}
                onSelect={() => {
                  const isSelected = selected.some(m => m.id === material.id)
                  const newSelected = isSelected
                    ? selected.filter(m => m.id !== material.id)
                    : [...selected, material]
                  setSelected(newSelected)
                  onSelect(newSelected)
                }}
              >
                <Check
                  className={cn(
                    "mr-2 h-4 w-4",
                    selected.some(m => m.id === material.id) ? "opacity-100" : "opacity-0"
                  )}
                />
                <div className="flex flex-col">
                  <span>{material.name}</span>
                  <span className="text-xs text-muted-foreground">
                    {material.category} • ${material.sell_price.toFixed(2)}
                  </span>
                </div>
              </CommandItem>
            ))}
          </CommandGroup>
        </Command>
      </PopoverContent>
    </Popover>
  )
}

// Source: shadcn/ui Combobox documentation
// https://ui.shadcn.com/docs/components/radix/combobox
```

### Anti-Patterns to Avoid
- **Importing without validation:** CSV may have encoding issues, price format inconsistencies, or malformed data. Always validate first.
- **Hardcoding material IDs:** ML model uses IDs 1-824 from CCube data. New materials need new IDs, don't overwrite existing.
- **Ignoring labor items:** 37 items in CSV are labor/subcontractor costs, not materials. Filter these out.
- **Direct COPY command:** Supabase doesn't allow COPY (superuser only). Use Dashboard import or INSERT batches.
- **Blocking import on duplicates:** 4 duplicate names exist. Flag for review, don't fail entire import.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Fuzzy string matching | Custom Levenshtein distance | RapidFuzz | Handles Unicode, optimized C++, 2-10x faster than Python implementations |
| CSV parsing edge cases | Custom CSV reader | pandas.read_csv() | Handles encoding detection, malformed rows, type inference, thousands of edge cases |
| Searchable dropdown | Custom autocomplete | shadcn/ui Combobox | Accessibility (WAI-ARIA), keyboard nav, focus management, screen reader support built-in |
| Bulk database inserts | Loop with individual INSERTs | Supabase Dashboard import or jsonb_populate_recordset | Dashboard handles batching, error reporting, rollback; manual loops are 100x slower |
| Data validation | Manual if/else checks | Pydantic models | Type coercion, nested validation, clear error messages, reusable schemas |

**Key insight:** Data migration and fuzzy matching are deceptively complex domains. CSV files have dozens of encoding issues (BOM markers, mixed line endings, escaped quotes). String similarity has many edge cases (Unicode normalization, case sensitivity, punctuation handling). Use battle-tested libraries that handle these problems.

## Common Pitfalls

### Pitfall 1: Encoding Issues in CSV Import
**What goes wrong:** CSV may have UTF-8 BOM, Latin-1 characters, or mixed encodings causing import failures
**Why it happens:** Excel exports can add BOM markers, French characters (é, à, ô) may use different encodings
**How to avoid:**
```python
# Let pandas auto-detect encoding
df = pd.read_csv('LV Material List.csv', encoding='utf-8-sig')  # Handles BOM
# Or explicitly detect
import chardet
with open('LV Material List.csv', 'rb') as f:
    result = chardet.detect(f.read())
    encoding = result['encoding']
df = pd.read_csv('LV Material List.csv', encoding=encoding)
```
**Warning signs:** UnicodeDecodeError, garbled French characters, missing rows

### Pitfall 2: Price Data Type Inconsistencies
**What goes wrong:** CSV has prices as strings ("$25.00"), empty strings, or mixed formats
**Why it happens:** Excel formatting, manual data entry, currency symbols
**How to avoid:**
```python
# Clean and convert prices
df['COST'] = pd.to_numeric(df['COST'].str.replace('$', '').str.replace(',', ''), errors='coerce')
df['SELL'] = pd.to_numeric(df['SELL'].str.replace('$', '').str.replace(',', ''), errors='coerce')
# Flag rows with invalid prices
df['price_valid'] = df['COST'].notna() & df['SELL'].notna()
```
**Warning signs:** TypeError on insert, NaN values in price columns, negative prices

### Pitfall 3: Material ID Mapping Breaks ML Model
**What goes wrong:** Importing materials with new IDs breaks existing material_predictor.py which expects IDs 1-824
**Why it happens:** ML model was trained on CCube data with specific material_ids, new database uses different IDs
**How to avoid:**
- Add `ml_material_id` column to map new DB IDs to ML model IDs
- For new materials not in ML model, leave `ml_material_id` NULL
- Update material_predictor.py to query by ml_material_id, not DB id
**Warning signs:** Material predictions return empty, quantity regressors throw KeyError, prices lookup fails

### Pitfall 4: Category Filter Breaks with NULL Values
**What goes wrong:** 231 items have empty CATEGORY, filtering/grouping queries fail
**Why it happens:** SQL WHERE category = 'X' excludes NULL values silently
**How to avoid:**
```sql
-- Incorrect: misses NULL categories
SELECT * FROM materials WHERE category = 'Bardeaux';

-- Correct: handle NULL explicitly
SELECT * FROM materials WHERE category = 'Bardeaux' OR category IS NULL;

-- Or filter out NULL in query
SELECT * FROM materials WHERE category IS NOT NULL AND category = 'Bardeaux';
```
**Warning signs:** Missing materials in selector dropdown, category counts don't match expectations

### Pitfall 5: Combobox Performance with 1,152 Items
**What goes wrong:** Rendering 1,152 items in dropdown causes lag, poor UX
**Why it happens:** React re-renders on every keystroke, DOM handles 1,152 elements
**How to avoid:**
- Implement virtual scrolling (react-window or @tanstack/react-virtual)
- Server-side search with debouncing (search API endpoint)
- Lazy load categories: show categories first, then materials on expand
```typescript
// Debounced search
const [searchTerm, setSearchTerm] = useState('')
const debouncedSearch = useDebounce(searchTerm, 300)

useEffect(() => {
  if (debouncedSearch.length >= 2) {
    fetch(`/api/materials/search?q=${debouncedSearch}&limit=50`)
      .then(res => res.json())
      .then(setMaterials)
  }
}, [debouncedSearch])
```
**Warning signs:** Dropdown opens slowly, typing is laggy, browser console warnings about performance

### Pitfall 6: Labor Items Treated as Materials
**What goes wrong:** 37 labor/subcontractor items appear in material selector, confusing users
**Why it happens:** CSV categorizes labor as "Main d'oeuvre" and "Sous-traitant pose" but they're in same file as materials
**How to avoid:**
```python
# Filter out labor during import
labor_categories = ["Main d'oeuvre", "Sous-traitant pose"]
materials_df = df[~df['CATEGORY'].isin(labor_categories)]
labor_df = df[df['CATEGORY'].isin(labor_categories)]

# Store labor separately or add type field
df['item_type'] = df['CATEGORY'].apply(
    lambda x: 'labor' if x in labor_categories else 'material'
)
```
**Warning signs:** "Frais de base - Appel de service" appears in material selector, cost estimates double-count labor

## Code Examples

Verified patterns from official sources:

### Example 1: Supabase Dashboard CSV Import
```typescript
// Supabase Dashboard automatically handles CSV import via UI:
// 1. Navigate to Table Editor
// 2. Click "Insert" → "Import Data from CSV"
// 3. Upload file, map columns, set data types
// 4. Preview and confirm

// For programmatic import (backend script):
import { createClient } from '@supabase/supabase-js'

const supabase = createClient(
  process.env.SUPABASE_URL!,
  process.env.SUPABASE_SERVICE_ROLE_KEY!
)

async function importMaterials(materials: any[]) {
  // Batch insert (max 1000 rows per request)
  const batchSize = 1000
  for (let i = 0; i < materials.length; i += batchSize) {
    const batch = materials.slice(i, i + batchSize)
    const { data, error } = await supabase
      .from('materials')
      .insert(batch)

    if (error) {
      console.error(`Batch ${i / batchSize + 1} failed:`, error)
    } else {
      console.log(`Imported ${batch.length} materials`)
    }
  }
}

// Source: Supabase import documentation
// https://supabase.com/docs/guides/database/import-data
```

### Example 2: Material Search API Endpoint
```python
from fastapi import APIRouter, Query
from app.services.supabase_client import get_supabase
from typing import List, Optional

router = APIRouter()

@router.get("/materials/search")
async def search_materials(
    q: str = Query(..., min_length=2, description="Search query"),
    category: Optional[str] = None,
    limit: int = Query(50, le=200)
):
    """Search materials by name with optional category filter."""
    supabase = get_supabase()

    if not supabase:
        return {"error": "Database not configured"}

    # Use pg_trgm for fuzzy text search
    query = supabase.from_('materials').select('*')

    # Fuzzy name search (requires pg_trgm extension and GIN index)
    query = query.ilike('name', f'%{q}%')

    if category:
        query = query.eq('category', category)

    # Only approved materials
    query = query.eq('review_status', 'approved')

    # Order by relevance, limit results
    result = query.order('name').limit(limit).execute()

    return {"materials": result.data, "count": len(result.data)}

# Source: Supabase Python client documentation
# https://supabase.com/docs/reference/python/introduction
```

### Example 3: Pandas Data Cleaning Pipeline
```python
import pandas as pd
from typing import Dict, List

def clean_materials_csv(csv_path: str) -> Dict[str, pd.DataFrame]:
    """Clean and validate materials CSV, return clean and flagged items."""

    # Read with BOM handling
    df = pd.read_csv(csv_path, encoding='utf-8-sig')

    # Strip whitespace from all string columns
    str_cols = df.select_dtypes(include=['object']).columns
    df[str_cols] = df[str_cols].apply(lambda x: x.str.strip())

    # Clean price columns
    for col in ['COST', 'SELL']:
        df[col] = pd.to_numeric(
            df[col].str.replace(r'[$,]', '', regex=True),
            errors='coerce'
        )

    # Clean numeric metadata columns
    numeric_cols = ['S en pi2', 'Long en pi', 'Larg en pi', 'Ep en pi']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    # Detect duplicates
    df['is_duplicate'] = df.duplicated(subset=['NAME'], keep='first')

    # Classify items
    labor_categories = ["Main d'oeuvre", "Sous-traitant pose"]
    df['item_type'] = df['CATEGORY'].apply(
        lambda x: 'labor' if x in labor_categories else 'material'
    )

    # Validation flags
    df['has_name'] = df['NAME'].notna() & (df['NAME'] != '')
    df['has_cost'] = df['COST'].notna()
    df['has_sell'] = df['SELL'].notna()
    df['has_category'] = df['CATEGORY'].notna() & (df['CATEGORY'] != '')
    df['has_unit'] = df['UNIT'].notna() & (df['UNIT'] != '')

    df['is_complete'] = (
        df['has_name'] &
        df['has_cost'] &
        df['has_sell'] &
        df['has_category'] &
        df['has_unit']
    )

    # Split into clean and flagged
    clean_materials = df[
        df['is_complete'] &
        ~df['is_duplicate'] &
        (df['item_type'] == 'material')
    ]

    flagged_items = df[
        ~df['is_complete'] |
        df['is_duplicate'] |
        (df['item_type'] == 'labor')
    ]

    return {
        'clean': clean_materials,
        'flagged': flagged_items,
        'labor': df[df['item_type'] == 'labor'],
        'duplicates': df[df['is_duplicate']],
        'stats': {
            'total': len(df),
            'clean': len(clean_materials),
            'flagged': len(flagged_items),
            'duplicates': df['is_duplicate'].sum(),
            'labor_items': (df['item_type'] == 'labor').sum()
        }
    }

# Source: Pandas data cleaning best practices
# https://www.kdnuggets.com/creating-automated-data-cleaning-pipelines-using-python-and-pandas
```

### Example 4: RapidFuzz Deduplication
```python
from rapidfuzz import fuzz, process
from typing import List, Tuple
import pandas as pd

def detect_similar_materials(
    materials: pd.DataFrame,
    threshold: int = 85
) -> List[Tuple[int, int, str, str, int]]:
    """Find materials with similar names using fuzzy matching.

    Returns list of (id1, id2, name1, name2, similarity_score).
    """
    results = []
    names = materials['NAME'].tolist()
    ids = materials.index.tolist()

    for i, (idx1, name1) in enumerate(zip(ids, names)):
        # Compare against remaining items
        for idx2, name2 in zip(ids[i+1:], names[i+1:]):
            # Use token_sort_ratio to ignore word order
            similarity = fuzz.token_sort_ratio(name1, name2)

            if similarity >= threshold:
                results.append((idx1, idx2, name1, name2, similarity))

    return results

# Example usage:
# df = pd.read_csv('materials.csv')
# similar = detect_similar_materials(df, threshold=85)
# for id1, id2, name1, name2, score in similar:
#     print(f"{score}% - {name1} ≈ {name2}")

# Source: RapidFuzz documentation
# https://github.com/maxbachmann/RapidFuzz
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Manual "material_lines" input | Searchable material selector with actual items | Phase 20 (Feb 2026) | Users pick specific materials instead of guessing line count |
| FuzzyWuzzy for string matching | RapidFuzz | 2021-2022 | 2-10x performance improvement, better Unicode handling |
| PostgreSQL COPY for bulk import | Supabase Dashboard import or jsonb_populate_recordset | N/A (Supabase limitation) | COPY requires superuser privileges not available in Supabase |
| Material prediction by numeric ID only | Database lookup by ml_material_id mapping | Phase 20 (Feb 2026) | Decouples UI display from ML model internals |
| Single-phase CSV import | Two-phase import (clean + flagged) | Best practice 2024+ | Better data quality, manual review for edge cases |

**Deprecated/outdated:**
- **TheFuzz (FuzzyWuzzy):** Replaced by RapidFuzz due to licensing issues and performance. Use RapidFuzz.
- **pandas.DataFrame.append():** Deprecated in pandas 1.4.0, use pd.concat() instead.
- **Direct SQL string formatting:** Use parameterized queries to prevent SQL injection, especially with user-provided search terms.

## Open Questions

1. **ML Material ID Mapping Strategy**
   - What we know: ML model uses material_ids 1-824 from CCube training data, material_prices.json has 824 entries
   - What's unclear: How to map Laurent's 1,152 materials to the 824 ML IDs? Some materials won't have ML predictions.
   - Recommendation: Add ml_material_id column (nullable), manually map common materials (bardeaux, membrane, etc.) to ML IDs, leave new/rare materials as NULL (they'll use fallback pricing)

2. **Custom Material Entry Flow**
   - What we know: Phase 20 requires "Add custom material" option for items not in database
   - What's unclear: Should custom materials be saved to database for future use? User-specific or global?
   - Recommendation: Two-tier system: (1) Session-only custom materials for one-off items, (2) "Request to add material" button that creates a flagged entry for admin review

3. **Material Count Calculation**
   - What we know: Current system has manual "material_lines" input, new system has material selector
   - What's unclear: How does system auto-count lines when user picks materials? One line per material, or grouped by category?
   - Recommendation: material_lines = count of distinct materials selected, labor_lines calculated separately from labor items table

4. **Search Performance at Scale**
   - What we know: 1,152 items in dropdown, users will type to search
   - What's unclear: Should search be client-side or server-side? How many results to show?
   - Recommendation: Server-side search with debouncing (300ms), pg_trgm GIN index for fast ILIKE queries, limit 50 results, show category counts to help users narrow down

5. **Duplicate Resolution Process**
   - What we know: 4 duplicate names detected, fuzzy matching will find more near-duplicates
   - What's unclear: Who reviews and merges duplicates? Amin, Laurent, or automated?
   - Recommendation: Flag duplicates in database (review_status='duplicate'), export CSV for Amin/Laurent to review, provide merge script to consolidate chosen duplicates

## Sources

### Primary (HIGH confidence)
- [Supabase Import Data Documentation](https://supabase.com/docs/guides/database/import-data) - CSV import methods, Dashboard usage
- [Supabase Python Client Documentation](https://supabase.com/docs/reference/python/introduction) - Batch insert patterns
- [shadcn/ui Combobox Documentation](https://ui.shadcn.com/docs/components/radix/combobox) - Searchable dropdown component
- [RapidFuzz GitHub Repository](https://github.com/maxbachmann/RapidFuzz) - Fuzzy string matching library

### Secondary (MEDIUM confidence)
- [Pandas Data Cleaning with KDnuggets](https://www.kdnuggets.com/data-cleaning-with-pandas) - CSV cleaning best practices
- [PostgreSQL Inventory Database Best Practices](https://www.linkedin.com/pulse/building-inventory-database-postgresql-ensuring-data-quality-torres) - Schema design patterns
- [Fuzzy Matching Tools for 2026](https://matchdatapro.com/top-5-fuzzy-matching-tools-for-2026/) - RapidFuzz vs alternatives
- [Building Multi-Select Dropdown in Next.js with ShadCN UI](https://medium.com/@codeaprogram/building-a-custom-multi-select-dropdown-in-next-js-with-shadcn-ui-b4574089df27) - Multi-select patterns

### Tertiary (LOW confidence)
- Medium articles on CSV import workflows - Useful examples but not authoritative
- GitHub discussions on Supabase bulk import - Community workarounds, not official recommendations

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - All libraries already in use or standard for domain (Supabase, pandas, RapidFuzz, shadcn)
- Architecture: HIGH - Patterns verified in official docs (Supabase CSV import, Combobox, pandas cleaning)
- Pitfalls: MEDIUM - Based on common CSV import issues and database design best practices, not project-specific testing
- Material ID mapping: MEDIUM - Requires investigation of existing ML model structure and CCube data

**Research date:** February 9, 2026
**Valid until:** March 11, 2026 (30 days - stable domain)

**Critical data findings:**
- Actual CSV has 1,152 rows (not 672 as roadmap stated)
- 813 complete items (76%), 259 flagged for review (24%)
- 37 labor items need filtering (categories: "Main d'oeuvre", "Sous-traitant pose")
- 4 duplicate names, fuzzy matching will find more near-duplicates
- Existing ML model uses 824 material_ids, requires mapping strategy
- 231 items missing CATEGORY field
- 288 items have supplier CODE field populated
