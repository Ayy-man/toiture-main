---
phase: 22-new-estimation-input-fields
plan: 01
subsystem: schemas, config, i18n, ui-components
tags:
  - pydantic-schemas
  - zod-validation
  - typescript-types
  - i18n-translations
  - shadcn-components
  - equipment-config
dependency_graph:
  requires: []
  provides:
    - backend_estimation_fields
    - frontend_estimation_schemas
    - equipment_config_json
    - estimation_i18n_keys
    - radio_group_component
  affects:
    - full-quote-form
    - estimation-ui
tech_stack:
  added: []
  patterns:
    - optional-fields-backward-compatibility
    - enum-field-validation
    - bilingual-equipment-config
key_files:
  created:
    - backend/app/models/equipment_config.json
    - frontend/src/components/ui/radio-group.tsx
  modified:
    - backend/app/schemas/hybrid_quote.py
    - frontend/src/lib/schemas/hybrid-quote.ts
    - frontend/src/types/hybrid-quote.ts
    - frontend/src/lib/i18n/fr.ts
    - frontend/src/lib/i18n/en.ts
decisions:
  - "All 7 new field groups added as Optional with None defaults for backward compatibility"
  - "Equipment config uses bilingual names (name_fr/name_en) for i18n support"
  - "All equipment costs set to $25/day placeholder - awaiting Laurent's real rental costs"
  - "Enum validations added via field_validator for duration_type, geographic_zone, premium_client_level, supply_chain_risk"
  - "~50 i18n keys organized into 3 logical sections: Crew & Duration, Location & Client, Equipment & Supply Chain"
metrics:
  duration: "6 minutes"
  tasks_completed: 2
  files_modified: 7
  commits: 2
  completed_date: "2026-02-09"
---

# Phase 22 Plan 01: Schema Fields, Config, i18n & Components Summary

**One-liner:** Added 7 new optional field groups to backend/frontend schemas, equipment config JSON with 5 items, ~50 bilingual i18n keys, and RadioGroup shadcn component for Phase 22 estimation fields.

## Execution Summary

Successfully added all data layer infrastructure for 6 new estimation field groups (employee count, duration, geographic zone, premium client level, tools/equipment, supply chain risk). All fields integrated with full backward compatibility - existing quotes continue to work with None/default values.

## What Was Built

### Backend Schema (Pydantic)
**File:** `backend/app/schemas/hybrid_quote.py`

Added 7 new Optional fields to `HybridQuoteRequest`:
1. **Employee count** (3 fields):
   - `employee_compagnons` (0-20): Number of journeyman roofers
   - `employee_apprentis` (0-20): Number of apprentice roofers
   - `employee_manoeuvres` (0-20): Number of laborers

2. **Duration** (2 fields):
   - `duration_type`: enum (half_day | full_day | multi_day)
   - `duration_days` (1-30): Number of days for multi-day projects

3. **Geographic zone** (1 field):
   - `geographic_zone`: enum (core | secondary | north_premium | extended | red_flag)

4. **Premium client level** (1 field):
   - `premium_client_level`: enum (standard | premium_1 | premium_2 | premium_3)

5. **Equipment items** (1 field):
   - `equipment_items`: List[str] - IDs from equipment_config.json

6. **Supply chain risk** (1 field):
   - `supply_chain_risk`: enum (standard | extended | import)

Added 4 field validators for enum constraints (duration_type, geographic_zone, premium_client_level, supply_chain_risk).

All fields use `Optional[T] = Field(default=None, ...)` for backward compatibility.

### Equipment Configuration
**File:** `backend/app/models/equipment_config.json`

Created JSON config with 5 equipment items:
- Crane (Grue)
- Scaffolding (Echafaudage)
- Dumpster (Conteneur a dechets)
- Generator (Generatrice)
- Compressor (Compresseur)

Each item has:
- `id`: string identifier
- `name_fr`: French display name
- `name_en`: English display name
- `daily_cost`: float (all set to $25.00 placeholder)

