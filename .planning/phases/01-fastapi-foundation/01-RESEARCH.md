# Phase 1: FastAPI Foundation - Research

**Researched:** 2026-01-18
**Domain:** FastAPI ML model serving, Pydantic v2 validation, CORS configuration
**Confidence:** HIGH

## Summary

This phase focuses on building a FastAPI backend that serves ML model predictions via HTTP. The existing codebase already contains trained sklearn models (`cortex_model_global.pkl`, `cortex_model_Bardeaux.pkl`) and prediction logic in `cortex-data/predict_final.py`. The backend needs to wrap this prediction logic in a REST API.

The standard approach for serving sklearn models with FastAPI in 2025-2026 uses the **lifespan context manager pattern** to load models at startup, **Pydantic v2** for request/response validation, and **CORSMiddleware** for cross-origin requests. Railway deployment requires binding to the `$PORT` environment variable.

**Primary recommendation:** Use file-type project structure (small/focused API), lifespan context manager for model loading, Pydantic v2 Field validators for input constraints, and uvicorn for both development and Railway deployment.

## Standard Stack

The established libraries and tools for FastAPI ML model serving:

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| fastapi | >=0.128.0 | Web framework | Built-in Pydantic v2, async support, automatic OpenAPI docs |
| pydantic | >=2.7.0 | Request/response validation | Rust-powered core, 5-10x faster than v1, Field constraints |
| uvicorn | >=0.30.0 | ASGI server | Default for FastAPI, async event loop, production-ready |
| joblib | >=1.3.0 | Model loading | Standard for sklearn model serialization, memory-mapped loading |
| numpy | >=1.26.0 | Numerical operations | Required by sklearn models |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| python-multipart | >=0.0.6 | Form data parsing | If accepting form data (not needed for JSON-only API) |
| httpx | >=0.27.0 | HTTP client for testing | Required for TestClient in tests |
| pytest | >=8.0.0 | Test framework | Standard Python testing |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| uvicorn | gunicorn + uvicorn workers | Better for multi-core production; overkill for Railway single-container |
| uvicorn | hypercorn | Supports HTTP/2; less common, Railway template uses hypercorn |
| joblib | pickle | joblib handles numpy arrays better, memory-maps large files |

**Installation:**
```bash
pip install "fastapi[standard]>=0.128.0" joblib numpy
```

The `[standard]` extra includes: uvicorn, httpx (for TestClient), python-multipart, and jinja2.

## Architecture Patterns

### Recommended Project Structure

For this focused ML API (single endpoint + health), use file-type structure:

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app, lifespan, include routers
│   ├── config.py            # Pydantic Settings for env vars
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── health.py        # GET /health endpoint
│   │   └── estimate.py      # POST /estimate endpoint
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── estimate.py      # Request/Response Pydantic models
│   ├── services/
│   │   ├── __init__.py
│   │   └── predictor.py     # ML model loading + prediction logic
│   └── models/              # ML model files copied here for deployment
│       ├── cortex_model_global.pkl
│       ├── cortex_model_Bardeaux.pkl
│       ├── category_encoder_v3.pkl
│       └── cortex_config_v3.json
├── tests/
│   ├── __init__.py
│   ├── conftest.py          # pytest fixtures
│   ├── test_health.py
│   └── test_estimate.py
├── requirements.txt
├── Dockerfile
└── .env.example
```

### Pattern 1: Lifespan Context Manager for Model Loading

**What:** Load ML models once at startup, store in module-level dict, clean up on shutdown
**When to use:** Always for ML model serving (avoids loading on every request)
**Source:** [FastAPI Lifespan Events](https://fastapi.tiangolo.com/advanced/events/)

```python
# app/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.services.predictor import load_models, unload_models

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Load ML models
    load_models()
    yield
    # Shutdown: Clean up
    unload_models()

app = FastAPI(lifespan=lifespan)
```

```python
# app/services/predictor.py
import joblib
import json
from pathlib import Path

# Module-level storage (shared across requests)
_models = {}
_config = {}

MODEL_DIR = Path(__file__).parent.parent / "models"

