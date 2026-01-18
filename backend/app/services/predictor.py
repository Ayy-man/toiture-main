"""ML model loading and prediction service.

Adapted from cortex-data/predict_final.py for FastAPI serving.
"""

import json
from pathlib import Path

import joblib
import numpy as np

# Module-level storage (shared across requests)
_models: dict = {}
_config: dict = {}

MODEL_DIR = Path(__file__).parent.parent / "models"


def load_models() -> None:
    """Load ML models at startup.

    Called once via lifespan context manager.
    """
    _models["global"] = joblib.load(MODEL_DIR / "cortex_model_global.pkl")
    _models["bardeaux"] = joblib.load(MODEL_DIR / "cortex_model_Bardeaux.pkl")
    _models["encoder"] = joblib.load(MODEL_DIR / "category_encoder_v3.pkl")
    with open(MODEL_DIR / "cortex_config_v3.json") as f:
        _config.update(json.load(f))


def unload_models() -> None:
    """Clean up models at shutdown."""
    _models.clear()
    _config.clear()


def predict(
    sqft: float,
    category: str,
    material_lines: int = 5,
    labor_lines: int = 2,
    has_subs: int = 0,
    complexity: int = 10,
) -> dict:
    """Generate price estimate for roofing job.

    Args:
        sqft: Square footage of roof
        category: Job category (Bardeaux, Elastomere, Other, etc.)
        material_lines: Number of material line items (default 5)
        labor_lines: Number of labor line items (default 2)
        has_subs: Whether subcontractors involved (0 or 1)
        complexity: Complexity score (default 10)

    Returns:
        dict with estimate, range_low, range_high, model, confidence
    """
    # Per-category features (no cat_enc)
    X_cat = np.array([[sqft, material_lines, labor_lines, has_subs, complexity]])

    # Global features (with cat_enc)
    cat_enc = _config["category_mapping"].get(category, 0)
    X_global = np.array(
        [[sqft, material_lines, labor_lines, has_subs, complexity, cat_enc]]
    )

    # Use specialized model for Bardeaux, global for others
    if category == "Bardeaux":
        prediction = _models["bardeaux"].predict(X_cat)[0]
        model_used = "Bardeaux (R2=0.65)"
        confidence = "HIGH"
    else:
        prediction = _models["global"].predict(X_global)[0]
        model_used = "Global (R2=0.59)"
        # Elastomere with accent from config
        confidence = "MEDIUM" if category in ["Other", "\u00c9lastom\u00e8re"] else "LOW"

    return {
        "estimate": round(float(prediction), 2),
        "range_low": round(float(prediction * 0.80), 2),
        "range_high": round(float(prediction * 1.20), 2),
        "model": model_used,
        "confidence": confidence,
    }
