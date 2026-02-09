---
phase: 20
plan: 03
subsystem: frontend-ui
tags: [materials, selector, ui, search, combobox]
dependencies:
  requires:
    - "20-02: Materials search API endpoints"
    - "Phase 11: shadcn/ui patterns and i18n"
  provides:
    - "MaterialSelector component for searchable material selection"
    - "Integrated material selector in materials form"
  affects:
    - "frontend/materiaux: Replaces manual material_lines input"
tech_stack:
  added:
    - "@radix-ui/react-popover"
    - "cmdk (Command Menu component)"
  patterns:
    - "useDeferredValue for search debouncing (React 19)"
    - "Popover + Command pattern for Combobox"
    - "Controlled multi-select state"
key_files:
  created:
    - frontend/src/components/ui/popover.tsx
    - frontend/src/components/ui/command.tsx
    - frontend/src/lib/api/materials.ts
    - frontend/src/components/estimateur/material-selector.tsx
  modified:
    - frontend/src/components/estimateur/materials-form.tsx
    - frontend/src/lib/i18n/fr.ts
    - frontend/src/lib/i18n/en.ts
    - frontend/package.json
decisions:
  - "Use useDeferredValue over custom debounce hook (React 19 concurrent feature)"
  - "Popover + Command pattern for searchable combobox (shadcn best practice)"
  - "Negative temporary IDs for custom materials (avoids database ID conflicts)"
  - "Auto-calculate material_lines via useEffect (maintains backward compatibility)"
  - "Category filter as Select above search (not inside Command)"
  - "Total estimated cost display in selected materials list"
metrics:
  duration: 903s
  tasks_completed: 2
  commits: 2
  files_modified: 8
  files_created: 4
  completed_at: "2026-02-09T17:10:35Z"
---

# Phase 20 Plan 03: Material Selector UI Summary

**One-liner:** Searchable multi-select material picker with category filter, custom material entry, and auto-calculated line count replacing manual input.

## What Was Built

Built a comprehensive material selector component that replaces the manual "material_lines" number input in the materials estimation form with a searchable dropdown backed by the materials database API.

**Core features:**
1. **Searchable dropdown** with debounced search (useDeferredValue pattern)
2. **Category filter** to narrow results
3. **Multi-select** with visual checkmarks
4. **Selected materials list** with remove buttons and total cost
5. **Custom material entry** for unlisted items
6. **Auto-calculated material_lines** synced with form state

## Tasks Completed

### Task 1: Install shadcn Command + Popover and create material API client ✅

**Commit:** `5932055`

**What was done:**

1. **Installed dependencies:**
   - `@radix-ui/react-popover` (1.1.15)
   - `cmdk` (1.1.1)

2. **Created shadcn/ui components:**
   - `frontend/src/components/ui/popover.tsx`: Popover, PopoverTrigger, PopoverContent components following shadcn v4 patterns
   - `frontend/src/components/ui/command.tsx`: Command, CommandInput, CommandList, CommandGroup, CommandItem, CommandEmpty components with cmdk integration

3. **Created materials API client:**
   - `frontend/src/lib/api/materials.ts` with TypeScript interfaces matching backend:
     - `MaterialItem` (14 fields: id, code, name, cost, sell_price, unit, category, supplier, note, dimensions, item_type, ml_material_id, review_status)
     - `MaterialSearchResponse` (materials, count, total_available)
     - `MaterialCategoryResponse` (categories, count)
   - `searchMaterials(q, category?, limit?)` function with 2+ char minimum and category filtering
   - `fetchMaterialCategories()` function for category dropdown
   - API URL from `process.env.NEXT_PUBLIC_API_URL` following existing patterns

**Files created:**
- `frontend/src/components/ui/popover.tsx` (51 lines)
- `frontend/src/components/ui/command.tsx` (148 lines)
- `frontend/src/lib/api/materials.ts` (65 lines)

**Files modified:**
- `frontend/package.json` (added 2 dependencies)
- `frontend/pnpm-lock.yaml` (lockfile updated)

**Verification:** ✅ All files exist, TypeScript types match backend schema

---

### Task 2: Build MaterialSelector component and integrate into materials form ✅

**Commit:** `80a117c`

**What was done:**

1. **Added i18n translations:**
   - French (`fr.ts`): `materialSelector` section with 13 keys (rechercher, aucunResultat, selectionner, materiauSelectionnes, touteCategories, ajouterPersonnalise, nomPersonnalise, prixPersonnalise, unitePersonnalisee, ajouter, annuler, supprimer, lignesAuto)
   - English (`en.ts`): Matching translations for bilingual support

2. **Created MaterialSelector component:**
   - **SelectedMaterial interface:** id, name, category, sell_price, unit, isCustom flag
   - **Category filter dropdown:** Fetches categories on mount, shows "All categories" + list
   - **Searchable combobox:** Popover + Command pattern with debounced search using `useDeferredValue`
   - **Search results:** Shows up to 50 materials with name, category, and price
   - **Multi-select logic:** Click to toggle selection, checkmarks for selected items
   - **Selected materials list:** Removable cards showing name, category, price per unit, and remove button
   - **Total cost display:** Sums sell_price of all selected materials
   - **Custom material dialog:** Name, unit price, and unit inputs with negative temporary ID generation
   - **Loading states:** Shows "Chargement..." while searching
   - **Empty states:** "Aucun materiau trouve" when no results

