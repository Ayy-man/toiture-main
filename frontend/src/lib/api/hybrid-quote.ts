import type { HybridQuoteRequest, HybridQuoteResponse } from "@/types/hybrid-quote";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface ApiError {
  detail: string;
}

/**
 * Submit hybrid quote request to backend
 *
 * @param data - Validated form data matching HybridQuoteRequest
 * @returns HybridQuoteResponse with work items, materials, pricing tiers
 * @throws Error with detail message on failure
 */
export async function submitHybridQuote(
  data: HybridQuoteRequest
): Promise<HybridQuoteResponse> {
  const response = await fetch(`${API_URL}/estimate/hybrid`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    let errorMessage = "Failed to generate quote";
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
