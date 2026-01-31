---
phase: 13-hybrid-quote-generation
plan: 03
subsystem: api
tags: [asyncio, openrouter, llm, cbr, ml, orchestration, json-parsing, pydantic]

# Dependency graph
requires:
  - phase: 13-01
    provides: HybridQuoteRequest, HybridQuoteResponse, HybridQuoteOutput, PricingTier schemas
  - phase: 13-02
    provides: calculate_confidence, calculate_confidence_ml_only, calculate_data_completeness
  - phase: 03-01
    provides: OpenRouter LLM client via get_client()
  - phase: 02-02
    provides: Pinecone CBR via query_similar_cases
  - phase: 10-02
    provides: Material prediction via predict_materials
  - phase: 01-02
    provides: Price prediction via predict()
provides:
  - Async hybrid quote orchestrator (generate_hybrid_quote)
  - Parallel CBR + ML execution with asyncio.gather()
  - LLM merger with JSON parsing and Pydantic validation
  - Graceful fallback handling (CBR-only, ML-only, LLM failure)
  - Processing time tracking for SLA monitoring
affects: [13-04, frontend-quote-ui, hybrid-quote-api-endpoint]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - Async orchestration with asyncio.gather() + return_exceptions=True
    - run_in_executor for wrapping sync functions in async context
    - JSON extraction from LLM responses with regex fallback
    - Pydantic model_validate() for LLM output validation

key-files:
  created:
    - backend/app/services/hybrid_quote.py
  modified: []

key-decisions:
  - "Reuse existing OpenRouter client via get_client() from llm_reasoning.py"
  - "JSON-in-prompt approach with _extract_json() regex for robust parsing"
  - "asyncio.gather() with return_exceptions=True for parallel execution"
  - "Fallback pricing tiers: Basic (-15%), Standard (base), Premium (+18%)"

patterns-established:
  - "Async orchestration: Use run_in_executor to wrap sync ML/CBR calls"
  - "LLM validation: Parse JSON with regex, validate with Pydantic model_validate()"
  - "Graceful degradation: Handle partial failures with explicit fallback paths"

# Metrics
duration: 2min
completed: 2026-01-31
---

# Phase 13 Plan 03: Hybrid Quote Orchestrator Summary

**Async orchestrator coordinating CBR + ML predictions in parallel, then LLM merger with JSON parsing and Pydantic validation for three-tier pricing quotes**

## Performance

- **Duration:** 2 min
- **Started:** 2026-01-31T21:26:41Z
- **Completed:** 2026-01-31T21:28:28Z
- **Tasks:** 1
- **Files modified:** 1

## Accomplishments
- Created async orchestrator with asyncio.gather() for parallel CBR + ML execution
- Implemented LLM merger reusing existing OpenRouter client from llm_reasoning.py
- Built robust JSON extraction handling both raw JSON and markdown code blocks
- Added Pydantic validation via HybridQuoteOutput.model_validate()
- Implemented graceful fallback handling for CBR-only, ML-only, and LLM failure cases
- Processing time tracking for <5 second SLA monitoring

## Task Commits

Each task was committed atomically:

1. **Task 1: Create hybrid quote orchestrator service** - `87cda7e` (feat)

## Files Created/Modified
- `backend/app/services/hybrid_quote.py` - Main orchestration service (416 lines)
  - `generate_hybrid_quote()` - Async entry point for hybrid quote generation
  - `_run_cbr_query()` - Async wrapper for CBR/Pinecone query
  - `_run_ml_prediction()` - Async wrapper for ML price and material prediction
  - `_format_merger_prompt()` - LLM prompt builder for CBR + ML merging
  - `_merge_with_llm()` - OpenRouter LLM call with JSON parsing
  - `_extract_json()` - Robust JSON extraction from LLM response
  - `_generate_fallback_tiers()` - Fallback pricing when LLM unavailable

## Decisions Made
- **Reuse existing OpenRouter client** - No new API configuration needed, leverages get_client() from llm_reasoning.py
- **JSON-in-prompt approach** - More robust than tool calling for this use case, handles both raw JSON and markdown code blocks
- **asyncio.gather with return_exceptions** - Allows parallel execution while gracefully handling individual failures
- **Fallback tier percentages** - Basic (-15%), Standard (base), Premium (+18%) match industry standards

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None - all verification tests passed on first attempt.

## User Setup Required

None - no external service configuration required. Uses existing OpenRouter, Pinecone, and ML model configurations.

## Next Phase Readiness
- Hybrid quote orchestrator ready for API endpoint integration
- 13-04 can now build frontend UI consuming generate_hybrid_quote()
- All three AI systems (CBR, ML, LLM) coordinated in single async pipeline
- Response time tracking enables SLA monitoring once endpoint deployed

---
*Phase: 13-hybrid-quote-generation*
*Completed: 2026-01-31*
