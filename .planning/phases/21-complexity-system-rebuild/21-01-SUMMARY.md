---
phase: 21-complexity-system-rebuild
plan: 01
subsystem: api
tags: [pydantic, json-config, complexity, labor-hours, tier-based]

# Dependency graph
requires:
  - phase: 13-hybrid-quote-generation
    provides: HybridQuoteRequest schema foundation
provides:
  - Tier-based complexity config (6 tiers, 0-100 scale)
  - Config-driven complexity calculator service
  - Backward-compatible schema accepting old + new formats
affects: [22-new-estimation-fields, 23-submission-workflow, frontend-tier-ui]

# Tech tracking
tech-stack:
  added: [complexity_tiers_config.json, complexity_calculator.py]
  patterns: [module-level JSON config caching, additive labor hours formula]

key-files:
  created:
    - backend/app/models/complexity_tiers_config.json
    - backend/app/services/complexity_calculator.py
  modified:
    - backend/app/schemas/hybrid_quote.py

key-decisions:
  - "JSON config for business rules (no code changes needed for hour adjustments)"
  - "Module-level config caching pattern (same as predictor.py)"
  - "Backward compatibility: old 6-slider format still works"
  - "Additive formula: total_hours = base + tier + factors (not percentage-based)"
  - "All hour values are PLACEHOLDERS pending Laurent validation"

patterns-established:
  - "Config-driven business logic: hours per tier/factor externalized to JSON"
  - "Dual complexity modes: tier-based (new) and slider-based (legacy)"

# Metrics
duration: 3min
completed: 2026-02-09
---

# Phase 21 Plan 01: Complexity System Rebuild Summary

**Tier-based complexity config with 6 tiers (0-100 scale) and calculator service using additive labor hour formula**

## Performance

- **Duration:** 3 min 24 sec
- **Started:** 2026-02-09T16:46:00Z
- **Completed:** 2026-02-09T16:49:24Z
- **Tasks:** 2
- **Files modified:** 3 (2 created, 1 modified)

## Accomplishments
- Created `complexity_tiers_config.json` with 6 named tiers (Simple to Extreme)
- 8 factor definitions with hour-based values (roof pitch, access, demolition, penetrations, security, material removal, sections, layers)
- Base time per category with sqft scaling and min hours
- Built `complexity_calculator.py` service with `calculate_complexity_hours()` function
- Updated `HybridQuoteRequest` schema to accept both old (0-56 slider) and new (tier + factor) formats
- All old complexity fields made Optional for backward compatibility

## Task Commits

Each task was committed atomically:

1. **Task 1: Create complexity tiers config JSON and calculator service** - `3cef1a5` (feat)
2. **Task 2: Update HybridQuoteRequest schema with new tier + factor fields** - `d0a7847` (feat)

## Files Created/Modified
- `backend/app/models/complexity_tiers_config.json` - 6-tier config with hour values per factor, base time per category
- `backend/app/services/complexity_calculator.py` - Calculator service returning base + tier + factor hours breakdown
- `backend/app/schemas/hybrid_quote.py` - Added 10 new Optional fields (tier, score, 8 factors), made old fields Optional

## Decisions Made
- **JSON config for business logic:** Hour values in external JSON file so Laurent can adjust without code deployment
- **Module-level caching:** Config loaded once at module import (same pattern as predictor.py)
- **Backward compatibility:** Old 6-slider format (0-56 scale) still works via Optional fields
- **Additive formula:** `total_hours = base_hours + tier_hours + factor_hours` (not percentage multipliers)
- **Placeholder values:** All hour values marked as PLACEHOLDERS in config `_note` field - Laurent must validate before production

## Deviations from Plan

None - plan executed exactly as written

## Issues Encountered

None

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

Backend foundation complete for tier-based complexity:
- Config file ready for Laurent to populate with real hour values
- Calculator service tested and working correctly
- Schema accepts both old and new formats (zero breaking changes)
- Frontend can now build tier selector UI (next plan)

**Critical next step:** Schedule working session with Laurent to validate hour values in config. Current values are placeholders only.

## Self-Check: PASSED

All files and commits verified:
- backend/app/models/complexity_tiers_config.json: FOUND
- backend/app/services/complexity_calculator.py: FOUND
- backend/app/schemas/hybrid_quote.py: FOUND
- Commit 3cef1a5: FOUND
- Commit d0a7847: FOUND

---
*Phase: 21-complexity-system-rebuild*
*Completed: 2026-02-09*
