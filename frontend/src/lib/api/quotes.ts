/**
 * API client for quotes endpoint.
 * Fetches paginated quotes from backend with filter support.
 */

import type { Quote, QuoteFilters, PaginatedQuotes } from "@/types/quote";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

/**
 * Fetch paginated quotes with optional filters.
 */
export async function fetchQuotes(
  page: number,
  perPage: number,
  filters: QuoteFilters
): Promise<PaginatedQuotes> {
  const params = new URLSearchParams({
    page: String(page),
    per_page: String(perPage),
  });

  // Add non-empty filters
  Object.entries(filters).forEach(([key, value]) => {
    if (value !== undefined && value !== "") {
      params.set(key, String(value));
    }
  });

  const response = await fetch(`${API_URL}/quotes?${params}`);
  if (!response.ok) {
    throw new Error("Failed to fetch quotes");
  }
  return response.json();
}

/**
 * Fetch all quotes matching filters for CSV export.
 * Limited to 10,000 records for performance.
 */
export async function fetchAllQuotesForExport(
  filters: QuoteFilters
): Promise<Quote[]> {
  const params = new URLSearchParams({
    page: "1",
    per_page: "10000",
  });

  Object.entries(filters).forEach(([key, value]) => {
    if (value !== undefined && value !== "") {
      params.set(key, String(value));
    }
  });

  const response = await fetch(`${API_URL}/quotes?${params}`);
  if (!response.ok) {
    throw new Error("Failed to fetch quotes for export");
  }
  const data: PaginatedQuotes = await response.json();
  return data.items;
}
