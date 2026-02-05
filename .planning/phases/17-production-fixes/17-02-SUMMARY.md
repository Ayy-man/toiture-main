# 17-02 Summary: Dashboard 500 Errors Fix

**Status:** Complete (code ready, needs deployment)
**Completed:** 2026-02-05

## Problem

`/dashboard/metrics` and `/dashboard/charts` endpoints returned 500 errors:
```json
{"detail":"Failed to fetch dashboard metrics"}
```

## Root Cause

Dashboard queries were selecting columns that don't exist in the `estimates` table:
- `margin_percent` - not stored
- `client_name` - not stored

The estimates table only contains: `id, sqft, category, material_lines, labor_lines, has_subs, complexity, ai_estimate, range_low, range_high, confidence, model, reasoning, reviewed, created_at`

## Fix

Updated `backend/app/routers/dashboard.py`:

**Metrics endpoint:**
- Changed SELECT from `"ai_estimate, margin_percent, client_name"` to `"ai_estimate, category, created_at"`
- Use category count as proxy for active_clients
- Set average_margin to 0.0 (feature not yet implemented)

**Charts endpoint:**
- Changed SELECT from `"created_at, category, ai_estimate, client_name"` to `"created_at, category, ai_estimate"`
- Disabled top_clients chart (returns empty array until client_name tracking added)

## Files Modified

- `backend/app/routers/dashboard.py`

## Verification

After deployment:
```bash
curl https://toiture-main-production-d6a5.up.railway.app/dashboard/metrics
curl https://toiture-main-production-d6a5.up.railway.app/dashboard/charts
```
Should return 200 with JSON data.
