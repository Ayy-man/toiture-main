/**
 * Re-exports for cleaner imports
 *
 * Usage:
 * import { EstimateFormData, EstimateResponse, CATEGORIES } from "@/types/estimate";
 */

// Schema exports
export {
  CATEGORIES,
  estimateFormSchema,
  type Category,
  type EstimateFormData,
} from "@/lib/schemas";

// API exports
export { submitEstimate, type EstimateResponse, type SimilarCase } from "@/lib/api";
