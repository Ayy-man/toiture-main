"""Pydantic models for hybrid quote generation with LLM tool calling support.

This module defines the type foundation for the hybrid quote system that combines
ML predictions with CBR (Case-Based Reasoning) using LLM-powered merger logic.

Models:
- HybridQuoteRequest: Input validation for job parameters and complexity factors
- WorkItem: LLM structured output for labor items
- MaterialLineItem: LLM structured output for material items
- PricingTier: Three-tier pricing (Basic/Standard/Premium)
- HybridQuoteOutput: Full LLM tool calling schema
- HybridQuoteResponse: API response with metadata
"""

from typing import List, Literal, Optional

from pydantic import BaseModel, Field, field_validator, model_validator

from app.schemas.estimate import ALLOWED_CATEGORIES


class HybridQuoteRequest(BaseModel):
    """Request model for hybrid quote generation endpoint.

    Accepts all job parameters including 6 complexity factors that sum to
    complexity_aggregate. The system uses these to generate accurate estimates.
    """

    # Core job parameters
    sqft: Optional[float] = Field(
        default=None,
        le=100000,
        description="Square footage of roof area"
    )
    category: str = Field(
        description="Job category (e.g., Bardeaux, Elastomere)"
    )
    created_by: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Estimator name"
    )

    # NEW: Tier-based complexity (Phase 21)
    complexity_tier: Optional[int] = Field(
        default=None,
        ge=1,
        le=6,
        description="Complexity tier (1-6). When provided, uses new tier-based system."
    )
    complexity_score: Optional[int] = Field(
        default=None,
        ge=0,
        le=100,
        description="Tier-based complexity score (0-100). Auto-calculated from tier if not provided."
    )

    # NEW: Factor checklist (Phase 21) - 8 factors replacing old 6 slider values
    factor_roof_pitch: Optional[str] = Field(
        default=None,
        description="Roof pitch category: flat|low|medium|steep|very_steep"
    )
    factor_access_difficulty: Optional[List[str]] = Field(
        default=None,
        description="Access difficulty checklist items (e.g., no_crane, narrow_driveway)"
    )
    factor_demolition: Optional[str] = Field(
        default=None,
        description="Demolition type: none|single_layer|multi_layer|structural"
    )
    factor_penetrations_count: Optional[int] = Field(
        default=None,
        ge=0,
        le=100,
        description="Number of roof penetrations (vents, pipes, skylights)"
    )
    factor_security: Optional[List[str]] = Field(
        default=None,
        description="Security requirements checklist (e.g., harness, scaffolding)"
    )
    factor_material_removal: Optional[str] = Field(
        default=None,
        description="Material removal type: none|standard|heavy|hazardous"
    )
    factor_roof_sections_count: Optional[int] = Field(
        default=None,
        ge=1,
        le=20,
        description="Number of distinct roof sections"
    )
    factor_previous_layers_count: Optional[int] = Field(
        default=None,
        ge=0,
        le=10,
        description="Number of existing layers to remove"
    )

    # NEW: Manual hour override (upward only)
    manual_extra_hours: Optional[float] = Field(
        default=None,
        ge=0,
        description="Manual extra hours added by estimator (upward override only)"
    )

    # OLD: Legacy complexity factors (kept for backward compatibility)
    complexity_aggregate: Optional[int] = Field(
        default=None,
        ge=0,
        le=56,
        description="LEGACY: Sum of 6 complexity factors (0-56). Use complexity_tier for new quotes."
    )
    access_difficulty: Optional[int] = Field(
        default=None,
        ge=0,
        le=10,
        description="Difficulty accessing the roof (0=easy, 10=very difficult)"
    )
    roof_pitch: Optional[int] = Field(
        default=None,
        ge=0,
        le=8,
        description="Steepness of roof pitch (0=flat, 8=very steep)"
    )
    penetrations: Optional[int] = Field(
        default=None,
        ge=0,
        le=10,
        description="Number/complexity of roof penetrations (vents, pipes, etc.)"
    )
    material_removal: Optional[int] = Field(
        default=None,
        ge=0,
        le=8,
        description="Difficulty of existing material removal (0=none, 8=extensive)"
    )
    safety_concerns: Optional[int] = Field(
        default=None,
        ge=0,
        le=10,
        description="Safety requirements (0=standard, 10=high-risk)"
    )
    timeline_constraints: Optional[int] = Field(
        default=None,
        ge=0,
        le=10,
        description="Urgency/timeline pressure (0=flexible, 10=urgent)"
    )

    # Optional features
    has_chimney: bool = Field(
        default=False,
        description="Whether the roof has a chimney"
    )
    has_skylights: bool = Field(
        default=False,
        description="Whether the roof has skylights"
    )

    # Line item counts (for material/labor complexity)
    material_lines: int = Field(
        default=5,
        ge=0,
        le=100,
        description="Expected number of material line items"
    )
    labor_lines: int = Field(
        default=2,
        ge=0,
        le=50,
        description="Expected number of labor line items"
    )

    # Subcontractor flag
    has_subs: bool = Field(
        default=False,
        description="Whether subcontractors are involved"
    )

    # Known price (for comparison/feedback)
    quoted_total: Optional[float] = Field(
        default=None,
        ge=0,
        description="Known quoted total if available (for comparison)"
    )

    @field_validator("category")
    @classmethod
    def validate_category(cls, v: str) -> str:
        """Validate category against allowed values.

        Accepts both "Elastomere" (without accent) and "Elastomere" (with accent),
        normalizing to the accented version.
        """
        # Normalize non-accented to accented version
        if v == "Elastomere":
            return "Elastomere"

        if v not in ALLOWED_CATEGORIES:
            raise ValueError(
                f"Invalid category '{v}'. Must be one of: {', '.join(ALLOWED_CATEGORIES)}"
            )
        return v

    @model_validator(mode="after")
    def validate_sqft_required(self) -> "HybridQuoteRequest":
        """Validate that sqft is required for non-Service Call categories."""
        if self.category != "Service Call":
            if self.sqft is None or self.sqft <= 0:
                raise ValueError(
                    "Square footage is required and must be positive for this category"
                )
        return self

    @model_validator(mode="after")
    def validate_complexity(self) -> "HybridQuoteRequest":
        """Validate complexity - either old slider system or new tier system."""
        # New tier system: skip old sum validation
        if self.complexity_tier is not None:
            return self

        # Old system: validate sum if aggregate and factors are provided
        if self.complexity_aggregate is not None:
            old_fields = [
                self.access_difficulty, self.roof_pitch, self.penetrations,
                self.material_removal, self.safety_concerns, self.timeline_constraints
            ]
            if all(f is not None for f in old_fields):
                calculated_sum = sum(old_fields)
                tolerance = max(1, int(calculated_sum * 0.05))
                if abs(self.complexity_aggregate - calculated_sum) > tolerance:
                    raise ValueError(
                        f"complexity_aggregate ({self.complexity_aggregate}) must equal sum of 6 factors "
                        f"({calculated_sum}) within 5% tolerance"
                    )
        return self

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "description": "OLD format (legacy 6 sliders)",
                    "sqft": 2500,
                    "category": "Bardeaux",
                    "complexity_aggregate": 25,
                    "access_difficulty": 5,
                    "roof_pitch": 4,
                    "penetrations": 3,
                    "material_removal": 5,
                    "safety_concerns": 4,
                    "timeline_constraints": 4,
                    "has_chimney": True,
                    "has_skylights": False,
                    "material_lines": 8,
                    "labor_lines": 3,
                    "has_subs": False,
                    "quoted_total": None,
                },
                {
                    "description": "NEW format (tier-based with factor checklist)",
                    "sqft": 2500,
                    "category": "Bardeaux",
                    "complexity_tier": 3,
                    "complexity_score": 42,
                    "factor_roof_pitch": "steep",
                    "factor_access_difficulty": ["no_crane", "narrow_driveway"],
                    "factor_demolition": "multi_layer",
                    "factor_penetrations_count": 4,
                    "factor_security": ["harness"],
                    "factor_material_removal": "standard",
                    "factor_roof_sections_count": 4,
                    "factor_previous_layers_count": 2,
                    "manual_extra_hours": 5.0,
                    "has_chimney": True,
                    "has_skylights": False,
                    "material_lines": 8,
                    "labor_lines": 3,
                    "has_subs": False,
                    "quoted_total": None,
                }
            ]
        }
    }


