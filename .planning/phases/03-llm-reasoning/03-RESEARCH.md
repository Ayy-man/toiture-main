# Phase 3: LLM Reasoning - Research

**Researched:** 2026-01-18
**Domain:** OpenRouter API integration, LLM-generated reasoning, confidence assessment
**Confidence:** HIGH

## Summary

This phase adds LLM-generated reasoning to the estimate response, explaining why the AI arrived at its price and confidence level by referencing similar historical cases. OpenRouter provides a unified gateway to 400+ LLM models through an OpenAI-compatible API, allowing flexible model selection without vendor lock-in.

The standard approach uses the `openai` Python package pointed at OpenRouter's base URL (`https://openrouter.ai/api/v1`), making integration straightforward for anyone familiar with OpenAI's SDK. For this use case (generating brief reasoning text from structured data), a fast, cost-effective model like `anthropic/claude-haiku-4.5` or `openai/gpt-4o-mini` is recommended.

**Primary recommendation:** Use the `openai` Python package with OpenRouter's base URL, initialize client at startup with API key from environment, create a dedicated `llm_reasoning.py` service module, and add a `reasoning` field to `EstimateResponse`. Use synchronous calls since the endpoint is already sync (CPU-bound sklearn), with tenacity for retry with exponential backoff.

## Standard Stack

The established libraries/tools for this domain:

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| openai | >=1.0.0 | LLM API client | OpenRouter is OpenAI-compatible; no separate SDK needed |
| tenacity | >=8.2.0 | Retry with exponential backoff | Standard Python retry library, async support |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| httpx | >=0.27.0 | HTTP client (if not using openai pkg) | Only if avoiding openai dependency |
| python-dotenv | >=1.0.0 | Environment variable loading | Development convenience (already in use) |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| openai package | httpx direct | httpx is lighter but requires manual response parsing |
| openai package | Official OpenRouter SDK | OpenRouter SDK is auto-generated, openai is more mature |
| tenacity | Manual retry loop | tenacity provides exponential backoff, jitter, async support |
| claude-haiku-4.5 | gpt-4o-mini | GPT-4o-mini is 8x cheaper on output ($0.60 vs $5/M) but Haiku may be faster |

**Installation:**
```bash
pip install "openai>=1.0.0" "tenacity>=8.2.0"
```

## Architecture Patterns

### Recommended Project Structure

Extend the Phase 2 backend structure:

```
backend/
├── app/
│   ├── services/
│   │   ├── predictor.py        # ML prediction (Phase 1)
│   │   ├── pinecone_cbr.py     # Pinecone operations (Phase 2)
│   │   ├── embeddings.py       # Query embedding (Phase 2)
│   │   └── llm_reasoning.py    # NEW: LLM reasoning generation
│   ├── routers/
│   │   └── estimate.py         # UPDATE: Add reasoning to response
│   ├── schemas/
│   │   └── estimate.py         # UPDATE: Add reasoning field
│   └── config.py               # UPDATE: Add OpenRouter settings
```

### Pattern 1: OpenRouter Client Initialization at Startup

**What:** Initialize OpenAI client configured for OpenRouter once at startup
**When to use:** Always - avoid re-creating client per request
**Example:**

```python
# app/services/llm_reasoning.py
from openai import OpenAI
from app.config import settings

# Module-level client storage
_client: OpenAI = None

def init_llm_client():
    """Initialize OpenRouter client. Called from lifespan."""
    global _client
    _client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=settings.openrouter_api_key,
        default_headers={
            "HTTP-Referer": settings.app_url,
            "X-Title": "TOITURELV Cortex",
        },
    )

def close_llm_client():
    """Cleanup on shutdown."""
    global _client
    _client = None

def get_client() -> OpenAI:
    """Get the OpenRouter client for operations."""
    if _client is None:
        raise RuntimeError("LLM client not initialized. Call init_llm_client() first.")
    return _client
```

### Pattern 2: Reasoning Generation with Structured Prompt

