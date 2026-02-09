# Roadmap: TOITURELV Cortex

**Created:** 2026-01-18
**Updated:** 2026-02-09
**Phases:** 25
**Requirements:** 51

## Phase Overview

| # | Phase | Goal | Requirements | Success Criteria |
|---|-------|------|--------------|------------------|
| 1 | FastAPI Foundation ✓ | Backend serves ML predictions | API-01, API-02, API-03, API-04 | 4 |
| 2 | Pinecone CBR ✓ | Similar case retrieval works | PIN-01, PIN-02, PIN-03 | 3 |
| 3 | LLM Reasoning ✓ | Estimates include explanations | LLM-01, LLM-02, LLM-03 | 3 |
| 4 | Estimate Form ✓ | Users can get estimates | FORM-01 to FORM-05 | 5 |
| 5 | Feedback System ✓ | Laurent can review and provide prices | DB-01 to DB-03, REVIEW-01 to REVIEW-04 | 7 |
| 6 | Analytics Dashboard ✓ | Team sees accuracy trends | DASH-01 to DASH-04 | 4 |
| 7 | Authentication ✓ | Password-protected access | AUTH-01, AUTH-02 | 2 |
| 8 | Deployment | Live on Railway + Vercel | DEPLOY-01 to DEPLOY-03 | 3 |
| 9 | Streaming Estimates | Fast estimates + streaming reasoning | PERF-01, PERF-02 | 4 |
| 10 | Material ID Prediction ✓ | Predict materials and quantities | MAT-01, MAT-02 | 2 |
| 11 | Cortex Admin Dashboard ✓ | Professional 4-tab admin interface | DASH-05 to DASH-12 | 8 |
| 12 | ~~Laurent Feedback Fixes~~ | SUPERSEDED → Phase 19 + 21 | — | — |
| 13 | Hybrid Quote Generation ✓ | Full quote with CBR + ML + LLM merger | HQG-01 to HQG-05 | 7 |
| 14 | Full Quote Frontend ✓ | Frontend with presets, invoice display, PDF | FQ-01 to FQ-05 | 6 |
| 15 | Frontend Design Overhaul | Modern UI with shadcn Lyra preset | UI-01 to UI-05 | 5 |
| 16 | I18n Language Toggle | Site-wide EN/FR toggle with persistence | I18N-01 to I18N-04 | 4 |
| 17 | Production Fixes | Fix production issues after deploy | PROD-01 to PROD-07 | 7 |
| 18 | Feedback Review Page | Retours page with insights and analytics | FB-01 to FB-04 | 4 |
| 19 | Data Quality & Labeling Fixes | Fix revenue labels, flag 2022 data, sqft mandatory | DQ-01 to DQ-03 | 5 |
| 20 | Materials Database & Import | Import 672-item XLS, build searchable selector | MAT-03 to MAT-06 | 7 |
| 21 | Complexity System Rebuild | 6-tier (0-100) time-based system for roofers | CX-01 to CX-04 | 8 |
| 22 | New Estimation Input Fields | Crew, duration, zone, premium, access, tools, supply chain | FIELD-01 to FIELD-07 | 9 |
| 23 | Submission Workflow & Editing | Editable quotes, approval workflow, notes, upsells | SUB-01 to SUB-05 | 10 |
| 24 | Export, Send & Red Flags | DOCX export, send options, warning system | EXP-01 to EXP-04 | 5 |
| 25 | UI Polish & Dark Mode | Dark mode toggle, FR/EN fixes, LV branding | UI-06 to UI-08 | 7 |

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

## Phase 6: Analytics Dashboard ✓

**Goal:** Team can see how accurate the AI is becoming

**Requirements:** DASH-01, DASH-02, DASH-03, DASH-04

**Status:** Complete (2026-01-19)

**Plans:** 2 plans

Plans:
- [x] 06-01-PLAN.md — Analytics infrastructure (dependencies, Supabase client, React Query, hooks)
- [x] 06-02-PLAN.md — Dashboard UI (charts, stats cards, time filter, /dashboard page)

**Success Criteria:**
1. Accuracy chart shows % within 10%/20% of Laurent's prices ✓
2. Confidence correlation visible (high confidence = more accurate?) ✓
3. Category breakdown shows estimate distribution ✓
4. Time filter works (last 7d, 30d, all time) ✓

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

## Phase 12: Laurent Feedback Fixes — SUPERSEDED

**Status:** Superseded (2026-02-09)

