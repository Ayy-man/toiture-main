"use client";

import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";
import type { MonthlyTrend } from "@/types/dashboard";

interface TrendChartProps {
  data: MonthlyTrend[] | undefined;
  isLoading: boolean;
}

/**
 * Format value as compact CAD currency.
 */
function formatCompactCurrency(value: number): string {
  return new Intl.NumberFormat("fr-CA", {
    style: "currency",
    currency: "CAD",
    notation: "compact",
    minimumFractionDigits: 0,
    maximumFractionDigits: 1,
  }).format(value);
}

/**
 * Custom tooltip for trend chart.
 */
function CustomTooltip({ active, payload, label }: {
  active?: boolean;
  payload?: Array<{ value: number; payload: MonthlyTrend }>;
  label?: string;
}) {
  if (!active || !payload?.length) {
    return null;
  }

  const data = payload[0].payload;

  return (
    <div className="rounded-lg border bg-background p-2 shadow-sm">
      <div className="font-medium">{label}</div>
      <div className="text-sm text-muted-foreground">
        {formatCompactCurrency(data.revenue)}
      </div>
      <div className="text-xs text-muted-foreground">
        {data.quote_count} soumission{data.quote_count > 1 ? "s" : ""}
      </div>
    </div>
  );
}

/**
 * Skeleton placeholder for loading state.
 */
function ChartSkeleton() {
  return (
    <div className="flex h-[300px] items-center justify-center">
      <div className="h-full w-full animate-pulse rounded bg-muted" />
    </div>
  );
}

export function TrendChart({ data, isLoading }: TrendChartProps) {
  if (isLoading) {
    return <ChartSkeleton />;
  }

  if (!data?.length) {
    return (
      <div className="flex h-[300px] items-center justify-center text-muted-foreground">
        Aucune donnee disponible
      </div>
    );
  }

  return (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={data} margin={{ top: 10, right: 10, left: 10, bottom: 10 }}>
        <XAxis
          dataKey="month"
          axisLine={false}
          tickLine={false}
          tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 12 }}
        />
        <YAxis
          axisLine={false}
          tickLine={false}
          tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 12 }}
          tickFormatter={formatCompactCurrency}
          width={80}
        />
        <Tooltip content={<CustomTooltip />} />
        <Line
          type="monotone"
          dataKey="revenue"
          stroke="#8B2323"
          strokeWidth={2}
          dot={{ fill: "#8B2323", strokeWidth: 0, r: 4 }}
          activeDot={{ fill: "#8B2323", strokeWidth: 0, r: 6 }}
        />
      </LineChart>
    </ResponsiveContainer>
  );
}
