/**
 * TypeScript types for hybrid quote generation.
 * Mirrors backend Pydantic models from backend/app/schemas/hybrid_quote.py
 */

/**
 * Request model for hybrid quote generation endpoint.
 * Contains job parameters and 6 complexity factors that sum to complexity_aggregate.
 */
export interface HybridQuoteRequest {
  // Core job parameters
  sqft: number;
  category: string;

  // Complexity factors (6 factors that sum to complexity_aggregate)
  complexity_aggregate: number; // 0-56
  access_difficulty: number; // 0-10
  roof_pitch: number; // 0-8
  penetrations: number; // 0-10
  material_removal: number; // 0-8
  safety_concerns: number; // 0-10
  timeline_constraints: number; // 0-10

  // Optional features
  has_chimney: boolean;
  has_skylights: boolean;

  // Line item counts (for material/labor complexity)
  material_lines: number; // 0-100
  labor_lines: number; // 0-50

  // Subcontractor flag
  has_subs: boolean;

  // Known price (for comparison/feedback)
  quoted_total?: number | null;
}

/**
 * Work item (labor) with estimated hours and source tracking.
 */
export interface WorkItem {
  name: string;
  labor_hours: number;
  source: "CBR" | "ML" | "MERGED";
}

/**
 * Material line item with quantity, pricing, and confidence tracking.
 */
export interface MaterialLineItem {
  material_id: number; // 1-1000
  quantity: number;
  unit_price: number;
  total: number;
  source: "CBR" | "ML" | "MERGED";
  confidence: number; // 0.0-1.0
}

/**
 * Three-tier pricing model (Basic/Standard/Premium).
 */
export interface PricingTier {
  tier: "Basic" | "Standard" | "Premium";
  total_price: number;
  materials_cost: number;
  labor_cost: number;
  description: string;
}

/**
 * API response model for hybrid quote generation.
 * Extends quote output with request metadata and review flags.
 */
export interface HybridQuoteResponse {
  // Quote output
  work_items: WorkItem[];
  materials: MaterialLineItem[];
  total_labor_hours: number;
  total_materials_cost: number;
  total_price: number;
  overall_confidence: number; // 0.0-1.0
  reasoning: string;
  pricing_tiers: PricingTier[]; // Always exactly 3 items

  // Response metadata
  request_id: string | null;
  needs_review: boolean;
  cbr_cases_used: number;
  ml_confidence: "HIGH" | "MEDIUM" | "LOW";
  processing_time_ms: number;
}
