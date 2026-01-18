"""Customer search endpoints for admin dashboard Clients tab."""

import logging
from typing import List

from fastapi import APIRouter, HTTPException, Query

from app.schemas.customers import CustomerDetail, CustomerResult, QuoteHistoryItem
from app.services.supabase_client import get_supabase

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/customers", tags=["customers"])


def calculate_segment(lifetime_value: float) -> str:
    """Determine customer segment based on lifetime value."""
    if lifetime_value > 50000:
        return "VIP"
    elif lifetime_value > 10000:
        return "Regular"
    return "New"


@router.get("/search", response_model=List[CustomerResult])
def search_customers(
    q: str = Query(..., min_length=2, description="Search query for customer name"),
    limit: int = Query(default=10, ge=1, le=50, description="Maximum results to return"),
):
    """Search customers by name.

    Searches the estimates table by client_name and aggregates quote data
    to return customer information with lifetime value and segment.
    """
    supabase = get_supabase()
    if supabase is None:
        raise HTTPException(
            status_code=503, detail="Supabase not configured. Customer search unavailable."
        )

    try:
        # Query estimates table for matching client names
        # We need to aggregate by client_name to get customer-level data
        result = (
            supabase.table("estimates")
            .select("id, client_name, city, ai_estimate")
            .ilike("client_name", f"%{q}%")
            .order("created_at", desc=True)
            .execute()
        )

        # Aggregate by client_name to build customer results
        customers_map = {}
        for row in result.data:
            client_name = row.get("client_name")
            if not client_name:
                continue

            if client_name not in customers_map:
                customers_map[client_name] = {
                    "id": row["id"],  # Use first quote ID as customer ID
                    "name": client_name,
                    "city": row.get("city"),
                    "total_quotes": 0,
                    "lifetime_value": 0.0,
                }

            customers_map[client_name]["total_quotes"] += 1
            price = row.get("ai_estimate") or 0
            customers_map[client_name]["lifetime_value"] += price

        # Convert to CustomerResult list with segments
        results = []
        for customer in customers_map.values():
            customer["segment"] = calculate_segment(customer["lifetime_value"])
            results.append(CustomerResult(**customer))

        # Sort by lifetime_value descending and limit
        results.sort(key=lambda c: c.lifetime_value, reverse=True)
        return results[:limit]

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to search customers: {e}")
        raise HTTPException(status_code=500, detail="Failed to search customers")


@router.get("/{customer_id}", response_model=CustomerDetail)
def get_customer_detail(customer_id: str):
    """Get full customer details with quote history.

    The customer_id is actually the ID of one of their quotes.
    We look up the client_name from that quote and aggregate all their data.
    """
    supabase = get_supabase()
    if supabase is None:
        raise HTTPException(
            status_code=503, detail="Supabase not configured. Customer lookup unavailable."
        )

    try:
        # First get the quote to find the client_name
        quote_result = (
            supabase.table("estimates")
            .select("client_name, city")
            .eq("id", customer_id)
            .execute()
        )

        if not quote_result.data:
            raise HTTPException(status_code=404, detail=f"Customer {customer_id} not found")

        client_name = quote_result.data[0].get("client_name")
        if not client_name:
            raise HTTPException(
                status_code=404, detail=f"No client name found for {customer_id}"
            )

        city = quote_result.data[0].get("city")

        # Get all quotes for this client
        quotes_result = (
            supabase.table("estimates")
            .select("id, created_at, category, sqft, ai_estimate")
            .eq("client_name", client_name)
            .order("created_at", desc=True)
            .execute()
        )

        # Build quote history and calculate aggregates
        quotes = []
        total_quotes = 0
        lifetime_value = 0.0

        for row in quotes_result.data:
            quotes.append(QuoteHistoryItem(
                id=row["id"],
                created_at=row["created_at"],
                category=row.get("category"),
                sqft=row.get("sqft"),
                total_price=row.get("ai_estimate"),
            ))
            total_quotes += 1
            lifetime_value += row.get("ai_estimate") or 0

        return CustomerDetail(
            id=customer_id,
            name=client_name,
            city=city,
            phone=None,  # Not stored in estimates table
            email=None,  # Not stored in estimates table
            total_quotes=total_quotes,
            lifetime_value=lifetime_value,
            segment=calculate_segment(lifetime_value),
            quotes=quotes,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get customer {customer_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get customer details")
