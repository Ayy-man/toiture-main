---
phase: 20
plan: 02
subsystem: backend-api
tags: [materials, search, api, supabase]
dependencies:
  requires:
    - "20-01: Materials database table with 1,152 items"
    - "Supabase client (Phase 5)"
  provides:
    - "GET /materials/search endpoint"
    - "GET /materials/categories endpoint"
  affects:
    - "frontend/materiaux: Will use these endpoints for material selector"
tech_stack:
  added: []
  patterns:
    - "Supabase ILIKE for fuzzy search"
    - "Pagination with count='exact'"
    - "503 graceful degradation when DB not configured"
key_files:
  created:
    - backend/app/routers/materials.py
  modified:
    - backend/app/schemas/materials.py
    - backend/app/main.py
decisions:
  - "Use ilike for fuzzy name matching (case-insensitive substring search)"
  - "Always exclude labor items (item_type='material') from material search"
  - "Return 503 when Supabase not configured (same pattern as feedback router)"
  - "No pagination for categories endpoint (~30 items max)"
metrics:
  duration: 154s
  tasks_completed: 2
  commits: 2
  files_modified: 3
  files_created: 1
  completed_at: "2026-02-09T16:48:39Z"
---

# Phase 20 Plan 02: Materials Search API Summary

**One-liner:** Backend API endpoints for searching materials by name and listing categories with pagination support.

## What Was Built

Created two REST API endpoints for the materials database:

1. **GET /materials/search**: Fuzzy search materials by name with optional category filter, pagination, and review status filtering
2. **GET /materials/categories**: Return sorted list of distinct material categories

Both endpoints integrate with the Supabase `materials` table created in plan 20-01 and follow the same graceful degradation pattern as the existing feedback router.

## Tasks Completed

### Task 1: Extend material schemas for database records and search ✅

**Commit:** `26e2867`

Added three new Pydantic models to `backend/app/schemas/materials.py`:

- `MaterialItem`: Represents a material from the database (14 fields including id, name, cost, sell_price, category, dimensions, review_status)
- `MaterialSearchResponse`: Search endpoint response with materials list, count, and total_available for pagination
- `MaterialCategoryResponse`: Categories endpoint response with sorted categories list and count

All existing Phase 10 material prediction models (`MaterialEstimateRequest`, `MaterialPrediction`, `MaterialEstimateResponse`, `FullEstimateResponse`) remain unchanged.

**Files modified:**
- `backend/app/schemas/materials.py` (+41 lines)
- `backend/requirements.txt` (included pandas/rapidfuzz from 20-01)

**Verification:** ✅ All models importable, no conflicts with existing models

### Task 2: Create materials router with search and categories endpoints ✅

**Commit:** `ec72a51`

Created `backend/app/routers/materials.py` with two endpoints:

**GET /materials/search:**
- Query params: `q` (required, min 2 chars), `category` (optional), `include_flagged` (bool), `limit` (max 200), `offset`
- Uses Supabase ILIKE for fuzzy name matching: `.ilike('name', f'%{q}%')`
- Always filters `item_type='material'` to exclude labor items
- Filters `review_status='approved'` unless `include_flagged=True`
- Returns MaterialSearchResponse with count and total_available for pagination

**GET /materials/categories:**
- No parameters
- Returns sorted list of distinct categories for approved materials
- Categories filtered: non-null, item_type='material', review_status='approved'
- No pagination needed (~30 categories max)

Both endpoints return 503 when Supabase not configured (graceful degradation pattern).

**Files created:**
- `backend/app/routers/materials.py` (109 lines)

**Files modified:**
- `backend/app/main.py`: Import materials router, register with `app.include_router(materials.router)`

**Verification:** ✅ Router prefix is `/materials`, routes registered in app, existing endpoints unaffected

## Deviations from Plan

None - plan executed exactly as written.

## Technical Decisions

| Decision | Rationale |
|----------|-----------|
| ILIKE for fuzzy search | Case-insensitive substring matching, efficient for Postgres full-text search |
| Always exclude labor items | Material search should only return materials, not labor |
| 503 for missing Supabase | Consistent with feedback router, clear signal of unavailable service |
| No pagination for categories | Categories are few (~30 max), frontend needs full list for dropdown |
| count='exact' on search | Provides total_available for accurate pagination UI |

## Integration Points

**Upstream dependencies:**
- Supabase `materials` table (created in 20-01)
- `get_supabase()` client from Phase 5

**Downstream consumers:**
- Frontend material selector (Phase 20-03): Will use `/materials/search` for autocomplete/typeahead
- Frontend category filter dropdown: Will use `/materials/categories`

## Testing Notes

**Manual verification performed:**
- ✅ Schema imports work (`MaterialItem`, `MaterialSearchResponse`, `MaterialCategoryResponse`)
- ✅ Existing Phase 10 schemas still import (`MaterialEstimateRequest`, `MaterialPrediction`)
- ✅ Router imports successfully with prefix `/materials`
- ✅ Routes registered in app: `/materials/search`, `/materials/categories`

**Production validation needed:**
- Test search with actual materials data in Supabase
- Verify category filter returns expected results
- Test pagination with limit/offset
- Confirm 503 response when Supabase not configured

## Success Criteria Met

- [x] GET /materials/search accepts query text, category filter, pagination params
- [x] GET /materials/categories returns distinct categories for dropdown filter
- [x] Both endpoints handle missing Supabase gracefully (503)
- [x] Existing material prediction schemas and endpoints unaffected
- [x] Router registered in FastAPI app
- [x] Search results limited and paginated
- [x] Only approved materials appear in search by default
- [x] Materials endpoint returns 503 when Supabase not configured

## Next Steps

**Phase 20-03:** Create frontend material selector component that consumes these endpoints
- Typeahead/autocomplete input using `/materials/search`
- Category filter dropdown using `/materials/categories`
- Integration with quote form

## Self-Check: PASSED

**Created files exist:**
```
FOUND: backend/app/routers/materials.py
```

**Commits exist:**
```
FOUND: 26e2867
FOUND: ec72a51
```

**All verifications passed:** ✅
