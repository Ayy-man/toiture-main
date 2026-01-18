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

interface AccuracyChartProps {
  accuracy10: number;
  accuracy20: number;
  totalReviewed: number;
}

const chartConfig = {
  accuracy10: {
    label: "Within 10%",
    color: "hsl(var(--chart-1))",
  },
  accuracy20: {
    label: "Within 20%",
    color: "hsl(var(--chart-2))",
  },
} satisfies ChartConfig;

export function AccuracyChart({
  accuracy10,
  accuracy20,
  totalReviewed,
}: AccuracyChartProps) {
  if (totalReviewed === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Estimate Accuracy</CardTitle>
          <CardDescription>
            Percentage of estimates within price thresholds
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex min-h-[200px] items-center justify-center text-muted-foreground">
            No reviewed estimates yet
          </div>
        </CardContent>
      </Card>
    );
  }

  const data = [
    {
      threshold: "Within 10%",
      accuracy10: accuracy10,
      accuracy20: 0,
    },
    {
      threshold: "Within 20%",
      accuracy10: 0,
      accuracy20: accuracy20,
    },
  ];

  return (
    <Card>
      <CardHeader>
        <CardTitle>Estimate Accuracy</CardTitle>
        <CardDescription>
          Percentage of estimates within price thresholds
        </CardDescription>
      </CardHeader>
      <CardContent>
        <ChartContainer config={chartConfig} className="min-h-[200px] w-full">
          <BarChart
            data={data}
            layout="vertical"
            margin={{ left: 0, right: 16 }}
          >
            <CartesianGrid horizontal={false} />
            <XAxis type="number" domain={[0, 100]} tickFormatter={(v) => `${v}%`} />
            <YAxis
              dataKey="threshold"
              type="category"
              tickLine={false}
              axisLine={false}
              width={80}
            />
            <ChartTooltip
              cursor={false}
              content={<ChartTooltipContent hideLabel />}
            />
            <ChartLegend content={<ChartLegendContent />} />
            <Bar
              dataKey="accuracy10"
              fill="var(--color-accuracy10)"
              radius={4}
            />
            <Bar
              dataKey="accuracy20"
              fill="var(--color-accuracy20)"
              radius={4}
            />
          </BarChart>
        </ChartContainer>
      </CardContent>
    </Card>
  );
}
