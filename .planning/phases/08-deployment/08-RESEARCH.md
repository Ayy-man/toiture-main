# Phase 8: Deployment - Research

**Researched:** 2026-01-18
**Domain:** Cloud deployment (Railway, Vercel)
**Confidence:** HIGH

## Summary

Phase 8 deploys the TOITURELV Cortex application to production with FastAPI on Railway and Next.js on Vercel. The backend requires careful Docker configuration due to ML dependencies (scikit-learn, sentence-transformers, PyTorch), while the frontend deployment is straightforward with Vercel's Next.js support.

Key findings:
- Railway supports FastAPI deployment via Dockerfile or Nixpacks, with health check support
- Vercel auto-detects Next.js 15 and supports pnpm monorepo structures
- CORS configuration is critical: backend must allow Vercel production domain
- Environment variables need configuration on both platforms for API keys
- CPU-only PyTorch installation significantly reduces Docker image size

**Primary recommendation:** Use Railway's Dockerfile builder with CPU-only PyTorch and Vercel's automatic Next.js detection, with explicit CORS and health check configuration.

## Standard Stack

The established deployment configuration for this domain:

### Core Infrastructure
| Platform | Purpose | Why Standard |
|----------|---------|--------------|
| Railway | FastAPI backend hosting | Python/ML-friendly, Dockerfile support, easy env vars |
| Vercel | Next.js frontend hosting | Native Next.js support, automatic deployments |

### Configuration Files
| File | Location | Purpose |
|------|----------|---------|
| Dockerfile | `backend/Dockerfile` | Custom build for ML dependencies |
| railway.json | `backend/railway.json` | Railway config as code (health check, start command) |
| vercel.json | `frontend/vercel.json` | Optional - Vercel config (headers, root directory) |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Railway | Render, Fly.io | Railway has simpler Python/ML support |
| Vercel | Netlify | Vercel has native Next.js 15 support |
| Dockerfile | Nixpacks | Dockerfile gives more control for ML deps |

**Installation:**
```bash
# Railway CLI (optional for local testing)
npm install -g @railway/cli

# Vercel CLI (optional for local testing)
npm install -g vercel
```

## Architecture Patterns

### Recommended Project Structure
```
project/
├── backend/
│   ├── Dockerfile           # Railway build config
│   ├── railway.json         # Railway deployment settings
│   ├── requirements.txt     # Python dependencies
│   └── app/                  # FastAPI application
├── frontend/
│   ├── vercel.json          # Optional Vercel settings
│   ├── package.json         # pnpm scripts
│   └── src/                  # Next.js application
```

### Pattern 1: Backend Dockerfile for ML Applications
**What:** Custom Dockerfile with CPU-only PyTorch to minimize image size
**When to use:** Applications with sentence-transformers, scikit-learn dependencies
**Example:**
```dockerfile
# Source: https://fastapi.tiangolo.com/deployment/docker/
# Optimized for Railway deployment with ML dependencies

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Prevent Python from writing .pyc files
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install CPU-only PyTorch FIRST to avoid CUDA deps
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

# Copy and install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/

# Railway injects PORT env var
CMD ["fastapi", "run", "app/main.py", "--host", "0.0.0.0", "--port", "${PORT:-8000}"]
```

### Pattern 2: Railway Config as Code
**What:** `railway.json` for health check and deployment configuration
**When to use:** Any Railway deployment
**Example:**
```json
{
  "$schema": "https://railway.com/railway.schema.json",
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "./Dockerfile"
  },
  "deploy": {
    "startCommand": "fastapi run app/main.py --host 0.0.0.0 --port $PORT",
    "healthcheckPath": "/health",
    "healthcheckTimeout": 300,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 3
  }
}
```

### Pattern 3: Environment-Based CORS
**What:** Dynamic CORS origins from environment variables
**When to use:** Production deployments with separate domains
**Example (already implemented in backend/app/config.py):**
```python
# CORS_ORIGINS env var should include production Vercel domain
cors_origins: list[str] = ["http://localhost:3000"]
```

Production CORS_ORIGINS should be:
```
CORS_ORIGINS=["https://your-app.vercel.app","http://localhost:3000"]
```

