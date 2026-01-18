"""Query embedding generation using sentence-transformers."""

from typing import List, Optional
import logging

from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

_model: SentenceTransformer = None


def load_embedding_model():
    """Load the embedding model at startup. Called from lifespan."""
    global _model
    logger.info("Loading sentence-transformers model...")
    _model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
    logger.info("Embedding model loaded successfully")


def unload_embedding_model():
    """Cleanup on shutdown."""
    global _model
    _model = None


def generate_query_embedding(text: str) -> List[float]:
    """Generate 384-dim embedding for query text."""
    if _model is None:
        raise RuntimeError("Embedding model not loaded. Ensure lifespan started.")
    embedding = _model.encode(text, convert_to_numpy=True)
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
