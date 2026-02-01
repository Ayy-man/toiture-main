---
status: testing
phase: 14-full-quote-frontend
source: [14-01-SUMMARY.md, 14-02-SUMMARY.md, 14-03-SUMMARY.md]
started: 2026-02-01T15:45:00Z
updated: 2026-02-01T15:45:00Z
---

## Current Test

number: 1
name: Navigate to Full Quote Form
expected: |
  Go to http://localhost:3000/estimateur/complet (with frontend dev server running).
  Form page loads with title "Soumission complete" and all form fields visible.
awaiting: user response

## Tests

### 1. Navigate to Full Quote Form
expected: Go to /estimateur/complet. Form page loads with title and all fields.
result: [pending]

### 2. Select Complexity Preset
expected: Click "Simple", "Modere", or "Complexe" toggle. The selected preset highlights. Below shows "Total: X/56" (11 for Simple, 28 for Modere, 44 for Complexe).
result: [pending]

### 3. Override Complexity Slider
expected: Expand "Personnaliser les facteurs" section. Drag any slider. Preset selection clears (no longer highlighted). Total updates based on new values.
result: [pending]

### 4. Submit Form and See Result
expected: Fill form fields and click "Generer la soumission". Loading state shows. Invoice-style result appears below with "SOUMISSION" header, work items list, and totals.
result: [pending]

### 5. Work Items Display Hours
expected: In the result, "TRAVAUX" section shows work items. Each work item has name on left and labor hours on right (e.g., "8.5 hrs").
result: [pending]

### 6. Materials and Labor Totals
expected: "SOMMAIRE" section shows: "Materiaux" with CAD amount, "Main-d'oeuvre (X hrs)" with CAD amount, and "TOTAL" bold at bottom.
result: [pending]

### 7. Confidence Warning Banner
expected: If backend returns confidence < 50%, amber warning banner appears at top of result: "Confiance: X% - Verification recommandee". If >= 50%, no banner.
result: [pending]

### 8. Collapsible Reasoning Section
expected: "Raisonnement" section shows with chevron. Click to expand/collapse. When expanded, shows LLM reasoning text. Default is collapsed.
result: [pending]

### 9. French Labels Throughout
expected: All labels are in French: "Superficie", "Categorie", "Complexite du travail", "Generer la soumission", etc.
result: [pending]

### 10. Export PDF Button Visible
expected: After generating a quote, "Exporter PDF" button visible at bottom of result section.
result: [pending]

### 11. PDF Download Works
expected: Click "Exporter PDF". Button shows loading spinner briefly. PDF file downloads automatically.
result: [pending]

### 12. PDF Filename Pattern
expected: Downloaded PDF filename follows pattern: Soumission-{category}-{date}.pdf (e.g., "Soumission-Bardeaux-2026-02-01.pdf")
result: [pending]

### 13. PDF Content - No Hours
expected: Open downloaded PDF. Work items listed as bullets WITHOUT hours (just names). No confidence warning. No reasoning section.
result: [pending]

### 14. PDF Content - Totals Display
expected: PDF shows: "Materiaux" with amount, "Main-d'oeuvre" with amount, "TOTAL" with amount. All formatted as CAD currency.
result: [pending]

## Summary

total: 14
passed: 0
issues: 0
pending: 14
skipped: 0

## Gaps

[none yet]
