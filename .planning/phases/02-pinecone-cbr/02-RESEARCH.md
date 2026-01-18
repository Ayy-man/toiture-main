# Phase 2: Pinecone CBR - Research

**Researched:** 2026-01-18
**Domain:** Pinecone vector database, sentence-transformers embedding generation, FastAPI integration
**Confidence:** HIGH

## Summary

This phase focuses on integrating Pinecone vector database for Case-Based Reasoning (CBR) by uploading pre-generated embeddings and enabling similarity queries at runtime. The existing codebase contains 8,132 pre-computed embeddings (384 dimensions) generated with `paraphrase-multilingual-MiniLM-L12-v2` and structured case metadata in `cbr_cases.json`.

The standard approach uses the modern `pinecone` package (not the deprecated `pinecone-client`), batch upserting with a batch size of 500-1000 for 384-dim vectors, and query-time embedding generation using `sentence-transformers`. For the free tier, a single serverless index in `us-east-1` with the `cosine` metric is optimal for this embedding model.

**Primary recommendation:** Use `pinecone>=8.0.0` with gRPC extras for performance, batch upsert embeddings with metadata containing key pricing fields (total, per_sqft, category), load sentence-transformers model at startup alongside sklearn models, and query with top_k=5 filtered by category when relevant.

## Standard Stack

The established libraries/tools for this domain:

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| pinecone | >=8.0.0 | Vector database client | Official Pinecone SDK, renamed from pinecone-client |
| pinecone[grpc] | >=8.0.0 | gRPC performance boost | Multiplexing for faster upserts/queries |
| sentence-transformers | >=3.0.0 | Query embedding generation | Standard for paraphrase-multilingual-MiniLM-L12-v2 |
| numpy | >=1.26.0 | Array operations | Loading .npz embeddings |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| tqdm | >=4.66.0 | Progress bars | Optional for batch upsert visibility |
| torch | >=2.0.0 | ML backend | Required by sentence-transformers |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| pinecone[grpc] | pinecone (REST only) | gRPC is 10-20% faster for bulk operations |
| sentence-transformers | transformers + manual pooling | sentence-transformers is simpler, handles pooling automatically |
| Pinecone | Qdrant/Weaviate | Self-hosted alternatives; Pinecone is managed, matches project spec |

**Installation:**
```bash
pip install "pinecone[grpc]>=8.0.0" sentence-transformers numpy tqdm
```

**Note:** Python 3.10+ required for pinecone v8. If using Python 3.9, use `pinecone>=5.0.0,<8.0.0`.

## Architecture Patterns

### Recommended Project Structure

Extend the Phase 1 backend structure:

```
backend/
├── app/
│   ├── services/
│   │   ├── predictor.py      # Existing ML prediction
│   │   ├── pinecone_cbr.py   # NEW: Pinecone operations
│   │   └── embeddings.py     # NEW: Query embedding generation
│   ├── routers/
│   │   └── estimate.py       # UPDATE: Add similar_cases
│   └── schemas/
│       └── estimate.py       # UPDATE: Add SimilarCase model
├── scripts/
│   └── upload_embeddings.py  # One-time upload script (not runtime)
```

### Pattern 1: Pinecone Client Initialization at Startup

**What:** Initialize Pinecone client and connect to index once at startup
**When to use:** Always - avoid re-creating client per request
**Example:**

```python
# app/services/pinecone_cbr.py
from pinecone.grpc import PineconeGRPC as Pinecone
from app.config import settings

# Module-level storage
_pc = None
_index = None

def init_pinecone():
    """Initialize Pinecone client and connect to index."""
    global _pc, _index
    _pc = Pinecone(api_key=settings.pinecone_api_key)
    _index = _pc.Index(host=settings.pinecone_index_host)

def get_index():
    """Get the Pinecone index for operations."""
    if _index is None:
        raise RuntimeError("Pinecone not initialized. Call init_pinecone() first.")
    return _index

def close_pinecone():
    """Cleanup on shutdown."""
    global _pc, _index
    _pc = None
    _index = None
```

### Pattern 2: Batch Upsert with Metadata

**What:** Upload vectors in batches of 500-1000 with flattened metadata
**When to use:** One-time upload script, not runtime
**Example:**

