"use client";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { useLanguage } from "@/lib/i18n";
import type { HybridQuoteResponseData } from "@/types/chat";
import { Loader2 } from "lucide-react";

interface QuoteSummaryCardProps {
  quote: HybridQuoteResponseData;
  onSelectTier: (tier: "Basic" | "Standard" | "Premium") => void;
  onCreateSubmission: (tier: "Basic" | "Standard" | "Premium") => void;
  selectedTier?: "Basic" | "Standard" | "Premium";
  isCreatingSubmission?: boolean;
}

export function QuoteSummaryCard({
  quote,
  onSelectTier,
  onCreateSubmission,
  selectedTier,
  isCreatingSubmission = false,
}: QuoteSummaryCardProps) {
  const { t, locale } = useLanguage();

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat("fr-CA", {
      style: "currency",
      currency: "CAD",
    }).format(price);
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.7) return "text-green-600 dark:text-green-400";
    if (confidence >= 0.5) return "text-amber-600 dark:text-amber-400";
    return "text-red-600 dark:text-red-400";
  };

  const getConfidenceDotColor = (confidence: number) => {
    if (confidence >= 0.7) return "bg-green-600";
    if (confidence >= 0.5) return "bg-amber-600";
    return "bg-red-600";
  };

  return (
    <Card className="w-full my-2">
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg">
            {locale === "fr" ? "Devis genere" : "Quote Generated"}
          </CardTitle>
          <Badge variant="outline" className={getConfidenceColor(quote.overall_confidence)}>
            {locale === "fr" ? "Confiance" : "Confidence"}:{" "}
            {(quote.overall_confidence * 100).toFixed(0)}%
          </Badge>
        </div>
      </CardHeader>
      <CardContent>
        {/* Three-tier pricing cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
          {quote.pricing_tiers.map((tier) => (
            <Card
              key={tier.tier}
              className={`cursor-pointer transition-all hover:shadow-md ${
                selectedTier === tier.tier
                  ? "ring-2 ring-primary"
                  : "hover:ring-1 hover:ring-muted-foreground"
              }`}
              onClick={() => onSelectTier(tier.tier)}
            >
              <CardHeader className="pb-3">
                <CardTitle className="text-base">
                  {tier.tier}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div className="text-2xl font-bold">{formatPrice(tier.total_price)}</div>
                  <div className="text-sm text-muted-foreground space-y-1">
                    <div>
                      {locale === "fr" ? "Materiaux" : "Materials"}:{" "}
                      {formatPrice(tier.materials_cost)}
                    </div>
                    <div>
                      {locale === "fr" ? "Main-d'oeuvre" : "Labor"}:{" "}
                      {formatPrice(tier.labor_cost)}
                    </div>
                  </div>
                  <p className="text-xs text-muted-foreground mt-2">{tier.description}</p>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Create Submission button */}
        <Button
          onClick={() => selectedTier && onCreateSubmission(selectedTier)}
          disabled={!selectedTier || isCreatingSubmission}
          className="w-full md:w-auto"
          size="lg"
        >
          {isCreatingSubmission && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
          {t.chat.createSubmission}
        </Button>

        {/* Confidence indicator */}
        <div className="flex items-center gap-2 mt-4 text-sm text-muted-foreground">
          <div
            className={`w-2 h-2 rounded-full ${getConfidenceDotColor(
              quote.overall_confidence
            )}`}
          />
          <span>
            {locale === "fr" ? "Confiance" : "Confidence"}:{" "}
            {(quote.overall_confidence * 100).toFixed(0)}%
          </span>
        </div>
      </CardContent>
    </Card>
  );
}
