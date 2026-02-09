# Phase 22: New Estimation Input Fields - Research

**Researched:** 2026-02-09
**Domain:** Form UI components, validation, schema design, i18n
**Confidence:** HIGH

## Summary

Phase 22 adds 7 new input field groups to the full-quote form for capturing estimator inputs that directly affect quote accuracy. The technical challenge is minimal since the form infrastructure, i18n system, and schema patterns are already established in Phase 21. The primary challenge is **business logic gaps** — 4 of 7 field groups require pricing rules and validation logic from Laurent/Amin.

The form uses React Hook Form + Zod validation, shadcn/ui components, and the existing bilingual i18n system. All necessary UI primitives exist except RadioGroup (easily added via shadcn CLI). The schema extension pattern is proven from Phase 21's complexity factors.

**Primary recommendation:** Implement UI and schema structure immediately for all 7 field groups, but use placeholder/symbolic values for fields with undefined business logic. Flag these fields with UI warnings until Laurent provides rules.

## Standard Stack

### Core (Already Integrated)
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| React Hook Form | 7.x | Form state management | Industry standard, already used in full-quote-form.tsx |
| Zod | 3.x | Schema validation | Type-safe validation, already used in hybrid-quote-form schema |
| shadcn/ui | Latest | UI components | Project's UI library, consistent design system |
| Tailwind CSS | 4.x | Styling | Project standard, dark mode ready |

### Supporting (Already in Project)
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| lucide-react | Latest | Icons | All form field icons, already imported |
| @hookform/resolvers | 3.x | Zod + RHF integration | Already configured in full-quote-form.tsx |

### Missing Component
| Component | Installation | Purpose |
|-----------|--------------|---------|
| RadioGroup | `npx shadcn@latest add radio-group` | Duration field, supply chain risk field |

**Installation:**
```bash
cd frontend
npx shadcn@latest add radio-group
```

## Architecture Patterns

### Recommended Field Organization

New fields integrate into existing form structure (full-quote-form.tsx sections):

```
┌─────────────────────────────────────────────┐
│ Project Details Section                     │
│ - Estimator (existing)                      │
│ - Sqft (existing)                           │
│ - Category (existing)                       │
│ - Material lines (existing)                 │
│ - Labor lines (existing)                    │
└─────────────────────────────────────────────┘
┌─────────────────────────────────────────────┐
│ Complexity Section (existing)               │
│ - Tier Selector                             │
│ - Factor Checklist (includes access)        │
└─────────────────────────────────────────────┘
┌─────────────────────────────────────────────┐
│ NEW: Crew & Duration Section                │
│ - Employee count (3 inputs + total)         │
│ - Duration (radio + conditional day picker) │
└─────────────────────────────────────────────┘
┌─────────────────────────────────────────────┐
│ NEW: Location & Client Section              │
│ - Geographic zone (dropdown or manual)      │
│ - Premium client level (dropdown)           │
└─────────────────────────────────────────────┘
┌─────────────────────────────────────────────┐
│ NEW: Equipment & Supply Chain Section       │
│ - Tools/equipment (checklist)               │
│ - Supply chain risk (radio + warning)       │
└─────────────────────────────────────────────┘
┌─────────────────────────────────────────────┐
│ Features Section (existing)                 │
│ - Has chimney (existing)                    │
│ - Has skylights (existing)                  │
│ - Has subcontractors (existing)             │
└─────────────────────────────────────────────┘
```

### Pattern 1: Employee Count Input Group

**What:** 3 number inputs (compagnons/apprentis/manoeuvres) with live total crew display

**Schema:**
```typescript
employee_compagnons: z.number().int().min(0).default(0),
employee_apprentis: z.number().int().min(0).default(0),
employee_manoeuvres: z.number().int().min(0).default(0),
```

**UI:**
```tsx
<div className="grid grid-cols-3 gap-3">
  <FormField name="employee_compagnons" label={t.fullQuote.compagnons} />
  <FormField name="employee_apprentis" label={t.fullQuote.apprentis} />
  <FormField name="employee_manoeuvres" label={t.fullQuote.manoeuvres} />
</div>
<div className="text-sm font-medium">
  {t.fullQuote.totalCrew}: {compagnons + apprentis + manoeuvres}
</div>
```

