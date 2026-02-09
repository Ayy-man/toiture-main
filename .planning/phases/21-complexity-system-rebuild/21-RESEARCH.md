# Phase 21: Complexity System Rebuild - Research

**Research Date:** 2026-02-09
**Researcher:** GSD Phase Researcher Agent
**Sprint Deadline:** Feb 11, 2026

## Executive Summary

Phase 21 replaces the current 6-factor slider complexity system (0-56 scale) with a tier-based system (0-100 scale) using 6 named tiers that map to real-world roofing scenarios. The new system shifts from percentage-based adjustments to time-based calculations, where each complexity tier and factor adds estimated hours to a base time value.

**Critical Path Items:**
1. Business logic gap: Laurent must provide base time values per job type and time multipliers/hours per tier and factor
2. UI rebuild: Replace sliders with tier selector (dropdown or visual cards)
3. Backend schema update: Maintain 6 individual factors but add tier selection and time-based calculations
4. Formula change: From percentage-based complexity multipliers to additive hours-based calculations

---

## 1. Current State Analysis

### 1.1 Existing Complexity System

**Frontend Implementation** (`frontend/src/components/estimateur/complexity-presets.tsx`):
- Three presets: Simple (11/56), Modéré (28/56), Complexe (44/56)
- Six sliders with different max values:
  - Access difficulty: 0-10
  - Roof pitch: 0-8
  - Penetrations: 0-10
  - Material removal: 0-8
  - Safety concerns: 0-10
  - Timeline constraints: 0-10
- Sum of factors = aggregate score (0-56)
- UI shows both preset buttons and collapsible custom sliders
- Preset clears when any slider manually adjusted

**Backend Schema** (`backend/app/schemas/hybrid_quote.py`):
- `HybridQuoteRequest` accepts all 6 factors individually
- `complexity_aggregate` field (0-56) with 5% tolerance validation
- Factors used in ML model (`cortex_config_v3.json` shows `complexity_score` as feature)
- LLM merger prompt includes 6-factor breakdown for explainable reasoning

**Current Usage in Pipeline**:
- ML prediction: Uses `complexity_aggregate` as feature in price/material models
- CBR query: Uses complexity in similarity weighting
- LLM merger: Receives all 6 factors for reasoning
- Confidence scoring: Data completeness check includes complexity

### 1.2 Problems with Current System

1. **Non-intuitive scale**: 0-56 range doesn't map to real-world understanding
2. **Percentage-based**: System treats complexity as multiplier, not additive hours
3. **Abstract factors**: Roofers think in scenarios (e.g., "3-story with crane access"), not slider values
4. **No tier names**: Missing human-readable descriptions (e.g., "Standard access, flat roof")
5. **Arbitrary maxes**: Why is roof pitch 0-8 but access 0-10? Not clear to users
6. **Missing time estimates**: No direct translation to labor hours added

---

## 2. Target State Design

### 2.1 Tier-Based System (0-100 Scale)

**Six Named Tiers:**

Each tier (0-100 scale, increments of ~17) represents a real-world job profile with descriptions for:
- Site conditions (access, distance, terrain)
- Roof characteristics (pitch, sections, previous layers)
- Access methods (ladder, scaffolding, crane, special equipment)

**Proposed Tier Structure** (Laurent approval needed):

| Tier | Name | Score Range | Description |
|------|------|-------------|-------------|
| 1 | Simple/Standard | 0-16 | Single-story detached house, flat to 4/12 pitch, driveway access, no crane needed, 1-2 roof sections, standard materials |
| 2 | Moderate | 17-33 | Two-story house, 4/12 to 6/12 pitch, good street access, some penetrations (vents/pipes), 2-3 roof sections, standard tear-off |
| 3 | Complex | 34-50 | Two-story with steep pitch (6/12-8/12), limited access (narrow street/driveway), multiple penetrations, 3-4 sections, multi-layer tear-off |
| 4 | High Complexity | 51-66 | Three-story or steep pitch (8/12+), difficult access (crane recommended), many penetrations, 4+ sections, heavy tear-off, safety equipment required |
| 5 | Very High Complexity | 67-83 | Three-story with very steep pitch (10/12+), crane required, extreme access difficulty (downtown, no parking), extensive penetrations, 5+ sections, multiple previous layers |
| 6 | Extreme | 84-100 | High-rise/commercial, extreme pitch, crane mandatory, hazardous access (scaffolding + safety harness), extensive structural work, winter conditions, historical building |

