"""LLM reasoning generation using OpenRouter.

Generates human-readable explanations for price estimates by referencing
similar historical cases and explaining confidence levels.
"""

import logging
from typing import Any, Optional

from openai import (
    APIConnectionError,
    APITimeoutError,
    AuthenticationError,
    OpenAI,
    RateLimitError,
)
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from app.config import settings

logger = logging.getLogger(__name__)

# Module-level client storage (same pattern as predictor.py, pinecone_cbr.py)
_client: Optional[OpenAI] = None


def init_llm_client() -> None:
    """Initialize OpenRouter client. Called from lifespan."""
    global _client
    logger.info("Initializing OpenRouter LLM client...")
    _client = OpenAI(
        base_url=settings.openrouter_base_url,
        api_key=settings.openrouter_api_key,
        timeout=30.0,
        default_headers={
            "HTTP-Referer": settings.app_url,
            "X-Title": "TOITURELV Cortex",
        },
    )
    logger.info("OpenRouter client initialized")


def close_llm_client() -> None:
    """Cleanup on shutdown."""
    global _client
    _client = None
    logger.info("OpenRouter client closed")


def get_client() -> OpenAI:
    """Get the OpenRouter client for operations.

    Raises:
        RuntimeError: If client not initialized via init_llm_client()
    """
    if _client is None:
        raise RuntimeError("LLM client not initialized. Call init_llm_client() first.")
    return _client


def format_similar_cases(cases: list[dict[str, Any]]) -> str:
    """Format similar cases for prompt inclusion.

    Args:
        cases: List of similar cases from CBR (max 5 used)

    Returns:
        Formatted string for LLM prompt
    """
    if not cases:
        return "No similar historical cases found."

    lines = []
    for i, case in enumerate(cases[:5], 1):  # Limit to 5 cases
        total = case.get("total")
        sqft = case.get("sqft")
        per_sqft = case.get("per_sqft")
        category = case.get("category", "Unknown")
        similarity = case.get("similarity", 0)
        year = case.get("year", "N/A")

        parts = [f"{i}. {category} ({year})"]
        if total:
            parts.append(f"${total:,.0f}")
        if sqft:
            parts.append(f"{sqft:,.0f} sqft")
        if per_sqft:
            parts.append(f"${per_sqft:.2f}/sqft")
        parts.append(f"{similarity:.0%} similar")

        lines.append(", ".join(parts))

    return "\n".join(lines)


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type(
        (
            AuthenticationError,  # OpenRouter can have transient 401s
            APITimeoutError,
            APIConnectionError,
            RateLimitError,
        )
    ),
)
def generate_reasoning(
    estimate: float,
    confidence: str,
    sqft: float,
    category: str,
    similar_cases: list[dict[str, Any]],
    model: Optional[str] = None,
) -> str:
    """Generate reasoning explanation for estimate.

    Args:
        estimate: Predicted price
        confidence: Confidence level (HIGH/MEDIUM/LOW)
        sqft: Square footage
        category: Job category
        similar_cases: List of similar historical cases from CBR
        model: OpenRouter model identifier (optional, uses default)

    Returns:
        Human-readable reasoning string (2-3 sentences)

    Raises:
        Exception: On API errors after retries exhausted
    """
    client = get_client()
    model = model or settings.openrouter_model

    cases_text = format_similar_cases(similar_cases)

    # Build confidence context
    if confidence == "HIGH":
        confidence_context = "The model has high confidence in this estimate."
    elif confidence == "MEDIUM":
        confidence_context = (
            "The model has moderate confidence. Some variation is expected."
        )
    else:
        confidence_context = (
            "The model has low confidence due to limited similar data or high variance."
        )

    prompt = f"""Based on the ML estimate and similar historical roofing jobs, explain this estimate in 2-3 sentences.

Job: {category}, {sqft:,.0f} sq ft
Estimate: ${estimate:,.2f}
Confidence: {confidence}
{confidence_context}

Similar Jobs:
{cases_text}

Write a brief, professional explanation referencing the similar jobs. Explain why the estimate is reasonable or note any factors affecting confidence."""

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "You are a roofing estimation assistant. Be concise, professional, and reference specific data from similar jobs.",
            },
            {"role": "user", "content": prompt},
        ],
        max_tokens=150,
        temperature=0.3,
    )

    return response.choices[0].message.content.strip()


def generate_reasoning_stream(
    estimate: float,
    confidence: str,
    sqft: float,
    category: str,
    similar_cases: list[dict[str, Any]],
    model: Optional[str] = None,
):
    """Generate reasoning explanation with streaming.

    Yields chunks of text as they arrive from the LLM.
    """
    client = get_client()
    model = model or settings.openrouter_model

    cases_text = format_similar_cases(similar_cases)

    if confidence == "HIGH":
        confidence_context = "The model has high confidence in this estimate."
    elif confidence == "MEDIUM":
        confidence_context = "The model has moderate confidence. Some variation is expected."
    else:
        confidence_context = "The model has low confidence due to limited similar data or high variance."

    prompt = f"""Based on the ML estimate and similar historical roofing jobs, explain this estimate in 2-3 sentences.

Job: {category}, {sqft:,.0f} sq ft
Estimate: ${estimate:,.2f}
Confidence: {confidence}
{confidence_context}

Similar Jobs:
{cases_text}

Write a brief, professional explanation referencing the similar jobs. Explain why the estimate is reasonable or note any factors affecting confidence."""

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "You are a roofing estimation assistant. Be concise, professional, and reference specific data from similar jobs.",
            },
            {"role": "user", "content": prompt},
        ],
        max_tokens=150,
        temperature=0.3,
        stream=True,
    )

    for chunk in response:
        if chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content
