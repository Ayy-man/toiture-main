"""Estimate endpoint for ML predictions."""

import json
import logging

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.schemas.estimate import EstimateRequest, EstimateResponse, SimilarCase
from app.schemas.hybrid_quote import HybridQuoteRequest, HybridQuoteResponse, PricingTier
from app.schemas.materials import (
    MaterialEstimateRequest,
    MaterialEstimateResponse,
    MaterialPrediction,
    FullEstimateResponse,
)
from app.services.embeddings import build_query_text, generate_query_embedding
from app.services.hybrid_quote import generate_hybrid_quote
from app.services.llm_reasoning import generate_reasoning_stream
from app.services.material_predictor import predict_materials
from app.services.pinecone_cbr import is_pinecone_available, query_similar_cases
from app.services.predictor import predict
from app.services.supabase_client import get_supabase

logger = logging.getLogger(__name__)

router = APIRouter(tags=["estimate"])


@router.post("/estimate", response_model=EstimateResponse)
def create_estimate(request: EstimateRequest):
    """Generate price estimate for roofing job.

    Uses ML model to predict price based on sqft, category, and other factors.
    Returns estimate with confidence range and similar historical cases.
    """
    try:
        # Get ML prediction
        result = predict(
            sqft=request.sqft,
            category=request.category,
            material_lines=request.material_lines,
            labor_lines=request.labor_lines,
            has_subs=request.has_subs,
            complexity=request.complexity,
        )

        # Get similar cases from CBR (skip if Pinecone not configured to avoid loading 500MB model)
        similar_cases = []
        if is_pinecone_available():
            try:
                query_text = build_query_text(
                    sqft=request.sqft,
                    category=request.category,
                    complexity=request.complexity,
                    material_lines=request.material_lines,
                    labor_lines=request.labor_lines,
                )
                query_vector = generate_query_embedding(query_text)
                similar_cases_data = query_similar_cases(
                    query_vector=query_vector,
                    top_k=5,
                    category_filter=None,  # Let similarity decide, don't filter by category
                )
                similar_cases = [SimilarCase(**case) for case in similar_cases_data]
            except Exception as e:
                logger.warning(f"CBR lookup failed: {e}")

        # LLM reasoning disabled for speed (was taking 15-30s)
        # TODO: Re-enable with faster model or async loading
        reasoning = None

        response = EstimateResponse(
            estimate=result["estimate"],
            range_low=result["range_low"],
            range_high=result["range_high"],
            confidence=result["confidence"],
            model=result["model"],
            similar_cases=similar_cases,
            reasoning=reasoning,
        )

        # Save estimate to Supabase (graceful degradation)
        try:
            supabase = get_supabase()
            if supabase is not None:
                supabase.table("estimates").insert({
                    "sqft": request.sqft,
                    "category": request.category,
                    "material_lines": request.material_lines,
                    "labor_lines": request.labor_lines,
                    "has_subs": bool(request.has_subs),
                    "complexity": request.complexity,
                    "ai_estimate": result["estimate"],
                    "range_low": result["range_low"],
                    "range_high": result["range_high"],
                    "confidence": result["confidence"],
                    "model": result["model"],
                    "reasoning": reasoning,
                }).execute()
                logger.info("Estimate saved to Supabase")
        except Exception as e:
            logger.warning(f"Failed to save estimate to Supabase: {e}")

        return response
    except Exception as e:
        logger.error(f"Estimate error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/estimate/stream")
