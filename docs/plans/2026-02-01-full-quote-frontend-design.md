# Full Quote Frontend Integration Design

**Date:** 2026-02-01
**Status:** Approved
**Phase:** 14 (Frontend Integration for Hybrid Quotes)

## Overview

Wire up the `/estimate/hybrid` endpoint to the frontend "Soumission Complète" tab, enabling full quote generation with work items, materials totals, and professional invoice-style output.

## Problem Statement

Yasmine's feedback: "It's like a 'price generator' but the client really needs a quote generator, with the specifics in his quotes, just like the ones he's done in the past."

Current state: Frontend only shows price + reasoning
Required: Full quotes with work items, totals, and export capabilities

## Decisions Made

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

## Form Design

### Complexity Presets

```
┌─────────────────────────────────────────────────┐
│ Complexité du travail                           │
│                                                 │
│   ○ Simple        ● Modéré        ○ Complexe   │
│                                                 │
│   ▶ Personnaliser les facteurs                 │
└─────────────────────────────────────────────────┘
```

### Preset Values

| Factor | Simple | Modéré | Complexe |
|--------|--------|--------|----------|
| Difficulté d'accès (0-10) | 2 | 5 | 8 |
| Pente du toit (0-8) | 2 | 4 | 6 |
| Pénétrations (0-10) | 1 | 5 | 8 |
| Retrait de matériaux (0-8) | 2 | 4 | 6 |
| Préoccupations de sécurité (0-10) | 2 | 5 | 8 |
| Contraintes de délai (0-10) | 2 | 5 | 8 |

### Full Form Fields

Existing (unchanged):
- Square footage (sqft)
- Category dropdown
- Material lines count
- Labor lines count
- Subcontractors toggle

New:
- Complexity preset selector (Simple/Modéré/Complexe)
- Collapsible 6-factor override section

## Output Display

### Internal View (for Laurent)

```
┌─────────────────────────────────────────────────────────────┐
│  ⚠️ Confiance: 42% — Vérification recommandée              │  ← Only if < 50%
│                                                             │
│  ══════════════════════════════════════════════════════    │
│                    SOUMISSION                               │
│  ══════════════════════════════════════════════════════    │
│                                                             │
│  Catégorie: Bardeaux                                        │
│  Superficie: 1,500 pi²                                      │
│                                                             │
│  ──────────────────────────────────────────────────────    │
│  TRAVAUX                                                    │
│  ──────────────────────────────────────────────────────    │
│  • Retirer les bardeaux existants              8.0 hrs     │
│  • Installer la membrane de protection         4.0 hrs     │
│  • Poser les nouveaux bardeaux               12.0 hrs     │
│  • Installer les solins                        3.0 hrs     │
│  • Nettoyage et inspection finale              2.0 hrs     │
│                                                             │
│  ──────────────────────────────────────────────────────    │
│  SOMMAIRE                                                   │
│  ──────────────────────────────────────────────────────    │
│  Matériaux                                      8,500 $    │
│  Main-d'œuvre (29.0 hrs)                        6,500 $    │
│                                                             │
│  ══════════════════════════════════════════════════════    │
│  TOTAL                                         15,000 $    │
│  ══════════════════════════════════════════════════════    │
│                                                             │
│  💡 Raisonnement                               [▼ Expand]   │
│  ──────────────────────────────────────────────────────    │
│                                                             │
│  [📄 Exporter PDF]  [📧 Envoyer]  [💾 Sauvegarder]         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Client PDF View

Same layout but:
- No labor hours shown (just work item names)
- No confidence warning
- No reasoning section
- Professional header with Toiture LV branding

## Action Buttons

### Exporter PDF
- Generates client-facing PDF (no hours)
- Downloads immediately
- Filename: `Soumission-{category}-{date}.pdf`

### Envoyer
- Opens modal with email input
- Pre-fills subject: "Soumission Toiture LV — {category}"
- Attaches PDF automatically
- Sends via backend

### Sauvegarder
- Saves to database as draft
- Appears in Historique tab with status "Brouillon"
- Can be edited and re-generated later

## Data Flow

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Form Input    │────▶│  POST /estimate │────▶│  Quote Display  │
│                 │     │     /hybrid     │     │                 │
│ • sqft          │     │                 │     │ • Work items    │
│ • category      │     │ Returns:        │     │ • Materials $   │
│ • 6 factors     │     │ • work_items    │     │ • Total         │
│ • presets       │     │ • materials     │     │ • Confidence    │
└─────────────────┘     │ • pricing_tiers │     └────────┬────────┘
                        │ • confidence    │              │
                        │ • reasoning     │              ▼
                        └─────────────────┘     ┌─────────────────┐
                                                │    Actions      │
                                                │                 │
                        ┌───────────────────────┤ • Export PDF    │
                        │                       │ • Send email    │
                        ▼                       │ • Save draft    │
                ┌───────────────┐               └─────────────────┘
                │  PDF Service  │                        │
                │               │                        ▼
                │ Client layout │               ┌─────────────────┐
                │ (no hours)    │               │    Supabase     │
                └───────────────┘               │                 │
                                                │ quotes table    │
                                                │ status: draft   │
                                                └─────────────────┘
```

## New Files

### Frontend

| File | Purpose |
|------|---------|
| `lib/api/hybrid-quote.ts` | API client for `/estimate/hybrid` |
| `lib/schemas/hybrid-quote.ts` | Zod schemas matching backend |
| `components/estimateur/full-quote-form.tsx` | Replace placeholder with real form |
| `components/estimateur/quote-result.tsx` | Invoice-style display component |
| `components/estimateur/complexity-presets.tsx` | Preset selector + 6 sliders |
| `components/estimateur/quote-actions.tsx` | Export/Send/Save buttons |
| `lib/pdf/quote-generator.ts` | Client-side PDF generation |

### Backend

| Endpoint | Purpose |
|----------|---------|
| `POST /quotes` | Save draft quote to database |
| `POST /quotes/{id}/send` | Send quote via email |
| `GET /quotes/{id}/pdf` | Generate PDF server-side (optional) |

## Implementation Phases

### Phase 14A: Core Quote Generation
- Form with presets + 6-factor override
- Call `/estimate/hybrid`
- Display invoice-style result
- Confidence warning

**Testable:** Generate quotes and verify work items make sense

### Phase 14B: PDF Export
- Client-facing layout (no hours)
- Download button
- Uses `@react-pdf/renderer` or similar

**Testable:** Verify PDF format looks professional

### Phase 14C: Save & Send
- Save to Supabase `quotes` table
- Drafts appear in Historique
- Email sending via backend

**Testable:** Full end-to-end workflow

## Estimated Scope

- ~400 lines frontend (form, display, actions)
- ~150 lines PDF generation
- ~100 lines backend (save/send endpoints)
- ~50 lines database schema

## Open Questions

None — all decisions made during brainstorming.

---

*Design approved: 2026-02-01*
