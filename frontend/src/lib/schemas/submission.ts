import { z } from "zod";

/**
 * Zod schema for line item form validation
 */
export const lineItemSchema = z.object({
  id: z.string(),
  type: z.enum(["material", "labor"]),
  material_id: z.number().nullable().optional(),
  name: z.string().min(1, "Name required"),
  quantity: z.number().positive("Must be positive"),
  unit_price: z.number().nonnegative("Must be non-negative"),
  total: z.number().nonnegative(),
  order: z.number().int().nonnegative(),
});

/**
 * Zod schema for submission form validation
 */
export const submissionFormSchema = z.object({
  lineItems: z.array(lineItemSchema).min(1, "At least one line item required"),
  client_name: z.string().optional(),
  selected_tier: z.enum(["Basic", "Standard", "Premium"]).default("Standard"),
});

export type LineItemFormData = z.infer<typeof lineItemSchema>;
export type SubmissionFormData = z.infer<typeof submissionFormSchema>;
