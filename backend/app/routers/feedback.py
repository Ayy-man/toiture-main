"""Feedback endpoints for estimate review and collection."""

import json
import logging
from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query

from app.schemas.feedback import (
    CategoryInsight,
    EstimateDetail,
    EstimateListItem,
    FeedbackEntry,
    FeedbackListResponse,
    FeedbackResponse,
    FeedbackSummary,
    QuickFeedbackRequest,
    QuickFeedbackResponse,
    SubmitFeedbackRequest,
)
from app.services.supabase_client import get_supabase

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


@router.post("/quick", response_model=QuickFeedbackResponse)
def submit_quick_feedback(request: QuickFeedbackRequest):
    """Submit quick feedback (thumbs up/down) on an estimate.

    This is for collecting user feedback directly from the estimate result,
    without requiring the full review workflow.
    """
    supabase = get_supabase()
    if supabase is None:
        raise HTTPException(
            status_code=503, detail="Supabase not configured. Feedback system unavailable."
        )

    try:
        import json
        from datetime import datetime

        # Insert into cortex_feedback table
        feedback_data = {
            "estimate_id": request.estimate_id,
            "input_params": json.dumps(request.input_params),
            "predicted_price": request.predicted_price,
            "predicted_materials": json.dumps(request.predicted_materials) if request.predicted_materials else None,
            "feedback": request.feedback,
            "actual_price": request.actual_price,
            "reason": request.reason,
            "issues": json.dumps(request.issues) if request.issues else None,
            "created_at": datetime.utcnow().isoformat(),
        }

        supabase.table("cortex_feedback").insert(feedback_data).execute()
        logger.info(f"Quick feedback recorded for estimate {request.estimate_id}: {request.feedback}")

        return QuickFeedbackResponse(success=True, message="Merci pour votre retour!")

    except Exception as e:
        logger.error(f"Failed to submit quick feedback: {e}")
        raise HTTPException(status_code=500, detail="Failed to submit feedback")


