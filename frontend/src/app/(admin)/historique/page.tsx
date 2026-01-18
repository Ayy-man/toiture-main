"use client";

import { useState } from "react";
import { fr } from "@/lib/i18n/fr";
import { useQuotes } from "@/lib/hooks/use-quotes";
import { QuoteFiltersComponent } from "@/components/historique/quote-filters";
import { QuoteTable } from "@/components/historique/quote-table";
import { exportToCSV } from "@/lib/utils/csv-export";
import { fetchAllQuotesForExport } from "@/lib/api/quotes";

/**
 * Historique page - Quote browser with pagination, filters, and CSV export.
 * Displays historical quotes from the backend /quotes endpoint.
 */
export default function HistoriquePage() {
  const [isExporting, setIsExporting] = useState(false);
  const {
    data,
    isFetching,
    isError,
    pagination,
    setPagination,
    filters,
    setFilters,
    pageCount,
    refetch,
  } = useQuotes();

  const handleExport = async () => {
    setIsExporting(true);
    try {
      const quotes = await fetchAllQuotesForExport(filters);
      exportToCSV(quotes, "historique-soumissions");
    } catch (error) {
      console.error("Export failed:", error);
    } finally {
      setIsExporting(false);
    }
  };

  if (isError) {
    return (
      <div>
        <h1 className="text-3xl font-bold tracking-tight mb-6">
          {fr.historique.titre}
        </h1>
        <div className="text-center py-8">
          <p className="text-destructive mb-4">{fr.common.erreur}</p>
          <button
            onClick={() => refetch()}
            className="text-primary underline hover:no-underline"
          >
            {fr.common.reessayer}
          </button>
        </div>
      </div>
    );
  }

  return (
    <div>
      <h1 className="text-3xl font-bold tracking-tight mb-6">
        {fr.historique.titre}
      </h1>

      <QuoteFiltersComponent
        filters={filters}
        onFiltersChange={setFilters}
        onExport={handleExport}
        isExporting={isExporting}
      />

      <QuoteTable
        data={data?.items ?? []}
        pagination={pagination}
        setPagination={setPagination}
        pageCount={pageCount}
        isFetching={isFetching}
      />
    </div>
  );
}
