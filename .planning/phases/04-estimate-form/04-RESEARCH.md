# Phase 4: Estimate Form - Research

**Researched:** 2026-01-18
**Domain:** Next.js 15 App Router, Form handling, shadcn/ui components, API integration
**Confidence:** HIGH

## Summary

This phase builds a Next.js frontend where users input job details and see ML-powered estimates with similar cases and LLM reasoning. The frontend calls the existing FastAPI backend `/estimate` endpoint (from Phases 1-3) that returns estimate, range, confidence, similar cases, and reasoning.

The standard approach in 2025-2026 uses **Next.js 15 with App Router**, **shadcn/ui for form components** (built on Radix UI), **React Hook Form + Zod** for form state and validation, and **react-markdown** for rendering LLM reasoning. For a simple form like this, Client Components with direct fetch to the backend are the cleanest approach - Server Actions are unnecessary since we're calling an external API, not mutating local data.

**Primary recommendation:** Use Next.js 15 App Router with shadcn/ui form components (Input, Select, Slider, Switch), React Hook Form + Zod for validation, direct fetch to FastAPI backend from a Client Component, and Card components to display results and similar cases.

## Standard Stack

The established libraries/tools for this domain:

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| next | 15.x | React framework | App Router, built-in TypeScript, Vercel deployment |
| react | 19.x | UI library | Bundled with Next.js 15, hooks for state |
| typescript | 5.x | Type safety | Standard for modern React projects |
| tailwindcss | 4.x | Utility CSS | Pairs with shadcn/ui, fast styling |
| shadcn/ui | latest | UI components | Accessible Radix primitives, copy-paste ownership |
| react-hook-form | 7.x | Form state | Controlled components, low re-renders |
| zod | 3.x | Schema validation | TypeScript inference, shared with backend concepts |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| react-markdown | 10.x | Render LLM reasoning | Display markdown from API |
| @radix-ui/react-* | (via shadcn) | Accessible primitives | Underlying shadcn components |
| lucide-react | latest | Icons | Icons in shadcn/ui |
| class-variance-authority | latest | Variant styling | Used by shadcn/ui components |
| clsx | latest | Class merging | Used by shadcn/ui cn() utility |
| tailwind-merge | latest | Tailwind class merging | Used by shadcn/ui cn() utility |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| shadcn/ui | Radix primitives directly | More control but more boilerplate |
| shadcn/ui | Chakra UI / MUI | Less customization control, larger bundle |
| react-hook-form | Native form + useState | More boilerplate, worse performance |
| react-hook-form | Formik | Heavier, older patterns |
| react-markdown | MDX | Overkill for display-only, adds complexity |
| Zod client-side | HTML5 validation only | No TypeScript inference, less control |

**Installation:**
```bash
# Create Next.js project
pnpm create next-app@latest frontend --typescript --tailwind --eslint --app --src-dir --import-alias "@/*"

# Initialize shadcn/ui
cd frontend
pnpm dlx shadcn@latest init

# Add required shadcn components
pnpm dlx shadcn@latest add form input select slider switch button card label

# Additional dependencies
pnpm add react-markdown zod @hookform/resolvers
```

## Architecture Patterns

### Recommended Project Structure

```
frontend/
├── src/
│   ├── app/
│   │   ├── layout.tsx          # Root layout with providers
│   │   ├── page.tsx            # Home page (estimate form)
│   │   └── globals.css         # Tailwind imports
│   ├── components/
│   │   ├── ui/                 # shadcn/ui components (auto-generated)
│   │   │   ├── button.tsx
│   │   │   ├── card.tsx
│   │   │   ├── form.tsx
│   │   │   ├── input.tsx
│   │   │   ├── select.tsx
│   │   │   ├── slider.tsx
│   │   │   └── switch.tsx
│   │   ├── estimate-form.tsx   # Main form component (Client Component)
│   │   ├── estimate-result.tsx # Result display (estimate + range)
│   │   ├── similar-cases.tsx   # Similar cases list
│   │   └── reasoning-display.tsx # LLM reasoning with markdown
│   ├── lib/
│   │   ├── utils.ts            # cn() helper (shadcn)
│   │   ├── api.ts              # API client for backend
│   │   └── schemas.ts          # Zod schemas for form + response
│   └── types/
│       └── estimate.ts         # TypeScript types
├── public/
├── .env.local                  # NEXT_PUBLIC_API_URL
├── next.config.ts
├── tailwind.config.ts
├── components.json             # shadcn/ui config
└── package.json
```

