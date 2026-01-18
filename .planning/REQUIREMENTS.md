# Requirements: TOITURELV Cortex

**Defined:** 2026-01-18
**Core Value:** Accurate price estimates with explainable reasoning

## v1 Requirements

### Backend API

- [x] **API-01**: FastAPI app with health check endpoint
- [x] **API-02**: POST /estimate endpoint accepts 6 inputs (sqft, category, material_lines, labor_lines, has_subs, complexity)
- [x] **API-03**: Endpoint returns estimate, range, confidence, similar cases, and LLM reasoning
- [x] **API-04**: CORS configured for frontend domain

### Pinecone Integration

- [x] **PIN-01**: Upload 8,132 CBR embeddings to Pinecone index
- [x] **PIN-02**: Query similar cases by embedding similarity
- [x] **PIN-03**: Return top 5 similar cases with metadata

### LLM Integration

- [x] **LLM-01**: OpenRouter client with configurable model
- [x] **LLM-02**: Generate reasoning from estimate + similar cases
- [x] **LLM-03**: Include confidence assessment in reasoning

### Frontend - Estimate Form

- [x] **FORM-01**: Input form with 6 fields (sqft, category dropdown, material_lines, labor_lines, has_subs toggle, complexity slider)
- [x] **FORM-02**: Submit calls backend /estimate endpoint
- [x] **FORM-03**: Display estimate with range and confidence
- [x] **FORM-04**: Display similar cases used for estimate
- [x] **FORM-05**: Display LLM reasoning

### Frontend - Review Queue

- [x] **REVIEW-01**: List pending estimates awaiting Laurent's review
- [x] **REVIEW-02**: Show AI estimate alongside input details
- [x] **REVIEW-03**: Laurent can enter his actual/expected price
- [x] **REVIEW-04**: Mark estimate as reviewed (thumbs up/down implicit from price difference)

### Frontend - Analytics Dashboard

- [x] **DASH-01**: Estimate accuracy chart (% within 10%, 20% of Laurent's price)
- [x] **DASH-02**: Confidence trends (when AI says high confidence, is it accurate?)
- [x] **DASH-03**: Material mix breakdown (pie/bar by category)
- [x] **DASH-04**: Basic stats (total estimates, avg accuracy, time period filter)

### Data Storage

- [x] **DB-01**: Supabase tables for estimates and feedback
- [x] **DB-02**: Store: inputs, AI estimate, Laurent's price, timestamp, category
- [x] **DB-03**: Query feedback for analytics calculations

### Authentication

- [x] **AUTH-01**: Simple password gate on frontend
- [x] **AUTH-02**: Password stored as env var, not hardcoded

### Deployment

- [ ] **DEPLOY-01**: FastAPI deployed to Railway
- [ ] **DEPLOY-02**: Next.js deployed to Vercel
- [ ] **DEPLOY-03**: Environment variables configured (Pinecone, OpenRouter, Supabase keys)

### Admin Dashboard

- [x] **DASH-05**: 4 tabs functional (Estimateur, Historique, Aperçu, Clients)
- [x] **DASH-06**: Estimateur returns results in <3 seconds with streaming
- [x] **DASH-07**: Quote browser handles 8,293 records with pagination
- [x] **DASH-08**: Customer search returns results in <1 second
- [x] **DASH-09**: Dashboard charts render with real data
- [x] **DASH-10**: French labels throughout (Quebec French)
- [x] **DASH-11**: Dark sidebar with brick red accents (#8B2323)
- [x] **DASH-12**: Mobile-responsive sidebar collapses

## v2 Requirements

### Auto-Update Pipeline

- **AUTO-01**: Automated retraining trigger when feedback threshold reached
- **AUTO-02**: Model versioning and rollback capability

### Enhanced Analytics

- **ANAL-01**: Time saved metrics
- **ANAL-02**: Per-estimator accuracy tracking
- **ANAL-03**: Export feedback to CSV for manual analysis

## Out of Scope

| Feature | Reason |
|---------|--------|
| Real-time C-Cube sync | Manual CSV export workflow is fine for now |
| User accounts | Shared password sufficient for small team |
| Mobile app | Responsive web works on mobile |
| Auto-update from feedback | v2 — design for it, don't build yet |
| Client-facing estimates | Internal tool only |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| API-01 | Phase 1 | Complete |
| API-02 | Phase 1 | Complete |
| API-03 | Phase 1-3 | Complete |
| API-04 | Phase 1 | Complete |
| PIN-01 | Phase 2 | Complete |
| PIN-02 | Phase 2 | Complete |
| PIN-03 | Phase 2 | Complete |
| LLM-01 | Phase 3 | Complete |
| LLM-02 | Phase 3 | Complete |
| LLM-03 | Phase 3 | Complete |
| FORM-01 | Phase 4 | Complete |
| FORM-02 | Phase 4 | Complete |
| FORM-03 | Phase 4 | Complete |
| FORM-04 | Phase 4 | Complete |
| FORM-05 | Phase 4 | Complete |
| DB-01 | Phase 5 | Complete |
| DB-02 | Phase 5 | Complete |
| DB-03 | Phase 5 | Complete |
| REVIEW-01 | Phase 5 | Complete |
| REVIEW-02 | Phase 5 | Complete |
| REVIEW-03 | Phase 5 | Complete |
| REVIEW-04 | Phase 5 | Complete |
| DASH-01 | Phase 6 | Complete |
| DASH-02 | Phase 6 | Complete |
| DASH-03 | Phase 6 | Complete |
| DASH-04 | Phase 6 | Complete |
| AUTH-01 | Phase 7 | Complete |
| AUTH-02 | Phase 7 | Complete |
| DEPLOY-01 | Phase 8 | Pending |
| DEPLOY-02 | Phase 8 | Pending |
| DEPLOY-03 | Phase 8 | Pending |
| DASH-05 | Phase 11 | Complete |
| DASH-06 | Phase 11 | Complete |
| DASH-07 | Phase 11 | Complete |
| DASH-08 | Phase 11 | Complete |
| DASH-09 | Phase 11 | Complete |
| DASH-10 | Phase 11 | Complete |
| DASH-11 | Phase 11 | Complete |
| DASH-12 | Phase 11 | Complete |

**Coverage:**
- v1 requirements: 36 total
- Mapped to phases: 36
- Unmapped: 0 ✓

---
*Requirements defined: 2026-01-18*
