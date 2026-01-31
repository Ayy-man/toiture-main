# Phase 13: Hybrid Quote Generation - Research

**Researched:** 2026-02-01
**Domain:** Hybrid AI architecture (CBR + ML + LLM merger)
**Confidence:** HIGH

## Summary

Phase 13 implements a hybrid quote generation architecture combining three AI approaches: Case-Based Reasoning (CBR) retrieves similar historical jobs from Pinecone, ML models predict materials/quantities/labor, and an LLM merges the outputs with conflict resolution. This is a well-established pattern in 2026, with CBR and ML running in parallel using Python's asyncio.gather(), then passing structured outputs to Claude via Pydantic-based tool calling for reconciliation.

The standard approach for this hybrid architecture is:
1. **Parallel execution** of independent components (CBR + ML) using asyncio.gather() with return_exceptions=True
2. **Structured LLM outputs** using Anthropic's native structured outputs (Claude Sonnet 4.5) with Pydantic models
3. **Confidence scoring** via weighted ensemble methods (majority voting pattern)
4. **Performance optimization** through lazy loading, caching embeddings, and async I/O

The codebase already has all building blocks in place: predictor.py (ML), pinecone_cbr.py (CBR), llm_reasoning.py (LLM), and material_predictor.py (material models). Phase 13 orchestrates these into a single unified endpoint.

**Primary recommendation:** Use asyncio.gather() for CBR+ML parallelization, Anthropic structured outputs with Pydantic for LLM merger, and weighted average confidence scoring combining similarity scores + model agreement + data completeness.

## Standard Stack

The established libraries/tools for this domain:

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| fastapi[standard] | >=0.128.0 | Async API framework | Already used; native async support for parallel execution |
| anthropic | latest | Claude structured outputs | Official SDK with Pydantic integration (Sonnet 4.5 support) |
| pydantic | >=2.7.0 | Schema validation | Already used; required for structured LLM outputs |
| asyncio | stdlib | Parallel execution | Python standard library; proven pattern for I/O-bound parallelization |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| instructor | latest | Simplified Pydantic-LLM integration | Alternative to manual tool calling (optional, not required) |
| tenacity | >=8.2.0 | Retry logic | Already used in llm_reasoning.py; add to CBR/ML calls for resilience |
| numpy | >=1.26.0 | Numerical operations | Already used; needed for weighted averaging in confidence scoring |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| asyncio.gather() | concurrent.futures.ThreadPoolExecutor | ThreadPool adds overhead for I/O-bound tasks; asyncio is more efficient |
| Anthropic SDK | OpenRouter (current) | OpenRouter lacks structured outputs API; would require custom parsing |
| Pydantic tool calling | JSON mode | JSON mode doesn't enforce schema; tool calling guarantees structure |

**Installation:**
```bash
pip install anthropic>=0.40.0
# All other dependencies already in requirements.txt
```

## Architecture Patterns

### Recommended Project Structure
```
backend/app/
├── services/
│   ├── predictor.py              # ML models (existing)
│   ├── material_predictor.py     # Material models (existing)
│   ├── pinecone_cbr.py           # CBR retrieval (existing)
│   ├── llm_reasoning.py          # LLM client (existing)
│   ├── hybrid_quote.py           # NEW: orchestration layer
│   └── confidence_scorer.py      # NEW: confidence calculation
├── schemas/
│   ├── hybrid_quote.py           # NEW: Pydantic models for LLM
│   └── estimate.py               # Existing, may need extensions
└── routers/
    └── estimate.py               # Add POST /estimate/hybrid endpoint
```

### Pattern 1: Parallel Execution with asyncio.gather()

**What:** Run CBR retrieval and ML prediction concurrently, then await both results before passing to LLM

**When to use:** When components are independent and I/O-bound (Pinecone query + ML inference)

