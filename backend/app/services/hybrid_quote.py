"""Hybrid quote generation orchestrator.

Coordinates CBR (similar case retrieval) and ML (material/labor prediction)
in parallel, then uses OpenRouter LLM to merge results into final quote.

Architecture:
1. Parallel: CBR query + ML prediction (asyncio.gather)
2. Sequential: LLM merger with JSON output + Pydantic validation
3. Confidence scoring from combined signals

Response time target: <5 seconds
"""

import asyncio
import json
import logging
import re
import time
from typing import Any, Dict, List

from app.config import settings
from app.schemas.hybrid_quote import (
    HybridQuoteRequest,
    HybridQuoteResponse,
    HybridQuoteOutput,
    PricingTier,
)
from app.services.confidence_scorer import (
    calculate_confidence,
    calculate_confidence_ml_only,
    calculate_data_completeness,
)
from app.services.embeddings import build_query_text, generate_query_embedding
from app.services.llm_reasoning import get_client  # Reuse existing OpenRouter client
from app.services.material_predictor import predict_materials
from app.services.pinecone_cbr import is_pinecone_available, query_similar_cases
from app.services.predictor import predict

logger = logging.getLogger(__name__)


async def _run_cbr_query(request: HybridQuoteRequest) -> List[Dict[str, Any]]:
    """Run CBR query in async context.

    Wraps synchronous Pinecone query in run_in_executor for async compatibility.
    Skips embedding generation if Pinecone not configured (saves ~500MB RAM).
    """
    # Early return if Pinecone not configured - avoids loading 500MB embedding model
    if not is_pinecone_available():
        logger.info("Pinecone not configured, skipping CBR query")
        return []

    loop = asyncio.get_event_loop()

    def sync_cbr():
        query_text = build_query_text(
            sqft=request.sqft,
            category=request.category,
            complexity=request.complexity_aggregate,
            material_lines=request.material_lines,
            labor_lines=request.labor_lines,
        )
        query_vector = generate_query_embedding(query_text)
        return query_similar_cases(
            query_vector=query_vector,
            top_k=5,
            category_filter=None,  # Let similarity decide
        )

    return await loop.run_in_executor(None, sync_cbr)


async def _run_ml_prediction(request: HybridQuoteRequest) -> Dict[str, Any]:
    """Run ML prediction in async context.

    Wraps synchronous ML prediction in run_in_executor for async compatibility.
    Calls both price predictor and material predictor.
    """
    loop = asyncio.get_event_loop()

    def sync_ml():
        # Get price prediction
        price_result = predict(
            sqft=request.sqft,
            category=request.category,
            material_lines=request.material_lines,
            labor_lines=request.labor_lines,
            has_subs=1 if request.has_subs else 0,
            complexity=request.complexity_aggregate,
        )

        # Get material prediction
        material_result = predict_materials(
            sqft=request.sqft,
            category=request.category,
            complexity=request.complexity_aggregate,
            has_chimney=request.has_chimney,
            has_skylights=request.has_skylights,
            material_lines=request.material_lines,
            labor_lines=request.labor_lines,
            has_subs=request.has_subs,
            quoted_total=request.quoted_total,
        )

        return {
            "price": price_result,
            "materials": material_result,
        }

    return await loop.run_in_executor(None, sync_ml)


