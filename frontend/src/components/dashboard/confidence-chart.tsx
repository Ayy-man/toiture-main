"use client";

import { Bar, BarChart, CartesianGrid, XAxis, YAxis } from "recharts";
import {
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
  ChartLegend,
  ChartLegendContent,
  type ChartConfig,
} from "@/components/ui/chart";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/components/ui/card";
import type { ConfidenceAccuracy } from "@/types/analytics";

interface ConfidenceChartProps {
  data: ConfidenceAccuracy[];
}

const chartConfig = {
  accuracy_10: {
    label: "Within 10%",
    color: "hsl(var(--chart-1))",
  },
  accuracy_20: {
    label: "Within 20%",
    color: "hsl(var(--chart-2))",
  },
} satisfies ChartConfig;

export function ConfidenceChart({ data }: ConfidenceChartProps) {
  if (!data || data.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Confidence vs Accuracy</CardTitle>
          <CardDescription>
            Accuracy rates by confidence level
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex min-h-[300px] items-center justify-center text-muted-foreground">
            No data available
          </div>
        </CardContent>
      </Card>
    );
  }

  // Order confidence levels consistently
  const order = ["HIGH", "MEDIUM", "LOW"];
  const sortedData = [...data].sort(
    (a, b) => order.indexOf(a.confidence) - order.indexOf(b.confidence)
  );

  return (
    <Card>
      <CardHeader>
        <CardTitle>Confidence vs Accuracy</CardTitle>
        <CardDescription>
          Accuracy rates by confidence level
        </CardDescription>
      </CardHeader>
      <CardContent>
        <ChartContainer config={chartConfig} className="min-h-[300px] w-full">
          <BarChart data={sortedData} margin={{ left: 0, right: 16 }}>
            <CartesianGrid vertical={false} />
            <XAxis
              dataKey="confidence"
              tickLine={false}
              axisLine={false}
              tickMargin={8}
            />
            <YAxis
              domain={[0, 100]}
              tickFormatter={(v) => `${v}%`}
              tickLine={false}
              axisLine={false}
            />
            <ChartTooltip
              cursor={false}
              content={<ChartTooltipContent />}
            />
            <ChartLegend content={<ChartLegendContent />} />
            <Bar
              dataKey="accuracy_10"
              fill="var(--color-accuracy_10)"
              radius={[4, 4, 0, 0]}
            />
            <Bar
              dataKey="accuracy_20"
              fill="var(--color-accuracy_20)"
              radius={[4, 4, 0, 0]}
            />
          </BarChart>
        </ChartContainer>
      </CardContent>
    </Card>
  );
}