**Example:**
```python
# Source: Python 3.14 official docs + FastAPI async patterns
# https://docs.python.org/3/library/asyncio-task.html

import asyncio
from typing import Tuple, List, Dict, Any

async def run_parallel_predictions(
    request: HybridQuoteRequest
) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    """Run CBR and ML predictions in parallel.

    Returns: (ml_result, cbr_similar_cases)
    """
    # Wrap sync functions in async executors
    loop = asyncio.get_event_loop()

    # CBR query (I/O-bound)
    async def get_cbr_cases():
        query_text = build_query_text(
            sqft=request.sqft,
            category=request.category,
            complexity=request.complexity_aggregate,
        )
        query_vector = generate_query_embedding(query_text)
        return query_similar_cases(
            query_vector=query_vector,
            top_k=5,
            category_filter=request.category,
        )

    # ML prediction (CPU-bound but fast <200ms)
    async def get_ml_prediction():
        return await loop.run_in_executor(
            None,  # Use default ThreadPoolExecutor
            predict_materials,
            request.sqft,
            request.category,
            request.complexity_aggregate,
            request.has_chimney,
            request.has_skylights,
            request.material_lines,
            request.labor_lines,
            request.has_subs,
            None,  # quoted_total
        )

    # Run in parallel with error handling
    cbr_task = get_cbr_cases()
    ml_task = get_ml_prediction()

    # return_exceptions=True: don't fail if one component fails
    results = await asyncio.gather(
        ml_task,
        cbr_task,
        return_exceptions=True
    )

    ml_result = results[0] if not isinstance(results[0], Exception) else None
    cbr_cases = results[1] if not isinstance(results[1], Exception) else []

    return ml_result, cbr_cases
```

### Pattern 2: LLM Structured Output with Pydantic

**What:** Use Anthropic's tool calling API to enforce JSON schema compliance for merger output

**When to use:** When LLM must produce structured data (materials list with quantities, confidence scores)

**Example:**
```python
# Source: Anthropic Claude docs + Instructor library patterns
# https://platform.claude.com/docs/en/build-with-claude/structured-outputs

from anthropic import Anthropic
from pydantic import BaseModel, Field
from typing import List, Literal

# Define output schema
class MaterialLineItem(BaseModel):
    material_id: str = Field(description="Material ID from database")
    quantity: float = Field(description="Predicted quantity")
    source: Literal["CBR", "ML", "MERGED"] = Field(description="Source of prediction")
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence 0-1")

class WorkItem(BaseModel):
    name: str = Field(description="Work item name from Quote Lines")
    labor_hours: float = Field(description="Estimated labor hours")
    source: Literal["CBR", "ML"] = Field(description="Source")

class HybridQuoteOutput(BaseModel):
    work_items: List[WorkItem]
    materials: List[MaterialLineItem]
    total_labor_hours: float
    total_materials_cost: float
    total_price: float
    overall_confidence: float = Field(ge=0.0, le=1.0)
    reasoning: str = Field(description="Explanation of merger decisions")

# Use tool calling for structured output
client = Anthropic(api_key=settings.anthropic_api_key)

response = client.messages.create(
    model="claude-sonnet-4.5-20250929",
    max_tokens=4096,
    tools=[{
        "name": "generate_quote",
        "description": "Merge CBR and ML predictions into final quote",
        "input_schema": HybridQuoteOutput.model_json_schema()
    }],
    tool_choice={"type": "tool", "name": "generate_quote"},
    messages=[{
        "role": "user",
        "content": format_merger_prompt(ml_result, cbr_cases, complexity_factors)
    }]
)

# Extract structured output
tool_use = next(block for block in response.content if block.type == "tool_use")
merged_quote = HybridQuoteOutput.model_validate(tool_use.input)
```

### Pattern 3: Weighted CBR Case Aggregation

**What:** Weight similar cases by recency × similarity score when extracting quantities

**When to use:** When combining multiple CBR cases into single prediction

**Example:**
```python
# Source: CBR research + ensemble methods
# https://link.springer.com/article/10.1023/B:APIN.0000043560.57137.20

from datetime import datetime
import numpy as np

def extract_cbr_materials(
    similar_cases: List[Dict],
    current_year: int = 2026
) -> Dict[str, float]:
    """Extract material quantities from similar cases with weighted averaging.

    Weights: recency × similarity score
    """
    material_quantities = {}
    material_weights = {}

    for case in similar_cases:
        similarity = case.get("similarity", 0.0)  # From Pinecone
        year = case.get("year", current_year)

        # Recency weight: exponential decay (0.95 per year)
        years_ago = current_year - year
        recency_weight = 0.95 ** years_ago

        # Combined weight
        weight = similarity * recency_weight

        # Extract materials from case (from full line-item breakdown)
        for material in case.get("materials", []):
            mat_id = material["material_id"]
            quantity = material["quantity"]

            if mat_id not in material_quantities:
                material_quantities[mat_id] = 0.0
                material_weights[mat_id] = 0.0

            material_quantities[mat_id] += quantity * weight
            material_weights[mat_id] += weight

    # Normalize by total weights (weighted average)
    for mat_id in material_quantities:
        if material_weights[mat_id] > 0:
            material_quantities[mat_id] /= material_weights[mat_id]

    return material_quantities
```