def _format_merger_prompt(
    request: HybridQuoteRequest,
    ml_result: Dict[str, Any],
    cbr_cases: List[Dict[str, Any]],
) -> str:
    """Format prompt for LLM to merge CBR + ML predictions.

    Creates a comprehensive prompt with all job details, CBR results,
    and ML predictions for the LLM to synthesize into a final quote.
    """

    # Format CBR cases
    cbr_summary = ""
    if cbr_cases:
        for i, case in enumerate(cbr_cases[:5], 1):
            cbr_summary += f"{i}. {case.get('category', 'N/A')}"
            if case.get("sqft"):
                cbr_summary += f", {case['sqft']:,.0f} sqft"
            if case.get("total"):
                cbr_summary += f", ${case['total']:,.0f}"
            cbr_summary += f" ({case.get('similarity', 0):.0%} similar)\n"
    else:
        cbr_summary = "No similar cases found (ML-only mode)\n"

    # Format ML materials (top 10 for brevity)
    ml_materials = ml_result.get("materials", {}).get("materials", [])[:10]
    ml_summary = ""
    for m in ml_materials:
        ml_summary += f"- ID {m['material_id']}: qty {m['quantity']:.1f}, ${m['total']:.0f}\n"

    ml_price = ml_result.get("price", {})

    prompt = f"""You are merging CBR (case-based) and ML (model-based) predictions into a final roofing quote.

**JOB DETAILS:**
Category: {request.category}
Square Footage: {request.sqft:,.0f}
Complexity Score: {request.complexity_aggregate}/56

6-Factor Breakdown:
- Access Difficulty: {request.access_difficulty}/10
- Roof Pitch: {request.roof_pitch}/8
- Penetrations: {request.penetrations}/10
- Material Removal: {request.material_removal}/8
- Safety Concerns: {request.safety_concerns}/10
- Timeline Constraints: {request.timeline_constraints}/10

Has Chimney: {request.has_chimney}
Has Skylights: {request.has_skylights}

**CBR RESULTS (5 most similar historical jobs):**
{cbr_summary}

**ML PREDICTIONS:**
Price Estimate: ${ml_price.get('estimate', 0):,.0f} ({ml_price.get('confidence', 'N/A')} confidence)
Range: ${ml_price.get('range_low', 0):,.0f} - ${ml_price.get('range_high', 0):,.0f}

Top 10 Predicted Materials:
{ml_summary}

Total Materials Cost: ${ml_result.get('materials', {}).get('total_materials_cost', 0):,.0f}

**MERGER RULES:**
1. For materials appearing in 3+/5 CBR cases, trust CBR quantities
2. For other materials, average CBR and ML quantities
3. Work items: prefer CBR (91% coverage) when available
4. Generate 3 pricing tiers: Basic (-15%), Standard (base), Premium (+18%)

**OUTPUT: Return ONLY valid JSON matching this structure:**
{{
  "work_items": [{{"name": "string", "labor_hours": number, "source": "CBR|ML|MERGED"}}],
  "materials": [{{"material_id": number, "quantity": number, "unit_price": number, "total": number, "source": "CBR|ML|MERGED", "confidence": number}}],
  "total_labor_hours": number,
  "total_materials_cost": number,
  "total_price": number,
  "overall_confidence": number,
  "reasoning": "string explaining key decisions",
  "pricing_tiers": [
    {{"tier": "Basic", "total_price": number, "materials_cost": number, "labor_cost": number, "description": "string"}},
    {{"tier": "Standard", "total_price": number, "materials_cost": number, "labor_cost": number, "description": "string"}},
    {{"tier": "Premium", "total_price": number, "materials_cost": number, "labor_cost": number, "description": "string"}}
  ]
}}

Be accurate. Return ONLY the JSON object, no markdown or explanation."""

    return prompt


def _extract_json(text: str) -> dict:
    """Extract JSON from LLM response, handling markdown code blocks.

    Supports:
    - Raw JSON objects
    - JSON wrapped in ```json ... ``` blocks
    - JSON wrapped in ``` ... ``` blocks
    """
    # Try to find JSON in code blocks first
    code_block_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if code_block_match:
        return json.loads(code_block_match.group(1))

    # Try to find raw JSON object
    json_match = re.search(r"\{.*\}", text, re.DOTALL)
    if json_match:
        return json.loads(json_match.group(0))

    raise ValueError(f"No valid JSON found in response: {text[:200]}")


async def _merge_with_llm(
    request: HybridQuoteRequest,
    ml_result: Dict[str, Any],
    cbr_cases: List[Dict[str, Any]],
) -> HybridQuoteOutput:
    """Use OpenRouter LLM to merge CBR + ML into final quote.

    Reuses the existing OpenRouter client from llm_reasoning module.
    Uses JSON-in-prompt approach with Pydantic validation.
    """
    client = get_client()  # Reuse existing OpenRouter client

    prompt = _format_merger_prompt(request, ml_result, cbr_cases)

    # Call OpenRouter with JSON instruction
    response = client.chat.completions.create(
        model=settings.openrouter_model,
        messages=[
            {
                "role": "system",
                "content": "You are a roofing quote merger. Output ONLY valid JSON, no markdown or explanation.",
            },
            {"role": "user", "content": prompt},
        ],
        max_tokens=2000,
        temperature=0.2,
    )

    response_text = response.choices[0].message.content.strip()

    # Parse JSON and validate with Pydantic
    try:
        data = _extract_json(response_text)
        return HybridQuoteOutput.model_validate(data)
    except (json.JSONDecodeError, ValueError) as e:
        logger.error(f"Failed to parse LLM response: {e}")
        logger.debug(f"Response was: {response_text[:500]}")
        raise ValueError(f"LLM did not produce valid JSON: {e}")


def _generate_fallback_tiers(base_price: float) -> List[PricingTier]:
    """Generate fallback pricing tiers when LLM unavailable.

    Uses fixed percentages: Basic (-15%), Standard (base), Premium (+18%).
    """
    return [
        PricingTier(
            tier="Basic",
            total_price=round(base_price * 0.85, 2),
            materials_cost=round(base_price * 0.55, 2),
            labor_cost=round(base_price * 0.30, 2),
            description="Essential materials, standard timeline",
        ),
        PricingTier(
            tier="Standard",
            total_price=round(base_price, 2),
            materials_cost=round(base_price * 0.60, 2),
            labor_cost=round(base_price * 0.40, 2),
            description="Full material coverage, standard labor",
        ),
        PricingTier(
            tier="Premium",
            total_price=round(base_price * 1.18, 2),
            materials_cost=round(base_price * 0.65, 2),
            labor_cost=round(base_price * 0.53, 2),
            description="Premium materials, expedited timeline",
        ),
    ]


