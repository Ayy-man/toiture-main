---
phase: 25-ui-polish-dark-mode
plan: 03
subsystem: frontend-ui-charts
tags: [dark-mode, recharts, dashboard, css-variables]
completed: 2026-02-10T20:58:49Z

dependency_graph:
  requires:
    - 25-01 (Dark mode toggle with next-themes)
    - Recharts library for dashboard charts
    - Tailwind CSS v4 dark mode variables
  provides:
    - Dark mode compatible dashboard charts
    - Semantic color system for chart components
  affects:
    - Apercu dashboard page visibility in dark mode
    - Chart readability across both themes

tech_stack:
  patterns:
    - CSS variable references in Recharts components
    - Inline style objects for tooltip backgrounds
    - Semantic color tokens for charts (--chart-1 through --chart-5)

key_files:
  modified:
    - frontend/src/components/apercu/revenue-chart.tsx: "Bar chart with --chart-1 fill and --popover tooltip"
    - frontend/src/components/apercu/trend-chart.tsx: "Line chart with --chart-1 stroke/dots and --popover tooltip"
    - frontend/src/components/apercu/category-chart.tsx: "Pie chart with --chart-N colors and --popover tooltip"

decisions:
  - decision: "Use hsl(var(--chart-1)) for all LV brick red references"
    rationale: "Matches globals.css chart color definitions that adapt to dark mode (34% lightness in light, 50% in dark)"
  - decision: "Replace COLORS array with CSS variable references"
    rationale: "Recharts accepts string values for fill/stroke, CSS variables evaluated at render time"
  - decision: "Inline style objects for tooltip backgrounds"
    rationale: "Recharts contentStyle prop requires object format, not className"
  - decision: "Keep metrics-cards.tsx unchanged"
    rationale: "Already uses semantic Tailwind classes (text-muted-foreground, bg-card) that adapt to dark mode"

metrics:
  duration_minutes: 1
  tasks_completed: 1
  files_modified: 3
  commits: 1
  deviations: 0
  checkpoint_pending: true
---

# Phase 25 Plan 03: Dashboard Charts Dark Mode Audit Summary

**One-liner:** Recharts dashboard charts fixed for dark mode with CSS variable colors and semantic tooltips.

## What Was Built

Fixed all Recharts dashboard components for dark mode compatibility:

1. **Revenue Chart (Bar Chart)**:
   - Changed bar fill from hardcoded `#8B2323` to `hsl(var(--chart-1))`
   - Updated tooltip to use `--popover` background and `--border` colors
   - Axis labels already used `--muted-foreground` (verified correct)

2. **Trend Chart (Line Chart)**:
   - Changed line stroke from hardcoded `#8B2323` to `hsl(var(--chart-1))`
   - Changed dot fills from hardcoded `#8B2323` to `hsl(var(--chart-1))`
   - Updated tooltip to use `--popover` background and `--border` colors
   - Axis labels already used `--muted-foreground` (verified correct)

3. **Category Chart (Pie Chart)**:
   - Replaced COLORS array hex values with CSS variables (`--chart-1` through `--chart-5`)
   - Updated tooltip to use `--popover` background and `--border` colors
   - Legend already used semantic foreground color (verified correct)
   - Label lines already used `--muted-foreground` (verified correct)

4. **Metrics Cards**:
   - No changes needed — already using semantic Tailwind classes
   - `text-muted-foreground`, `bg-card`, `text-card-foreground` all adapt to dark mode

**Color Mapping:**
- Light mode: `--chart-1` = `hsl(10 72% 34%)` (LV brick red)
- Dark mode: `--chart-1` = `hsl(10 72% 50%)` (lighter red for contrast)

## Deviations from Plan

None. Plan executed exactly as written. All chart components updated to use semantic CSS variables.

## Verification Results

✅ **Build:** `pnpm build` completes successfully (6.7s compile time)
✅ **Hardcoded colors:** `grep -E '#[0-9a-fA-F]{3,6}'` returns no results for chart files
✅ **CSS variables:** All chart elements use `hsl(var(--chart-N))` pattern
✅ **Tooltips:** All tooltips use `--popover`, `--border`, `--popover-foreground` variables
✅ **Axis labels:** All X/Y axes use `--muted-foreground` for tick text

## Checkpoint Pending

**Task 2: Visual verification of dark mode and LV branding**

This plan includes a `type="checkpoint:human-verify"` task that requires manual browser testing. The automated Task 1 is complete and committed. Task 2 requires:

1. **Dark mode toggle test** - Switch between light/dark, verify theme persistence
2. **Language switch test** - Switch EN/FR, verify tier names change
3. **Dashboard charts test** - Verify charts readable in dark mode
4. **Branding verification** - Verify LV red accent visible in both modes
5. **PDF export test** - Verify PDF labels match selected language

**Action Required:** Human user must open the app in browser (localhost:3000 or production) and visually verify the items listed in Task 2 of the plan.

## Self-Check: PASSED

**Files modified:**
- ✓ frontend/src/components/apercu/revenue-chart.tsx (modified lines 36-44, 86-91)
- ✓ frontend/src/components/apercu/trend-chart.tsx (modified lines 38-48, 91-99)
- ✓ frontend/src/components/apercu/category-chart.tsx (modified lines 11-16, 39-50)

**Commits:**
- ✓ 173c347: feat(25-03): fix Recharts components for dark mode compatibility

All files and commits exist. No errors during verification.

## Known Issues

None. All chart components successfully updated with dark mode compatible colors.

## Next Steps

- **Human verification:** User must complete Task 2 visual verification
- After verification approved, Phase 25 will be complete (3/3 plans)
- Phase 25 completion enables final sprint delivery (Deadline: Feb 16, 2026)
