# Phase 6: Analytics Dashboard - Research

**Researched:** 2026-01-18
**Domain:** React charting (Recharts/shadcn), Supabase analytics queries, dashboard patterns
**Confidence:** HIGH

## Summary

This phase builds an analytics dashboard for the TOITURELV Cortex system, displaying accuracy metrics, confidence trends, and category breakdowns. The frontend already uses Next.js 14+ with shadcn/ui (Phase 4), and Supabase stores feedback data (Phase 5 dependency).

The standard approach uses **shadcn/ui Charts** (built on Recharts) for all visualizations, with Supabase PostgreSQL functions (RPC) for aggregate queries. shadcn/ui provides 53 pre-built chart components that integrate seamlessly with the existing Tailwind/shadcn stack and support dark mode automatically.

**Primary recommendation:** Use shadcn/ui's native Chart components (Recharts under the hood) with PostgreSQL RPC functions for aggregations. Avoid client-side calculations for metrics - compute accuracy percentages in the database.

## Standard Stack

The established libraries for this analytics dashboard:

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| recharts | >=2.12.0 | Charting engine | Used by shadcn/ui charts, D3-based, React-native |
| @/components/ui/chart | N/A | shadcn chart wrappers | ChartContainer, ChartTooltip, ChartLegend - themed to match app |
| @supabase/supabase-js | >=2.39.0 | Database client | Already configured in Phase 5 |
| @tanstack/react-query | >=5.0.0 | Data fetching/caching | Recommended for Supabase dashboards, handles refetching |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| date-fns | >=3.0.0 | Date manipulation | Time period calculations (7d, 30d ago) |
| @supabase-cache-helpers/postgrest-react-query | >=1.0.0 | Supabase + React Query bridge | Optional: simplifies query key management |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Recharts (shadcn) | Tremor | Tremor is heavier, uses Recharts anyway, adds another dependency |
| Recharts (shadcn) | Chart.js | Smaller but only 6 chart types, less React-native |
| React Query | SWR | React Query has better devtools, mutation handling |
| PostgreSQL RPC | Client-side aggregation | RPC is faster, reduces data transfer, handles scale |

**Installation:**
```bash
cd frontend
pnpm add recharts date-fns @tanstack/react-query
pnpm dlx shadcn@latest add chart tabs toggle-group card
```

Note: Recharts may already be installed if shadcn chart was added previously. Check `package.json`.

## Architecture Patterns

### Recommended Project Structure

```
frontend/src/
├── app/
│   └── dashboard/
│       └── page.tsx          # Dashboard page (server component shell)
├── components/
│   └── dashboard/
│       ├── accuracy-chart.tsx      # DASH-01: % within 10%/20%
│       ├── confidence-chart.tsx    # DASH-02: confidence vs accuracy
│       ├── category-breakdown.tsx  # DASH-03: pie/bar by category
│       ├── stats-cards.tsx         # DASH-04: KPI cards
│       ├── time-filter.tsx         # Period selector component
│       └── dashboard-content.tsx   # Client component wrapper
├── lib/
│   ├── supabase/
│   │   └── analytics.ts      # RPC function calls
│   └── hooks/
│       └── use-analytics.ts  # React Query hooks for dashboard
└── types/
    └── analytics.ts          # TypeScript types for metrics
```

### Pattern 1: shadcn/ui Chart with ChartContainer