```python
# scripts/upload_embeddings.py
import numpy as np
import json
from pinecone.grpc import PineconeGRPC as Pinecone
from tqdm import tqdm

def upload_embeddings(api_key: str, index_host: str):
    # Load pre-computed data
    embeddings_data = np.load("cortex-data/cbr_embeddings.npz")
    case_ids = embeddings_data["case_ids"]  # shape: (8132,)
    embeddings = embeddings_data["embeddings"]  # shape: (8132, 384)

    with open("cortex-data/cbr_cases.json") as f:
        cases = {c["case_id"]: c for c in json.load(f)}

    pc = Pinecone(api_key=api_key)
    index = pc.Index(host=index_host)

    # Prepare vectors with metadata
    batch_size = 500  # Optimal for 384-dim vectors
    vectors = []

    for i, (case_id, embedding) in enumerate(zip(case_ids, embeddings)):
        case = cases.get(str(case_id), {})

        # Flatten metadata for Pinecone (max 40KB per record)
        metadata = {
            "case_id": str(case_id),
            "year": case.get("year"),
            "category": case.get("features", {}).get("category", "Unknown"),
            "sqft": case.get("features", {}).get("sqft"),
            "total": case.get("pricing", {}).get("total"),
            "per_sqft": case.get("pricing", {}).get("per_sqft"),
            "material_sell": case.get("pricing", {}).get("material_sell"),
            "labor_sell": case.get("pricing", {}).get("labor_sell"),
            "complexity_score": case.get("features", {}).get("complexity_score"),
        }
        # Remove None values (Pinecone doesn't accept null in metadata)
        metadata = {k: v for k, v in metadata.items() if v is not None}

        vectors.append({
            "id": str(case_id),
            "values": embedding.tolist(),
            "metadata": metadata
        })

    # Upsert in batches
    for i in tqdm(range(0, len(vectors), batch_size), desc="Uploading"):
        batch = vectors[i:i + batch_size]
        index.upsert(vectors=batch, namespace="cbr")

    print(f"Uploaded {len(vectors)} vectors to Pinecone")
```

### Pattern 3: Query-Time Embedding Generation

**What:** Generate embeddings for query text using the same model used for case embeddings
**When to use:** Runtime, when processing estimate requests
**Example:**

```python
# app/services/embeddings.py
from sentence_transformers import SentenceTransformer
from typing import List

# Module-level model storage
_model = None

def load_embedding_model():
    """Load sentence-transformers model at startup."""
    global _model
    _model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
    # Optional: move to GPU if available
    # _model = _model.to('cuda')

def unload_embedding_model():
    """Cleanup on shutdown."""
    global _model
    _model = None

def generate_query_embedding(text: str) -> List[float]:
    """Generate 384-dim embedding for query text."""
    if _model is None:
        raise RuntimeError("Embedding model not loaded")
    embedding = _model.encode(text, convert_to_numpy=True)
    return embedding.tolist()

def build_query_text(sqft: float, category: str, complexity: int) -> str:
    """Build query text from estimate inputs for embedding."""
    # Match the format used when creating case embeddings
    return f"Roofing job: {category}, {sqft} sqft, complexity {complexity}"
```

### Pattern 4: Similar Cases Query

**What:** Query Pinecone for top 5 similar cases with optional category filter
**When to use:** Within /estimate endpoint to find similar historical jobs
**Example:**

```python
# app/services/pinecone_cbr.py
from typing import List, Dict, Any, Optional

def query_similar_cases(
    query_vector: List[float],
    top_k: int = 5,
    category_filter: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Query Pinecone for similar cases."""
    index = get_index()

    # Build filter if category specified
    filter_dict = None
    if category_filter:
        filter_dict = {"category": {"$eq": category_filter}}

    results = index.query(
        vector=query_vector,
        top_k=top_k,
        include_metadata=True,
        namespace="cbr",
        filter=filter_dict
    )

    # Format results for API response
    similar_cases = []
    for match in results.matches:
        similar_cases.append({
            "case_id": match.id,
            "score": round(match.score, 4),  # Cosine similarity
            "category": match.metadata.get("category"),
            "sqft": match.metadata.get("sqft"),
            "total": match.metadata.get("total"),
            "per_sqft": match.metadata.get("per_sqft"),
            "year": match.metadata.get("year"),
        })

    return similar_cases
```

