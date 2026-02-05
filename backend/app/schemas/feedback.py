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


class QuickFeedbackRequest(BaseModel):
    """Request body for submitting quick feedback (thumbs up/down) on an estimate."""

    estimate_id: str = Field(..., description="UUID of the estimate")
    input_params: dict = Field(..., description="Original input parameters")
    predicted_price: float = Field(..., description="AI predicted price")
    predicted_materials: Optional[list] = Field(
        default=None, description="Predicted materials if full quote"
    )
    feedback: Literal["positive", "negative"] = Field(
        ..., description="Was the estimate helpful?"
    )
    actual_price: Optional[float] = Field(
        default=None, description="User's actual/expected price"
    )
    reason: Optional[str] = Field(
        default=None, description="Reason for negative feedback"
    )
    # Structured feedback fields for model tuning
    issues: Optional[list[str]] = Field(
        default=None,
        description="List of issue categories: missing_materials, wrong_quantities, labor_too_low, labor_too_high, complexity_mismatch, cbr_irrelevant"
    )


class QuickFeedbackResponse(BaseModel):
    """Response after submitting quick feedback."""

    success: bool
    message: str


# === Feedback Review Page Schemas ===


class FeedbackEntry(BaseModel):
    """A single feedback entry for the Retours page."""

    id: str
    estimate_id: str
    created_at: datetime
    input_params: dict
    predicted_price: float
    predicted_materials: Optional[list] = None
    feedback: Literal["positive", "negative"]
    actual_price: Optional[float] = None
    reason: Optional[str] = None
    issues: Optional[list[str]] = None  # Structured issue categories
    # Computed fields
    category: Optional[str] = None
    sqft: Optional[float] = None
    price_gap: Optional[float] = None
    price_gap_percent: Optional[float] = None


class FeedbackListResponse(BaseModel):
    """Paginated list of feedback entries."""

    items: list[FeedbackEntry]
    total: int
    page: int
    limit: int
    has_more: bool


class FeedbackSummary(BaseModel):
    """Summary statistics for feedback dashboard."""

    total_count: int
    positive_count: int
    negative_count: int
    approval_rate: float  # percentage 0-100
    avg_gap_absolute: Optional[float] = None  # average $ difference
    avg_gap_percent: Optional[float] = None  # average % difference
    weekly_count: int


class CategoryInsight(BaseModel):
    """Insight for a category's estimation accuracy."""

    category: str
    count: int
    avg_gap_percent: float
    direction: Literal["under", "over"]  # under-estimated or over-estimated
