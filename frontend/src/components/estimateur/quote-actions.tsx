"use client";

import { useState } from "react";
import { pdf } from "@react-pdf/renderer";
import { Button } from "@/components/ui/button";
import { FileDown, FileText, Loader2 } from "lucide-react";
import { QuotePDFDocument } from "@/lib/pdf/quote-template";
import { generateQuoteDOCX } from "@/lib/docx/quote-template";
import type { HybridQuoteResponse } from "@/types/hybrid-quote";
import { useLanguage } from "@/lib/i18n";

interface QuoteActionsProps {
  quote: HybridQuoteResponse;
  category: string;
  sqft: number;
}

export function QuoteActions({ quote, category, sqft }: QuoteActionsProps) {
  const { t, locale } = useLanguage();
  const [isExporting, setIsExporting] = useState(false);
  const [isExportingDOCX, setIsExportingDOCX] = useState(false);

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

  async function handleExportDOCX() {
    setIsExportingDOCX(true);
    try {
      const now = new Date();
      const dateStr = now.toLocaleDateString("fr-CA");
      const filenameDateStr = now.toISOString().split("T")[0];

      const blob = await generateQuoteDOCX(
        quote,
        category,
        sqft,
        dateStr,
        locale as "fr" | "en"
      );

      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `Soumission-${category}-${filenameDateStr}.docx`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error("DOCX export failed:", error);
    } finally {
      setIsExportingDOCX(false);
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
            {t.common.chargement}
          </>
        ) : (
          <>
            <FileDown className="mr-2 h-4 w-4" />
            {t.fullQuote.exporterPDF}
          </>
        )}
      </Button>

      <Button
        variant="outline"
        onClick={handleExportDOCX}
        disabled={isExportingDOCX}
      >
        {isExportingDOCX ? (
          <>
            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            {t.common.chargement}
          </>
        ) : (
          <>
            <FileText className="mr-2 h-4 w-4" />
            {(t.fullQuote as any).exporterDOCX || (t.fullQuote as any).exportDOCX}
          </>
        )}
      </Button>

      {/* Future buttons for Send (Phase 24-02/03) */}
    </div>
  );
}