### Pattern 5: Updated Estimate Endpoint

**What:** Integrate similar cases into existing /estimate endpoint
**When to use:** Extending Phase 1 implementation
**Example:**

```python
# app/routers/estimate.py (updated)
from app.services.embeddings import generate_query_embedding, build_query_text
from app.services.pinecone_cbr import query_similar_cases

@router.post("/estimate", response_model=EstimateResponse)
def get_estimate(request: EstimateRequest):
    # Existing ML prediction
    prediction = predict(
        sqft=request.sqft,
        category=request.category,
        # ... other params
    )

    # Generate query embedding and find similar cases
    query_text = build_query_text(request.sqft, request.category, request.complexity)
    query_vector = generate_query_embedding(query_text)
    similar_cases = query_similar_cases(
        query_vector=query_vector,
        top_k=5,
        category_filter=request.category  # Optional: filter by same category
    )

    return EstimateResponse(
        estimate=prediction["estimate"],
        range_low=prediction["range_low"],
        range_high=prediction["range_high"],
        confidence=prediction["confidence"],
        model=prediction["model"],
        similar_cases=similar_cases,  # NEW field
    )
```

### Anti-Patterns to Avoid

- **Creating Pinecone client per request:** Creates connection overhead. Initialize once at startup.
- **Uploading embeddings at runtime:** Upload is a one-time operation. Use separate script.
- **Loading embedding model per request:** 2-3 second overhead. Load at startup via lifespan.
- **Storing full case text in metadata:** 40KB limit. Store only essential fields for display.
- **Using REST when gRPC available:** gRPC is faster for bulk operations.

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Vector similarity search | Manual numpy cosine similarity | Pinecone query | Scales to millions, approximate nearest neighbors |
| Embedding generation | Manual transformer + pooling | sentence-transformers encode() | Handles tokenization, pooling, normalization |
| Batch upload progress | Manual counter | tqdm with show_progress=True | Built-in SDK support |
| Connection pooling | Manual HTTP session management | Pinecone SDK pool_threads | Handles concurrency correctly |

**Key insight:** The embeddings are already generated. This phase is about upload and retrieval, not embedding generation. The only runtime embedding is for the query text, which is fast (50-100ms).

## Common Pitfalls

### Pitfall 1: Using Deprecated pinecone-client Package

**What goes wrong:** Import errors, API incompatibilities, or using outdated patterns
**Why it happens:** Old tutorials reference `pinecone-client` which was renamed
**How to avoid:** Use `pinecone` package (v5.1.0+), uninstall `pinecone-client` first
**Warning signs:** `pinecone.init()` in code (old v2 API)

```bash
# WRONG
pip install pinecone-client

# CORRECT
pip uninstall pinecone-client
pip install "pinecone[grpc]>=8.0.0"
```

### Pitfall 2: Not Handling None Values in Metadata

**What goes wrong:** Upsert fails with "null value not allowed"
**Why it happens:** Pinecone metadata doesn't accept None/null values
**How to avoid:** Filter out None values before upserting
**Warning signs:** `ValueError` during upsert

```python
# WRONG
metadata = {"sqft": None, "total": 15000}

# CORRECT
metadata = {"sqft": None, "total": 15000}
metadata = {k: v for k, v in metadata.items() if v is not None}
```

### Pitfall 3: Mismatched Embedding Dimensions

**What goes wrong:** Upsert or query fails with dimension mismatch error
**Why it happens:** Index created with wrong dimension, or using different embedding model
**How to avoid:** Create index with dimension=384 (matches MiniLM-L12-v2)
**Warning signs:** "Vector dimension X does not match index dimension Y"

```python
# CORRECT: 384 dimensions for paraphrase-multilingual-MiniLM-L12-v2
pc.create_index(
    name="toiturelv-cortex",
    dimension=384,  # Must match embedding model output
    metric="cosine",
    spec=ServerlessSpec(cloud="aws", region="us-east-1")
)
```

### Pitfall 4: Blocking Event Loop with Embedding Model

