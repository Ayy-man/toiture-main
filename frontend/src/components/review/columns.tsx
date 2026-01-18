"use client";

import { ColumnDef } from "@tanstack/react-table";
import { Button } from "@/components/ui/button";
import type { PendingEstimate } from "@/types/feedback";

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

/**
 * Create column definitions for the pending estimates table
 *
 * @param onReview - Callback when Review button is clicked
 */
export function createColumns(
  onReview: (estimate: PendingEstimate) => void
): ColumnDef<PendingEstimate>[] {
  return [
    {
      accessorKey: "created_at",
      header: "Date",
      cell: ({ row }) => {
        const date = new Date(row.getValue("created_at"));
        return date.toLocaleDateString("en-CA");
      },
    },
    {
      accessorKey: "category",
      header: "Category",
    },
    {
      accessorKey: "sqft",
      header: "Sqft",
      cell: ({ row }) => {
        const sqft = row.getValue("sqft") as number;
        return sqft.toLocaleString();
      },
    },
    {
      accessorKey: "ai_estimate",
      header: "AI Estimate",
      cell: ({ row }) => {
        const estimate = row.getValue("ai_estimate") as number;
        return currencyFormatter.format(estimate);
      },
    },
    {
      accessorKey: "confidence",
      header: "Confidence",
      cell: ({ row }) => {
        const confidence = row.getValue("confidence") as
          | "HIGH"
          | "MEDIUM"
          | "LOW";
        return (
          <span
            className={`inline-flex items-center rounded-md px-2 py-1 text-xs font-medium ${confidenceColors[confidence]}`}
          >
            {confidence}
          </span>
        );
      },
    },
    {
      id: "actions",
      header: "",
      cell: ({ row }) => {
        return (
          <Button
            variant="outline"
            size="sm"
            onClick={() => onReview(row.original)}
          >
            Review
          </Button>
        );
      },
    },
  ];
}