**Disposition:**
- 12-01 (2022 data flags) → **Merged into Phase 19**
- 12-02 (Revenue relabeling) → **Merged into Phase 19**
- 12-03 (Sqft compliance) → **Merged into Phase 19**
- 12-04 (Complexity 0-56) → **Superseded by Phase 21** (tier-based 0-100)
- 12-05 (3 pricing tiers) → **Already complete** (Phase 13/14)

---

## Phase 13: Hybrid Quote Generation

**Goal:** Full quote generation using CBR + ML + LLM merger architecture

**Requirements:** HQG-01, HQG-02, HQG-03, HQG-04, HQG-05

**Status:** Complete (2026-02-01)

**Plans:** 4 plans

Plans:
- [x] 13-01-PLAN.md — Pydantic schemas for hybrid quote request, response, and LLM structured outputs
- [x] 13-02-PLAN.md — Confidence scorer service (CBR similarity + ML-CBR agreement + data completeness)
- [x] 13-03-PLAN.md — Hybrid quote orchestrator (parallel CBR+ML, OpenRouter LLM merger)
- [x] 13-04-PLAN.md — POST /estimate/hybrid endpoint with service call detection

**Success Criteria:**
1. CBR retrieves similar jobs with full line-item breakdown
2. ML predicts material IDs, quantities, work items, and labor
3. LLM merges CBR + ML outputs, resolving conflicts
4. Output includes work items, material IDs, quantities, labor hours, total price
5. Confidence scoring reflects CBR/ML agreement
6. Three-tier pricing (Basic/Standard/Premium) generated
7. Response time <5 seconds for full quote

**Dependencies:** Phase 10 complete (material prediction), Phase 2 (CBR), Phase 3 (LLM)

---

## Phase 14: Full Quote Frontend Integration ✓

**Goal:** Wire /estimate/hybrid endpoint to frontend with complexity presets, invoice-style output, and PDF export

**Requirements:** FQ-01, FQ-02, FQ-03, FQ-04, FQ-05

**Status:** Complete (2026-02-01)

**Plans:** 3 plans

Plans:
- [x] 14-01-PLAN.md — TypeScript types, API client, and complexity presets component
- [x] 14-02-PLAN.md — Invoice-style quote result display and form integration
- [x] 14-03-PLAN.md — PDF export with client-facing template

**Success Criteria:**
1. Form with complexity presets (Simple/Modere/Complexe) works
2. 6-factor override sliders function correctly
3. Invoice-style result displays work items and totals
4. Confidence warning shows when < 50%
5. PDF export generates client-facing document (no hours)
6. French labels throughout (Quebec French)

**Dependencies:** Phase 13 complete (hybrid quote endpoint)

**Design Doc:** docs/plans/2026-02-01-full-quote-frontend-design.md

---

## Phase 15: Frontend Design Overhaul ✓

**Goal:** Modern, polished UI using shadcn Lyra preset with fixed layout issues

**Requirements:** UI-01, UI-02, UI-03, UI-04, UI-05

**Status:** Complete (2026-02-01)

**Plans:** 1 plan

Plans:
- [x] 15-01-PLAN.md — Lyra theme, sidebar fix, form redesign, component polish

**Success Criteria:**
1. shadcn Lyra preset applied with JetBrains Mono font and large radius
2. Sidebar layout fixed - no overlapping text, proper spacing
3. Form inputs have proper visual hierarchy and polish
4. Complexity control redesigned (not broken slider)
5. Consistent dark theme with proper contrast

**Dependencies:** Phase 14 complete

**Preset Config:** `pnpm dlx shadcn@latest create --preset "https://ui.shadcn.com/init?base=base&style=lyra&baseColor=zinc&theme=zinc&iconLibrary=hugeicons&font=jetbrains-mono&menuAccent=bold&menuColor=default&radius=large&template=next&rtl=false" --template next`

---

## Phase 16: I18n Language Toggle ✓

**Goal:** Site-wide English/French language toggle with persistent preference

**Requirements:** I18N-01, I18N-02, I18N-03, I18N-04

**Status:** Complete (2026-02-01)

**Plans:** 1 plan

Plans:
- [x] 16-01-PLAN.md — I18n infrastructure, language toggle, component updates

**Success Criteria:**
1. Language toggle visible in header/sidebar
2. All UI labels switch between English and French
3. Language preference persists across sessions (localStorage/cookie)
4. Default language is French (Quebec market)
5. All existing fr.ts translations used, en.ts translations added

