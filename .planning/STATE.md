# Project State: TOITURELV Cortex

**Last Updated:** 2026-02-09

## Project Reference

See: .planning/PROJECT.md (updated 2026-01-18)

**Core value:** Accurate price estimates with explainable reasoning
**Current focus:** Sprint Phases 19-25 — Laurent Sprint Delivery (Deadline: Feb 16, 2026)

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
| 13 | Complete | 4/4 | 100% |
| 14 | Complete | 3/3 | 100% |
| 15 | Complete | 1/1 | 100% |
| 16 | Complete | 1/1 | 100% |
| 19 | Complete | 3/3 | 100% |
| 20 | Complete | 3/3 | 100% |
| 21 | Complete | 3/3 | 100% |
| 22 | Complete | 2/2 | 100% |

**Overall:** 42/44 plans complete for v1 + sprint (95%)

```
v1 Progress:     [██████████████████░░] 95%
Sprint Progress: [████████████████████] 100% (19-22)
```

## Current Sprint — Deadline: February 16, 2026

| Phase | Name | Sprint Deadline | Status |
|-------|------|-----------------|--------|
| 19 | Data Quality & Labeling Fixes | Feb 11 | Complete (3/3) |
| 20 | Materials Database & Import | Feb 10-12 | Complete (3/3) |
| 21 | Complexity System Rebuild | Feb 11 | Complete (3/3) |
| 22 | New Estimation Input Fields | Feb 12 | Complete (2/2) |
| 23 | Submission Workflow & Editing | Feb 13 | Planned |
| 24 | Export, Send & Red Flags | Feb 13-14 | Planned |
| 25 | UI Polish & Dark Mode | Feb 13 | Planned |

**Business logic gaps (need Laurent/Amin input):**
- Complexity: base time values per job type, time multipliers per tier
- Employee count: suggestion rules (job type × complexity → crew)
- Geographic zones: Google Maps API budget approval needed
- Premium client: daily surcharge amounts per level
- Duration: half-day transport cost rules, multi-day discount

**Out of scope for this codebase (separate projects):**
- AI Agent (inbound call handling)
- Solar calculation tool
- GoHighLevel integration
- CCube ↔ QuickBooks invoice flow

### Phase 16 Complete
- **16-01:** I18n language toggle implementation (Complete)
  - English translations (en.ts) matching fr.ts structure
  - LanguageContext with LanguageProvider and useLanguage hook
  - Barrel export in index.ts for clean imports
  - LanguageProvider wrapping admin layout
  - EN/FR toggle in sidebar footer
  - All 15 components updated to use useLanguage hook
  - localStorage persistence with "cortex-locale" key
  - Default language is French (Quebec market)

### Phase 15 Complete
- **15-01:** Frontend design overhaul with Lyra preset (Complete)
  - Lyra theme CSS variables with zinc palette and large radius
  - JetBrains Mono font added
  - Sidebar rewritten with explicit width control (16rem → 4rem)
  - Full quote form redesigned with 3 card sections
  - Complexity presets with pill-style buttons and progress bar
  - Button and slider components polished

### Phase 14 Complete
- **14-01:** TypeScript types, API client, complexity presets (Complete)
  - HybridQuoteRequest/Response types matching backend
  - Zod schema with range validation
  - submitHybridQuote() API client
  - ComplexityPresets component with 3 presets and 6 sliders
- **14-02:** Invoice-style quote result display (Complete)
  - QuoteResult component with invoice-style layout
  - Work items with labor hours display
  - Materials/labor/total summary section
  - Collapsible reasoning section with markdown
  - Confidence warning banner when < 50%
- **14-03:** PDF export with client-facing template (Complete)
  - @react-pdf/renderer integration
  - QuotePDFDocument template (excludes hours, confidence, reasoning)
  - QuoteActions component with export button
  - French locale formatting and filename pattern

### Phase 13 Complete
**Phase 13: Hybrid Quote Generation** (Complete)
- Goal: ML + CBR hybrid quote generation with LLM merger
- Status: All plans complete - endpoint ready for frontend integration

### Phase 13 Complete
- **13-01:** Pydantic schemas for hybrid quote (Complete)
  - HybridQuoteRequest with 6 complexity factors validation
  - HybridQuoteOutput for LLM tool calling (model_json_schema() ready)
  - HybridQuoteResponse with metadata and review flags
  - WorkItem, MaterialLineItem, PricingTier supporting models
  - Three-tier pricing enforcement (Basic/Standard/Premium)