**What goes wrong:** High latency, timeouts under load
**Why it happens:** SentenceTransformer.encode() is CPU-bound, blocks async event loop
**How to avoid:** Use regular `def` (not `async def`) for endpoint, FastAPI runs in threadpool
**Warning signs:** p99 latency spikes under concurrent requests

```python
# CORRECT - Regular function, runs in threadpool
@router.post("/estimate")
def get_estimate(request: EstimateRequest):  # NOT async def
    embedding = model.encode(text)  # CPU-bound work
    ...
```

### Pitfall 5: Not Using Index Host URL

**What goes wrong:** Connection failures, "index not found" errors
**Why it happens:** Using index name instead of host URL in v4+ SDK
**How to avoid:** Store and use the index host URL from creation response
**Warning signs:** `PineconeConnectionError`

```python
# WRONG (old API)
index = pc.Index(name="my-index")

# CORRECT (v4+ API) - Use host URL
index = pc.Index(host="my-index-abc123.svc.aped-1234-abcd.pinecone.io")
```

### Pitfall 6: Free Tier Region Restriction

**What goes wrong:** Index creation fails
**Why it happens:** Free tier only supports us-east-1 region
**How to avoid:** Always use `us-east-1` for Starter plan
**Warning signs:** "Region not available for your plan"

## Code Examples

Verified patterns from official sources:

### Complete Upload Script

```python
# scripts/upload_embeddings.py
#!/usr/bin/env python3
"""One-time script to upload CBR embeddings to Pinecone."""

import os
import json
import numpy as np
from pinecone.grpc import PineconeGRPC as Pinecone
from pinecone import ServerlessSpec
from tqdm import tqdm

def main():
    # Configuration
    api_key = os.environ["PINECONE_API_KEY"]
    index_name = os.environ.get("PINECONE_INDEX_NAME", "toiturelv-cortex")

    # Initialize Pinecone
    pc = Pinecone(api_key=api_key)

    # Create index if it doesn't exist
    if index_name not in [idx.name for idx in pc.list_indexes()]:
        print(f"Creating index {index_name}...")
        pc.create_index(
            name=index_name,
            dimension=384,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1")
        )

    # Get index host
    index_info = pc.describe_index(index_name)
    index = pc.Index(host=index_info.host)

    # Load embeddings
    print("Loading embeddings...")
    data = np.load("cortex-data/cbr_embeddings.npz")
    case_ids = data["case_ids"]
    embeddings = data["embeddings"]

    # Load case metadata
    with open("cortex-data/cbr_cases.json") as f:
        cases = {str(c["case_id"]): c for c in json.load(f)}

    # Prepare vectors
    print("Preparing vectors...")
    vectors = []
    for case_id, embedding in zip(case_ids, embeddings):
        case = cases.get(str(case_id), {})
        features = case.get("features", {})
        pricing = case.get("pricing", {})

        metadata = {
            "case_id": str(case_id),
            "year": case.get("year"),
            "category": features.get("category", "Unknown"),
            "sqft": features.get("sqft"),
            "total": pricing.get("total"),
            "per_sqft": pricing.get("per_sqft"),
            "material_sell": pricing.get("material_sell"),
            "labor_sell": pricing.get("labor_sell"),
            "complexity_score": features.get("complexity_score"),
        }
        # Remove None values
        metadata = {k: v for k, v in metadata.items() if v is not None}

        vectors.append({
            "id": str(case_id),
            "values": embedding.tolist(),
            "metadata": metadata
        })

    # Upsert in batches
    batch_size = 500
    print(f"Uploading {len(vectors)} vectors in batches of {batch_size}...")
    for i in tqdm(range(0, len(vectors), batch_size)):
        batch = vectors[i:i + batch_size]
        index.upsert(vectors=batch, namespace="cbr")

    # Verify
    stats = index.describe_index_stats()
    print(f"\nUpload complete! Index stats: {stats}")

if __name__ == "__main__":
    main()
```

### Embeddings Service Module