@router.get("", response_model=FeedbackListResponse)
def get_feedback_list(
    type: Optional[str] = Query(None, description="Filter by feedback type: positive or negative"),
    category: Optional[str] = Query(None, description="Filter by category"),
    since: Optional[str] = Query(None, description="Filter by date (ISO format, e.g., 2025-01-01)"),
    sort: Optional[str] = Query("date", description="Sort by: date or gap"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
):
    """Get all feedback entries with optional filters.

    Supports filtering by type, category, date, and sorting by date or price gap.
    """
    supabase = get_supabase()
    if supabase is None:
        raise HTTPException(
            status_code=503, detail="Supabase not configured. Feedback system unavailable."
        )

    try:
        # Build query
        query = supabase.table("cortex_feedback").select("*", count="exact")

        # Apply filters
        if type and type in ["positive", "negative"]:
            query = query.eq("feedback", type)

        if since:
            query = query.gte("created_at", since)

        # Note: category filtering will be done post-query since it's in JSON

        # Apply sorting
        if sort == "gap":
            # Sort by absolute price gap - will need post-processing
            query = query.order("created_at", desc=True)
        else:
            query = query.order("created_at", desc=True)

        # Execute count query first
        count_result = query.execute()
        total = count_result.count or 0

        # Apply pagination
        offset = (page - 1) * limit
        query = supabase.table("cortex_feedback").select("*")

        if type and type in ["positive", "negative"]:
            query = query.eq("feedback", type)
        if since:
            query = query.gte("created_at", since)

        query = query.order("created_at", desc=True).range(offset, offset + limit - 1)
        result = query.execute()

        # Process entries
        entries = []
        for row in result.data:
            # Parse input_params to extract category and sqft
            input_params = row.get("input_params", {})
            if isinstance(input_params, str):
                try:
                    input_params = json.loads(input_params)
                except:
                    input_params = {}

            row_category = input_params.get("category")
            row_sqft = input_params.get("sqft")

            # Filter by category if specified
            if category and row_category and row_category.lower() != category.lower():
                continue

            # Calculate price gap
            predicted = row.get("predicted_price", 0)
            actual = row.get("actual_price")
            price_gap = None
            price_gap_percent = None

            if actual is not None and predicted > 0:
                price_gap = actual - predicted
                price_gap_percent = (price_gap / predicted) * 100

            # Parse predicted_materials
            predicted_materials = row.get("predicted_materials")
            if isinstance(predicted_materials, str):
                try:
                    predicted_materials = json.loads(predicted_materials)
                except:
                    predicted_materials = None

            # Parse issues
            issues = row.get("issues")
            if isinstance(issues, str):
                try:
                    issues = json.loads(issues)
                except:
                    issues = None

            entry = FeedbackEntry(
                id=row.get("id", ""),
                estimate_id=row.get("estimate_id", ""),
                created_at=row.get("created_at"),
                input_params=input_params,
                predicted_price=predicted,
                predicted_materials=predicted_materials,
                feedback=row.get("feedback", "positive"),
                actual_price=actual,
                reason=row.get("reason"),
                issues=issues,
                category=row_category,
                sqft=row_sqft,
                price_gap=price_gap,
                price_gap_percent=price_gap_percent,
            )
            entries.append(entry)

        # Sort by gap if requested
        if sort == "gap":
            entries.sort(
                key=lambda x: abs(x.price_gap) if x.price_gap is not None else 0,
                reverse=True
            )

        has_more = (page * limit) < total

        return FeedbackListResponse(
            items=entries[:limit],  # Ensure we don't exceed limit after category filter
            total=total,
            page=page,
            limit=limit,
            has_more=has_more,
        )

    except Exception as e:
        logger.error(f"Failed to fetch feedback list: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch feedback list")


@router.get("/summary", response_model=FeedbackSummary)
def get_feedback_summary():
    """Get summary statistics for the feedback dashboard.

    Returns total count, approval rate, average gap, and weekly count.
    """
    supabase = get_supabase()
    if supabase is None:
        raise HTTPException(
            status_code=503, detail="Supabase not configured. Feedback system unavailable."
        )

    try:
        # Get all feedback entries
        result = supabase.table("cortex_feedback").select("*").execute()
        entries = result.data or []

        total_count = len(entries)
        positive_count = sum(1 for e in entries if e.get("feedback") == "positive")
        negative_count = total_count - positive_count

        approval_rate = (positive_count / total_count * 100) if total_count > 0 else 0

        # Calculate average gap (only for entries with actual_price)
        gaps = []
        gap_percents = []
        for entry in entries:
            predicted = entry.get("predicted_price", 0)
            actual = entry.get("actual_price")
            if actual is not None and predicted > 0:
                gap = abs(actual - predicted)
                gap_percent = abs((actual - predicted) / predicted * 100)
                gaps.append(gap)
                gap_percents.append(gap_percent)

        avg_gap_absolute = sum(gaps) / len(gaps) if gaps else None
        avg_gap_percent = sum(gap_percents) / len(gap_percents) if gap_percents else None

        # Count entries from last 7 days
        week_ago = datetime.utcnow() - timedelta(days=7)
        weekly_count = 0
        for entry in entries:
            created_at = entry.get("created_at")
            if created_at:
                if isinstance(created_at, str):
                    try:
                        entry_date = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                        if entry_date.replace(tzinfo=None) >= week_ago:
                            weekly_count += 1
                    except:
                        pass

        return FeedbackSummary(
            total_count=total_count,
            positive_count=positive_count,
            negative_count=negative_count,
            approval_rate=round(approval_rate, 1),
            avg_gap_absolute=round(avg_gap_absolute, 2) if avg_gap_absolute else None,
            avg_gap_percent=round(avg_gap_percent, 1) if avg_gap_percent else None,
            weekly_count=weekly_count,
        )

    except Exception as e:
        logger.error(f"Failed to fetch feedback summary: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch feedback summary")
