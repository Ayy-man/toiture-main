"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { cn } from "@/lib/utils";
import { useLanguage } from "@/lib/i18n";
import type { PricingTier } from "@/types/hybrid-quote";

interface PricingTableProps {
  tiers: PricingTier[];
  recommendedTier?: string;
  className?: string;
}

/**
 * 3-column pricing table for Basic/Standard/Premium tiers.
 * Highlights the recommended tier with a ring border.
 */
export function PricingTable({
  tiers,
  recommendedTier = "Standard",
  className,
}: PricingTableProps) {
  const { t } = useLanguage();

  // Format currency in CAD with fr-CA locale
  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat("fr-CA", {
      style: "currency",
      currency: "CAD",
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  // Get tier name translation
  const getTierName = (tier: string) => {
    switch (tier) {
      case "Basic":
        return t.fullQuote.basic;
      case "Standard":
        return t.fullQuote.standard;
      case "Premium":
        return t.fullQuote.premium;
      default:
        return tier;
    }
  };

  // Calculate markup percentage from tier
  const getMarkupPercentage = (tier: PricingTier) => {
    // Standard is the base (0%), Basic is -15%, Premium is +18%
    const standardTier = tiers.find((t) => t.tier === "Standard");
    if (!standardTier) return "0%";

    const diff = ((tier.total_price - standardTier.total_price) / standardTier.total_price) * 100;
    return diff > 0 ? `+${diff.toFixed(0)}%` : `${diff.toFixed(0)}%`;
  };

  return (
    <div className={cn("grid grid-cols-1 sm:grid-cols-3 gap-3", className)}>
      {tiers.map((tier) => {
        const isRecommended = tier.tier === recommendedTier;
        return (
          <Card
            key={tier.tier}
            className={cn(
              "relative",
              isRecommended && "ring-2 ring-primary"
            )}
          >
            {isRecommended && (
              <div className="absolute -top-3 left-1/2 -translate-x-1/2 bg-primary text-primary-foreground text-xs font-semibold px-3 py-1 rounded-full">
                {t.fullQuote.recommended}
              </div>
            )}
            <CardHeader className="pb-3">
              <CardTitle className="text-lg">{getTierName(tier.tier)}</CardTitle>
              <p className="text-xs text-muted-foreground">
                {t.fullQuote.markup}: {getMarkupPercentage(tier)}
              </p>
            </CardHeader>
            <CardContent className="space-y-2">
              <div className="text-2xl font-bold">
                {formatCurrency(tier.total_price)}
              </div>
              <div className="text-sm space-y-1 text-muted-foreground">
                <div className="flex justify-between">
                  <span>Main-d&apos;oeuvre</span>
                  <span>{formatCurrency(tier.labor_cost)}</span>
                </div>
                <div className="flex justify-between">
                  <span>Materiaux</span>
                  <span>{formatCurrency(tier.materials_cost)}</span>
                </div>
              </div>
            </CardContent>
          </Card>
        );
      })}
    </div>
  );
}