**Dependencies:** Phase 15 complete (frontend design)

---

## Phase 17: Production Fixes

**Goal:** Fix production issues discovered after deployment

**Requirements:** PROD-01, PROD-02, PROD-03, PROD-04, PROD-05, PROD-06, PROD-07

**Status:** In Progress (2026-02-05)

**Plans:** 7 plans

Plans:
- [x] 17-01-PLAN.md — Mixed content fix (HTTPS API URL)
- [x] 17-02-PLAN.md — Dashboard 500 errors (column fixes)
- [ ] 17-03-PLAN.md — Verify Historique/Clients after deploy
- [x] 17-04-PLAN.md — Matériaux tab real prediction form
- [x] 17-05-PLAN.md — Similar cases sqft range filter
- [x] 17-06-PLAN.md — Feedback system quick endpoint
- [ ] 17-07-PLAN.md — French translations completion

**Success Criteria:**
1. No mixed content errors in production
2. Dashboard endpoints return valid data
3. Historique and Clients pages work
4. Matériaux tab shows real predictions
5. All UI text in French when FR selected

**Dependencies:** Phase 16 complete, deployment active

---

## Phase 18: Feedback Review Page

**Goal:** Dedicated page for reviewing and analyzing feedback ("Retours")

**Requirements:** FB-01, FB-02, FB-03, FB-04

**Status:** Planned (2026-02-05)

**Plans:** 0 plans

Plans:
- [ ] TBD (run /gsd:plan-phase 18 to break down)

**Success Criteria:**
1. "Retours" nav item in sidebar between Clients and bottom
2. Summary cards: total, approval rate, avg gap, weekly count
3. Filterable table with feedback entries
4. Expandable rows showing full estimate details
5. Insights section with category analysis
6. Backend endpoints: GET /feedback, GET /feedback/summary
7. Empty state when no feedback exists
8. All labels in French

**Dependencies:** Phase 17 complete (feedback system working)

**Details:**
- Summary cards: Total retours, Taux d'approbation, Écart moyen, Retours cette semaine
- Filters: type (Tous/Positif/Négatif), category, date range, sort
- Table columns: Date, Catégorie, Superficie, Prix estimé, Vrai prix, Écart, Verdict, Raison
- Expandable row: input params, materials, similar cases, full reason, reconstruct button
- Insights: sous-estimées categories, surestimées categories, missing materials

---

## Phase 19: Data Quality & Labeling Fixes

**Goal:** Fix critical data quality issues and misleading labels identified by Laurent (consolidates former Phase 12)

**Sprint Deadline:** Feb 11, 2026

**Requirements:** DQ-01, DQ-02, DQ-03, DQ-04, DQ-05 (formerly LF-01 to LF-03)

**Status:** Planned (2026-02-09)

**Plans:** 3 plans

Plans:
- [ ] 19-01-PLAN.md — Revenue label replacement + chart disclaimers (DQ-01, DQ-02)
- [ ] 19-02-PLAN.md — 2022 data quality flag + backend compliance endpoint (DQ-03, DQ-05 backend)
- [ ] 19-03-PLAN.md — Sqft required field + estimator dropdown + compliance dashboard (DQ-04, DQ-05 frontend)

**Success Criteria:**
1. ALL instances of "Revenue"/"Revenu" changed to "Total Quote Value"/"Valeur totale des soumissions" across frontend + backend
2. Disclaimer added to financial charts: "These are quoted amounts, not invoiced revenue"
3. 2022 corrupted labor quotes (1,512 records) flagged with data_quality_flag in database
4. Flagged 2022 data excluded from labor cost training
5. Square footage field is required on estimate forms (exception for service calls)
6. Compliance dashboard tracks sqft data entry by estimator
7. Alert triggers if sqft compliance drops below 80%

**Dependencies:** None — can start immediately

**Source:** Laurent meeting January 21, 2026 + Sprint plan February 9, 2026 (consolidates Phase 12)

---

## Phase 20: Materials Database & Import

**Goal:** Import Laurent's 672-item materials XLS into platform and build searchable material selector UI

**Sprint Deadline:** Feb 10-12, 2026

**Requirements:** MAT-03, MAT-04, MAT-05, MAT-06

**Status:** Planned (2026-02-09)

**Plans:** 3 plans

Plans:
- [ ] 20-01-PLAN.md — Supabase materials table DDL + CSV import script + deduplication report
- [ ] 20-02-PLAN.md — Materials search API endpoints (GET /materials/search, GET /materials/categories)
- [ ] 20-03-PLAN.md — Frontend material selector UI (searchable multi-select, custom material entry, auto line-count)