**What:** Use ChartContainer wrapper with ChartConfig for consistent theming
**When to use:** All charts in the dashboard
**Source:** [shadcn/ui Charts Documentation](https://ui.shadcn.com/docs/components/chart)

```typescript
"use client"

import { Bar, BarChart, CartesianGrid, XAxis, YAxis } from "recharts"
import {
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
  ChartLegend,
  ChartLegendContent,
  type ChartConfig,
} from "@/components/ui/chart"

const chartConfig = {
  within10: {
    label: "Within 10%",
    color: "hsl(var(--chart-1))",  // Uses CSS variables
  },
  within20: {
    label: "Within 20%",
    color: "hsl(var(--chart-2))",
  },
} satisfies ChartConfig

interface AccuracyData {
  period: string
  within10: number
  within20: number
}

export function AccuracyChart({ data }: { data: AccuracyData[] }) {
  return (
    <ChartContainer config={chartConfig} className="min-h-[300px] w-full">
      <BarChart accessibilityLayer data={data}>
        <CartesianGrid vertical={false} />
        <XAxis dataKey="period" tickLine={false} axisLine={false} />
        <YAxis tickFormatter={(value) => `${value}%`} />
        <ChartTooltip content={<ChartTooltipContent />} />
        <ChartLegend content={<ChartLegendContent />} />
        <Bar dataKey="within10" fill="var(--color-within10)" radius={4} />
        <Bar dataKey="within20" fill="var(--color-within20)" radius={4} />
      </BarChart>
    </ChartContainer>
  )
}
```

### Pattern 2: Supabase RPC for Aggregate Queries

**What:** Create PostgreSQL functions for complex analytics, call via RPC
**When to use:** Any aggregation with GROUP BY, date filtering, or percentage calculations
**Source:** [Supabase RPC Documentation](https://supabase.com/docs/reference/javascript/rpc)

```sql
-- Create in Supabase SQL Editor (Phase 5 or 6)
CREATE OR REPLACE FUNCTION get_accuracy_stats(
  start_date TIMESTAMPTZ DEFAULT NULL,
  end_date TIMESTAMPTZ DEFAULT NULL
)
RETURNS TABLE (
  total_estimates BIGINT,
  reviewed_count BIGINT,
  within_10_percent BIGINT,
  within_20_percent BIGINT,
  accuracy_10 DECIMAL,
  accuracy_20 DECIMAL
) AS $$
BEGIN
  RETURN QUERY
  SELECT
    COUNT(*)::BIGINT AS total_estimates,
    COUNT(CASE WHEN laurent_price IS NOT NULL THEN 1 END)::BIGINT AS reviewed_count,
    COUNT(CASE WHEN laurent_price IS NOT NULL
      AND ABS(ai_estimate - laurent_price) / laurent_price <= 0.10 THEN 1 END)::BIGINT AS within_10_percent,
    COUNT(CASE WHEN laurent_price IS NOT NULL
      AND ABS(ai_estimate - laurent_price) / laurent_price <= 0.20 THEN 1 END)::BIGINT AS within_20_percent,
    ROUND(
      COUNT(CASE WHEN laurent_price IS NOT NULL
        AND ABS(ai_estimate - laurent_price) / laurent_price <= 0.10 THEN 1 END)::DECIMAL
      / NULLIF(COUNT(CASE WHEN laurent_price IS NOT NULL THEN 1 END), 0) * 100, 1
    ) AS accuracy_10,
    ROUND(
      COUNT(CASE WHEN laurent_price IS NOT NULL
        AND ABS(ai_estimate - laurent_price) / laurent_price <= 0.20 THEN 1 END)::DECIMAL
      / NULLIF(COUNT(CASE WHEN laurent_price IS NOT NULL THEN 1 END), 0) * 100, 1
    ) AS accuracy_20
  FROM estimates
  WHERE
    (start_date IS NULL OR created_at >= start_date)
    AND (end_date IS NULL OR created_at <= end_date);
END;
$$ LANGUAGE plpgsql;
```

```typescript
// frontend/src/lib/supabase/analytics.ts
import { createClient } from "@/lib/supabase/client"

export interface AccuracyStats {
  total_estimates: number
  reviewed_count: number
  within_10_percent: number
  within_20_percent: number
  accuracy_10: number
  accuracy_20: number
}

export async function getAccuracyStats(
  startDate?: Date,
  endDate?: Date
): Promise<AccuracyStats> {
  const supabase = createClient()

  const { data, error } = await supabase.rpc("get_accuracy_stats", {
    start_date: startDate?.toISOString() ?? null,
    end_date: endDate?.toISOString() ?? null,
  })

  if (error) throw error
  return data[0]
}
```

### Pattern 3: React Query for Dashboard Data

**What:** Use React Query hooks for data fetching with automatic caching/refetching
**When to use:** All dashboard data fetching
**Source:** [React Query with Supabase](https://supabase.com/blog/react-query-nextjs-app-router-cache-helpers)

```typescript
// frontend/src/lib/hooks/use-analytics.ts
"use client"

import { useQuery } from "@tanstack/react-query"
import { getAccuracyStats, getCategoryBreakdown, getConfidenceTrend } from "@/lib/supabase/analytics"
import { subDays, startOfDay } from "date-fns"

export type TimePeriod = "7d" | "30d" | "all"

function getDateRange(period: TimePeriod): { start: Date | undefined; end: Date } {
  const end = new Date()
  switch (period) {
    case "7d":
      return { start: startOfDay(subDays(end, 7)), end }
    case "30d":
      return { start: startOfDay(subDays(end, 30)), end }
    case "all":
      return { start: undefined, end }
  }
}

export function useAccuracyStats(period: TimePeriod) {
  const { start, end } = getDateRange(period)

  return useQuery({
    queryKey: ["accuracy-stats", period],
    queryFn: () => getAccuracyStats(start, end),
    staleTime: 1000 * 60 * 5, // 5 minutes
    refetchOnWindowFocus: true,
  })
}

export function useCategoryBreakdown(period: TimePeriod) {
  const { start, end } = getDateRange(period)

  return useQuery({
    queryKey: ["category-breakdown", period],
    queryFn: () => getCategoryBreakdown(start, end),
    staleTime: 1000 * 60 * 5,
  })
}
```

### Pattern 4: Time Period Filter with Toggle Group

**What:** Use shadcn Toggle Group for quick period selection
**When to use:** Dashboard time filtering (DASH-04)
**Source:** [shadcn/ui Toggle Group](https://ui.shadcn.com/docs/components/toggle-group)

```typescript
"use client"

import { ToggleGroup, ToggleGroupItem } from "@/components/ui/toggle-group"

interface TimeFilterProps {
  value: "7d" | "30d" | "all"
  onChange: (value: "7d" | "30d" | "all") => void
}

export function TimeFilter({ value, onChange }: TimeFilterProps) {
  return (
    <ToggleGroup
      type="single"
      value={value}
      onValueChange={(v) => v && onChange(v as "7d" | "30d" | "all")}
      className="justify-start"
    >
      <ToggleGroupItem value="7d" aria-label="Last 7 days">
        7 Days
      </ToggleGroupItem>
      <ToggleGroupItem value="30d" aria-label="Last 30 days">
        30 Days
      </ToggleGroupItem>
      <ToggleGroupItem value="all" aria-label="All time">
        All Time
      </ToggleGroupItem>
    </ToggleGroup>
  )
}
```

### Pattern 5: Pie/Donut Chart for Category Breakdown

**What:** Use PieChart with custom labels for percentage display
**When to use:** DASH-03 category breakdown
**Source:** [Recharts PieChart](https://recharts.github.io/en-US/examples/PieChartWithCustomizedLabel/)

```typescript
"use client"

import { PieChart, Pie, Cell, ResponsiveContainer } from "recharts"
import {
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
  ChartLegend,
  ChartLegendContent,
  type ChartConfig,
} from "@/components/ui/chart"

interface CategoryData {
  category: string
  count: number
  percentage: number
}

const CATEGORY_COLORS: Record<string, string> = {
  "Bardeaux": "hsl(var(--chart-1))",
  "Elastomere": "hsl(var(--chart-2))",
  "Other": "hsl(var(--chart-3))",
  "Service Call": "hsl(var(--chart-4))",
  "Gutters": "hsl(var(--chart-5))",
}

export function CategoryBreakdown({ data }: { data: CategoryData[] }) {
  const chartConfig = data.reduce((acc, item) => {
    acc[item.category] = {
      label: item.category,
      color: CATEGORY_COLORS[item.category] || "hsl(var(--chart-1))",
    }
    return acc
  }, {} as ChartConfig)

  return (
    <ChartContainer config={chartConfig} className="min-h-[300px] w-full">
      <PieChart>
        <Pie
          data={data}
          dataKey="count"
          nameKey="category"
          cx="50%"
          cy="50%"
          innerRadius={60}
          outerRadius={100}
          label={({ category, percentage }) => `${percentage}%`}
        >
          {data.map((entry) => (
            <Cell
              key={entry.category}
              fill={CATEGORY_COLORS[entry.category] || "hsl(var(--chart-1))"}
            />
          ))}
        </Pie>
        <ChartTooltip content={<ChartTooltipContent />} />
        <ChartLegend content={<ChartLegendContent />} />
      </PieChart>
    </ChartContainer>
  )
}
```

### Anti-Patterns to Avoid

- **Client-side aggregation:** Don't fetch raw data and calculate percentages in React. Use database functions.
- **Missing ResponsiveContainer/min-height:** Charts won't render without a defined container height.
- **Hardcoded colors:** Use CSS variables (`var(--chart-N)`) for automatic dark mode support.
- **Fetching on every render:** Use React Query with appropriate staleTime to prevent excessive API calls.
- **Not handling empty data:** Charts throw errors with empty arrays. Always check and show empty states.

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Chart theming | Custom CSS for charts | shadcn ChartConfig + CSS vars | Automatic dark mode, consistent with UI |
| Date period calculations | Manual date math | date-fns subDays/startOfDay | Edge cases with timezones, DST |
| Data caching | useState + useEffect | React Query useQuery | Handles stale data, refetching, loading states |
| Percentage calculations | JavaScript in component | PostgreSQL CASE WHEN | More accurate, handles nulls, faster at scale |
| Responsive charts | Fixed dimensions | ResponsiveContainer or responsive prop | Charts adapt to container |
| Tooltip formatting | Custom tooltip component | ChartTooltipContent with formatters | Consistent with shadcn styling |

**Key insight:** shadcn/ui Charts deliberately don't abstract Recharts away - this means you get full Recharts power while maintaining shadcn theming. Don't fight this by building custom wrappers.

## Common Pitfalls

### Pitfall 1: Charts Not Rendering (No Height)

**What goes wrong:** Chart area appears empty or collapsed
**Why it happens:** Recharts requires explicit height on container
**How to avoid:** Always add `min-h-[Xpx]` class to ChartContainer
**Warning signs:** Empty space where chart should be, no console errors

```typescript
// WRONG - no height
<ChartContainer config={config}>
  <BarChart data={data}>...</BarChart>
</ChartContainer>

// CORRECT - explicit height
<ChartContainer config={config} className="min-h-[300px] w-full">
  <BarChart data={data}>...</BarChart>
</ChartContainer>
```

### Pitfall 2: ChartConfig Type Errors

**What goes wrong:** TypeScript errors about ChartConfig type
**Why it happens:** Dynamic config doesn't match ChartConfig type
**How to avoid:** Use `satisfies ChartConfig` for static configs, type assertion for dynamic

```typescript
// Static config
const chartConfig = {
  value: { label: "Value", color: "hsl(var(--chart-1))" }
} satisfies ChartConfig

// Dynamic config (from API data)
const dynamicConfig = data.reduce((acc, item) => {
  acc[item.key] = { label: item.label, color: item.color }
  return acc
}, {} as ChartConfig)
```

### Pitfall 3: Empty Data Crashes

**What goes wrong:** React error when data array is empty
**Why it happens:** Some Recharts components don't handle empty arrays gracefully
**How to avoid:** Always check for data before rendering, show empty state

```typescript
if (!data || data.length === 0) {
  return (
    <Card>
      <CardContent className="flex items-center justify-center h-[300px]">
        <p className="text-muted-foreground">No data for selected period</p>
      </CardContent>
    </Card>
  )
}
```

### Pitfall 4: Division by Zero in Percentage Calculations

**What goes wrong:** NaN or Infinity displayed, or PostgreSQL errors
**Why it happens:** Dividing by zero when no reviewed estimates exist
**How to avoid:** Use NULLIF in SQL, handle NaN in TypeScript

```sql
-- SQL: Use NULLIF to return NULL instead of error
ROUND(count_within / NULLIF(total_reviewed, 0) * 100, 1)
```

```typescript
// TypeScript: Handle NaN/null
const accuracy = data.accuracy_10 ?? 0
```

### Pitfall 5: Stale Data on Dashboard

**What goes wrong:** Dashboard shows old data even after new estimates are reviewed
**Why it happens:** No cache invalidation after mutations
**How to avoid:** Invalidate queries after review submission in Phase 5

```typescript
// In review queue mutation (Phase 5)
const queryClient = useQueryClient()

const mutation = useMutation({
  mutationFn: submitReview,
  onSuccess: () => {
    queryClient.invalidateQueries({ queryKey: ["accuracy-stats"] })
    queryClient.invalidateQueries({ queryKey: ["category-breakdown"] })
  }
})
```

## Code Examples

Verified patterns for DASH-01 through DASH-04:

### DASH-01: Accuracy Chart

```typescript
// frontend/src/components/dashboard/accuracy-chart.tsx
"use client"

import { Bar, BarChart, CartesianGrid, XAxis, YAxis } from "recharts"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import {
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
  type ChartConfig,
} from "@/components/ui/chart"

const chartConfig = {
  accuracy10: {
    label: "Within 10%",
    color: "hsl(var(--chart-1))",
  },
  accuracy20: {
    label: "Within 20%",
    color: "hsl(var(--chart-2))",
  },
} satisfies ChartConfig

interface AccuracyChartProps {
  accuracy10: number
  accuracy20: number
  totalReviewed: number
}

export function AccuracyChart({ accuracy10, accuracy20, totalReviewed }: AccuracyChartProps) {
  const data = [
    { metric: "Accuracy", accuracy10, accuracy20 },
  ]

  if (totalReviewed === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Estimate Accuracy</CardTitle>
          <CardDescription>Percentage within threshold of Laurent's price</CardDescription>
        </CardHeader>
        <CardContent className="flex items-center justify-center h-[200px]">
          <p className="text-muted-foreground">No reviewed estimates yet</p>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Estimate Accuracy</CardTitle>
        <CardDescription>
          Based on {totalReviewed} reviewed estimate{totalReviewed !== 1 ? "s" : ""}
        </CardDescription>
      </CardHeader>
      <CardContent>
        <ChartContainer config={chartConfig} className="min-h-[200px] w-full">
          <BarChart data={data} layout="vertical">
            <CartesianGrid horizontal={false} />
            <XAxis type="number" domain={[0, 100]} tickFormatter={(v) => `${v}%`} />
            <YAxis type="category" dataKey="metric" hide />
            <ChartTooltip
              content={<ChartTooltipContent />}
              formatter={(value) => [`${value}%`, ""]}
            />
            <Bar dataKey="accuracy10" fill="var(--color-accuracy10)" radius={4} />
            <Bar dataKey="accuracy20" fill="var(--color-accuracy20)" radius={4} />
          </BarChart>
        </ChartContainer>
        <div className="flex justify-center gap-4 mt-4 text-sm">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded" style={{ background: "hsl(var(--chart-1))" }} />
            <span>Within 10%: {accuracy10}%</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded" style={{ background: "hsl(var(--chart-2))" }} />
            <span>Within 20%: {accuracy20}%</span>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
```

### DASH-04: Stats Cards

```typescript
// frontend/src/components/dashboard/stats-cards.tsx
"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { TrendingUp, TrendingDown, CheckCircle, Clock } from "lucide-react"

interface StatsCardsProps {
  totalEstimates: number
  reviewedCount: number
  accuracy10: number
  accuracy20: number
}

export function StatsCards({ totalEstimates, reviewedCount, accuracy10, accuracy20 }: StatsCardsProps) {
  const pendingReview = totalEstimates - reviewedCount

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Total Estimates</CardTitle>
          <TrendingUp className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{totalEstimates}</div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Reviewed</CardTitle>
          <CheckCircle className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{reviewedCount}</div>
          <p className="text-xs text-muted-foreground">{pendingReview} pending</p>
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
          <div className="text-2xl font-bold">{accuracy10}%</div>
          <p className="text-xs text-muted-foreground">of reviewed estimates</p>
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
          <div className="text-2xl font-bold">{accuracy20}%</div>
          <p className="text-xs text-muted-foreground">of reviewed estimates</p>
        </CardContent>
      </Card>
    </div>
  )
}
```

### PostgreSQL Functions for Analytics

```sql
-- Create all analytics functions (run in Supabase SQL Editor)

-- Function 1: Get overall accuracy stats
CREATE OR REPLACE FUNCTION get_accuracy_stats(
  start_date TIMESTAMPTZ DEFAULT NULL,
  end_date TIMESTAMPTZ DEFAULT NULL
)
RETURNS TABLE (
  total_estimates BIGINT,
  reviewed_count BIGINT,
  within_10_percent BIGINT,
  within_20_percent BIGINT,
  accuracy_10 DECIMAL,
  accuracy_20 DECIMAL
) AS $$
BEGIN
  RETURN QUERY
  SELECT
    COUNT(*)::BIGINT,
    COUNT(CASE WHEN laurent_price IS NOT NULL THEN 1 END)::BIGINT,
    COUNT(CASE WHEN laurent_price IS NOT NULL
      AND ABS(ai_estimate - laurent_price) / NULLIF(laurent_price, 0) <= 0.10 THEN 1 END)::BIGINT,
    COUNT(CASE WHEN laurent_price IS NOT NULL
      AND ABS(ai_estimate - laurent_price) / NULLIF(laurent_price, 0) <= 0.20 THEN 1 END)::BIGINT,
    COALESCE(ROUND(
      COUNT(CASE WHEN laurent_price IS NOT NULL
        AND ABS(ai_estimate - laurent_price) / NULLIF(laurent_price, 0) <= 0.10 THEN 1 END)::DECIMAL
      / NULLIF(COUNT(CASE WHEN laurent_price IS NOT NULL THEN 1 END), 0) * 100, 1
    ), 0),
    COALESCE(ROUND(
      COUNT(CASE WHEN laurent_price IS NOT NULL
        AND ABS(ai_estimate - laurent_price) / NULLIF(laurent_price, 0) <= 0.20 THEN 1 END)::DECIMAL
      / NULLIF(COUNT(CASE WHEN laurent_price IS NOT NULL THEN 1 END), 0) * 100, 1
    ), 0)
  FROM estimates
  WHERE
    (start_date IS NULL OR created_at >= start_date)
    AND (end_date IS NULL OR created_at <= end_date);
END;
$$ LANGUAGE plpgsql;

-- Function 2: Get category breakdown
CREATE OR REPLACE FUNCTION get_category_breakdown(
  start_date TIMESTAMPTZ DEFAULT NULL,
  end_date TIMESTAMPTZ DEFAULT NULL
)
RETURNS TABLE (
  category TEXT,
  count BIGINT,
  percentage DECIMAL
) AS $$
BEGIN
  RETURN QUERY
  WITH totals AS (
    SELECT COUNT(*)::DECIMAL AS total
    FROM estimates
    WHERE
      (start_date IS NULL OR created_at >= start_date)
      AND (end_date IS NULL OR created_at <= end_date)
  )
  SELECT
    e.category,
    COUNT(*)::BIGINT,
    ROUND(COUNT(*)::DECIMAL / NULLIF(t.total, 0) * 100, 1)
  FROM estimates e, totals t
  WHERE
    (start_date IS NULL OR e.created_at >= start_date)
    AND (end_date IS NULL OR e.created_at <= end_date)
  GROUP BY e.category, t.total
  ORDER BY COUNT(*) DESC;
END;
$$ LANGUAGE plpgsql;

-- Function 3: Get confidence vs accuracy correlation
CREATE OR REPLACE FUNCTION get_confidence_accuracy(
  start_date TIMESTAMPTZ DEFAULT NULL,
  end_date TIMESTAMPTZ DEFAULT NULL
)
RETURNS TABLE (
  confidence TEXT,
  total_count BIGINT,
  reviewed_count BIGINT,
  accuracy_10 DECIMAL,
  accuracy_20 DECIMAL
) AS $$
BEGIN
  RETURN QUERY
  SELECT
    e.confidence,
    COUNT(*)::BIGINT,
    COUNT(CASE WHEN laurent_price IS NOT NULL THEN 1 END)::BIGINT,
    COALESCE(ROUND(
      COUNT(CASE WHEN laurent_price IS NOT NULL
        AND ABS(ai_estimate - laurent_price) / NULLIF(laurent_price, 0) <= 0.10 THEN 1 END)::DECIMAL
      / NULLIF(COUNT(CASE WHEN laurent_price IS NOT NULL THEN 1 END), 0) * 100, 1
    ), 0),
    COALESCE(ROUND(
      COUNT(CASE WHEN laurent_price IS NOT NULL
        AND ABS(ai_estimate - laurent_price) / NULLIF(laurent_price, 0) <= 0.20 THEN 1 END)::DECIMAL
      / NULLIF(COUNT(CASE WHEN laurent_price IS NOT NULL THEN 1 END), 0) * 100, 1
    ), 0)
  FROM estimates e
  WHERE
    (start_date IS NULL OR e.created_at >= start_date)
    AND (end_date IS NULL OR e.created_at <= end_date)
  GROUP BY e.confidence
  ORDER BY
    CASE e.confidence
      WHEN 'HIGH' THEN 1
      WHEN 'MEDIUM' THEN 2
      WHEN 'LOW' THEN 3
    END;
END;
$$ LANGUAGE plpgsql;
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Chart.js / raw D3 | Recharts + shadcn/ui | 2024 | Declarative, React-native, themed |
| Custom tooltip styling | ChartTooltipContent | shadcn/ui charts | Consistent with design system |
| useEffect for data | React Query | 2023+ | Better caching, loading states |
| Client-side aggregation | PostgreSQL RPC | Always recommended | Performance, accuracy |
| Fixed chart dimensions | ResponsiveContainer | Recharts standard | Mobile-friendly |

**Deprecated/outdated:**
- **react-chartjs-2 with Chart.js 2.x:** Chart.js 4.x is current, but Recharts is preferred for React
- **D3 direct DOM manipulation:** Use Recharts or visx for React integration
- **Supabase .select() for aggregations:** Use RPC for GROUP BY operations

## Open Questions

Things that couldn't be fully resolved:

1. **Exact schema of estimates table (Phase 5)**
   - What we know: Will have ai_estimate, laurent_price, category, confidence, created_at
   - What's unclear: Exact column names, whether confidence is stored or calculated
   - Recommendation: Reference Phase 5 plan when creating SQL functions, adjust column names as needed

2. **Historical trend visualization**
   - What we know: Requirements mention accuracy "over time" but DASH-01 is just accuracy, not a time series
   - What's unclear: Whether a line chart showing weekly/monthly accuracy trends is needed
   - Recommendation: Start with current-period stats; add trend chart as enhancement if requested

3. **React Query provider setup**
   - What we know: Need QueryClientProvider in app
   - What's unclear: Whether Phase 4/5 already set this up
   - Recommendation: Check for existing provider before adding; add to layout if missing

## Sources

### Primary (HIGH confidence)
- [shadcn/ui Charts Documentation](https://ui.shadcn.com/docs/components/chart) - Official component guide
- [shadcn/ui Bar Charts](https://ui.shadcn.com/charts/bar) - 10+ bar chart examples
- [shadcn/ui Line Charts](https://ui.shadcn.com/charts/line) - Line chart patterns
- [Supabase RPC Documentation](https://supabase.com/docs/reference/javascript/rpc) - PostgreSQL function calls
- [Recharts API](https://recharts.github.io/en-US/api/) - Full component reference

### Secondary (MEDIUM confidence)
- [React Query with Supabase Guide](https://supabase.com/blog/react-query-nextjs-app-router-cache-helpers) - Supabase official blog
- [shadcn-ui/ui Discussion #4133](https://github.com/shadcn-ui/ui/discussions/4133) - Community chart library comparison
- [Supabase GROUP BY Discussion](https://github.com/orgs/supabase/discussions/19517) - RPC pattern for aggregations
- [PostgreSQL Percentage Calculations](https://www.crunchydata.com/blog/percentage-calculations-using-postgres-window-functions) - SQL patterns

### Tertiary (LOW confidence)
- Various Medium articles on React Query + Supabase patterns
- DEV.to data visualization library comparisons

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - shadcn officially uses Recharts, documented extensively
- Architecture: HIGH - React Query + Supabase RPC is well-documented pattern
- Pitfalls: HIGH - Common issues verified in GitHub issues and documentation
- SQL functions: MEDIUM - Schema depends on Phase 5 implementation

**Research date:** 2026-01-18
**Valid until:** 2026-02-18 (30 days - libraries are stable)
