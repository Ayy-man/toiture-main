"""Pydantic models for AI chat interface.

Defines request/response schemas for conversational roofing quote generation.
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ChatMessageRequest(BaseModel):
    """Request model for sending a chat message.

    Accepts natural language input and maintains conversation state
    across multiple messages via session_id.
    """

    session_id: str = Field(
        description="UUID for conversation tracking (client-generated)"
    )
    message: str = Field(
        min_length=1,
        max_length=2000,
        description="User's natural language input"
    )
    language: Optional[str] = Field(
        default="fr",
        description="Language code for bilingual responses (fr or en)"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "session_id": "550e8400-e29b-41d4-a716-446655440000",
                    "message": "1200 pi2, bardeaux, pente raide",
                    "language": "fr"
                }
            ]
        }
    }


class ChatMessageResponse(BaseModel):
    """Response model for chat message.

    Returns assistant's reply, extracted fields, suggestions,
    and optionally a generated quote when ready.
    """

    reply: str = Field(
        description="Assistant's natural language response"
    )
    extracted_fields: Dict[str, Any] = Field(
        description="Current cumulative extracted fields merged from all messages"
    )
    suggestions: List[str] = Field(
        description="Quick-reply suggestion pills (3-5 context-aware options)"
    )
    quote: Optional[Any] = Field(
        default=None,
        description="HybridQuoteResponse when quote is generated (Any to avoid circular import)"
    )
    needs_clarification: bool = Field(
        description="True if critical fields are still missing"
    )
    session_state: str = Field(
        description="Current conversation state: greeting | extracting | clarifying | ready | generated"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "reply": "Parfait! J'ai note 1200 pi2 de bardeaux avec pente raide. Quel est le niveau de complexite?",
                    "extracted_fields": {
                        "sqft": 1200,
                        "category": "Bardeaux",
                        "factor_roof_pitch": "steep"
                    },
                    "suggestions": [
                        "Simple (Tier 1-2)",
                        "Moyen (Tier 3-4)",
                        "Complexe (Tier 5-6)"
                    ],
                    "quote": None,
                    "needs_clarification": True,
                    "session_state": "extracting"
                }
            ]
        }
    }


class ChatSession(BaseModel):
    """Session model for conversation state tracking.

    Maintains conversation history, extracted fields, and state
    for in-memory session store.
    """

    session_id: str = Field(
        description="Session identifier"
    )
    messages: List[Dict[str, str]] = Field(
        description="Conversation history as [{'role': 'user'|'assistant', 'content': '...'}]"
    )
    extracted_fields: Dict[str, Any] = Field(
        description="Accumulated extracted fields from all messages"
    )
    state: str = Field(
        description="Current state in conversation flow"
    )
    created_at: str = Field(
        description="ISO timestamp of session creation"
    )
    language: str = Field(
        description="Session language (fr or en)"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "session_id": "550e8400-e29b-41d4-a716-446655440000",
                    "messages": [
                        {"role": "user", "content": "1200 pi2 bardeaux"},
                        {"role": "assistant", "content": "Parfait! Quel est le niveau de complexite?"}
                    ],
                    "extracted_fields": {
                        "sqft": 1200,
                        "category": "Bardeaux"
                    },
                    "state": "extracting",
                    "created_at": "2026-02-12T00:00:00Z",
                    "language": "fr"
                }
            ]
        }
    }