**Note:** Final tier names, score ranges, and descriptions must be approved by Laurent. These are research recommendations based on typical roofing industry complexity categories.

### 2.2 Time-Based Calculation Model

**Formula Change:**
```
OLD: labor_cost = base_labor × (1 + complexity_percentage)
NEW: total_labor_hours = base_time + tier_hours + factor_hours
     labor_cost = total_labor_hours × crew_cost_per_hour
```

**Components:**

1. **Base time** (Laurent to provide):
   - Per job type (e.g., "1500 sqft Bardeaux = 24 base hours")
   - Scales linearly with sqft (e.g., 2000 sqft = 32 hours)

2. **Tier hours** (Laurent to provide):
   - Each tier adds fixed hours to base time
   - Example: Tier 1 (+0h), Tier 2 (+4h), Tier 3 (+8h), Tier 4 (+16h), Tier 5 (+24h), Tier 6 (+40h)

3. **Factor hours** (Laurent to provide):
   - Individual factors still captured for granularity
   - Each factor adds estimated hours
   - Example: "No crane access = +6 hours", "Steep pitch (8/12+) = +4 hours"

4. **Conservative default**:
   - System assumes average skill workers (never best-case scenario)
   - Manual override allowed upward only (estimator can add time, system never suggests less)

### 2.3 Factor Checklist

Eight factors remain available for granular adjustments:

| Factor | Type | Impact |
|--------|------|--------|
| Roof pitch | Dropdown (Flat/Low/Medium/Steep/Very Steep) | +0 to +8 hours |
| Access difficulty | Checklist (crane, driveway width, street blocking, elevation) | +0 to +12 hours |
| Demolition | Radio (none/single layer/multi-layer/structural) | +0 to +10 hours |
| Penetrations | Number input (vents, pipes, skylights, chimneys) | +0.5h per penetration |
| Security | Checklist (harness, scaffolding, guardrails, winter safety) | +0 to +8 hours |
| Material removal | Radio (none/standard/heavy/hazardous) | +0 to +6 hours |
| Roof sections | Number input (1-10+) | +1h per section above 2 |
| Previous layers | Number input (0-5+) | +2h per layer above 1 |

**Note:** Hours per factor are estimates pending Laurent's input. The system should support easy configuration changes without code deployment.

---

## 3. Implementation Approach

### 3.1 Data Model Changes

**Backend Schema Updates** (`backend/app/schemas/hybrid_quote.py`):

```python
class HybridQuoteRequest(BaseModel):
    # NEW FIELDS
    complexity_tier: int = Field(ge=1, le=6, description="Complexity tier (1-6)")
    complexity_score: int = Field(ge=0, le=100, description="Tier-based score (0-100)")

    # MODIFIED: Keep existing 6 factors for backward compatibility and granularity
    # But change semantics to hours-based, not 0-10 scale
    roof_pitch: str = Field(description="Pitch category: flat|low|medium|steep|very_steep")
    access_difficulty_checklist: List[str] = Field(description="List of access challenges")
    demolition_type: str = Field(description="none|single|multi|structural")
    penetrations_count: int = Field(ge=0, le=100, description="Number of roof penetrations")
    safety_requirements: List[str] = Field(description="Safety equipment needed")
    material_removal_type: str = Field(description="none|standard|heavy|hazardous")
    roof_sections_count: int = Field(ge=1, le=20, description="Number of distinct roof sections")
    previous_layers_count: int = Field(ge=0, le=10, description="Number of existing layers")

    # DEPRECATED (keep for backward compatibility, but ignore in v2 calculations)
    complexity_aggregate: Optional[int] = Field(default=None, ge=0, le=56)
    access_difficulty: Optional[int] = Field(default=None, ge=0, le=10)
    # ... other old fields marked optional
```