```python
# app/services/embeddings.py
"""Query embedding generation using sentence-transformers."""

from sentence_transformers import SentenceTransformer
from typing import List
import logging

logger = logging.getLogger(__name__)

_model: SentenceTransformer = None

def load_embedding_model():
    """Load the embedding model at startup. Called from lifespan."""
    global _model
    logger.info("Loading sentence-transformers model...")
    _model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
    logger.info("Embedding model loaded successfully")

def unload_embedding_model():
    """Cleanup on shutdown."""
    global _model
    _model = None

def generate_query_embedding(text: str) -> List[float]:
    """Generate 384-dim embedding for query text.

    Args:
        text: Query text to embed

    Returns:
        List of 384 floats representing the embedding

    Raises:
        RuntimeError: If model not loaded
    """
    if _model is None:
        raise RuntimeError("Embedding model not loaded. Ensure lifespan started.")
    embedding = _model.encode(text, convert_to_numpy=True)
    return embedding.tolist()

def build_query_text(
    sqft: float,
    category: str,
    complexity: int,
    material_lines: int = None,
    labor_lines: int = None
) -> str:
    """Build query text from estimate inputs.

    Constructs a text representation of the job for semantic similarity.
    Should match the format used when generating case embeddings.
    """
    parts = [f"Toiture {category}"]
    if sqft:
        parts.append(f"{sqft} pieds carres")
    parts.append(f"complexite {complexity}")
    if material_lines:
        parts.append(f"{material_lines} lignes materiaux")
    if labor_lines:
        parts.append(f"{labor_lines} lignes main-d'oeuvre")
    return ", ".join(parts)
```

### Pinecone CBR Service Module

```python
# app/services/pinecone_cbr.py
"""Pinecone operations for Case-Based Reasoning."""

from pinecone.grpc import PineconeGRPC as Pinecone
from typing import List, Dict, Any, Optional
import logging
from app.config import settings

logger = logging.getLogger(__name__)

_pc: Pinecone = None
_index = None

def init_pinecone():
    """Initialize Pinecone client. Called from lifespan."""
    global _pc, _index
    logger.info("Connecting to Pinecone...")
    _pc = Pinecone(api_key=settings.pinecone_api_key)
    _index = _pc.Index(host=settings.pinecone_index_host)
    logger.info("Pinecone connected successfully")

def close_pinecone():
    """Cleanup on shutdown."""
    global _pc, _index
    _pc = None
    _index = None

def query_similar_cases(
    query_vector: List[float],
    top_k: int = 5,
    category_filter: Optional[str] = None,
    namespace: str = "cbr"
) -> List[Dict[str, Any]]:
    """Query Pinecone for similar historical cases.

    Args:
        query_vector: 384-dim embedding of the query
        top_k: Number of similar cases to return
        category_filter: Optional category to filter results
        namespace: Pinecone namespace (default: "cbr")

    Returns:
        List of similar cases with metadata and similarity scores
    """
    if _index is None:
        raise RuntimeError("Pinecone not initialized")

    filter_dict = None
    if category_filter:
        filter_dict = {"category": {"$eq": category_filter}}

    results = _index.query(
        vector=query_vector,
        top_k=top_k,
        include_metadata=True,
        namespace=namespace,
        filter=filter_dict
    )

    similar_cases = []
    for match in results.matches:
        similar_cases.append({
            "case_id": match.id,
            "similarity": round(float(match.score), 4),
            "category": match.metadata.get("category"),
            "sqft": match.metadata.get("sqft"),
            "total": match.metadata.get("total"),
            "per_sqft": match.metadata.get("per_sqft"),
            "year": match.metadata.get("year"),
        })

    return similar_cases
```

### Updated Response Schema

```python
# app/schemas/estimate.py (additions)
from pydantic import BaseModel
from typing import List, Optional

class SimilarCase(BaseModel):
    """A similar historical case from CBR."""
    case_id: str
    similarity: float  # Cosine similarity score 0-1
    category: Optional[str] = None
    sqft: Optional[float] = None
    total: Optional[float] = None
    per_sqft: Optional[float] = None
    year: Optional[int] = None

class EstimateResponse(BaseModel):
    """Response from /estimate endpoint."""
    estimate: float
    range_low: float
    range_high: float
    confidence: str
    model: str
    similar_cases: List[SimilarCase] = []  # NEW field
```

### Updated Lifespan

