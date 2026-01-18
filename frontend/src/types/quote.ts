/**
 * Quote types for the Historique tab.
 * Maps to backend PaginatedQuotes response from /quotes endpoint.
 */

export interface Quote {
  id: string;
  client_name: string | null;
  category: string | null;
  city: string | null;
  sqft: number | null;
  total_price: number | null;
  margin_percent: number | null;
  created_at: string;
}

export interface QuoteFilters {
  category?: string;
  city?: string;
  min_sqft?: number;
  max_sqft?: number;
  min_price?: number;
  max_price?: number;
  start_date?: string;
  end_date?: string;
}

export interface PaginatedQuotes {
  items: Quote[];
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
}
