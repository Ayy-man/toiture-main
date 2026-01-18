# Roadmap: TOITURELV Cortex

**Created:** 2026-01-18
**Phases:** 11
**Requirements:** 32

## Phase Overview

| # | Phase | Goal | Requirements | Success Criteria |
|---|-------|------|--------------|------------------|
| 1 | FastAPI Foundation ✓ | Backend serves ML predictions | API-01, API-02, API-03, API-04 | 4 |
| 2 | Pinecone CBR ✓ | Similar case retrieval works | PIN-01, PIN-02, PIN-03 | 3 |
| 3 | LLM Reasoning ✓ | Estimates include explanations | LLM-01, LLM-02, LLM-03 | 3 |
| 4 | Estimate Form ✓ | Users can get estimates | FORM-01 to FORM-05 | 5 |
| 5 | Feedback System ✓ | Laurent can review and provide prices | DB-01 to DB-03, REVIEW-01 to REVIEW-04 | 7 |
| 6 | Analytics Dashboard | Team sees accuracy trends | DASH-01 to DASH-04 | 4 |
| 7 | Authentication ✓ | Password-protected access | AUTH-01, AUTH-02 | 2 |
| 8 | Deployment | Live on Railway + Vercel | DEPLOY-01 to DEPLOY-03 | 3 |
| 9 | Streaming Estimates | Fast estimates + streaming reasoning | PERF-01, PERF-02 | 4 |
| 10 | Material ID Prediction ✓ | Predict materials and quantities | MAT-01, MAT-02 | 2 |
| 11 | Cortex Admin Dashboard ✓ | Professional 4-tab admin interface | DASH-05 to DASH-12 | 8 |

---

## Phase 1: FastAPI Foundation ✓

**Goal:** Backend API serves ML model predictions via HTTP

**Requirements:** API-01, API-02, API-03, API-04

**Status:** Complete (2026-01-18)

**Plans:** 2 plans

Plans:
- [x] 01-01-PLAN.md — Backend structure, model loading, CORS configuration
- [x] 01-02-PLAN.md — Health and estimate endpoints with validation and tests

**Success Criteria:**
1. `GET /health` returns 200 OK
2. `POST /estimate` with valid inputs returns estimate, range, and confidence
3. Invalid inputs return appropriate error messages
4. CORS allows requests from localhost:3000

**Dependencies:** Trained model files (.pkl), config files (.json)

---

## Phase 2: Pinecone CBR ✓

**Goal:** Upload embeddings and retrieve similar historical cases

**Requirements:** PIN-01, PIN-02, PIN-03

**Status:** Complete (2026-01-18)

**Plans:** 2 plans

Plans:
- [x] 02-01-PLAN.md — Pinecone services and embedding upload script
- [x] 02-02-PLAN.md — Endpoint integration with similar cases and tests

**Success Criteria:**
1. All 8,132 embeddings uploaded to Pinecone index ✓
2. Query returns top 5 similar cases with job details ✓
3. /estimate endpoint includes similar_cases in response ✓

**Dependencies:** Phase 1 complete, Pinecone API key, cbr_embeddings.npz

---

## Phase 3: LLM Reasoning ✓

**Goal:** Estimates include human-readable explanations

**Requirements:** LLM-01, LLM-02, LLM-03

**Status:** Complete (2026-01-18)

**Plans:** 2 plans

Plans:
- [x] 03-01-PLAN.md — LLM service and OpenRouter configuration
- [x] 03-02-PLAN.md — Endpoint integration and reasoning tests

**Success Criteria:**
1. OpenRouter client configured with model selection ✓
2. /estimate response includes reasoning field ✓
3. Reasoning references similar cases and explains confidence ✓

**Dependencies:** Phase 2 complete, OpenRouter API key

---

## Phase 4: Estimate Form ✓

**Goal:** Next.js frontend where users input job details and see estimates

**Requirements:** FORM-01, FORM-02, FORM-03, FORM-04, FORM-05

**Status:** Complete (2026-01-18) — API integration testing deferred to Phase 8

**Plans:** 2 plans

Plans:
- [x] 04-01-PLAN.md — Next.js setup with shadcn/ui, Zod schemas, API client
- [x] 04-02-PLAN.md — Estimate form component with result display

**Success Criteria:**
1. Form with all 6 inputs renders correctly
2. Submit fetches from backend and displays results
3. Similar cases displayed with relevant details
4. LLM reasoning displayed clearly

**Dependencies:** Phase 3 complete (full backend API ready)

---

## Phase 5: Feedback System ✓

**Goal:** Laurent can review estimates and enter his prices

**Requirements:** DB-01, DB-02, DB-03, REVIEW-01, REVIEW-02, REVIEW-03, REVIEW-04

**Status:** Complete (2026-01-18)

**Plans:** 2 plans

Plans:
- [x] 05-01-PLAN.md — Backend Supabase integration (client, save estimates, feedback endpoints)
- [x] 05-02-PLAN.md — Frontend review queue (TanStack Table, feedback dialog, /review page)

**Success Criteria:**
1. Supabase tables created (estimates, feedback) ✓
2. New estimates saved to database ✓
3. Review queue shows pending estimates ✓
4. Laurent can enter his price and mark reviewed ✓
5. Feedback queryable for analytics ✓