- **13-02:** Confidence scorer service (Complete)
  - calculate_confidence() with weighted formula (30% CBR, 40% agreement, 30% completeness)
  - calculate_data_completeness() for input field presence scoring
  - calculate_material_agreement() using Jaccard similarity
  - ML-only fallback always flags for review
  - Confidence < 0.5 triggers needs_review flag
- **13-03:** Hybrid quote orchestrator service (Complete)
  - generate_hybrid_quote() async orchestrator
  - Parallel CBR + ML execution with asyncio.gather()
  - LLM merger using existing OpenRouter client
  - JSON parsing with regex fallback + Pydantic validation
  - Graceful fallback: CBR-only, ML-only, LLM failure cases
  - Processing time tracking for <5s SLA monitoring
- **13-04:** Hybrid quote endpoint (Complete)
  - POST /estimate/hybrid endpoint accepting HybridQuoteRequest
  - Service call detection routing (material_lines=0 or sqft<100)
  - Three-tier pricing for service calls
  - Full hybrid pipeline for normal jobs
  - Error handling: 503 for total failure, 500 for other errors

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
| model_validator for complexity_aggregate | 13-01 | Runs after all fields populated for cross-field validation |
| 5% tolerance for complexity sum | 13-01 | Handles frontend rounding differences |
| Three-tier pricing at model level | 13-01 | Enforces Basic/Standard/Premium in schema |
| Source tracking Literal types | 13-01 | Transparency for CBR/ML/MERGED origin |
| 30/40/30 confidence weights | 13-02 | CBR similarity, ML-CBR agreement, data completeness |
| Review threshold at 0.5 | 13-02 | Flags low confidence for Laurent's manual review |
| ML-only always needs review | 13-02 | No CBR validation available |
| Reuse OpenRouter client via get_client() | 13-03 | No new API configuration needed |
| JSON-in-prompt with regex extraction | 13-03 | More robust than tool calling for LLM merger |
| asyncio.gather with return_exceptions | 13-03 | Graceful parallel execution with failure handling |
| Fallback tier percentages (-15%/base/+18%) | 13-03 | Industry standard pricing spread |
| Service call detection: material_lines=0 OR sqft<100 | 13-04 | Routes labor-only jobs to fast path |
| Service call tier multipliers (0.9x/1.0x/1.2x) | 13-04 | Industry service call pricing pattern |
| 503 for CBR+ML total failure | 13-04 | Service unavailable semantics |
| Standard tier for default invoice display | 14-02 | Middle tier suitable for internal quote view |
| fr-CA locale for CAD formatting | 14-02 | Quebec client base expects space thousands separator |
| Collapsible reasoning (default collapsed) | 14-02 | LLM reasoning valuable but secondary to invoice |
| Controller wrapper for ComplexityPresets | 14-02 | Clean integration with react-hook-form for 6 factors |
| Confidence warning threshold < 50% | 14-02 | Matches backend needs_review flag |
| @react-pdf/renderer for client-side PDF | 14-03 | No server roundtrip, faster UX |
| PDF excludes labor hours | 14-03 | Client-facing quotes hide internal details |
| Standard tier for PDF display | 14-03 | Middle tier represents typical pricing |
| Revenue → Quote Value terminology | 19-01 | Data represents quoted amounts, not invoiced revenue |
| Disclaimer banner above charts | 19-01 | Clarifies quoted vs invoiced revenue distinction |
| Chart titles via i18n keys | 19-01 | Enables proper EN/FR translation for all chart titles |
| JSON config for complexity business rules | 21-01 | Hour values externalized for no-code adjustments by Laurent |
| Module-level config caching for tiers | 21-01 | Same pattern as predictor.py, loaded once at import |
| Backward compatibility for old complexity | 21-01 | Old 6-slider format (0-56) still works via Optional fields |
| Additive labor hour formula | 21-01 | total = base + tier + factors (not percentage multipliers) |
| Placeholder hour values in config | 21-01 | All values need Laurent validation before production |
| pandas for CSV processing | 20-01 | Robust UTF-8 BOM handling and data validation |
| RapidFuzz token_sort_ratio | 20-01 | Better for materials with reordered words |
| ILIKE for fuzzy material search | 20-02 | Case-insensitive substring matching, efficient for Postgres |
| Exclude labor items from material search | 20-02 | Material search should only return materials (item_type filter) |
| DFS clustering for duplicates | 20-01 | Captures transitive relationships in duplicate groups |
| Flag both items in duplicate pairs | 20-01 | Manual review needed to determine canonical item |
| Data quality flag as TEXT column | 19-02 | Flexible tagging strategy for multiple quality issue types |
| Service Call exclusion from sqft compliance | 19-02 | Service calls legitimately have no sqft requirement |
| Compliance alert threshold 80% | 19-02 | Industry-standard compliance threshold for data quality |
| All Phase 22 fields Optional with None defaults | 22-01 | Backward compatibility for existing quotes |
| Bilingual equipment config pattern | 22-01 | name_fr/name_en fields enable i18n without code changes |
| Equipment costs placeholder at $25/day | 22-01 | Awaiting real rental costs from Laurent |
| Enum field validators for Phase 22 | 22-01 | duration_type, geographic_zone, premium_client_level, supply_chain_risk |
| Equipment options hardcoded in component | 22-02 | Avoids async loading complexity, bilingual via locale check |
| Live crew total calculation with form.watch() | 22-02 | Derived value pattern for totalCrew display |
| Conditional rendering for multi-day day picker | 22-02 | Day picker only renders when duration_type === 'multi_day' |
| Conditional supply chain warning | 22-02 | Warning only shows for extended/import risk levels |
| Backward compatible API submission | 22-02 | Only send non-default values to backend (undefined for omitted fields) |

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
| 2026-01-31 | Plan 13-01 executed | Hybrid quote Pydantic schemas |
| 2026-01-31 | Plan 13-02 executed | Confidence scorer service with weighted formula |
| 2026-01-31 | Plan 13-03 executed | Hybrid quote orchestrator with async CBR+ML+LLM |
| 2026-01-31 | Plan 13-04 executed | Hybrid quote endpoint with service call detection |
| 2026-02-01 | Plan 14-01 executed | TypeScript types, API client, complexity presets |
| 2026-02-01 | Plan 14-02 executed | Invoice-style quote display and full form integration |
| 2026-02-01 | Plan 14-03 executed | PDF export with client-facing template |
| 2026-02-01 | Plan 15-01 executed | Frontend design overhaul with Lyra preset |
| 2026-02-01 | Plan 16-01 executed | I18n language toggle with EN/FR persistence |
| 2026-02-09 | Plan 19-01 executed | Revenue label corrections - apercu dashboard |
| 2026-02-09 | Plan 21-01 executed | Tier-based complexity config and calculator service |
| 2026-02-09 | Plan 20-01 executed | Materials database import scripts and SQL DDL |
| 2026-02-09 | Plan 21-02 executed | TierSelector and FactorChecklist UI components |
| 2026-02-09 | Plan 20-02 executed | Materials search and categories API endpoints |
| 2026-02-09 | Plan 20-03 executed | Material selector UI with searchable multi-select |
| 2026-02-09 | Plan 19-02 executed | Data quality flags and compliance endpoint |
| 2026-02-09 | Plan 19-03 executed | Compliance monitoring UI and conditional sqft validation |
| 2026-02-09 | Plan 21-03 executed | Full quote form integration with tier selector and backend orchestrator |
| 2026-02-09 | Plan 22-01 executed | Schema fields, equipment config, i18n keys, RadioGroup component |
| 2026-02-09 | Plan 22-02 executed | 3 new Card sections in full-quote form (Crew & Duration, Location & Client, Equipment & Supply Chain) |

