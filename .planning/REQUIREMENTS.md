# Requirements: TOITURELV Cortex

**Defined:** 2026-01-18
**Core Value:** Accurate price estimates with explainable reasoning

## v1 Requirements

### Backend API

- [x] **API-01**: FastAPI app with health check endpoint
- [x] **API-02**: POST /estimate endpoint accepts 6 inputs (sqft, category, material_lines, labor_lines, has_subs, complexity)
- [ ] **API-03**: Endpoint returns estimate, range, confidence, similar cases, and LLM reasoning *(partial: similar cases in Phase 2, reasoning in Phase 3)*
- [x] **API-04**: CORS configured for frontend domain

### Pinecone Integration

- [x] **PIN-01**: Upload 8,132 CBR embeddings to Pinecone index
- [x] **PIN-02**: Query similar cases by embedding similarity
- [x] **PIN-03**: Return top 5 similar cases with metadata

### LLM Integration

- [ ] **LLM-01**: OpenRouter client with configurable model
- [ ] **LLM-02**: Generate reasoning from estimate + similar cases
- [ ] **LLM-03**: Include confidence assessment in reasoning

### Frontend - Estimate Form

- [ ] **FORM-01**: Input form with 6 fields (sqft, category dropdown, material_lines, labor_lines, has_subs toggle, complexity slider)
- [ ] **FORM-02**: Submit calls backend /estimate endpoint
- [ ] **FORM-03**: Display estimate with range and confidence
- [ ] **FORM-04**: Display similar cases used for estimate
- [ ] **FORM-05**: Display LLM reasoning

### Frontend - Review Queue

- [ ] **REVIEW-01**: List pending estimates awaiting Laurent's review
- [ ] **REVIEW-02**: Show AI estimate alongside input details
- [ ] **REVIEW-03**: Laurent can enter his actual/expected price
- [ ] **REVIEW-04**: Mark estimate as reviewed (thumbs up/down implicit from price difference)

### Frontend - Analytics Dashboard

- [ ] **DASH-01**: Estimate accuracy chart (% within 10%, 20% of Laurent's price)
- [ ] **DASH-02**: Confidence trends (when AI says high confidence, is it accurate?)
- [ ] **DASH-03**: Material mix breakdown (pie/bar by category)
- [ ] **DASH-04**: Basic stats (total estimates, avg accuracy, time period filter)

### Data Storage

- [ ] **DB-01**: Supabase tables for estimates and feedback
- [ ] **DB-02**: Store: inputs, AI estimate, Laurent's price, timestamp, category
- [ ] **DB-03**: Query feedback for analytics calculations

### Authentication

- [ ] **AUTH-01**: Simple password gate on frontend
- [ ] **AUTH-02**: Password stored as env var, not hardcoded

### Deployment

- [ ] **DEPLOY-01**: FastAPI deployed to Railway
- [ ] **DEPLOY-02**: Next.js deployed to Vercel
- [ ] **DEPLOY-03**: Environment variables configured (Pinecone, OpenRouter, Supabase keys)

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
| API-03 | Phase 1-3 | Partial |
| API-04 | Phase 1 | Complete |
| PIN-01 | Phase 2 | Complete |
| PIN-02 | Phase 2 | Complete |
| PIN-03 | Phase 2 | Complete |
| LLM-01 | Phase 3 | Pending |
| LLM-02 | Phase 3 | Pending |
| LLM-03 | Phase 3 | Pending |
| FORM-01 | Phase 4 | Pending |
| FORM-02 | Phase 4 | Pending |
| FORM-03 | Phase 4 | Pending |
| FORM-04 | Phase 4 | Pending |
| FORM-05 | Phase 4 | Pending |
| DB-01 | Phase 5 | Pending |
| DB-02 | Phase 5 | Pending |
| DB-03 | Phase 5 | Pending |
| REVIEW-01 | Phase 5 | Pending |
| REVIEW-02 | Phase 5 | Pending |
| REVIEW-03 | Phase 5 | Pending |
| REVIEW-04 | Phase 5 | Pending |
| DASH-01 | Phase 6 | Pending |
| DASH-02 | Phase 6 | Pending |
| DASH-03 | Phase 6 | Pending |
| DASH-04 | Phase 6 | Pending |
| AUTH-01 | Phase 7 | Pending |
| AUTH-02 | Phase 7 | Pending |
| DEPLOY-01 | Phase 8 | Pending |
| DEPLOY-02 | Phase 8 | Pending |
| DEPLOY-03 | Phase 8 | Pending |

**Coverage:**
- v1 requirements: 28 total
- Mapped to phases: 28
- Unmapped: 0 ✓

---
*Requirements defined: 2026-01-18*
