---
phase: 26-ux-overhaul-polish
plan: 01
subsystem: ui
tags: [next.js, react, shadcn-ui, i18n, navigation, layout]

# Dependency graph
requires:
  - phase: 25-ui-polish-dark-mode
    provides: Dark mode toggle, theme system, admin layout infrastructure
provides:
  - Dashboard and Review pages inside admin sidebar layout
  - Sidebar with 7 nav items (Estimateur, Historique, Apercu, Clients, Retours, Dashboard, Review)
  - i18n-compliant sidebar labels (nav.navigation, nav.dashboard, nav.review)
  - Multi-level breadcrumbs showing sub-route context
  - Redesigned login page with shadcn components
  - Wider content width (max-w-4xl) on estimateur pages
affects: [27-ai-chat-interface, future-admin-pages]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Breadcrumb sub-route labels via routeLabels record"
    - "shadcn Card-based login layout with CSS variable theming"

key-files:
  created:
    - frontend/src/app/(admin)/dashboard/page.tsx
    - frontend/src/app/(admin)/review/page.tsx
    - frontend/src/components/estimateur/wizard/step-crew.tsx
    - frontend/src/components/estimateur/wizard/step-materials.tsx
    - frontend/src/components/estimateur/wizard/step-review.tsx
  modified:
    - frontend/src/components/admin/app-sidebar.tsx
    - frontend/src/app/(admin)/layout.tsx
    - frontend/src/lib/i18n/fr.ts
    - frontend/src/lib/i18n/en.ts
    - frontend/src/app/login/page.tsx
    - frontend/src/app/(admin)/estimateur/soumissions/page.tsx
    - frontend/src/components/estimateur/wizard/wizard-container.tsx

key-decisions:
  - "Move orphaned pages into admin route group instead of creating separate layouts"
  - "Use shadcn Card/Input/Button components for login instead of raw HTML"
  - "Add second breadcrumb level to show sub-routes like 'Estimateur > Soumission Complete'"
  - "Create wizard step stubs to resolve build errors in WIP wizard-container.tsx"

patterns-established:
  - "All admin pages live inside (admin) route group for consistent sidebar/breadcrumb UX"
  - "i18n keys for navigation items prevent hardcoded English strings"
  - "bg-background instead of hardcoded zinc colors for proper dark mode support"

# Metrics
duration: 9min
completed: 2026-02-12
---

# Phase 26 Plan 01: Navigation & Login UX Fixes Summary

**Dashboard and Review pages moved into admin sidebar layout, login redesigned with shadcn Card/Input/Button, sidebar i18n fixed, breadcrumbs show sub-route labels, form content widened to max-w-4xl**

## Performance

- **Duration:** 9 min
- **Started:** 2026-02-11T21:03:30Z
- **Completed:** 2026-02-11T21:12:47Z
- **Tasks:** 2
- **Files modified:** 12
- **Commits:** 2

## Accomplishments

- Dashboard (/dashboard) and Review (/review) pages now render inside admin sidebar layout (no longer orphaned)
- Sidebar navigation expanded to 7 items with BarChart3 and ClipboardCheck icons
- Hardcoded "Navigation" label replaced with i18n key (respects EN/FR toggle)
- Breadcrumbs now show sub-route labels (e.g., "Cortex > Soumission Complete" for /estimateur/complet)
- Login page redesigned with shadcn Card/Input/Button/Label and Home icon for LV branding
- Content width on /estimateur/soumissions widened from max-w-2xl to max-w-4xl

## Task Commits

Each task was committed atomically:

1. **Task 1: Move orphaned pages and fix sidebar navigation** - `9cfb3ab` (feat)
   - Created /dashboard and /review inside admin route group
   - Added Dashboard and Review nav items with icons to sidebar
   - Fixed i18n: nav.navigation, nav.dashboard, nav.review (FR/EN)
   - Added breadcrumb sub-route labels (complet, materiaux, soumissions)
   - Deleted standalone /dashboard and /review pages
   - Fixed wizard-container import and created step stubs (blocking fix)

2. **Task 2: Redesign login page and widen form content** - `18b085b` (feat)
   - Replaced raw HTML login form with shadcn Card/Input/Button/Label
   - Added Home icon in primary-colored circle for LV branding
   - Used bg-background instead of hardcoded zinc colors for dark mode support
   - Changed max-w-2xl to max-w-4xl on /estimateur/soumissions

