"use client";

import { useState, useMemo } from "react";
import { ChevronDown, AlertTriangle } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible";
import { cn } from "@/lib/utils";
import ReactMarkdown from "react-markdown";
import type { HybridQuoteResponse } from "@/types/hybrid-quote";
import { QuoteActions } from "./quote-actions";
import { FeedbackPanel } from "./feedback-panel";

export interface QuoteResultProps {
  quote: HybridQuoteResponse;
  category: string;
  sqft: number;
  inputParams?: Record<string, unknown>;
}

/**
 * Invoice-style quote result display component.
 * Displays work items, materials total, labor total, and grand total with confidence warning.
 * Collapsible reasoning section with markdown rendering.
 */
export function QuoteResult({ quote, category, sqft, inputParams }: QuoteResultProps) {
  const [isReasoningOpen, setIsReasoningOpen] = useState(false);

  // Generate a stable estimate ID for feedback tracking
  const estimateId = useMemo(() => crypto.randomUUID(), []);

  // Format currency in CAD with fr-CA locale
  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat("fr-CA", {
      style: "currency",
      currency: "CAD",
      minimumFractionDigits: 0,
      maximumFractionDigits: amount % 1 === 0 ? 0 : 2,
    }).format(amount);
  };

  // Format hours with one decimal place
  const formatHours = (hours: number) => {
    return hours.toFixed(1);
  };

  // Get Standard tier pricing (middle tier)
  const standardTier = quote.pricing_tiers.find((t) => t.tier === "Standard");
  if (!standardTier) {
    return (
      <Card>
        <CardContent className="pt-6">
          <p className="text-destructive">
            Erreur: Tarification Standard non disponible
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardContent className="pt-6 space-y-6">
        {/* Confidence Warning Banner */}
        {quote.overall_confidence < 0.5 && (
          <div className="flex items-start gap-3 rounded-lg bg-amber-50 border border-amber-200 p-4">
            <AlertTriangle className="h-5 w-5 text-amber-600 mt-0.5 flex-shrink-0" />
            <div className="flex-1">
              <p className="font-medium text-amber-800">
                Confiance: {Math.round(quote.overall_confidence * 100)}% -
                Verification recommandee
              </p>
            </div>
          </div>
        )}

        {/* Header Section */}
        <div className="text-center border-b pb-4">
          <h2 className="text-2xl font-bold mb-2">SOUMISSION</h2>
          <div className="text-sm text-muted-foreground space-y-1">
            <p>
              <span className="font-medium">Categorie:</span> {category}
            </p>
            <p>
              <span className="font-medium">Superficie:</span> {sqft} pi2
            </p>
          </div>
        </div>

        {/* Work Items Section */}
        <div className="space-y-3">
          <h3 className="text-sm font-semibold uppercase tracking-wide text-muted-foreground border-b pb-2">
            TRAVAUX
          </h3>
          <div className="space-y-2">
            {quote.work_items.map((item, index) => (
              <div
                key={index}
                className="flex justify-between items-baseline text-sm"
              >
                <div className="flex items-baseline gap-2">
                  <span className="text-muted-foreground">•</span>
                  <span>{item.name}</span>
                </div>
                <span className="text-muted-foreground tabular-nums">
                  {formatHours(item.labor_hours)} hrs
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Summary Section */}
        <div className="space-y-3">
          <h3 className="text-sm font-semibold uppercase tracking-wide text-muted-foreground border-b pb-2">
            SOMMAIRE
          </h3>
          <div className="space-y-2 text-sm">
            {/* Materials */}
            <div className="flex justify-between items-baseline">
              <span>Materiaux</span>
              <span className="font-medium tabular-nums">
                {formatCurrency(quote.total_materials_cost)}
              </span>
            </div>
            {/* Labor */}
            <div className="flex justify-between items-baseline">
              <span>
                Main-d&apos;oeuvre ({formatHours(quote.total_labor_hours)} hrs)
              </span>
              <span className="font-medium tabular-nums">
                {formatCurrency(standardTier.labor_cost)}
              </span>
            </div>
            {/* Divider */}
            <hr className="my-2" />
            {/* Total */}
            <div className="flex justify-between items-baseline text-lg font-bold">
              <span>TOTAL</span>
              <span className="tabular-nums">
                {formatCurrency(standardTier.total_price)}
              </span>
            </div>
          </div>
        </div>

        {/* Reasoning Section (Collapsible) */}
        <Collapsible open={isReasoningOpen} onOpenChange={setIsReasoningOpen}>
          <CollapsibleTrigger className="w-full flex justify-between items-center py-2 text-sm font-medium hover:text-foreground/80 transition-colors">
            <span>Raisonnement</span>
            <ChevronDown
              className={cn(
                "h-4 w-4 transition-transform duration-200",
                isReasoningOpen && "rotate-180"
              )}
            />
          </CollapsibleTrigger>
          <CollapsibleContent className="pt-3 text-sm text-muted-foreground prose prose-sm max-w-none">
            <ReactMarkdown>{quote.reasoning}</ReactMarkdown>
          </CollapsibleContent>
        </Collapsible>

        {/* QuoteActions - PDF export and future actions */}
        <QuoteActions quote={quote} category={category} sqft={sqft} />

        {/* Feedback Panel */}
        <FeedbackPanel
          estimateId={estimateId}
          inputParams={inputParams || { category, sqft }}
          predictedPrice={standardTier.total_price}
          predictedMaterials={quote.materials}
        />
      </CardContent>
    </Card>
  );
}
