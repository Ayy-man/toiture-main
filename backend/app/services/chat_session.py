"""In-memory session store for chat conversations.

Manages conversation state, message history, and extracted fields
across multiple chat messages within a session.
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List

logger = logging.getLogger(__name__)

# Module-level session storage (same pattern as predictor.py)
_sessions: Dict[str, Dict[str, Any]] = {}


def get_session(session_id: str) -> Dict[str, Any]:
    """Get existing session or create new one with defaults.

    Also performs TTL cleanup: evicts sessions older than 24 hours.

    Args:
        session_id: Session identifier (UUID)

    Returns:
        Session dict with messages, extracted_fields, state, created_at, language
    """
    # TTL cleanup: remove sessions older than 24 hours
    _cleanup_stale_sessions()

    # Return existing session or create new one
    if session_id not in _sessions:
        _sessions[session_id] = {
            "messages": [],
            "extracted_fields": {},
            "state": "greeting",
            "created_at": datetime.utcnow().isoformat(),
            "language": "fr"
        }
        logger.info(f"Created new session: {session_id}")

    return _sessions[session_id]


def update_session(
    session_id: str,
    messages: List[Dict[str, str]],
    extracted_fields: Dict[str, Any],
    state: str
) -> None:
    """Update session with new messages, fields, and state.

    Args:
        session_id: Session identifier
        messages: Updated conversation history
        extracted_fields: Updated extracted fields
        state: New conversation state
    """
    if session_id not in _sessions:
        logger.warning(f"Attempting to update non-existent session: {session_id}")
        # Create session if it doesn't exist (defensive)
        get_session(session_id)

    _sessions[session_id]["messages"] = messages
    _sessions[session_id]["extracted_fields"] = extracted_fields
    _sessions[session_id]["state"] = state

    logger.debug(f"Updated session {session_id}: {len(messages)} messages, state={state}")


def clear_session(session_id: str) -> None:
    """Remove session from store.

    Args:
        session_id: Session identifier to clear
    """
    if session_id in _sessions:
        del _sessions[session_id]
        logger.info(f"Cleared session: {session_id}")
    else:
        logger.warning(f"Attempted to clear non-existent session: {session_id}")


def get_session_count() -> int:
    """Return count of active sessions.

    Useful for health check monitoring.

    Returns:
        Number of active sessions in memory
    """
    return len(_sessions)


def _cleanup_stale_sessions() -> None:
    """Remove sessions older than 24 hours.

    Called automatically by get_session() to prevent unbounded memory growth.
    """
    now = datetime.utcnow()
    cutoff = now - timedelta(hours=24)
    stale_sessions = []

    for session_id, session_data in _sessions.items():
        created_at_str = session_data.get("created_at")
        if created_at_str:
            try:
                created_at = datetime.fromisoformat(created_at_str.replace("Z", "+00:00"))
                if created_at < cutoff:
                    stale_sessions.append(session_id)
            except (ValueError, AttributeError) as e:
                logger.warning(f"Invalid created_at for session {session_id}: {e}")
                # Mark for cleanup if timestamp is invalid
                stale_sessions.append(session_id)

    # Remove stale sessions
    for session_id in stale_sessions:
        del _sessions[session_id]
        logger.info(f"Cleaned up stale session: {session_id}")

    if stale_sessions:
        logger.info(f"Cleaned up {len(stale_sessions)} stale sessions (>24h old)")
