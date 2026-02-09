---
phase: 23-submission-workflow-editing
plan: 03
status: complete
started: 2026-02-09T01:10:00Z
completed: 2026-02-10T01:30:00Z
commits:
  - hash: 944d886
    message: "feat(23-03): add submission editor core components"
  - hash: af8f66a
    message: "feat(23-03): wire submission workflow into application"
---

# Plan 23-03 Summary: Submission UI Integration

## What Was Done

### Task 1: Core Submission Components
**Commit:** `944d886`

Created 4 new components:
- **SortableLineItem** (`sortable-line-item.tsx`): Drag-droppable row using @dnd-kit with GripVertical handle, inline editing for name/quantity/price, live total recalculation
- **NotesPanel** (`notes-panel.tsx`): Timestamped notes display sorted DESC, add input textarea, created_by attribution
- **UpsellDialog** (`upsell-dialog.tsx`): Category-specific bilingual suggestions from upsell_rules.json, create button per suggestion, skip footer
- **SubmissionEditor** (`submission-editor.tsx`, 400+ lines): Main editor with DndContext, line items array, MaterialSelector integration via Dialog, totals calculation, action buttons (Save/Finalize/Approve/Reject/Return to Draft), notes panel, upsell dialog, child submissions display

### Task 2: Application Wiring
**Commit:** `af8f66a`

- **SubmissionList** (`submission-list.tsx`): List view with status filter tabs (All/Draft/Pending/Approved/Rejected), submission cards, click-to-open editor
- **full-quote-form.tsx**: Added "Create Submission" button after QuoteResult, converts HybridQuoteResponse to LineItem[], creates submission via API, renders SubmissionEditor
- **nav-tabs.tsx**: Added 4th "Soumissions" tab (URL-based routing)
- **soumissions/page.tsx**: New route at /estimateur/soumissions rendering SubmissionList

## Files Created
- `frontend/src/components/estimateur/sortable-line-item.tsx`
- `frontend/src/components/estimateur/notes-panel.tsx`
- `frontend/src/components/estimateur/upsell-dialog.tsx`
- `frontend/src/components/estimateur/submission-editor.tsx`
- `frontend/src/components/estimateur/submission-list.tsx`
- `frontend/src/app/(admin)/estimateur/soumissions/page.tsx`

## Files Modified
- `frontend/src/components/estimateur/full-quote-form.tsx`
- `frontend/src/components/estimateur/nav-tabs.tsx`

## Verification
- TypeScript compilation passed
- All components export correctly
- Form wiring connects quote generation to submission creation
- Navigation wiring adds Soumissions tab

## Deviations
None.