## Session Continuity

Last session: 2026-02-09
Stopped at: Phase 22 complete (2/2 plans) — next is Phase 23 (Submission Workflow & Editing)
Resume file: None

## Blockers

1. ~~**Materials XLS file**~~: ✅ Available at `cortex-data/LV Material List.csv`
2. **Business logic rules**: Complexity time multipliers, crew suggestion rules, premium surcharges — need from Laurent
3. **Google Maps API budget**: Geographic zone auto-calculation requires API approval from Amin
4. **Equipment rental costs**: Phase 22-01 created equipment config with $25/day placeholders — need real costs from Laurent

## Notes

- Tech stack: FastAPI (Railway) + Next.js (Vercel) + Pinecone + Supabase + OpenRouter
- Frontend complete: estimate form, review queue, password gate, analytics dashboard, admin dashboard (all 4 tabs)
- Backend complete: ML prediction, CBR, LLM reasoning, feedback API, material prediction, dashboard API, hybrid quote endpoint
- Deployment config ready: Dockerfile, railway.json, vercel.json
- Docker build test skipped (Docker not installed locally) - will validate on Railway
- Material prediction models: F1-micro 70.3%, 122 quantity regressors, 506 rules, 21 feature triggers
- Material endpoints: POST /estimate/materials, POST /estimate/full (lazy loading)
- Phase 11 Admin Dashboard complete: all 4 tabs (Estimateur, Historique, Apercu, Clients)
- Phase 6 Analytics Dashboard complete: /dashboard route with charts
- Phase 13 Hybrid Quote complete: POST /estimate/hybrid with service call detection and LLM merger
- Phase 14 Full Quote Frontend complete: ComplexityPresets, QuoteResult, PDF export
- Phase 16 I18n complete: EN/FR toggle with localStorage persistence
- Phase 19-01 complete: Revenue labels corrected to "Quote Value" with disclaimer banner
- Phase 20-01 complete: Materials import scripts (SQL DDL, CSV import, fuzzy deduplication)
- Phase 20-02 complete: Materials search API (GET /materials/search, /materials/categories)
- Phase 20-03 complete: MaterialSelector component (searchable multi-select, category filter, custom materials)
- Phase 21-01 complete: Tier-based complexity config (6 tiers, 8 factors) and calculator service
- Phase 21-02 complete: TierSelector and FactorChecklist UI components
- Phase 21-03 complete: Full quote form with TierSelector + FactorChecklist, backend orchestrator integration
- Phase 19-02 complete: Data quality flags, compliance endpoint (GET /dashboard/compliance)
- Phase 19-03 complete: Conditional sqft validation, estimator dropdown, compliance UI on Apercu
- Phase 19 complete (3/3 plans) - Data quality, labeling fixes, compliance monitoring
- Phase 20 complete (3/3 plans) - Materials database import, search API, selector UI
- Phase 21 complete (3/3 plans) - Complexity system fully rebuilt with 6-tier 0-100 scale
- Phase 22-01 complete - Schema fields, equipment config, i18n keys, RadioGroup for 7 new field groups
- Phase 22-02 complete - 3 new Card sections in full-quote form with all 6 field groups wired to API
- Next: Phase 22-03 (backend integration), then Phases 23-25
- PostgreSQL RPC functions needed in Supabase for analytics dashboard