**Business Logic Gap:** Laurent needs to provide crew suggestion rules (job type × complexity tier → suggested crew composition).

### Pattern 2: Duration Radio + Conditional Day Picker

**What:** Radio buttons for half-day/full-day/multi-day, with number input appearing for multi-day selection

**Schema:**
```typescript
duration_type: z.enum(['half_day', 'full_day', 'multi_day']).default('full_day'),
duration_days: z.number().int().min(1).max(30).optional(),
```

**UI (RadioGroup pattern):**
```tsx
<RadioGroup value={value} onValueChange={onChange}>
  <RadioGroupItem value="half_day" label={t.fullQuote.halfDay} />
  <RadioGroupItem value="full_day" label={t.fullQuote.fullDay} />
  <RadioGroupItem value="multi_day" label={t.fullQuote.multiDay} />
</RadioGroup>
{value === 'multi_day' && (
  <Input type="number" min={2} max={30} label={t.fullQuote.numberOfDays} />
)}
```

**Business Logic Gap:** Laurent needs to define:
- Half-day transport cost absorption rules
- Multi-day per-day discount percentage
- When to suggest multi-day vs full-day (sqft × complexity threshold?)

### Pattern 3: Geographic Zone Dropdown

**What:** Dropdown with 5 Quebec roofing zones affecting travel time/cost

**Schema:**
```typescript
geographic_zone: z.enum([
  'core',           // Core Montreal/Laval
  'secondary',      // Greater Montreal
  'north_premium',  // North Shore, Laurentians
  'extended',       // Outaouais, Mauricie
  'red_flag'        // Remote (Abitibi, Côte-Nord)
]).optional(),
```

**UI:**
```tsx
<Select onValueChange={field.onChange} value={field.value}>
  <SelectItem value="core">{t.fullQuote.zoneCore} (+0%)</SelectItem>
  <SelectItem value="secondary">{t.fullQuote.zoneSecondary} (+5%)</SelectItem>
  <SelectItem value="north_premium">{t.fullQuote.zoneNorthPremium} (+10%)</SelectItem>
  <SelectItem value="extended">{t.fullQuote.zoneExtended} (+15%)</SelectItem>
  <SelectItem value="red_flag">{t.fullQuote.zoneRedFlag} (+25%)</SelectItem>
</Select>
```

**Business Logic Gap:** Google Maps Distance Matrix API integration requires:
- API key budget approval from Amin
- Toitures LV office address as origin
- Distance → zone mapping logic
- Fallback to manual selection if API unavailable

**Auto-suggest approach (if API approved):**
```typescript
// Backend endpoint: POST /api/geocode/zone
// Input: client_address (string)
// Output: { zone: 'core' | 'secondary' | ..., distance_km: number }
```

### Pattern 4: Premium Client Level Dropdown

**What:** 4 service tiers affecting daily surcharge

**Schema:**
```typescript
premium_client_level: z.enum([
  'standard',      // No extras
  'premium_1',     // Daily cleanup
  'premium_2',     // Lawn protection
  'premium_3'      // VIP white-glove
]).default('standard'),
```

**UI:**
```tsx
<Select onValueChange={field.onChange} value={field.value}>
  <SelectItem value="standard">
    {t.fullQuote.premiumStandard} — {t.fullQuote.noExtras}
  </SelectItem>
  <SelectItem value="premium_1">
    {t.fullQuote.premium1} — {t.fullQuote.dailyCleanup} (+$TBD/day)
  </SelectItem>
  <SelectItem value="premium_2">
    {t.fullQuote.premium2} — {t.fullQuote.lawnProtection} (+$TBD/day)
  </SelectItem>
  <SelectItem value="premium_3">
    {t.fullQuote.premium3} — {t.fullQuote.vipWhiteGlove} (+$TBD/day)
  </SelectItem>
</Select>
```

**Business Logic Gap:** Laurent needs to define daily surcharge amounts for each level (e.g., +$50/day for premium_1, +$100/day for premium_2, +$200/day for premium_3).

### Pattern 5: Tools/Equipment Checklist

**What:** Pre-populated checklist of common roofing equipment with symbolic $25/day placeholder prices

**Schema:**
```typescript
equipment_items: z.array(z.string()).default([]),
// Backend calculates cost from equipment_config.json
```

