# Project State: TOITURELV Cortex

**Last Updated:** 2026-01-19

## Project Reference

See: .planning/PROJECT.md (updated 2026-01-18)

**Core value:** Accurate price estimates with explainable reasoning
**Current focus:** Phase 8 - Deployment (In Progress)

## Progress

| Phase | Status | Plans | Progress |
|-------|--------|-------|----------|
| 1 | Complete | 2/2 | 100% |
| 2 | Complete | 2/2 | 100% |
| 3 | Complete | 2/2 | 100% |
| 4 | Complete | 2/2 | 100% |
| 5 | Complete | 2/2 | 100% |
| 6 | Complete | 2/2 | 100% |
| 7 | Complete | 1/1 | 100% |
| 8 | In Progress | 1/2 | 50% |
| 9 | Complete | 1/1 | 100% |
| 10 | Complete | 2/2 | 100% |
| 11 | Complete | 6/6 | 100% |

**Overall:** 22/24 plans complete (92%)

```
Progress: [██████████████████░░] 92%
```

## Current Phase

**Phase 8: Deployment** (In Progress)
- Goal: Deploy backend to Railway, frontend to Vercel
- Status: Config files ready, deployment execution pending

### Phase 8 In Progress
- **08-01:** Deployment configuration files (Complete)
  - Dockerfile with CPU-only PyTorch (~2GB smaller)
  - railway.json with health check and restart policy
  - vercel.json with Next.js framework config
  - Fixed all Python imports (backend.app.* to app.*)
  - Environment variable documentation (.env.example)
- **08-02:** Deployment execution (Pending)