**What:** Generate reasoning from estimate + similar cases using a structured prompt
**When to use:** Within /estimate endpoint after getting ML prediction and CBR results
**Example:**

```python
# app/services/llm_reasoning.py
from typing import List, Dict, Any
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
)
def generate_reasoning(
    estimate: float,
    confidence: str,
    sqft: float,
    category: str,
    similar_cases: List[Dict[str, Any]],
    model: str = None,
) -> str:
    """Generate reasoning explanation for estimate.

    Args:
        estimate: Predicted price
        confidence: Confidence level (HIGH/MEDIUM/LOW)
        sqft: Square footage
        category: Job category
        similar_cases: List of similar historical cases from CBR
        model: OpenRouter model identifier (optional, uses default)

    Returns:
        Human-readable reasoning string
    """
    from app.config import settings

    client = get_client()
    model = model or settings.openrouter_model

    # Format similar cases for prompt
    cases_text = format_similar_cases(similar_cases)

    prompt = f"""You are an expert roofing estimator assistant. Based on the ML model's estimate and similar historical cases, provide a brief explanation (2-3 sentences) for this roofing job estimate.

Job Details:
- Category: {category}
- Square footage: {sqft:,.0f} sq ft
- Estimated price: ${estimate:,.2f}
- Confidence: {confidence}

Similar Historical Cases:
{cases_text}

Explain why this estimate makes sense, referencing the similar cases. If confidence is LOW, mention what factors contribute to uncertainty. Be concise and professional."""

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful roofing estimation assistant. Be concise and reference specific data."},
            {"role": "user", "content": prompt},
        ],
        max_tokens=200,
        temperature=0.3,  # Lower temperature for consistent, factual responses
    )

    return response.choices[0].message.content.strip()


def format_similar_cases(cases: List[Dict[str, Any]]) -> str:
    """Format similar cases for prompt inclusion."""
    if not cases:
        return "No similar cases found."

    lines = []
    for i, case in enumerate(cases, 1):
        total = case.get("total", 0)
        sqft = case.get("sqft", "N/A")
        per_sqft = case.get("per_sqft", "N/A")
        category = case.get("category", "Unknown")
        similarity = case.get("similarity", 0)
        year = case.get("year", "N/A")

        lines.append(
            f"{i}. {category} job ({year}): ${total:,.0f} total, "
            f"{sqft} sqft, ${per_sqft}/sqft, {similarity:.0%} similar"
        )

    return "\n".join(lines)
```

### Pattern 3: Confidence Assessment in Reasoning

**What:** Include confidence factors in reasoning based on case similarity and spread
**When to use:** When generating reasoning to explain confidence level
**Example:**

```python
# app/services/llm_reasoning.py
def assess_confidence_factors(
    confidence: str,
    similar_cases: List[Dict[str, Any]],
) -> str:
    """Generate confidence assessment based on similar cases.

    Analyzes case similarity scores and price variance to explain confidence.
    """
    if not similar_cases:
        return "Limited confidence due to no similar historical cases found."

    # Calculate metrics
    similarities = [c.get("similarity", 0) for c in similar_cases]
    avg_similarity = sum(similarities) / len(similarities)

    totals = [c.get("total", 0) for c in similar_cases if c.get("total")]
    if totals:
        price_spread = (max(totals) - min(totals)) / (sum(totals) / len(totals))
    else:
        price_spread = 1.0  # High spread = low confidence

    factors = []

    if avg_similarity > 0.85:
        factors.append("highly similar historical cases")
    elif avg_similarity > 0.70:
        factors.append("moderately similar historical cases")
    else:
        factors.append("limited similarity to historical cases")

    if price_spread < 0.2:
        factors.append("consistent pricing in similar jobs")
    elif price_spread < 0.4:
        factors.append("moderate price variation in similar jobs")
    else:
        factors.append("high price variation in similar jobs")

    return f"Confidence based on: {', '.join(factors)}."
```

### Pattern 4: Updated Estimate Endpoint

