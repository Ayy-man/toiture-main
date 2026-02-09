"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { AlertTriangle } from "lucide-react";
import { useLanguage } from "@/lib/i18n";
import { useDashboardMetrics, useDashboardCharts, useComplianceReport } from "@/lib/hooks/use-dashboard";
import { MetricsCards } from "@/components/apercu/metrics-cards";
import { RevenueChart } from "@/components/apercu/revenue-chart";
import { CategoryChart } from "@/components/apercu/category-chart";
import { TrendChart } from "@/components/apercu/trend-chart";
import { TopClients } from "@/components/apercu/top-clients";

export default function ApercuPage() {
  const { t } = useLanguage();
  const { data: metrics, isLoading: metricsLoading } = useDashboardMetrics();
  const { data: charts, isLoading: chartsLoading } = useDashboardCharts();
  const { data: compliance, isLoading: complianceLoading } = useComplianceReport();

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

      {/* Compliance Section */}
      <Card>
        <CardHeader>
          <CardTitle>{t.apercu.sqftCompliance}</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {complianceLoading ? (
            <div className="flex items-center justify-center py-8">
              <div className="text-sm text-muted-foreground">{t.common.chargement}</div>
            </div>
          ) : !compliance ? (
            <div className="text-sm text-muted-foreground text-center py-8">
              {t.apercu.noComplianceData}
            </div>
          ) : (
            <>
              {/* Alert Banner */}
              {compliance.alert && (
                <Alert variant="destructive" className="border-amber-500 bg-amber-50 text-amber-900 dark:border-amber-800 dark:bg-amber-950 dark:text-amber-200">
                  <AlertTriangle className="h-4 w-4" />
                  <AlertDescription>{t.apercu.complianceAlert}</AlertDescription>
                </Alert>
              )}

              {/* Overall Rate Display */}
              <div className="flex items-center justify-center py-4">
                <div className="text-center">
                  <div className="text-sm text-muted-foreground mb-1">
                    {t.apercu.completionRate}
                  </div>
                  <div className={`text-4xl font-bold ${compliance.overall_completion_rate >= 0.8 ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'}`}>
                    {(compliance.overall_completion_rate * 100).toFixed(1)}%
                  </div>
                  <div className="text-xs text-muted-foreground mt-1">
                    {compliance.total_with_sqft} / {compliance.total_estimates} {t.apercu.totalEstimatesCol.toLowerCase()}
                  </div>
                </div>
              </div>

              {/* Per-Estimator Table */}
              <div className="rounded-md border">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b bg-muted/50">
                      <th className="p-3 text-left font-medium">{t.apercu.estimateurCol}</th>
                      <th className="p-3 text-right font-medium">{t.apercu.totalEstimatesCol}</th>
                      <th className="p-3 text-right font-medium">{t.apercu.sqftCompletedCol}</th>
                      <th className="p-3 text-right font-medium">{t.apercu.rateCol}</th>
                    </tr>
                  </thead>
                  <tbody>
                    {compliance.estimators.map((est, idx) => (
                      <tr key={idx} className="border-b last:border-0">
                        <td className="p-3">{est.name || 'Unknown'}</td>
                        <td className="p-3 text-right">{est.total_estimates}</td>
                        <td className="p-3 text-right">{est.sqft_completed}</td>
                        <td className={`p-3 text-right font-medium ${est.completion_rate >= 0.8 ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'}`}>
                          {(est.completion_rate * 100).toFixed(1)}%
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