def load_models():
    """Called once at startup via lifespan."""
    _models["global"] = joblib.load(MODEL_DIR / "cortex_model_global.pkl")
    _models["bardeaux"] = joblib.load(MODEL_DIR / "cortex_model_Bardeaux.pkl")
    _models["encoder"] = joblib.load(MODEL_DIR / "category_encoder_v3.pkl")
    with open(MODEL_DIR / "cortex_config_v3.json") as f:
        _config.update(json.load(f))

def unload_models():
    """Called at shutdown."""
    _models.clear()
    _config.clear()

def predict(sqft: float, category: str, material_lines: int = 5,
            labor_lines: int = 2, has_subs: int = 0, complexity: int = 10) -> dict:
    """Prediction logic adapted from predict_final.py."""
    import numpy as np

    # Build feature arrays
    X_cat = np.array([[sqft, material_lines, labor_lines, has_subs, complexity]])
    cat_enc = _config["category_mapping"].get(category, 0)
    X_global = np.array([[sqft, material_lines, labor_lines, has_subs, complexity, cat_enc]])

    # Select model
    if category == "Bardeaux":
        prediction = _models["bardeaux"].predict(X_cat)[0]
        model_used = "Bardeaux (R2=0.65)"
        confidence = "HIGH"
    else:
        prediction = _models["global"].predict(X_global)[0]
        model_used = "Global (R2=0.59)"
        confidence = "MEDIUM" if category in ["Other", "Elastomere"] else "LOW"

    return {
        "estimate": round(float(prediction), 2),
        "range_low": round(float(prediction * 0.80), 2),
        "range_high": round(float(prediction * 1.20), 2),
        "model": model_used,
        "confidence": confidence
    }
```

### Pattern 2: Pydantic v2 Request Validation with Field Constraints

**What:** Define request/response models with built-in validation
**When to use:** All API endpoints accepting JSON input
**Source:** [Pydantic v2 Validators](https://docs.pydantic.dev/latest/concepts/validators/)

```python
# app/schemas/estimate.py
from pydantic import BaseModel, Field, field_validator
from typing import Literal

class EstimateRequest(BaseModel):
    sqft: float = Field(..., gt=0, le=100000, description="Square footage of roof")
    category: str = Field(..., description="Job category")
    material_lines: int = Field(default=5, ge=0, le=100)
    labor_lines: int = Field(default=2, ge=0, le=50)
    has_subs: Literal[0, 1] = Field(default=0)
    complexity: int = Field(default=10, ge=1, le=100)

    @field_validator("category")
    @classmethod
    def validate_category(cls, v: str) -> str:
        valid = ["Bardeaux", "Elastomere", "Other", "Gutters",
                 "Heat Cables", "Insulation", "Service Call",
                 "Skylights", "Unknown", "Ventilation"]
        if v not in valid:
            raise ValueError(f"category must be one of: {valid}")
        return v

class EstimateResponse(BaseModel):
    estimate: float
    range_low: float
    range_high: float
    confidence: Literal["HIGH", "MEDIUM", "LOW"]
    model: str
```

### Pattern 3: CORS Middleware Configuration

**What:** Enable cross-origin requests from frontend
**When to use:** When frontend on different origin (localhost:3000) calls backend
**Source:** [FastAPI CORS](https://fastapi.tiangolo.com/tutorial/cors/)

```python
# app/main.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend origin
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

### Pattern 4: Environment Configuration with Pydantic Settings

**What:** Type-validated environment variables
**When to use:** Any configuration that varies by environment

```python
# app/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    cors_origins: list[str] = ["http://localhost:3000"]
    model_dir: str = "app/models"

    class Config:
        env_file = ".env"

settings = Settings()
```

### Anti-Patterns to Avoid

- **Loading model on every request:** 100-500ms overhead per request. Use lifespan instead.
- **Using `async def` for CPU-bound prediction:** Blocks event loop. Use `def` for sklearn predict.
- **Hardcoding CORS origins:** Use environment variables for production flexibility.
- **Endpoint calling endpoint:** Creates extra serialization overhead. Share service functions.

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Request validation | Manual if/else checks | Pydantic Field constraints | Automatic 422 errors with detailed messages |
| CORS handling | Manual headers | CORSMiddleware | Handles preflight, edge cases |
| JSON serialization | Manual json.dumps | Pydantic response_model | Automatic, handles numpy types |
| Model loading | Load per-request | Lifespan context manager | Official FastAPI pattern, 100x faster |
| Error responses | Manual try/except everywhere | HTTPException + exception_handler | Consistent format, auto-documented |

