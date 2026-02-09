"""Complexity calculator service for tier-based labor hour estimation.

Converts tier selection + factor checklist into additive labor hours
using config-driven business rules from complexity_tiers_config.json.

Formula: total_labor_hours = base_hours + tier_hours + factor_hours
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# Load config at module level (same pattern as predictor.py)
_CONFIG_PATH = Path(__file__).parent.parent / "models" / "complexity_tiers_config.json"
_config: Optional[Dict] = None


def _load_config() -> Dict:
    """Load and cache tier config from JSON file."""
    global _config
    if _config is None:
        with open(_CONFIG_PATH) as f:
            _config = json.load(f)
        logger.info(f"Loaded complexity tiers config v{_config.get('version', '?')}")
    return _config


def get_tier_config() -> Dict:
    """Get the full tier configuration (for frontend to consume via API if needed)."""
    return _load_config()


def calculate_complexity_hours(
    category: str,
    sqft: float,
    tier: int,
    factors: Dict[str, Any],
) -> Dict[str, Any]:
    """Calculate total labor hours from tier + factors.

    Args:
        category: Job category (e.g., "Bardeaux")
        sqft: Square footage of roof area
        tier: Complexity tier (1-6)
        factors: Dict of factor values:
            - roof_pitch: str (flat|low|medium|steep|very_steep)
            - access_difficulty: List[str] (checklist items)
            - demolition: str (none|single_layer|multi_layer|structural)
            - penetrations_count: int
            - security: List[str] (checklist items)
            - material_removal: str (none|standard|heavy|hazardous)
            - roof_sections_count: int
            - previous_layers_count: int

    Returns:
        Dict with base_hours, tier_hours, factor_hours, total_hours, breakdown, tier_name
    """
    config = _load_config()

    # 1. Base time (sqft-scaled by category)
    cat_key = category if category in config["base_time_per_category"] else "Autres"
    base_config = config["base_time_per_category"][cat_key]
    base_hours = (sqft / 1000) * base_config["hours_per_1000sqft"]
    base_hours = max(base_hours, base_config["min_hours"])

    # 2. Tier hours
    if tier < 1 or tier > len(config["tiers"]):
        tier = 1  # Default to simple if invalid
    tier_config = config["tiers"][tier - 1]
    tier_hours = tier_config["base_hours_added"]
    tier_name = tier_config["name_fr"]

    # 3. Factor hours (additive)
    factor_hours = 0.0
    breakdown = {}

    # Roof pitch (dropdown)
    pitch = factors.get("roof_pitch")
    if pitch and pitch in config["factors"]["roof_pitch"]["options"]:
        h = config["factors"]["roof_pitch"]["options"][pitch]["hours"]
        factor_hours += h
        breakdown["roof_pitch"] = h

    # Access difficulty (checklist - sum all selected)
    for item in factors.get("access_difficulty", []):
        if item in config["factors"]["access_difficulty"]["options"]:
            h = config["factors"]["access_difficulty"]["options"][item]["hours"]
            factor_hours += h
            breakdown[f"access_{item}"] = h

    # Demolition (dropdown)
    demo = factors.get("demolition")
    if demo and demo in config["factors"]["demolition"]["options"]:
        h = config["factors"]["demolition"]["options"][demo]["hours"]
        factor_hours += h
        breakdown["demolition"] = h

    # Penetrations (count-based)
    pen_count = factors.get("penetrations_count", 0)
    if pen_count > 0:
        h = pen_count * config["factors"]["penetrations"]["hours_per_item"]
        factor_hours += h
        breakdown["penetrations"] = h

    # Security (checklist - sum all selected)
    for item in factors.get("security", []):
        if item in config["factors"]["security"]["options"]:
            h = config["factors"]["security"]["options"][item]["hours"]
            factor_hours += h
            breakdown[f"security_{item}"] = h

    # Material removal (dropdown)
    removal = factors.get("material_removal")
    if removal and removal in config["factors"]["material_removal"]["options"]:
        h = config["factors"]["material_removal"]["options"][removal]["hours"]
        factor_hours += h
        breakdown["material_removal"] = h

    # Roof sections (count above baseline)
    sections = factors.get("roof_sections_count", 0)
    sections_config = config["factors"]["roof_sections"]
    if sections > sections_config["baseline"]:
        h = (sections - sections_config["baseline"]) * sections_config["hours_per_item_above"]
        factor_hours += h
        breakdown["roof_sections"] = h

    # Previous layers (count above baseline)
    layers = factors.get("previous_layers_count", 0)
    layers_config = config["factors"]["previous_layers"]
    if layers > layers_config["baseline"]:
        h = (layers - layers_config["baseline"]) * layers_config["hours_per_item_above"]
        factor_hours += h
        breakdown["previous_layers"] = h

    total_hours = base_hours + tier_hours + factor_hours

    # Compute complexity_score (0-100) from tier
    complexity_score = tier_config["score_min"] + (
        (tier_config["score_max"] - tier_config["score_min"]) // 2
    )

    return {
        "base_hours": round(base_hours, 1),
        "tier_hours": round(tier_hours, 1),
        "factor_hours": round(factor_hours, 1),
        "total_hours": round(total_hours, 1),
        "breakdown": breakdown,
        "tier_name": tier_name,
        "complexity_score": complexity_score,
    }