**Configuration File** (new: `backend/app/models/complexity_tiers_config.json`):

```json
{
  "tiers": [
    {
      "tier": 1,
      "name": "Simple/Standard",
      "score_min": 0,
      "score_max": 16,
      "description_fr": "Maison plain-pied, toit plat à faible pente...",
      "description_en": "Single-story detached house, flat to low pitch...",
      "base_hours_added": 0
    },
    // ... tiers 2-6
  ],
  "factors": {
    "roof_pitch": {
      "flat": {"hours": 0, "label_fr": "Plat (0-2/12)", "label_en": "Flat (0-2/12)"},
      "low": {"hours": 2, "label_fr": "Faible (3/12-4/12)", "label_en": "Low (3/12-4/12)"},
      // ... categories
    },
    "access_difficulty_items": {
      "no_crane": {"hours": 6, "label_fr": "Pas d'accès pour grue", "label_en": "No crane access"},
      "narrow_driveway": {"hours": 2, "label_fr": "Entrée étroite", "label_en": "Narrow driveway"},
      // ... items
    },
    // ... other factors
  },
  "base_time_per_category": {
    "Bardeaux": {"hours_per_1000sqft": 16, "min_hours": 8},
    "Elastomère": {"hours_per_1000sqft": 20, "min_hours": 12},
    // ... categories
  }
}
```

**Why JSON config?**
- Business rules change frequently (Laurent adjusts time estimates)
- No code deployment needed for hour adjustments
- Easy A/B testing of different time formulas
- Version control for business logic

### 3.2 Frontend Changes

**New Component: Tier Selector** (`frontend/src/components/estimateur/tier-selector.tsx`):

Two UI options (recommend Option A):

**Option A: Visual Cards** (Recommended)
- 6 cards in 2×3 or 3×2 grid
- Each card shows: tier name, score range, icon, 1-sentence description
- Selected card highlighted with primary color border
- Hover shows full description tooltip
- Mobile: stacks vertically

**Option B: Enhanced Dropdown**
- Dropdown with rich options (not just text)
- Each option shows tier name + score + brief description
- Simpler but less visual

**Factor Checklist Panel** (`frontend/src/components/estimateur/factor-checklist.tsx`):
- Collapsible panel (collapsed by default)
- "Advanced adjustments" or "Fine-tune complexity" label
- Eight factor inputs using appropriate UI:
  - Dropdowns for categorical (pitch, demolition, material removal)
  - Checkboxes for multi-select (access, safety)
  - Number inputs for counts (penetrations, sections, layers)
- Each factor shows "+X hours" dynamically as user selects
- Running total: "Total adjustments: +14 hours"

**Modified Component: Full Quote Form** (`frontend/src/components/estimateur/full-quote-form.tsx`):
- Remove `<ComplexityPresets>` component
- Add `<TierSelector>` component
- Add `<FactorChecklist>` component (optional/collapsible)
- Update form state to track tier + individual factors
- Compute `complexity_score` (0-100) from tier selection
- Submit new schema to backend

