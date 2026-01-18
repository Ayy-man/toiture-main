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

/**
 * SSE event types from streaming endpoint
 */
interface StreamEstimateEvent {
  type: "estimate" | "reasoning_chunk" | "done" | "error";
  data: unknown;
}

/**
 * Callbacks for streaming estimate events
 */
export interface StreamCallbacks {
  onEstimate: (data: Omit<EstimateResponse, "reasoning">) => void;
  onReasoningChunk: (chunk: string) => void;
  onDone: (reasoning: string | null) => void;
  onError: (error: string) => void;
}

/**
 * Submit estimate request with streaming response
 *
 * Returns estimate data immediately, then streams reasoning chunks
 */
export async function submitEstimateStream(
  data: EstimateFormData,
  callbacks: StreamCallbacks
): Promise<void> {
  const response = await fetch(`${API_URL}/estimate/stream`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      sqft: data.sqft,
      category: data.category,
      material_lines: data.material_lines,
      labor_lines: data.labor_lines,
      has_subs: data.has_subs ? 1 : 0,
      complexity: data.complexity,
    }),
  });

  if (!response.ok) {
    let errorMessage = "Failed to get estimate";
    try {
      const errorData: ApiError = await response.json();
      errorMessage = errorData.detail || errorMessage;
    } catch {
      errorMessage = response.statusText || errorMessage;
    }
    throw new Error(errorMessage);
  }

  const reader = response.body?.getReader();
  if (!reader) {
    throw new Error("No response body");
  }

  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n\n");
    buffer = lines.pop() || "";

    for (const line of lines) {
      if (line.startsWith("data: ")) {
        try {
          const event: StreamEstimateEvent = JSON.parse(line.slice(6));

          switch (event.type) {
            case "estimate":
              callbacks.onEstimate(event.data as Omit<EstimateResponse, "reasoning">);
              break;
            case "reasoning_chunk":
              callbacks.onReasoningChunk(event.data as string);
              break;
            case "done":
              callbacks.onDone((event.data as { reasoning: string | null }).reasoning);
              break;
            case "error":
              callbacks.onError(event.data as string);
              break;
          }
        } catch {
          // Ignore parse errors for incomplete chunks
        }
      }
    }
  }
}