**Success Criteria:**
1. Materials table created in Supabase with fields: code, name, unit_price, unit_of_measure, category
2. All 1,152 items from Laurent's CSV parsed and imported (~813 clean, ~259 flagged for review)
3. Materials mapped to existing CCube extraction data by material code
4. Deduplication check run, similar items flagged for Amin/Laurent review
5. Material selector UI: searchable dropdown, user picks materials, system auto-counts lines
6. "Add custom material" option for items not in database
7. Manual "number of material lines" input replaced with selector

**Dependencies:** Laurent's materials file — available at `cortex-data/LV Material List.csv`

**Source:** Sprint plan February 9, 2026 — Section 3.4

---

## Phase 21: Complexity System Rebuild

**Goal:** Replace current 6-factor slider (0-56) with tier-based system (0-100) that maps to real-world scenarios roofers understand

**Sprint Deadline:** Feb 11, 2026

**Requirements:** CX-01, CX-02, CX-03, CX-04

**Status:** Planned (2026-02-09)

**Plans:** 0 plans

Plans:
- [ ] TBD (run /gsd:plan-phase 21 to break down)

**Success Criteria:**
1. 6 named tiers (0-100) with descriptions: site, roof, access for each tier
2. Tier selector (dropdown or visual) replaces current presets + sliders
3. Each tier auto-populates a time multiplier (business logic from Laurent needed)
4. Factor checklist available: roof pitch, access difficulty, demolition, penetrations, security, material removal, roof sections, previous layers
5. Each factor adds estimated hours to base_time (time-based, not percentage-based)
6. Conservative crew default: system assumes average skill workers, never best
7. Manual override allowed upward only (can add time, system never suggests less)
8. Formula: total_labor_hours = base_time + complexity_extra_hours; labor_cost = total_labor_hours × crew_cost_per_hour

**Dependencies:** Phase 19 (data quality fixes), Laurent provides time multipliers per tier

**Source:** Sprint plan February 9, 2026 — Section 3.1 + Laurent Feb 5 meeting

**Business Logic Gap:** Laurent needs to provide:
- Base time values per job type (e.g., "1500 sqft flat roof = X base hours")
- Time multipliers per tier
- Hours added per factor (e.g., "no crane = +Y hours")

---

## Phase 22: New Estimation Input Fields

**Goal:** Add all missing form fields that estimators need to generate accurate quotes

**Sprint Deadline:** Feb 12, 2026

**Requirements:** FIELD-01 to FIELD-07

**Status:** Planned (2026-02-09)

**Plans:** 0 plans

Plans:
- [ ] TBD (run /gsd:plan-phase 22 to break down)

**Success Criteria:**
1. **Employee count**: 3 number inputs (compagnons/apprentis/manoeuvres) with total crew display
2. **Duration**: Radio buttons — half-day (≤5h) / full-day (≤10h) / multi-day (N days picker)
3. **Geographic zone**: 5 zones (core/secondary/north premium/extended/red flag) with auto-suggest price adjustment
4. **Premium client level**: 4 options — Standard / Premium 1 (daily cleanup) / Premium 2 (lawn protection) / Premium 3 (VIP white-glove)
5. **Access difficulty**: Checklist — crane access, driveway width, street blocking, elevation, terrain, material drop zone
6. **Tools/equipment**: Checklist of common tools with pre-populated symbolic $25/day prices
7. **Supply chain risk**: Radio — standard (≤1 week) / extended (2-4 weeks) / import (6-8 weeks) with warning
8. All new fields included in HybridQuoteRequest schema (backend) and full-quote form (frontend)
9. All fields bilingual (FR/EN)

**Dependencies:** Phase 21 (complexity rebuild — access difficulty integrates with tiers)

**Source:** Sprint plan February 9, 2026 — Section 3.2

**Business Logic Gap:**
- Employee count suggestions: Laurent needs to define rules (job type × complexity → crew composition)
- Geographic zones: Requires Google Maps Distance Matrix API or manual zone selection — confirm API budget with Amin
- Premium level surcharges: Laurent needs to define daily surcharge amounts per level
- Duration pricing impact: Rules for half-day transport cost absorption, multi-day discount per day

---

## Phase 23: Submission Workflow & Editing

**Goal:** Make AI-generated quotes editable with approval workflow, notes, and upsell suggestions

