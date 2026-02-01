# 14-01 Summary: TypeScript Types, API Client, and Complexity Presets

## What Was Built

### Task 1: TypeScript Types and Zod Schema
- **frontend/src/types/hybrid-quote.ts** — TypeScript interfaces matching backend:
  - `HybridQuoteRequest` with 16 fields including 6 complexity factors
  - `WorkItem`, `MaterialLineItem`, `PricingTier` supporting types
  - `HybridQuoteResponse` with full quote output structure
  - Source literals: `"CBR" | "ML" | "MERGED"` for transparency

- **frontend/src/lib/schemas/hybrid-quote.ts** — Zod validation schema:
  - `hybridQuoteFormSchema` with range validation for all factors
  - Exports `HybridQuoteFormData` type for form state

### Task 2: API Client
- **frontend/src/lib/api/hybrid-quote.ts** — Fetch-based client:
  - `submitHybridQuote(data)` → POST to `/estimate/hybrid`
  - Error handling extracts `detail` message from API errors
  - Uses `NEXT_PUBLIC_API_URL` env var with localhost fallback

### Task 3: Complexity Presets Component
- **frontend/src/components/estimateur/complexity-presets.tsx** — Reusable component:
  - Three presets: Simple (11pts), Modere (28pts), Complexe (44pts)
  - Collapsible "Personnaliser les facteurs" section with 6 sliders
  - Auto-computed aggregate displays as "Total: X/56"
  - Preset clears to custom mode when any slider adjusted
  - French labels throughout (Quebec French)

## Key Decisions

| Decision | Rationale |
|----------|-----------|
| ToggleGroup for presets | Clean single-selection UI from Radix |
| Collapsible default closed | Keeps form clean, power users can expand |
| Preset clears on custom adjustment | Clear indication of custom vs preset mode |
| Sum-based aggregate | Matches backend `complexity_aggregate` validation |

## Artifacts Created

| File | Purpose |
|------|---------|
| frontend/src/types/hybrid-quote.ts | TypeScript interfaces |
| frontend/src/lib/schemas/hybrid-quote.ts | Zod validation |
| frontend/src/lib/api/hybrid-quote.ts | API client |
| frontend/src/components/estimateur/complexity-presets.tsx | UI component |

## Verification

- [x] All files created and committed
- [x] Types match backend HybridQuoteRequest/Response
- [x] API client follows existing patterns
- [x] Component is reusable with controlled props

## What's Next

Plan 14-02: Invoice-style quote result display and form integration
- Wire ComplexityPresets into full quote form
- Create invoice-style result display for HybridQuoteResponse
- Show work items, materials, pricing tiers

---
*Completed: 2026-02-01*
