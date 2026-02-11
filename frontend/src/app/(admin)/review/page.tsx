"use client";

import { useState, useEffect, useCallback } from "react";
import { DataTable } from "@/components/review/data-table";
import { createColumns } from "@/components/review/columns";
import { FeedbackDialog } from "@/components/review/feedback-dialog";
import {
  fetchPendingEstimates,
  fetchEstimateDetail,
  submitFeedback,
} from "@/lib/feedback-api";
import type { PendingEstimate, EstimateDetail } from "@/types/feedback";

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
    <div className="max-w-4xl">
      {/* Error State */}
      {error && (
        <div className="mb-6 rounded-lg border border-destructive/50 bg-destructive/10 p-4">
          <p className="text-sm text-destructive">{error}</p>
          <button
            className="mt-2 text-sm underline"
            onClick={loadEstimates}
          >
            Retry
          </button>
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
    </div>
  );
}