Note: All costs are symbolic placeholders awaiting Laurent's real rental costs.

### Frontend Zod Schema
**File:** `frontend/src/lib/schemas/hybrid-quote.ts`

Added matching fields with Zod validation:
- Employee fields: `z.number().int().min(0).max(20).default(0)`
- Duration type: `z.enum(['half_day', 'full_day', 'multi_day']).default('full_day')`
- Duration days: `z.number().int().min(1).max(30).optional()`
- Geographic zone: `z.enum(['core', 'secondary', 'north_premium', 'extended', 'red_flag']).optional()`
- Premium client: `z.enum(['standard', 'premium_1', 'premium_2', 'premium_3']).default('standard')`
- Equipment items: `z.array(z.string()).default([])`
- Supply chain risk: `z.enum(['standard', 'extended', 'import']).default('standard')`

Defaults ensure form has sensible initial values (full_day, standard service, standard supply chain, 0 employees).

### TypeScript Types
**File:** `frontend/src/types/hybrid-quote.ts`

Extended `HybridQuoteRequest` interface with 9 new optional fields matching backend Pydantic model:
```typescript
employee_compagnons?: number;
employee_apprentis?: number;
employee_manoeuvres?: number;
duration_type?: 'half_day' | 'full_day' | 'multi_day';
duration_days?: number;
geographic_zone?: 'core' | 'secondary' | 'north_premium' | 'extended' | 'red_flag';
premium_client_level?: 'standard' | 'premium_1' | 'premium_2' | 'premium_3';
equipment_items?: string[];
supply_chain_risk?: 'standard' | 'extended' | 'import';
```

### i18n Translations
**Files:** `frontend/src/lib/i18n/fr.ts` + `frontend/src/lib/i18n/en.ts`

Added ~50 new keys (25+ per language) under `fullQuote` object, organized into 3 sections:

#### Crew & Duration (11 keys)
- Section heading: `crewDuration`, `crewDurationDescription`
- Worker types: `compagnons`, `apprentis`, `manoeuvres`
- Crew summary: `totalCrew`, `workers`
- Duration: `projectDuration`, `halfDay`, `fullDay`, `multiDay`, `numberOfDays`

#### Location & Client (19 keys)
- Section heading: `locationClient`, `locationClientDescription`
- Geographic zone: `geographicZone`, `selectZone`, 5 zone options
- Premium levels: `premiumClientLevel`, 4 premium options with descriptions
- Pricing info: `surchargePerDay`, `surchargeTBD`

#### Equipment & Supply Chain (17 keys)
- Section heading: `equipmentSupplyChain`, `equipmentSupplyChainDescription`
- Equipment: `toolsEquipment`, `dailyCost`
- Supply chain: `supplyChainRisk`, 3 risk levels with descriptions
- Warnings: `supplyWarning`, time units (`week`, `weeks`)
- Placeholder notice: `placeholderPricing`

All translations are real Quebec French (not placeholders), using proper terminology from Toitures LV domain.

### UI Component
**File:** `frontend/src/components/ui/radio-group.tsx`

Added shadcn RadioGroup component for form UI:
- `RadioGroup`: container component with grid layout
- `RadioGroupItem`: individual radio button with check icon indicator
- Uses @radix-ui/react-radio-group primitives
- Styled with Tailwind classes matching Lyra theme

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] shadcn CLI hanging**
- **Found during:** Task 1 - RadioGroup installation
- **Issue:** `npx shadcn@latest add radio-group --yes` command hung indefinitely (process running but no output after 30+ seconds)
- **Fix:** Manually created radio-group.tsx component with standard shadcn implementation from official template
- **Files modified:** `frontend/src/components/ui/radio-group.tsx`
- **Commit:** c121573 (included in Task 1 commit)
- **Rationale:** Blocking issue preventing task completion. Manual component creation provides identical functionality to CLI-generated version.