**Visual Mockup Structure:**
```
┌─────────────────────────────────────────┐
│ Full Quote Form                          │
├─────────────────────────────────────────┤
│ Square Footage: [1500] sqft              │
│ Category: [Bardeaux ▼]                   │
├─────────────────────────────────────────┤
│ Complexity Tier:                         │
│ ┌──────┬──────┬──────┐                  │
│ │ Tier │ Tier │ Tier │                  │
│ │  1   │  2   │  3   │ [Cards]          │
│ │Simple│Mod.  │Comp. │                  │
│ └──────┴──────┴──────┘                  │
│ ┌──────┬──────┬──────┐                  │
│ │ Tier │ Tier │ Tier │                  │
│ │  4   │  5   │  6   │                  │
│ │High  │V.High│Extrem│                  │
│ └──────┴──────┴──────┘                  │
├─────────────────────────────────────────┤
│ ▼ Advanced Adjustments (+14 hours)      │
│   [Collapsed by default]                 │
│   - Roof pitch: [Medium ▼] (+2h)        │
│   - Access: ☑ No crane (+6h)            │
│   - Penetrations: [8] (+4h)              │
│   ...                                    │
└─────────────────────────────────────────┘
```

### 3.3 Backend Calculation Logic

**New Service** (`backend/app/services/complexity_calculator.py`):

```python
from typing import Dict, Any
from app.models.complexity_tiers_config import load_tier_config

def calculate_total_labor_hours(
    category: str,
    sqft: float,
    tier: int,
    factors: Dict[str, Any]
) -> Dict[str, float]:
    """
    Calculate total labor hours from tier + factors.

    Returns:
        {
            "base_hours": float,
            "tier_hours": float,
            "factor_hours": float,
            "total_hours": float,
            "breakdown": {...}  # detailed hour breakdown per factor
        }
    """
    config = load_tier_config()

    # 1. Base time (sqft-scaled)
    base_config = config["base_time_per_category"][category]
    base_hours = (sqft / 1000) * base_config["hours_per_1000sqft"]
    base_hours = max(base_hours, base_config["min_hours"])

    # 2. Tier hours
    tier_config = config["tiers"][tier - 1]
    tier_hours = tier_config["base_hours_added"]

    # 3. Factor hours
    factor_hours = 0
    breakdown = {}

    # Roof pitch
    if factors.get("roof_pitch"):
        pitch_hours = config["factors"]["roof_pitch"][factors["roof_pitch"]]["hours"]
        factor_hours += pitch_hours
        breakdown["roof_pitch"] = pitch_hours

    # Access difficulty (checklist - sum all selected)
    for item in factors.get("access_difficulty_checklist", []):
        item_hours = config["factors"]["access_difficulty_items"][item]["hours"]
        factor_hours += item_hours
        breakdown[f"access_{item}"] = item_hours

    # ... other factors

    # Penetrations (count × hours per)
    penetrations = factors.get("penetrations_count", 0)
    if penetrations > 0:
        penetrations_hours = penetrations * config["factors"]["penetrations"]["hours_per_item"]
        factor_hours += penetrations_hours
        breakdown["penetrations"] = penetrations_hours

    # ... similar for sections, layers

    total_hours = base_hours + tier_hours + factor_hours

    return {
        "base_hours": base_hours,
        "tier_hours": tier_hours,
        "factor_hours": factor_hours,
        "total_hours": total_hours,
        "breakdown": breakdown
    }
```

**Integration Points:**
1. **ML Prediction**: Instead of `complexity_aggregate` (0-56), pass `complexity_score` (0-100) to models
2. **CBR Query**: Use new score for similarity filtering
3. **LLM Merger**: Include tier name + hours breakdown in prompt for better reasoning
4. **Confidence Scoring**: Update to check `complexity_score` instead of old aggregate

### 3.4 Migration Strategy

**Phase A: Parallel Mode** (Recommended for sprint timeline):
- Keep old system working
- Add new tier system alongside
- Backend accepts both old and new complexity formats
- Frontend: Add feature flag to toggle between old/new UI
- Validate new system against historical quotes (compare calculated hours to actual)

**Phase B: Cutover** (After validation):
- Default to new system
- Hide old sliders behind "legacy mode" toggle
- Migrate all new quotes to tier-based system

