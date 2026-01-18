"use client";

import { useState, useEffect, useCallback } from "react";
import Link from "next/link";
import { DataTable } from "@/components/review/data-table";
import { createColumns } from "@/components/review/columns";
import { FeedbackDialog } from "@/components/review/feedback-dialog";
import {
  fetchPendingEstimates,
  fetchEstimateDetail,
  submitFeedback,
} from "@/lib/feedback-api";
import type { PendingEstimate, EstimateDetail } from "@/types/feedback";
import { Button } from "@/components/ui/button";

/**
 * Review Queue page for Laurent to view and provide feedback on AI estimates
 */
export default function ReviewPage() {
  const [estimates, setEstimates] = useState<PendingEstimate[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedEstimate, setSelectedEstimate] = useState<EstimateDetail | null>(
    null
  );
  const [dialogOpen, setDialogOpen] = useState(false);
  const [detailLoading, setDetailLoading] = useState(false);

  // Fetch pending estimates
  const loadEstimates = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const data = await fetchPendingEstimates();
      setEstimates(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load estimates");
    } finally {
      setLoading(false);
    }
  }, []);

  // Load estimates on mount
  useEffect(() => {
    loadEstimates();
  }, [loadEstimates]);

  // Handle Review button click
  const handleReview = async (estimate: PendingEstimate) => {
    setDetailLoading(true);
    setError(null);

    try {
      const detail = await fetchEstimateDetail(estimate.id);
      setSelectedEstimate(detail);
      setDialogOpen(true);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to load estimate details"
      );
    } finally {
      setDetailLoading(false);
    }
  };

  // Handle feedback submission
  const handleSubmit = async (price: number) => {
    if (!selectedEstimate) return;

    await submitFeedback({
      estimate_id: selectedEstimate.id,
      laurent_price: price,
    });

    // Refresh list and close dialog
    await loadEstimates();
  };

  // Handle dialog close
  const handleDialogClose = (open: boolean) => {
    if (!open) {
      setSelectedEstimate(null);
    }
    setDialogOpen(open);
  };

  // Create columns with review callback
  const columns = createColumns(handleReview);

  return (
    <div className="flex min-h-screen items-start justify-center bg-zinc-50 font-sans dark:bg-black">
      <main className="container mx-auto max-w-4xl py-8 px-4">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-3xl font-bold tracking-tight text-black dark:text-zinc-50">
              Review Queue
            </h1>
            <p className="text-sm text-zinc-600 dark:text-zinc-400 mt-1">
              {loading
                ? "Loading..."
                : `${estimates.length} pending estimate${estimates.length !== 1 ? "s" : ""}`}
            </p>
          </div>
          <Link href="/">
            <Button variant="outline">Back to Estimator</Button>
          </Link>
        </div>

        {/* Error State */}
        {error && (
          <div className="mb-6 rounded-lg border border-destructive/50 bg-destructive/10 p-4">
            <p className="text-sm text-destructive">{error}</p>
            <Button
              variant="outline"
              size="sm"
              className="mt-2"
              onClick={loadEstimates}
            >
              Retry
            </Button>
          </div>
        )}

        {/* Loading State */}
        {loading && (
          <div className="flex items-center justify-center h-48 text-muted-foreground">
            Loading estimates...
          </div>
        )}

        {/* Detail Loading Overlay */}
        {detailLoading && (
          <div className="fixed inset-0 z-40 flex items-center justify-center bg-black/20">
            <div className="rounded-lg bg-background p-4 shadow-lg">
              Loading details...
            </div>
          </div>
        )}

        {/* Data Table */}
        {!loading && <DataTable columns={columns} data={estimates} />}

        {/* Feedback Dialog */}
        <FeedbackDialog
          estimate={selectedEstimate}
          open={dialogOpen}
          onOpenChange={handleDialogClose}
          onSubmit={handleSubmit}
        />
      </main>
    </div>
  );
}
