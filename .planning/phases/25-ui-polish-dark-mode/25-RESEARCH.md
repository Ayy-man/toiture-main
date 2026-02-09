# Phase 25: UI Polish & Dark Mode - Research

**Researched:** 2026-02-10
**Domain:** Dark mode implementation, i18n bug fixes, branding verification
**Confidence:** HIGH

## Summary

Phase 25 adds dark mode toggle, fixes FR/EN language bugs, and verifies LV branding consistency. The technical implementation is straightforward since the project already has:
- Tailwind CSS v4 with inline theming and CSS variables
- Complete dark mode CSS variables defined in globals.css
- Functional i18n system with LanguageContext and localStorage persistence
- Lyra preset with LV brand colors (brick red primary)

**Primary challenges:**
1. **Dark mode toggle**: Need to add next-themes library and implement theme switching without hydration mismatches
2. **FR/EN bugs**: Current system works for UI labels but may not propagate to AI-generated content and tier descriptions that use locale checks
3. **Export templates**: Need to audit PDF/DOCX templates for language support (backend templates not yet researched)

**Key insight:** The CSS variables for dark mode already exist (lines 65-108 in globals.css) — we just need to wire up the toggle mechanism and ensure the `.dark` class is applied properly.

## Standard Stack

### Core Libraries (To Add)

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| next-themes | ^0.4.3 | Dark mode state management | Industry standard for Next.js, handles SSR hydration, localStorage persistence, system preference |

**Installation:**
```bash
cd frontend
pnpm add next-themes
```

### Existing Infrastructure (Already Integrated)

| Component | Location | Current State | Notes |
|-----------|----------|---------------|-------|
| Dark CSS Variables | `src/app/globals.css` lines 65-108 | ✅ Complete | All color tokens defined for `.dark` class |
| i18n Context | `src/lib/i18n/context.tsx` | ✅ Working | localStorage key: "cortex-locale" |
| Language Toggle | `src/components/admin/app-sidebar.tsx` lines 73-119 | ✅ Working | EN/FR pill toggle in sidebar footer |
| Translations | `src/lib/i18n/fr.ts`, `src/lib/i18n/en.ts` | ✅ Complete | 369 lines each, full coverage |
| LV Brand Colors | `src/app/globals.css` lines 26-28 | ✅ Applied | Primary: hsl(10 72% 34%), ring same |

## Architecture Patterns

### Pattern 1: Dark Mode with next-themes

**What:** Add ThemeProvider and theme toggle button using next-themes for SSR-safe dark mode

**Why this approach:**
- Prevents flash of unstyled content (FOUC) during hydration
- Handles localStorage persistence automatically
- Supports system preference detection
- Works with Tailwind's class-based dark mode strategy

**Implementation Strategy:**

1. **Add ThemeProvider to root layout** (src/app/layout.tsx):
```tsx
import { ThemeProvider } from "next-themes"

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={`${geistSans.variable} ${geistMono.variable} ${jetbrainsMono.variable} antialiased`}>
        <ThemeProvider
          attribute="class"
          defaultTheme="system"
          enableSystem
          disableTransitionOnChange
        >
          <QueryProvider>{children}</QueryProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
```

**Key props:**
- `attribute="class"`: Adds `dark` class to `<html>` element (matches Tailwind v4 strategy)
- `defaultTheme="system"`: Respects OS preference initially
- `enableSystem`: Allows "System" option in toggle
- `suppressHydrationWarning`: Prevents Next.js warning about class mismatch during hydration
- `disableTransitionOnChange`: Prevents jarring CSS transitions when switching themes

2. **Create ThemeToggle component** (new file: src/components/ui/theme-toggle.tsx):
```tsx
"use client";

import { Moon, Sun } from "lucide-react";
import { useTheme } from "next-themes";
import { Button } from "@/components/ui/button";
import { useEffect, useState } from "react";

export function ThemeToggle() {
  const { theme, setTheme } = useTheme();
  const [mounted, setMounted] = useState(false);

  // Prevent hydration mismatch by only rendering after mount
  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) {
    return <Button variant="ghost" size="icon" className="size-9" disabled />;
  }

  return (
    <Button
      variant="ghost"
      size="icon"
      onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
      className="size-9"
    >
      <Sun className="size-5 rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
      <Moon className="absolute size-5 rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
      <span className="sr-only">Toggle theme</span>
    </Button>
  );
}
```

