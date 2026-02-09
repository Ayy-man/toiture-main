"""Pydantic models for submission workflow with approval process.

This module defines the type foundation for the editable submission system
with state machine workflow, notes, audit trail, and upsell support.

Models:
- SubmissionStatus: Enum for workflow states
- VALID_TRANSITIONS: State machine transition rules
- LineItem: Editable material/labor line items
- Note: Timestamped attributed notes
- AuditEntry: Audit log entries for state changes
- SubmissionCreate: Create new submission from quote
- SubmissionUpdate: Update draft submission
- SubmissionResponse: Full submission with metadata
- SubmissionListItem: List view with summary data
- NoteCreate: Add note to submission
- UpsellCreate: Create upsell child submission
"""

from enum import Enum
from typing import Dict, List, Literal, Optional

from pydantic import BaseModel, Field, field_validator, model_validator


class SubmissionStatus(str, Enum):
    """Submission workflow status states."""

    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"


# State machine: defines valid status transitions
VALID_TRANSITIONS: Dict[SubmissionStatus, List[SubmissionStatus]] = {
    SubmissionStatus.DRAFT: [SubmissionStatus.PENDING_APPROVAL],
    SubmissionStatus.PENDING_APPROVAL: [
        SubmissionStatus.APPROVED,
        SubmissionStatus.REJECTED,
        SubmissionStatus.DRAFT,
    ],
    SubmissionStatus.APPROVED: [],  # Terminal state
    SubmissionStatus.REJECTED: [SubmissionStatus.DRAFT],
}


class LineItem(BaseModel):
    """Editable line item for materials or labor.

    Supports in-place editing of quantities and prices with automatic
    total recalculation and validation.
    """

    id: str = Field(description="Unique line item ID (UUID)")
    type: Literal["material", "labor"] = Field(description="Line item type")
    material_id: Optional[int] = Field(
        default=None, description="Material ID from materials table (for material items)"
    )
    name: str = Field(description="Display name for line item")
    quantity: float = Field(gt=0, description="Quantity (must be positive)")
    unit_price: float = Field(ge=0, description="Price per unit")
    total: float = Field(ge=0, description="Total cost (quantity * unit_price)")
    order: int = Field(ge=0, description="Display order for sorting")

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
                    "id": "line_abc123",
                    "type": "material",
                    "material_id": 42,
                    "name": "IKO Cambridge Shingles",
                    "quantity": 25.0,
                    "unit_price": 45.99,
                    "total": 1149.75,
                    "order": 0,
                }
            ]
        }
    }


class Note(BaseModel):
    """Timestamped attributed note attached to submission."""

    id: str = Field(description="Note ID (UUID)")
    text: str = Field(description="Note content")
    created_by: str = Field(description="User who created the note")
    created_at: str = Field(description="ISO timestamp when note was created")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "note_xyz789",
                    "text": "Client requested premium shingles upgrade",
                    "created_by": "steven@toitureslv.com",
                    "created_at": "2026-02-13T14:30:00Z",
                }
            ]
        }
    }


class AuditEntry(BaseModel):
    """Audit log entry for tracking submission changes."""

    action: str = Field(
        description="Action performed (e.g., 'created', 'edited', 'finalized', 'approved')"
    )
    user: str = Field(description="User who performed the action")
    timestamp: str = Field(description="ISO timestamp of the action")
    changes: Optional[dict] = Field(
        default=None, description="Changed fields (old/new values)"
    )
    reason: Optional[str] = Field(default=None, description="Reason for action (e.g., rejection reason)")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "action": "finalized",
                    "user": "steven@toitureslv.com",
                    "timestamp": "2026-02-13T15:00:00Z",
                    "changes": {"status": {"old": "draft", "new": "pending_approval"}},
                    "reason": None,
                }
            ]
        }
    }


class SubmissionCreate(BaseModel):
    """Create new submission from hybrid quote output."""

    category: str = Field(description="Job category (e.g., Bardeaux, Elastomere)")
    sqft: Optional[float] = Field(
        default=None, description="Square footage of roof area"
    )
    client_name: Optional[str] = Field(
        default=None, max_length=200, description="Client name for this submission"
    )
    created_by: Optional[str] = Field(
        default=None, max_length=100, description="Estimator creating the submission"
    )
    line_items: List[LineItem] = Field(
        description="List of material and labor line items"
    )
    pricing_tiers: list = Field(
        default_factory=list,
        description="Three-tier pricing from hybrid quote (Basic/Standard/Premium)",
    )
    selected_tier: str = Field(
        default="Standard", description="Selected pricing tier"
    )
    estimate_id: Optional[str] = Field(
        default=None, description="Source estimate ID if created from estimate"
    )

    @model_validator(mode="after")
    def calculate_totals(self) -> "SubmissionCreate":
        """Calculate total costs from line items."""
        # Calculate materials and labor costs separately
        materials_cost = sum(
            item.total for item in self.line_items if item.type == "material"
        )
        labor_cost = sum(
            item.total for item in self.line_items if item.type == "labor"
        )

        # Store calculated values for service layer to use
        self.total_materials_cost = materials_cost
        self.total_labor_cost = labor_cost
        self.total_price = materials_cost + labor_cost

        return self

    # Add computed fields (will be set by validator)
    total_materials_cost: float = 0.0
    total_labor_cost: float = 0.0
    total_price: float = 0.0


class SubmissionUpdate(BaseModel):
    """Update existing draft submission (only allowed in draft status)."""

    line_items: Optional[List[LineItem]] = Field(
        default=None, description="Updated line items"
    )
    selected_tier: Optional[str] = Field(
        default=None, description="Updated selected tier"
    )
    client_name: Optional[str] = Field(
        default=None, max_length=200, description="Updated client name"
    )


class NoteCreate(BaseModel):
    """Create new note on submission."""

    text: str = Field(min_length=1, max_length=2000, description="Note content")
    created_by: str = Field(description="User creating the note")


class UpsellCreate(BaseModel):
    """Create upsell child submission linked to parent."""

    upsell_type: str = Field(
        description="Type of upsell (e.g., heating_cables, gutters)"
    )
    created_by: Optional[str] = Field(
        default=None, description="User creating the upsell"
    )


class SubmissionResponse(BaseModel):
    """Full submission response with all details."""

    # Core fields
    id: str
    created_at: str
    updated_at: str
    status: str
    category: str

    # Optional fields
    estimate_id: Optional[str] = None
    created_by: Optional[str] = None
    client_name: Optional[str] = None
    sqft: Optional[float] = None
    finalized_at: Optional[str] = None
    approved_at: Optional[str] = None
    approved_by: Optional[str] = None

    # Upsell tracking
    parent_submission_id: Optional[str] = None
    upsell_type: Optional[str] = None
    children: Optional[List["SubmissionResponse"]] = None

    # Pricing
    pricing_tiers: list
    selected_tier: str
    total_materials_cost: float
    total_labor_cost: float
    total_price: float

    # Line items, notes, audit
    line_items: List[LineItem]
    notes: List[Note]
    audit_log: List[AuditEntry]

    model_config = {"from_attributes": True}


class SubmissionListItem(BaseModel):
    """Summary view for submission list/table display."""

    id: str
    status: str
    category: str
    client_name: Optional[str] = None
    total_price: float
    created_at: str
    updated_at: str
    upsell_type: Optional[str] = None
    has_children: bool = False

    model_config = {"from_attributes": True}
