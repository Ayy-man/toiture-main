"""Pydantic models for estimate endpoint request/response."""

from typing import List, Literal, Optional

from pydantic import BaseModel, Field, field_validator


# Allowed categories for roofing jobs
ALLOWED_CATEGORIES = [
    "Bardeaux",
    "Élastomère",
    "Other",
    "Gutters",
    "Heat Cables",
    "Insulation",
    "Service Call",
    "Skylights",
    "Unknown",
    "Ventilation",
]


class EstimateRequest(BaseModel):
    """Request model for estimate endpoint."""

    sqft: float = Field(gt=0, le=100000, description="Square footage of roof")
    category: str = Field(description="Job category")
    material_lines: int = Field(default=5, ge=0, le=100)
    labor_lines: int = Field(default=2, ge=0, le=50)
    has_subs: Literal[0, 1] = 0
    complexity: int = Field(default=10, ge=1, le=100)

    @field_validator("category")
    @classmethod
    def validate_category(cls, v: str) -> str:
        """Validate category against allowed values.

        Accepts both "Elastomere" (without accent) and "Élastomère" (with accent),
        normalizing to the accented version.
        """
        # Normalize non-accented to accented version
        if v == "Elastomere":
            return "Élastomère"

        if v not in ALLOWED_CATEGORIES:
            raise ValueError(
                f"Invalid category '{v}'. Must be one of: {', '.join(ALLOWED_CATEGORIES)}"
            )
        return v


class SimilarCase(BaseModel):
    """A similar historical case from CBR."""

    case_id: str
    similarity: float  # Cosine similarity score 0-1
    category: Optional[str] = None
    sqft: Optional[float] = None
    total: Optional[float] = None
    per_sqft: Optional[float] = None
    year: Optional[int] = None


class EstimateResponse(BaseModel):
    """Response model for estimate endpoint."""

    estimate: float
    range_low: float
    range_high: float
    confidence: Literal["HIGH", "MEDIUM", "LOW"]
    model: str
    similar_cases: List[SimilarCase] = []
    reasoning: Optional[str] = None  # LLM-generated explanation
