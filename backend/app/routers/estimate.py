"""Estimate endpoint for ML predictions."""

import logging

from fastapi import APIRouter, HTTPException

from app.schemas.estimate import EstimateRequest, EstimateResponse, SimilarCase
from app.services.embeddings import build_query_text, generate_query_embedding
from app.services.llm_reasoning import generate_reasoning
from app.services.pinecone_cbr import query_similar_cases
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

        # Get similar cases from CBR
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
            similar_cases = []

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
