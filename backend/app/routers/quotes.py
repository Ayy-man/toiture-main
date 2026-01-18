"""Quotes listing endpoints for admin dashboard Historique tab."""

import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from app.schemas.quotes import PaginatedQuotes, QuoteItem
from app.services.supabase_client import get_supabase

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/quotes", tags=["quotes"])


@router.get("/", response_model=PaginatedQuotes)
def get_quotes(
    page: int = Query(default=1, ge=1, description="Page number"),
    per_page: int = Query(default=20, ge=1, le=100, description="Items per page"),
    category: Optional[str] = Query(default=None, description="Filter by category"),
    city: Optional[str] = Query(default=None, description="Filter by city"),
    min_sqft: Optional[float] = Query(default=None, ge=0, description="Minimum sqft"),
    max_sqft: Optional[float] = Query(default=None, ge=0, description="Maximum sqft"),
    min_price: Optional[float] = Query(default=None, ge=0, description="Minimum price"),
    max_price: Optional[float] = Query(default=None, ge=0, description="Maximum price"),
    start_date: Optional[str] = Query(default=None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(default=None, description="End date (YYYY-MM-DD)"),
):
    """Get paginated list of quotes with optional filters.

    Returns quotes from the estimates table with pagination and filtering support.
    """
    supabase = get_supabase()
    if supabase is None:
        raise HTTPException(
            status_code=503, detail="Supabase not configured. Quotes system unavailable."
        )

    try:
        # Build base query with count
        query = supabase.table("estimates").select(
            "id, created_at, sqft, category, ai_estimate, confidence",
            count="exact"
        )

        # Apply filters
        if category:
            query = query.eq("category", category)
        if city:
            query = query.ilike("city", f"%{city}%")
        if min_sqft is not None:
            query = query.gte("sqft", min_sqft)
        if max_sqft is not None:
            query = query.lte("sqft", max_sqft)
        if min_price is not None:
            query = query.gte("ai_estimate", min_price)
        if max_price is not None:
            query = query.lte("ai_estimate", max_price)
        if start_date:
            query = query.gte("created_at", start_date)
        if end_date:
            # Add time to make end_date inclusive
            query = query.lte("created_at", f"{end_date}T23:59:59")

        # Apply ordering and pagination
        offset = (page - 1) * per_page
        query = query.order("created_at", desc=True)
        query = query.range(offset, offset + per_page - 1)

        result = query.execute()

        # Map estimates table fields to QuoteItem schema
        items = []
        for row in result.data:
            items.append(QuoteItem(
                id=row["id"],
                client_name=row.get("client_name"),
                category=row.get("category"),
                city=row.get("city"),
                sqft=row.get("sqft"),
                total_price=row.get("ai_estimate"),  # Map ai_estimate to total_price
                margin_percent=row.get("margin_percent"),
                created_at=row["created_at"],
            ))

        # Calculate pagination metadata
        total = result.count if result.count is not None else len(items)
        total_pages = (total + per_page - 1) // per_page if total > 0 else 1

        return PaginatedQuotes(
            items=items,
            total=total,
            page=page,
            per_page=per_page,
            total_pages=total_pages,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch quotes: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch quotes")