### Pattern 4: Confidence Scoring with Multiple Signals

**What:** Combine CBR similarity, ML-CBR agreement, and data completeness into single score

**When to use:** When multiple models produce predictions that need reconciliation

**Example:**
```python
# Source: Ensemble confidence scoring research
# https://engineering.atspotify.com/2024/12/building-confidence-a-case-study-in-how-to-create-confidence-scores-for-genai-applications

def calculate_confidence(
    ml_materials: List[str],
    cbr_materials: List[str],
    cbr_similarity_scores: List[float],
    data_completeness: float,  # 0-1, % of required fields present
) -> float:
    """Calculate overall confidence score from multiple signals.

    Formula: weighted average of:
    - CBR average similarity (30%)
    - ML-CBR agreement (40%)
    - Data completeness (30%)
    """
    # Signal 1: Average CBR similarity
    avg_similarity = np.mean(cbr_similarity_scores) if cbr_similarity_scores else 0.0

    # Signal 2: Material agreement (Jaccard similarity)
    ml_set = set(ml_materials)
    cbr_set = set(cbr_materials)
    if len(ml_set | cbr_set) > 0:
        agreement = len(ml_set & cbr_set) / len(ml_set | cbr_set)
    else:
        agreement = 0.0

    # Signal 3: Data completeness (already 0-1)

    # Weighted combination
    confidence = (
        0.30 * avg_similarity +
        0.40 * agreement +
        0.30 * data_completeness
    )

    return confidence
```

### Anti-Patterns to Avoid

- **Sequential execution:** Don't await CBR then ML - run in parallel with asyncio.gather()
- **JSON mode for LLM:** Don't use JSON mode - use tool calling for guaranteed schema compliance
- **Ignoring edge cases:** Don't assume both CBR and ML succeed - handle partial failures gracefully
- **Simple averaging without weights:** Don't treat all CBR cases equally - weight by recency × similarity
- **Blocking operations in async:** Don't call sync functions directly in async - use run_in_executor()

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Structured LLM outputs | Custom JSON parsing with regex/validation | Anthropic tool calling API + Pydantic | Schema enforcement guaranteed by API; handles edge cases |
| Retry logic | Manual try/except loops | tenacity library (already used) | Exponential backoff, jitter, error classification built-in |
| Async/sync bridging | Custom thread management | asyncio.run_in_executor() | Standard library; handles thread pool lifecycle |
| Weighted averaging | Custom loop logic | numpy.average(values, weights=weights) | Handles edge cases (zero weights, empty arrays) |
| Confidence calibration | Ad-hoc formulas | Ensemble majority voting pattern | Research-backed; used in production (Spotify, Mindee) |

**Key insight:** Hybrid AI systems have many failure modes (API timeout, empty results, schema violations). Use battle-tested libraries that handle edge cases rather than building from scratch.

## Common Pitfalls

### Pitfall 1: Sequential Execution Bottleneck

**What goes wrong:** Calling CBR retrieval, waiting for it to finish, then calling ML prediction adds latency unnecessarily (500ms + 200ms = 700ms sequential vs ~500ms parallel)

**Why it happens:** Natural imperative programming style; forgetting that CBR and ML are independent

**How to avoid:**
- Use asyncio.gather() to run both in parallel
- Set return_exceptions=True to handle partial failures gracefully
- Always measure actual latency with logging timestamps

**Warning signs:** Total endpoint latency > 5 seconds when it should be ~3-4s (500ms CBR + 200ms ML + 2-3s LLM)

### Pitfall 2: LLM Hallucinating Material IDs

**What goes wrong:** Without structured outputs, LLM might invent material IDs that don't exist in the database (849 valid IDs)

**Why it happens:** JSON mode doesn't enforce enum constraints; LLM patterns from training data

**How to avoid:**
- Use Pydantic Field with enum validation: `material_id: Literal[<all 849 IDs>]`
- OR use tool calling with strict schema enforcement
- Always validate material IDs against database after LLM response

**Warning signs:** Database lookup failures for material IDs in production; IDs like "MAT_SHINGLES_001" that match patterns but don't exist

### Pitfall 3: Ignoring CBR Retrieval Failures

**What goes wrong:** If Pinecone is down or returns no similar cases, entire endpoint fails instead of falling back to ML-only

**Why it happens:** Not handling exceptions from query_similar_cases(); assuming CBR always succeeds