## Verification Results

All verification steps passed:

1. **Backward compatibility**: `HybridQuoteRequest(sqft=1000, category='Bardeaux', complexity_tier=2)` validates successfully with all new fields returning None
2. **New fields validation**: Request with all new fields populated validates correctly
3. **Equipment config**: JSON is valid with 5 items
4. **Frontend TypeScript**: `npx tsc --noEmit` passes with zero errors
5. **RadioGroup component**: File exists and exports RadioGroup + RadioGroupItem
6. **i18n keys**: Both fr.ts and en.ts have matching keys (verified via grep count: 7/7)

## Self-Check: PASSED

### Created Files Exist
```bash
✓ backend/app/models/equipment_config.json
✓ frontend/src/components/ui/radio-group.tsx
```

### Commits Exist
```bash
✓ c121573: feat(22-01): add 7 new estimation fields to backend schema, equipment config, and RadioGroup
✓ 1d813e4: feat(22-01): add frontend Zod schema, TypeScript types, and i18n keys for 7 new fields
```

### Modified Files Contain Expected Content
```bash
✓ backend/app/schemas/hybrid_quote.py contains "employee_compagnons"
✓ frontend/src/lib/schemas/hybrid-quote.ts contains "employee_compagnons"
✓ frontend/src/types/hybrid-quote.ts contains "employee_compagnons"
✓ frontend/src/lib/i18n/fr.ts contains "compagnons: \"Compagnons\""
✓ frontend/src/lib/i18n/en.ts contains "compagnons: \"Journeymen\""
```

## Business Logic Gaps

**Equipment daily costs**: All 5 equipment items have placeholder $25/day costs. Laurent needs to provide:
- Real crane rental cost
- Real scaffolding rental cost
- Real dumpster rental cost
- Real generator rental cost
- Real compressor rental cost

**Premium client surcharges**: i18n includes "surchargeTBD" (Rate to be confirmed). Laurent needs to specify daily surcharge amounts for Premium 1, 2, 3 levels.

These gaps do NOT block Phase 22 Plan 02 (UI implementation). Form can display placeholder values, and config can be updated later without code changes.

## Impact on Codebase

### Schema Compatibility
- Existing `/estimate/hybrid` endpoint accepts new fields as Optional
- Old quotes (without new fields) still validate and process correctly
- New quotes can include any combination of new fields
- Frontend defaults ensure forms always submit valid data

### i18n Coverage
- Full bilingual support for all new estimation features
- Organized key structure matches UI section layout
- French translations use Quebec terminology (compagnons, échafaudage, etc.)
- English translations use industry-standard terms (journeymen, scaffolding, etc.)

### Type Safety
- Frontend TypeScript types mirror backend Pydantic exactly
- Zod schema enforces validation before API submission
- Enum types prevent invalid option values
- Array types for equipment items allow multi-select

## Next Steps

**Phase 22 Plan 02** (UI Implementation) can proceed immediately:
1. Build CrewDuration section with employee count inputs and duration radio group
2. Build LocationClient section with geographic zone select and premium level radio group
3. Build EquipmentSupplyChain section with equipment checkboxes and supply chain radio group
4. Integrate sections into full quote form
5. Wire up form state to new Zod schema fields

All schema, types, i18n, and components are ready. No blockers for Plan 02.

## Lessons Learned

1. **shadcn CLI reliability**: CLI tools can hang on large projects. Always have manual fallback for component generation.
2. **Bilingual config pattern**: Separate name_fr/name_en fields in JSON enables easy i18n without code changes.
3. **Placeholder values strategy**: Symbolic pricing values with JSON config comments enable future updates without developer involvement.
4. **i18n organization**: Section-based key grouping (crew/location/equipment) mirrors UI structure and aids future maintenance.

---

**Status:** Plan complete - all tasks executed, verified, and committed. Ready for Phase 22 Plan 02 (UI implementation).
