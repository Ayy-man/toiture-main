---
phase: 24-export-send-red-flags
plan: 01
subsystem: frontend-exports
tags: [docx, export, bilingual, word-documents]
dependency_graph:
  requires: [14-03-pdf-export, 16-01-i18n]
  provides: [docx-export-function, docx-ui-button]
  affects: [quote-actions-component, i18n-translations]
tech_stack:
  added: [docx-9.5.1]
  patterns: [client-side-document-generation, blob-download]
key_files:
  created:
    - frontend/src/lib/docx/quote-template.ts
  modified:
    - frontend/src/components/estimateur/quote-actions.tsx
    - frontend/src/lib/i18n/fr.ts
    - frontend/src/lib/i18n/en.ts
    - frontend/package.json
    - frontend/pnpm-lock.yaml
decisions:
  - decision: Use docx npm package for Word document generation
    rationale: Industry-standard library with clean API for programmatic DOCX creation
  - decision: Mirror PDF template structure exactly
    rationale: Consistent content between PDF and DOCX formats for client flexibility
  - decision: Standard tier pricing for DOCX (same as PDF)
    rationale: Middle tier represents typical pricing for client-facing quotes
  - decision: No labor hours in DOCX (same as PDF)
    rationale: Client-facing quotes hide internal labor hour details
  - decision: Bilingual support via locale parameter
    rationale: Quebec market requires FR/EN toggle for all exports
  - decision: TextRun children for styling (color, bold, size)
    rationale: docx package API requires style properties on TextRun, not Paragraph
  - decision: Conditional i18n key access (exporterDOCX vs exportDOCX)
    rationale: Different key names in FR/EN translations, fallback pattern ensures compatibility
metrics:
  duration_seconds: 296
  tasks_completed: 2
  files_created: 1
  files_modified: 5
  commits: 2
  lines_added: ~500
completed_date: 2026-02-10
---

# Phase 24 Plan 01: DOCX Export Summary

**One-liner:** Word document export using docx npm package with bilingual support matching PDF template structure.

## Overview

Added DOCX (Word) export functionality alongside existing PDF export, enabling clients to download editable quote documents. Implemented using the `docx` npm package with full bilingual support (FR/EN) and content structure matching the existing PDF template.

## What Was Built

### 1. DOCX Quote Template (`frontend/src/lib/docx/quote-template.ts`)
- **generateQuoteDOCX** async function returning Blob
- Function signature: `(quote, category, sqft, date, locale) => Promise<Blob>`
- Document structure mirrors PDF exactly:
  - **Header:** "SOUMISSION" (FR) or "QUOTE" (EN) title + "Toiture LV" subtitle
  - **Job Info:** Date, Category, Area (in pi2/sq ft based on locale)
  - **Work Items:** Bullet list with item names (NO labor hours - client facing)
  - **Summary:** Table with Materials, Labor, and TOTAL rows
  - **Footer:** 30-day validity notice (bilingual)
- Uses Standard tier for pricing (matches PDF decision from Phase 14-03)
- Locale parameter controls all text labels (FR/EN)
- formatCAD helper for French Canadian currency formatting

### 2. QuoteActions Component Updates
- Added `FileText` icon import from lucide-react
- Added `generateQuoteDOCX` import from new template
- Extracted `locale` from `useLanguage()` hook (alongside existing `t`)
- Added `isExportingDOCX` state for loading indicator
- Added `handleExportDOCX` function mirroring PDF export pattern:
  - Generates DOCX blob with locale parameter
  - Creates download link with filename pattern: `Soumission-{category}-{date}.docx`
  - Handles cleanup (revokeObjectURL)
