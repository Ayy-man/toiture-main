"""Pydantic models for dashboard metrics and charts."""

from typing import List, Optional

from pydantic import BaseModel


class DashboardMetrics(BaseModel):
    """Key performance indicators for the dashboard overview."""

    total_revenue: float
    total_quotes: int
    average_margin: float
    active_clients: int
    period_start: Optional[str] = None
    period_end: Optional[str] = None


class RevenueByYear(BaseModel):
    """Revenue breakdown by year."""

    year: int
    revenue: float
    quote_count: int


class RevenueByCategory(BaseModel):
    """Revenue breakdown by category."""

    category: str
    revenue: float
    quote_count: int
    percentage: float


class MonthlyTrend(BaseModel):
    """Monthly revenue trend data point."""

    month: str  # "2024-01" format
    revenue: float
    quote_count: int


class TopClient(BaseModel):
    """Top client by total spending."""

    name: str
    total_spent: float
    quote_count: int


class DashboardCharts(BaseModel):
    """Aggregated chart data for dashboard visualizations."""

    revenue_by_year: List[RevenueByYear]
    revenue_by_category: List[RevenueByCategory]
    monthly_trend: List[MonthlyTrend]
    top_clients: List[TopClient]
