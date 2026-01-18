"""Estimate endpoint for ML predictions."""

from fastapi import APIRouter, HTTPException

from backend.app.schemas.estimate import EstimateRequest, EstimateResponse
from backend.app.services.predictor import predict

router = APIRouter(tags=["estimate"])


@router.post("/estimate", response_model=EstimateResponse)
def create_estimate(request: EstimateRequest):
    """Generate price estimate for roofing job.

    Uses ML model to predict price based on sqft, category, and other factors.
    Returns estimate with confidence range.
    """
    try:
        result = predict(
            sqft=request.sqft,
            category=request.category,
            material_lines=request.material_lines,
            labor_lines=request.labor_lines,
            has_subs=request.has_subs,
            complexity=request.complexity,
        )
        return EstimateResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
