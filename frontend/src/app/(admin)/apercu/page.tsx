"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useLanguage } from "@/lib/i18n";
import { useDashboardMetrics, useDashboardCharts } from "@/lib/hooks/use-dashboard";
import { MetricsCards } from "@/components/apercu/metrics-cards";
import { RevenueChart } from "@/components/apercu/revenue-chart";
import { CategoryChart } from "@/components/apercu/category-chart";
import { TrendChart } from "@/components/apercu/trend-chart";
import { TopClients } from "@/components/apercu/top-clients";

export default function ApercuPage() {
  const { t } = useLanguage();
  const { data: metrics, isLoading: metricsLoading } = useDashboardMetrics();
  const { data: charts, isLoading: chartsLoading } = useDashboardCharts();

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold tracking-tight">
        {t.apercu.titre}
      </h1>

      {/* KPI Cards */}
      <MetricsCards metrics={metrics} isLoading={metricsLoading} />

      {/* Disclaimer Banner */}
      <div className="rounded-lg border border-blue-200 bg-blue-50 dark:border-blue-800 dark:bg-blue-950 px-4 py-3 text-sm text-blue-800 dark:text-blue-200">
        {t.apercu.disclaimer}
      </div>

      {/* Charts Grid */}
      <div className="grid gap-6 lg:grid-cols-3">
        {/* Revenue by Year - spans 2 columns */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>{t.apercu.valeurParAnnee}</CardTitle>
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
            <CardTitle>{t.apercu.valeurParCategorie}</CardTitle>
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
            <CardTitle>{t.apercu.tendanceMensuelle}</CardTitle>
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
            <CardTitle>{t.apercu.topClients}</CardTitle>
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
