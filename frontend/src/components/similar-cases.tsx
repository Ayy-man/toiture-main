"use client";

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import type { SimilarCase } from "@/lib/api";

interface SimilarCasesProps {
  cases: SimilarCase[];
}

/**
 * Display a list of similar historical cases from CBR
 */
export function SimilarCases({ cases }: SimilarCasesProps) {
  if (cases.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Similar Cases</CardTitle>
          <CardDescription>Historical jobs for comparison</CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">
            No similar cases found.
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Similar Cases</CardTitle>
        <CardDescription>Historical jobs for comparison</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {cases.map((caseItem, index) => (
            <div
              key={caseItem.case_id}
              className={index < cases.length - 1 ? "border-b pb-4" : ""}
            >
              <div className="flex items-center justify-between">
                <span className="font-medium">
                  {caseItem.category || "Unknown"} ({caseItem.year || "N/A"})
                </span>
                <span className="text-sm font-medium text-primary">
                  {(caseItem.similarity * 100).toFixed(0)}% match
                </span>
              </div>
              <div className="mt-1 grid grid-cols-2 gap-2 text-sm text-muted-foreground">
                <span>{caseItem.sqft?.toLocaleString() || "N/A"} sqft</span>
                <span className="text-right">
                  ${caseItem.total?.toLocaleString() || "N/A"} total
                </span>
                <span className="col-span-2 text-right">
                  ${caseItem.per_sqft?.toFixed(2) || "N/A"}/sqft
                </span>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
