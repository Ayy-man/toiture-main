import { z } from "zod";
import { CATEGORIES } from "../schemas";

/**
 * Zod schema for hybrid quote form validation.
 * Supports new tier-based complexity system (Phase 21).
 */
export const hybridQuoteFormSchema = z.object({
  // Core job parameters
  sqft: z.number().min(0).max(100000).optional(),
  category: z.enum(CATEGORIES, { message: "Invalid category" }),

  // NEW: Tier-based complexity
  complexity_tier: z.number().int().min(1).max(6),

  // NEW: Factor checklist values
  factor_roof_pitch: z.string().nullable().default(null),
  factor_access_difficulty: z.array(z.string()).default([]),
  factor_demolition: z.string().nullable().default(null),
  factor_penetrations_count: z.number().int().min(0).default(0),
  factor_security: z.array(z.string()).default([]),
  factor_material_removal: z.string().nullable().default(null),
  factor_roof_sections_count: z.number().int().min(1).default(2),
  factor_previous_layers_count: z.number().int().min(0).default(0),
  manual_extra_hours: z.number().min(0).default(0),

  // Line item counts
  material_lines: z.number().int().min(0).max(100),
  labor_lines: z.number().int().min(0).max(50),

  // Optional features
  has_chimney: z.boolean(),
  has_skylights: z.boolean(),
  has_subs: z.boolean(),

  // Known price
  quoted_total: z.number().nonnegative().nullable().optional(),

  // Estimator field
  created_by: z.string().optional(),
}).superRefine((data, ctx) => {
  // Conditional sqft validation: required for all categories except "Service Call"
  if (data.category !== "Service Call") {
    if (data.sqft === undefined || data.sqft === null || data.sqft <= 0) {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        message: "Square footage is required for this category",
        path: ["sqft"],
      });
    }
  }
});

export type HybridQuoteFormData = z.infer<typeof hybridQuoteFormSchema>;
