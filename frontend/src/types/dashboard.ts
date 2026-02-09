/**
 * Dashboard metrics summary (KPI cards).
 */
export interface DashboardMetrics {
  total_revenue: number;
  total_quotes: number;
  average_margin: number;
  active_clients: number;
  period_start: string | null;
  period_end: string | null;
}

/**
 * Revenue aggregated by year.
 */
export interface RevenueByYear {
  year: number;
  revenue: number;
  quote_count: number;
}

/**
 * Revenue aggregated by category.
 */
export interface RevenueByCategory {
  category: string;
  revenue: number;
  quote_count: number;
  percentage: number;
}

/**
 * Monthly revenue trend data.
 */
export interface MonthlyTrend {
  month: string;
  revenue: number;
  quote_count: number;
}

/**
 * Top client by total spending.
 */
export interface TopClient {
  name: string;
  total_spent: number;
  quote_count: number;
}

/**
 * Dashboard charts data.
 */
export interface DashboardCharts {
  revenue_by_year: RevenueByYear[];
  revenue_by_category: RevenueByCategory[];
  monthly_trend: MonthlyTrend[];
  top_clients: TopClient[];
}

/**
 * Estimator compliance data (per-estimator breakdown).
 */
export interface EstimatorCompliance {
  name: string;
  total_estimates: number;
  sqft_completed: number;
  completion_rate: number;
}

/**
 * Compliance report (overall sqft data quality).
 */
export interface ComplianceReport {
  overall_completion_rate: number;
  estimators: EstimatorCompliance[];
  alert: boolean;
  total_estimates: number;
  total_with_sqft: number;
}
