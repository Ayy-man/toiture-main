"use client";

import { DollarSign, FileText, Percent, Users } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { CardSkeleton } from "@/components/shared/card-skeleton";
import { useLanguage } from "@/lib/i18n";
import type { DashboardMetrics } from "@/types/dashboard";

interface MetricsCardsProps {
  metrics: DashboardMetrics | undefined;
  isLoading: boolean;
}

/**
 * Format number as CAD currency.
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
 * Format number as percentage.
 */
function formatPercent(value: number): string {
  return new Intl.NumberFormat("fr-CA", {
    style: "percent",
    minimumFractionDigits: 1,
    maximumFractionDigits: 1,
  }).format(value / 100);
}

export function MetricsCards({ metrics, isLoading }: MetricsCardsProps) {
  const { t } = useLanguage();

  // Show card skeletons during loading
  if (isLoading) {
    return (
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <CardSkeleton />
        <CardSkeleton />
        <CardSkeleton />
        <CardSkeleton />
      </div>
    );
  }

  const cards = [
    {
      title: t.apercu.revenuTotal,
      icon: DollarSign,
      value: metrics ? formatCurrency(metrics.total_revenue) : null,
    },
    {
      title: t.apercu.nombreSoumissions,
      icon: FileText,
      value: metrics ? metrics.total_quotes.toLocaleString("fr-CA") : null,
    },
    {
      title: t.apercu.margeMovenne,
      icon: Percent,
      value: metrics ? formatPercent(metrics.average_margin) : null,
    },
    {
      title: t.apercu.clientsActifs,
      icon: Users,
      value: metrics ? metrics.active_clients.toLocaleString("fr-CA") : null,
    },
  ];

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      {cards.map((card) => (
        <Card key={card.title}>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">{card.title}</CardTitle>
            <card.icon className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{card.value ?? "-"}</div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