**Phase C: Deprecation** (Future sprint):
- Remove old complexity fields from schema
- Clean up unused code

**For Feb 11 deadline**: Implement Phase A only. Full cutover requires Laurent validation of time formulas.

---

## 4. Business Logic Requirements

### 4.1 Data Needed from Laurent

**Critical for Phase 21:**

1. **Base time values per job type:**
   - "How many hours for a baseline 1000 sqft Bardeaux job?" (Assume: standard access, flat roof, no complications)
   - Repeat for: Elastomère, Metal, TPO, Other categories
   - Provide min hours (e.g., "Never quote less than 8 hours even for tiny jobs")

2. **Tier hour additions:**
   - For each of 6 tiers: "How many hours does this complexity level add to base time?"
   - Example: Tier 1 (+0h), Tier 2 (+4h), Tier 3 (+8h), Tier 4 (+16h), Tier 5 (+24h), Tier 6 (+40h)
   - Or provide real-world examples: "Show me 3 actual jobs for each tier, I'll measure hours"

3. **Factor hours:**
   - Roof pitch: "How much longer for 8/12 pitch vs flat?" → hours difference
   - No crane access: "If we can't use crane, how many extra hours?" → hours added
   - Multi-layer tear-off: "Each additional layer adds how many hours?" → hours per layer
   - Penetrations: "Each vent/pipe/skylight adds how much time?" → hours per item
   - ... for all 8 factors

4. **Crew cost per hour:**
   - "What's your average crew cost per hour?" (includes wages, benefits, overhead)
   - Needed for: `labor_cost = total_hours × crew_cost_per_hour`
   - Note: This may overlap with Phase 22 (employee count inputs)

5. **Tier descriptions validation:**
   - Review the 6 proposed tier descriptions above
   - Adjust to match how LV actually categorizes jobs
   - Provide Quebec-specific examples (e.g., "Plateau duplex" = Tier X)

**Recommended approach:**
- Schedule 1-hour working session with Laurent
- Bring 20-30 historical completed quotes from different complexity levels
- For each quote: "How many hours did the crew actually work?" (from CCube time tracking?)
- Reverse-engineer formulas from real data
- Validate formulas against next 20 quotes

### 4.2 Fallback Strategy

If Laurent's data unavailable by Feb 11:

1. **Estimate from historical quotes:**
   - Analyze `Quote Time Lines_clean.csv` for actual labor hours
   - Group by category + complexity level (using old 0-56 scores as proxy)
   - Calculate median hours per group
   - Use as temporary formulas with confidence flags

2. **Use industry standards:**
   - Roofing industry averages: ~1.5-2 hours per 100 sqft for standard shingle jobs
   - Apply documented complexity multipliers from roofing associations
   - Mark all quotes as "needs review" (low confidence) until Laurent validates

3. **Defer time-based calculations:**
   - Implement tier UI and factor checklists
   - Keep percentage-based calculations temporarily
   - Display tier names for UX improvement
   - Defer formula cutover to Phase 22 (when crew inputs added)

---

## 5. Testing & Validation

### 5.1 Validation Dataset

**Test with historical quotes:**
1. Select 50 completed quotes across all 6 proposed tiers
2. For each quote:
   - Manually assign tier (1-6) based on job description
   - Select applicable factors (pitch, access, penetrations, etc.)
   - Calculate estimated hours using new formula
   - Compare to actual hours worked (from CCube time tracking if available)
3. Acceptable accuracy: ±20% of actual hours for 80% of quotes
4. Flag outliers for Laurent review

**Edge cases to test:**
- Service calls (labor only, no materials)
- Very small jobs (<500 sqft)
- Very large jobs (>5000 sqft)
- Multi-day projects (how does base time scale?)
- Winter jobs (safety requirements increase hours?)
- Commercial vs residential (different tier mappings?)

### 5.2 User Acceptance Criteria

