"""Chat API router for conversational quote generation.

Provides endpoints for natural language roofing job descriptions
that are converted to structured quotes via LLM field extraction.
"""

import logging
from typing import Any, Dict

from fastapi import APIRouter, HTTPException

from app.schemas.chat import ChatMessageRequest, ChatMessageResponse
from app.schemas.hybrid_quote import HybridQuoteRequest
from app.services.chat_extraction import (
    check_readiness,
    extract_fields,
    get_suggestions,
)
from app.services.chat_session import (
    clear_session,
    get_session,
    update_session,
)
from app.services.hybrid_quote import generate_hybrid_quote

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])


# Greeting detection keywords
GREETING_KEYWORDS_FR = ["bonjour", "salut", "allo", "hi", "hello", "hey"]
GREETING_KEYWORDS_EN = ["hi", "hello", "hey", "greetings"]


def _is_greeting(message: str, language: str = "fr") -> bool:
    """Check if message is a greeting-like input.

    Args:
        message: User message text
        language: Language code

    Returns:
        True if message is empty or contains only greeting keywords
    """
    msg_lower = message.lower().strip()

    # Empty or very short messages
    if len(msg_lower) < 3:
        return True

    # Check for greeting keywords
    keywords = GREETING_KEYWORDS_FR if language == "fr" else GREETING_KEYWORDS_EN
    return any(keyword in msg_lower for keyword in keywords)


def _build_greeting_message(language: str = "fr") -> str:
    """Build bilingual greeting message.

    Args:
        language: Language code ("fr" or "en")

    Returns:
        Greeting message string
    """
    if language == "fr":
        return (
            "Bonjour! Decrivez le projet de toiture et je vais preparer le devis. "
            "Par exemple: '1200 pi2, bardeaux, pente raide, acces difficile'"
        )
    else:
        return (
            "Hi! Describe the roofing job and I'll build the quote. "
            "For example: '1200 sqft, shingles, steep pitch, difficult access'"
        )


def _user_wants_quote(message: str, language: str = "fr") -> bool:
    """Check if user explicitly asked to generate the quote.

    Args:
        message: User message text
        language: Language code

    Returns:
        True if message contains quote generation keywords
    """
    msg_lower = message.lower().strip()

    if language == "fr":
        keywords = ["generer", "générer", "devis", "oui", "yes", "go", "ok", "parfait"]
    else:
        keywords = ["generate", "quote", "yes", "go", "ok", "perfect", "ready"]

    return any(keyword in msg_lower for keyword in keywords)


async def _map_to_hybrid_quote_request(fields: Dict[str, Any]) -> Dict[str, Any]:
    """Map extracted chat fields to HybridQuoteRequest format.

    Args:
        fields: Extracted fields from chat session

    Returns:
        Dict suitable for HybridQuoteRequest validation
    """
    # Start with extracted fields
    request_dict = fields.copy()

    # Add defaults for optional fields if not present
    if "material_lines" not in request_dict:
        request_dict["material_lines"] = 5
    if "labor_lines" not in request_dict:
        request_dict["labor_lines"] = 2
    if "has_subs" not in request_dict:
        request_dict["has_subs"] = False
    if "has_chimney" not in request_dict:
        request_dict["has_chimney"] = False
    if "has_skylights" not in request_dict:
        request_dict["has_skylights"] = False

    return request_dict