**Key insight:** FastAPI's Pydantic integration handles 90% of input validation and error formatting automatically. Manual validation code is almost always a mistake.

## Common Pitfalls

### Pitfall 1: Using async def for ML Inference

**What goes wrong:** sklearn.predict() is CPU-bound, blocks the event loop
**Why it happens:** Developers assume async is always better
**How to avoid:** Use regular `def` for prediction endpoints (FastAPI runs in threadpool)
**Warning signs:** High latency under concurrent load

```python
# WRONG - blocks event loop
@router.post("/estimate")
async def estimate(request: EstimateRequest):
    result = model.predict(...)  # CPU-bound, blocks!
    return result

# CORRECT - runs in threadpool
@router.post("/estimate")
def estimate(request: EstimateRequest):
    result = model.predict(...)  # Runs in separate thread
    return result
```

### Pitfall 2: Not Binding to Railway's PORT

**What goes wrong:** App starts but Railway can't route traffic to it
**Why it happens:** Hardcoded port 8000 doesn't match Railway's assigned port
**How to avoid:** Use `$PORT` environment variable

```python
# Dockerfile CMD or Procfile
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### Pitfall 3: Model Files Not Included in Docker Image

**What goes wrong:** FileNotFoundError when loading .pkl files
**Why it happens:** .pkl files in .dockerignore or not copied
**How to avoid:** Explicitly COPY model files in Dockerfile

```dockerfile
COPY app/models/*.pkl app/models/
COPY app/models/*.json app/models/
```

### Pitfall 4: Pydantic v1 Syntax in v2

**What goes wrong:** Deprecation warnings or errors
**Why it happens:** Using `@validator` instead of `@field_validator`
**How to avoid:** Use Pydantic v2 syntax

```python
# Pydantic v1 (deprecated)
from pydantic import validator
@validator("field")
def check_field(cls, v):
    ...

# Pydantic v2 (current)
from pydantic import field_validator
@field_validator("field")
@classmethod
def check_field(cls, v):
    ...
```

### Pitfall 5: Missing CORS Middleware Order

**What goes wrong:** CORS errors despite correct configuration
**Why it happens:** CORSMiddleware added after other middleware that raises errors
**How to avoid:** Add CORSMiddleware first, before other middleware

```python
# Add CORS first
app.add_middleware(CORSMiddleware, ...)
app.add_middleware(OtherMiddleware, ...)  # After CORS
```

## Code Examples

Verified patterns from official sources:

### Health Check Endpoint

```python
# app/routers/health.py
from fastapi import APIRouter

router = APIRouter(tags=["health"])

@router.get("/health")
def health_check():
    """Simple liveness check."""
    return {"status": "ok", "version": "1.0.0"}
```

### Estimate Endpoint

```python
# app/routers/estimate.py
from fastapi import APIRouter, HTTPException
from app.schemas.estimate import EstimateRequest, EstimateResponse
from app.services.predictor import predict

router = APIRouter(tags=["estimate"])

@router.post("/estimate", response_model=EstimateResponse)
def get_estimate(request: EstimateRequest):
    """
    Get price estimate for roofing job.

    Returns estimate with range and confidence level.
    """
    try:
        result = predict(
            sqft=request.sqft,
            category=request.category,
            material_lines=request.material_lines,
            labor_lines=request.labor_lines,
            has_subs=request.has_subs,
            complexity=request.complexity
        )
        return EstimateResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### Main Application Entry Point

```python
# app/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import health, estimate
from app.services.predictor import load_models, unload_models
from app.config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    load_models()
    yield
    unload_models()

app = FastAPI(
    title="TOITURELV Cortex API",
    description="ML-powered roofing estimate API",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(estimate.router)
```

### Test Example

```python
# tests/test_estimate.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_estimate_valid_request():
    response = client.post(
        "/estimate",
        json={
            "sqft": 1500,
            "category": "Bardeaux",
            "material_lines": 8,
            "labor_lines": 3,
            "has_subs": 0,
            "complexity": 15
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "estimate" in data
    assert "range_low" in data
    assert "range_high" in data
    assert data["confidence"] in ["HIGH", "MEDIUM", "LOW"]

def test_estimate_invalid_category():
    response = client.post(
        "/estimate",
        json={"sqft": 1500, "category": "InvalidCategory"}
    )
    assert response.status_code == 422  # Validation error

def test_estimate_negative_sqft():
    response = client.post(
        "/estimate",
        json={"sqft": -100, "category": "Bardeaux"}
    )
    assert response.status_code == 422  # Validation error

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
```

### Dockerfile for Railway

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY app/ app/

# Railway provides PORT env var
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
```

### requirements.txt

```
fastapi[standard]>=0.128.0
pydantic>=2.7.0
pydantic-settings>=2.0.0
joblib>=1.3.0
numpy>=1.26.0
scikit-learn>=1.4.0
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `@app.on_event("startup")` | `lifespan` context manager | FastAPI 0.93+ | Deprecated event handlers, use lifespan |
| Pydantic v1 `@validator` | Pydantic v2 `@field_validator` | Pydantic 2.0 (2023) | 5-10x faster validation |
| Pydantic v1 `class Config` | Pydantic v2 `model_config` | Pydantic 2.0 | New syntax, same functionality |
| Flask-style sync routes | Async-first FastAPI | Always | Better concurrency |
| gunicorn + uvicorn workers | Single uvicorn (containers) | Kubernetes era | One process per container pattern |

**Deprecated/outdated:**
- `@app.on_event("startup")` / `@app.on_event("shutdown")`: Use lifespan context manager
- Pydantic v1 entirely: FastAPI 0.126.0+ requires Pydantic v2
- Python 3.8: Not supported by FastAPI 0.125.0+

## Open Questions

Things that couldn't be fully resolved:

1. **Elastomere vs Elastomere encoding**
   - What we know: Config uses "Elastomere" (with accent), predict_final.py checks "Elastomere"
   - What's unclear: Whether frontend will send accent or not
   - Recommendation: Accept both in validation, normalize to accented version

2. **Model file location in deployment**
   - What we know: Models currently in cortex-data/, need to be accessible in Docker
   - What's unclear: Whether to copy into app/models/ or mount as volume
   - Recommendation: Copy into app/models/ directory for simplicity (no volume mounts needed)

## Sources

### Primary (HIGH confidence)
- [FastAPI Official Documentation - Lifespan Events](https://fastapi.tiangolo.com/advanced/events/) - Model loading pattern
- [FastAPI Official Documentation - CORS](https://fastapi.tiangolo.com/tutorial/cors/) - CORS configuration
- [FastAPI Official Documentation - Bigger Applications](https://fastapi.tiangolo.com/tutorial/bigger-applications/) - Project structure
- [FastAPI Official Documentation - Testing](https://fastapi.tiangolo.com/tutorial/testing/) - TestClient usage
- [Pydantic v2 Validators](https://docs.pydantic.dev/latest/concepts/validators/) - field_validator syntax
- [PyPI FastAPI](https://pypi.org/project/fastapi/) - Version 0.128.0, Python >=3.9

### Secondary (MEDIUM confidence)
- [Railway FastAPI Deployment Guide](https://docs.railway.com/guides/fastapi) - Railway-specific configuration
- [FastAPI Best Practices GitHub](https://github.com/zhanymkanov/fastapi-best-practices) - Project structure patterns
- [FastAPI ML Serving Articles](https://medium.com/analytics-vidhya/serve-a-machine-learning-model-using-sklearn-fastapi-and-docker-85aabf96729b) - sklearn model serving patterns

### Tertiary (LOW confidence)
- Various Medium articles on FastAPI performance - Async/sync guidance (verified with official docs)

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - Verified with PyPI and official FastAPI docs
- Architecture: HIGH - Official FastAPI documentation patterns
- Pitfalls: HIGH - Combination of official docs and verified community patterns

**Research date:** 2026-01-18
**Valid until:** 2026-02-18 (30 days - FastAPI is stable, Pydantic v2 is mature)
