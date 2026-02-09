"""Red flag evaluator service for submission risk assessment.

This service evaluates submissions for 5 risk categories before sending:
1. Budget mismatch: Client quoted total 30%+ below predicted
2. Geographic distance: Site >60km from LV headquarters
3. Material risk: Imported materials with 6+ week lead time
4. Crew availability: Multi-day project during peak season (June-Sept)
5. Low margin: Profit margin below 15% threshold

Returns bilingual warning messages for frontend display.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from app.schemas.red_flag import RedFlagCategory, RedFlagResponse, RedFlagSeverity


def evaluate_red_flags(
    submission: Dict[str, Any],
    request_data: Optional[Dict[str, Any]] = None
) -> List[RedFlagResponse]:
    """Evaluate submission data for red flag warnings.

    Args:
        submission: Submission record from database with pricing fields
        request_data: Optional dict with original request fields (quoted_total,
                     geographic_zone, supply_chain_risk, duration_type)

    Returns:
        List of applicable red flags with bilingual messages
    """
    flags = []

    # Parse request data from submission if not provided separately
    # Phase 22 stores original request fields in the submission record
    if request_data is None:
        request_data = {}

    # 1. Budget mismatch: client quoted_total is 30%+ below predicted total
    quoted_total = request_data.get("quoted_total")
    predicted_total = submission.get("total_price", 0)
    if quoted_total and predicted_total > 0:
        if float(quoted_total) < float(predicted_total) * 0.7:
            flags.append(RedFlagResponse(
                category=RedFlagCategory.budget_mismatch,
                severity=RedFlagSeverity.warning,
                message_fr=f"Le budget client ({float(quoted_total):,.0f}$) est 30%+ inférieur au prix prévu ({float(predicted_total):,.0f}$)",
                message_en=f"Client budget (${float(quoted_total):,.0f}) is 30%+ below predicted (${float(predicted_total):,.0f})",
            ))

    # 2. Geographic distance: red_flag zone means >60km from LV HQ
    geographic_zone = request_data.get("geographic_zone")
    if geographic_zone == "red_flag":
        flags.append(RedFlagResponse(
            category=RedFlagCategory.geographic,
            severity=RedFlagSeverity.warning,
            message_fr="Le chantier est à plus de 60km du siège de Toiture LV",
            message_en="Site is more than 60km from Toiture LV headquarters",
        ))

    # 3. Material risk: imported materials with 6+ week lead time
    supply_chain_risk = request_data.get("supply_chain_risk")
    if supply_chain_risk == "import":
        flags.append(RedFlagResponse(
            category=RedFlagCategory.material_risk,
            severity=RedFlagSeverity.critical,
            message_fr="Matériaux importés avec délai de 6+ semaines",
            message_en="Imported materials with 6+ week lead time",
        ))

    # 4. Crew availability: multi-day during peak season (June-Sept)
    duration_type = request_data.get("duration_type")
    if duration_type == "multi_day":
        now = datetime.now()
        if 6 <= now.month <= 9:
            flags.append(RedFlagResponse(
                category=RedFlagCategory.crew_availability,
                severity=RedFlagSeverity.warning,
                message_fr="Projet multi-jours en haute saison (juin-septembre)",
                message_en="Multi-day project during peak season (June-September)",
            ))

    # 5. Low margin: margin < 15%
    materials_cost = float(submission.get("total_materials_cost", 0))
    labor_cost = float(submission.get("total_labor_cost", 0))
    total_price = float(submission.get("total_price", 0))
    total_costs = materials_cost + labor_cost
    margin = (total_price - total_costs) / total_price if total_price > 0 else 0

    if margin < 0.15:
        margin_pct = margin * 100
        flags.append(RedFlagResponse(
            category=RedFlagCategory.low_margin,
            severity=RedFlagSeverity.critical,
            message_fr=f"La marge est de {margin_pct:.1f}% (seuil: 15%)",
            message_en=f"Margin is {margin_pct:.1f}% (threshold: 15%)",
        ))

    return flags
