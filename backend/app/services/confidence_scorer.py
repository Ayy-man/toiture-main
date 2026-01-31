"""Confidence scoring for hybrid quote generation.

Combines multiple signals into overall confidence score:
- CBR similarity (30%): Average similarity of top-k cases from Pinecone
- ML-CBR agreement (40%): Jaccard similarity of predicted material IDs
- Data completeness (30%): Percentage of optional fields provided

Confidence < 0.5 flags quote for Laurent's manual review.
"""

import logging
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

logger = logging.getLogger(__name__)

# Weight configuration (from CONTEXT.md decision)
WEIGHT_CBR_SIMILARITY = 0.30
WEIGHT_ML_CBR_AGREEMENT = 0.40
WEIGHT_DATA_COMPLETENESS = 0.30
REVIEW_THRESHOLD = 0.50


def calculate_data_completeness(
    sqft: Optional[float],
    category: Optional[str],
    complexity_aggregate: Optional[int],
    has_chimney: Optional[bool],
    has_skylights: Optional[bool],
    quoted_total: Optional[float],
) -> float:
    """Calculate data completeness score (0-1).

    Required fields (sqft, category) contribute 50%.
    Optional fields contribute remaining 50%.
    """
    score = 0.0

    # Required fields (50% weight)
    if sqft is not None and sqft > 0:
        score += 0.25
    if category is not None and category != "Unknown":
        score += 0.25

    # Optional fields (50% weight, 10% each)
    if complexity_aggregate is not None:
        score += 0.10
    if has_chimney is not None:
        score += 0.10
    if has_skylights is not None:
        score += 0.10
    if quoted_total is not None and quoted_total > 0:
        score += 0.20  # Extra weight - very helpful for accuracy

    return min(1.0, score)


def calculate_material_agreement(
    ml_material_ids: List[int],
    cbr_material_ids: List[int],
) -> float:
    """Calculate Jaccard similarity between ML and CBR material predictions.

    Jaccard = |A ∩ B| / |A ∪ B|
    Returns 0 if both sets are empty.
    """
    ml_set = set(ml_material_ids)
    cbr_set = set(cbr_material_ids)

    union = ml_set | cbr_set
    if len(union) == 0:
        return 0.0

    intersection = ml_set & cbr_set
    return len(intersection) / len(union)


def calculate_confidence(
    cbr_cases: List[Dict[str, Any]],
    ml_material_ids: List[int],
    data_completeness: float,
    cbr_material_ids: Optional[List[int]] = None,
) -> Tuple[float, bool]:
    """Calculate overall confidence score and review flag.

    Args:
        cbr_cases: Similar cases from Pinecone with 'similarity' field
        ml_material_ids: Material IDs predicted by ML model
        data_completeness: Pre-calculated data completeness (0-1)
        cbr_material_ids: Material IDs extracted from CBR cases (optional,
                          if not provided, extracted from cbr_cases)

    Returns:
        Tuple of (confidence_score, needs_review)
        - confidence_score: 0.0-1.0
        - needs_review: True if confidence < REVIEW_THRESHOLD
    """
    # Signal 1: Average CBR similarity (30%)
    if cbr_cases:
        similarities = [case.get("similarity", 0.0) for case in cbr_cases]
        avg_cbr_similarity = float(np.mean(similarities))
    else:
        avg_cbr_similarity = 0.0
        logger.warning("No CBR cases - CBR similarity contribution is 0")

    # Signal 2: ML-CBR material agreement (40%)
    if cbr_material_ids is None:
        # Extract from CBR cases if not provided
        cbr_material_ids = []
        for case in cbr_cases:
            for material in case.get("materials", []):
                mat_id = material.get("material_id")
                if mat_id is not None:
                    cbr_material_ids.append(mat_id)

    material_agreement = calculate_material_agreement(ml_material_ids, cbr_material_ids)

    # Signal 3: Data completeness (30%)
    # Already provided as argument

    # Weighted combination
    confidence = (
        WEIGHT_CBR_SIMILARITY * avg_cbr_similarity
        + WEIGHT_ML_CBR_AGREEMENT * material_agreement
        + WEIGHT_DATA_COMPLETENESS * data_completeness
    )

    # Clamp to [0, 1]
    confidence = max(0.0, min(1.0, confidence))

    # Determine if review is needed
    needs_review = confidence < REVIEW_THRESHOLD

    logger.info(
        f"Confidence breakdown: CBR={avg_cbr_similarity:.2f}, "
        f"Agreement={material_agreement:.2f}, Completeness={data_completeness:.2f} "
        f"-> Overall={confidence:.2f} (needs_review={needs_review})"
    )

    return confidence, needs_review


def calculate_confidence_ml_only(
    ml_material_ids: List[int],
    data_completeness: float,
) -> Tuple[float, bool]:
    """Calculate confidence when CBR is unavailable (ML-only fallback).

    Uses modified formula:
    - ML model coverage: 30% (based on number of materials predicted)
    - Data completeness: 70% (more weight since no CBR)

    Always flags for review since CBR is missing.
    """
    # Estimate ML coverage based on material count (heuristic)
    # More materials = more confident the model found patterns
    material_count = len(ml_material_ids)
    ml_coverage = min(1.0, material_count / 20)  # Expect ~20 materials for full coverage

    confidence = 0.30 * ml_coverage + 0.70 * data_completeness

    # ML-only always needs review
    needs_review = True

    logger.info(
        f"ML-only confidence: Coverage={ml_coverage:.2f}, "
        f"Completeness={data_completeness:.2f} -> Overall={confidence:.2f} "
        "(ML-only always needs review)"
    )

    return confidence, needs_review