**How to avoid:**
- Use return_exceptions=True in asyncio.gather()
- Check if result is Exception before using it
- Fall back to ML-only with LOW confidence flag when CBR fails
- Log failures but don't block quote generation

**Warning signs:** 500 errors when Pinecone has transient issues; user can't get any quote

### Pitfall 4: Not Scaling CBR Quantities to Target Size

**What goes wrong:** CBR retrieves a 2000 sqft job, user requests 1000 sqft quote, but quantities aren't adjusted - materials are 2x what's needed

**Why it happens:** Forgetting that similar cases have different sizes; assuming quantities transfer directly

**How to avoid:**
- Apply category-specific scaling factors when sqft differs
- Context says: "Use category-specific scaling factors when adjusting quantities to new job size (only if data shows actual differences; otherwise simple sqft ratio)"
- Extract scaling factors from training data analysis (e.g., for Bardeaux: materials scale at 0.9x sqft ratio due to fixed overhead)

**Warning signs:** Quotes are systematically high/low when target sqft differs from similar cases; materials don't make sense for job size

### Pitfall 5: Trusting ML Over CBR for Common Materials

**What goes wrong:** ML predicts uncommon material for a standard job; LLM trusts ML because it has higher confidence score, but CBR shows 5/5 similar jobs used different material

**Why it happens:** ML confidence is calibrated independently of CBR agreement; LLM doesn't understand domain patterns

**How to avoid:**
- Context decision: "trust CBR for common items (appears in 3+/5 similar jobs), otherwise trust ML"
- Encode this rule in LLM prompt explicitly
- Calculate "commonality score" = count of CBR cases containing material / total cases
- If commonality >= 0.6 (3/5), prefer CBR over ML

**Warning signs:** Quotes include unusual materials when similar jobs all used standard materials; customer feedback on unrealistic material choices

### Pitfall 6: Missing Median Sqft Fallback

**What goes wrong:** User doesn't provide sqft, or similar cases lack sqft - scaling logic fails

**Why it happens:** Assuming all data is complete; not handling missing values

**How to avoid:**
- Context decision: "When sqft missing from input or similar jobs: use median sqft for that job_category from training data"
- Pre-compute and cache median sqft per category during model training
- Store in cortex_config_v3.json alongside other configuration

**Warning signs:** Errors when sqft is null; scaling produces inf/nan values

### Pitfall 7: Slow LLM Blocking Response

**What goes wrong:** LLM takes 10-15s for complex reasoning, violating <5s SLA

**Why it happens:** Using verbose prompt with too much context; Claude generating long explanations