### Anti-Patterns to Avoid
- **Hardcoded URLs:** Never hardcode API URLs; use environment variables
- **CUDA in production (for this app):** CPU-only PyTorch is sufficient and much smaller
- **Wildcard CORS in production:** Use specific domains, not `*`
- **Missing health check:** Always configure health check for zero-downtime deploys

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| HTTPS termination | Custom SSL handling | Railway/Vercel built-in | Both platforms handle HTTPS automatically |
| Domain management | Manual DNS | Platform domains | Railway and Vercel provide automatic domains |
| CI/CD pipeline | Custom scripts | GitHub integration | Both platforms auto-deploy from GitHub |
| Health monitoring | Custom endpoint polling | Platform health checks | Railway has built-in health check system |
| Secret rotation | Manual env var updates | Platform secret management | Both have secure variable management |

**Key insight:** Both Railway and Vercel handle infrastructure concerns (HTTPS, domains, scaling, secrets) automatically. Focus on application configuration, not infrastructure.

## Common Pitfalls

### Pitfall 1: PyTorch CUDA Dependencies in Docker
**What goes wrong:** Docker image becomes 8GB+ with unused CUDA libraries
**Why it happens:** Default PyTorch installation includes CUDA even when not needed
**How to avoid:** Install CPU-only PyTorch before other deps:
```dockerfile
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu
```
**Warning signs:** Build times >10 minutes, image size >2GB

### Pitfall 2: Railway Health Check Timeout
**What goes wrong:** Deployment fails with "health check failed"
**Why it happens:** ML model loading takes >5 minutes on cold start
**How to avoid:**
1. Set `healthcheckTimeout: 300` (5 minutes) in railway.json
2. Health endpoint should return before model fully loaded (current `/health` is fine)
**Warning signs:** Deployments succeed locally but fail on Railway

### Pitfall 3: CORS Configuration for Production
**What goes wrong:** Frontend can't reach backend: "CORS policy: No 'Access-Control-Allow-Origin'"
**Why it happens:** CORS_ORIGINS doesn't include production Vercel domain
**How to avoid:** Update CORS_ORIGINS env var on Railway with exact Vercel domain
**Warning signs:** Works locally, fails after deployment

### Pitfall 4: Frontend Environment Variables Not Set
**What goes wrong:** Frontend shows "Failed to fetch" or uses wrong API URL
**Why it happens:** NEXT_PUBLIC_ env vars must be set in Vercel, not just locally
**How to avoid:** Configure all NEXT_PUBLIC_ vars in Vercel dashboard before deploying
**Warning signs:** Console errors about undefined API_URL

### Pitfall 5: Railway IPv6 for Private Networking
**What goes wrong:** Service-to-service communication fails
**Why it happens:** Railway uses IPv6 for private networking
**How to avoid:** Bind to `[::]` not `0.0.0.0` if using private networking (not applicable here since using public domains)
**Warning signs:** Only affects multi-service Railway setups

### Pitfall 6: Health Check Hostname Blocking
**What goes wrong:** Health check fails with "failed with status 400"
**Why it happens:** App rejects requests from `healthcheck.railway.app` hostname
**How to avoid:** FastAPI with default CORS middleware handles this; don't add host restrictions
**Warning signs:** "Health check failed with service unavailable"

## Code Examples

Verified patterns from official sources:

### Backend Dockerfile (Production)
```dockerfile
# Source: Railway docs + FastAPI docs
# For Railway deployment with sentence-transformers

FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# CPU-only PyTorch (reduces image from 8GB to ~1GB)
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY app/ ./app/

# Use exec form for proper signal handling
# Railway injects $PORT automatically
CMD ["sh", "-c", "fastapi run app/main.py --host 0.0.0.0 --port ${PORT:-8000}"]
```

### railway.json
```json
{
  "$schema": "https://railway.com/railway.schema.json",
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "./Dockerfile"
  },
  "deploy": {
    "healthcheckPath": "/health",
    "healthcheckTimeout": 300,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 3
  }
}
```

### Frontend vercel.json (Optional)
```json
{
  "$schema": "https://openapi.vercel.sh/vercel.json",
  "framework": "nextjs",
  "installCommand": "pnpm install",
  "buildCommand": "pnpm build"
}
```

