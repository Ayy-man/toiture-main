/**
 * TypeScript types for submission workflow.
 * Mirrors backend Pydantic models from backend/app/schemas/submission.py
 */

/**
 * Submission status enum matching backend SubmissionStatus
 */
export type SubmissionStatus = 'draft' | 'pending_approval' | 'approved' | 'rejected';

/**
 * Line item type (material or labor)
 */
export type LineItemType = 'material' | 'labor';

/**
 * Editable line item in a submission
 */
export interface LineItem {
  id: string; // UUID
  type: LineItemType;
  material_id?: number | null; // Optional reference to materials table
  name: string;
  quantity: number;
  unit_price: number;
  total: number; // quantity * unit_price
  order: number; // For drag-and-drop ordering
}

/**
 * Note attached to a submission
 */
export interface Note {
  id: string; // UUID
  text: string;
  created_by: string;
  created_at: string; // ISO 8601 timestamp
}

/**
 * Audit log entry for submission state changes
 */
export interface AuditEntry {
  action: string; // e.g., "created", "edited", "finalized", "approved", "rejected", "returned_to_draft"
  user: string;
  timestamp: string; // ISO 8601 timestamp
  changes?: Record<string, unknown>; // Optional changes object
  reason?: string; // Optional reason (e.g., rejection reason)
}

/**
 * Three-tier pricing (Basic/Standard/Premium)
 */
export interface PricingTier {
  tier: "Basic" | "Standard" | "Premium";
  total_price: number;
  materials_cost: number;
  labor_cost: number;
  description: string;
}

/**
 * Full submission with all fields
 */
export interface Submission {
  id: string; // UUID
  estimate_id?: string | null; // Optional reference to original estimate
  status: SubmissionStatus;
  category: string;
  sqft?: number | null;
  client_name?: string | null;
  line_items: LineItem[];
  pricing_tiers: PricingTier[]; // Always exactly 3 tiers
  selected_tier: "Basic" | "Standard" | "Premium";
  total_price: number; // Calculated from selected_tier
  notes: Note[];
  audit_log: AuditEntry[];
  created_by: string;
  created_at: string; // ISO 8601 timestamp
  updated_at: string; // ISO 8601 timestamp
  finalized_at?: string | null; // ISO 8601 timestamp when status moved to pending_approval
  parent_submission_id?: string | null; // If this is an upsell, link to parent
  upsell_type?: string | null; // Type of upsell (e.g., "heating_cables", "gutters")
  children?: SubmissionListItem[]; // Upsell child submissions
}

/**
 * Compact submission for list views
 */
export interface SubmissionListItem {
  id: string;
  status: SubmissionStatus;
  category: string;
  client_name?: string | null;
  total_price: number;
  created_at: string;
  upsell_type?: string | null;
  has_children: boolean;
}

/**
 * Payload for creating a new submission
 */
export interface SubmissionCreatePayload {
  category: string;
  sqft?: number | null;
  client_name?: string | null;
  created_by: string;
  line_items: Omit<LineItem, 'id'>[]; // Line items without IDs (server generates UUIDs)
  pricing_tiers: PricingTier[];
  selected_tier: "Basic" | "Standard" | "Premium";
  estimate_id?: string | null; // Optional link to original estimate
}

/**
 * Upsell suggestion (bilingual)
 */
export interface UpsellSuggestion {
  type: string; // e.g., "heating_cables", "gutters", "ventilation"
  name_fr: string;
  name_en: string;
  description_fr: string;
  description_en: string;
}