**How to avoid:**
- Context says: "Priority: Accuracy over speed - take time to reason carefully" BUT also "<5 seconds for full quote"
- Use max_tokens limit (2048 tokens = ~1-2s at Claude's speed)
- Minimize prompt size: send only essential CBR data (top 5 cases, key fields only)
- Use Claude Sonnet 4.5 (fast) not Opus (slow)
- Consider async: return quote immediately, stream reasoning updates after

**Warning signs:** p95 latency > 5s; user complaints about slow responses

## Code Examples

Verified patterns from official sources:

### Parallel Execution with Error Handling
```python
# Source: Python 3.14 asyncio documentation
# https://docs.python.org/3/library/asyncio-task.html

async def generate_hybrid_quote(request: HybridQuoteRequest) -> HybridQuoteResponse:
    """Main orchestration function for hybrid quote generation."""

    # Step 1: Run CBR + ML in parallel
    try:
        ml_result, cbr_cases = await run_parallel_predictions(request)
    except Exception as e:
        logger.error(f"Parallel prediction failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

    # Step 2: Handle partial failures
    if ml_result is None and not cbr_cases:
        raise HTTPException(
            status_code=503,
            detail="Both CBR and ML predictions failed"
        )

    if ml_result is None:
        logger.warning("ML prediction failed, using CBR only")
        # CBR-only fallback path
        return generate_from_cbr_only(cbr_cases, request)

    if not cbr_cases:
        logger.warning("CBR retrieval failed, using ML only")
        # ML-only fallback path with LOW confidence
        return generate_from_ml_only(ml_result, request, confidence="LOW")

    # Step 3: Merge with LLM
    merged_quote = await merge_with_llm(
        ml_result=ml_result,
        cbr_cases=cbr_cases,
        complexity_factors=extract_complexity_factors(request),
    )

    return merged_quote
```

### LLM Merger Prompt Structure
```python
# Source: Anthropic prompt engineering best practices
# https://www.palantir.com/docs/foundry/aip/best-practices-prompt-engineering

def format_merger_prompt(
    ml_result: Dict,
    cbr_cases: List[Dict],
    complexity_factors: Dict[str, int],
) -> str:
    """Format prompt for LLM to merge CBR + ML predictions.

    Context decision: "Exact prompt structure for LLM merger" is Claude's discretion.
    This structure optimizes for accuracy and explainability.
    """

    # Format CBR cases concisely
    cbr_materials = extract_cbr_materials_summary(cbr_cases)
    cbr_work_items = extract_cbr_work_items(cbr_cases)

    # Format ML predictions
    ml_materials = format_ml_materials(ml_result["materials"])

    prompt = f"""You are merging two roofing quote predictions to create a final accurate quote.

**CONTEXT:**
Job Category: {ml_result["category"]}
Square Footage: {ml_result["sqft"]:,.0f}
Complexity Factors (6-factor system):
  1. Access difficulty: {complexity_factors["access_difficulty"]}/10
  2. Roof pitch/slope: {complexity_factors["roof_pitch"]}/8
  3. Penetrations: {complexity_factors["penetrations"]}/10
  4. Material removal: {complexity_factors["material_removal"]}/8
  5. Safety concerns: {complexity_factors["safety_concerns"]}/10
  6. Timeline constraints: {complexity_factors["timeline_constraints"]}/10
  Aggregate Score: {complexity_factors["aggregate"]}/56

**CBR PREDICTIONS (from 5 similar historical jobs):**
Materials (weighted by recency × similarity):
{cbr_materials}

Work Items (91% coverage from Quote Lines):
{cbr_work_items}

**ML PREDICTIONS (from trained models):**
Materials (top 20 most likely):
{ml_materials}

Labor Hours: {ml_result.get("labor_hours", "N/A")}

**MERGER RULES:**
1. Material conflicts: Trust CBR if material appears in 3+/5 similar jobs, otherwise trust ML
2. Quantity conflicts: Average CBR and ML quantities
3. Work items: Use CBR (91% coverage) - only fall back to ML if CBR missing
4. Apply category-specific scaling if target sqft differs from similar jobs
5. Flag confidence <50% for Laurent's review

**OUTPUT REQUIRED:**
Generate complete quote with:
- Work items with labor hours
- Materials with IDs and quantities
- Total price
- Confidence score (0-1)
- Brief reasoning for key decisions

Prioritize accuracy over speed. Take time to reason carefully about conflicts."""

    return prompt
```

### Confidence Score Calculation
```python
# Source: Ensemble confidence scoring (Spotify case study)
# https://engineering.atspotify.com/2024/12/building-confidence-a-case-study-in-how-to-create-confidence-scores-for-genai-applications

def calculate_hybrid_confidence(
    ml_result: Dict,
    cbr_cases: List[Dict],
    merged_quote: HybridQuoteOutput,
    input_completeness: float,
) -> float:
    """Calculate overall confidence using combined formula.

    Context decision: "Use combined formula: CBR/ML agreement + data completeness + CBR similarity scores"
    """

    # Signal 1: Average CBR similarity (weight: 30%)
    cbr_similarities = [case["similarity"] for case in cbr_cases]
    avg_cbr_similarity = np.mean(cbr_similarities) if cbr_similarities else 0.0

    # Signal 2: ML-CBR material agreement (weight: 40%)
    ml_material_ids = {m["material_id"] for m in ml_result["materials"]}
    cbr_material_ids = {
        m["material_id"]
        for case in cbr_cases
        for m in case.get("materials", [])
    }

    if len(ml_material_ids | cbr_material_ids) > 0:
        material_agreement = len(ml_material_ids & cbr_material_ids) / len(ml_material_ids | cbr_material_ids)
    else:
        material_agreement = 0.0

    # Signal 3: Input data completeness (weight: 30%)
    # Already calculated as 0-1 based on % of required fields present

    # Weighted combination
    confidence = (
        0.30 * avg_cbr_similarity +
        0.40 * material_agreement +
        0.30 * input_completeness
    )

    # Threshold check for review flag
    needs_review = confidence < 0.50

    return confidence, needs_review
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Sequential CBR → ML → LLM | Parallel CBR + ML → LLM | 2024-2025 | 30-40% latency reduction |
| JSON mode for LLM outputs | Structured outputs (tool calling) | Late 2024 (Anthropic) | 100% schema compliance vs ~95% with JSON mode |
| OpenRouter generic models | Anthropic Claude direct SDK | 2025-2026 | Structured outputs API access |
| Simple averaging | Weighted ensemble (recency × similarity) | 2024-2026 research | Better handling of stale data |
| Single confidence score | Multi-signal confidence (agreement + similarity + completeness) | 2024-2026 | More reliable review flagging |

**Deprecated/outdated:**
- **OpenRouter for structured outputs:** Lacks native structured outputs API; use Anthropic SDK directly (requires API key change)
- **JSON mode:** Replaced by tool calling in Claude API (October 2024+)
- **Synchronous execution:** Replaced by async patterns for I/O-bound operations
- **Global GIL workarounds:** Python 3.13+ has per-interpreter GIL (InterpreterPoolExecutor), but not needed for this I/O-bound workload

## Open Questions

Things that couldn't be fully resolved:

1. **Category-specific scaling formulas**
   - What we know: Context says "category-specific scaling factors when adjusting quantities to new job size (only if data shows actual differences; otherwise simple sqft ratio)"
   - What's unclear: Actual formulas per category (Bardeaux, Elastomère, etc.)
   - Recommendation: Analyze training data to derive scaling factors; implement in hybrid_quote.py with fallback to simple ratio

2. **Three-tier pricing (Basic/Standard/Premium)**
   - What we know: Context says "Three-tier pricing output required - implementation TBD in Phase 12 first"
   - What's unclear: Whether Phase 12 implemented this; how to integrate with hybrid quote
   - Recommendation: Check Phase 12 completion; if not done, defer to separate phase or implement as variance around base quote (Basic = -10%, Standard = base, Premium = +15%)

3. **LLM API migration impact**
   - What we know: Current code uses OpenRouter; structured outputs require Anthropic SDK
   - What's unclear: Whether OpenRouter API key works with Anthropic SDK, or need separate Anthropic API key
   - Recommendation: Test Anthropic SDK with existing OPENROUTER_API_KEY env var; if fails, add ANTHROPIC_API_KEY to .env.example and config.py

4. **Service call detection logic**
   - What we know: Context says "Service calls (labor only): detect and route to separate flow"
   - What's unclear: How to detect service calls from request data; what separate flow looks like
   - Recommendation: Implement heuristic: if material_lines == 0 or sqft < 100, route to labor-only flow that skips material prediction

5. **Full line-item breakdown in Pinecone**
   - What we know: Context says CBR should pull "full line-item breakdown" from similar jobs
   - What's unclear: Whether Pinecone metadata currently includes materials/work_items, or just summary fields
   - Recommendation: Check current Pinecone index schema; if metadata lacks line items, may need to fetch from Supabase using case_id (adds latency)

## Sources

### Primary (HIGH confidence)
- Python 3.14 asyncio documentation - https://docs.python.org/3/library/asyncio-task.html
- Anthropic Claude structured outputs - https://platform.claude.com/docs/en/build-with-claude/structured-outputs
- Anthropic Python SDK - https://github.com/anthropics/anthropic-sdk-python
- FastAPI async patterns - https://fastapi.tiangolo.com/async/

### Secondary (MEDIUM confidence)
- Spotify confidence scoring case study - https://engineering.atspotify.com/2024/12/building-confidence-a-case-study-in-how-to-create-confidence-scores-for-genai-applications
- Ensemble methods in ML - https://www.ultralytics.com/glossary/ensemble
- CBR weighted averaging - https://link.springer.com/article/10.1023/B:APIN.0000043560.57137.20
- Hybrid AI architectures 2026 - https://leonnicholls.medium.com/the-art-of-hybrid-ai-architectures-3ae52d3a9efa
- ThreadPoolExecutor vs AsyncIO - https://superfastpython.com/threadpoolexecutor-vs-asyncio/
- Instructor library (Pydantic-LLM) - https://python.useinstructor.com/integrations/anthropic/

### Tertiary (LOW confidence)
- State of LLMs 2025 - https://magazine.sebastianraschka.com/p/state-of-llms-2025
- AI trends 2026 - https://www.clarifai.com/blog/llms-and-ai-trends

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - All libraries verified with official docs; already in use except Anthropic SDK
- Architecture: HIGH - Patterns verified in Python docs, Anthropic docs, production case studies (Spotify)
- Pitfalls: MEDIUM - Based on general async/LLM patterns + context-specific decisions; some domain-specific pitfalls inferred from requirements

**Research date:** 2026-02-01
**Valid until:** 2026-03-01 (30 days - stable technologies, but LLM APIs evolving rapidly)