**UI (Checkbox pattern from Phase 21):**
```tsx
<div className="space-y-2">
  {equipmentOptions.map(item => (
    <div key={item.id} className="flex items-center gap-2">
      <Checkbox
        checked={value.includes(item.id)}
        onCheckedChange={(checked) => {
          if (checked) onChange([...value, item.id]);
          else onChange(value.filter(x => x !== item.id));
        }}
      />
      <label>{item.label}</label>
      <span className="text-xs text-primary">{item.daily_cost}/jour</span>
    </div>
  ))}
</div>
```

**Equipment Config (backend/app/models/equipment_config.json):**
```json
{
  "equipment_items": [
    { "id": "crane", "name_fr": "Grue", "name_en": "Crane", "daily_cost": 25 },
    { "id": "scaffolding", "name_fr": "Échafaudage", "name_en": "Scaffolding", "daily_cost": 25 },
    { "id": "dumpster", "name_fr": "Conteneur", "name_en": "Dumpster", "daily_cost": 25 },
    { "id": "generator", "name_fr": "Génératrice", "name_en": "Generator", "daily_cost": 25 },
    { "id": "compressor", "name_fr": "Compresseur", "name_en": "Compressor", "daily_cost": 25 }
  ]
}
```

**Note:** $25/day is symbolic placeholder. Laurent needs to provide real daily rental costs per item.

### Pattern 6: Supply Chain Risk Radio

**What:** Radio buttons with visual warning for extended/import lead times

**Schema:**
```typescript
supply_chain_risk: z.enum([
  'standard',   // ≤1 week
  'extended',   // 2-4 weeks
  'import'      // 6-8 weeks
]).default('standard'),
```

**UI:**
```tsx
<RadioGroup value={value} onValueChange={onChange}>
  <RadioGroupItem value="standard">
    {t.fullQuote.supplyStandard} (≤1 {t.fullQuote.week})
  </RadioGroupItem>
  <RadioGroupItem value="extended">
    {t.fullQuote.supplyExtended} (2-4 {t.fullQuote.weeks})
  </RadioGroupItem>
  <RadioGroupItem value="import">
    {t.fullQuote.supplyImport} (6-8 {t.fullQuote.weeks})
  </RadioGroupItem>
</RadioGroup>
{(value === 'extended' || value === 'import') && (
  <div className="flex items-center gap-2 text-warning">
    <AlertCircle className="size-4" />
    <span className="text-sm">{t.fullQuote.supplyWarning}</span>
  </div>
)}
```

**Note:** No pricing impact currently defined. Laurent may want to add holding cost or rush fees for extended lead times.

### Pattern 7: Access Difficulty Integration

**Status:** Already implemented in Phase 21 (factor-checklist.tsx)

Access difficulty checklist already exists with 6 items:
- no_crane (no crane access) — +6h
- narrow_driveway — +2h
- street_blocking — +3h
- high_elevation (3+ stories) — +4h
- difficult_terrain — +2h
- no_material_drop — +3h

**No changes needed for Phase 22.** This requirement is satisfied by existing Phase 21 implementation.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Form validation | Custom validation logic | Zod schemas + React Hook Form | Type-safe, already integrated |
| Radio buttons | Custom radio component | shadcn RadioGroup | Accessible, keyboard nav, consistent styling |
| Conditional rendering | Complex state management | React Hook Form watch() | Already in use for tier/factor dependencies |
| i18n key management | Manual translation objects | Existing fr.ts/en.ts pattern | Consistent with Phase 21 additions |
| Schema versioning | Backend breaking changes | Optional fields with defaults | Backward compatible with existing quotes |

**Key insight:** Form infrastructure from Phase 21 handles all new field types. Zero custom form logic needed.

## Common Pitfalls

### Pitfall 1: Breaking Backend Compatibility

**What goes wrong:** Adding required fields to HybridQuoteRequest breaks existing API clients and old quote data

**Why it happens:** Frontend developer adds new field, assumes backend always provides it

**How to avoid:**
- Mark ALL new fields as optional in Pydantic schema (Optional[T])
- Provide sensible defaults in schema definition
- Backend validation checks for None, applies defaults
- Never assume client sends new fields

**Warning signs:**
- ValidationError on old quote submission
- 422 Unprocessable Entity on form submit
- Database migration fails on existing records

### Pitfall 2: Business Logic in UI

