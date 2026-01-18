"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { fr } from "@/lib/i18n/fr";
import { useDashboardMetrics, useDashboardCharts } from "@/lib/hooks/use-dashboard";
import { MetricsCards } from "@/components/apercu/metrics-cards";
import { RevenueChart } from "@/components/apercu/revenue-chart";
import { CategoryChart } from "@/components/apercu/category-chart";
import { TrendChart } from "@/components/apercu/trend-chart";
import { TopClients } from "@/components/apercu/top-clients";

export default function ApercuPage() {
  const { data: metrics, isLoading: metricsLoading } = useDashboardMetrics();
  const { data: charts, isLoading: chartsLoading } = useDashboardCharts();

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold tracking-tight">
        {fr.apercu.titre}
      </h1>

      {/* KPI Cards */}
      <MetricsCards metrics={metrics} isLoading={metricsLoading} />

      {/* Charts Grid */}
      <div className="grid gap-6 lg:grid-cols-3">
        {/* Revenue by Year - spans 2 columns */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Revenu par annee</CardTitle>
          </CardHeader>
          <CardContent>
            <RevenueChart
              data={charts?.revenue_by_year}
              isLoading={chartsLoading}
            />
          </CardContent>
        </Card>

        {/* Revenue by Category */}
        <Card>
          <CardHeader>
            <CardTitle>Revenu par categorie</CardTitle>
          </CardHeader>
          <CardContent>
            <CategoryChart
              data={charts?.revenue_by_category}
              isLoading={chartsLoading}
            />
          </CardContent>
        </Card>

        {/* Monthly Trend - spans 2 columns */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Tendance mensuelle</CardTitle>
          </CardHeader>
          <CardContent>
            <TrendChart
              data={charts?.monthly_trend}
              isLoading={chartsLoading}
            />
          </CardContent>
        </Card>

        {/* Top Clients */}
        <Card>
          <CardHeader>
            <CardTitle>Top clients</CardTitle>
          </CardHeader>
          <CardContent>
            <TopClients
              clients={charts?.top_clients}
              isLoading={chartsLoading}
            />
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
