# Phase 14: Full Quote Frontend Integration - Context

**Created:** 2026-02-01
**Source:** Brainstorming session with user

## Design Decisions Made

All decisions documented in: `docs/plans/2026-02-01-full-quote-frontend-design.md`

### Summary of Key Decisions

| Aspect | Decision |
|--------|----------|
| Work items | 3-6 high-level tasks (e.g., "Remove existing shingles") |
| Materials | Total only, not itemized list |
| Pricing | One price (Standard tier from backend's 3 tiers) |
| Complexity input | Presets (Simple/Modéré/Complexe) + optional 6-factor override |
| Output layout | Invoice-style, printable format |
| Actions | View + PDF export + Send email + Save draft — all from launch |
| Confidence | Prominent warning banner when < 50% |
| Internal vs Client | Internal shows labor hours; client PDF hides them |

### Complexity Preset Values

| Factor | Simple | Modéré | Complexe |
|--------|--------|--------|----------|
| Difficulté d'accès (0-10) | 2 | 5 | 8 |
| Pente du toit (0-8) | 2 | 4 | 6 |
| Pénétrations (0-10) | 1 | 5 | 8 |
| Retrait de matériaux (0-8) | 2 | 4 | 6 |
| Préoccupations de sécurité (0-10) | 2 | 5 | 8 |
| Contraintes de délai (0-10) | 2 | 5 | 8 |

### Backend Endpoint

Uses existing `POST /estimate/hybrid` from Phase 13:
- Request: `HybridQuoteRequest` with 6 complexity factors
- Response: `HybridQuoteResponse` with work items, materials, pricing tiers

### Files to Create

| File | Purpose |
|------|---------|
| `frontend/src/types/hybrid-quote.ts` | TypeScript types matching backend |
| `frontend/src/lib/api/hybrid-quote.ts` | API client for `/estimate/hybrid` |
| `frontend/src/components/estimateur/complexity-presets.tsx` | Preset selector + 6 sliders |
| `frontend/src/components/estimateur/quote-result.tsx` | Invoice-style display |
| `frontend/src/components/estimateur/quote-actions.tsx` | Export/Send/Save buttons |
| `frontend/src/lib/pdf/quote-template.tsx` | Client-side PDF generation |

### Files to Modify

| File | Change |
|------|--------|
| `frontend/src/lib/i18n/fr.ts` | Add fullQuote section |
| `frontend/src/components/estimateur/full-quote-form.tsx` | Replace placeholder |

### Implementation Phases

- **14A:** Core Quote Generation (form + display)
- **14B:** PDF Export
- **14C:** Save & Send (deferred - needs backend endpoints)

---

*Context captured: 2026-02-01*
