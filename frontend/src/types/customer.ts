export type CustomerSegment = "VIP" | "Regular" | "New";

export interface CustomerResult {
  id: string;
  name: string;
  city: string | null;
  total_quotes: number;
  lifetime_value: number;
  segment: CustomerSegment;
}

export interface CustomerQuote {
  id: string;
  category: string | null;
  sqft: number | null;
  total_price: number | null;
  created_at: string;
}

export interface CustomerDetail {
  id: string;
  name: string;
  city: string | null;
  phone: string | null;
  email: string | null;
  total_quotes: number;
  lifetime_value: number;
  segment: CustomerSegment;
  quotes: CustomerQuote[];
}