async def generate_hybrid_quote(
    request: HybridQuoteRequest,
) -> HybridQuoteResponse:
    """Main orchestration: parallel CBR+ML, then LLM merger.

    Architecture:
    1. Calculate data completeness upfront
    2. Run CBR + ML predictions in parallel (asyncio.gather)
    3. Handle partial failures gracefully
    4. Calculate confidence from combined signals
    5. Merge with LLM (or fallback to ML-only)
    6. Track processing time for SLA monitoring

    Response time target: <5 seconds
    """
    start_time = time.time()

    # Calculate data completeness upfront
    data_completeness = calculate_data_completeness(
        sqft=request.sqft,
        category=request.category,
        complexity_aggregate=request.complexity_aggregate,
        has_chimney=request.has_chimney,
        has_skylights=request.has_skylights,
        quoted_total=request.quoted_total,
    )

    # Step 1: Run CBR + ML in parallel
    cbr_task = _run_cbr_query(request)
    ml_task = _run_ml_prediction(request)

    results = await asyncio.gather(
        cbr_task,
        ml_task,
        return_exceptions=True,
    )

    cbr_result = results[0] if not isinstance(results[0], Exception) else []
    ml_result = results[1] if not isinstance(results[1], Exception) else None

    if isinstance(results[0], Exception):
        logger.warning(f"CBR query failed: {results[0]}")
    if isinstance(results[1], Exception):
        logger.error(f"ML prediction failed: {results[1]}")

    # Step 2: Handle partial failures
    if ml_result is None and not cbr_result:
        raise RuntimeError("Both CBR and ML predictions failed")

    # Extract ML material IDs for confidence scoring
    ml_material_ids = []
    if ml_result:
        ml_material_ids = [
            m["material_id"]
            for m in ml_result.get("materials", {}).get("materials", [])
        ]

    # Step 3: Calculate confidence
    if ml_result is None:
        # CBR-only fallback (rare)
        confidence, needs_review = 0.4, True
        logger.warning("ML failed, using CBR-only with low confidence")
    elif not cbr_result:
        # ML-only fallback
        confidence, needs_review = calculate_confidence_ml_only(
            ml_material_ids=ml_material_ids,
            data_completeness=data_completeness,
        )
        logger.warning("CBR failed, using ML-only")
    else:
        # Normal path: both CBR and ML succeeded
        confidence, needs_review = calculate_confidence(
            cbr_cases=cbr_result,
            ml_material_ids=ml_material_ids,
            data_completeness=data_completeness,
        )

    # Step 4: Merge with LLM (or fallback)
    try:
        merged = await _merge_with_llm(request, ml_result or {}, cbr_result)
    except Exception as e:
        logger.error(f"LLM merger failed: {e}")
        # Fallback: use ML price with generated tiers
        base_price = (
            ml_result.get("price", {}).get("estimate", 0) if ml_result else 0
        )
        merged = HybridQuoteOutput(
            work_items=[],
            materials=[],
            total_labor_hours=0,
            total_materials_cost=(
                ml_result.get("materials", {}).get("total_materials_cost", 0)
                if ml_result
                else 0
            ),
            total_price=base_price,
            overall_confidence=confidence,
            reasoning="LLM merger unavailable. Using ML predictions directly.",
            pricing_tiers=_generate_fallback_tiers(base_price),
        )
        needs_review = True  # Always review if LLM failed

    # Step 5: Build response
    processing_time_ms = int((time.time() - start_time) * 1000)

    response = HybridQuoteResponse(
        work_items=merged.work_items,
        materials=merged.materials,
        total_labor_hours=merged.total_labor_hours,
        total_materials_cost=merged.total_materials_cost,
        total_price=merged.total_price,
        overall_confidence=merged.overall_confidence,
        reasoning=merged.reasoning,
        pricing_tiers=merged.pricing_tiers,
        needs_review=needs_review,
        cbr_cases_used=len(cbr_result),
        ml_confidence=(
            ml_result.get("price", {}).get("confidence", "LOW")
            if ml_result
            else "LOW"
        ),
        processing_time_ms=processing_time_ms,
    )

    logger.info(
        f"Hybrid quote generated in {processing_time_ms}ms "
        f"(CBR={len(cbr_result)} cases, confidence={confidence:.2f})"
    )

    return response
