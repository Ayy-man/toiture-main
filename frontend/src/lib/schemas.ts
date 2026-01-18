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
 */
export const estimateFormSchema = z.object({
  sqft: z.coerce
    .number()
    .positive("Square footage must be positive")
    .max(100000, "Square footage cannot exceed 100,000"),
  category: z.enum(CATEGORIES, {
    message: "Invalid category",
  }),
  material_lines: z.coerce
    .number()
    .int("Material lines must be a whole number")
    .min(0, "Material lines cannot be negative")
    .max(100, "Material lines cannot exceed 100")
    .default(5),
  labor_lines: z.coerce
    .number()
    .int("Labor lines must be a whole number")
    .min(0, "Labor lines cannot be negative")
    .max(50, "Labor lines cannot exceed 50")
    .default(2),
  has_subs: z.boolean().default(false),
  complexity: z.coerce
    .number()
    .int("Complexity must be a whole number")
    .min(1, "Complexity must be at least 1")
    .max(100, "Complexity cannot exceed 100")
    .default(10),
});

export type EstimateFormData = z.infer<typeof estimateFormSchema>;
