import type {
  PendingEstimate,
  EstimateDetail,
  SubmitFeedbackRequest,
} from "@/types/feedback";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

/**
 * API error response structure
 */
interface ApiError {
  detail: string;
}

/**
 * Fetch all pending (unreviewed) estimates
 *
 * @returns Array of pending estimates
 * @throws Error with detail message on failure
 */
export async function fetchPendingEstimates(): Promise<PendingEstimate[]> {
  const response = await fetch(`${API_URL}/feedback/pending`);

  if (!response.ok) {
    let errorMessage = "Failed to fetch pending estimates";
    try {
      const errorData: ApiError = await response.json();
      errorMessage = errorData.detail || errorMessage;
    } catch {
      errorMessage = response.statusText || errorMessage;
    }
    throw new Error(errorMessage);
  }

  return response.json();
}

/**
 * Fetch detailed information for a specific estimate
 *
 * @param id - Estimate UUID
 * @returns Full estimate details including inputs, AI output, and reasoning
 * @throws Error with detail message on failure
 */
export async function fetchEstimateDetail(id: string): Promise<EstimateDetail> {
  const response = await fetch(`${API_URL}/feedback/estimate/${id}`);

  if (!response.ok) {
    let errorMessage = "Failed to fetch estimate details";
    try {
      const errorData: ApiError = await response.json();
      errorMessage = errorData.detail || errorMessage;
    } catch {
      errorMessage = response.statusText || errorMessage;
    }
    throw new Error(errorMessage);
  }

  return response.json();
}

/**
 * Submit feedback for an estimate
 *
 * @param request - Contains estimate_id and laurent_price
 * @throws Error with detail message on failure
 */
export async function submitFeedback(
  request: SubmitFeedbackRequest
): Promise<void> {
  const response = await fetch(`${API_URL}/feedback/submit`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    let errorMessage = "Failed to submit feedback";
    try {
      const errorData: ApiError = await response.json();
      errorMessage = errorData.detail || errorMessage;
    } catch {
      errorMessage = response.statusText || errorMessage;
    }
    throw new Error(errorMessage);
  }
}
