# Codebase Structure

**Last Updated:** 2026-02-01

## Directory Layout

```
Toiture-P1/
├── .planning/                    # GSD planning documents
│   ├── codebase/                 # Codebase analysis documents
│   ├── phases/                   # Phase plans and summaries
│   ├── PROJECT.md                # Project overview
│   ├── ROADMAP.md                # Phase roadmap
│   ├── REQUIREMENTS.md           # Requirements traceability
│   └── STATE.md                  # Current project state
├── backend/                      # FastAPI backend
│   ├── app/
│   │   ├── main.py               # FastAPI entry point
│   │   ├── routers/              # API route handlers
│   │   │   ├── estimate.py       # /estimate endpoints
│   │   │   ├── auth.py           # /auth endpoints
│   │   │   ├── feedback.py       # /feedback endpoints
│   │   │   └── dashboard.py      # /dashboard endpoints
│   │   ├── services/             # Business logic
│   │   │   ├── predictor.py      # ML price prediction
│   │   │   ├── pinecone_client.py # CBR vector search
│   │   │   ├── llm_service.py    # LLM reasoning
│   │   │   ├── material_predictor.py # Material prediction
│   │   │   ├── hybrid_orchestrator.py # Hybrid quote generation
│   │   │   └── confidence_scorer.py # Quote confidence scoring
│   │   ├── schemas/              # Pydantic models
│   │   │   ├── estimate.py       # Estimate schemas
│   │   │   └── hybrid_quote.py   # Hybrid quote schemas
│   │   └── models/               # ML model artifacts
│   │       ├── cortex_v4_gb.pkl
│   │       ├── material_classifier.pkl
│   │       └── *.json            # Config and rules
│   ├── tests/                    # pytest tests
│   ├── requirements.txt          # Python dependencies
│   ├── Dockerfile                # Container build
│   └── railway.json              # Railway deployment config
├── frontend/                     # Next.js frontend
│   ├── src/
│   │   ├── app/                  # App Router pages
│   │   │   ├── (admin)/          # Admin layout group
│   │   │   │   ├── layout.tsx    # Admin layout with sidebar
│   │   │   │   ├── estimateur/   # Estimateur page
│   │   │   │   ├── historique/   # Quote history page
│   │   │   │   ├── apercu/       # Dashboard metrics
│   │   │   │   └── clients/      # Client search
│   │   │   ├── login/            # Login page
│   │   │   ├── globals.css       # Global styles + theme
│   │   │   └── layout.tsx        # Root layout
│   │   ├── components/
│   │   │   ├── ui/               # shadcn/ui components
│   │   │   │   ├── sidebar.tsx   # Full shadcn sidebar
│   │   │   │   ├── breadcrumb.tsx
│   │   │   │   ├── button.tsx
│   │   │   │   ├── card.tsx
│   │   │   │   └── ...
│   │   │   ├── admin/            # Admin-specific components
│   │   │   │   ├── app-sidebar.tsx
│   │   │   │   └── page-wrapper.tsx
│   │   │   ├── estimateur/       # Estimateur components
│   │   │   │   ├── estimate-form.tsx
│   │   │   │   ├── complexity-presets.tsx
│   │   │   │   ├── quote-result.tsx
│   │   │   │   └── quote-pdf-document.tsx
│   │   │   ├── charts/           # Recharts wrappers
│   │   │   └── data-table/       # TanStack Table components
│   │   ├── lib/
│   │   │   ├── api/              # API clients
│   │   │   │   ├── client.ts     # Base fetch client
│   │   │   │   ├── estimate.ts   # Estimate API
│   │   │   │   └── hybrid-quote.ts # Hybrid quote API
│   │   │   ├── hooks/            # React Query hooks
│   │   │   ├── i18n/             # French translations
│   │   │   │   └── fr.ts
│   │   │   ├── schemas/          # Zod schemas
│   │   │   │   └── hybrid-quote.ts
│   │   │   ├── types/            # TypeScript types
│   │   │   │   └── hybrid-quote.ts
│   │   │   └── utils.ts          # Utility functions
│   │   └── middleware.ts         # Auth middleware
│   ├── package.json              # Node dependencies
│   ├── tsconfig.json             # TypeScript config
│   ├── tailwind.config.ts        # Tailwind config
│   ├── components.json           # shadcn/ui config
│   └── vercel.json               # Vercel deployment config
├── cortex-data/                  # Data and training scripts
│   ├── *.csv                     # Training datasets
│   ├── *.py                      # Training scripts
│   └── *.pkl                     # Model artifacts
└── Project docs/                 # Business documentation
    └── TOITURELV-CORTEX-SPEC.md  # Technical specification
```

## Directory Purposes

**`backend/`:**
- Purpose: FastAPI REST API serving ML predictions and business logic
- Entry point: `app/main.py`
- Deployed to: Railway

**`frontend/`:**
- Purpose: Next.js admin dashboard and estimation interface
- Entry point: `src/app/layout.tsx`
- Deployed to: Vercel

**`cortex-data/`:**
- Purpose: Data processing scripts and training data
- Not deployed (development only)

**`.planning/`:**
- Purpose: GSD workflow documentation and project management
- Contains: Phase plans, requirements, codebase analysis

## Key File Locations

**Backend Entry Points:**
- `backend/app/main.py` - FastAPI app with lifespan context
- `backend/app/routers/estimate.py` - `/estimate/*` endpoints
- `backend/app/routers/dashboard.py` - `/dashboard/*` endpoints

**Frontend Entry Points:**
- `frontend/src/app/(admin)/layout.tsx` - Admin layout with sidebar
- `frontend/src/app/(admin)/estimateur/page.tsx` - Main estimateur page
- `frontend/src/middleware.ts` - Auth route protection

**Configuration:**
- `backend/app/models/cortex_config_v4.json` - ML model config
- `frontend/src/lib/i18n/fr.ts` - French translations
- `frontend/src/app/globals.css` - Theme colors and CSS variables

**Shared Types:**
- `frontend/src/lib/types/hybrid-quote.ts` - TypeScript types
- `frontend/src/lib/schemas/hybrid-quote.ts` - Zod validation
- `backend/app/schemas/hybrid_quote.py` - Pydantic models

## Naming Conventions

**Files:**
- Python: `snake_case.py` (e.g., `hybrid_orchestrator.py`)
- TypeScript: `kebab-case.ts` (e.g., `hybrid-quote.ts`)
- React components: `kebab-case.tsx` (e.g., `quote-result.tsx`)

**Directories:**
- Lowercase with hyphens: `cortex-data/`
- Route groups in parentheses: `(admin)/`

**Components:**
- PascalCase exports: `export function QuoteResult() {}`
- File matches component: `quote-result.tsx` → `QuoteResult`

## Where to Add New Code

**New API Endpoint:**
1. Add router in `backend/app/routers/`
2. Register in `backend/app/main.py`
3. Add schemas in `backend/app/schemas/`

**New Frontend Page:**
1. Create directory in `frontend/src/app/(admin)/`
2. Add `page.tsx` file
3. Update navigation in `frontend/src/components/admin/app-sidebar.tsx`

**New UI Component:**
1. shadcn primitive: Add to `frontend/src/components/ui/`
2. Feature component: Add to `frontend/src/components/{feature}/`
3. Admin component: Add to `frontend/src/components/admin/`

**New API Client:**
1. Add client in `frontend/src/lib/api/`
2. Add types in `frontend/src/lib/types/`
3. Add Zod schema in `frontend/src/lib/schemas/`

---

*Structure updated: 2026-02-01*
