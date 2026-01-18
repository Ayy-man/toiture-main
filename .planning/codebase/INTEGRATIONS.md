# External Integrations

**Analysis Date:** 2026-01-18

## Current State

**No active external integrations.** The project currently operates as a standalone data analysis and ML training pipeline using local files only.

## APIs & External Services

### Planned Integrations (Per Specification)

**Vector Database:**
- Pinecone
  - Purpose: Store and query 8,132 CBR case embeddings for similar job retrieval
  - SDK/Client: `pinecone` Python package
  - Auth: `PINECONE_API_KEY` (env var)
  - Index: `toiturelv-cortex`
  - Tier: Free tier sufficient (8K vectors fits)
  - Status: Not implemented

**LLM API:**
- OpenRouter
  - Purpose: Case revision and confidence scoring via LLM
  - Model: `mistral-7b` (Mistral 7B)
  - SDK/Client: Direct HTTP requests via `requests` library
  - Auth: `OPENROUTER_API_KEY` (env var)
  - Endpoint: `https://openrouter.ai/api/v1/chat/completions`
  - Status: Not implemented

**Embedding Model:**
- Sentence Transformers (Local)
  - Model: `paraphrase-multilingual-MiniLm-L12-v2`
  - Dimensions: 384
  - Purpose: Generate query embeddings for Pinecone search
  - Status: Embeddings pre-generated, stored in `cbr_embeddings.npz`

## Data Storage

**Databases:**
- None currently
- Future: Pinecone (vector DB for embeddings)

**File Storage:**
- Local filesystem only
- Data path: `/Users/aymanbaig/Desktop/cortex-data/`
- CSV files: ~200MB+ total
- Model artifacts: `.pkl` files (~5MB total)

**Caching:**
- None configured
- Planned: Cache similar cases for repeat queries (per spec)

## Source Data System

**C-Cube (External CRM):**
- TOITURELV's existing quoting system
- No API available
- Data exported manually as CSV
- Export files:
  - `Quotes Data Export.csv` - Quote headers
  - `Quote Lines.csv` - Line items
  - `Quote Materials.csv` - Material records
  - `Quote Sub Lines.csv` - Subcontractor records
  - `Quote Time Lines.csv` - Labor time records
  - `Quote Companies.csv` - Company/client data
- Status: Manual CSV export workflow

## Authentication & Identity

**Auth Provider:**
- None currently
- No user authentication implemented
- API will be unauthenticated initially (MVP)

## Monitoring & Observability

**Error Tracking:**
- None configured

**Logs:**
- `print()` statements with `sys.stdout.flush()`
- No structured logging framework

**Analytics:**
- None

## CI/CD & Deployment

**Hosting (Planned):**
- Backend: Railway (FastAPI)
- Frontend: Vercel (Next.js)

**CI Pipeline:**
- None configured
- No GitHub Actions or similar

**Docker:**
- Not implemented
- Planned: Dockerfile for Railway deployment

## Environment Configuration

**Required env vars (Future):**
```
# Backend (.env)
PINECONE_API_KEY=xxx          # Pinecone vector DB access
OPENROUTER_API_KEY=xxx        # LLM API access
INDEX_NAME=toiturelv-cortex   # Pinecone index name
CORS_ORIGINS=http://localhost:3000,https://yourdomain.com

# Frontend (.env.local)
NEXT_PUBLIC_API_URL=http://localhost:8000  # Backend URL
```

**Current configuration:**
- Hardcoded in Python scripts
- `DATA_PATH = "/Users/aymanbaig/Desktop/cortex-data/"`

**Secrets location:**
- Not applicable (no secrets currently)
- Future: Environment variables on Railway/Vercel

## Webhooks & Callbacks

**Incoming:**
- None

**Outgoing:**
- None

## Planned Integration Architecture

```
User Request (Frontend)
        │
        ▼
    Next.js (Vercel)
        │
        ▼ POST /api/estimate (proxy)
        │
    FastAPI (Railway)
        │
        ├──▶ Sentence Transformers (generate embedding)
        │
        ├──▶ Pinecone (query similar cases)
        │
        ├──▶ CBR Engine (calculate base estimate)
        │
        └──▶ OpenRouter/Mistral (revise estimate + reasoning)
                │
                ▼
        Estimate Response (JSON)
```

## API Design (Planned)

**POST /estimate**
```json
// Request
{
  "roof_sqft": 1500,
  "material": "asphalt_shingle",
  "pitch": "6/12",
  "city": "Montreal",
  "access_difficulty": 3,
  "special_notes": "chimney, second story, winter job"
}

// Response
{
  "estimate_low": 12400,
  "estimate_high": 13200,
  "estimate_mid": 12800,
  "confidence": 0.94,
  "unit": "CAD",
  "similar_cases": [...],
  "reasoning": "Based on 47 similar Montreal shingle jobs...",
  "algorithm_used": "hybrid_cbr_llm",
  "timestamp": "2025-01-18T14:32:00Z"
}
```

**GET /health**
```json
{ "status": "ok", "version": "1.0.0" }
```

## Data Quality Constraints

**Known Issues (from source system C-Cube):**
- 2022 labor data unreliable (median 1.3 hrs vs normal 20-30 hrs)
- 22% missing city data - fallback to region-level grouping
- 28% missing chimney detection - manual override via `special_notes`
- Square footage available for only 33% of quotes

**Workarounds Built Into Pipeline:**
- `master_data_pipeline_v4_fixed.py` handles French number formatting
- Text extraction patterns for sqft from descriptions
- Validation flags: `is_valid_for_analysis`, `labor_data_reliable`

## Third-Party Rate Limits

**OpenRouter:**
- Rate limits apply (varies by plan)
- Mitigation: Batch requests, cache similar cases

**Pinecone (Free Tier):**
- 100K vectors max
- Current: 8,132 vectors (well under limit)
- No scaling issues for MVP

---

*Integration audit: 2026-01-18*
