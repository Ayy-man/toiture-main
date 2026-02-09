"""Materials endpoints for database search and categories."""

import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from app.schemas.materials import (
    MaterialCategoryResponse,
    MaterialItem,
    MaterialSearchResponse,
)
from app.services.supabase_client import get_supabase

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/materials", tags=["materials"])


@router.get("/search", response_model=MaterialSearchResponse)
def search_materials(
    q: str = Query(..., min_length=2, description="Search text (minimum 2 characters)"),
    category: Optional[str] = Query(None, description="Filter by category"),
    include_flagged: bool = Query(False, description="Include flagged items in results"),
    limit: int = Query(default=50, le=200, description="Maximum results to return"),
    offset: int = Query(default=0, ge=0, description="Pagination offset"),
):
    """Search materials by name with optional category filter and pagination.

    Returns materials matching the search query, excluding labor items by default.
    Only approved materials are returned unless include_flagged is True.
    """
    supabase = get_supabase()
    if supabase is None:
        raise HTTPException(
            status_code=503, detail="Database not configured"
        )

    try:
        # Build query with exact count for pagination
        query = supabase.from_("materials").select("*", count="exact")

        # Filter by search text (fuzzy name matching)
        query = query.ilike("name", f"%{q}%")

        # Always exclude labor items from material search
        query = query.eq("item_type", "material")

        # Filter by review status unless flagged items are requested
        if not include_flagged:
            query = query.eq("review_status", "approved")

        # Filter by category if provided
        if category:
            query = query.eq("category", category)

        # Order and paginate
        query = query.order("name").range(offset, offset + limit - 1)

        # Execute query
        result = query.execute()

        return MaterialSearchResponse(
            materials=result.data,
            count=len(result.data),
            total_available=result.count or 0,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to search materials: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to search materials: {str(e)}")


@router.get("/categories", response_model=MaterialCategoryResponse)
def get_categories():
    """Get list of distinct material categories.

    Returns sorted list of all categories for approved materials.
    Categories are relatively few (~30 max) so no pagination is needed.
    """
    supabase = get_supabase()
    if supabase is None:
        raise HTTPException(
            status_code=503, detail="Database not configured"
        )

    try:
        # Query for distinct categories
        query = supabase.from_("materials").select("category")
        query = query.eq("item_type", "material")
        query = query.eq("review_status", "approved")
        query = query.not_.is_("category", "null")

        result = query.execute()

        # Extract unique categories and sort
        categories = list(set(row["category"] for row in result.data if row.get("category")))
        categories.sort()

        return MaterialCategoryResponse(
            categories=categories,
            count=len(categories),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get categories: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get categories: {str(e)}")
