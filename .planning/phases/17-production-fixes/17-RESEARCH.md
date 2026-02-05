# Phase 17: Production Fixes - Research

**Created:** 2026-02-05
**Source:** Production deployment testing and user feedback

## Overview

After deploying to Railway (backend) and Vercel (frontend), multiple issues were discovered that need fixing before the app is usable in production.

## Issues Identified

### ISSUE #1: Mixed Content (CRITICAL)
- **Problem:** Vercel frontend (HTTPS) hitting Railway backend over HTTP
- **Impact:** Browsers silently block mixed content requests
- **Root Cause:** NEXT_PUBLIC_API_URL env var likely set with http:// instead of https://
- **Fix:** Update to https:// and redeploy

### ISSUE #2: Dashboard 500 Errors (CRITICAL)
- **Problem:** /dashboard/metrics and /dashboard/charts return 500
- **Impact:** Aperçu page completely broken
- **Likely Causes:**
  - Data files not included in Docker image (cbr_cases.json, master_quotes_valid.csv)
  - Field name mismatch
  - Division by zero in metric calculations
  - Missing dependency
- **Fix:** Check Railway logs for traceback, fix root cause

### ISSUE #3: Historique and Clients Pages Broken
- **Problem:** Pages show empty or error state
- **Impact:** Can't browse historical quotes or customers
- **Dependencies:** May be fixed by Steps 1-2
- **Endpoints:** /quotes, /customers

### ISSUE #4: Matériaux Tab Placeholder
- **Problem:** Shows "Bientôt disponible - Phase 10" but backend exists
- **Backend Status:**
  - /estimate/materials endpoint EXISTS and works
  - material_selector.pkl (11MB) loaded
  - quantity_regressors.pkl (25MB) loaded
  - MaterialPredictor class in material_predictor.py
- **Fix:** Replace placeholder with actual form and results display

### ISSUE #5: Similar Cases Quality
- **Problem:** 1500 sqft bardeaux query returns five 138 sqft jobs
- **Impact:** Similar cases are useless for comparison
- **Root Cause:** No sqft filter in Pinecone query
- **Fix:** Add metadata filter: min 0.5x, max 2x input sqft

### ISSUE #6: Missing Feedback System
- **Problem:** No way to collect feedback on estimates
- **Impact:** Can't improve model without feedback data
- **Required:**
  - 👍/👎 buttons on Prix and Soumission Complète results
  - Expand panel for actual price and reason
  - POST to /feedback → Supabase cortex_feedback table
- **Note:** Review queue UI is out of scope - just collect data

### ISSUE #7: French Hardcode Incomplete
- **Problem:** Prix tab and other pages still have English strings
- **Impact:** Inconsistent UX for French users
- **Scope:** ~20+ strings identified, possibly more
- **Note:** Keep EN/FR toggle functional

## Plan Structure

| Plan | Title | Priority | Status |
|------|-------|----------|--------|
| 17-01 | Mixed Content Fix | CRITICAL | ✅ Complete (already fixed) |
| 17-02 | Dashboard 500 Errors | CRITICAL | ✅ Code ready, needs deploy |
| 17-03 | Historique & Clients Pages | HIGH | ⏳ Verify after 17-02 deploy |
| 17-04 | Matériaux Tab Implementation | HIGH | ✅ Code ready, needs deploy |
| 17-05 | Similar Cases Quality Filter | MEDIUM | ✅ Code ready, needs deploy |
| 17-06 | Feedback System | MEDIUM | ✅ Code ready, needs deploy + Supabase |
| 17-07 | French Translation Completion | LOW | ❌ Not started |

## Execution Order

Plans must be executed in order due to dependencies:
1. **Wave 1:** 17-01 (Mixed Content) - unlocks everything else
2. **Wave 2:** 17-02 (Dashboard 500s) - may fix 17-03
3. **Wave 3:** 17-03 (Historique/Clients) - verify after 17-02
4. **Wave 4:** 17-04, 17-05, 17-06, 17-07 can run in parallel

## Verification Checklist

After all plans complete:
- [ ] /dashboard/metrics returns 200 with JSON
- [ ] /dashboard/charts returns 200 with JSON
- [ ] /quotes?page=1&limit=10 returns quote data
- [ ] /customers returns customer data
- [ ] Aperçu page shows KPI cards and charts with real numbers
- [ ] Historique page shows paginated quotes
- [ ] Clients page shows searchable customers
- [ ] Matériaux tab shows real predictions (not placeholder)
- [ ] Similar cases for 1500 sqft return jobs in 750-3000 sqft range
- [ ] Feedback 👍/👎 appears on Prix and Soumission Complète results
- [ ] Feedback POST succeeds and stores in Supabase
- [ ] No English strings remain on any page
- [ ] No Mixed Content warnings in browser console
- [ ] No 500 errors in browser console

## Production URLs

- **Backend:** https://toiture-main-production-d6a5.up.railway.app
- **Frontend:** (Vercel URL - check Vercel dashboard)