**For Laurent (estimator perspective):**
- "Can I quickly identify which tier a job belongs to by reading the description?"
- "Do the hour estimates match my intuition for typical jobs?"
- "Can I easily adjust for special circumstances using factor checklist?"
- "Does the system explain WHERE the hours come from?" (transparency)

**For Steven (estimator using system):**
- "Is the tier selector faster than the old sliders?"
- "Do the tier names make sense without training?"
- "Can I still override if the system underestimates?"
- "Does the quote look professional with hour breakdowns?"

### 5.3 Rollback Plan

**If new system fails in production:**
1. Feature flag: Toggle back to old complexity sliders
2. Backend: Old schema fields still functional
3. Database: New tier fields nullable, system falls back to old aggregate
4. Timeline: <5 minutes to rollback via environment variable change

---

## 6. Dependencies & Risks

### 6.1 Dependencies

**Blocking:**
- Phase 19 complete (data quality fixes) — ensures clean historical data for validation
- Laurent availability for time multiplier input session (est. 1-2 hours)

**Non-blocking but helpful:**
- Phase 20 (materials database) — provides material names for better tier descriptions
- Phase 22 (crew inputs) — integrates with labor hours calculations

### 6.2 Risks

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| Laurent unavailable for input | High | Medium | Use historical data analysis + fallback formulas |
| Time formulas inaccurate | High | Medium | Phased rollout with validation step before full cutover |
| Users confused by tier names | Medium | Low | User testing with Steven before launch |
| Backend calculation too slow | Low | Low | Cache tier config, pre-calculate common scenarios |
| Old quotes break with new schema | Medium | Low | Maintain backward compatibility, gradual migration |

### 6.3 Sprint Timeline Concerns

**Feb 11 deadline is tight for:**
1. Laurent working session (needs scheduling)
2. Full validation of formulas (50 quote test dataset)
3. User testing with Steven

**Recommended scope adjustment:**
- Feb 11: Ship UI changes + tier selector (UX improvement)
- Feb 13: Deploy formula changes after Laurent validation
- Feb 16: Full cutover after production testing

---

## 7. Open Questions

**For user/product owner:**
1. Should the 6 individual factors remain as granular inputs, or simplify to just tier selection?
   - **Recommendation:** Keep factors but make collapsible/optional for power users

2. How should the system handle jobs that don't fit any tier? (e.g., unique custom work)
   - **Recommendation:** Add "Custom" tier (Tier 7?) with manual hour input + notes field

3. Should tier selection be binding, or can estimator manually override the score?
   - **Recommendation:** Tier sets initial score, but show score as editable number input below selector

4. Do tier descriptions need to be bilingual from day 1, or FR only for MVP?
   - **Recommendation:** FR only for Feb 11, EN translations added in Phase 25 (i18n fixes)

**For Laurent (business logic):**
5. Are base time values category-specific only, or also material-specific?
   - (e.g., does "Bardeaux with premium shingles" take longer than "Bardeaux with standard"?)

6. How do multi-day jobs affect the formula? Is it linear (2 days = 2× hours) or discounted?
   - Phase 22 adds duration inputs, but formula impact unclear

7. Should safety factors add hours, add cost (equipment rental), or both?
   - Phase 22 adds tools/equipment inputs, potential overlap with complexity safety factor

8. What's the relationship between access difficulty (complexity factor) and geographic zone (Phase 22)?
   - Do they compound, or is zone a separate cost adder?

---

## 8. Recommended Implementation Plan

### Phase 21A: UI & Tier Selection (3-4 days)
1. Design tier descriptions with Laurent input (1 day)
2. Build tier selector component (visual cards) (1 day)
3. Build factor checklist component (1 day)
4. Wire to form state, disable old sliders (0.5 day)
5. Add feature flag for tier mode vs legacy mode (0.5 day)

