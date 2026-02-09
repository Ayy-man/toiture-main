"use client";

import { Bar, BarChart, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";
import type { RevenueByYear } from "@/types/dashboard";

interface RevenueChartProps {
  data: RevenueByYear[] | undefined;
  isLoading: boolean;
}

/**
 * Format value as compact CAD currency (e.g., 1.5M).
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
 * Custom tooltip for revenue chart.
 */
function CustomTooltip({ active, payload, label }: {
  active?: boolean;
  payload?: Array<{ value: number }>;
  label?: string | number;
}) {
  if (!active || !payload?.length) {
    return null;
  }

  return (
    <div
      style={{
        backgroundColor: "hsl(var(--popover))",
        borderColor: "hsl(var(--border))",
        color: "hsl(var(--popover-foreground))",
      }}
      className="rounded-lg border p-2 shadow-sm"
    >
      <div className="font-medium">{label}</div>
      <div className="text-sm text-muted-foreground">
        {formatCompactCurrency(payload[0].value)}
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

export function RevenueChart({ data, isLoading }: RevenueChartProps) {
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
      <BarChart data={data} margin={{ top: 10, right: 10, left: 10, bottom: 10 }}>
        <XAxis
          dataKey="year"
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
        <Bar
          dataKey="revenue"
          fill="hsl(var(--chart-1))"
          radius={[4, 4, 0, 0]}
        />
      </BarChart>
    </ResponsiveContainer>
  );
}
