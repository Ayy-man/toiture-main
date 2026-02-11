"""LLM-powered field extraction for chat interface.

Uses GPT-4o-mini via OpenRouter to extract structured roofing job fields
from natural language input. Maps Quebec French roofing terminology to
HybridQuoteRequest schema fields.
"""

import json
import logging
import re
from typing import Any, Dict, List, Tuple

from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)
from openai import (
    APIConnectionError,
    APITimeoutError,
    AuthenticationError,
    RateLimitError,
)

from app.config import settings
from app.services.llm_reasoning import get_client

logger = logging.getLogger(__name__)

# Required fields for quote generation (category always required, sqft not for Service Call)
REQUIRED_FIELDS = ["category", "sqft"]

# Context-aware suggestion pills
SUGGESTION_MAP = {
    "greeting": ["Bardeaux", "Membrane", "TPO", "Appel de service", "Toit plat"],
    "need_sqft": ["500 pi2", "1000 pi2", "1500 pi2", "2000 pi2", "2500 pi2"],
    "need_category": ["Bardeaux", "Membrane/Elastomere", "TPO", "Service Call"],
    "need_complexity": ["Simple (Tier 1-2)", "Moyen (Tier 3-4)", "Complexe (Tier 5-6)"],
    "ready": ["Generer le devis", "Ajouter des details", "Changer la superficie"],
}

# Bilingual system prompts
EXTRACTION_SYSTEM_PROMPT_FR = """Tu es un assistant d'estimation pour Toitures LV, une compagnie de toiture au Quebec.

Ta tâche: extraire des champs structurés des descriptions en langage naturel de projets de toiture.

**MAPPING DES TERMES FRANCAIS:**
- "bardeaux" → category: "Bardeaux"
- "membrane", "elastomere" → category: "Membrane/Elastomere"
- "TPO" → category: "TPO"
- "toit plat", "flat roof" → category: "Membrane/Elastomere" ou "TPO"
- "appel de service", "service call" → category: "Service Call"
- "pente raide", "steep pitch" → factor_roof_pitch: "steep"
- "pente moyenne" → factor_roof_pitch: "medium"
- "pente faible" → factor_roof_pitch: "low"
- "toit plat" → factor_roof_pitch: "flat"

**SCHEMA DES CHAMPS (HybridQuoteRequest):**
- sqft: superficie en pieds carrés (nombre)
- category: "Bardeaux" | "Membrane/Elastomere" | "TPO" | "Service Call"
- complexity_tier: niveau de complexité 1-6 (1=simple, 6=très complexe)
- factor_roof_pitch: "flat" | "low" | "medium" | "steep" | "very_steep"
- factor_access_difficulty: liste ["no_crane", "narrow_driveway", "height_over_3_stories"]
- factor_demolition: "none" | "single_layer" | "multi_layer" | "structural"
- factor_penetrations_count: nombre de pénétrations (cheminées, évents)
- has_chimney: booléen
- has_skylights: booléen

**REPONSE JSON:**
Retourne TOUJOURS un JSON avec ces deux clés:
{
  "extracted": { ... champs extraits ... },
  "reply": "Réponse en langage naturel"
}

**REGLES:**
1. Si sqft ou category manquent, demande-les dans la réponse
2. Suggère un complexity_tier (1-6) basé sur les conditions décrites
3. Sois conversationnel et naturel dans "reply"
4. Retourne SEULEMENT le JSON, pas de markdown"""

