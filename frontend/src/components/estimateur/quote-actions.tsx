"use client";

import { useState } from "react";
import { pdf } from "@react-pdf/renderer";
import { Button } from "@/components/ui/button";
import { FileDown, Loader2 } from "lucide-react";
import { QuotePDFDocument } from "@/lib/pdf/quote-template";
import type { HybridQuoteResponse } from "@/types/hybrid-quote";
import { fr } from "@/lib/i18n/fr";

interface QuoteActionsProps {
  quote: HybridQuoteResponse;
  category: string;
  sqft: number;
}

export function QuoteActions({ quote, category, sqft }: QuoteActionsProps) {
  const [isExporting, setIsExporting] = useState(false);

  async function handleExportPDF() {
    setIsExporting(true);
    try {
      // Format date for filename and document
      const now = new Date();
      const dateStr = now.toLocaleDateString("fr-CA"); // YYYY-MM-DD format
      const filenameDateStr = now.toISOString().split("T")[0]; // YYYY-MM-DD

      // Generate PDF blob
      const blob = await pdf(
        <QuotePDFDocument
          quote={quote}
          category={category}
          sqft={sqft}
          date={dateStr}
        />
      ).toBlob();

      // Create download link
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `Soumission-${category}-${filenameDateStr}.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error("PDF export failed:", error);
    } finally {
      setIsExporting(false);
    }
  }

  return (
    <div className="flex flex-wrap gap-3 pt-4 border-t">
      <Button
        variant="outline"
        onClick={handleExportPDF}
        disabled={isExporting}
      >
        {isExporting ? (
          <>
            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            {fr.common.chargement}
          </>
        ) : (
          <>
            <FileDown className="mr-2 h-4 w-4" />
            {fr.fullQuote.exporterPDF}
          </>
        )}
      </Button>

      {/* Future buttons for Send and Save (Phase 14C) */}
      {/*
      <Button variant="outline" disabled>
        <Mail className="mr-2 h-4 w-4" />
        {fr.fullQuote.envoyer}
      </Button>
      <Button variant="outline" disabled>
        <Save className="mr-2 h-4 w-4" />
        {fr.fullQuote.sauvegarder}
      </Button>
      */}
    </div>
  );
}