**What:** Integrate LLM reasoning into existing /estimate endpoint
**When to use:** After Phase 2 implementation
**Example:**

```python
# app/routers/estimate.py (updated)
from app.services.llm_reasoning import generate_reasoning
import logging

logger = logging.getLogger(__name__)

@router.post("/estimate", response_model=EstimateResponse)
def create_estimate(request: EstimateRequest):
    # Existing: Get ML prediction
    result = predict(...)

    # Existing: Get similar cases from CBR (Phase 2)
    similar_cases = get_similar_cases(...)

    # NEW: Generate LLM reasoning
    try:
        reasoning = generate_reasoning(
            estimate=result["estimate"],
            confidence=result["confidence"],
            sqft=request.sqft,
            category=request.category,
            similar_cases=similar_cases,
        )
    except Exception as e:
        logger.warning(f"LLM reasoning failed: {e}")
        reasoning = None  # Graceful degradation

    return EstimateResponse(
        estimate=result["estimate"],
        range_low=result["range_low"],
        range_high=result["range_high"],
        confidence=result["confidence"],
        model=result["model"],
        similar_cases=similar_cases,
        reasoning=reasoning,  # NEW field
    )
```

### Pattern 5: Config Settings for OpenRouter

**What:** Add OpenRouter configuration to settings
**When to use:** Extending existing pydantic-settings config
**Example:**

```python
# app/config.py (additions)
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Existing settings...

    # OpenRouter settings
    openrouter_api_key: str = ""
    openrouter_model: str = "anthropic/claude-haiku-4.5"  # Default model
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    app_url: str = "https://toiturelv-cortex.railway.app"  # For HTTP-Referer header

    class Config:
        env_file = ".env"
```

### Anti-Patterns to Avoid

- **Creating OpenAI client per request:** Creates connection overhead. Initialize once at startup.
- **Using async client with sync endpoint:** The estimate endpoint is sync (sklearn is CPU-bound). Keep LLM calls sync.
- **No retry logic:** OpenRouter can have transient failures. Always use tenacity with exponential backoff.
- **Long prompts:** Keep prompts concise. Similar cases data can bloat token count.
- **High temperature for factual reasoning:** Use low temperature (0.3-0.5) for consistent, factual responses.
- **No timeout:** LLM calls can hang. Set reasonable timeouts (30-60s).
- **Blocking on LLM failure:** Gracefully degrade - return response without reasoning if LLM fails.

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| OpenRouter API client | Manual httpx/requests | openai package with base_url | Handles auth, parsing, streaming, types |
| Retry with backoff | Manual sleep loops | tenacity decorator | Handles jitter, max attempts, exceptions |
| Rate limit handling | Manual tracking | OpenRouter automatic fallback | Provider routing handles this |
| Streaming responses | Manual SSE parsing | openai package stream=True | Built-in chunk handling |

**Key insight:** OpenRouter is fully OpenAI-compatible, so use the mature openai package rather than raw HTTP. The only customization needed is `base_url` and optional headers.

## Common Pitfalls

### Pitfall 1: Not Handling LLM Timeouts

**What goes wrong:** Endpoint hangs indefinitely on slow LLM response
**Why it happens:** No timeout configured, model is overloaded
**How to avoid:** Set timeout in openai client or tenacity
**Warning signs:** Occasional 30s+ response times, gateway timeouts

```python
# Set timeout on client
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key,
    timeout=30.0,  # 30 second timeout
)
```

### Pitfall 2: Token Count Explosion with Similar Cases

**What goes wrong:** Prompt exceeds token limit, high API costs
**Why it happens:** Including full case details in prompt
**How to avoid:** Summarize cases, include only key fields (total, sqft, similarity)
**Warning signs:** 400 errors about token limits, unexpectedly high bills

```python
# WRONG - Too much data
prompt = f"Similar cases: {json.dumps(similar_cases)}"

# CORRECT - Summarized
prompt = f"Similar cases:\n{format_similar_cases(similar_cases[:5])}"
```

