"""Pydantic models for red flag evaluation and quote sending workflow.

This module defines schemas for:
- Red flag warnings (budget, geographic, material, crew, margin)
- Send submission requests with send options (now/schedule/draft)
- Send status tracking
- Red flag dismissal
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, model_validator


class RedFlagSeverity(str, Enum):
    """Red flag severity levels."""

    warning = "warning"
    critical = "critical"


class RedFlagCategory(str, Enum):
    """Red flag categories for risk evaluation."""

    budget_mismatch = "budget_mismatch"
    geographic = "geographic"
    material_risk = "material_risk"
    crew_availability = "crew_availability"
    low_margin = "low_margin"


class RedFlagResponse(BaseModel):
    """Red flag response with bilingual messages."""

    category: RedFlagCategory = Field(
        description="Red flag category identifier"
    )
    severity: RedFlagSeverity = Field(
        description="Severity level: warning or critical"
    )
    message_fr: str = Field(
        description="French message for Quebec users"
    )
    message_en: str = Field(
        description="English message for translation support"
    )
    dismissible: bool = Field(
        default=True,
        description="Whether this flag can be dismissed by estimator"
    )


class SendStatus(str, Enum):
    """Send status for submission tracking."""

    draft = "draft"
    scheduled = "scheduled"
    sent = "sent"
    failed = "failed"


class SendSubmissionRequest(BaseModel):
    """Request model for sending quote to client."""

    send_option: str = Field(
        ...,
        pattern="^(now|schedule|draft)$",
        description="Send option: now (immediate), schedule (future), or draft (save only)"
    )
    recipient_email: Optional[str] = Field(
        None,
        pattern=r"^[^@]+@[^@]+\.[^@]+$",
        description="Client email address (required for now/schedule)"
    )
    email_subject: Optional[str] = Field(
        None,
        description="Email subject line"
    )
    email_body: Optional[str] = Field(
        None,
        description="Email body (HTML supported)"
    )
    scheduled_send_at: Optional[datetime] = Field(
        None,
        description="Scheduled send timestamp (required for schedule option)"
    )

    @model_validator(mode="after")
    def validate_send_requirements(self) -> "SendSubmissionRequest":
        """Validate cross-field requirements for send options.

        - now: requires recipient_email
        - schedule: requires recipient_email and scheduled_send_at
        - draft: no additional requirements
        """
        if self.send_option == "now":
            if not self.recipient_email:
                raise ValueError("recipient_email is required when send_option is 'now'")

        elif self.send_option == "schedule":
            if not self.recipient_email:
                raise ValueError("recipient_email is required when send_option is 'schedule'")
            if not self.scheduled_send_at:
                raise ValueError("scheduled_send_at is required when send_option is 'schedule'")

        return self


class DismissFlagsRequest(BaseModel):
    """Request model for dismissing red flags."""

    dismissed_categories: List[RedFlagCategory] = Field(
        description="List of red flag categories to dismiss"
    )
    dismissed_by: str = Field(
        default="estimator",
        description="User who dismissed the flags"
    )