### Phase 21B: Backend Schema & Calculation (2-3 days)
1. Create `complexity_tiers_config.json` with placeholder formulas (0.5 day)
2. Update `HybridQuoteRequest` schema with new fields (0.5 day)
3. Build `complexity_calculator.py` service (1 day)
4. Integrate with ML prediction pipeline (0.5 day)
5. Update LLM merger prompt to use tier descriptions (0.5 day)

### Phase 21C: Validation & Tuning (2-3 days)
1. Extract 50 historical quotes as test dataset (0.5 day)
2. Laurent working session: define formulas from real data (1 day)
3. Run validation tests, adjust formulas (0.5 day)
4. User testing with Steven (0.5 day)
5. Fix issues, document final formulas (0.5 day)

**Total: 7-10 days** (Feb 11 deadline requires 7-day execution)

**Critical path:** Laurent working session must happen by Feb 10 to meet deadline.

---

## 9. Success Criteria Checklist

- [ ] 6 named tiers defined with descriptions for site, roof, and access conditions per tier
- [ ] Tier selector UI (dropdown or visual cards) implemented and replaces current presets
- [ ] Each tier auto-populates a time multiplier from business logic config
- [ ] Factor checklist available with 8 factors: roof pitch, access difficulty, demolition, penetrations, security, material removal, roof sections, previous layers
- [ ] Each factor adds estimated hours (time-based, not percentage-based) to base_time
- [ ] Conservative crew default: system assumes average skill workers (never best-case)
- [ ] Manual override allowed upward only (estimator can add time, system never suggests less)
- [ ] Formula implemented: `total_labor_hours = base_time + complexity_extra_hours; labor_cost = total_labor_hours × crew_cost_per_hour`
- [ ] Backend accepts new tier + factor schema while maintaining backward compatibility
- [ ] Validation tests show ±20% accuracy on 50 historical quotes
- [ ] Laurent approves tier descriptions and time formulas
- [ ] Steven (estimator) successfully generates 5 quotes using new system
- [ ] Rollback plan tested (can revert to old system in <5 minutes)

---

## 10. Resources & References

**Industry Standards:**
- NRCA (National Roofing Contractors Association) labor hour guides
- RSI (Roofing Specifications Institute) complexity classifications
- Quebec construction labor rate databases (CCQ - Commission de la construction du Québec)

**Technical References:**
- Current complexity implementation: `frontend/src/components/estimateur/complexity-presets.tsx`
- Backend schema: `backend/app/schemas/hybrid_quote.py`
- ML model features: `backend/app/models/cortex_config_v3.json`
- Phase 13 context: `.planning/phases/13-hybrid-quote-generation/13-CONTEXT.md`

**Data Sources:**
- Historical quotes: `cortex-data/Quotes Data Export_clean.csv`
- Time tracking: `cortex-data/Quote Time Lines_clean.csv`
- Material data: `cortex-data/Quote Materials_clean.csv`

---

## Conclusion

Phase 21 is a fundamental rebuild of how complexity is captured and calculated. The shift from abstract 0-56 sliders to named tiers with time-based formulas will:

1. **Improve UX**: Roofers select scenarios they recognize, not arbitrary numbers
2. **Increase accuracy**: Hours-based calculations match real labor tracking
3. **Enable transparency**: System explains "Tier 3 = +8 hours because steep pitch + no crane"
4. **Support Phase 22**: Integrates naturally with crew/duration/zone inputs coming next

**Critical success factor:** Laurent's input on business logic. Without accurate base times and factor hours, the system will produce incorrect quotes. Recommend prioritizing the Laurent working session over feature completeness for Feb 11 deadline.

**Recommended approach:** Ship tier UI improvements by Feb 11, deploy formula changes by Feb 13 after validation. This de-risks the sprint while delivering user-facing value on schedule.

---

*Research completed: 2026-02-09*
*Next step: Create 21-CONTEXT.md with user decisions from /gsd:discuss-phase 21*