### Environment Variables

**Railway (Backend):**
```bash
# Required
CORS_ORIGINS=["https://your-app.vercel.app","http://localhost:3000"]
MODEL_DIR=app/models
PINECONE_API_KEY=<your-key>
PINECONE_INDEX_HOST=<your-host>
OPENROUTER_API_KEY=<your-key>
OPENROUTER_MODEL=openai/gpt-4o-mini
SUPABASE_URL=<your-url>
SUPABASE_SERVICE_KEY=<your-key>
```

**Vercel (Frontend):**
```bash
# Required (NEXT_PUBLIC_ prefix for client-side access)
NEXT_PUBLIC_API_URL=https://your-backend.railway.app
NEXT_PUBLIC_SUPABASE_URL=<your-url>
NEXT_PUBLIC_SUPABASE_ANON_KEY=<your-key>

# Server-side only
IRON_SESSION_SECRET=<32-char-random-string>
APP_PASSWORD=<team-password>
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Gunicorn + Uvicorn workers | `fastapi run` CLI | FastAPI 0.100+ | Simplified deployment, built-in worker support |
| tiangolo/uvicorn-gunicorn-fastapi image | python:3.11-slim base | 2024 | Deprecated base image, use official Python |
| Heroku-style Procfile | railway.json config as code | 2024 | More declarative, version-controlled config |
| Manual CORS headers | FastAPI CORSMiddleware | Always | Don't manually set Access-Control headers |

**Deprecated/outdated:**
- `tiangolo/uvicorn-gunicorn-fastapi` Docker image: Deprecated, use official Python image
- Nixpacks builder: Deprecated in favor of Railpack (Railway's new default)
- `hypercorn` server: Railway docs show hypercorn but `fastapi run` (uvicorn) is simpler

## Open Questions

Things that couldn't be fully resolved:

1. **Sentence-transformers model download on cold start**
   - What we know: Model downloaded from HuggingFace on first load
   - What's unclear: If Railway caches this between deploys
   - Recommendation: Monitor first deploy time; consider pre-downloading in Dockerfile if slow

2. **Railway Hobby vs Pro memory limits**
   - What we know: Hobby has 8GB max, Pro has 32GB max
   - What's unclear: Exact memory usage of sentence-transformers + scikit-learn loaded
   - Recommendation: Start with Hobby plan; monitor memory usage in Railway dashboard

3. **Vercel preview environment CORS**
   - What we know: Preview URLs change on each deploy
   - What's unclear: Whether wildcard subdomain CORS is needed
   - Recommendation: For MVP, use production environment only; add preview support later if needed

## Sources

### Primary (HIGH confidence)
- [Railway FastAPI Deployment Guide](https://docs.railway.com/guides/fastapi) - Official deployment steps
- [Railway Config as Code](https://docs.railway.com/reference/config-as-code) - railway.json schema
- [Railway Healthchecks](https://docs.railway.com/reference/healthchecks) - Health check configuration
- [FastAPI Docker Deployment](https://fastapi.tiangolo.com/deployment/docker/) - Official Dockerfile patterns
- [Vercel Environment Variables](https://vercel.com/docs/environment-variables) - Env var configuration
- [Vercel Project Configuration](https://vercel.com/docs/projects/project-configuration) - vercel.json schema

### Secondary (MEDIUM confidence)
- [Railway Pricing Plans](https://docs.railway.com/reference/pricing/plans) - Memory limits verified
- [Vercel CORS Guide](https://vercel.com/kb/guide/how-to-enable-cors) - CORS configuration patterns
- [Sentence Transformers Installation](https://sbert.net/docs/installation.html) - CPU-only setup

### Tertiary (LOW confidence)
- WebSearch results for PyTorch CPU-only Docker deployment - multiple community sources agree
- WebSearch results for Railway ML deployment patterns - limited to blog posts

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - Official documentation verified for both platforms
- Architecture: HIGH - Patterns from official docs and guides
- Pitfalls: MEDIUM - Mix of official docs and community experience

**Research date:** 2026-01-18
**Valid until:** 2026-02-18 (30 days - both platforms are stable)