### Pitfall 3: No Graceful Degradation

**What goes wrong:** Entire /estimate endpoint fails when LLM is down
**Why it happens:** No try/except around LLM call, reasoning is required field
**How to avoid:** Make reasoning optional, catch exceptions, return None on failure
**Warning signs:** 500 errors when OpenRouter has issues

```python
# WRONG
reasoning = generate_reasoning(...)  # If this fails, entire endpoint fails

# CORRECT
try:
    reasoning = generate_reasoning(...)
except Exception as e:
    logger.warning(f"LLM reasoning failed: {e}")
    reasoning = None  # Response still works without reasoning
```

### Pitfall 4: Treating 401 as Fatal

**What goes wrong:** Request fails permanently on transient 401
**Why it happens:** OpenRouter occasionally returns 401 due to internal bugs
**How to avoid:** Include 401 in retryable exceptions
**Warning signs:** Intermittent "invalid API key" errors that resolve on retry

```python
from tenacity import retry_if_exception_type
from openai import AuthenticationError, APITimeoutError, APIConnectionError

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((AuthenticationError, APITimeoutError, APIConnectionError)),
)
def generate_reasoning(...):
    ...
```

### Pitfall 5: Using Wrong Model Identifier Format

**What goes wrong:** 404 "model not found" error
**Why it happens:** Model identifiers are `provider/model-name`, not just `model-name`
**How to avoid:** Always use full identifier with provider prefix
**Warning signs:** "Model not found" errors

```python
# WRONG
model = "claude-haiku-4.5"
model = "gpt-4o-mini"

# CORRECT
model = "anthropic/claude-haiku-4.5"
model = "openai/gpt-4o-mini"
```

### Pitfall 6: Forgetting HTTP-Referer Header

**What goes wrong:** Missing app attribution on OpenRouter dashboard
**Why it happens:** Optional header not included
**How to avoid:** Always include HTTP-Referer and X-Title headers
**Warning signs:** Can't track usage by app on OpenRouter dashboard

## Code Examples

Verified patterns from official sources:

### Complete LLM Reasoning Service Module

