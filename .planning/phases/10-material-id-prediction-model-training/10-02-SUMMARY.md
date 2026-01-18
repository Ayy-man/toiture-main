---
phase: 10-material-id-prediction
plan: 02
subsystem: api
tags: [fastapi, pydantic, material-prediction, ml-inference, lazy-loading]

# Dependency graph
requires:
  - phase: 10-01
    provides: "Trained material prediction models (selector, quantity regressors, rules)"
provides:
  - "POST /estimate/materials endpoint for material ID predictions"
  - "POST /estimate/full endpoint combining price + material estimates"
  - "MaterialPredictor service with lazy loading"
  - "Pydantic schemas for material endpoints"
affects: [11-cortex-admin-dashboard, frontend]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Lazy loading for ML models (same as predictor.py)"
    - "Feature extraction for material triggers"

key-files:
  created:
    - backend/app/schemas/materials.py
    - backend/app/services/material_predictor.py
  modified:
    - backend/app/routers/estimate.py

key-decisions:
  - "Use 0.3 threshold for multi-label classification (tuned during training)"
  - "Lazy load all material models on first /estimate/materials call"
  - "Feature triggers extract material_id from trigger objects"

patterns-established:
  - "MaterialEstimateRequest schema for material endpoints"
  - "Lazy loading pattern for material prediction models"

# Metrics
duration: 3min
completed: 2026-01-18
---

# Phase 10 Plan 02: Material Prediction Endpoints Summary

**FastAPI endpoints exposing material ID predictions via /estimate/materials and /estimate/full with lazy-loaded ML models**

## Performance

- **Duration:** 3 min
- **Started:** 2026-01-18T18:32:11Z
- **Completed:** 2026-01-18T18:35:38Z
- **Tasks:** 3
- **Files modified:** 3

## Accomplishments

- Created Pydantic schemas for material prediction requests/responses
- Built MaterialPredictor service with lazy loading (same pattern as predictor.py)
- Added /estimate/materials endpoint returning predicted material IDs with quantities
- Added /estimate/full endpoint combining price estimate + material predictions
- Response times within targets: materials < 2s, full < 5s

## Task Commits

Each task was committed atomically:

1. **Task 1: Create Pydantic schemas for material endpoints** - `572c684` (feat)
2. **Task 2: Create material predictor service with lazy loading** - `cd73067` (feat)
3. **Task 3: Add material endpoints to estimate router** - `adad2c0` (feat)

## Files Created/Modified

- `backend/app/schemas/materials.py` - MaterialEstimateRequest, MaterialPrediction, MaterialEstimateResponse, FullEstimateResponse
- `backend/app/services/material_predictor.py` - predict_materials() with lazy model loading
- `backend/app/routers/estimate.py` - Added /estimate/materials and /estimate/full endpoints

## Decisions Made

- **Threshold 0.3 for classification:** Tuned during model training for better F1 on imbalanced data
- **Lazy loading pattern:** Follow exact pattern from predictor.py for consistency
- **Feature trigger extraction:** Triggers are objects with material_id key, not raw IDs

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Fixed feature trigger format**
- **Found during:** Task 3 (endpoint testing)
- **Issue:** Feature triggers in JSON are objects with `material_id` key, not raw integers. Code was trying to append objects to predicted_ids list.
- **Fix:** Extract `trigger["material_id"]` from each trigger object before appending
- **Files modified:** backend/app/services/material_predictor.py
- **Verification:** Endpoints return 200 with valid material predictions
- **Committed in:** adad2c0 (Task 3 commit)

---

**Total deviations:** 1 auto-fixed (1 blocking)
**Impact on plan:** Minor data format fix. No scope creep.

## Issues Encountered

None - after the auto-fix, all tests passed.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Material prediction endpoints ready for frontend integration
- /estimate/full combines price + materials in single call
- Ready for Phase 11 (Cortex Admin Dashboard) to consume these endpoints
- No blockers

---
*Phase: 10-material-id-prediction*
*Completed: 2026-01-18*
