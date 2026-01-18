"""Pydantic models for customer search and details."""

from typing import List, Optional

from pydantic import BaseModel, Field


class CustomerResult(BaseModel):
    """Customer search result item."""

    id: str
    name: str
    city: Optional[str] = None
    total_quotes: int = 0
    lifetime_value: float = 0.0
    segment: str = "New"  # "VIP", "Regular", "New"


class QuoteHistoryItem(BaseModel):
    """Individual quote in customer history."""

    id: str
    created_at: str
    category: Optional[str] = None
    sqft: Optional[float] = None
    total_price: Optional[float] = None


class CustomerDetail(BaseModel):
    """Full customer details with quote history."""

    id: str
    name: str
    city: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    total_quotes: int = 0
    lifetime_value: float = 0.0
    segment: str = "New"
    quotes: List[QuoteHistoryItem] = Field(default_factory=list)