def create_estimate_stream(request: EstimateRequest):
    """Generate price estimate with streaming LLM reasoning.

    Returns SSE stream:
    1. First event: estimate data (fast)
    2. Subsequent events: reasoning text chunks (streamed)
    """

    def generate():
        try:
            # Get ML prediction (fast)
            result = predict(
                sqft=request.sqft,
                category=request.category,
                material_lines=request.material_lines,
                labor_lines=request.labor_lines,
                has_subs=request.has_subs,
                complexity=request.complexity,
            )

            # Get similar cases from CBR (skip if Pinecone not configured to avoid loading 500MB model)
            similar_cases = []
            if is_pinecone_available():
                try:
                    query_text = build_query_text(
                        sqft=request.sqft,
                        category=request.category,
                        complexity=request.complexity,
                        material_lines=request.material_lines,
                        labor_lines=request.labor_lines,
                    )
                    query_vector = generate_query_embedding(query_text)
                    similar_cases_data = query_similar_cases(
                        query_vector=query_vector,
                        top_k=5,
                        category_filter=None,
                    )
                    similar_cases = [SimilarCase(**case) for case in similar_cases_data]
                except Exception as e:
                    logger.warning(f"CBR lookup failed: {e}")

            # Send estimate data immediately
            estimate_data = {
                "type": "estimate",
                "data": {
                    "estimate": result["estimate"],
                    "range_low": result["range_low"],
                    "range_high": result["range_high"],
                    "confidence": result["confidence"],
                    "model": result["model"],
                    "similar_cases": [c.model_dump() for c in similar_cases],
                },
            }
            yield f"data: {json.dumps(estimate_data)}\n\n"

            # Stream LLM reasoning
            try:
                reasoning_text = ""
                for chunk in generate_reasoning_stream(
                    estimate=result["estimate"],
                    confidence=result["confidence"],
                    sqft=request.sqft,
                    category=request.category,
                    similar_cases=[
                        {
                            "category": c.category,
                            "sqft": c.sqft,
                            "total": c.total,
                            "per_sqft": c.per_sqft,
                            "similarity": c.similarity,
                            "year": c.year,
                        }
                        for c in similar_cases
                    ],
                ):
                    reasoning_text += chunk
                    yield f"data: {json.dumps({'type': 'reasoning_chunk', 'data': chunk})}\n\n"

                # Send completion signal
                yield f"data: {json.dumps({'type': 'done', 'data': {'reasoning': reasoning_text}})}\n\n"

                # Save to Supabase after streaming completes
                try:
                    supabase = get_supabase()
                    if supabase is not None:
                        supabase.table("estimates").insert({
                            "sqft": request.sqft,
                            "category": request.category,
                            "material_lines": request.material_lines,
                            "labor_lines": request.labor_lines,
                            "has_subs": bool(request.has_subs),
                            "complexity": request.complexity,
                            "ai_estimate": result["estimate"],
                            "range_low": result["range_low"],
                            "range_high": result["range_high"],
                            "confidence": result["confidence"],
                            "model": result["model"],
                            "reasoning": reasoning_text,
                        }).execute()
                except Exception as e:
                    logger.warning(f"Failed to save estimate: {e}")

            except Exception as e:
                logger.warning(f"LLM reasoning failed: {e}")
                yield f"data: {json.dumps({'type': 'done', 'data': {'reasoning': None, 'error': str(e)}})}\n\n"

        except Exception as e:
            logger.error(f"Stream error: {e}")
            yield f"data: {json.dumps({'type': 'error', 'data': str(e)})}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.post("/estimate/materials", response_model=MaterialEstimateResponse)
def predict_materials_endpoint(request: MaterialEstimateRequest):
    """Predict material IDs and quantities for roofing job.

    Uses multi-label classifier for ID selection and per-material regressors
    for quantity prediction. Applies co-occurrence rules and feature triggers.
    """
    try:
        result = predict_materials(
            sqft=request.sqft,
            category=request.category,
            complexity=request.complexity,
            has_chimney=request.has_chimney,
            has_skylights=request.has_skylights,
            material_lines=request.material_lines,
            labor_lines=request.labor_lines,
            has_subs=request.has_subs,
            quoted_total=request.quoted_total,
        )

        return MaterialEstimateResponse(
            materials=[MaterialPrediction(**m) for m in result["materials"]],
            total_materials_cost=result["total_materials_cost"],
            model_info=result["model_info"],
            applied_rules=result["applied_rules"],
        )
    except Exception as e:
        logger.error(f"Material prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/estimate/full", response_model=FullEstimateResponse)