```python
# app/main.py (updated lifespan)
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.services.predictor import load_models, unload_models
from app.services.embeddings import load_embedding_model, unload_embedding_model
from app.services.pinecone_cbr import init_pinecone, close_pinecone

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    load_models()           # ML prediction models
    load_embedding_model()  # sentence-transformers model
    init_pinecone()         # Pinecone connection
    yield
    # Shutdown
    close_pinecone()
    unload_embedding_model()
    unload_models()
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `pinecone-client` package | `pinecone` package | v5.1.0 (2024) | Package renamed, new import |
| `pinecone.init(api_key=...)` | `Pinecone(api_key=...)` | v3.0.0 (2023) | Object-oriented client |
| `index = pinecone.Index("name")` | `index = pc.Index(host="...")` | v4.0.0 (2024) | Must use host URL, not name |
| Pod-based indexes | Serverless indexes | 2024 | Default for new indexes |
| Python 3.8 support | Python 3.10+ required | v8.0.0 (2025) | 3.9 EOL |

**Deprecated/outdated:**
- `pinecone-client` package: Renamed to `pinecone` in v5.1.0
- `pinecone.init()`: Replaced with `Pinecone()` class constructor
- Pod-based indexes: Serverless is recommended for new projects
- `GRPCIndex`: Replaced with `PineconeGRPC.Index()`

## Open Questions

Things that couldn't be fully resolved:

1. **Query text format matching case embeddings**
   - What we know: Embeddings were generated from case text (description + materials)
   - What's unclear: Exact text format used during embedding generation
   - Recommendation: Check cortex-data scripts that generated embeddings, match format

2. **Category filter vs no filter for queries**
   - What we know: Filtering by category returns more relevant cases
   - What's unclear: Whether cross-category similarity is valuable
   - Recommendation: Start with category filter, make optional based on user feedback

3. **Pinecone index host URL storage**
   - What we know: Need to store host URL after index creation
   - What's unclear: Whether to store in .env or create a config file
   - Recommendation: Store as PINECONE_INDEX_HOST environment variable

## Sources

### Primary (HIGH confidence)
- [Pinecone Python SDK Documentation](https://docs.pinecone.io/reference/python-sdk) - Client initialization, index operations
- [Pinecone Upsert Records Guide](https://docs.pinecone.io/guides/index-data/upsert-data) - Batch upsert patterns
- [PyPI pinecone package](https://pypi.org/project/pinecone/) - v8.0.0 release notes, Python 3.10+ requirement
- [GitHub pinecone-python-client](https://github.com/pinecone-io/pinecone-python-client) - Migration guide from pinecone-client

### Secondary (MEDIUM confidence)
- [HuggingFace paraphrase-multilingual-MiniLM-L12-v2](https://huggingface.co/sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2) - Model specs, 384 dimensions
- [Pinecone Pricing](https://www.pinecone.io/pricing/) - Free tier limits (5 indexes, 2GB storage, us-east-1 only)
- [Pinecone Database Limits](https://docs.pinecone.io/reference/api/database-limits) - Batch size limits per dimension

### Tertiary (LOW confidence)
- DataCamp Pinecone course - Batch upsert patterns (verified with official docs)
- Community forum posts on upsert syntax (verified with official docs)

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - Verified with PyPI, official Pinecone docs
- Architecture: HIGH - Based on official SDK patterns and Phase 1 structure
- Pitfalls: HIGH - Documented in official migration guides and release notes

**Research date:** 2026-01-18
**Valid until:** 2026-02-18 (30 days - Pinecone SDK is actively developed, check for updates)

---

## Appendix: Data File Reference

**Existing CBR data in cortex-data/:**

| File | Format | Content |
|------|--------|---------|
| `cbr_embeddings.npz` | NumPy compressed | 8,132 embeddings (384-dim) + case_ids |
| `cbr_cases.json` | JSON array | 8,293 structured cases with full metadata |

**Embedding dimensions:** 384 (paraphrase-multilingual-MiniLM-L12-v2)
**Case ID format:** String numeric ("1", "2", ..., "8132")

**Key metadata fields for Pinecone:**
- `case_id`: String identifier
- `category`: Job category (Bardeaux, Elastomere, etc.)
- `sqft`: Square footage (may be null)
- `total`: Total price
- `per_sqft`: Price per sqft (may be null)
- `year`: Job year (2020-2024)
