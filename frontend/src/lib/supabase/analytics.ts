import { getClient } from "./client";
import type {
  AccuracyStats,
  CategoryBreakdown,
  ConfidenceAccuracy,
} from "@/types/analytics";

// RPC function parameter and return types for Supabase
// These match the PostgreSQL function signatures in the database

interface RpcParams {
  start_date: string | null;
  end_date: string | null;
}

/**
 * Fetch overall accuracy statistics from Supabase RPC.
 * Returns counts and percentages for estimates within 10%/20% of actual price.
 */
export async function getAccuracyStats(
  startDate?: Date,
  endDate?: Date
): Promise<AccuracyStats> {
  const supabase = getClient();

  const params: RpcParams = {
    start_date: startDate?.toISOString() ?? null,
    end_date: endDate?.toISOString() ?? null,
  };

  const { data, error } = await supabase.rpc(
    "get_accuracy_stats",
    params as unknown as undefined
  );

  if (error) {
    throw new Error(`Failed to fetch accuracy stats: ${error.message}`);
  }

  // RPC returns array with single row
  const result = data as AccuracyStats[] | null;
  if (!result || result.length === 0) {
    return {
      total_estimates: 0,
      reviewed_count: 0,
      within_10_percent: 0,
      within_20_percent: 0,
      accuracy_10: 0,
      accuracy_20: 0,
    };
  }

  return result[0];
}

/**
 * Fetch category breakdown from Supabase RPC.
 * Returns count and percentage for each estimate category.
 */
export async function getCategoryBreakdown(
  startDate?: Date,
  endDate?: Date
): Promise<CategoryBreakdown[]> {
  const supabase = getClient();

  const params: RpcParams = {
    start_date: startDate?.toISOString() ?? null,
    end_date: endDate?.toISOString() ?? null,
  };

  const { data, error } = await supabase.rpc(
    "get_category_breakdown",
    params as unknown as undefined
  );

  if (error) {
    throw new Error(`Failed to fetch category breakdown: ${error.message}`);
  }

  return (data as CategoryBreakdown[] | null) ?? [];
}

/**
 * Fetch confidence vs accuracy correlation from Supabase RPC.
 * Returns accuracy metrics grouped by confidence level (HIGH, MEDIUM, LOW).
 */
export async function getConfidenceAccuracy(
  startDate?: Date,
  endDate?: Date
): Promise<ConfidenceAccuracy[]> {
  const supabase = getClient();

  const params: RpcParams = {
    start_date: startDate?.toISOString() ?? null,
    end_date: endDate?.toISOString() ?? null,
  };

  const { data, error } = await supabase.rpc(
    "get_confidence_accuracy",
    params as unknown as undefined
  );

  if (error) {
    throw new Error(`Failed to fetch confidence accuracy: ${error.message}`);
  }

  return (data as ConfidenceAccuracy[] | null) ?? [];
}
