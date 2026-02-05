# 17-05 Summary: Similar Cases Quality Filter

**Status:** Complete (code ready, needs deployment)
**Completed:** 2026-02-05

## Problem

A 1500 sqft bardeaux query was returning five 138 sqft jobs as "similar cases". This made the similar cases section useless for comparison.

## Root Cause

Pinecone queries used only embedding similarity without filtering by square footage. A small job could match a large job if other features (category, complexity) were similar.

## Solution

Added `sqft_filter` parameter to `query_similar_cases()` that filters results to 0.5x-2x the input sqft value.

For a 1500 sqft query:
- Minimum: 750 sqft (1500 × 0.5)
- Maximum: 3000 sqft (1500 × 2.0)

## Implementation

### Backend Changes

**`backend/app/services/pinecone_cbr.py`:**
```python
def query_similar_cases(
    query_vector: List[float],
    top_k: int = 5,
    category_filter: Optional[str] = None,
    sqft_filter: Optional[float] = None,  # NEW
    namespace: str = "cbr"
) -> List[Dict[str, Any]]:
```

Added Pinecone filter conditions:
```python
if sqft_filter and sqft_filter > 0:
    sqft_min = sqft_filter * 0.5
    sqft_max = sqft_filter * 2.0
    filter_conditions.append({"sqft": {"$gte": sqft_min}})
    filter_conditions.append({"sqft": {"$lte": sqft_max}})
```

**`backend/app/routers/estimate.py`:**
Updated both `/estimate` and `/estimate/stream` endpoints to pass `sqft_filter=request.sqft`.

**`backend/app/services/hybrid_quote.py`:**
Updated CBR query to pass `sqft_filter=request.sqft`.

## Files Modified

- `backend/app/services/pinecone_cbr.py`
- `backend/app/routers/estimate.py` (2 locations)
- `backend/app/services/hybrid_quote.py`

## Verification

After deployment:
```bash
curl -X POST https://toiture-main-production-d6a5.up.railway.app/estimate \
  -H "Content-Type: application/json" \
  -d '{"sqft":1500,"category":"Bardeaux","material_lines":10,"labor_lines":5,"has_subs":false,"complexity":50}'
```

Check `similar_cases[].sqft` - all values should be between 750 and 3000.
