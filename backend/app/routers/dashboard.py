"""Dashboard metrics and charts endpoints for admin dashboard Apercu tab."""

import logging
from collections import defaultdict
from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from app.schemas.dashboard import (
    DashboardCharts,
    DashboardMetrics,
    MonthlyTrend,
    RevenueByCategory,
    RevenueByYear,
    TopClient,
)
from app.services.supabase_client import get_supabase

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/metrics", response_model=DashboardMetrics)
def get_dashboard_metrics(
    start_date: Optional[str] = Query(default=None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(default=None, description="End date (YYYY-MM-DD)"),
):
    """Get key performance indicators for the dashboard.

    Returns total revenue, quote count, average margin, and active clients
    with optional date filtering.
    """
    supabase = get_supabase()
    if supabase is None:
        raise HTTPException(
            status_code=503, detail="Supabase not configured. Dashboard unavailable."
        )

    try:
        # Build query with date filters
        # Note: Only select columns that exist in the estimates table
        query = supabase.table("estimates").select(
            "ai_estimate, category, created_at"
        )

        if start_date:
            query = query.gte("created_at", start_date)
        if end_date:
            query = query.lte("created_at", f"{end_date}T23:59:59")

        result = query.execute()

        # Calculate aggregates
        total_revenue = 0.0
        total_quotes = 0
        categories_seen = set()

        for row in result.data:
            total_quotes += 1
            total_revenue += row.get("ai_estimate") or 0

            # Track unique categories as proxy for activity
            category = row.get("category")
            if category:
                categories_seen.add(category)

        # Note: margin_percent and client_name columns don't exist in current schema
        # Setting defaults until those features are added
        average_margin = 0.0
        active_clients = len(categories_seen)  # Use categories as proxy

        return DashboardMetrics(
            total_revenue=total_revenue,
            total_quotes=total_quotes,
            average_margin=average_margin,
            active_clients=active_clients,
            period_start=start_date,
            period_end=end_date,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch dashboard metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch dashboard metrics")


@router.get("/charts", response_model=DashboardCharts)
def get_dashboard_charts(
    start_date: Optional[str] = Query(default=None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(default=None, description="End date (YYYY-MM-DD)"),
):
    """Get chart data for dashboard visualizations.

    Returns revenue by year, revenue by category, monthly trends,
    and top clients with optional date filtering.
    """
    supabase = get_supabase()
    if supabase is None:
        raise HTTPException(
            status_code=503, detail="Supabase not configured. Dashboard unavailable."
        )

    try:
        # Build query with date filters
        # Note: Only select columns that exist in the estimates table
        query = supabase.table("estimates").select(
            "created_at, category, ai_estimate"
        )

        if start_date:
            query = query.gte("created_at", start_date)
        if end_date:
            query = query.lte("created_at", f"{end_date}T23:59:59")

        result = query.execute()

        # Aggregate data for all chart types
        revenue_by_year = defaultdict(lambda: {"revenue": 0.0, "quote_count": 0})
        revenue_by_category = defaultdict(lambda: {"revenue": 0.0, "quote_count": 0})
        monthly_trend = defaultdict(lambda: {"revenue": 0.0, "quote_count": 0})
        total_revenue = 0.0

        for row in result.data:
            price = row.get("ai_estimate") or 0
            total_revenue += price

            # Extract year and month from created_at
            created_at = row.get("created_at", "")
            if created_at:
                # Handle both datetime formats: "2024-01-15T10:30:00" or "2024-01-15"
                date_part = created_at[:10] if len(created_at) >= 10 else created_at
                parts = date_part.split("-")
                if len(parts) >= 2:
                    year = int(parts[0])
                    month = f"{parts[0]}-{parts[1]}"

                    revenue_by_year[year]["revenue"] += price
                    revenue_by_year[year]["quote_count"] += 1

                    monthly_trend[month]["revenue"] += price
                    monthly_trend[month]["quote_count"] += 1

            # Category aggregation
            category = row.get("category") or "Unknown"
            revenue_by_category[category]["revenue"] += price
            revenue_by_category[category]["quote_count"] += 1

        # Build response objects
        revenue_by_year_list = [
            RevenueByYear(year=year, revenue=data["revenue"], quote_count=data["quote_count"])
            for year, data in sorted(revenue_by_year.items())
        ]

        revenue_by_category_list = [
            RevenueByCategory(
                category=cat,
                revenue=data["revenue"],
                quote_count=data["quote_count"],
                percentage=(data["revenue"] / total_revenue * 100) if total_revenue > 0 else 0,
            )
            for cat, data in sorted(
                revenue_by_category.items(), key=lambda x: x[1]["revenue"], reverse=True
            )
        ]

        monthly_trend_list = [
            MonthlyTrend(month=month, revenue=data["revenue"], quote_count=data["quote_count"])
            for month, data in sorted(monthly_trend.items())
        ]

        # Note: client_name column doesn't exist in current schema
        # Top clients feature disabled until that column is added
        top_clients_list = []

        return DashboardCharts(
            revenue_by_year=revenue_by_year_list,
            revenue_by_category=revenue_by_category_list,
            monthly_trend=monthly_trend_list,
            top_clients=top_clients_list,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch dashboard charts: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch dashboard charts")
