"use client";

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import type { EstimateResponse } from "@/lib/api";

interface EstimateResultProps {
  result: EstimateResponse;
}

/**
 * Display the estimate result with amount, range, and confidence
 */
export function EstimateResult({ result }: EstimateResultProps) {
  const confidenceColors = {
    HIGH: "text-green-600",
    MEDIUM: "text-yellow-600",
    LOW: "text-red-600",
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Estimate</CardTitle>
        <CardDescription>
          ${result.range_low.toLocaleString()} - $
          {result.range_high.toLocaleString()}
        </CardDescription>
      </CardHeader>
      <CardContent>
        <p className="text-4xl font-bold">
          ${result.estimate.toLocaleString()}
        </p>
        <div className="mt-4 flex items-center gap-4">
          <span
            className={`text-sm font-medium ${confidenceColors[result.confidence]}`}
          >
            {result.confidence} Confidence
          </span>
          <span className="text-sm text-muted-foreground">
            Model: {result.model}
          </span>
        </div>
      </CardContent>
    </Card>
  );
}
