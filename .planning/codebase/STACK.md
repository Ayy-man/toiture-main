# Technology Stack

**Last Updated:** 2026-02-01

## Languages

**Backend:**
- Python 3.11+ - FastAPI backend, ML prediction, data pipelines

**Frontend:**
- TypeScript - Next.js frontend (strict mode enabled)

## Runtime

**Backend:**
- Python 3.11+
- uvicorn ASGI server

**Frontend:**
- Node.js 18+
- pnpm package manager

**Lockfiles:**
- `backend/requirements.txt` - Python dependencies (pinned)
- `frontend/pnpm-lock.yaml` - pnpm lockfile

## Frameworks

**Backend (Python):**
- FastAPI 0.115+ - REST API framework
- Pydantic 2.x - Request/response validation
- scikit-learn - ML models (GradientBoosting)
- sentence-transformers - Embedding generation
- pinecone - Vector database client
- openai - OpenRouter LLM client (OpenAI SDK compatible)

**Frontend (TypeScript):**
- Next.js 16.1.6 - React framework (App Router)
- React 19.2.3 - UI library
- shadcn/ui v4 - Component library (Radix primitives)
- Tailwind CSS 4.x - Utility-first styling
- TanStack Table v8 - Data tables
- React Query - Server state management
- react-hook-form + Zod - Form handling and validation
- @react-pdf/renderer - Client-side PDF generation
- Recharts - Data visualization charts

**Testing:**
- pytest - Backend unit tests
- jest (configured) - Frontend tests

## Key Dependencies

**Backend Critical:**
- `fastapi` - REST API framework
- `pydantic` - Schema validation
- `joblib` - Model serialization
- `pandas` - Data manipulation
- `numpy` - Numerical computing
- `pinecone` - Vector database
- `openai` - LLM API client (via OpenRouter)
- `sentence-transformers` - Text embeddings
- `supabase` - Database client
- `iron-session` - Session management (for auth endpoints)

**Frontend Critical:**
- `next` - React framework
- `react`, `react-dom` - UI library
- `@radix-ui/*` - Accessible UI primitives
- `tailwindcss` - CSS framework
- `@tanstack/react-table` - Data tables
- `@tanstack/react-query` - Server state
- `react-hook-form` - Form management
- `zod` - Schema validation
- `@react-pdf/renderer` - PDF generation
- `recharts` - Charts and visualizations
- `lucide-react` - Icon library
- `date-fns` - Date utilities
- `class-variance-authority` - Component variants
- `clsx`, `tailwind-merge` - Class utilities

## Configuration

**Environment Variables:**

Backend (`.env`):
```
PINECONE_API_KEY=xxx
OPENROUTER_API_KEY=xxx
INDEX_NAME=toiturelv-cortex
CORS_ORIGINS=http://localhost:3000,https://yourdomain.com
SUPABASE_URL=xxx
SUPABASE_KEY=xxx
APP_PASSWORD=xxx
```

Frontend (`.env.local`):
```
NEXT_PUBLIC_API_URL=http://localhost:8000
SUPABASE_URL=xxx
SUPABASE_ANON_KEY=xxx
IRON_SESSION_SECRET=xxx
APP_PASSWORD=xxx
```

**Build Configuration:**
- `tsconfig.json` - TypeScript config (strict mode)
- `tailwind.config.ts` - Tailwind with shadcn theme
- `next.config.ts` - Next.js configuration
- `components.json` - shadcn/ui config

## Platform Requirements

**Development:**
- Python 3.11+ with pip
- Node.js 18+ with pnpm
- ~100GB+ disk space (training data)

**Production:**
- Railway - FastAPI backend
- Vercel - Next.js frontend
- Pinecone - Vector database (8K vectors indexed)
- Supabase - PostgreSQL database
- OpenRouter - LLM API (Mistral 7B, Cerebras)

## UI Component Library

**shadcn/ui v4 Components (Installed):**
- Sidebar (full implementation with SidebarRail, tooltips)
- Button, Card, Input, Label, Textarea
- Table, Tabs, Dialog, Sheet
- Breadcrumb, Separator
- Select, Checkbox
- Form (react-hook-form integration)
- Toast, Sonner
- Charts (Recharts wrappers)

**Brand Colors:**
- Primary: Brick red `hsl(10, 72%, 34%)` (#8B2323)
- Sidebar: Dark `hsl(0, 0%, 7%)` (#121212)

## Data Files

**Model Artifacts (backend/app/models/):**
- `cortex_v4_gb.pkl` - GradientBoosting price predictor
- `cortex_v4_bardeaux.pkl` - Tuned Bardeaux category model
- `category_encoder_v4.pkl` - Category LabelEncoder
- `cortex_config_v4.json` - Model configuration
- `material_classifier.pkl` - Multi-label material classifier
- `quantity_regressors.pkl` - 122 material quantity models
- `feature_triggers.json` - 21 feature-material triggers
- `material_cooccurrence.json` - 506 co-occurrence rules
- `material_medians.json` - 824 material median prices

**CBR System:**
- Pinecone index: `toiturelv-cortex` (8,132 vectors, 384-dim)
- Embedding model: `paraphrase-multilingual-MiniLM-L12-v2`

---

*Stack updated: 2026-02-01*