@router.post("/message", response_model=ChatMessageResponse)
async def send_message(request: ChatMessageRequest):
    """Send a chat message and receive assistant response.

    Handles natural language input, extracts fields, manages conversation state,
    and auto-generates quotes when ready.

    Args:
        request: ChatMessageRequest with session_id, message, language

    Returns:
        ChatMessageResponse with reply, extracted fields, suggestions, and optional quote
    """
    try:
        # Get or create session
        session = get_session(request.session_id)

        # Update session language if provided
        if request.language:
            session["language"] = request.language

        language = session.get("language", "fr")
        state = session.get("state", "greeting")
        messages = session.get("messages", [])
        extracted_fields = session.get("extracted_fields", {})

        # Check if this is the first message and it's a greeting
        is_first_message = len(messages) == 0
        is_greeting_input = _is_greeting(request.message, language)

        # Handle greeting state
        if state == "greeting" and is_first_message and is_greeting_input:
            # Send greeting and move to extracting state
            greeting_reply = _build_greeting_message(language)

            # Append greeting to conversation
            messages.append({"role": "user", "content": request.message})
            messages.append({"role": "assistant", "content": greeting_reply})

            # Update session
            new_state = "extracting"
            update_session(request.session_id, messages, extracted_fields, new_state)

            # Get suggestions
            suggestions = get_suggestions(new_state, extracted_fields, language)

            return ChatMessageResponse(
                reply=greeting_reply,
                extracted_fields=extracted_fields,
                suggestions=suggestions,
                quote=None,
                needs_clarification=True,
                session_state=new_state
            )

        # Normal extraction flow: append user message
        messages.append({"role": "user", "content": request.message})

        # Extract fields from message
        try:
            extraction_result = await extract_fields(
                message=request.message,
                conversation_history=messages[:-1],  # Exclude current message
                current_fields=extracted_fields,
                language=language
            )

            newly_extracted = extraction_result["extracted"]
            llm_reply = extraction_result["reply"]

            # Merge newly extracted fields (new values overwrite old)
            extracted_fields.update(newly_extracted)

            logger.info(f"Extracted fields: {newly_extracted}")
            logger.info(f"Merged fields: {extracted_fields}")

        except Exception as e:
            logger.error(f"LLM extraction failed: {e}")
            # Fallback: return helpful error message
            fallback_reply = (
                "Je rencontre un problème technique. Pouvez-vous réessayer?"
                if language == "fr"
                else "I'm having technical difficulties. Could you try again?"
            )

            messages.append({"role": "assistant", "content": fallback_reply})
            update_session(request.session_id, messages, extracted_fields, state)

            return ChatMessageResponse(
                reply=fallback_reply,
                extracted_fields=extracted_fields,
                suggestions=get_suggestions(state, extracted_fields, language),
                quote=None,
                needs_clarification=True,
                session_state=state
            )

        # Check readiness for quote generation
        is_ready, missing_fields = check_readiness(extracted_fields)

        # Determine if user wants to generate quote now
        user_wants_quote = _user_wants_quote(request.message, language)

        # Quote generation logic
        quote = None
        new_state = state

        if is_ready and user_wants_quote:
            # Generate quote
            try:
                request_dict = await _map_to_hybrid_quote_request(extracted_fields)
                quote_request = HybridQuoteRequest(**request_dict)
                quote = await generate_hybrid_quote(quote_request)

                new_state = "generated"

                # Update reply to confirm quote generation
                if language == "fr":
                    llm_reply = f"Parfait! Voici votre devis pour {extracted_fields.get('sqft', 0):.0f} pi2 de {extracted_fields.get('category', 'toiture')}."
                else:
                    llm_reply = f"Perfect! Here's your quote for {extracted_fields.get('sqft', 0):.0f} sqft of {extracted_fields.get('category', 'roofing')}."

                logger.info(f"Generated quote for session {request.session_id}")

            except Exception as e:
                logger.error(f"Quote generation failed: {e}")
                # Return error but keep extracted fields
                if language == "fr":
                    llm_reply += f" Erreur lors de la génération du devis: {str(e)}"
                else:
                    llm_reply += f" Error generating quote: {str(e)}"

                new_state = "ready"  # Stay in ready state

        elif is_ready and not user_wants_quote:
            # Ready but user hasn't asked to generate yet
            new_state = "ready"

            # Summarize extracted fields and ask if ready
            if language == "fr":
                summary = f"J'ai noté: {extracted_fields.get('sqft', 0):.0f} pi2, {extracted_fields.get('category', 'toiture')}"
                if extracted_fields.get('complexity_tier'):
                    summary += f", complexité tier {extracted_fields['complexity_tier']}"
                llm_reply = f"{summary}. Prêt à générer le devis?"
            else:
                summary = f"I have: {extracted_fields.get('sqft', 0):.0f} sqft, {extracted_fields.get('category', 'roofing')}"
                if extracted_fields.get('complexity_tier'):
                    summary += f", complexity tier {extracted_fields['complexity_tier']}"
                llm_reply = f"{summary}. Ready to generate the quote?"

        else:
            # Not ready yet - determine state
            if not extracted_fields.get("category"):
                new_state = "clarifying"
            elif not extracted_fields.get("sqft") and extracted_fields.get("category") != "Service Call":
                new_state = "clarifying"
            else:
                new_state = "extracting"

        # Append assistant reply to messages
        messages.append({"role": "assistant", "content": llm_reply})

        # Update session
        update_session(request.session_id, messages, extracted_fields, new_state)

        # Get context-aware suggestions
        suggestions = get_suggestions(new_state, extracted_fields, language)

        return ChatMessageResponse(
            reply=llm_reply,
            extracted_fields=extracted_fields,
            suggestions=suggestions,
            quote=quote,
            needs_clarification=not is_ready,
            session_state=new_state
        )

    except Exception as e:
        logger.error(f"Unexpected error in chat endpoint: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/reset")
async def reset_session(session_id: str):
    """Reset a chat session, clearing all history and extracted fields.

    Args:
        session_id: Session identifier to reset

    Returns:
        Status message
    """
    clear_session(session_id)
    return {"status": "ok", "message": "Session reset"}


@router.get("/session/{session_id}")
async def get_session_state(session_id: str):
    """Get current session state.

    Useful for page reload recovery.

    Args:
        session_id: Session identifier

    Returns:
        Session data (messages, extracted_fields, state)

    Raises:
        HTTPException: 404 if session doesn't exist
    """
    from app.services.chat_session import _sessions

    if session_id not in _sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    session = _sessions[session_id]

    return {
        "session_id": session_id,
        "messages": session.get("messages", []),
        "extracted_fields": session.get("extracted_fields", {}),
        "state": session.get("state", "greeting"),
        "language": session.get("language", "fr")
    }
