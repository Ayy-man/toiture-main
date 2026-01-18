"""Feedback endpoints for estimate review and collection."""

import logging
from typing import List

from fastapi import APIRouter, HTTPException

from backend.app.schemas.feedback import (
    EstimateDetail,
    EstimateListItem,
    FeedbackResponse,
    SubmitFeedbackRequest,
)
from backend.app.services.supabase_client import get_supabase

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/feedback", tags=["feedback"])


@router.get("/pending", response_model=List[EstimateListItem])
def get_pending_estimates():
    """Get all estimates pending review.

    Returns estimates where reviewed=false, ordered by most recent first.
    """
    supabase = get_supabase()
    if supabase is None:
        raise HTTPException(
            status_code=503, detail="Supabase not configured. Feedback system unavailable."
        )

    try:
        result = (
            supabase.table("estimates")
            .select("id, created_at, sqft, category, ai_estimate, confidence, reviewed")
            .eq("reviewed", False)
            .order("created_at", desc=True)
            .execute()
        )
        return result.data
    except Exception as e:
        logger.error(f"Failed to fetch pending estimates: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch pending estimates")


@router.get("/estimate/{estimate_id}", response_model=EstimateDetail)
def get_estimate_detail(estimate_id: str):
    """Get full details of a specific estimate."""
    supabase = get_supabase()
    if supabase is None:
        raise HTTPException(
            status_code=503, detail="Supabase not configured. Feedback system unavailable."
        )

    try:
        result = (
            supabase.table("estimates")
            .select("*")
            .eq("id", estimate_id)
            .execute()
        )

        if not result.data:
            raise HTTPException(status_code=404, detail=f"Estimate {estimate_id} not found")

        return result.data[0]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch estimate {estimate_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch estimate details")


@router.post("/submit", response_model=FeedbackResponse)
def submit_feedback(request: SubmitFeedbackRequest):
    """Submit feedback for an estimate.

    Records Laurent's actual price and marks the estimate as reviewed.
    """
    supabase = get_supabase()
    if supabase is None:
        raise HTTPException(
            status_code=503, detail="Supabase not configured. Feedback system unavailable."
        )

    try:
        # Get the estimate to verify it exists and get ai_estimate
        estimate_result = (
            supabase.table("estimates")
            .select("id, ai_estimate")
            .eq("id", request.estimate_id)
            .execute()
        )

        if not estimate_result.data:
            raise HTTPException(
                status_code=404, detail=f"Estimate {request.estimate_id} not found"
            )

        estimate = estimate_result.data[0]

        # Insert feedback record
        supabase.table("feedback").insert({
            "estimate_id": request.estimate_id,
            "laurent_price": request.laurent_price,
            "ai_estimate": estimate["ai_estimate"],
        }).execute()

        # Mark estimate as reviewed
        supabase.table("estimates").update({
            "reviewed": True
        }).eq("id", request.estimate_id).execute()

        return FeedbackResponse(status="success", estimate_id=request.estimate_id)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to submit feedback for {request.estimate_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to submit feedback")
