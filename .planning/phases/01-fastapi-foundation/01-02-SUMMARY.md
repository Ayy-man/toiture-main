---
phase: 01-fastapi-foundation
plan: 02
subsystem: api
tags: [fastapi, pydantic, pytest, endpoints, validation]

# Dependency graph
requires:
  - phase: 01-01
    provides: FastAPI app structure with lifespan and predictor service
provides:
  - Health check endpoint (GET /health)
  - Estimate endpoint (POST /estimate) with Pydantic validation
  - Request/response schemas for estimate
  - Comprehensive endpoint tests
affects: [01-03, phase-2]

# Tech tracking
tech-stack:
  added: [pytest, httpx]
  patterns: [pydantic-field-validators, testclient-lifespan-context]

key-files:
  created:
    - backend/app/schemas/estimate.py
    - backend/app/routers/health.py
    - backend/app/routers/estimate.py
    - backend/tests/conftest.py
    - backend/tests/test_health.py
    - backend/tests/test_estimate.py
  modified:
    - backend/app/schemas/__init__.py
    - backend/app/routers/__init__.py
    - backend/app/main.py

key-decisions:
  - "Use sync def (not async) for estimate endpoint - sklearn is CPU-bound"
  - "Accept both accented and non-accented Elastomere via field_validator"
  - "TestClient as context manager to trigger lifespan model loading in tests"

patterns-established:
  - "Pydantic field_validator: normalize input values (Elastomere -> Elastomere)"
  - "TestClient fixture: use with-statement for lifespan events"
  - "Router organization: separate health and estimate routers, include in main.py"

# Metrics
duration: 4min
completed: 2026-01-18
---

# Phase 1 Plan 02: API Endpoints Summary

**Health and estimate endpoints with Pydantic v2 validation, category normalization, and 9 pytest tests**

## Performance

- **Duration:** 4 min
- **Started:** 2026-01-18T09:38:13Z
- **Completed:** 2026-01-18T09:41:51Z
- **Tasks:** 3
- **Files modified:** 10

## Accomplishments

- EstimateRequest/EstimateResponse Pydantic schemas with validation constraints
- Health endpoint returning status and version
- Estimate endpoint with ML prediction integration
- 9 comprehensive tests covering valid inputs, validation errors, and edge cases

## Task Commits

Each task was committed atomically:

1. **Task 1: Create Pydantic schemas** - `cdeae37` (feat)
2. **Task 2: Create health and estimate routers** - `cd47bf6` (feat)
3. **Task 3: Wire routers and add tests** - `705617d` (feat)

## Files Created/Modified

- `backend/app/schemas/estimate.py` - EstimateRequest/EstimateResponse with validation
- `backend/app/schemas/__init__.py` - Export schemas
- `backend/app/routers/health.py` - GET /health endpoint
- `backend/app/routers/estimate.py` - POST /estimate endpoint with ML integration
- `backend/app/routers/__init__.py` - Export routers
- `backend/app/main.py` - Include routers
- `backend/tests/__init__.py` - Tests package marker
- `backend/tests/conftest.py` - TestClient fixture with lifespan support
- `backend/tests/test_health.py` - Health endpoint test
- `backend/tests/test_estimate.py` - 8 estimate endpoint tests

## Decisions Made

- **Sync endpoints:** Used regular `def` instead of `async def` for estimate endpoint since sklearn predict() is CPU-bound and would block the event loop if async
- **Category normalization:** field_validator accepts "Elastomere" (without accent) and normalizes to "Elastomere" (with accent) for ML model compatibility
- **TestClient context manager:** Used `with TestClient(app) as client:` in fixture to trigger lifespan events, ensuring models are loaded during tests

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] TestClient not triggering lifespan events**
- **Found during:** Task 3 (running tests)
- **Issue:** Tests returned 500 errors because models weren't loaded - TestClient wasn't triggering lifespan context manager
- **Fix:** Changed fixture from `return TestClient(app)` to `with TestClient(app) as client: yield client`
- **Files modified:** backend/tests/conftest.py
- **Verification:** All 9 tests pass
- **Committed in:** 705617d (Task 3 commit)

---

**Total deviations:** 1 auto-fixed (1 blocking)
**Impact on plan:** Essential fix for test functionality. No scope creep.

## Issues Encountered

None beyond the auto-fixed blocking issue.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- API endpoints complete and tested
- Ready for Plan 03 (Dockerfile and Railway deployment)
- Model files must be copied from cortex-data/ to backend/app/models/ before running:
  - cortex_model_global.pkl
  - cortex_model_Bardeaux.pkl
  - category_encoder_v3.pkl
  - cortex_config_v3.json

---
*Phase: 01-fastapi-foundation*
*Completed: 2026-01-18*
