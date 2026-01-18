# Roadmap: TOITURELV Cortex

**Created:** 2026-01-18
**Phases:** 8
**Requirements:** 28

## Phase Overview

| # | Phase | Goal | Requirements | Success Criteria |
|---|-------|------|--------------|------------------|
| 1 | FastAPI Foundation ✓ | Backend serves ML predictions | API-01, API-02, API-03, API-04 | 4 |
| 2 | Pinecone CBR ✓ | Similar case retrieval works | PIN-01, PIN-02, PIN-03 | 3 |
| 3 | LLM Reasoning ✓ | Estimates include explanations | LLM-01, LLM-02, LLM-03 | 3 |
| 4 | Estimate Form ✓ | Users can get estimates | FORM-01 to FORM-05 | 5 |
| 5 | Feedback System | Laurent can review and provide prices | DB-01 to DB-03, REVIEW-01 to REVIEW-04 | 7 |
| 6 | Analytics Dashboard | Team sees accuracy trends | DASH-01 to DASH-04 | 4 |
| 7 | Authentication ✓ | Password-protected access | AUTH-01, AUTH-02 | 2 |
| 8 | Deployment | Live on Railway + Vercel | DEPLOY-01 to DEPLOY-03 | 3 |

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

## Phase 5: Feedback System

**Goal:** Laurent can review estimates and enter his prices

**Requirements:** DB-01, DB-02, DB-03, REVIEW-01, REVIEW-02, REVIEW-03, REVIEW-04

**Success Criteria:**
1. Supabase tables created (estimates, feedback)
2. New estimates saved to database
3. Review queue shows pending estimates
4. Laurent can enter his price and mark reviewed
5. Feedback queryable for analytics

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

**Success Criteria:**
1. FastAPI running on Railway with health check passing
2. Next.js running on Vercel, connected to backend
3. All environment variables configured
4. Team can access and use the full application

**Dependencies:** All previous phases complete

---

## Milestone: v1 Complete

After Phase 8:
- Team can get AI estimates with reasoning
- Laurent can review and provide actual prices
- Analytics show model accuracy
- Feedback stored for future model improvement

**Next milestone:** Auto-update pipeline (v2)

---
*Roadmap created: 2026-01-18*
