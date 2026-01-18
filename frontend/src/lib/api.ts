import type { EstimateFormData } from "./schemas";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

/**
 * A similar historical case from CBR
 * Matches backend/app/schemas/estimate.py SimilarCase
 */
export interface SimilarCase {
  case_id: string;
  similarity: number;
  category: string | null;
  sqft: number | null;
  total: number | null;
  per_sqft: number | null;
  year: number | null;
}

/**
 * Response from /estimate endpoint
 * Matches backend/app/schemas/estimate.py EstimateResponse
 */
export interface EstimateResponse {
  estimate: number;
  range_low: number;
  range_high: number;
  confidence: "HIGH" | "MEDIUM" | "LOW";
  model: string;
  similar_cases: SimilarCase[];
  reasoning: string | null;
}

/**
 * API error response structure
 */
interface ApiError {
  detail: string;
}

/**
 * Submit estimate request to backend
 *
 * Converts frontend form data to backend API format:
 * - has_subs: boolean -> 0/1 (backend expects Literal[0, 1])
 *
 * @param data - Validated form data from estimateFormSchema
 * @returns EstimateResponse with prediction and similar cases
 * @throws Error with detail message on failure
 */
export async function submitEstimate(
  data: EstimateFormData
): Promise<EstimateResponse> {
  const response = await fetch(`${API_URL}/estimate`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      sqft: data.sqft,
      category: data.category,
      material_lines: data.material_lines,
      labor_lines: data.labor_lines,
      has_subs: data.has_subs ? 1 : 0, // Convert boolean to 0/1 for backend
      complexity: data.complexity,
    }),
  });

  if (!response.ok) {
    let errorMessage = "Failed to get estimate";
    try {
      const errorData: ApiError = await response.json();
      errorMessage = errorData.detail || errorMessage;
    } catch {
      // If response isn't JSON, use status text
      errorMessage = response.statusText || errorMessage;
    }
    throw new Error(errorMessage);
  }

  return response.json();
}
