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


def is_pinecone_available() -> bool:
    """Check if Pinecone is configured and ready for queries."""
    return _index is not None


def query_similar_cases(
    query_vector: List[float],
    top_k: int = 5,
    category_filter: Optional[str] = None,
    sqft_filter: Optional[float] = None,
    namespace: str = "cbr"
) -> List[Dict[str, Any]]:
    """Query Pinecone for similar historical cases.

    Args:
        query_vector: Embedding vector for similarity search
        top_k: Number of results to return
        category_filter: Optional category to filter by
        sqft_filter: If provided, filters to cases within 0.5x-2x this sqft value
        namespace: Pinecone namespace
    """
    if _index is None:
        logger.warning("Pinecone not initialized, returning empty results")
        return []

    # Build filter conditions
    filter_conditions = []

    if category_filter:
        filter_conditions.append({"category": {"$eq": category_filter}})

    # Add sqft range filter: 0.5x to 2x the input sqft
    # This ensures similar cases are actually comparable in size
    if sqft_filter and sqft_filter > 0:
        sqft_min = sqft_filter * 0.5
        sqft_max = sqft_filter * 2.0
        filter_conditions.append({"sqft": {"$gte": sqft_min}})
        filter_conditions.append({"sqft": {"$lte": sqft_max}})

    # Combine filters with $and if multiple conditions
    filter_dict = None
    if len(filter_conditions) == 1:
        filter_dict = filter_conditions[0]
    elif len(filter_conditions) > 1:
        filter_dict = {"$and": filter_conditions}

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
