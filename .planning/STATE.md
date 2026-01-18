# Project State: TOITURELV Cortex

**Last Updated:** 2026-01-18

## Project Reference

See: .planning/PROJECT.md (updated 2026-01-18)

**Core value:** Accurate price estimates with explainable reasoning
**Current focus:** Phase 8 - Deployment (in progress)

## Progress

| Phase | Status | Plans | Progress |
|-------|--------|-------|----------|
| 1 | Complete | 2/2 | 100% |
| 2 | Complete | 2/2 | 100% |
| 3 | Complete | 2/2 | 100% |
| 4 | Complete | 2/2 | 100% |
| 5 | Complete | 2/2 | 100% |
| 6 | In Progress | 1/2 | 50% |
| 7 | Complete | 1/1 | 100% |
| 8 | In Progress | 1/2 | 50% |

**Overall:** 13/16 plans complete (81%)

```
Progress: [████████████████░░░░] 81%
```

## Current Phase

**Phase 8: Deployment** (In Progress)
- Goal: Deploy backend to Railway, frontend to Vercel
- Requirements: DEPLOY-01, DEPLOY-02, DEPLOY-03
- Status: Plan 01 complete, Plan 02 pending

### Phase 8 In Progress
- **08-01:** Deployment configuration files
  - Dockerfile with CPU-only PyTorch (~2GB smaller)
  - railway.json with health check and restart policy
  - vercel.json with Next.js framework config
  - Fixed all Python imports (backend.app.* to app.*)
  - Environment variable documentation (.env.example)

### Phase 6 In Progress
- **06-01:** Analytics data layer with React Query and Supabase hooks
  - React Query provider with 5-min staleTime
  - Supabase browser client for RPC calls
  - Analytics hooks: useAccuracyStats, useCategoryBreakdown, useConfidenceAccuracy
  - Time period filtering (7d, 30d, all)

### Phase 5 Complete
- **05-01:** Supabase integration with feedback API endpoints
  - Supabase client singleton with graceful degradation
  - Estimates auto-saved to database after prediction
  - Feedback endpoints: GET /pending, GET /estimate/{id}, POST /submit
- **05-02:** Review queue UI with TanStack Table
  - /review page with pending estimates table
  - Feedback dialog for entering Laurent's price
  - API client for feedback operations

### Phase 4 Complete
- **04-01:** Next.js 15 project with shadcn/ui, Zod schemas, API client
- **04-02:** EstimateForm with 6 fields, validation, result display components
- Form displays correctly (testing deferred until backend deployed to Railway)

### Phase 7 Complete
- **07-01:** Password gate with iron-session, middleware protection, login/logout
- iron-session 8.x for encrypted cookie sessions
- Server Actions for auth (authenticate/logout)
- Middleware-based route protection

### Phase 3 Complete
- **03-01:** LLM reasoning service module with OpenRouter
- **03-02:** LLM integration into /estimate endpoint
- reasoning field in EstimateResponse (graceful degradation)

### Phase 2 Complete
- **02-01:** Pinecone services and embedding upload (8,132 vectors)
- **02-02:** Endpoint integration with similar cases

### Phase 1 Complete
- **01-01:** Backend structure and model loading
- **01-02:** API endpoints with Pydantic validation

## Key Decisions

| Decision | Made In | Rationale |
|----------|---------|-----------|
| Lifespan context manager over @app.on_event | 01-01 | FastAPI 0.128+ best practice |
| Module-level _models dict for model storage | 01-01 | Shared access across requests |
| openai pkg with OpenRouter base_url | 03-01 | Mature SDK, OpenAI API compatibility |
| iron-session 8.x over NextAuth.js | 07-01 | Lightweight stateless sessions |
| get_supabase() returns None vs raises | 05-01 | Graceful degradation pattern |
| Feedback endpoints return 503 when unavailable | 05-01 | Clear signal for unconfigured service |
| Generic DataTable component | 05-02 | Reusable for analytics dashboard |
| createColumns factory with onReview callback | 05-02 | Avoids prop drilling |
| Type assertions for Supabase RPC | 06-01 | No generated types for custom functions |
| 5-min staleTime for analytics | 06-01 | Balance freshness and performance |
| CPU-only PyTorch in Docker | 08-01 | ~2GB smaller image, no GPU needed |
| Import path backend.app.* to app.* | 08-01 | Railway runs from backend/ directory |
| Health check timeout 300s | 08-01 | ML models need time to load |

## Session History

| Date | Action | Notes |
|------|--------|-------|
| 2026-01-18 | Project initialized | Codebase mapped, PROJECT.md created |
| 2026-01-18 | Roadmap created | 8 phases, 28 requirements |
| 2026-01-18 | Plan 01-01 executed | Backend structure with lifespan and CORS |
| 2026-01-18 | Plan 01-02 executed | API endpoints, schemas, 9 tests passing |
| 2026-01-18 | Plan 03-01 executed | LLM reasoning service with OpenRouter |
| 2026-01-18 | Plan 03-02 executed | LLM integration into /estimate endpoint |
| 2026-01-18 | Plan 04-01 executed | Next.js 15, shadcn/ui, Zod schemas, API client |
| 2026-01-18 | Plan 07-01 executed | Password gate auth with iron-session |
| 2026-01-18 | Plan 04-02 executed | Estimate form with 6 fields, result display |
| 2026-01-18 | Plan 05-01 executed | Supabase integration, feedback API endpoints |
| 2026-01-18 | Plan 05-02 executed | Review queue UI with TanStack Table |
| 2026-01-18 | Plan 06-01 executed | Analytics data layer with React Query hooks |
| 2026-01-18 | Plan 08-01 executed | Deployment config: Dockerfile, railway.json, vercel.json |

## Session Continuity

Last session: 2026-01-18
Stopped at: Completed 08-01-PLAN.md
Resume file: None

## Blockers

None currently.

## Notes

- Tech stack: FastAPI (Railway) + Next.js (Vercel) + Pinecone + Supabase + OpenRouter
- Frontend complete: estimate form, review queue, password gate, analytics hooks
- Backend complete: ML prediction, CBR, LLM reasoning, feedback API
- Deployment config ready: Dockerfile, railway.json, vercel.json
- Docker build test skipped (Docker not installed locally) - will validate on Railway
- Next: Phase 9 (Streaming Estimates with Cerebras)
- PostgreSQL RPC functions needed in Supabase for analytics dashboard

## Roadmap Evolution

- Phase 9 added: Streaming estimates with Cerebras fast inference

---
*State updated: 2026-01-18*