**What goes wrong:** Hardcoding pricing multipliers (e.g., "north_premium = +10%") in frontend

**Why it happens:** Developer wants to show price preview, doesn't have backend config

**How to avoid:**
- All pricing logic lives in backend (complexity_calculator.py or new pricing_calculator.py)
- Frontend displays symbolic hints only ("usually +10-15%")
- Real calculations happen server-side with authoritative config
- Frontend gets final numbers from API response

**Warning signs:**
- Pricing constants defined in .tsx files
- Multiplication logic in React components
- Estimator sees different number than QuoteResult

### Pitfall 3: Missing i18n Keys

**What goes wrong:** Form deploys with "t.fullQuote.compagnons" showing as raw key instead of translated text

**Why it happens:** Developer adds frontend field but forgets to update fr.ts and en.ts

**How to avoid:**
- Add ALL new i18n keys before implementing components
- Test in both languages before committing
- Use TypeScript's type safety (DeepStringify checks missing keys)

**Warning signs:**
- Raw keys appearing in UI (t.something.newKey)
- TypeScript error: Property 'newKey' does not exist on type...
- FR works but EN shows untranslated text

### Pitfall 4: Google Maps API Cost Explosion

**What goes wrong:** Distance Matrix API called on every form keystroke, rack up $1000+ monthly bill

**Why it happens:** Developer adds onChange handler to address field, triggers API per character

**How to avoid:**
- Debounce API calls (500ms delay after last keystroke)
- Cache address → zone mapping (localStorage or Supabase cache table)
- Add manual override dropdown (bypass API if needed)
- Monitor API usage via Google Cloud Console

**Warning signs:**
- Network tab shows 50+ API calls for one address
- Amin reports unexpected GCP charges
- Address autocomplete feels sluggish

### Pitfall 5: Undefined Business Logic Shows "TBD"

**What goes wrong:** Form goes live with "Premium 1: +$TBD/day" placeholders, estimators guess values

**Why it happens:** Frontend rushes deployment before Laurent provides pricing rules

**How to avoid:**
- Add visual warning badges for fields with undefined logic
- Disable "Generate Quote" button if critical fields have placeholder values
- Log which fields lack business rules in .planning/STATE.md
- Schedule follow-up meeting with Laurent to collect missing rules

**Warning signs:**
- Estimators asking "what should I put here?"
- Quote totals vary wildly between estimators
- Feedback shows "Premium pricing doesn't make sense"

## Code Examples

### Employee Count with Total Display

```tsx
// Source: Pattern adapted from Phase 21 factor-checklist.tsx (number input)
const compagnons = form.watch("employee_compagnons");
const apprentis = form.watch("employee_apprentis");
const manoeuvres = form.watch("employee_manoeuvres");
const totalCrew = compagnons + apprentis + manoeuvres;

<Card>
  <CardHeader>
    <CardTitle>{t.fullQuote.crewComposition}</CardTitle>
  </CardHeader>
  <CardContent className="space-y-4">
    <div className="grid grid-cols-3 gap-3">
      <FormField
        control={form.control}
        name="employee_compagnons"
        render={({ field }) => (
          <FormItem>
            <FormLabel>{t.fullQuote.compagnons}</FormLabel>
            <FormControl>
              <Input
                type="number"
                min={0}
                max={10}
                {...field}
                onChange={(e) => field.onChange(parseInt(e.target.value) || 0)}
              />
            </FormControl>
          </FormItem>
        )}
      />
      {/* Repeat for apprentis, manoeuvres */}
    </div>
    <div className="flex justify-between items-center pt-2 border-t">
      <span className="text-sm font-medium">{t.fullQuote.totalCrew}</span>
      <span className="text-sm font-semibold text-primary">
        {totalCrew} {t.fullQuote.workers}
      </span>
    </div>
  </CardContent>
</Card>
```

### Duration Radio with Conditional Day Picker

