import { z } from "zod";

/**
 * Allowed roofing job categories
 * Note: "Elastomere" (without accent) is used for frontend simplicity
 * Backend normalizes to "Elastomere" via field_validator
 */
export const CATEGORIES = [
  "Bardeaux",
  "Elastomere",
  "Other",
  "Gutters",
  "Heat Cables",
  "Insulation",
  "Service Call",
  "Skylights",
  "Unknown",
  "Ventilation",
] as const;

export type Category = (typeof CATEGORIES)[number];

/**
 * Zod schema for estimate form validation
 * Mirrors backend Pydantic validation rules in backend/app/schemas/estimate.py
 * Note: Uses z.number() directly - form handles string-to-number conversion
 */
export const estimateFormSchema = z.object({
  sqft: z
    .number()
    .min(0, "Square footage cannot be negative")
    .max(100000, "Square footage cannot exceed 100,000")
    .optional(),
  category: z.enum(CATEGORIES, {
    message: "Invalid category",
  }),
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
  has_subs: z.boolean(),
  complexity: z
    .number()
    .int("Complexity must be a whole number")
    .min(1, "Complexity must be at least 1")
    .max(100, "Complexity cannot exceed 100"),
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

export type EstimateFormData = z.infer<typeof estimateFormSchema>;
