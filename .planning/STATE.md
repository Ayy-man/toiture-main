# Project State: TOITURELV Cortex

**Last Updated:** 2026-01-18

## Project Reference

See: .planning/PROJECT.md (updated 2026-01-18)

**Core value:** Accurate price estimates with explainable reasoning
**Current focus:** Phase 5 - Case History (or Phase 6 - Analytics Dashboard)

## Progress

| Phase | Status | Plans | Progress |
|-------|--------|-------|----------|
| 1 | Complete | 2/2 | 100% |
| 2 | Complete | 2/2 | 100% |
| 3 | Complete | 2/2 | 100% |
| 4 | Complete | 2/2 | 100% |
| 5 | Pending | 0/? | 0% |
| 6 | Pending | 0/? | 0% |
| 7 | Complete | 1/1 | 100% |
| 8 | Pending | 0/? | 0% |

**Overall:** 9/14 plans complete (64%)

```
Progress: [█████████████░░░░░░░] 64%
```

## Current Phase

**Phase 4: Estimate Form** (Complete)
- Goal: Frontend form for estimate requests
- Requirements: FORM-01 through FORM-05
- Status: All plans complete

### Phase 4 Complete
- **04-01:** Next.js 15 project with shadcn/ui, Zod schemas, API client
- **04-02:** EstimateForm with 6 fields, validation, result display components
- Form displays correctly (testing deferred until backend deployed to Railway)

### Phase 7 Complete
- **07-01:** Password gate with iron-session, middleware protection, login/logout
- iron-session 8.x for encrypted cookie sessions
- Server Actions for auth (authenticate/logout)
- Middleware-based route protection
- LogoutButton component ready for layout integration

### Phase 3 Complete
- **03-01:** LLM reasoning service module with OpenRouter
- **03-02:** LLM integration into /estimate endpoint
- LLM client lifecycle in FastAPI lifespan
- reasoning field in EstimateResponse (graceful degradation)
- 16 tests passing

### Phase 2 Complete
- **02-01:** Pinecone services and embedding upload (8,132 vectors)
- **02-02:** Endpoint integration with similar cases
- **Verified:** 3/3 must-haves, 6/6 CBR tests passing

### Phase 1 Complete
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
| openai pkg with OpenRouter base_url | 03-01 | Mature SDK, OpenAI API compatibility |
| Default model openai/gpt-4o-mini | 03-01 | Best cost/quality balance ($0.15/$0.60 per 1M tokens) |
| 30s timeout with 3 retry attempts | 03-01 | Prevents hangs, handles transient 401s |
| Temperature 0.3 for reasoning | 03-01 | Consistent, factual responses |
| LLM init last, close first in lifespan | 03-02 | Proper dependency order |
| Optional[str] reasoning with None default | 03-02 | Graceful degradation when LLM unavailable |
| Catch all exceptions in reasoning generation | 03-02 | Never block estimates due to LLM failures |
| Zod 4 with message param for enum | 04-01 | Zod 4.x uses simplified API for enum options |
| Frontend uses Elastomere without accent | 04-01 | Backend field_validator normalizes to accented version |
| Boolean to 0/1 conversion in API client | 04-01 | Backend expects Literal[0, 1] for has_subs |
| types/estimate.ts re-export pattern | 04-01 | Cleaner imports from single location |
| iron-session 8.x over NextAuth.js | 07-01 | Lightweight stateless sessions for simple shared password |
| Server Actions over API routes for auth | 07-01 | Direct form action, simpler pattern |
| await cookies() pattern | 07-01 | Required for Next.js 15 async dynamic APIs |
| Redirect param preservation | 07-01 | Unauthenticated users return to intended destination |
| Controlled form with react-hook-form | 04-02 | Consistent state management with Zod validation |
| Color-coded confidence badge | 04-02 | Visual clarity: green (HIGH), yellow (MEDIUM), red (LOW) |
| Inline result display below form | 04-02 | Single-page UX without navigation |

## Session History

| Date | Action | Notes |
|------|--------|-------|
| 2026-01-18 | Project initialized | Codebase mapped, PROJECT.md created |
| 2026-01-18 | Roadmap created | 8 phases, 28 requirements |
| 2026-01-18 | Plan 01-01 executed | Backend structure with lifespan and CORS |
| 2026-01-18 | Plan 01-02 executed | API endpoints, schemas, 9 tests passing |
| 2026-01-18 | Phase 1 verified | All 4 success criteria met, goal achieved |
| 2026-01-18 | Plan 03-01 executed | LLM reasoning service with OpenRouter |
| 2026-01-18 | Plan 03-02 executed | LLM integration into /estimate endpoint |
| 2026-01-18 | Plan 04-01 executed | Next.js 15, shadcn/ui, Zod schemas, API client |
| 2026-01-18 | Plan 07-01 executed | Password gate auth with iron-session |
| 2026-01-18 | Plan 04-02 executed | Estimate form with 6 fields, result display (testing deferred) |

## Session Continuity

Last session: 2026-01-18
Stopped at: Completed 04-02-PLAN.md
Resume file: None

## Blockers

None currently.

## Notes

- Existing ML models in cortex-data/ (v3 in predict_final.py, v4 trained but not integrated)
- 8,132 CBR embeddings ready for Pinecone upload
- Tech stack: FastAPI (Railway) + Next.js (Vercel) + Pinecone + Supabase + OpenRouter
- ML model files need to be copied from cortex-data/ to backend/app/models/ before running
- Frontend estimate form complete with all 6 input fields
- Authentication complete - all routes protected except /login, API, and static assets
- Backend needs deployment to Railway for full end-to-end testing
- Phase 4 complete: Ready for Phase 5 (Case History) or Phase 6 (Analytics Dashboard)

---
*State updated: 2026-01-18*
