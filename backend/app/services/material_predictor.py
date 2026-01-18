"""Material ID and quantity prediction service.

Uses lazy loading to reduce memory footprint at startup.
"""

import gc
import json
import logging
from pathlib import Path
from typing import Dict, Any

import numpy as np

logger = logging.getLogger(__name__)

# Module-level storage (shared across requests)
_models: dict = {}
_loaded: bool = False

MODEL_DIR = Path(__file__).parent.parent / "models"


def _ensure_models_loaded() -> None:
    """Lazy-load material prediction models on first use."""
    global _loaded
    if _loaded:
        return

    import joblib

    logger.info("Lazy-loading material prediction models (first use)...")

    _models["selector"] = joblib.load(MODEL_DIR / "material_selector.pkl")
    _models["binarizer"] = joblib.load(MODEL_DIR / "material_binarizer.pkl")
    _models["quantity"] = joblib.load(MODEL_DIR / "quantity_regressors.pkl")
    _models["category_encoder"] = joblib.load(MODEL_DIR / "category_encoder_material.pkl")

    with open(MODEL_DIR / "co_occurrence_rules.json") as f:
        _models["rules"] = json.load(f)

    with open(MODEL_DIR / "feature_triggers.json") as f:
        _models["triggers"] = json.load(f)

    with open(MODEL_DIR / "material_prices.json") as f:
        _models["prices"] = json.load(f)

    gc.collect()
    _loaded = True
    logger.info("Material prediction models loaded successfully")


def predict_materials(
    sqft: float,
    category: str,
    complexity: int = 10,
    has_chimney: bool = False,
    has_skylights: bool = False,
    material_lines: int = 5,
    labor_lines: int = 2,
    has_subs: bool = False,
    quoted_total: float = None,
) -> Dict[str, Any]:
    """Predict material IDs and quantities for a roofing job.

    Returns dict with:
    - materials: List of {material_id, quantity, unit_price, total, confidence}
    - total_materials_cost: Sum of all material totals
    - model_info: Description of model used
    - applied_rules: List of co-occurrence rules that fired
    """
    _ensure_models_loaded()

    # Encode category
    try:
        cat_enc = _models["category_encoder"].transform([category])[0]
    except ValueError:
        cat_enc = 0  # Unknown category

    # Build feature vector (same order as training)
    X = np.array([[
        sqft,
        complexity,
        quoted_total if quoted_total else sqft * 15,  # Estimate if not provided
        1 if has_chimney else 0,
        1 if has_skylights else 0,
        material_lines,
        labor_lines,
        1 if has_subs else 0,
        cat_enc,
    ]])

    # Predict material IDs
    probs = _models["selector"].predict_proba(X)[0]
    # Use 0.3 threshold (tuned during training)
    predicted_binary = (probs > 0.3).astype(int).reshape(1, -1)
    predicted_ids = _models["binarizer"].inverse_transform(predicted_binary)[0]
    predicted_ids = list(predicted_ids)

    # Apply feature triggers
    if has_chimney and "chimney_materials" in _models["triggers"]:
        for mat_id in _models["triggers"]["chimney_materials"]:
            if mat_id not in predicted_ids:
                predicted_ids.append(mat_id)

    if has_skylights and "skylight_materials" in _models["triggers"]:
        for mat_id in _models["triggers"]["skylight_materials"]:
            if mat_id not in predicted_ids:
                predicted_ids.append(mat_id)

    # Apply co-occurrence rules
    applied_rules = []
    for rule in _models["rules"]:
        if rule["antecedent"] in predicted_ids and rule["consequent"] not in predicted_ids:
            predicted_ids.append(rule["consequent"])
            applied_rules.append(
                f"{rule['antecedent']} -> {rule['consequent']} (conf={rule['confidence']:.2f})"
            )

    # Predict quantities for each material
    materials = []
    for mat_id in predicted_ids:
        mat_id_str = str(mat_id)

        # Get quantity from regressor or default to 1
        if mat_id_str in _models["quantity"]:
            qty = max(1, round(_models["quantity"][mat_id_str].predict(X)[0], 1))
            confidence = "HIGH"
        else:
            qty = 1.0
            confidence = "LOW"

        # Get unit price from lookup
        unit_price = _models["prices"].get(mat_id_str, 50.0)
        total = round(qty * unit_price, 2)

        materials.append({
            "material_id": mat_id,
            "quantity": qty,
            "unit_price": unit_price,
            "total": total,
            "confidence": confidence,
        })

    # Sort by total (descending) for usability
    materials.sort(key=lambda x: x["total"], reverse=True)

    total_cost = sum(m["total"] for m in materials)

    return {
        "materials": materials,
        "total_materials_cost": round(total_cost, 2),
        "model_info": "OneVsRest + GradientBoosting (v1)",
        "applied_rules": applied_rules,
    }