- Added DOCX export button next to PDF button:
  - FileText icon (distinguishes from PDF's FileDown icon)
  - Loader2 spinner during export
  - Bilingual label using conditional i18n key access

### 3. I18n Translation Keys
- **French (fr.ts):** `exporterDOCX: "Exporter DOCX"`
- **English (en.ts):** `exportDOCX: "Export DOCX"`
- Located in `fullQuote` section alongside existing `exporterPDF` key

### 4. Package Dependencies
- Installed `docx@9.5.1` via pnpm
- Package provides: Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, and layout/styling enums

## Technical Implementation

### docx Package API Patterns
```typescript
// Document structure
new Document({
  sections: [{
    children: [
      // Paragraphs with TextRun children for styling
      new Paragraph({
        children: [
          new TextRun({ text: "Bold text", bold: true }),
          new TextRun({ text: "Regular text" })
        ],
        alignment: AlignmentType.CENTER
      }),

      // Tables with borderless cells
      new Table({
        width: { size: 100, type: WidthType.PERCENTAGE },
        rows: [
          new TableRow({
            children: [
              new TableCell({ children: [new Paragraph({ text: "Cell" })] })
            ]
          })
        ]
      })
    ]
  }]
});

// Generate Blob
await Packer.toBlob(doc);
```

### Key Insights
1. **Style properties belong to TextRun, not Paragraph** — `bold`, `color`, `size` must be on TextRun children
2. **Font sizes use half-points** — size 18 = 9pt, size 22 = 11pt, size 48 = 24pt
3. **Table borders require explicit NONE style** — All cells need border config to achieve borderless appearance
4. **Bullet lists use bullet property** — `bullet: { level: 0 }` on Paragraph for bullet points
5. **Border on paragraph via border.bottom** — Used for section header underlines

### Bilingual Implementation
- Locale parameter passed from `useLanguage()` hook's `locale` field
- All text labels conditionally rendered: `locale === "fr" ? "Materiaux" : "Materials"`
- Currency formatting uses `fr-CA` locale (space thousands separator)
- Area units: `pi2` (FR) vs `sq ft` (EN)

## Deviations from Plan

**None — plan executed exactly as written.**

All tasks completed as specified:
1. docx package installed successfully
2. generateQuoteDOCX function created with exact signature and structure from plan
3. QuoteActions updated with DOCX button and bilingual i18n keys
4. All verification checks passed

## Commits

| Commit | Hash | Description |
|--------|------|-------------|
| 1 | df74e63 | feat(24-01): add DOCX export template with docx package |
| 2 | 1691fcd | feat(24-01): wire DOCX export button with bilingual i18n |

## Verification Results

All verification checks passed:

1. ✅ `pnpm list docx` — docx@9.5.1 installed in dependencies
2. ✅ File exists: `frontend/src/lib/docx/quote-template.ts` with `generateQuoteDOCX` export
3. ✅ QuoteActions imports and uses `generateQuoteDOCX`
4. ✅ i18n keys: `exporterDOCX` in fr.ts, `exportDOCX` in en.ts
5. ✅ TypeScript compiles (pre-existing errors unrelated to changes)

## Success Criteria Met

- [x] DOCX export function generates Word document blob matching PDF content structure
- [x] QuoteActions shows both PDF and DOCX export buttons
- [x] DOCX template is bilingual (locale parameter controls all labels)
- [x] TypeScript compiles without errors related to new code
- [x] Package dependencies properly installed

## User Experience

Users can now:
1. Generate a full quote in the "Soumission Complete" tab
2. Choose between two export formats:
   - **PDF** — Static, print-ready format (existing)
   - **DOCX** — Editable Word format (new) for client modifications
3. Download files with descriptive filenames: `Soumission-{category}-{date}.{format}`
4. See loading indicators during export (Loader2 spinner)
5. Experience consistent bilingual labeling (FR/EN toggle)

## Next Steps

- **Phase 24-02:** Implement "Send" dialog for email/SMS delivery options
- **Phase 24-03:** Add red flag warning system for high-risk quotes
- Laurent may want to add company logo to both PDF and DOCX headers (LV logo file needed)

## Self-Check: PASSED

### Files Created
```bash
✓ FOUND: frontend/src/lib/docx/quote-template.ts
```

### Commits Exist
```bash
✓ FOUND: df74e63 (Task 1 - DOCX template)
✓ FOUND: 1691fcd (Task 2 - QuoteActions + i18n)
```

### Imports Verified
```bash
✓ FOUND: import { generateQuoteDOCX } in quote-actions.tsx
✓ FOUND: exporterDOCX in fr.ts
✓ FOUND: exportDOCX in en.ts
```

All claims verified. Plan execution complete.