## Files Created/Modified

**Created:**
- `frontend/src/app/(admin)/dashboard/page.tsx` - Client component rendering DashboardContent inside admin layout
- `frontend/src/app/(admin)/review/page.tsx` - Client component with review queue functionality, no standalone layout wrapper
- `frontend/src/components/estimateur/wizard/step-crew.tsx` - WIP stub for Step 3 (Crew & Duration)
- `frontend/src/components/estimateur/wizard/step-materials.tsx` - WIP stub for Step 4 (Materials)
- `frontend/src/components/estimateur/wizard/step-review.tsx` - WIP stub for Step 5 (Review)

**Modified:**
- `frontend/src/components/admin/app-sidebar.tsx` - Added Dashboard (BarChart3) and Review (ClipboardCheck) nav items, fixed i18n for "Navigation" label
- `frontend/src/app/(admin)/layout.tsx` - Added dashboard, review, retours, complet, materiaux, soumissions to routeLabels; added second breadcrumb level
- `frontend/src/lib/i18n/fr.ts` - Added nav.dashboard, nav.review, nav.navigation
- `frontend/src/lib/i18n/en.ts` - Added nav.dashboard, nav.review, nav.navigation
- `frontend/src/app/login/page.tsx` - Redesigned with shadcn Card/Input/Button/Label and Home icon
- `frontend/src/app/(admin)/estimateur/soumissions/page.tsx` - Changed max-w-2xl to max-w-4xl
- `frontend/src/components/estimateur/wizard/wizard-container.tsx` - Fixed FactorConfig import path (from tier-selector to factor-checklist)

**Deleted:**
- `frontend/src/app/dashboard/page.tsx` - Orphaned dashboard page
- `frontend/src/app/review/page.tsx` - Orphaned review page

## Decisions Made

- **Move pages into admin route group**: Ensures consistent sidebar/breadcrumb UX instead of separate layouts
- **shadcn components for login**: Professional appearance, respects CSS variable theming, no hardcoded colors
- **Second breadcrumb level**: Shows sub-route context (e.g., "Estimateur > Soumission Complete" for /estimateur/complet)
- **Wider content width (max-w-4xl)**: Provides more horizontal space for full quote form and submission list

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Fixed wizard-container.tsx import error**
- **Found during:** Task 1 verification (Next.js build)
- **Issue:** `wizard-container.tsx` imported `FactorConfig` from `tier-selector.tsx` but type only exists in `factor-checklist.tsx`
- **Fix:** Changed import from `"../tier-selector"` to `"../factor-checklist"` for FactorConfig type
- **Files modified:** `frontend/src/components/estimateur/wizard/wizard-container.tsx`
- **Verification:** Build passed without TypeScript errors
- **Committed in:** `9cfb3ab` (Task 1 commit)

**2. [Rule 3 - Blocking] Created wizard step stubs to resolve missing imports**
- **Found during:** Task 1 verification (Next.js build)
- **Issue:** `wizard-container.tsx` imported step-crew, step-materials, step-review but files didn't exist (WIP wizard)
- **Fix:** Created stub components with minimal props matching usage patterns
- **Files created:**
  - `frontend/src/components/estimateur/wizard/step-crew.tsx` - Stub with "Coming soon" message
  - `frontend/src/components/estimateur/wizard/step-materials.tsx` - Stub with "Coming soon" message
  - `frontend/src/components/estimateur/wizard/step-review.tsx` - Stub with tiers/factorConfig/isLoading props
- **Verification:** Build passed, wizard-container.tsx imports resolved
- **Committed in:** `9cfb3ab` (Task 1 commit)

---

**Total deviations:** 2 auto-fixed (both Rule 3 - Blocking)
**Impact on plan:** Both fixes necessary to unblock TypeScript compilation. Wizard is WIP but included in build, so stubs prevent build errors. No scope creep.

## Issues Encountered

None - plan executed smoothly. Auto-fixes were for pre-existing WIP code, not newly introduced bugs.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Navigation UX fully polished: all pages accessible from sidebar, breadcrumbs provide context
- Login page redesigned with shadcn components and proper dark mode support
- Content width optimized for forms
- Ready for Phase 26-02 (Error States & Loading Indicators) and 26-03 (Accessibility & Polish)

---
*Phase: 26-ux-overhaul-polish*
*Completed: 2026-02-12*