### Pattern 1: Client Component Form with Direct Fetch

**What:** Use a Client Component for the form with direct fetch to FastAPI backend
**When to use:** When calling an external API (not mutating Next.js data)
**Why not Server Actions:** Server Actions are for server-side mutations. Direct fetch is simpler for external APIs.

```typescript
// src/components/estimate-form.tsx
"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { estimateFormSchema, EstimateFormData } from "@/lib/schemas";
import { submitEstimate, EstimateResponse } from "@/lib/api";

export function EstimateForm() {
  const [result, setResult] = useState<EstimateResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const form = useForm<EstimateFormData>({
    resolver: zodResolver(estimateFormSchema),
    defaultValues: {
      sqft: 1500,
      category: "Bardeaux",
      material_lines: 5,
      labor_lines: 2,
      has_subs: false,
      complexity: 10,
    },
  });

  async function onSubmit(data: EstimateFormData) {
    setIsLoading(true);
    setError(null);
    try {
      const response = await submitEstimate(data);
      setResult(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to get estimate");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <form onSubmit={form.handleSubmit(onSubmit)}>
      {/* Form fields */}
    </form>
  );
}
```

### Pattern 2: Zod Schema for Form Validation

**What:** Define form schema with Zod for client-side validation + TypeScript inference
**When to use:** Always for forms with validation requirements

```typescript
// src/lib/schemas.ts
import { z } from "zod";

// Categories matching backend ALLOWED_CATEGORIES
export const CATEGORIES = [
  "Bardeaux",
  "Elastomere", // Frontend sends without accent, backend normalizes
  "Other",
  "Gutters",
  "Heat Cables",
  "Insulation",
  "Service Call",
  "Skylights",
  "Unknown",
  "Ventilation",
] as const;

export const estimateFormSchema = z.object({
  sqft: z.coerce
    .number()
    .positive("Square footage must be positive")
    .max(100000, "Square footage cannot exceed 100,000"),
  category: z.enum(CATEGORIES, {
    errorMap: () => ({ message: "Please select a category" }),
  }),
  material_lines: z.coerce
    .number()
    .int()
    .min(0, "Cannot be negative")
    .max(100, "Cannot exceed 100"),
  labor_lines: z.coerce
    .number()
    .int()
    .min(0, "Cannot be negative")
    .max(50, "Cannot exceed 50"),
  has_subs: z.boolean(),
  complexity: z.coerce
    .number()
    .int()
    .min(1, "Minimum complexity is 1")
    .max(100, "Maximum complexity is 100"),
});

export type EstimateFormData = z.infer<typeof estimateFormSchema>;
```

### Pattern 3: API Client with Type Safety

**What:** Typed API client for backend communication
**When to use:** All external API calls

```typescript
// src/lib/api.ts
import { EstimateFormData } from "./schemas";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface SimilarCase {
  case_id: string;
  similarity: number;
  category: string | null;
  sqft: number | null;
  total: number | null;
  per_sqft: number | null;
  year: number | null;
}

export interface EstimateResponse {
  estimate: number;
  range_low: number;
  range_high: number;
  confidence: "HIGH" | "MEDIUM" | "LOW";
  model: string;
  similar_cases: SimilarCase[];
  reasoning: string | null;
}

export async function submitEstimate(data: EstimateFormData): Promise<EstimateResponse> {
  const response = await fetch(`${API_URL}/estimate`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      ...data,
      has_subs: data.has_subs ? 1 : 0, // Convert boolean to 0/1 for backend
    }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || `Request failed: ${response.status}`);
  }

  return response.json();
}
```

