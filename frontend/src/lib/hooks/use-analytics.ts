"use client";

import { useQuery } from "@tanstack/react-query";
import { subDays, startOfDay } from "date-fns";
import {
  getAccuracyStats,
  getCategoryBreakdown,
  getConfidenceAccuracy,
} from "@/lib/supabase/analytics";
import type { TimePeriod } from "@/types/analytics";

/**
 * Calculate date range from time period.
 */
function getDateRange(period: TimePeriod): {
  start: Date | undefined;
  end: Date;
} {
  const end = new Date();

  switch (period) {
    case "7d":
      return { start: startOfDay(subDays(end, 7)), end };
    case "30d":
      return { start: startOfDay(subDays(end, 30)), end };
    case "all":
      return { start: undefined, end };
  }
}

/**
 * Hook for fetching accuracy statistics.
 * Returns counts and percentages for estimates within 10%/20% of actual price.
 */
export function useAccuracyStats(period: TimePeriod) {
  const { start, end } = getDateRange(period);

  return useQuery({
    queryKey: ["accuracy-stats", period],
    queryFn: () => getAccuracyStats(start, end),
    staleTime: 1000 * 60 * 5, // 5 minutes
  });
}

/**
 * Hook for fetching category breakdown.
 * Returns count and percentage for each estimate category.
 */
export function useCategoryBreakdown(period: TimePeriod) {
  const { start, end } = getDateRange(period);

  return useQuery({
    queryKey: ["category-breakdown", period],
    queryFn: () => getCategoryBreakdown(start, end),
    staleTime: 1000 * 60 * 5, // 5 minutes
  });
}

/**
 * Hook for fetching confidence vs accuracy correlation.
 * Returns accuracy metrics grouped by confidence level (HIGH, MEDIUM, LOW).
 */
export function useConfidenceAccuracy(period: TimePeriod) {
  const { start, end } = getDateRange(period);

  return useQuery({
    queryKey: ["confidence-accuracy", period],
    queryFn: () => getConfidenceAccuracy(start, end),
    staleTime: 1000 * 60 * 5, // 5 minutes
  });
}
