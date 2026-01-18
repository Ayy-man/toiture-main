"use client";

import { useQuery } from "@tanstack/react-query";
import {
  fetchDashboardMetrics,
  fetchDashboardCharts,
} from "@/lib/api/dashboard";

/**
 * Hook for fetching dashboard metrics (KPIs).
 */
export function useDashboardMetrics(startDate?: string, endDate?: string) {
  return useQuery({
    queryKey: ["dashboard", "metrics", startDate, endDate],
    queryFn: () => fetchDashboardMetrics(startDate, endDate),
    staleTime: 1000 * 60 * 5, // 5 minutes
  });
}

/**
 * Hook for fetching dashboard charts data.
 */
export function useDashboardCharts(startDate?: string, endDate?: string) {
  return useQuery({
    queryKey: ["dashboard", "charts", startDate, endDate],
    queryFn: () => fetchDashboardCharts(startDate, endDate),
    staleTime: 1000 * 60 * 5, // 5 minutes
  });
}