EXTRACTION_SYSTEM_PROMPT_EN = """You are an estimation assistant for Toitures LV, a Quebec roofing company.

Your task: extract structured fields from natural language descriptions of roofing jobs.

**TERM MAPPING:**
- "shingles", "bardeaux" → category: "Bardeaux"
- "membrane", "elastomere" → category: "Membrane/Elastomere"
- "TPO" → category: "TPO"
- "flat roof" → category: "Membrane/Elastomere" or "TPO"
- "service call" → category: "Service Call"
- "steep pitch" → factor_roof_pitch: "steep"
- "medium pitch" → factor_roof_pitch: "medium"
- "low pitch" → factor_roof_pitch: "low"
- "flat roof" → factor_roof_pitch: "flat"

**FIELD SCHEMA (HybridQuoteRequest):**
- sqft: square footage (number)
- category: "Bardeaux" | "Membrane/Elastomere" | "TPO" | "Service Call"
- complexity_tier: complexity level 1-6 (1=simple, 6=very complex)
- factor_roof_pitch: "flat" | "low" | "medium" | "steep" | "very_steep"
- factor_access_difficulty: list ["no_crane", "narrow_driveway", "height_over_3_stories"]
- factor_demolition: "none" | "single_layer" | "multi_layer" | "structural"
- factor_penetrations_count: number of penetrations (chimneys, vents)
- has_chimney: boolean
- has_skylights: boolean

**JSON RESPONSE:**
ALWAYS return JSON with these two keys:
{
  "extracted": { ... extracted fields ... },
  "reply": "Natural language response"
}

**RULES:**
1. If sqft or category are missing, ask for them in the reply
2. Suggest a complexity_tier (1-6) based on described conditions
3. Be conversational and natural in "reply"
4. Return ONLY the JSON, no markdown"""


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type(
        (
            AuthenticationError,
            APITimeoutError,
            APIConnectionError,
            RateLimitError,
        )
    ),
)
async def extract_fields(
    message: str,
    conversation_history: List[Dict[str, str]],
    current_fields: Dict[str, Any],
    language: str = "fr"
) -> Dict[str, Any]:
    """Extract structured fields from natural language using LLM.

    Uses GPT-4o-mini via OpenRouter to parse user input and extract
    HybridQuoteRequest fields with Quebec French terminology mapping.

    Args:
        message: User's natural language input
        conversation_history: List of previous messages (role, content)
        current_fields: Already extracted fields from session
        language: Language code ("fr" or "en")

    Returns:
        Dict with keys:
        - extracted: Dict of newly extracted fields to merge
        - reply: Natural language response to user
        - suggestions: List of suggestion pills (handled separately)

    Raises:
        Exception: On API errors after retries exhausted
    """
    client = get_client()  # Reuse OpenRouter client

    # Select system prompt based on language
    system_prompt = (
        EXTRACTION_SYSTEM_PROMPT_FR if language == "fr"
        else EXTRACTION_SYSTEM_PROMPT_EN
    )

    # Build conversation context
    messages = [
        {"role": "system", "content": system_prompt},
    ]

    # Add conversation history (last 10 messages to stay within token limits)
    for msg in conversation_history[-10:]:
        messages.append(msg)

    # Add current message
    messages.append({"role": "user", "content": message})

    # Add context about already extracted fields
    if current_fields:
        context_msg = f"Already extracted fields: {json.dumps(current_fields, indent=2)}"
        messages.append({"role": "system", "content": context_msg})

    # Call OpenRouter
    response = client.chat.completions.create(
        model=settings.openrouter_model,  # gpt-4o-mini
        messages=messages,
        max_tokens=500,
        temperature=0.2,  # Low temperature for reliable extraction
    )

    response_text = response.choices[0].message.content.strip()

    # Parse JSON response (with regex fallback like hybrid_quote.py)
    try:
        data = _extract_json(response_text)

        # Validate structure
        if "extracted" not in data or "reply" not in data:
            raise ValueError("Response missing 'extracted' or 'reply' keys")

        return {
            "extracted": data["extracted"],
            "reply": data["reply"],
            "suggestions": []  # Will be filled by get_suggestions()
        }

    except (json.JSONDecodeError, ValueError) as e:
        logger.error(f"Failed to parse LLM extraction response: {e}")
        logger.debug(f"Response was: {response_text[:500]}")

        # Fallback: return empty extraction with helpful message
        fallback_reply = (
            "Désolé, j'ai du mal à comprendre. Pouvez-vous reformuler?"
            if language == "fr"
            else "Sorry, I'm having trouble understanding. Could you rephrase?"
        )
        return {
            "extracted": {},
            "reply": fallback_reply,
            "suggestions": []
        }


def _extract_json(text: str) -> dict:
    """Extract JSON from LLM response, handling markdown code blocks.

    Supports:
    - Raw JSON objects
    - JSON wrapped in ```json ... ``` blocks
    - JSON wrapped in ``` ... ``` blocks

    Args:
        text: LLM response text

    Returns:
        Parsed JSON dict

    Raises:
        ValueError: If no valid JSON found
    """
    # Try to find JSON in code blocks first
    code_block_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if code_block_match:
        return json.loads(code_block_match.group(1))

    # Try to find raw JSON object
    json_match = re.search(r"\{.*\}", text, re.DOTALL)
    if json_match:
        return json.loads(json_match.group(0))

    raise ValueError(f"No valid JSON found in response: {text[:200]}")


def check_readiness(extracted_fields: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Check if minimum required fields are present for quote generation.

    Args:
        extracted_fields: Currently extracted fields from session

    Returns:
        Tuple of (is_ready: bool, missing_fields: List[str])
    """
    missing = []

    # Category is always required
    if "category" not in extracted_fields or not extracted_fields["category"]:
        missing.append("category")

    # Sqft required for all categories except Service Call
    category = extracted_fields.get("category", "")
    if category != "Service Call":
        if "sqft" not in extracted_fields or not extracted_fields["sqft"]:
            missing.append("sqft")

    is_ready = len(missing) == 0

    return is_ready, missing


def get_suggestions(
    state: str,
    extracted_fields: Dict[str, Any],
    language: str
) -> List[str]:
    """Get context-aware suggestion pills based on current state.

    Args:
        state: Current conversation state
        extracted_fields: Currently extracted fields
        language: Language code ("fr" or "en")

    Returns:
        List of 3-5 suggestion strings
    """
    # Determine what's needed
    category = extracted_fields.get("category")
    sqft = extracted_fields.get("sqft")
    complexity_tier = extracted_fields.get("complexity_tier")

    # English variants for suggestion map
    SUGGESTION_MAP_EN = {
        "greeting": ["Shingles", "Membrane", "TPO", "Service Call", "Flat Roof"],
        "need_sqft": ["500 sqft", "1000 sqft", "1500 sqft", "2000 sqft", "2500 sqft"],
        "need_category": ["Shingles", "Membrane/Elastomere", "TPO", "Service Call"],
        "need_complexity": ["Simple (Tier 1-2)", "Medium (Tier 3-4)", "Complex (Tier 5-6)"],
        "ready": ["Generate quote", "Add more details", "Change area"],
    }

    suggestion_source = SUGGESTION_MAP if language == "fr" else SUGGESTION_MAP_EN

    # State-based suggestions
    if state == "greeting":
        return suggestion_source["greeting"]
    elif not category:
        return suggestion_source["need_category"]
    elif not sqft and category != "Service Call":
        return suggestion_source["need_sqft"]
    elif not complexity_tier:
        return suggestion_source["need_complexity"]
    elif state == "ready":
        return suggestion_source["ready"]
    else:
        # Default extracting state
        return suggestion_source["need_complexity"]
