"use client";

import { useState } from "react";
import { Loader2 } from "lucide-react";
import { AccuracyChart } from "./accuracy-chart";
import { ConfidenceChart } from "./confidence-chart";
import { CategoryBreakdown } from "./category-breakdown";
import { StatsCards } from "./stats-cards";
import { TimeFilter } from "./time-filter";
import {
  useAccuracyStats,
  useCategoryBreakdown,
  useConfidenceAccuracy,
} from "@/lib/hooks/use-analytics";
import type { TimePeriod } from "@/types/analytics";

export function DashboardContent() {
  const [period, setPeriod] = useState<TimePeriod>("30d");

  const accuracyQuery = useAccuracyStats(period);
  const categoryQuery = useCategoryBreakdown(period);
  const confidenceQuery = useConfidenceAccuracy(period);

  const isLoading =
    accuracyQuery.isLoading ||
    categoryQuery.isLoading ||
    confidenceQuery.isLoading;

  const hasError =
    accuracyQuery.isError || categoryQuery.isError || confidenceQuery.isError;

  if (hasError) {
    return (
      <div className="space-y-6">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">
              Analytics Dashboard
            </h1>
            <p className="text-muted-foreground">
              Track AI estimate accuracy and performance
            </p>
          </div>
          <TimeFilter value={period} onChange={setPeriod} />
        </div>
        <div className="rounded-lg border border-destructive/50 bg-destructive/10 p-6 text-center">
          <p className="text-destructive">
            Failed to load analytics data. Please check your Supabase
            configuration.
          </p>
        </div>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">
              Analytics Dashboard
            </h1>
            <p className="text-muted-foreground">
              Track AI estimate accuracy and performance
            </p>
          </div>
          <TimeFilter value={period} onChange={setPeriod} />
        </div>
        <div className="flex min-h-[400px] items-center justify-center">
          <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
        </div>
      </div>
    );
  }

  // Extract data with defaults
  const accuracy = accuracyQuery.data ?? {
    total_estimates: 0,
    reviewed_count: 0,
    within_10_percent: 0,
    within_20_percent: 0,
    accuracy_10: 0,
    accuracy_20: 0,
  };

  const categories = categoryQuery.data ?? [];
  const confidence = confidenceQuery.data ?? [];

  return (
    <div className="space-y-6">
      {/* Header with title and time filter */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">
            Analytics Dashboard
          </h1>
          <p className="text-muted-foreground">
            Track AI estimate accuracy and performance
          </p>
        </div>
        <TimeFilter value={period} onChange={setPeriod} />
      </div>

      {/* Stats cards row */}
      <StatsCards
        totalEstimates={accuracy.total_estimates}
        reviewedCount={accuracy.reviewed_count}
        accuracy10={accuracy.accuracy_10}
        accuracy20={accuracy.accuracy_20}
      />

      {/* Charts grid */}
      <div className="grid gap-6 lg:grid-cols-2">
        <AccuracyChart
          accuracy10={accuracy.accuracy_10}
          accuracy20={accuracy.accuracy_20}
          totalReviewed={accuracy.reviewed_count}
        />
        <ConfidenceChart data={confidence} />
      </div>

      {/* Category breakdown full width */}
      <CategoryBreakdown data={categories} />
    </div>
  );
}