### Pattern 4: shadcn/ui Form with React Hook Form

**What:** Use shadcn/ui Form components with React Hook Form integration
**When to use:** All forms with shadcn/ui

```typescript
// src/components/estimate-form.tsx (form fields)
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Slider } from "@/components/ui/slider";
import { Switch } from "@/components/ui/switch";
import { Button } from "@/components/ui/button";
import { CATEGORIES } from "@/lib/schemas";

// Inside the form component:
<Form {...form}>
  <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
    {/* Square Footage - Number Input */}
    <FormField
      control={form.control}
      name="sqft"
      render={({ field }) => (
        <FormItem>
          <FormLabel>Square Footage</FormLabel>
          <FormControl>
            <Input
              type="number"
              placeholder="1500"
              {...field}
            />
          </FormControl>
          <FormDescription>Total roof area in square feet</FormDescription>
          <FormMessage />
        </FormItem>
      )}
    />

    {/* Category - Select Dropdown */}
    <FormField
      control={form.control}
      name="category"
      render={({ field }) => (
        <FormItem>
          <FormLabel>Category</FormLabel>
          <Select onValueChange={field.onChange} defaultValue={field.value}>
            <FormControl>
              <SelectTrigger>
                <SelectValue placeholder="Select category" />
              </SelectTrigger>
            </FormControl>
            <SelectContent>
              {CATEGORIES.map((cat) => (
                <SelectItem key={cat} value={cat}>
                  {cat}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          <FormMessage />
        </FormItem>
      )}
    />

    {/* Complexity - Slider */}
    <FormField
      control={form.control}
      name="complexity"
      render={({ field }) => (
        <FormItem>
          <FormLabel>Complexity: {field.value}</FormLabel>
          <FormControl>
            <Slider
              min={1}
              max={100}
              step={1}
              value={[field.value]}
              onValueChange={(value) => field.onChange(value[0])}
            />
          </FormControl>
          <FormDescription>Job complexity (1 = simple, 100 = very complex)</FormDescription>
          <FormMessage />
        </FormItem>
      )}
    />

    {/* Has Subcontractors - Toggle Switch */}
    <FormField
      control={form.control}
      name="has_subs"
      render={({ field }) => (
        <FormItem className="flex items-center justify-between">
          <div>
            <FormLabel>Has Subcontractors</FormLabel>
            <FormDescription>Will this job involve subcontractors?</FormDescription>
          </div>
          <FormControl>
            <Switch
              checked={field.value}
              onCheckedChange={field.onChange}
            />
          </FormControl>
        </FormItem>
      )}
    />

    <Button type="submit" disabled={isLoading}>
      {isLoading ? "Getting Estimate..." : "Get Estimate"}
    </Button>
  </form>
</Form>
```

### Pattern 5: Result Display with Cards

**What:** Display estimate results in Card components
**When to use:** Showing structured results

```typescript
// src/components/estimate-result.tsx
"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { EstimateResponse } from "@/lib/api";

interface EstimateResultProps {
  result: EstimateResponse;
}

export function EstimateResult({ result }: EstimateResultProps) {
  const confidenceColor = {
    HIGH: "text-green-600",
    MEDIUM: "text-yellow-600",
    LOW: "text-red-600",
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-3xl">
          ${result.estimate.toLocaleString()}
        </CardTitle>
        <CardDescription>
          Range: ${result.range_low.toLocaleString()} - ${result.range_high.toLocaleString()}
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="flex items-center gap-4">
          <span className={confidenceColor[result.confidence]}>
            {result.confidence} confidence
          </span>
          <span className="text-muted-foreground text-sm">
            Model: {result.model}
          </span>
        </div>
      </CardContent>
    </Card>
  );
}
```

### Pattern 6: Similar Cases Display

**What:** Display similar historical cases in a list or grid
**When to use:** FORM-04 requirement

