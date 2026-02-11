import type {
  ChatMessageRequest,
  ChatMessageResponse,
  ChatSessionState,
} from "@/types/chat";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface ApiError {
  detail: string;
}

/**
 * Send a chat message to the backend
 *
 * @param sessionId - Session UUID for conversation tracking
 * @param message - User's natural language input
 * @param language - Language code ("fr" or "en")
 * @returns ChatMessageResponse with reply, extracted fields, suggestions, and optional quote
 * @throws Error with detail message on failure
 */
export async function sendChatMessage(
  sessionId: string,
  message: string,
  language?: string
): Promise<ChatMessageResponse> {
  const requestBody: ChatMessageRequest = {
    session_id: sessionId,
    message,
    language: language || "fr",
  };

  const response = await fetch(`${API_URL}/chat/message`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(requestBody),
  });

  if (!response.ok) {
    let errorMessage = "Failed to send chat message";
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
 * Reset a chat session, clearing all history and extracted fields
 *
 * @param sessionId - Session UUID to reset
 * @throws Error with detail message on failure
 */
export async function resetChatSession(sessionId: string): Promise<void> {
  const response = await fetch(`${API_URL}/chat/reset?session_id=${sessionId}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
  });

  if (!response.ok) {
    let errorMessage = "Failed to reset chat session";
    try {
      const errorData: ApiError = await response.json();
      errorMessage = errorData.detail || errorMessage;
    } catch {
      errorMessage = response.statusText || errorMessage;
    }
    throw new Error(errorMessage);
  }
}

/**
 * Get current session state (useful for page reload recovery)
 *
 * @param sessionId - Session UUID
 * @returns ChatSessionState or null if session doesn't exist
 * @throws Error with detail message on failure (except 404)
 */
export async function getChatSession(
  sessionId: string
): Promise<ChatSessionState | null> {
  const response = await fetch(`${API_URL}/chat/session/${sessionId}`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
  });

  if (response.status === 404) {
    return null;
  }

  if (!response.ok) {
    let errorMessage = "Failed to get chat session";
    try {
      const errorData: ApiError = await response.json();
      errorMessage = errorData.detail || errorMessage;
    } catch {
      errorMessage = response.statusText || errorMessage;
    }
    throw new Error(errorMessage);
  }

  const data = await response.json();

  return {
    sessionId: data.session_id,
    messages: data.messages,
    extractedFields: data.extracted_fields,
    sessionState: data.state,
    suggestions: [], // Backend doesn't return suggestions in session state
  };
}

/**
 * Generate a unique session ID
 *
 * @returns UUID string for session tracking
 */
export function generateSessionId(): string {
  // Use browser crypto API if available
  if (typeof crypto !== "undefined" && crypto.randomUUID) {
    return crypto.randomUUID();
  }

  // Fallback for older browsers
  return Date.now().toString(36) + Math.random().toString(36).slice(2);
}
