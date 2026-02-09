import type {
  Submission,
  SubmissionListItem,
  SubmissionCreatePayload,
  UpsellSuggestion,
} from "@/types/submission";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface ApiError {
  detail: string;
}

/**
 * Create a new submission
 *
 * @param data - Submission creation payload
 * @param userName - Optional username for audit trail (defaults to "estimateur")
 * @returns Created submission
 * @throws Error with detail message on failure
 */
export async function createSubmission(
  data: SubmissionCreatePayload,
  userName?: string
): Promise<Submission> {
  const response = await fetch(`${API_URL}/submissions`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-User-Name": userName || "estimateur",
      "X-User-Role": "estimator",
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    let errorMessage = "Failed to create submission";
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
 * Get a single submission by ID
 *
 * @param id - Submission UUID
 * @returns Full submission with children
 * @throws Error with detail message on failure
 */
export async function getSubmission(id: string): Promise<Submission> {
  const response = await fetch(`${API_URL}/submissions/${id}`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
  });

  if (!response.ok) {
    let errorMessage = "Failed to fetch submission";
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
 * List submissions with optional filters
 *
 * @param params - Optional query parameters (status, limit, offset)
 * @returns Array of submission list items
 * @throws Error with detail message on failure
 */
export async function listSubmissions(params?: {
  status?: string;
  limit?: number;
  offset?: number;
}): Promise<SubmissionListItem[]> {
  const queryParams = new URLSearchParams();
  if (params?.status) queryParams.append("status", params.status);
  if (params?.limit) queryParams.append("limit", params.limit.toString());
  if (params?.offset) queryParams.append("offset", params.offset.toString());

  const url = `${API_URL}/submissions${queryParams.toString() ? `?${queryParams.toString()}` : ""}`;

  const response = await fetch(url, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
  });

  if (!response.ok) {
    let errorMessage = "Failed to list submissions";
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
 * Update a draft submission
 *
 * @param id - Submission UUID
 * @param data - Fields to update (line_items, selected_tier, client_name)
 * @param userName - Optional username for audit trail
 * @returns Updated submission
 * @throws Error with detail message on failure
 */
export async function updateSubmission(
  id: string,
  data: {
    line_items?: Omit<import("@/types/submission").LineItem, "id">[];
    selected_tier?: "Basic" | "Standard" | "Premium";
    client_name?: string;
  },
  userName?: string
): Promise<Submission> {
  const response = await fetch(`${API_URL}/submissions/${id}`, {
    method: "PATCH",
    headers: {
      "Content-Type": "application/json",
      "X-User-Name": userName || "estimateur",
      "X-User-Role": "estimator",
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    let errorMessage = "Failed to update submission";
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
 * Finalize a submission (draft -> pending_approval)
 *
 * @param id - Submission UUID
 * @param userName - Optional username for audit trail
 * @returns Updated submission
 * @throws Error with detail message on failure
 */
export async function finalizeSubmission(
  id: string,
  userName?: string
): Promise<Submission> {
  const response = await fetch(`${API_URL}/submissions/${id}/finalize`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-User-Name": userName || "estimateur",
      "X-User-Role": "estimator",
    },
  });

  if (!response.ok) {
    let errorMessage = "Failed to finalize submission";
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
 * Approve a submission (pending_approval -> approved, admin only)
 *
 * @param id - Submission UUID
 * @param userName - Optional username for audit trail
 * @param userRole - Optional user role (defaults to "admin")
 * @returns Updated submission
 * @throws Error with detail message on failure (403 if not admin)
 */
export async function approveSubmission(
  id: string,
  userName?: string,
  userRole?: string
): Promise<Submission> {
  const response = await fetch(`${API_URL}/submissions/${id}/approve`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-User-Name": userName || "estimateur",
      "X-User-Role": userRole || "admin",
    },
  });

  if (!response.ok) {
    let errorMessage = "Failed to approve submission";
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
 * Reject a submission (pending_approval -> rejected, admin only)
 *
 * @param id - Submission UUID
 * @param reason - Optional rejection reason
 * @param userName - Optional username for audit trail
 * @param userRole - Optional user role (defaults to "admin")
 * @returns Updated submission
 * @throws Error with detail message on failure (403 if not admin)
 */
export async function rejectSubmission(
  id: string,
  reason?: string,
  userName?: string,
  userRole?: string
): Promise<Submission> {
  const response = await fetch(`${API_URL}/submissions/${id}/reject`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-User-Name": userName || "estimateur",
      "X-User-Role": userRole || "admin",
    },
    body: JSON.stringify({ reason }),
  });

  if (!response.ok) {
    let errorMessage = "Failed to reject submission";
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
 * Return submission to draft (rejected|pending_approval -> draft)
 *
 * @param id - Submission UUID
 * @param userName - Optional username for audit trail
 * @returns Updated submission
 * @throws Error with detail message on failure
 */
export async function returnToDraft(
  id: string,
  userName?: string
): Promise<Submission> {
  const response = await fetch(`${API_URL}/submissions/${id}/return-to-draft`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-User-Name": userName || "estimateur",
      "X-User-Role": "estimator",
    },
  });

  if (!response.ok) {
    let errorMessage = "Failed to return submission to draft";
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
 * Add a note to a submission
 *
 * @param id - Submission UUID
 * @param text - Note text
 * @param userName - Username for attribution
 * @returns Updated submission
 * @throws Error with detail message on failure
 */
export async function addNote(
  id: string,
  text: string,
  userName: string
): Promise<Submission> {
  const response = await fetch(`${API_URL}/submissions/${id}/notes`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-User-Name": userName,
      "X-User-Role": "estimator",
    },
    body: JSON.stringify({
      text,
      created_by: userName,
    }),
  });

  if (!response.ok) {
    let errorMessage = "Failed to add note";
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
 * Create an upsell child submission
 *
 * @param parentId - Parent submission UUID
 * @param upsellType - Type of upsell (e.g., "heating_cables")
 * @param userName - Optional username for audit trail
 * @returns Created upsell submission
 * @throws Error with detail message on failure
 */
export async function createUpsell(
  parentId: string,
  upsellType: string,
  userName?: string
): Promise<Submission> {
  const response = await fetch(`${API_URL}/submissions/${parentId}/upsells`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-User-Name": userName || "estimateur",
      "X-User-Role": "estimator",
    },
    body: JSON.stringify({ upsell_type: upsellType }),
  });

  if (!response.ok) {
    let errorMessage = "Failed to create upsell";
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
 * Get upsell suggestions for a submission
 *
 * @param id - Submission UUID
 * @returns Array of bilingual upsell suggestions
 * @throws Error with detail message on failure
 */
export async function getUpsellSuggestions(id: string): Promise<UpsellSuggestion[]> {
  const response = await fetch(`${API_URL}/submissions/${id}/upsell-suggestions`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
  });

  if (!response.ok) {
    let errorMessage = "Failed to fetch upsell suggestions";
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
