import type { DashboardMetrics, DashboardCharts, ComplianceReport } from "@/types/dashboard";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

/**
 * Fetch dashboard metrics (KPIs).
 */
export async function fetchDashboardMetrics(
  startDate?: string,
  endDate?: string
): Promise<DashboardMetrics> {
  const params = new URLSearchParams();
  if (startDate) params.set("start_date", startDate);
  if (endDate) params.set("end_date", endDate);

  const url = params.toString()
    ? `${API_URL}/dashboard/metrics?${params}`
    : `${API_URL}/dashboard/metrics`;

  const response = await fetch(url);
  if (!response.ok) {
    throw new Error("Failed to fetch dashboard metrics");
  }
  return response.json();
}

/**
 * Fetch dashboard charts data.
 */
export async function fetchDashboardCharts(
  startDate?: string,
  endDate?: string
): Promise<DashboardCharts> {
  const params = new URLSearchParams();
  if (startDate) params.set("start_date", startDate);
  if (endDate) params.set("end_date", endDate);

  const url = params.toString()
    ? `${API_URL}/dashboard/charts?${params}`
    : `${API_URL}/dashboard/charts`;

  const response = await fetch(url);
  if (!response.ok) {
    throw new Error("Failed to fetch dashboard charts");
  }
  return response.json();
}

/**
 * Fetch compliance report (sqft data quality).
 */
export async function fetchComplianceReport(
  days: number = 30
): Promise<ComplianceReport> {
  const url = `${API_URL}/dashboard/compliance?days=${days}`;

  const response = await fetch(url);
  if (!response.ok) {
    throw new Error("Failed to fetch compliance report");
  }
  return response.json();
}