```python
# app/services/llm_reasoning.py
"""LLM reasoning generation using OpenRouter."""

import logging
from typing import List, Dict, Any, Optional

from openai import OpenAI
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)
from openai import AuthenticationError, APITimeoutError, APIConnectionError, RateLimitError

from app.config import settings

logger = logging.getLogger(__name__)

# Module-level client storage
_client: Optional[OpenAI] = None


def init_llm_client():
    """Initialize OpenRouter client. Called from lifespan."""
    global _client
    logger.info("Initializing OpenRouter LLM client...")
    _client = OpenAI(
        base_url=settings.openrouter_base_url,
        api_key=settings.openrouter_api_key,
        timeout=30.0,
        default_headers={
            "HTTP-Referer": settings.app_url,
            "X-Title": "TOITURELV Cortex",
        },
    )
    logger.info("OpenRouter client initialized")


def close_llm_client():
    """Cleanup on shutdown."""
    global _client
    _client = None


def get_client() -> OpenAI:
    """Get the OpenRouter client."""
    if _client is None:
        raise RuntimeError("LLM client not initialized")
    return _client


def format_similar_cases(cases: List[Dict[str, Any]]) -> str:
    """Format similar cases for prompt inclusion."""
    if not cases:
        return "No similar historical cases found."

    lines = []
    for i, case in enumerate(cases[:5], 1):  # Limit to 5 cases
        total = case.get("total")
        sqft = case.get("sqft")
        per_sqft = case.get("per_sqft")
        category = case.get("category", "Unknown")
        similarity = case.get("similarity", 0)
        year = case.get("year", "N/A")

        parts = [f"{i}. {category} ({year})"]
        if total:
            parts.append(f"${total:,.0f}")
        if sqft:
            parts.append(f"{sqft:,.0f} sqft")
        if per_sqft:
            parts.append(f"${per_sqft:.2f}/sqft")
        parts.append(f"{similarity:.0%} similar")

        lines.append(", ".join(parts))

    return "\n".join(lines)


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((
        AuthenticationError,  # OpenRouter can have transient 401s
        APITimeoutError,
        APIConnectionError,
        RateLimitError,
    )),
)
def generate_reasoning(
    estimate: float,
    confidence: str,
    sqft: float,
    category: str,
    similar_cases: List[Dict[str, Any]],
    model: Optional[str] = None,
) -> str:
    """Generate reasoning explanation for estimate.

    Args:
        estimate: Predicted price
        confidence: Confidence level (HIGH/MEDIUM/LOW)
        sqft: Square footage
        category: Job category
        similar_cases: List of similar historical cases from CBR
        model: OpenRouter model identifier (optional)

    Returns:
        Human-readable reasoning string (2-3 sentences)

    Raises:
        Exception: On API errors after retries exhausted
    """
    client = get_client()
    model = model or settings.openrouter_model

    cases_text = format_similar_cases(similar_cases)

    # Build confidence context
    if confidence == "HIGH":
        confidence_context = "The model has high confidence in this estimate."
    elif confidence == "MEDIUM":
        confidence_context = "The model has moderate confidence. Some variation is expected."
    else:
        confidence_context = "The model has low confidence due to limited similar data or high variance."

    prompt = f"""Based on the ML estimate and similar historical roofing jobs, explain this estimate in 2-3 sentences.

Job: {category}, {sqft:,.0f} sq ft
Estimate: ${estimate:,.2f}
Confidence: {confidence}
{confidence_context}

Similar Jobs:
{cases_text}

Write a brief, professional explanation referencing the similar jobs. Explain why the estimate is reasonable or note any factors affecting confidence."""

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "You are a roofing estimation assistant. Be concise, professional, and reference specific data from similar jobs. Write 2-3 sentences maximum.",
            },
            {"role": "user", "content": prompt},
        ],
        max_tokens=150,
        temperature=0.3,
    )

    return response.choices[0].message.content.strip()
```

### Updated Response Schema

```python
# app/schemas/estimate.py (additions)
from pydantic import BaseModel
from typing import List, Optional

class EstimateResponse(BaseModel):
    """Response from /estimate endpoint."""
    estimate: float
    range_low: float
    range_high: float
    confidence: Literal["HIGH", "MEDIUM", "LOW"]
    model: str
    similar_cases: List[SimilarCase] = []
    reasoning: Optional[str] = None  # NEW: LLM-generated reasoning
```

### Updated Lifespan

```python
# app/main.py (updated lifespan)
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.services.predictor import load_models, unload_models
from app.services.embeddings import load_embedding_model, unload_embedding_model
from app.services.pinecone_cbr import init_pinecone, close_pinecone
from app.services.llm_reasoning import init_llm_client, close_llm_client

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    load_models()           # ML prediction models
    load_embedding_model()  # sentence-transformers model
    init_pinecone()         # Pinecone connection
    init_llm_client()       # OpenRouter client (NEW)
    yield
    # Shutdown
    close_llm_client()      # NEW
    close_pinecone()
    unload_embedding_model()
    unload_models()
```

### Environment Variables

```bash
# .env additions for Phase 3
OPENROUTER_API_KEY=sk-or-v1-xxxxx
OPENROUTER_MODEL=anthropic/claude-haiku-4.5
APP_URL=https://toiturelv-cortex.railway.app
```

## Model Selection Guide

### Recommended Models for Reasoning

| Model | Price (Input/Output) | Speed | Best For |
|-------|---------------------|-------|----------|
| `openai/gpt-4o-mini` | $0.15/$0.60 per 1M | Fast | Cost-effective, good quality |
| `anthropic/claude-haiku-4.5` | $1/$5 per 1M | Very Fast | Premium quality, faster |
| `google/gemini-2.0-flash` | ~$0.075/$0.30 per 1M | Fast | Budget option with good quality |
| `meta-llama/llama-3.1-8b-instruct` | ~$0.05/$0.10 per 1M | Fast | Most economical |