**Dependencies:** Phase 4 complete, Supabase project created

---

## Phase 6: Analytics Dashboard

**Goal:** Team can see how accurate the AI is becoming

**Requirements:** DASH-01, DASH-02, DASH-03, DASH-04

**Plans:** 2 plans

Plans:
- [ ] 06-01-PLAN.md — Analytics infrastructure (dependencies, Supabase client, React Query, hooks)
- [ ] 06-02-PLAN.md — Dashboard UI (charts, stats cards, time filter, /dashboard page)

**Success Criteria:**
1. Accuracy chart shows % within 10%/20% of Laurent's prices
2. Confidence correlation visible (high confidence = more accurate?)
3. Category breakdown shows estimate distribution
4. Time filter works (last 7d, 30d, all time)

**Dependencies:** Phase 5 complete (feedback data exists)

---

## Phase 7: Authentication ✓

**Goal:** Only authorized users can access the app

**Requirements:** AUTH-01, AUTH-02

**Status:** Complete (2026-01-18)

**Plans:** 1 plan

Plans:
- [x] 07-01-PLAN.md — Password gate with iron-session, login page, middleware protection

**Success Criteria:**
1. Unauthenticated users see password prompt ✓
2. Correct password grants access to all features ✓
3. Password stored in environment variable ✓

**Dependencies:** Phase 4 complete (frontend exists)

---

## Phase 8: Deployment

**Goal:** App live and accessible to team

**Requirements:** DEPLOY-01, DEPLOY-02, DEPLOY-03

**Plans:** 2 plans

Plans:
- [ ] 08-01-PLAN.md — Deployment configuration (Dockerfile, railway.json, vercel.json, import fixes)
- [ ] 08-02-PLAN.md — Deploy to platforms (Railway backend, Vercel frontend, env vars, verification)

**Success Criteria:**
1. FastAPI running on Railway with health check passing
2. Next.js running on Vercel, connected to backend
3. All environment variables configured
4. Team can access and use the full application

**Dependencies:** All previous phases complete

---

## Phase 9: Streaming Estimates

**Goal:** Fast estimates with progressive LLM reasoning via streaming

**Requirements:** PERF-01, PERF-02

**Plans:** 1 plan

Plans:
- [ ] 09-01-PLAN.md — Streaming endpoint with Cerebras integration

**Success Criteria:**
1. Estimate + similar cases return in <2s
2. LLM reasoning streams in progressively after estimate
3. Cerebras API integrated for fast inference
4. Frontend displays streaming reasoning with loading state

**Dependencies:** Phase 8 complete (deployment working)

---

## Phase 10: Material ID Prediction ✓

**Goal:** Train multi-label classifier for material ID selection and quantity prediction

**Requirements:** MAT-01, MAT-02

**Status:** Complete (2026-01-19)

**Plans:** 2 plans

Plans:
- [x] 10-01-PLAN.md — Material prediction model training (F1-micro 70.3%, 122 regressors)
- [x] 10-02-PLAN.md — Material prediction API endpoints (/estimate/materials, /estimate/full)

**Success Criteria:**
1. Material ID selection F1-micro >= 70% ✓ (achieved 70.3%)
2. Quantity MAPE <= 30% for predictable materials ✓
3. POST /estimate/materials returns predicted materials ✓
4. POST /estimate/full combines price + materials ✓
5. Models load lazily on first request ✓

**Dependencies:** Phase 1 complete (backend structure)

---

## Phase 11: Cortex Admin Dashboard ✓

**Goal:** Build professional 4-tab admin dashboard replacing simple form

**Requirements:** DASH-05, DASH-06, DASH-07, DASH-08, DASH-09, DASH-10, DASH-11, DASH-12

**Status:** Complete (2026-01-19)

**Plans:** 6 plans

Plans:
- [x] 11-01-PLAN.md — Sidebar layout, navigation, French i18n, CSS variables
- [x] 11-02-PLAN.md — Backend endpoints for quotes, customers, dashboard metrics
- [x] 11-03-PLAN.md — Historique tab with paginated quote browser and CSV export
- [x] 11-04-PLAN.md — Clients tab with customer search and detail view
- [x] 11-05-PLAN.md — Aperçu tab with KPI cards and charts
- [x] 11-06-PLAN.md — Estimateur tab with 3 sub-views (Prix, Matériaux, Complet)

**Success Criteria:**
1. 4 tabs functional: Estimateur, Historique, Aperçu, Clients ✓
2. Estimateur returns results in <3 seconds with streaming ✓
3. Quote browser handles 8,293 records with pagination ✓
4. Customer search returns results in <1 second ✓
5. Dashboard charts render with real data ✓
6. French labels throughout (Quebec French) ✓
7. Dark sidebar with brick red accents (#8B2323) ✓
8. Mobile-responsive sidebar collapses ✓

**Dependencies:** Phase 10 complete (material prediction model ready)

---

## Milestone: v1 Complete

After Phase 9:
- Team can get AI estimates with reasoning
- Laurent can review and provide actual prices
- Analytics show model accuracy
- Feedback stored for future model improvement
- **Fast streaming responses with Cerebras**

**Next milestone:** Auto-update pipeline (v2)

---
*Roadmap created: 2026-01-18*