```tsx
// Source: shadcn RadioGroup documentation pattern
const durationType = form.watch("duration_type");

<FormField
  control={form.control}
  name="duration_type"
  render={({ field }) => (
    <FormItem>
      <FormLabel>{t.fullQuote.projectDuration}</FormLabel>
      <FormControl>
        <RadioGroup onValueChange={field.onChange} value={field.value}>
          <div className="flex items-center space-x-2">
            <RadioGroupItem value="half_day" id="half_day" />
            <label htmlFor="half_day" className="text-sm cursor-pointer">
              {t.fullQuote.halfDay} (≤5h)
            </label>
          </div>
          <div className="flex items-center space-x-2">
            <RadioGroupItem value="full_day" id="full_day" />
            <label htmlFor="full_day" className="text-sm cursor-pointer">
              {t.fullQuote.fullDay} (≤10h)
            </label>
          </div>
          <div className="flex items-center space-x-2">
            <RadioGroupItem value="multi_day" id="multi_day" />
            <label htmlFor="multi_day" className="text-sm cursor-pointer">
              {t.fullQuote.multiDay}
            </label>
          </div>
        </RadioGroup>
      </FormControl>
    </FormItem>
  )}
/>

{durationType === 'multi_day' && (
  <FormField
    control={form.control}
    name="duration_days"
    render={({ field }) => (
      <FormItem>
        <FormLabel>{t.fullQuote.numberOfDays}</FormLabel>
        <FormControl>
          <Input
            type="number"
            min={2}
            max={30}
            placeholder="3"
            {...field}
            onChange={(e) => field.onChange(parseInt(e.target.value) || 2)}
          />
        </FormControl>
      </FormItem>
    )}
  />
)}
```

### Supply Chain Risk with Warning

