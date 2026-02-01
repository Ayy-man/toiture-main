import { z } from "zod";
import { CATEGORIES } from "../schemas";

/**
 * Zod schema for hybrid quote form validation.
 * Mirrors backend HybridQuoteRequest validation in backend/app/schemas/hybrid_quote.py
 */
export const hybridQuoteFormSchema = z.object({
  // Core job parameters
  sqft: z
    .number()
    .positive("Square footage must be positive")
    .max(100000, "Square footage cannot exceed 100,000"),

  category: z.enum(CATEGORIES, {
    message: "Invalid category",
  }),

  // Complexity factors (6 factors that sum to complexity_aggregate)
  complexity_aggregate: z
    .number()
    .int("Complexity aggregate must be a whole number")
    .min(0, "Complexity aggregate cannot be negative")
    .max(56, "Complexity aggregate cannot exceed 56"),

  access_difficulty: z
    .number()
    .int("Access difficulty must be a whole number")
    .min(0, "Access difficulty cannot be negative")
    .max(10, "Access difficulty cannot exceed 10"),

  roof_pitch: z
    .number()
    .int("Roof pitch must be a whole number")
    .min(0, "Roof pitch cannot be negative")
    .max(8, "Roof pitch cannot exceed 8"),

  penetrations: z
    .number()
    .int("Penetrations must be a whole number")
    .min(0, "Penetrations cannot be negative")
    .max(10, "Penetrations cannot exceed 10"),

  material_removal: z
    .number()
    .int("Material removal must be a whole number")
    .min(0, "Material removal cannot be negative")
    .max(8, "Material removal cannot exceed 8"),

  safety_concerns: z
    .number()
    .int("Safety concerns must be a whole number")
    .min(0, "Safety concerns cannot be negative")
    .max(10, "Safety concerns cannot exceed 10"),

  timeline_constraints: z
    .number()
    .int("Timeline constraints must be a whole number")
    .min(0, "Timeline constraints cannot be negative")
    .max(10, "Timeline constraints cannot exceed 10"),

  // Optional features
  has_chimney: z.boolean(),
  has_skylights: z.boolean(),

  // Line item counts
  material_lines: z
    .number()
    .int("Material lines must be a whole number")
    .min(0, "Material lines cannot be negative")
    .max(100, "Material lines cannot exceed 100"),

  labor_lines: z
    .number()
    .int("Labor lines must be a whole number")
    .min(0, "Labor lines cannot be negative")
    .max(50, "Labor lines cannot exceed 50"),

  // Subcontractor flag
  has_subs: z.boolean(),

  // Known price (for comparison/feedback)
  quoted_total: z
    .number()
    .nonnegative("Quoted total cannot be negative")
    .nullable()
    .optional(),
}).refine(
  (data) => {
    // Validate that complexity_aggregate matches sum of 6 factors (with 5% tolerance)
    const calculatedSum =
      data.access_difficulty +
      data.roof_pitch +
      data.penetrations +
      data.material_removal +
      data.safety_concerns +
      data.timeline_constraints;

    const tolerance = Math.max(1, Math.floor(calculatedSum * 0.05));

    return Math.abs(data.complexity_aggregate - calculatedSum) <= tolerance;
  },
  {
    message: "Complexity aggregate must equal sum of 6 factors (within 5% tolerance)",
    path: ["complexity_aggregate"],
  }
);

export type HybridQuoteFormData = z.infer<typeof hybridQuoteFormSchema>;
