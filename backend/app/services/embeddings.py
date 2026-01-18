"""Query embedding generation using sentence-transformers."""

from typing import List, Optional
import logging
import gc

logger = logging.getLogger(__name__)

_model = None


def load_embedding_model():
    """Lazy load - model loaded on first use to reduce startup memory."""
    # Don't load at startup - load lazily on first embed call
    logger.info("Embedding model will load on first use (lazy loading)")


def _get_model():
    """Get or load the embedding model (lazy singleton)."""
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        logger.info("Loading sentence-transformers model (first use)...")
        # Use smaller model: L6 instead of L12 (half the memory)
        _model = SentenceTransformer('all-MiniLM-L6-v2')
        gc.collect()  # Force garbage collection
        logger.info("Embedding model loaded")
    return _model


def unload_embedding_model():
    """Cleanup on shutdown."""
    global _model
    _model = None


def generate_query_embedding(text: str) -> List[float]:
    """Generate 384-dim embedding for query text."""
    model = _get_model()
    embedding = model.encode(text, convert_to_numpy=True)
    return embedding.tolist()


def build_query_text(
    sqft: float,
    category: str,
    complexity: int,
    material_lines: Optional[int] = None,
    labor_lines: Optional[int] = None
) -> str:
    """Build query text from estimate inputs for semantic similarity."""
    parts = [f"Toiture {category}"]
    if sqft:
        parts.append(f"{sqft} pieds carres")
    parts.append(f"complexite {complexity}")
    if material_lines:
        parts.append(f"{material_lines} lignes materiaux")
    if labor_lines:
        parts.append(f"{labor_lines} lignes main-d'oeuvre")
    return ", ".join(parts)