## Roadmap Evolution

- Phase 9 added: Streaming estimates with Cerebras fast inference
- Phase 10 added: Material ID Prediction Model Training (7,433 samples, multi-label classifier)
- Phase 11 added: Cortex Admin Dashboard (4-tab professional interface) - moved after material prediction
- Phase 13 added: Hybrid Quote Generation (ML + CBR + LLM merger for full quote generation)
- Phase 15 added: Frontend Design Overhaul (shadcn Lyra preset, fix broken UI/UX)
- Phase 16 added: I18n Language Toggle (site-wide EN/FR toggle with persistence)
- Phase 17 added: Production Fixes (fix issues after deploy)
- Phase 18 added: Feedback Review Page (Retours nav item with insights and analytics)
- **Phase 19 added:** Data Quality & Labeling Fixes (revenue relabeling, 2022 flags, sqft mandatory)
- **Phase 20 added:** Materials Database & Import (672-item XLS, searchable selector)
- **Phase 21 added:** Complexity System Rebuild (6-tier 0-100, time-based)
- **Phase 22 added:** New Estimation Input Fields (crew, duration, zone, premium, access, tools, supply chain)
- **Phase 23 added:** Submission Workflow & Editing (editable quotes, approval, notes, upsells)
- **Phase 24 added:** Export, Send & Red Flags (DOCX, send options, warning system)
- **Phase 25 added:** UI Polish & Dark Mode (dark toggle, FR/EN fixes, branding)

---
*State updated: 2026-02-09 (Sprint phases 19-25 added — Deadline Feb 16)*