```typescript
// src/components/similar-cases.tsx
"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { SimilarCase } from "@/lib/api";

interface SimilarCasesProps {
  cases: SimilarCase[];
}

export function SimilarCases({ cases }: SimilarCasesProps) {
  if (cases.length === 0) {
    return (
      <Card>
        <CardContent className="pt-6">
          <p className="text-muted-foreground">No similar cases found.</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Similar Historical Cases</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {cases.map((c, index) => (
            <div key={c.case_id} className="border-b pb-4 last:border-0">
              <div className="flex justify-between items-start">
                <div>
                  <p className="font-medium">
                    {c.category || "Unknown"} ({c.year || "N/A"})
                  </p>
                  <p className="text-sm text-muted-foreground">
                    {c.sqft?.toLocaleString() || "N/A"} sqft
                  </p>
                </div>
                <div className="text-right">
                  <p className="font-medium">
                    ${c.total?.toLocaleString() || "N/A"}
                  </p>
                  <p className="text-sm text-muted-foreground">
                    ${c.per_sqft?.toFixed(2) || "N/A"}/sqft
                  </p>
                </div>
              </div>
              <p className="text-xs text-muted-foreground mt-1">
                {(c.similarity * 100).toFixed(0)}% similar
              </p>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
```

### Pattern 7: Markdown Reasoning Display

**What:** Render LLM reasoning with react-markdown
**When to use:** FORM-05 requirement

```typescript
// src/components/reasoning-display.tsx
"use client";

import Markdown from "react-markdown";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface ReasoningDisplayProps {
  reasoning: string | null;
}

export function ReasoningDisplay({ reasoning }: ReasoningDisplayProps) {
  if (!reasoning) {
    return null;
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>AI Reasoning</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="prose prose-sm max-w-none dark:prose-invert">
          <Markdown>{reasoning}</Markdown>
        </div>
      </CardContent>
    </Card>
  );
}
```

### Anti-Patterns to Avoid

- **Using Server Actions for external API calls:** Server Actions are for server-side mutations. Direct fetch is simpler for calling external APIs.
- **Putting form state in multiple useState calls:** Use React Hook Form for unified form state management.
- **Not handling loading/error states:** Always show loading indicators and error messages.
- **Hardcoding API URL:** Use environment variables for flexibility.
- **Not validating client-side:** Always validate before sending to reduce failed requests.
- **Using dangerouslySetInnerHTML for markdown:** Use react-markdown for security.

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Form validation | Manual if/else | Zod + React Hook Form | Type inference, declarative, battle-tested |
| Accessible select | Native <select> | shadcn Select (Radix) | Keyboard nav, screen readers, styling |
| Accessible slider | Range input | shadcn Slider (Radix) | Touch support, ARIA, styling |
| Accessible toggle | Checkbox | shadcn Switch (Radix) | Proper toggle semantics |
| Loading states | Manual flags | React Hook Form isSubmitting + useState | Integrated, consistent |
| Markdown rendering | innerHTML | react-markdown | XSS safe, component customization |
| Error display | Manual try/catch | Form + FormMessage | Consistent, accessible |

**Key insight:** shadcn/ui gives you copy-paste ownership of accessible components. Don't build accessibility from scratch.

## Common Pitfalls

### Pitfall 1: Forgetting NEXT_PUBLIC_ Prefix for API URL

**What goes wrong:** API URL is undefined in browser, fetch fails
**Why it happens:** Environment variables without NEXT_PUBLIC_ are server-only
**How to avoid:** Always prefix client-side env vars with NEXT_PUBLIC_
**Warning signs:** "Cannot read property 'replace' of undefined" or empty API URL

```typescript
// WRONG
const API_URL = process.env.API_URL; // undefined in browser

// CORRECT
const API_URL = process.env.NEXT_PUBLIC_API_URL;
```

### Pitfall 2: CORS Errors in Development

