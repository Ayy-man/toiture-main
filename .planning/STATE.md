# Project State: TOITURELV Cortex

**Last Updated:** 2026-01-18

## Project Reference

See: .planning/PROJECT.md (updated 2026-01-18)

**Core value:** Accurate price estimates with explainable reasoning
**Current focus:** Phase 3 - LLM Reasoning

## Progress

| Phase | Status | Plans | Progress |
|-------|--------|-------|----------|
| 1 | ✓ Complete | 2/2 | 100% |
| 2 | ✓ Complete | 2/2 | 100% |
| 3 | ○ Pending | 0/2 | 0% |
| 4 | ○ Pending | 0/2 | 0% |
| 5 | ○ Pending | 0/? | 0% |
| 6 | ○ Pending | 0/? | 0% |
| 7 | ○ Pending | 0/? | 0% |
| 8 | ○ Pending | 0/? | 0% |

**Overall:** 2/8 phases complete (25%)

```
Progress: [█████░░░░░░░░░░░░░░░] 25%
```

## Current Phase

**Phase 3: LLM Reasoning**
- Goal: Estimates include human-readable explanations
- Requirements: LLM-01, LLM-02, LLM-03
- Status: Not started
- Dependencies: OpenRouter API key (configured)

### Phase 2 Complete ✓
- **02-01:** Pinecone services and embedding upload (8,132 vectors)
- **02-02:** Endpoint integration with similar cases
- **Verified:** 3/3 must-haves, 6/6 CBR tests passing

### Phase 1 Complete ✓
- **01-01:** Backend structure and model loading
- **01-02:** API endpoints with Pydantic validation
- **Verified:** 7/7 must-haves, 9/9 tests passing

## Key Decisions

| Decision | Made In | Rationale |
|----------|---------|-----------|
| Lifespan context manager over @app.on_event | 01-01 | FastAPI 0.128+ best practice, deprecated events |
| Module-level _models dict for model storage | 01-01 | Shared access across requests without globals |
| Path(__file__) for MODEL_DIR | 01-01 | Works regardless of CWD |
| Sync def for estimate endpoint | 01-02 | sklearn is CPU-bound, async would block event loop |
| Accept both accented/non-accented Elastomere | 01-02 | User convenience with field_validator normalization |
| TestClient as context manager in fixtures | 01-02 | Required for lifespan events to trigger model loading |

## Session History

| Date | Action | Notes |
|------|--------|-------|
| 2026-01-18 | Project initialized | Codebase mapped, PROJECT.md created |
| 2026-01-18 | Roadmap created | 8 phases, 28 requirements |
| 2026-01-18 | Plan 01-01 executed | Backend structure with lifespan and CORS |
| 2026-01-18 | Plan 01-02 executed | API endpoints, schemas, 9 tests passing |
| 2026-01-18 | Phase 1 verified | All 4 success criteria met, goal achieved |

## Session Continuity

Last session: 2026-01-18
Stopped at: Completed 01-02-PLAN.md
Resume file: None

## Blockers

None currently.

## Notes

- Existing ML models in cortex-data/ (v3 in predict_final.py, v4 trained but not integrated)
- 8,132 CBR embeddings ready for Pinecone upload
- Tech stack: FastAPI (Railway) + Next.js (Vercel) + Pinecone + Supabase + OpenRouter
- ML model files need to be copied from cortex-data/ to backend/app/models/ before running

---
*State updated: 2026-01-18*