**Why this pattern:**
- `mounted` state prevents hydration mismatch (theme is undefined on server)
- Sun/Moon icons swap with smooth rotation animation
- Icon sizing matches sidebar iconography (size-5)
- Screen reader accessible with sr-only label

3. **Add toggle to admin layout header** (src/app/(admin)/layout.tsx):

Place toggle in header next to breadcrumb, top-right corner:

```tsx
<header className="flex h-16 shrink-0 items-center gap-2 border-b px-4">
  <SidebarTrigger className="-ml-1" />
  <Separator orientation="vertical" className="mr-2 h-4" />
  <Breadcrumb>
    {/* existing breadcrumb */}
  </Breadcrumb>
  <div className="ml-auto">
    <ThemeToggle />
  </div>
</header>
```

**References:**
- [shadcn/ui Dark Mode Next.js Guide](https://ui.shadcn.com/docs/dark-mode/next)
- [next-themes GitHub](https://github.com/pacocoursey/next-themes)
- [Tailwind CSS v4 Dark Mode](https://tailwindcss.com/docs/dark-mode)

### Pattern 2: Tailwind CSS v4 Dark Mode Strategy

**Current Setup (Already Working):**

The project uses Tailwind CSS v4 with the **class strategy** via the `@custom-variant` directive:

```css
/* src/app/globals.css line 4 */
@custom-variant dark (&:is(.dark *));
```

This means:
- Dark mode activates when any parent element has class `dark`
- next-themes will add `class="dark"` to `<html>` element
- All `dark:*` utility classes will work automatically
- No tailwind.config.ts needed (inline theming via @theme block)

**Color Variable Structure:**

Light mode (`:root` lines 12-63):
```css
--background: hsl(0 0% 100%);
--foreground: hsl(240 10% 3.9%);
--primary: hsl(10 72% 34%);  /* LV brick red */
```

Dark mode (`.dark` lines 65-108):
```css
--background: hsl(240 10% 3.9%);
--foreground: hsl(0 0% 98%);
--primary: hsl(10 72% 50%);  /* Lighter LV red for contrast */
```

**Why this works:**
- CSS variables are bound to Tailwind utilities via `@theme inline` block (lines 110-151)
- Components use semantic color names: `bg-background`, `text-foreground`, `border-border`
- When `.dark` class is applied, all variables swap values automatically
- No component rewrites needed

**Testing checklist:**
- [ ] Sidebar dark theme persists across theme toggle
- [ ] Cards have proper contrast in both modes
- [ ] Form inputs readable in dark mode
- [ ] Charts/graphs remain legible
- [ ] PDF preview modal background adjusts

**References:**
- [Tailwind CSS v4 Inline Theming Guide](https://medium.com/@kevstrosky/theme-colors-with-tailwind-css-v4-0-and-next-themes-dark-light-custom-mode-36dca1e20419)
- [Theming in Tailwind CSS v4](https://medium.com/@sir.raminyavari/theming-in-tailwind-css-v4-support-multiple-color-schemes-and-dark-mode-ba97aead5c14)

### Pattern 3: FR/EN Language Bug Audit

**Current i18n System:**

Architecture (from Phase 16):
```
LanguageProvider (src/lib/i18n/context.tsx)
  ↓
localStorage "cortex-locale" (default: "fr")
  ↓
useLanguage() hook → { locale, setLocale, t }
  ↓
Components use t.nav.estimateur, t.fullQuote.titre, etc.
```

**Known working:**
- ✅ Nav items (app-sidebar.tsx uses useLanguage hook)
- ✅ Form labels (full-quote-form.tsx uses t.fullQuote.*)
- ✅ Breadcrumbs (admin layout uses routeLabels object)
- ✅ Static UI text (all components import useLanguage)

**Potential bugs (to investigate):**

1. **Tier descriptions in full-quote-form.tsx** (lines 54-96):
   - Uses inline ternary: `locale === 'fr' ? "French text" : "English text"`
   - ✅ Should work (hooks into locale state)
   - But not using translation files — inconsistent with rest of app

2. **AI-generated reasoning text** (backend estimate.py line 72):
   - Currently disabled: `reasoning = None`
   - When re-enabled, LLM prompts need to include language parameter
   - Backend has no concept of locale — frontend must send it

3. **Export templates** (Phase 24 - not yet implemented):
   - PDF exports via @react-pdf/renderer
   - DOCX exports (planned, not built)
   - Need bilingual templates with locale-aware content

**FR/EN bug fix strategy:**

**Wave 1: Frontend audit**
1. Search for hardcoded strings not in translation files
2. Move tier descriptions from inline ternaries to fr.ts/en.ts
3. Verify all components use `t.*` instead of direct strings
4. Test language toggle mid-session (switch EN→FR→EN while viewing results)

**Wave 2: Backend integration**
1. Add optional `locale` field to API request schemas
2. Pass locale to LLM reasoning prompts when generating explanations
3. Ensure similar cases display currency/units in user's language

**Wave 3: Export templates**
1. Create bilingual PDF templates (header, labels, footer)
2. Create bilingual DOCX templates (when implemented in Phase 24)
3. Use locale from request payload to select template language

**Audit commands:**
```bash
# Find hardcoded French strings
grep -r "Superficie\|Matériaux\|Soumission" frontend/src --include="*.tsx" --exclude-dir=i18n

# Find hardcoded English strings
grep -r "Square Footage\|Materials\|Quote" frontend/src --include="*.tsx" --exclude-dir=i18n

# Find inline ternaries with locale checks
grep -r "locale === 'fr'" frontend/src --include="*.tsx"
```

### Pattern 4: LV Branding Verification

**Current Brand Implementation:**

Primary brand color (Toiture LV brick red):
```css
/* Light mode */
--primary: hsl(10 72% 34%);
--primary-foreground: hsl(0 0% 98%);

/* Dark mode */
--primary: hsl(10 72% 50%);  /* Brighter for contrast */
--primary-foreground: hsl(240 5.9% 10%);
```

**Where brand colors appear:**

1. **Sidebar** (lines 54-62, 100-107 in globals.css):
   - Primary accent: `--sidebar-primary` uses same hsl(10 72% ...)
   - Border and ring use primary color
   - ✅ Branding applied

2. **Buttons** (components/ui/button.tsx):
   - Default variant uses `bg-primary text-primary-foreground`
   - ✅ Brand red on primary actions

3. **Form focus states** (globals.css line 45):
   - `--ring: hsl(10 72% 34%);` — focus rings are LV red
   - ✅ Branding applied

4. **Charts** (globals.css lines 47-52):
   - `--chart-1: hsl(10 72% 34%);` — primary chart color is LV red
   - ✅ Branding applied to dashboard

5. **PDF exports** (@react-pdf/renderer in frontend):
   - Need to verify PDF templates use LV colors
   - Logo placement, header colors, accent bars

6. **DOCX exports** (Phase 24 - not yet implemented):
   - Templates will need LV logo and brand colors
   - Pending implementation

**Branding verification checklist:**
- [ ] Header/sidebar show LV red accents in both light/dark mode
- [ ] Primary buttons use LV red background
- [ ] Focus rings on form inputs show LV red
- [ ] Charts on dashboard use LV red as primary color
- [ ] PDF exports have LV logo and red header
- [ ] DOCX exports (when implemented) have LV branding
- [ ] Dark mode preserves LV red accents (brighter variant for contrast)

**Color accessibility (WCAG):**
- Light mode primary (hsl 10 72% 34%) on white: Contrast ratio ~4.5:1 ✅
- Dark mode primary (hsl 10 72% 50%) on dark bg: Need to verify contrast
- Test with browser DevTools contrast checker

**Logo asset locations:**
```
frontend/public/          # Check for logo files
backend/templates/        # PDF/DOCX template assets (when created)
```

### Pattern 5: Hydration-Safe Theme Switching

**Problem:** Server renders with unknown theme, client hydrates with localStorage theme, causing flash/mismatch

**Solution:** next-themes injects blocking script in `<head>` to read localStorage before first paint

**Implementation details:**

1. **ThemeProvider must wrap all client components** but be placed in server component (layout.tsx)

2. **Use suppressHydrationWarning on html tag** to prevent Next.js warning:
```tsx
<html lang="en" suppressHydrationWarning>
```

3. **Theme-dependent UI must handle undefined state:**
```tsx
const [mounted, setMounted] = useState(false);

useEffect(() => {
  setMounted(true);
}, []);

if (!mounted) {
  return <Skeleton />; // Or null, or disabled button
}
```

4. **Avoid theme checks on server:**
```tsx
// ❌ BAD - will cause hydration mismatch
const { theme } = useTheme();
return <div className={theme === 'dark' ? 'dark-styles' : 'light-styles'}>

// ✅ GOOD - use Tailwind dark: variants
return <div className="bg-white dark:bg-gray-900">
```

**Why this matters:**
- Next.js 16 with React 19 has stricter hydration checks
- Mismatches cause console errors and potential layout shifts
- next-themes handles this with script injection + suppressHydrationWarning

**References:**
- [Don't use localStorage for Dark Mode in Next.js](https://medium.com/@kjinengineer/dont-use-localstorage-for-dark-mode-in-next-js-here-s-a-better-way-f6d4c98c3c07)
- [next-themes GitHub - Avoiding Hydration Mismatch](https://github.com/pacocoursey/next-themes)

## Known Challenges

### Challenge 1: Backend Language Support

**Issue:** Backend generates AI reasoning and template content but has no concept of user locale

**Current state:**
- Frontend sends requests with form data (sqft, category, etc.)
- Backend returns reasoning text in hardcoded language (likely French from prompts)
- Reasoning currently disabled (estimate.py line 72: `reasoning = None`)

**Solutions:**

**Option A: Add locale to request schemas** (Recommended)
```python
# app/schemas/estimate.py
class EstimateRequest(BaseModel):
    sqft: int
    category: str
    # ... other fields
    locale: Optional[str] = "fr"  # Default to French

# app/services/llm_reasoning.py
def generate_reasoning_stream(locale: str = "fr"):
    if locale == "en":
        system_prompt = "You are a roofing estimator. Explain in English..."
    else:
        system_prompt = "Vous êtes un estimateur de toiture. Expliquez en français..."
```

**Option B: Detect from Accept-Language header**
```python
from fastapi import Request

@router.post("/estimate")
def create_estimate(request: EstimateRequest, req: Request):
    locale = req.headers.get("Accept-Language", "fr-CA")[:2]
    # Use locale for reasoning generation
```

**Recommendation:** Option A — explicit locale parameter is more predictable and testable

**Impact:** Low effort, high value — ensures AI explanations match user's language

### Challenge 2: PDF Export Language

**Issue:** @react-pdf/renderer components may have hardcoded French labels

**Current state:**
- PDF generation exists in frontend (uses @react-pdf/renderer)
- Need to audit PDF template for language support

**Solution:**
```tsx
// In PDF component
import { useLanguage } from "@/lib/i18n";

export function QuotePDF() {
  const { t } = useLanguage();

  return (
    <Document>
      <Page>
        <Text>{t.fullQuote.soumission}</Text> {/* "SOUMISSION" or "QUOTE" */}
        {/* ... rest of template using t.* */}
      </Page>
    </Document>
  );
}
```

**Verification needed:**
- Locate PDF template component
- Check for hardcoded "SOUMISSION", "Matériaux", "Total"
- Replace with translation keys
- Test PDF generation in both languages

### Challenge 3: Dark Mode in Charts

**Issue:** Recharts library may need theme-aware color configuration

**Current state:**
- Dashboard uses Recharts for analytics (package.json: "recharts": "^2.15.4")
- Chart colors defined in CSS variables (--chart-1 through --chart-5)

**Solution:** Recharts respects CSS variables, but axis labels may need manual color updates

Example fix:
```tsx
<LineChart data={data}>
  <XAxis
    stroke="hsl(var(--muted-foreground))"  // Use semantic color
    className="text-xs"
  />
  <Tooltip
    contentStyle={{
      backgroundColor: 'hsl(var(--popover))',
      borderColor: 'hsl(var(--border))',
      color: 'hsl(var(--popover-foreground))',
    }}
  />
</LineChart>
```

**Testing needed:**
- View dashboard in dark mode
- Check chart axis labels are readable
- Verify tooltip background has proper contrast
- Ensure legend text is visible

## Implementation Waves

### Wave 1: Dark Mode Toggle (High Priority)
**Goal:** Working dark mode toggle with theme persistence

**Tasks:**
1. Install next-themes: `pnpm add next-themes`
2. Add ThemeProvider to src/app/layout.tsx
3. Create src/components/ui/theme-toggle.tsx
4. Add ThemeToggle to admin layout header (top-right)
5. Test theme switching and localStorage persistence
6. Verify dark mode CSS variables work across all pages

**Success criteria:**
- [ ] Sun/moon button appears in top-right corner
- [ ] Click toggles between light and dark mode
- [ ] Theme persists after page refresh
- [ ] No hydration mismatch errors in console
- [ ] Sidebar, forms, cards all readable in dark mode

**Files to modify:**
- `frontend/package.json` (add next-themes)
- `frontend/src/app/layout.tsx` (wrap with ThemeProvider)
- `frontend/src/components/ui/theme-toggle.tsx` (new file)
- `frontend/src/app/(admin)/layout.tsx` (add toggle to header)

### Wave 2: FR/EN Bug Audit (Medium Priority)
**Goal:** Ensure all content respects language toggle

**Tasks:**
1. Run grep commands to find hardcoded strings
2. Move tier descriptions from inline ternaries to translation files
3. Add locale parameter to backend API schemas
4. Update LLM reasoning to use locale-aware prompts
5. Test mid-session language switching (EN→FR→EN)

**Success criteria:**
- [ ] All UI text switches language immediately
- [ ] Tier descriptions use translation files
- [ ] No hardcoded French/English strings outside i18n/
- [ ] AI reasoning respects user's language (when re-enabled)

**Files to modify:**
- `frontend/src/lib/i18n/fr.ts` (add missing tier keys)
- `frontend/src/lib/i18n/en.ts` (add missing tier keys)
- `frontend/src/components/estimateur/full-quote-form.tsx` (use t.* for tiers)
- `backend/app/schemas/estimate.py` (add locale field)
- `backend/app/services/llm_reasoning.py` (locale-aware prompts)

### Wave 3: Branding Verification (Low Priority)
**Goal:** Confirm LV brand colors applied everywhere

**Tasks:**
1. Audit PDF template for LV logo and brand colors
2. Verify dark mode preserves LV red accents
3. Test contrast ratios for accessibility
4. Check charts use LV red as primary color
5. Document brand color usage for Phase 24 (DOCX templates)

**Success criteria:**
- [ ] LV red visible in header, buttons, focus rings (both modes)
- [ ] PDF exports have LV logo and red header
- [ ] Dark mode LV red passes contrast checks
- [ ] Charts show LV red as primary color
- [ ] Brand guidelines documented for future templates

**Files to audit:**
- `frontend/src/app/globals.css` (verify --primary values)
- `frontend/src/components/**/pdf-*.tsx` (if exists)
- `frontend/src/components/apercu/*` (dashboard charts)

## Testing Strategy

### Unit Tests (Optional - No Tests Currently)
Project has no test files. If adding tests:
```bash
# Install testing libraries
pnpm add -D @testing-library/react @testing-library/jest-dom vitest

# Test theme toggle
- Renders sun icon in light mode
- Renders moon icon in dark mode
- Calls setTheme on click

# Test i18n
- useLanguage returns correct locale
- setLocale updates localStorage
- Translation keys exist in both fr.ts and en.ts
```

### Manual Testing Checklist

**Dark mode toggle:**
- [ ] Toggle switches between light and dark
- [ ] Theme persists after refresh
- [ ] System preference option works (if implemented)
- [ ] No FOUC (flash of unstyled content)
- [ ] All pages readable in both modes

**Language toggle:**
- [ ] Switch EN→FR updates all UI text
- [ ] Switch FR→EN updates all UI text
- [ ] Tier descriptions change language
- [ ] Form labels change language
- [ ] Nav items change language
- [ ] Language persists after refresh

**Branding:**
- [ ] Primary buttons show LV red
- [ ] Sidebar accents show LV red
- [ ] Focus rings show LV red
- [ ] Charts use LV red
- [ ] PDF exports have LV logo (if templates exist)

**Cross-browser:**
- [ ] Chrome/Edge (Chromium)
- [ ] Firefox
- [ ] Safari (macOS/iOS)

**Accessibility:**
- [ ] Tab navigation works with theme toggle
- [ ] Screen reader announces theme change
- [ ] Contrast ratios pass WCAG AA (4.5:1)
- [ ] Focus indicators visible in both modes

## Dependencies

### Phase Dependencies
- Phase 15 (Frontend Design Overhaul): ✅ Complete — Lyra theme and CSS variables already set up
- Phase 16 (I18n Language Toggle): ✅ Complete — LanguageContext and translations exist
- Phase 24 (Export & Send): ⏳ Planned — Will need bilingual PDF/DOCX templates

### External Dependencies
- next-themes library (install with pnpm)
- Tailwind CSS v4 dark mode support (already configured)
- lucide-react icons (already installed)

### Business Logic Dependencies
**None** — This phase is purely UI/UX polish with no backend logic requirements

## Open Questions for Planning

1. **Theme options:** Should we support "System" preference or just Light/Dark toggle?
   - Recommendation: Support all 3 (Light/Dark/System) for flexibility
   - Implementation: next-themes handles this by default with `enableSystem`

2. **Default theme:** Should new users start with Light or Dark mode?
   - Current: defaultTheme="system" respects OS preference
   - Alternative: defaultTheme="light" for consistency

3. **Tier descriptions:** Move to translation files or keep inline?
   - Recommendation: Move to fr.ts/en.ts for consistency with rest of app
   - Impact: Small refactor in full-quote-form.tsx

4. **AI reasoning language:** Should backend auto-detect or require explicit locale?
   - Recommendation: Explicit locale parameter in request schema
   - Rationale: More predictable, easier to test

5. **PDF templates:** Do current PDF exports exist? Need audit.
   - Action: Search codebase for @react-pdf/renderer usage
   - If found: Add locale support; If not: Document requirement for Phase 24

6. **Toggle placement:** Top-right header or sidebar footer?
   - Requirement says "top-right corner"
   - Recommendation: Header next to breadcrumb (more visible)

## Resources

### Documentation
- [shadcn/ui Dark Mode - Next.js](https://ui.shadcn.com/docs/dark-mode/next)
- [next-themes GitHub Repository](https://github.com/pacocoursey/next-themes)
- [Tailwind CSS v4 Dark Mode](https://tailwindcss.com/docs/dark-mode)
- [Next.js 15 + Tailwind v4 + Dark Mode Guide](https://dev.to/darshan_bajgain/setting-up-2025-nextjs-15-with-shadcn-tailwind-css-v4-no-config-needed-dark-mode-5kl)

### Examples
- [2-line Dark Mode with next-themes](https://dev.to/ramunarasinga/shadcn-ui-codebase-analysis-perfect-nextjs-dark-mode-in-2-lines-of-code-with-next-themes-8f5)
- [Theme Colors with Tailwind v4 + Next Themes](https://medium.com/@kevstrosky/theme-colors-with-tailwind-css-v4-0-and-next-themes-dark-light-custom-mode-36dca1e20419)
- [Theming in Tailwind CSS v4](https://medium.com/@sir.raminyavari/theming-in-tailwind-css-v4-support-multiple-color-schemes-and-dark-mode-ba97aead5c14)

### Tools
- Chrome DevTools Contrast Checker (for WCAG compliance)
- React DevTools (verify ThemeProvider wrapping)
- localStorage inspector (verify theme persistence)

## Next Steps for Planning

1. **Break down into 2-3 plans:**
   - Plan 25-01: Dark mode toggle with next-themes
   - Plan 25-02: FR/EN bug audit and tier description refactor
   - Plan 25-03: Branding verification and contrast testing (optional)

2. **Estimate effort:**
   - Plan 25-01: ~2-3 hours (install, implement, test toggle)
   - Plan 25-02: ~3-4 hours (grep audit, refactor, backend locale param)
   - Plan 25-03: ~1-2 hours (visual audit, PDF check)

3. **Identify quick wins:**
   - Dark mode toggle can be implemented in isolation (no backend changes)
   - Translation file updates are low-risk refactors
   - Branding verification is mostly manual testing

4. **Flag blockers:**
   - None identified — all dependencies met, no business logic required
   - PDF template audit may reveal missing templates (document for Phase 24)

---

**Confidence Level:** HIGH
- Tailwind v4 dark mode is well-documented and stable
- next-themes is the industry-standard solution for Next.js
- CSS variables already defined — just need toggle mechanism
- i18n system proven working from Phase 16

**Risk Level:** LOW
- No breaking changes to existing functionality
- Pure additive features (toggle, translation cleanup)
- Graceful degradation if next-themes fails (renders disabled button)

**Recommended First Step:** Implement Plan 25-01 (dark mode toggle) as standalone proof-of-concept before tackling language audit.