**What goes wrong:** "Access to fetch blocked by CORS policy"
**Why it happens:** Frontend (localhost:3000) and backend (localhost:8000) are different origins
**How to avoid:** Ensure FastAPI CORS includes frontend origin (already done in Phase 1)
**Warning signs:** Network requests fail with CORS error in browser console

```python
# Backend already configured in Phase 1:
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Must include frontend
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

### Pitfall 3: Not Converting has_subs Boolean to 0/1

**What goes wrong:** Backend validation error (expects 0 or 1, not true/false)
**Why it happens:** Form uses boolean Switch, backend expects Literal[0, 1]
**How to avoid:** Convert in API client before sending
**Warning signs:** 422 validation error on has_subs field

```typescript
// In API client:
body: JSON.stringify({
  ...data,
  has_subs: data.has_subs ? 1 : 0, // Convert boolean to 0/1
}),
```

### Pitfall 4: Not Providing Default Values in React Hook Form

**What goes wrong:** Controlled component warning, form fields undefined
**Why it happens:** shadcn Form components require controlled inputs
**How to avoid:** Always provide defaultValues in useForm
**Warning signs:** React warning about uncontrolled to controlled, undefined field values

```typescript
const form = useForm<EstimateFormData>({
  resolver: zodResolver(estimateFormSchema),
  defaultValues: {
    sqft: 1500,
    category: "Bardeaux",
    material_lines: 5,
    labor_lines: 2,
    has_subs: false,
    complexity: 10,
  },
});
```

### Pitfall 5: Slider Value Array vs Number

**What goes wrong:** TypeScript error or slider doesn't update
**Why it happens:** Radix Slider uses array for value (supports range), form expects number
**How to avoid:** Extract first element from value array, wrap form value in array
**Warning signs:** Type mismatch errors, slider not reflecting form state

```typescript
<Slider
  value={[field.value]}  // Wrap number in array for Slider
  onValueChange={(value) => field.onChange(value[0])}  // Extract first value
/>
```

### Pitfall 6: z.coerce for Form Inputs

**What goes wrong:** Type error - string vs number
**Why it happens:** HTML inputs always return strings, even type="number"
**How to avoid:** Use z.coerce.number() in Zod schema
**Warning signs:** "Expected number, received string" validation errors

```typescript
// WRONG
sqft: z.number().positive(),  // Fails because input returns string

// CORRECT
sqft: z.coerce.number().positive(),  // Coerces string "1500" to number 1500
```

## Code Examples

Verified patterns from official sources:

### Complete Page Component

```typescript
// src/app/page.tsx
import { EstimateForm } from "@/components/estimate-form";

export default function Home() {
  return (
    <main className="container mx-auto py-8 px-4 max-w-2xl">
      <h1 className="text-3xl font-bold mb-8">TOITURELV Cortex</h1>
      <p className="text-muted-foreground mb-8">
        Get AI-powered price estimates for roofing jobs
      </p>
      <EstimateForm />
    </main>
  );
}
```

### Complete Layout

```typescript
// src/app/layout.tsx
import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "TOITURELV Cortex",
  description: "AI-powered roofing price estimates",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={inter.className}>{children}</body>
    </html>
  );
}
```

### Environment Configuration

```bash
# .env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
```

```bash
# .env.production (for Vercel)
NEXT_PUBLIC_API_URL=https://your-railway-app.railway.app
```

### next.config.ts

```typescript
// next.config.ts
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // No special config needed for this simple setup
};

export default nextConfig;
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Pages Router | App Router | Next.js 13+ (2023) | Server Components default, layouts |
| getServerSideProps | Server Components + fetch | Next.js 13+ | Simpler data fetching |
| Formik | React Hook Form | 2022-2023 | Lighter, better performance |
| styled-components | Tailwind CSS | 2022-2024 | Utility-first, smaller bundle |
| Custom UI | shadcn/ui | 2023-2024 | Copy-paste, accessible, customizable |
| React 18 | React 19 | 2024-2025 | useActionState, useFormStatus, useOptimistic |
| Pydantic v1 style schemas | Zod TypeScript-first | 2023+ | Better TS inference |

