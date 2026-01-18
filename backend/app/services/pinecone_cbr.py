"""Pinecone operations for Case-Based Reasoning."""

from typing import Any, Dict, List, Optional
import logging

from pinecone.grpc import PineconeGRPC as Pinecone

from app.config import settings

logger = logging.getLogger(__name__)

_pc: Pinecone = None
_index = None


def init_pinecone():
    """Initialize Pinecone client. Called from lifespan."""
    global _pc, _index
    if not settings.pinecone_api_key:
        logger.warning("Pinecone API key not set, skipping initialization")
        return
    if not settings.pinecone_index_host:
        logger.warning("Pinecone index host not set, skipping initialization")
        return
    logger.info("Connecting to Pinecone...")
    _pc = Pinecone(api_key=settings.pinecone_api_key)
    _index = _pc.Index(host=settings.pinecone_index_host)
    logger.info("Pinecone connected successfully")


def close_pinecone():
    """Cleanup on shutdown."""
    global _pc, _index
    _pc = None
    _index = None


def query_similar_cases(
    query_vector: List[float],
    top_k: int = 5,
    category_filter: Optional[str] = None,
    namespace: str = "cbr"
) -> List[Dict[str, Any]]:
    """Query Pinecone for similar historical cases."""
    if _index is None:
        logger.warning("Pinecone not initialized, returning empty results")
        return []

    filter_dict = None
    if category_filter:
        filter_dict = {"category": {"$eq": category_filter}}

    results = _index.query(
        vector=query_vector,
        top_k=top_k,
        include_metadata=True,
        namespace=namespace,
        filter=filter_dict
    )

    similar_cases = []
    for match in results.matches:
        similar_cases.append({
            "case_id": match.id,
            "similarity": round(float(match.score), 4),
            "category": match.metadata.get("category"),
            "sqft": match.metadata.get("sqft"),
            "total": match.metadata.get("total"),
            "per_sqft": match.metadata.get("per_sqft"),
            "year": match.metadata.get("year"),
        })

    return similar_cases