class WorkItem(BaseModel):
    """Work item (labor) for LLM structured output.

    Represents a single labor task with estimated hours and source tracking.
    """

    name: str = Field(
        description="Description of the work item/labor task"
    )
    labor_hours: float = Field(
        ge=0,
        description="Estimated labor hours for this task"
    )
    source: Literal["CBR", "ML", "MERGED"] = Field(
        description="Source of this estimate: CBR (case-based), ML (model), or MERGED (combined)"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "Tear-off existing shingles",
                    "labor_hours": 16.0,
                    "source": "MERGED",
                }
            ]
        }
    }


class MaterialLineItem(BaseModel):
    """Material line item for LLM structured output.

    Represents a single material with quantity, pricing, and confidence tracking.
    """

    material_id: int = Field(
        ge=1,
        le=1000,
        description="Material ID from the material database"
    )
    quantity: float = Field(
        gt=0,
        description="Quantity of material needed"
    )
    unit_price: float = Field(
        ge=0,
        description="Price per unit of material"
    )
    total: float = Field(
        ge=0,
        description="Total cost (quantity * unit_price)"
    )
    source: Literal["CBR", "ML", "MERGED"] = Field(
        description="Source of this estimate: CBR (case-based), ML (model), or MERGED (combined)"
    )
    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Confidence score for this material prediction (0.0-1.0)"
    )

    @field_validator("total")
    @classmethod
    def validate_total(cls, v: float, info) -> float:
        """Validate that total approximately equals quantity * unit_price."""
        data = info.data
        if "quantity" in data and "unit_price" in data:
            expected = data["quantity"] * data["unit_price"]
            # Allow small rounding differences (within 1 cent)
            if abs(v - expected) > 0.01:
                raise ValueError(
                    f"total ({v}) must equal quantity * unit_price ({expected})"
                )
        return v

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "material_id": 42,
                    "quantity": 25.0,
                    "unit_price": 45.99,
                    "total": 1149.75,
                    "source": "ML",
                    "confidence": 0.85,
                }
            ]
        }
    }


