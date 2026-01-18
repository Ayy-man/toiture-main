"use client";

import { useState } from "react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import type { EstimateDetail } from "@/types/feedback";

// Confidence badge colors matching estimate-result.tsx pattern
const confidenceColors = {
  HIGH: "text-green-600 bg-green-50",
  MEDIUM: "text-yellow-600 bg-yellow-50",
  LOW: "text-red-600 bg-red-50",
};

// CAD currency formatter
const currencyFormatter = new Intl.NumberFormat("en-CA", {
  style: "currency",
  currency: "CAD",
  minimumFractionDigits: 0,
  maximumFractionDigits: 0,
});

interface FeedbackDialogProps {
  estimate: EstimateDetail | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSubmit: (price: number) => Promise<void>;
}

/**
 * Dialog for reviewing estimate details and submitting Laurent's price
 */
export function FeedbackDialog({
  estimate,
  open,
  onOpenChange,
  onSubmit,
}: FeedbackDialogProps) {
  const [price, setPrice] = useState<string>("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async () => {
    const priceValue = parseFloat(price);
    if (isNaN(priceValue) || priceValue < 0) {
      setError("Please enter a valid price");
      return;
    }

    setIsSubmitting(true);
    setError(null);

    try {
      await onSubmit(priceValue);
      setPrice("");
      onOpenChange(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to submit");
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleClose = () => {
    setPrice("");
    setError(null);
    onOpenChange(false);
  };

  if (!estimate) return null;

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="max-w-lg max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Review Estimate</DialogTitle>
        </DialogHeader>

        <div className="space-y-4">
          {/* Estimate Details */}
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className="text-muted-foreground">Category:</span>
              <span className="ml-2 font-medium">{estimate.category}</span>
            </div>
            <div>
              <span className="text-muted-foreground">Sqft:</span>
              <span className="ml-2 font-medium">
                {estimate.sqft.toLocaleString()}
              </span>
            </div>
            <div>
              <span className="text-muted-foreground">Complexity:</span>
              <span className="ml-2 font-medium">{estimate.complexity}</span>
            </div>
            <div>
              <span className="text-muted-foreground">Material Lines:</span>
              <span className="ml-2 font-medium">{estimate.material_lines}</span>
            </div>
            <div>
              <span className="text-muted-foreground">Labor Lines:</span>
              <span className="ml-2 font-medium">{estimate.labor_lines}</span>
            </div>
            <div>
              <span className="text-muted-foreground">Has Subs:</span>
              <span className="ml-2 font-medium">
                {estimate.has_subs ? "Yes" : "No"}
              </span>
            </div>
          </div>

          {/* AI Estimate Section */}
          <div className="rounded-lg border p-4 space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-muted-foreground">AI Estimate:</span>
              <span className="text-xl font-bold">
                {currencyFormatter.format(estimate.ai_estimate)}
              </span>
            </div>
            <div className="flex items-center justify-between text-sm">
              <span className="text-muted-foreground">Range:</span>
              <span>
                {currencyFormatter.format(estimate.range_low)} -{" "}
                {currencyFormatter.format(estimate.range_high)}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-muted-foreground">Confidence:</span>
              <span
                className={`inline-flex items-center rounded-md px-2 py-1 text-xs font-medium ${confidenceColors[estimate.confidence]}`}
              >
                {estimate.confidence}
              </span>
            </div>
            <div className="text-xs text-muted-foreground">
              Model: {estimate.model}
            </div>
          </div>

          {/* Reasoning Section */}
          {estimate.reasoning && (
            <div className="space-y-2">
              <span className="text-sm font-medium">AI Reasoning:</span>
              <div className="max-h-40 overflow-y-auto rounded-lg border bg-muted/30 p-3 text-sm">
                {estimate.reasoning}
              </div>
            </div>
          )}

          {/* Price Input */}
          <div className="space-y-2">
            <label
              htmlFor="laurent-price"
              className="text-sm font-medium leading-none"
            >
              Your Price (CAD)
            </label>
            <Input
              id="laurent-price"
              type="number"
              min="0"
              step="100"
              placeholder="Enter your price"
              value={price}
              onChange={(e) => setPrice(e.target.value)}
            />
          </div>

          {/* Error Display */}
          {error && (
            <p className="text-sm font-medium text-destructive">{error}</p>
          )}
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={handleClose} disabled={isSubmitting}>
            Cancel
          </Button>
          <Button onClick={handleSubmit} disabled={isSubmitting || !price}>
            {isSubmitting ? "Submitting..." : "Submit Feedback"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
