"""Pydantic models for quotes listing and filtering."""

from typing import List, Optional

from pydantic import BaseModel, Field


class QuoteItem(BaseModel):
    """Individual quote item for list display."""

    id: str
    client_name: Optional[str] = None
    category: Optional[str] = None
    city: Optional[str] = None
    sqft: Optional[float] = None
    total_price: Optional[float] = None
    margin_percent: Optional[float] = None
    created_at: str


class PaginatedQuotes(BaseModel):
    """Paginated response containing quotes and pagination metadata."""

    items: List[QuoteItem]
    total: int
    page: int = Field(..., ge=1)
    per_page: int = Field(..., ge=1, le=100)
    total_pages: int


class QuoteFilters(BaseModel):
    """Filter parameters for quotes queries."""

    category: Optional[str] = None
    city: Optional[str] = None
    min_sqft: Optional[float] = None
    max_sqft: Optional[float] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