```tsx
// Source: Pattern from existing AlertCircle usage in full-quote-form.tsx
const supplyRisk = form.watch("supply_chain_risk");

<FormField
  control={form.control}
  name="supply_chain_risk"
  render={({ field }) => (
    <FormItem>
      <FormLabel>{t.fullQuote.supplyChainRisk}</FormLabel>
      <FormControl>
        <RadioGroup onValueChange={field.onChange} value={field.value}>
          <div className="flex items-center space-x-2">
            <RadioGroupItem value="standard" id="supply_standard" />
            <label htmlFor="supply_standard" className="text-sm cursor-pointer">
              {t.fullQuote.supplyStandard} (≤1 {t.fullQuote.week})
            </label>
          </div>
          <div className="flex items-center space-x-2">
            <RadioGroupItem value="extended" id="supply_extended" />
            <label htmlFor="supply_extended" className="text-sm cursor-pointer">
              {t.fullQuote.supplyExtended} (2-4 {t.fullQuote.weeks})
            </label>
          </div>
          <div className="flex items-center space-x-2">
            <RadioGroupItem value="import" id="supply_import" />
            <label htmlFor="supply_import" className="text-sm cursor-pointer">
              {t.fullQuote.supplyImport} (6-8 {t.fullQuote.weeks})
            </label>
          </div>
        </RadioGroup>
      </FormControl>
    </FormItem>
  )}
/>

{(supplyRisk === 'extended' || supplyRisk === 'import') && (
  <div className="flex items-center gap-2 rounded-lg border border-warning/50 bg-warning/10 p-3 text-warning">
    <AlertCircle className="size-5 shrink-0" />
    <p className="text-sm">{t.fullQuote.supplyWarning}</p>
  </div>
)}
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Manual crew entry | Employee role breakdown | Phase 22 | Enables crew cost calculation by role |
| Implicit duration | Explicit duration field | Phase 22 | Captures half-day transport absorption rules |
| Travel cost guesswork | Geographic zone pricing | Phase 22 | Consistent zone-based surcharges |
| One service level | 4 premium tiers | Phase 22 | Upsell opportunities, service differentiation |
| Equipment cost buried | Itemized equipment | Phase 22 | Transparent rental costs |
| No supply chain risk | Lead time tracking | Phase 22 | Client expectation management |

**Deprecated/outdated:**
- None — Phase 22 is additive, no existing fields removed or replaced

## Open Questions

### 1. Google Maps API Budget

**What we know:**
- Distance Matrix API costs $5-10 per 1000 requests
- Toitures LV estimates ~200-300 quotes/month
- Potential cost: $1-3/month if every quote geocodes

**What's unclear:**
- Does Amin have GCP billing set up for Cortex project?
- Is auto-geocoding worth the cost vs manual dropdown?
- Should we cache address → zone mapping to reduce API calls?

**Recommendation:**
- Implement manual zone dropdown first (Phase 22)
- Build geocoding as optional Phase 23+ enhancement if Amin approves budget
- Add cache layer (Supabase table) if geocoding goes live

### 2. Employee Count Suggestions

**What we know:**
- Estimators currently guess crew composition
- Laurent mentioned "complexity affects crew size" (Phase 21 notes)

**What's unclear:**
- Job type × complexity tier → suggested crew formula
- When to suggest 2 compagnons vs 1 compagnon + 1 apprenti
- Does category (Bardeaux vs Elastomère) affect crew composition?

**Recommendation:**
- Launch with manual entry (no suggestions)
- Log estimator choices to identify patterns
- Schedule follow-up with Laurent to define suggestion rules

### 3. Duration Pricing Impact

**What we know:**
- Half-day jobs may absorb transport cost
- Multi-day jobs may get per-day discount

**What's unclear:**
- At what threshold does half-day become full-day? (5h or 6h?)
- Multi-day discount: % per day? Flat discount?
- Does discount apply per calendar day or per work day?

**Recommendation:**
- Add duration field to schema (capture data)
- Backend logs duration but doesn't apply pricing yet
- Laurent provides rules → backend applies in Phase 23 or later

### 4. Premium Client Surcharge Amounts

**What we know:**
- 4 tiers exist (standard, premium 1, 2, 3)
- Each tier adds services (daily cleanup, lawn protection, white-glove)

**What's unclear:**
- Daily surcharge amount per tier (e.g., +$50/day, +$100/day, +$200/day?)
- Are surcharges per day or flat fee per job?
- Does premium level affect materials cost or labor only?

**Recommendation:**
- Use placeholder "$TBD/day" in UI
- Add visual warning: "Premium pricing not yet configured"
- Collect Laurent's pricing before Phase 22 deployment

## Sources

### Primary (HIGH confidence)

**Codebase analysis:**
- `/frontend/src/components/estimateur/full-quote-form.tsx` — Form structure, existing patterns
- `/frontend/src/components/estimateur/tier-selector.tsx` — Visual selector UI pattern
- `/frontend/src/components/estimateur/factor-checklist.tsx` — Checkbox/number input patterns
- `/frontend/src/lib/i18n/context.tsx` — i18n system architecture
- `/frontend/src/lib/i18n/fr.ts` — French translation structure (318 lines)
- `/frontend/src/lib/schemas/hybrid-quote.ts` — Zod schema validation pattern
- `/backend/app/schemas/hybrid_quote.py` — Pydantic schema structure (666 lines)
- `/backend/app/services/complexity_calculator.py` — Config-driven calculation pattern

**shadcn/ui documentation:**
- RadioGroup component: https://ui.shadcn.com/docs/components/radio-group
- Checkbox component: https://ui.shadcn.com/docs/components/checkbox
- Select component: https://ui.shadcn.com/docs/components/select
- Form patterns: https://ui.shadcn.com/docs/components/form

### Secondary (MEDIUM confidence)

**Phase documentation:**
- `.planning/phases/21-complexity-system-rebuild/21-RESEARCH.md` — Factor checklist patterns
- `.planning/ROADMAP.md` — Phase 22 requirements and dependencies
- `.planning/STATE.md` — Known business logic gaps

### Tertiary (LOW confidence)

**Google Maps pricing:**
- Distance Matrix API: $5 per 1000 requests (standard pricing)
- Geocoding API: $5 per 1000 requests (alternative for simple zone lookup)
- Source: Google Cloud pricing calculator (not verified against current rates)

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — All libraries already integrated, RadioGroup is standard shadcn component
- Architecture: HIGH — Form patterns proven in Phase 21, zero architectural risk
- Business logic: LOW — 4 of 7 field groups need Laurent input before pricing can be implemented
- i18n keys: HIGH — Pattern established, just needs 40-50 new translation keys

**Research date:** 2026-02-09
**Valid until:** 2026-03-09 (30 days — stable stack, no fast-moving dependencies)

**Critical path blockers:**
1. RadioGroup component installation (5 min task)
2. Laurent/Amin business logic collection (40-60 min meeting)
3. i18n key additions (15-20 min per language)

**Non-blockers (can launch without):**
- Google Maps API integration (manual dropdown works)
- Employee count suggestions (manual entry works)
- Duration pricing rules (capture data, apply rules later)
- Premium surcharge amounts (use "TBD" placeholder with warning)