class PricingTier(BaseModel):
    """Three-tier pricing model (Basic/Standard/Premium).

    Each tier represents a different quality/service level with associated pricing.
    """

    tier: Literal["Basic", "Standard", "Premium"] = Field(
        description="Pricing tier level"
    )
    total_price: float = Field(
        ge=0,
        description="Total price for this tier"
    )
    materials_cost: float = Field(
        ge=0,
        description="Materials cost component"
    )
    labor_cost: float = Field(
        ge=0,
        description="Labor cost component"
    )
    description: str = Field(
        description="Brief explanation of what this tier includes and tier differences"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "tier": "Standard",
                    "total_price": 12500.00,
                    "materials_cost": 7500.00,
                    "labor_cost": 5000.00,
                    "description": "Standard quality materials with full warranty coverage",
                }
            ]
        }
    }


class HybridQuoteOutput(BaseModel):
    """LLM tool calling schema for hybrid quote generation.

    This model is designed to be converted to JSON schema for Claude's
    structured outputs API. It defines the complete output structure
    for the LLM merger logic.
    """

    work_items: List[WorkItem] = Field(
        description="List of labor/work items with hour estimates"
    )
    materials: List[MaterialLineItem] = Field(
        description="List of material line items with quantities and pricing"
    )
    total_labor_hours: float = Field(
        ge=0,
        description="Total labor hours across all work items"
    )
    total_materials_cost: float = Field(
        ge=0,
        description="Total cost of all materials"
    )
    total_price: float = Field(
        ge=0,
        description="Final total price (materials + labor + margin)"
    )
    overall_confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Overall confidence in this estimate (0.0-1.0)"
    )
    reasoning: str = Field(
        description="Explanation of merger decisions and estimate rationale"
    )
    pricing_tiers: List[PricingTier] = Field(
        description="Three pricing tiers: Basic, Standard, Premium"
    )

    @model_validator(mode="after")
    def validate_pricing_tiers(self) -> "HybridQuoteOutput":
        """Ensure exactly 3 pricing tiers (Basic, Standard, Premium)."""
        if len(self.pricing_tiers) != 3:
            raise ValueError(
                f"pricing_tiers must have exactly 3 items, got {len(self.pricing_tiers)}"
            )

        tier_names = {tier.tier for tier in self.pricing_tiers}
        expected_tiers = {"Basic", "Standard", "Premium"}

        if tier_names != expected_tiers:
            raise ValueError(
                f"pricing_tiers must include Basic, Standard, and Premium. "
                f"Got: {tier_names}"
            )

        return self

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "work_items": [
                        {"name": "Tear-off existing shingles", "labor_hours": 16.0, "source": "MERGED"},
                        {"name": "Install new shingles", "labor_hours": 24.0, "source": "MERGED"},
                    ],
                    "materials": [
                        {
                            "material_id": 42,
                            "quantity": 25.0,
                            "unit_price": 45.99,
                            "total": 1149.75,
                            "source": "ML",
                            "confidence": 0.85,
                        }
                    ],
                    "total_labor_hours": 40.0,
                    "total_materials_cost": 7500.00,
                    "total_price": 12500.00,
                    "overall_confidence": 0.78,
                    "reasoning": "Combined CBR case #123 with ML prediction, weighted by confidence scores",
                    "pricing_tiers": [
                        {
                            "tier": "Basic",
                            "total_price": 10000.00,
                            "materials_cost": 6000.00,
                            "labor_cost": 4000.00,
                            "description": "Economy materials, standard installation",
                        },
                        {
                            "tier": "Standard",
                            "total_price": 12500.00,
                            "materials_cost": 7500.00,
                            "labor_cost": 5000.00,
                            "description": "Quality materials with full warranty",
                        },
                        {
                            "tier": "Premium",
                            "total_price": 16000.00,
                            "materials_cost": 9500.00,
                            "labor_cost": 6500.00,
                            "description": "Premium materials, extended warranty, priority scheduling",
                        },
                    ],
                }
            ]
        }
    }