**Deprecated/outdated:**
- Next.js Pages Router: Still works but App Router is default
- `useFormState`: Renamed to `useActionState` in React 19
- Class components: Functional components with hooks standard
- Create React App: Next.js or Vite preferred

## Open Questions

Things that couldn't be fully resolved:

1. **Category display names (French vs English)**
   - What we know: Backend uses "Elastomere" (without accent for frontend), normalizes to "Elastomere" internally
   - What's unclear: Whether to show French names like "Elastomere" or English translations
   - Recommendation: Use backend category names as-is since this is an internal tool for Quebec company

2. **Dark mode support**
   - What we know: shadcn/ui supports dark mode via CSS variables
   - What's unclear: Whether user wants dark mode toggle
   - Recommendation: Defer to Phase 7 or later, start with light mode only

3. **Currency formatting (CAD vs USD)**
   - What we know: TOITURELV is Quebec-based (CAD)
   - What's unclear: Whether to show $ or CAD$
   - Recommendation: Use $ (standard for Canadian businesses), add CAD if needed later

## Sources

### Primary (HIGH confidence)
- [Next.js Official Docs - App Router](https://nextjs.org/docs/app/getting-started/project-structure) - Project structure, routing
- [Next.js Official Docs - Forms](https://nextjs.org/docs/app/guides/forms) - Form handling patterns
- [shadcn/ui Official Docs](https://ui.shadcn.com/docs/installation/next) - Installation, components
- [React Hook Form Official Docs](https://react-hook-form.com/) - Form state management
- [Zod Official Docs](https://zod.dev/) - Schema validation
- [react-markdown GitHub](https://github.com/remarkjs/react-markdown) - Markdown rendering

### Secondary (MEDIUM confidence)
- [shadcn/ui Form Component](https://ui.shadcn.com/docs/components/form) - RHF integration patterns
- [Vercel Environment Variables](https://vercel.com/docs/projects/environment-variables) - NEXT_PUBLIC_ pattern
- WebSearch results for "Next.js 15 form best practices 2025" - Community patterns

### Tertiary (LOW confidence)
- Various Medium articles on Next.js + shadcn/ui (verified with official docs)

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - Verified with official Next.js, shadcn/ui, React Hook Form docs
- Architecture: HIGH - Based on official documentation and established patterns
- Pitfalls: HIGH - Common issues documented in official troubleshooting and community

**Research date:** 2026-01-18
**Valid until:** 2026-02-18 (30 days - Next.js and shadcn/ui are stable)

---

## Appendix: Requirements Mapping

| Requirement | Implementation |
|-------------|----------------|
| FORM-01: 6 input fields | shadcn Input (sqft), Select (category), Input (material/labor lines), Switch (has_subs), Slider (complexity) |
| FORM-02: Submit calls /estimate | fetch() in Client Component, API client module |
| FORM-03: Display estimate with range/confidence | EstimateResult component with Card |
| FORM-04: Display similar cases | SimilarCases component with Card list |
| FORM-05: Display LLM reasoning | ReasoningDisplay component with react-markdown |

## Appendix: Backend API Contract

From Phase 1-3 research, the /estimate endpoint:

**Request (POST /estimate):**
```json
{
  "sqft": 1500,
  "category": "Bardeaux",
  "material_lines": 5,
  "labor_lines": 2,
  "has_subs": 0,
  "complexity": 10
}
```

**Response:**
```json
{
  "estimate": 12500.00,
  "range_low": 10000.00,
  "range_high": 15000.00,
  "confidence": "HIGH",
  "model": "Bardeaux (R2=0.65)",
  "similar_cases": [
    {
      "case_id": "Q-12345",
      "similarity": 0.92,
      "category": "Bardeaux",
      "sqft": 1450,
      "total": 12000,
      "per_sqft": 8.27,
      "year": 2024
    }
  ],
  "reasoning": "This estimate is based on 5 similar Bardeaux jobs..."
}
```
