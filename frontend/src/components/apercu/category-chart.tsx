"use client";

import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, Legend } from "recharts";
import type { RevenueByCategory } from "@/types/dashboard";

interface CategoryChartProps {
  data: RevenueByCategory[] | undefined;
  isLoading: boolean;
}

// Color palette using CSS variables for dark mode compatibility
const COLORS = [
  "hsl(var(--chart-1))", // brick red primary
  "hsl(var(--chart-2))", // teal
  "hsl(var(--chart-3))", // blue
  "hsl(var(--chart-4))", // yellow
  "hsl(var(--chart-5))", // orange
];

/**
 * Format value as CAD currency.
 */
function formatCurrency(value: number): string {
  return new Intl.NumberFormat("fr-CA", {
    style: "currency",
    currency: "CAD",
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(value);
}

/**
 * Custom tooltip for category chart.
 */
function CustomTooltip({ active, payload }: {
  active?: boolean;
  payload?: Array<{ name: string; value: number; payload: RevenueByCategory }>;
}) {
  if (!active || !payload?.length) {
    return null;
  }

  const data = payload[0].payload;

  return (
    <div
      style={{
        backgroundColor: "hsl(var(--popover))",
        borderColor: "hsl(var(--border))",
        color: "hsl(var(--popover-foreground))",
      }}
      className="rounded-lg border p-2 shadow-sm"
    >
      <div className="font-medium">{data.category}</div>
      <div className="text-sm text-muted-foreground">
        {formatCurrency(data.revenue)} ({data.percentage.toFixed(1)}%)
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
      <div className="h-48 w-48 animate-pulse rounded-full bg-muted" />
    </div>
  );
}

export function CategoryChart({ data, isLoading }: CategoryChartProps) {
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
      <PieChart>
        <Pie
          data={data}
          dataKey="revenue"
          nameKey="category"
          cx="50%"
          cy="50%"
          outerRadius={80}
          label={({ category, percentage }) =>
            `${category} (${percentage.toFixed(0)}%)`
          }
          labelLine={{ stroke: "hsl(var(--muted-foreground))" }}
        >
          {data.map((_, index) => (
            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
          ))}
        </Pie>
        <Tooltip content={<CustomTooltip />} />
        <Legend
          verticalAlign="bottom"
          height={36}
          formatter={(value) => (
            <span className="text-sm text-foreground">{value}</span>
          )}
        />
      </PieChart>
    </ResponsiveContainer>
  );
}
