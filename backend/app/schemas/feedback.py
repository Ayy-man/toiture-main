"""Pydantic models for feedback system endpoints."""

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field


class EstimateListItem(BaseModel):
    """Summary view of an estimate for list display."""

    id: str
    created_at: datetime
    sqft: float
    category: str
    ai_estimate: float
    confidence: Literal["HIGH", "MEDIUM", "LOW"]
    reviewed: bool


class EstimateDetail(EstimateListItem):
    """Full estimate details for individual view."""

    material_lines: int
    labor_lines: int
    has_subs: bool
    complexity: int
    range_low: float
    range_high: float
    model: str
    reasoning: Optional[str] = None


class SubmitFeedbackRequest(BaseModel):
    """Request body for submitting feedback on an estimate."""

    estimate_id: str = Field(..., description="UUID of the estimate to review")
    laurent_price: float = Field(
        ..., gt=0, description="Laurent's actual price for this job"
    )


class FeedbackResponse(BaseModel):
    """Response after successfully submitting feedback."""

    status: Literal["success"]
    estimate_id: str
