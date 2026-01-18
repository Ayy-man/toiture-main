"""Supabase client for estimate storage and feedback collection.

Follows the same singleton pattern as predictor.py and llm_reasoning.py.
"""

import logging
import os
from typing import Optional

from supabase import Client, create_client

logger = logging.getLogger(__name__)

# Module-level client storage (same pattern as other services)
_client: Optional[Client] = None


def init_supabase() -> None:
    """Initialize Supabase client. Called from lifespan."""
    global _client

    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

    if not supabase_url or not supabase_key:
        logger.warning(
            "SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY not set. "
            "Feedback system will be unavailable."
        )
        return

    logger.info("Initializing Supabase client...")
    _client = create_client(supabase_url, supabase_key)
    logger.info("Supabase client initialized")


def get_supabase() -> Optional[Client]:
    """Get the Supabase client for operations.

    Returns None if not configured (graceful degradation).
    """
    return _client


def close_supabase() -> None:
    """Cleanup on shutdown."""
    global _client
    _client = None
    logger.info("Supabase client closed")
