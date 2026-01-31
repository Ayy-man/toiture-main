---
phase: 13-hybrid-quote-generation
plan: 01
subsystem: api
tags: [pydantic, schemas, hybrid-quote, llm-tool-calling, json-schema]

# Dependency graph
requires:
  - phase: 01-fastapi-foundation
    provides: Backend structure with FastAPI and Pydantic patterns
  - phase: 10-material-id-prediction-model-training
    provides: Material prediction models referenced in schemas
provides:
  - HybridQuoteRequest Pydantic model for job parameters and 6 complexity factors
  - HybridQuoteOutput LLM tool calling schema with JSON schema support
  - HybridQuoteResponse API response with metadata and review flags
  - WorkItem, MaterialLineItem, PricingTier supporting models
  - Package exports for cleaner imports
affects: [13-02-hybrid-quote-api, 13-03-llm-merger-service, 13-04-full-quote-ui]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - model_validator for cross-field validation (complexity sum check)
    - Literal types for constrained source tracking (CBR/ML/MERGED)
    - json_schema_extra for API documentation examples

key-files:
  created:
    - backend/app/schemas/hybrid_quote.py
  modified:
    - backend/app/schemas/__init__.py

key-decisions:
  - "Used model_validator instead of field_validator for complexity_aggregate validation (runs after all fields populated)"
  - "5% tolerance for complexity_aggregate sum to handle frontend rounding"
  - "Three-tier pricing (Basic/Standard/Premium) enforced at model level"
  - "Source tracking with Literal[CBR, ML, MERGED] for transparency"

patterns-established:
  - "LLM tool calling schemas: Pydantic models with model_json_schema() support"
  - "Cross-field validation: model_validator(mode='after') for complex constraints"
  - "API documentation: json_schema_extra with realistic examples"

# Metrics
duration: 3min
completed: 2026-01-31
---

# Phase 13 Plan 01: Hybrid Quote Pydantic Schemas Summary

**Pydantic schemas for hybrid quote generation with LLM tool calling support, 6 complexity factors validation, and three-tier pricing enforcement**

## Performance

- **Duration:** 3 minutes
- **Started:** 2026-01-31T21:14:38Z
- **Completed:** 2026-01-31T21:17:54Z
- **Tasks:** 2/2
- **Files modified:** 2

## Accomplishments
- Created comprehensive HybridQuoteRequest with 6 complexity factors and cross-field validation
- Built HybridQuoteOutput schema optimized for Claude's structured outputs API (model_json_schema() ready)
- Implemented three-tier pricing enforcement (Basic/Standard/Premium) via model_validator
- Added source tracking (CBR/ML/MERGED) across WorkItem and MaterialLineItem models
- Exported all 6 models from package init for cleaner imports

## Task Commits

Each task was committed atomically:

1. **Task 1: Create hybrid quote Pydantic schemas** - `13240ac` (feat)
2. **Task 2: Export schemas from package init** - `b6f46a4` (chore)

## Files Created/Modified
- `backend/app/schemas/hybrid_quote.py` - 559 lines defining 6 Pydantic models for hybrid quote system
- `backend/app/schemas/__init__.py` - Added exports for HybridQuoteRequest, HybridQuoteResponse, HybridQuoteOutput, WorkItem, MaterialLineItem, PricingTier

## Decisions Made
- **model_validator over field_validator:** Used model_validator(mode="after") for complexity_aggregate validation because field_validators run before all fields are available
- **5% tolerance:** Added rounding tolerance to complexity_aggregate sum check to handle frontend rounding differences
- **Explicit tier enforcement:** model_validator ensures exactly 3 pricing tiers with required names (Basic, Standard, Premium)
- **Source tracking pattern:** Literal["CBR", "ML", "MERGED"] provides transparency for where estimates originated

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed complexity validation using model_validator**
- **Found during:** Task 1 (schema creation)
- **Issue:** field_validator for complexity_aggregate couldn't access other fields reliably
- **Fix:** Changed to model_validator(mode="after") which runs after all fields are populated
- **Files modified:** backend/app/schemas/hybrid_quote.py
- **Verification:** Tests confirm invalid complexity_aggregate is correctly rejected
- **Committed in:** 13240ac (Task 1 commit)

---

**Total deviations:** 1 auto-fixed (Rule 1 - Bug)
**Impact on plan:** Bug fix necessary for correct validation. No scope creep.

## Issues Encountered
None - plan executed smoothly after the validation approach fix.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- Pydantic schemas ready for Phase 13-02 (Hybrid Quote API endpoint)
- model_json_schema() support ready for Phase 13-03 (LLM merger service)
- HybridQuoteOutput can be used directly as Claude tool calling schema

---
*Phase: 13-hybrid-quote-generation*
*Completed: 2026-01-31*