**Sprint Deadline:** Feb 13, 2026

**Requirements:** SUB-01 to SUB-05

**Status:** Planned (2026-02-09)

**Plans:** 0 plans

Plans:
- [ ] TBD (run /gsd:plan-phase 23 to break down)

**Success Criteria:**
1. **Editable submissions**: After AI generates quote, each line item can be modified (quantity, price), removed, or reordered
2. New items can be added from materials database (Phase 20)
3. "Finalize" button locks the submission
4. **Quote status workflow**: draft → pending approval → approved (new status column in DB)
5. **Notes field**: Timestamped, attributed to user who wrote them
6. **Approval flow**: Only admin (Laurent) can approve — estimators can create and suggest changes
7. Approval log maintained for audit trail
8. **Upsell system**: After main submission, auto-suggest related services by job type
9. Upsell rules: Bardeau → heating cables, gutters, ventilation; Élastomère → drain, insulation, maintenance; Metal → gutters, snow guards, warranty; Any → inspection plan, maintenance contract
10. Each upsell generates as a SEPARATE submission document linked to parent

**Dependencies:** Phase 20 (materials DB for adding items), Phase 22 (new fields in submissions)

**Source:** Sprint plan February 9, 2026 — Section 3.3

---

## Phase 24: Export, Send & Red Flags

**Goal:** DOCX export, send options, and automated warning system

**Sprint Deadline:** Feb 13-14, 2026

**Requirements:** EXP-01 to EXP-04

**Status:** Planned (2026-02-09)

**Plans:** 0 plans

Plans:
- [ ] TBD (run /gsd:plan-phase 24 to break down)

**Success Criteria:**
1. **DOCX export**: Generates Word document alongside existing PDF
2. Both formats include: LV logo, job details, itemized materials, labor breakdown, total with taxes, terms & conditions, signature line
3. **Send options**: Send now (email) / Schedule send (date+time picker) / Save as draft
4. **Red flag system**: Auto-flag submissions matching warning patterns:
   - Budget mismatch (client expects below-standard work)
   - Geographic (distance > 60km from LV HQ)
   - Material risk (imported materials with 6+ week lead time)
   - Crew availability (multi-day during peak season June-Sept)
   - Low margin (calculated margin < 15%)
5. Red flags displayed as dismissible warnings before sending
6. All export templates bilingual

**Dependencies:** Phase 23 (submission workflow for send/draft states)

**Source:** Sprint plan February 9, 2026 — Sections 3.3.4, 3.3.5, 3.3.6

---

## Phase 25: UI Polish & Dark Mode

**Goal:** Dark mode toggle, FR/EN language bug fixes, LV branding verification

**Sprint Deadline:** Feb 13, 2026

**Requirements:** UI-06, UI-07, UI-08

**Status:** Planned (2026-02-09)

**Plans:** 0 plans

Plans:
- [ ] TBD (run /gsd:plan-phase 25 to break down)

**Success Criteria:**
1. **Dark mode toggle**: Sun/moon button in top-right corner
2. Light theme = current LV colors; Dark theme = dark background, light text, same LV accents
3. Theme preference saved per user (localStorage)
4. **FR/EN bug fix**: All content respects language toggle — test by switching mid-session
5. AI-generated text and submission templates also respect language setting
6. **LV branding**: Verify brand colors applied to header, buttons, accents, PDF/DOCX templates
7. Keep 3 separate sections (price calculator, materials, full submission) — do NOT merge

**Dependencies:** None — can run in parallel with other phases

**Source:** Sprint plan February 9, 2026 — Section 3.5

---

## Milestone: v2 Sprint Delivery

**Deadline:** February 16, 2026

After Phases 19-25:
- Data quality issues fixed (revenue labeling, 2022 flags)
- 672 materials searchable in platform
- Tier-based complexity system roofers understand
- All estimation fields Laurent requested (crew, duration, zone, premium, tools, access, supply chain)
- Editable submissions with approval workflow
- Upsell suggestions as separate submissions
- DOCX + PDF export with LV branding
- Send options (immediate/scheduled/draft)
- Red flag warnings
- Dark mode + language fixes

**Out of scope for this milestone (separate projects):**
- AI Agent (inbound call handling)
- Solar calculation tool
- GoHighLevel integration
- CCube ↔ QuickBooks invoice flow

**Next milestone:** Integrations (GHL, QuickBooks, AI Agent)

---
*Roadmap created: 2026-01-18*
*Sprint phases 19-25 added: 2026-02-09*
