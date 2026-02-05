"""Query embedding generation using sentence-transformers.

Pre-loads model at startup when Pinecone is configured to avoid request timeouts.
"""

import gc
import logging
from typing import List, Optional

logger = logging.getLogger(__name__)

_model = None
_should_load = False


def load_embedding_model(eager: bool = False):
    """Load embedding model.

    Args:
        eager: If True, load model immediately (called when Pinecone is configured)
    """
    global _should_load
    _should_load = eager

    if eager:
        logger.info("Pre-loading embedding model at startup (Pinecone configured)...")
        _get_model()  # Force immediate load
    else:
        logger.info("Embedding model disabled (Pinecone not configured)")


def _get_model():
    """Get or load the embedding model (lazy singleton)."""
    global _model
    if _model is None:
        # Delay torch import to startup
        import torch
        torch.set_grad_enabled(False)

        from sentence_transformers import SentenceTransformer
        logger.info("Loading sentence-transformers model (first use)...")

        # Use multilingual model for French content
        # Same model used to generate cbr_embeddings.npz
        _model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        _model.eval()

        gc.collect()
        logger.info("Embedding model loaded")
    return _model


def unload_embedding_model():
    """Cleanup on shutdown."""
    global _model
    _model = None
    gc.collect()


def generate_query_embedding(text: str) -> List[float]:
    """Generate 384-dim embedding for query text."""
    import torch

    model = _get_model()
    with torch.inference_mode():
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
