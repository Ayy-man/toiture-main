/**
 * Time period filter for analytics queries.
 */
export type TimePeriod = "7d" | "30d" | "all";

/**
 * Overall accuracy statistics from get_accuracy_stats RPC.
 */
export interface AccuracyStats {
  total_estimates: number;
  reviewed_count: number;
  within_10_percent: number;
  within_20_percent: number;
  accuracy_10: number;
  accuracy_20: number;
}

/**
 * Category breakdown from get_category_breakdown RPC.
 */
export interface CategoryBreakdown {
  category: string;
  count: number;
  percentage: number;
}

/**
 * Confidence vs accuracy correlation from get_confidence_accuracy RPC.
 */
export interface ConfidenceAccuracy {
  confidence: string;
  total_count: number;
  reviewed_count: number;
  accuracy_10: number;
  accuracy_20: number;
}