### Phase 11 Complete
- **11-01:** Admin dashboard layout with shadcn/ui Sidebar (Complete)
  - Dark sidebar (#1A1A1A) with brick red (#8B2323) Cortex branding
  - French navigation: Estimateur, Historique, Apercu, Clients
  - Mobile responsive with collapsible sidebar
  - Root redirects to /estimateur
- **11-02:** Dashboard backend API (Complete)
  - Quotes pagination and filters
  - Customer search and detail
  - Dashboard metrics and charts endpoints
- **11-03:** Historique quote browser (Complete)
  - Paginated quote table with TanStack Table
  - 8 filter types: category, city, sqft, price, dates
  - CSV export with UTF-8 BOM for French characters
  - French locale formatting (CAD currency, fr-CA dates)
- **11-04:** Clients customer search (Complete)
  - Debounced search with useDeferredValue
  - Segment badges (VIP gold, Regular gray, New outline)
  - Quote history table with fr-CA formatting
- **11-05:** Apercu dashboard metrics (Complete)
  - 4 KPI cards: Revenue, Quotes, Margin, Active Clients
  - Revenue by year bar chart
  - Revenue by category pie chart
  - Monthly trend line chart
  - Top 10 clients ranked list
- **11-06:** Estimateur sub-views (Complete)
  - Tab navigation: Prix, Materiaux, Soumission Complete
  - Prix shows existing streaming estimate form
  - Materiaux and Complet show Phase 10 placeholders
  - Consistent amber styling for coming soon callouts

### Phase 10 Complete
- **10-01:** Material ID prediction model training
  - Multi-label classifier with OneVsRestClassifier + GradientBoosting (F1-micro 70.3%)
  - 122 per-material quantity regressors
  - 506 co-occurrence rules (confidence >= 0.7)
  - 21 feature triggers (20 chimney, 1 skylight)
  - 824 material median prices
  - Model artifacts copied to backend/app/models/
- **10-02:** Material prediction API endpoints
  - POST /estimate/materials returns predicted material IDs with quantities
  - POST /estimate/full combines price estimate + materials
  - MaterialPredictor service with lazy loading pattern
  - Response times: materials < 2s, full < 5s

### Phase 9 Complete
- **09-01:** Streaming estimates with Cerebras fast inference
  - Progressive LLM reasoning with Server-Sent Events
  - Cerebras integration for fast streaming

### Phase 6 Complete
- **06-01:** Analytics data layer with React Query and Supabase hooks
  - React Query provider with 5-min staleTime
  - Supabase browser client for RPC calls
  - Analytics hooks: useAccuracyStats, useCategoryBreakdown, useConfidenceAccuracy
  - Time period filtering (7d, 30d, all)
- **06-02:** Analytics dashboard charts (Complete)
  - Dashboard page at /dashboard route
  - Accuracy bar chart (DASH-01)
  - Confidence vs accuracy grouped chart (DASH-02)
  - Category breakdown donut chart (DASH-03)
  - Stats cards with KPIs (DASH-04)
  - Time period filter toggle

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
| GradientBoosting over RandomForest for material classifier | 10-01 | 20x smaller model (11MB vs 200MB+) |
| Threshold 0.35 for multi-label classification | 10-01 | Better F1 on imbalanced data |
| Feature trigger ratio threshold (2x) | 10-01 | Captures meaningful correlations |
| Lazy loading for material models | 10-02 | Same pattern as predictor.py |
| Extract material_id from trigger objects | 10-02 | Feature triggers are objects, not raw IDs |
| Custom sidebar over shadcn CLI | 11-01 | CLI was hanging, manual implementation works |
| Route group (admin) for layout isolation | 11-01 | Separates admin layout from login/other pages |
| Custom tooltip components per chart | 11-05 | Specific data formatting for each chart type |
| Brick red (#8B2323) for charts | 11-05 | Consistent with Cortex branding |
| Generic exportToCSV<T> for type safety | 11-03 | Works with Quote[] without Record<string, unknown> |
| keepPreviousData for pagination | 11-03 | Prevents table flicker on page changes |
| Server-side pagination with manualPagination | 11-03 | Backend handles paging for 8k+ quotes |
| useDeferredValue over custom debounce | 11-04 | Native React concurrent feature |
| Exact match for /estimateur route | 11-06 | Prevents sub-routes from highlighting root tab |
| Amber placeholder styling | 11-06 | Light amber for "coming soon" visibility |
| Client wrapper for dashboard hooks | 06-02 | dashboard-content.tsx owns all hook calls |
| Empty state messages in charts | 06-02 | Friendly UX when no data available |

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
| 2026-01-18 | Plan 10-01 executed | Material ID prediction models trained |
| 2026-01-18 | Plan 10-02 executed | Material prediction API endpoints |
| 2026-01-18 | Plan 11-01 executed | Admin dashboard layout with sidebar |
| 2026-01-18 | Plan 11-05 executed | Apercu dashboard with KPIs and charts |
| 2026-01-18 | Plan 11-03 executed | Historique quote browser with pagination |
| 2026-01-19 | Plan 11-04 executed | Clients customer search with segment badges |
| 2026-01-19 | Plan 11-06 executed | Estimateur sub-views with tab navigation |
| 2026-01-19 | Plan 06-02 executed | Analytics dashboard charts (Phase 6 complete) |

## Session Continuity

Last session: 2026-01-19
Stopped at: Completed 06-02-PLAN.md (Phase 6 complete)
Resume file: None

## Blockers

None currently.

## Notes

- Tech stack: FastAPI (Railway) + Next.js (Vercel) + Pinecone + Supabase + OpenRouter
- Frontend complete: estimate form, review queue, password gate, analytics dashboard, admin dashboard (all 4 tabs)
- Backend complete: ML prediction, CBR, LLM reasoning, feedback API, material prediction, dashboard API
- Deployment config ready: Dockerfile, railway.json, vercel.json
- Docker build test skipped (Docker not installed locally) - will validate on Railway
- Material prediction models: F1-micro 70.3%, 122 quantity regressors, 506 rules, 21 feature triggers
- Material endpoints: POST /estimate/materials, POST /estimate/full (lazy loading)
- Phase 11 Admin Dashboard complete: all 4 tabs (Estimateur, Historique, Apercu, Clients)
- Phase 6 Analytics Dashboard complete: /dashboard route with charts
- Next: Phase 8-02 (deployment execution)
- PostgreSQL RPC functions needed in Supabase for analytics dashboard

## Roadmap Evolution

- Phase 9 added: Streaming estimates with Cerebras fast inference
- Phase 10 added: Material ID Prediction Model Training (7,433 samples, multi-label classifier)
- Phase 11 added: Cortex Admin Dashboard (4-tab professional interface) - moved after material prediction

---
*State updated: 2026-01-19 (Phase 6 Plan 02 complete - Phase 6 complete with all 2 plans)*
