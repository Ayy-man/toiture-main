---
phase: 11-cortex-admin-dashboard
plan: 01
subsystem: ui
tags: [next.js, shadcn-ui, sidebar, french-i18n, tailwind]

# Dependency graph
requires:
  - phase: 04-frontend-foundation
    provides: Next.js 15 project with shadcn/ui components
  - phase: 09-streaming-estimates
    provides: Streaming estimate form component
provides:
  - Admin dashboard layout with dark sidebar
  - French navigation labels (Estimateur, Historique, Apercu, Clients)
  - Brick red (#8B2323) branding with CSS variables
  - Route-based tab navigation with active state highlighting
affects: [11-02, 11-03, 11-04]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "shadcn/ui Sidebar with SidebarProvider context"
    - "Next.js (admin) route group for layout isolation"
    - "French i18n with centralized translation constants"
    - "CSS custom properties for theme colors"

key-files:
  created:
    - frontend/src/components/ui/sidebar.tsx
    - frontend/src/components/admin/app-sidebar.tsx
    - frontend/src/lib/i18n/fr.ts
    - frontend/src/app/(admin)/layout.tsx
    - frontend/src/app/(admin)/page.tsx
    - frontend/src/app/(admin)/estimateur/page.tsx
    - frontend/src/app/(admin)/historique/page.tsx
    - frontend/src/app/(admin)/apercu/page.tsx
    - frontend/src/app/(admin)/clients/page.tsx
  modified:
    - frontend/src/app/globals.css
    - frontend/src/app/page.tsx
    - frontend/package.json

key-decisions:
  - "Custom sidebar implementation using existing Radix primitives"
  - "Route group (admin) isolates dashboard layout from other pages"
  - "Root path redirects to /estimateur as default tab"

patterns-established:
  - "AppSidebar: Client component with usePathname for active detection"
  - "AdminLayout: Server component wrapping SidebarProvider"
  - "fr object: Centralized French translations for UI labels"

# Metrics
duration: 45min
completed: 2026-01-18
---

# Phase 11 Plan 01: Admin Dashboard Layout Summary

**Dark sidebar (#1A1A1A) with brick red (#8B2323) Cortex branding and French navigation for 4-tab admin dashboard**

## Performance

- **Duration:** 45 min
- **Started:** 2026-01-18T18:12:00Z
- **Completed:** 2026-01-18T18:57:00Z
- **Tasks:** 3
- **Files modified:** 12

## Accomplishments

- Created shadcn/ui-compatible sidebar component with mobile responsive support
- Established French translation system with nav, form, and common labels
- Built admin layout with dark theme and brick red accent branding
- Set up 4 tab routes with working navigation and active state highlighting

## Task Commits

Each task was committed atomically:

1. **Task 1: Install shadcn/ui Sidebar and add French i18n** - `4564b64` (feat)
2. **Task 2: Create admin layout and sidebar components** - `a4493cf` (feat)
3. **Task 3: Create placeholder tab pages and update root redirect** - `edd65c6` (feat)

## Files Created/Modified

- `frontend/src/components/ui/sidebar.tsx` - Full sidebar component with SidebarProvider context
- `frontend/src/components/admin/app-sidebar.tsx` - Dark sidebar with 4 French navigation items
- `frontend/src/lib/i18n/fr.ts` - French translation constants
- `frontend/src/app/(admin)/layout.tsx` - Admin layout wrapper with SidebarProvider
- `frontend/src/app/(admin)/page.tsx` - Redirects to /estimateur
- `frontend/src/app/(admin)/estimateur/page.tsx` - Renders EstimateForm
- `frontend/src/app/(admin)/historique/page.tsx` - Placeholder for quote browser
- `frontend/src/app/(admin)/apercu/page.tsx` - Placeholder for dashboard
- `frontend/src/app/(admin)/clients/page.tsx` - Placeholder for customer search
- `frontend/src/app/globals.css` - Added brick red CSS variables
- `frontend/src/app/page.tsx` - Changed to redirect to /estimateur
- `frontend/package.json` - Added Radix tooltip and separator dependencies

## Decisions Made

- **Custom sidebar implementation:** Created sidebar component manually instead of using shadcn CLI due to npm hanging. Uses existing Radix Slot primitive and matches shadcn/ui API.
- **Route group (admin):** Used Next.js route group to isolate admin layout from login and other pages.
- **Root redirect:** Changed root page from showing EstimateForm directly to redirecting to /estimateur for consistent admin experience.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] shadcn CLI installation hanging**
- **Found during:** Task 1 (Install shadcn/ui Sidebar)
- **Issue:** `npx shadcn@latest add sidebar` command hung indefinitely
- **Fix:** Created sidebar component manually following shadcn/ui source patterns
- **Files modified:** frontend/src/components/ui/sidebar.tsx
- **Verification:** Build passes, sidebar renders correctly
- **Committed in:** 4564b64 (Task 1 commit)

**2. [Rule 3 - Blocking] npm install corrupted node_modules**
- **Found during:** Task 3 verification (npm run build)
- **Issue:** Build failed with ERR_INVALID_PACKAGE_CONFIG
- **Fix:** Removed node_modules and .next, ran fresh npm install
- **Files modified:** node_modules (reinstalled)
- **Verification:** Build succeeds after clean install
- **Committed in:** N/A (not tracked in git)

---

**Total deviations:** 2 auto-fixed (2 blocking)
**Impact on plan:** Deviations were necessary to work around tooling issues. Final result matches plan requirements.

## Issues Encountered

- shadcn CLI hanging on component installation - worked around by manual implementation
- Corrupted package.json in node_modules - resolved with clean install

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Admin dashboard layout complete and working
- All 4 navigation tabs have routes with placeholder content
- Ready for Plan 02 (Historique quote browser)
- Ready for Plan 03 (Apercu dashboard metrics)
- Ready for Plan 04 (Clients customer search)

---
*Phase: 11-cortex-admin-dashboard*
*Completed: 2026-01-18*
