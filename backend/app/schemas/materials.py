"""Pydantic models for material prediction endpoints."""

from typing import List, Optional, Literal

from pydantic import BaseModel, Field


class MaterialEstimateRequest(BaseModel):
    """Request for material prediction."""

    sqft: float = Field(gt=0, le=100000, description="Square footage of roof")
    category: str = Field(description="Job category (Bardeaux, Elastomere, etc.)")
    complexity: int = Field(default=10, ge=1, le=100)
    has_chimney: bool = Field(default=False)
    has_skylights: bool = Field(default=False)
    material_lines: int = Field(default=5, ge=0, le=100)
    labor_lines: int = Field(default=2, ge=0, le=50)
    has_subs: bool = Field(default=False)
    quoted_total: Optional[float] = Field(
        default=None, description="If known, helps prediction"
    )


class MaterialPrediction(BaseModel):
    """Single material prediction."""

    material_id: int
    quantity: float
    unit_price: float
    total: float
    confidence: Literal["HIGH", "MEDIUM", "LOW"]


class MaterialEstimateResponse(BaseModel):
    """Response for /estimate/materials endpoint."""

    materials: List[MaterialPrediction]
    total_materials_cost: float
    model_info: str
    applied_rules: List[str] = []  # Co-occurrence rules that fired


class FullEstimateResponse(BaseModel):
    """Response for /estimate/full endpoint."""

    # Price estimate (from existing predictor)
    estimate: float
    range_low: float
    range_high: float
    confidence: Literal["HIGH", "MEDIUM", "LOW"]
    model: str
    # Material prediction
    materials: List[MaterialPrediction]
    total_materials_cost: float
    applied_rules: List[str] = []