def create_full_estimate(request: MaterialEstimateRequest):
    """Generate complete estimate with price prediction AND material list.

    Combines:
    - Price estimate from existing ML model
    - Material predictions from material model
    """
    try:
        # Get price prediction (existing)
        price_result = predict(
            sqft=request.sqft,
            category=request.category,
            material_lines=request.material_lines,
            labor_lines=request.labor_lines,
            has_subs=1 if request.has_subs else 0,
            complexity=request.complexity,
        )

        # Get material predictions (new)
        material_result = predict_materials(
            sqft=request.sqft,
            category=request.category,
            complexity=request.complexity,
            has_chimney=request.has_chimney,
            has_skylights=request.has_skylights,
            material_lines=request.material_lines,
            labor_lines=request.labor_lines,
            has_subs=request.has_subs,
            quoted_total=request.quoted_total,
        )

        return FullEstimateResponse(
            estimate=price_result["estimate"],
            range_low=price_result["range_low"],
            range_high=price_result["range_high"],
            confidence=price_result["confidence"],
            model=price_result["model"],
            materials=[MaterialPrediction(**m) for m in material_result["materials"]],
            total_materials_cost=material_result["total_materials_cost"],
            applied_rules=material_result["applied_rules"],
        )
    except Exception as e:
        logger.error(f"Full estimate error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/estimate/hybrid", response_model=HybridQuoteResponse)
async def create_hybrid_estimate(request: HybridQuoteRequest):
    """Generate full hybrid quote using CBR + ML + LLM merger.

    This endpoint:
    1. Runs CBR (similar case retrieval) and ML (material prediction) in parallel
    2. Merges results using LLM with structured outputs
    3. Generates three-tier pricing (Basic/Standard/Premium)
    4. Returns confidence score and review flag

    Service calls (labor-only jobs) are detected and handled separately.

    Response time target: <5 seconds
    """
    # Service call detection: skip materials pipeline for labor-only jobs
    is_service_call = (
        request.material_lines == 0 or
        request.sqft < 100
    )

    if is_service_call:
        logger.info(f"Service call detected (sqft={request.sqft}, material_lines={request.material_lines})")
        # For service calls, use simple price prediction only
        try:
            price_result = predict(
                sqft=request.sqft,
                category=request.category,
                material_lines=request.material_lines,
                labor_lines=request.labor_lines,
                has_subs=1 if request.has_subs else 0,
                complexity=request.complexity_aggregate,
            )

            # Service call response: labor only, no materials
            return HybridQuoteResponse(
                work_items=[],
                materials=[],
                total_labor_hours=request.labor_lines * 2.0,  # Rough estimate
                total_materials_cost=0,
                total_price=price_result["estimate"],
                overall_confidence=0.6,  # Service calls are straightforward
                reasoning="Service call detected. Labor-only estimate based on ML prediction.",
                pricing_tiers=[
                    PricingTier(
                        tier="Basic",
                        total_price=round(price_result["estimate"] * 0.9, 2),
                        materials_cost=0,
                        labor_cost=round(price_result["estimate"] * 0.9, 2),
                        description="Standard service call"
                    ),
                    PricingTier(
                        tier="Standard",
                        total_price=round(price_result["estimate"], 2),
                        materials_cost=0,
                        labor_cost=round(price_result["estimate"], 2),
                        description="Service call with inspection"
                    ),
                    PricingTier(
                        tier="Premium",
                        total_price=round(price_result["estimate"] * 1.2, 2),
                        materials_cost=0,
                        labor_cost=round(price_result["estimate"] * 1.2, 2),
                        description="Emergency/rush service call"
                    ),
                ],
                needs_review=False,  # Service calls are low complexity
                cbr_cases_used=0,
                ml_confidence=price_result["confidence"],
                processing_time_ms=50,  # Fast path
            )
        except Exception as e:
            logger.error(f"Service call estimate error: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    # Normal path: full hybrid quote generation
    try:
        response = await generate_hybrid_quote(request)
        return response
    except RuntimeError as e:
        # Both CBR and ML failed
        logger.error(f"Hybrid quote failed: {e}")
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        logger.error(f"Hybrid quote error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