3. **Integrated into materials-form.tsx:**
   - Imported `MaterialSelector` and `SelectedMaterial` type
   - Added `selectedMaterials` state (`SelectedMaterial[]`)
   - Added `useEffect` to auto-update `form.setValue('material_lines', selectedMaterials.length)`
   - **Replaced** manual `material_lines` Input with:
     - `MaterialSelector` component (takes full width, md:col-span-2)
     - Read-only display showing auto-calculated count
   - **Kept unchanged:** sqft, category, complexity, toggles, labor_lines, submit logic
   - Maintained backward compatibility with existing `/estimate/materials` endpoint

**Files created:**
- `frontend/src/components/estimateur/material-selector.tsx` (367 lines)

**Files modified:**
- `frontend/src/components/estimateur/materials-form.tsx` (+20 lines, removed manual input)
- `frontend/src/lib/i18n/fr.ts` (+13 translation keys)
- `frontend/src/lib/i18n/en.ts` (+13 translation keys)

**Verification:** ✅ MaterialSelector imported and used, translations exist in both languages

## Deviations from Plan

None - plan executed exactly as written.

## Technical Decisions

| Decision | Rationale |
|----------|-----------|
| useDeferredValue for debouncing | Native React 19 concurrent feature, matches Phase 11-04 pattern |
| Popover + Command pattern | Shadcn best practice for searchable combobox |
| Negative temporary IDs for custom materials | Avoids conflicts with database IDs, easy to detect custom items |
| Category filter as Select | Better UX than nested filter inside Command dropdown |
| Auto-sync material_lines via useEffect | Maintains backward compatibility with existing API |
| Total estimated cost in selector | Gives estimators immediate pricing feedback |
| md:col-span-2 for selector | Full width on desktop for better visibility |

## Integration Points

**Upstream dependencies:**
- Materials search API (Phase 20-02): `GET /materials/search`, `GET /materials/categories`
- shadcn/ui components: Dialog, Select, Label, Input, Button
- i18n system (Phase 16): useLanguage hook for FR/EN translations

**Downstream consumers:**
- Materials form: Uses MaterialSelector instead of manual material_lines input
- Material prediction endpoint: Still receives material_lines as a number (backward compatible)

## User Experience Flow

1. **Estimator opens Materiaux tab** → Sees category filter dropdown and material selector button
2. **Selects category** (optional) → Narrows search results
3. **Clicks selector button** → Popover opens with search input
4. **Types material name** (2+ chars) → Search results appear with debounce
5. **Clicks material** → Adds to selection with checkmark, closes popover
6. **Repeats** for multiple materials → Selected list grows
7. **Reviews selected materials** → Sees name, category, price per unit, remove buttons
8. **Sees total cost** → Sum of all selected material prices
9. **Adds custom material** (if needed) → Opens dialog, enters name/price/unit
10. **Submits form** → material_lines auto-populated with selection count

## Success Criteria Met

- [x] Material selector replaces manual material_lines input
- [x] Users search by typing 2+ characters, results from backend API
- [x] Category filter dropdown narrows results
- [x] Multi-select with visual checkmarks and removal
- [x] Custom material entry for items not in database
- [x] Auto-calculated material_lines synced with form state
- [x] Bilingual labels (FR/EN) via i18n
- [x] TypeScript compiles without errors
- [x] Backward compatibility maintained with existing API

## Testing Notes

**Manual verification performed:**
- ✅ shadcn Command and Popover components created with correct patterns
- ✅ Materials API client matches backend schema
- ✅ MaterialSelector component imports all required dependencies
- ✅ i18n translations exist in both FR and EN
- ✅ materials-form.tsx imports and uses MaterialSelector
- ✅ material_lines auto-updates via useEffect

**Production validation needed:**
- Test search with actual materials data from Supabase
- Verify category filter returns correct results
- Test custom material addition with negative IDs
- Confirm material_lines correctly passed to `/estimate/materials` endpoint
- Validate debounced search performance with 1000+ materials

## Next Steps

**Phase 20 complete** - All plans (20-01, 20-02, 20-03) finished.

**Related work:**
- Phase 22: Add more estimation input fields (crew, duration, zone, premium, access, tools, supply chain)
- Phase 23: Submission workflow with editable quotes and material selection editing
- Future: Material quantity estimation based on sqft and category

## Self-Check: PASSED

**Created files exist:**
```
FOUND: frontend/src/components/ui/popover.tsx
FOUND: frontend/src/components/ui/command.tsx
FOUND: frontend/src/lib/api/materials.ts
FOUND: frontend/src/components/estimateur/material-selector.tsx
```

**Modified files exist:**
```
FOUND: frontend/src/components/estimateur/materials-form.tsx
FOUND: frontend/src/lib/i18n/fr.ts
FOUND: frontend/src/lib/i18n/en.ts
```

**Commits exist:**
```
FOUND: 5932055 (Task 1 - shadcn components and API client)
FOUND: 80a117c (Task 2 - MaterialSelector component and integration)
```

**Verifications passed:**
```
✅ MaterialSelector component created (367 lines)
✅ Imported in materials-form.tsx
✅ i18n translations added (FR/EN)
✅ Dependencies installed (cmdk, @radix-ui/react-popover)
✅ TypeScript types match backend schema
```

**All verifications passed:** ✅
