// Matches backend EstimateListItem
export interface PendingEstimate {
  id: string;
  created_at: string;
  sqft: number;
  category: string;
  ai_estimate: number;
  confidence: "HIGH" | "MEDIUM" | "LOW";
  reviewed: boolean;
}

// Matches backend EstimateDetail
export interface EstimateDetail extends PendingEstimate {
  material_lines: number;
  labor_lines: number;
  has_subs: boolean;
  complexity: number;
  range_low: number;
  range_high: number;
  model: string;
  reasoning: string | null;
}

// Request for submitting feedback
export interface SubmitFeedbackRequest {
  estimate_id: string;
  laurent_price: number;
}
