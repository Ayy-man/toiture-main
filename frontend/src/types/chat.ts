export interface ChatMessage {
  id: string; // UUID generated client-side
  role: "user" | "assistant";
  content: string;
  timestamp: string; // ISO timestamp
  quote?: ChatQuoteData; // Present when quote is embedded in this message
}

export interface ChatMessageRequest {
  session_id: string;
  message: string;
  language?: string; // "fr" | "en"
}

export interface ChatMessageResponse {
  reply: string;
  extracted_fields: Record<string, unknown>;
  suggestions: string[];
  quote: HybridQuoteResponseData | null;
  needs_clarification: boolean;
  session_state: string; // "greeting" | "extracting" | "clarifying" | "ready" | "generated"
}

// Reuse the existing HybridQuoteResponse type shape but as a simple interface
// to avoid import issues (the full type is in types/hybrid-quote or inlined from API response)
export interface HybridQuoteResponseData {
  work_items: Array<{ name: string; labor_hours: number; source: string }>;
  materials: Array<{
    material_id: number;
    quantity: number;
    unit_price: number;
    total: number;
  }>;
  total_labor_hours: number;
  total_materials_cost: number;
  total_price: number;
  overall_confidence: number;
  reasoning: string;
  pricing_tiers: Array<{
    tier: "Basic" | "Standard" | "Premium";
    total_price: number;
    materials_cost: number;
    labor_cost: number;
    description: string;
  }>;
  needs_review: boolean;
  processing_time_ms: number;
}

export interface ChatQuoteData {
  quote: HybridQuoteResponseData;
  selectedTier?: "Basic" | "Standard" | "Premium";
}

export interface ChatSessionState {
  sessionId: string;
  messages: ChatMessage[];
  extractedFields: Record<string, unknown>;
  sessionState: string;
  suggestions: string[];
}