**Recommendation:** Start with `openai/gpt-4o-mini` for best cost/quality balance. This use case (generating 2-3 sentences of reasoning) uses ~150 output tokens per request, so even at high volume costs are minimal.

### Cost Estimation

For 1,000 estimates/month with gpt-4o-mini:
- Input: ~300 tokens/request = 300K tokens = $0.045
- Output: ~150 tokens/request = 150K tokens = $0.09
- **Total: ~$0.14/month**

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| OpenAI-only | Multi-provider via OpenRouter | 2024 | Vendor flexibility, cost optimization |
| Sync-only openai pkg | Async support added | openai 1.0.0 | Better for async frameworks |
| Manual retry | tenacity integration | 2024 | Standardized retry patterns |
| Fixed model | Configurable model via env | 2024 | Easy A/B testing, cost control |

**Current best practice:**
- Use openai package with OpenRouter base URL
- Configure model via environment variable
- Include retry logic with exponential backoff
- Graceful degradation when LLM unavailable

## Open Questions

Things that couldn't be fully resolved:

1. **Optimal model for French-language reasoning**
   - What we know: Input data uses French terms (category names, sqft in "pieds carres")
   - What's unclear: Whether to output reasoning in French or English
   - Recommendation: Start with English, add French option if Laurent prefers

2. **Streaming vs non-streaming**
   - What we know: Non-streaming is simpler, streaming shows faster perceived response
   - What's unclear: Whether frontend will display streaming reasoning
   - Recommendation: Start non-streaming, add streaming in later phase if needed

3. **Caching reasoning for same inputs**
   - What we know: Same inputs = same estimate + cases = could cache reasoning
   - What's unclear: How often identical requests occur
   - Recommendation: Defer caching until usage patterns are clear

## Sources

### Primary (HIGH confidence)
- [OpenRouter Quickstart](https://openrouter.ai/docs/quickstart) - API endpoint, headers, authentication
- [OpenRouter API Parameters](https://openrouter.ai/docs/api/reference/parameters) - temperature, max_tokens, model format
- [OpenRouter Error Handling](https://openrouter.ai/docs/api/reference/errors-and-debugging) - Error codes, retry strategies
- [OpenRouter Python Examples (GitHub)](https://github.com/OpenRouterTeam/openrouter-examples-python) - Official openai package integration
- [Tenacity Documentation](https://tenacity.readthedocs.io/) - Retry patterns, exponential backoff

### Secondary (MEDIUM confidence)
- [OpenRouter in Python (Snyk)](https://snyk.io/articles/openrouter-in-python-use-any-llm-with-one-api-key/) - Client configuration patterns
- [OpenRouter Model Comparison](https://www.teamday.ai/blog/top-ai-models-openrouter-2025) - Cost vs performance analysis
- [Karpathy llm-council (GitHub)](https://github.com/karpathy/llm-council) - httpx async pattern example

### Tertiary (LOW confidence)
- Medium articles on OpenRouter integration (verified with official docs)
- DataCamp OpenRouter tutorial (verified patterns with official examples)

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - Verified with official OpenRouter docs and examples
- Architecture: HIGH - Based on official SDK patterns and existing Phase 1-2 structure
- Pitfalls: HIGH - Documented in official error handling docs and community experience

**Research date:** 2026-01-18
**Valid until:** 2026-02-18 (30 days - OpenRouter models and pricing change frequently)

---

## Appendix: Requirements Mapping

| Requirement | Implementation |
|-------------|----------------|
| LLM-01: OpenRouter client with configurable model | `init_llm_client()` + `settings.openrouter_model` |
| LLM-02: Generate reasoning from estimate + similar cases | `generate_reasoning()` function |
| LLM-03: Include confidence assessment in reasoning | Confidence context in prompt + `assess_confidence_factors()` |
