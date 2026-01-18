"use client";

import { TrendingUp, TrendingDown, CheckCircle, FileText } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface StatsCardsProps {
  totalEstimates: number;
  reviewedCount: number;
  accuracy10: number;
  accuracy20: number;
}

export function StatsCards({
  totalEstimates,
  reviewedCount,
  accuracy10,
  accuracy20,
}: StatsCardsProps) {
  const pendingCount = totalEstimates - reviewedCount;

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Total Estimates</CardTitle>
          <FileText className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{totalEstimates}</div>
          <p className="text-xs text-muted-foreground">
            All time estimate count
          </p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Reviewed</CardTitle>
          <CheckCircle className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{reviewedCount}</div>
          <p className="text-xs text-muted-foreground">
            {pendingCount} pending review
          </p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Within 10%</CardTitle>
          {accuracy10 >= 50 ? (
            <TrendingUp className="h-4 w-4 text-green-500" />
          ) : (
            <TrendingDown className="h-4 w-4 text-red-500" />
          )}
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{accuracy10.toFixed(1)}%</div>
          <p className="text-xs text-muted-foreground">
            Estimates within 10% of actual
          </p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Within 20%</CardTitle>
          {accuracy20 >= 70 ? (
            <TrendingUp className="h-4 w-4 text-green-500" />
          ) : (
            <TrendingDown className="h-4 w-4 text-red-500" />
          )}
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{accuracy20.toFixed(1)}%</div>
          <p className="text-xs text-muted-foreground">
            Estimates within 20% of actual
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
