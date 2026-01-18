"use client";

import { PieChart, Pie, Cell, Label } from "recharts";
import {
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
  type ChartConfig,
} from "@/components/ui/chart";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/components/ui/card";
import type { CategoryBreakdown as CategoryBreakdownType } from "@/types/analytics";

interface CategoryBreakdownProps {
  data: CategoryBreakdownType[];
}

// Color mapping for categories
const CATEGORY_COLORS: Record<string, string> = {
  Bardeaux: "hsl(var(--chart-1))",
  Elastomere: "hsl(var(--chart-2))",
  Other: "hsl(var(--chart-3))",
  "Service Call": "hsl(var(--chart-4))",
  Gutters: "hsl(var(--chart-5))",
};

function getCategoryColor(category: string): string {
  return CATEGORY_COLORS[category] ?? "hsl(var(--chart-3))";
}

function buildChartConfig(data: CategoryBreakdownType[]): ChartConfig {
  const config: ChartConfig = {};
  for (const item of data) {
    config[item.category] = {
      label: item.category,
      color: getCategoryColor(item.category),
    };
  }
  return config;
}

export function CategoryBreakdown({ data }: CategoryBreakdownProps) {
  if (!data || data.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Category Distribution</CardTitle>
          <CardDescription>
            Estimate breakdown by roofing category
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

  const chartConfig = buildChartConfig(data);
  const total = data.reduce((sum, item) => sum + item.count, 0);

  return (
    <Card>
      <CardHeader>
        <CardTitle>Category Distribution</CardTitle>
        <CardDescription>
          Estimate breakdown by roofing category
        </CardDescription>
      </CardHeader>
      <CardContent>
        <ChartContainer config={chartConfig} className="mx-auto min-h-[300px] w-full max-w-[400px]">
          <PieChart>
            <ChartTooltip
              cursor={false}
              content={<ChartTooltipContent hideLabel />}
            />
            <Pie
              data={data}
              dataKey="count"
              nameKey="category"
              innerRadius={60}
              outerRadius={100}
              strokeWidth={2}
              paddingAngle={2}
            >
              {data.map((entry) => (
                <Cell
                  key={entry.category}
                  fill={getCategoryColor(entry.category)}
                />
              ))}
              <Label
                content={({ viewBox }) => {
                  if (viewBox && "cx" in viewBox && "cy" in viewBox) {
                    return (
                      <text
                        x={viewBox.cx}
                        y={viewBox.cy}
                        textAnchor="middle"
                        dominantBaseline="middle"
                      >
                        <tspan
                          x={viewBox.cx}
                          y={viewBox.cy}
                          className="fill-foreground text-3xl font-bold"
                        >
                          {total}
                        </tspan>
                        <tspan
                          x={viewBox.cx}
                          y={(viewBox.cy || 0) + 24}
                          className="fill-muted-foreground text-sm"
                        >
                          Estimates
                        </tspan>
                      </text>
                    );
                  }
                  return null;
                }}
              />
            </Pie>
          </PieChart>
        </ChartContainer>
        <div className="mt-4 flex flex-wrap justify-center gap-4">
          {data.map((item) => (
            <div key={item.category} className="flex items-center gap-2">
              <div
                className="h-3 w-3 rounded-full"
                style={{ backgroundColor: getCategoryColor(item.category) }}
              />
              <span className="text-sm text-muted-foreground">
                {item.category}: {item.percentage.toFixed(1)}%
              </span>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
