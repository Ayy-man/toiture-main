# Phase 12: Laurent Feedback Fixes - Research

**Created:** 2026-01-29
**Source:** Laurent meeting feedback (January 21, 2026)

## Overview

Laurent reviewed the system on January 21, 2026 and provided critical feedback. This phase addresses 3 fixes and 2 improvements he requested.

## Issues Identified

### ISSUE #1: Missing Square Footage Data (CRITICAL)
- **Problem:** Only 33% of historical quotes contain square footage data
- **Root Cause:** Not a required field in CCube system (source data)
- **Impact:** Algorithm can't train properly on 67% of historical data
- **Note:** Square footage IS already required in our app (gt=0, le=100000). The issue is compliance tracking.

### ISSUE #2: 2022 Labor Hours Data Corrupted (HIGH)
- **Problem:** 1,512 quotes have wrong labor hours (coded 1h but actually 56h)
- **Root Cause:** "Flat roof day" item coded as 1 hour at $7,200 instead of 56 hours
- **Impact:** Cannot use 2022 data for labor cost training
- **Affects:** Elastomere category specifically

### ISSUE #3: Revenue vs Quote Value Confusion (CRITICAL)
- **Problem:** All documents say "Revenue" but data is actually "Quote Value"
- **Impact:** Misleading financial reports, unknown win rate
- **Scope:** 32+ occurrences across backend, frontend, and docs

## Improvements Requested

### IMPROVEMENT #1: Better Complexity Definition
- **Current:** Single 1-100 slider, vague and subjective
- **Requested:** 6 specific factors with 0-56 point scale
  1. Access difficulty (0-10 points)
  2. Roof pitch/slope (0-8 points)
  3. Number of penetrations (0-10 points)
  4. Material removal complexity (0-8 points)
  5. Safety concerns (0-10 points)
  6. Timeline constraints (0-10 points)

### IMPROVEMENT #2: Three Quote Options
- **Current:** Single estimate with ±20% range
- **Requested:** Basic/Standard/Premium tiers
  - BASIC: Minimum acceptable (budget option)
  - STANDARD: Recommended (most common)
  - PREMIUM: Best quality (upsell)

## Codebase Analysis

### Square Footage Locations
- `backend/app/schemas/estimate.py:26` - Required field (gt=0, le=100000)
- `backend/app/schemas/materials.py:11` - Required field
- `frontend/src/lib/schemas.ts:29-32` - Zod validation
- `backend/app/routers/estimate.py` - Multiple endpoints

### Revenue Label Locations (32+ occurrences)
**Backend:**
- `backend/app/schemas/dashboard.py` - RevenueByYear, RevenueByCategory, total_revenue
- `backend/app/routers/dashboard.py` - 25 occurrences

**Frontend:**
- `frontend/src/types/dashboard.ts` - 7 occurrences
- `frontend/src/components/apercu/revenue-chart.tsx` - 2 occurrences
- `frontend/src/components/apercu/category-chart.tsx` - 2 occurrences
- `frontend/src/components/apercu/trend-chart.tsx` - 2 occurrences
- `frontend/src/components/apercu/metrics-cards.tsx` - 1 occurrence
- `frontend/src/app/(admin)/apercu/page.tsx` - 3 occurrences
- `frontend/src/lib/i18n/fr.ts` - French labels

### Complexity Locations
- `backend/app/schemas/estimate.py:31` - Single int field (1-100)
- `backend/app/schemas/materials.py:13` - Single int field
- `backend/app/services/predictor.py:84,89` - ML feature
- `backend/app/services/material_predictor.py:82` - ML feature
- `backend/app/services/embeddings.py:61,69` - Query text
- `frontend/src/components/estimate-form.tsx:225-244` - Slider UI
- `frontend/src/lib/schemas.ts:47-51` - Zod validation

### Quote Generation Locations
- `backend/app/routers/estimate.py` - Estimate endpoints
- `backend/app/services/predictor.py` - Price prediction (±20% range)
- `backend/app/schemas/estimate.py` - EstimateResponse

### Data Quality Flag Locations (None exist)
- Need to add to Supabase `estimates` table
- Need to update `backend/app/schemas/quotes.py`
- Need to update `backend/app/routers/quotes.py`

## Plan Structure

| Plan | Title | Priority | Complexity |
|------|-------|----------|------------|
| 12-01 | Data Quality Flags + 2022 Filtering | HIGH | Low |
| 12-02 | Revenue → Total Quote Value Renaming | CRITICAL | Low |
| 12-03 | Square Footage Compliance Dashboard | CRITICAL | Medium |
| 12-04 | 6-Factor Complexity System | MEDIUM | High |
| 12-05 | Three Quote Options (Tiers) | MEDIUM | High |

## Dependencies

- Plans 12-01, 12-02, 12-03 have no dependencies (can run in parallel)
- Plan 12-04 affects ML features (may need model retraining consideration)
- Plan 12-05 affects pricing algorithm and UI

## Testing Strategy

Each plan includes:
1. Schema/type validation tests
2. API endpoint tests
3. UI component tests (where applicable)
4. Build verification