class HybridQuoteResponse(BaseModel):
    """API response model for hybrid quote generation.

    Extends HybridQuoteOutput with request metadata and review flags.
    """

    # Fields from HybridQuoteOutput
    work_items: List[WorkItem] = Field(
        description="List of labor/work items with hour estimates"
    )
    materials: List[MaterialLineItem] = Field(
        description="List of material line items with quantities and pricing"
    )
    total_labor_hours: float = Field(
        ge=0,
        description="Total labor hours across all work items"
    )
    total_materials_cost: float = Field(
        ge=0,
        description="Total cost of all materials"
    )
    total_price: float = Field(
        ge=0,
        description="Final total price (materials + labor + margin)"
    )
    overall_confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Overall confidence in this estimate (0.0-1.0)"
    )
    reasoning: str = Field(
        description="Explanation of merger decisions and estimate rationale"
    )
    pricing_tiers: List[PricingTier] = Field(
        description="Three pricing tiers: Basic, Standard, Premium"
    )

    # Response metadata
    request_id: Optional[str] = Field(
        default=None,
        description="Unique request ID for tracking"
    )
    needs_review: bool = Field(
        description="True if confidence < 0.5, flagged for human review"
    )
    cbr_cases_used: int = Field(
        ge=0,
        description="Number of similar CBR cases found and used"
    )
    ml_confidence: Literal["HIGH", "MEDIUM", "LOW"] = Field(
        description="ML model confidence level"
    )
    processing_time_ms: int = Field(
        ge=0,
        description="Total processing time in milliseconds"
    )

    @model_validator(mode="after")
    def validate_pricing_tiers(self) -> "HybridQuoteResponse":
        """Ensure exactly 3 pricing tiers (Basic, Standard, Premium)."""
        if len(self.pricing_tiers) != 3:
            raise ValueError(
                f"pricing_tiers must have exactly 3 items, got {len(self.pricing_tiers)}"
            )

        tier_names = {tier.tier for tier in self.pricing_tiers}
        expected_tiers = {"Basic", "Standard", "Premium"}

        if tier_names != expected_tiers:
            raise ValueError(
                f"pricing_tiers must include Basic, Standard, and Premium. "
                f"Got: {tier_names}"
            )

        return self

    @model_validator(mode="after")
    def set_needs_review(self) -> "HybridQuoteResponse":
        """Auto-set needs_review based on confidence threshold."""
        # This is informational - the actual value should be set by the caller
        # but we can validate consistency
        if self.overall_confidence < 0.5 and not self.needs_review:
            # Log warning but don't fail - caller may have overridden
            pass
        return self

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "work_items": [
                        {"name": "Tear-off existing shingles", "labor_hours": 16.0, "source": "MERGED"},
                    ],
                    "materials": [
                        {
                            "material_id": 42,
                            "quantity": 25.0,
                            "unit_price": 45.99,
                            "total": 1149.75,
                            "source": "ML",
                            "confidence": 0.85,
                        }
                    ],
                    "total_labor_hours": 40.0,
                    "total_materials_cost": 7500.00,
                    "total_price": 12500.00,
                    "overall_confidence": 0.78,
                    "reasoning": "Combined CBR case #123 with ML prediction",
                    "pricing_tiers": [
                        {
                            "tier": "Basic",
                            "total_price": 10000.00,
                            "materials_cost": 6000.00,
                            "labor_cost": 4000.00,
                            "description": "Economy materials",
                        },
                        {
                            "tier": "Standard",
                            "total_price": 12500.00,
                            "materials_cost": 7500.00,
                            "labor_cost": 5000.00,
                            "description": "Quality materials",
                        },
                        {
                            "tier": "Premium",
                            "total_price": 16000.00,
                            "materials_cost": 9500.00,
                            "labor_cost": 6500.00,
                            "description": "Premium materials",
                        },
                    ],
                    "request_id": "req_abc123",
                    "needs_review": False,
                    "cbr_cases_used": 5,
                    "ml_confidence": "HIGH",
                    "processing_time_ms": 1234,
                }
            ]
        }
    }
