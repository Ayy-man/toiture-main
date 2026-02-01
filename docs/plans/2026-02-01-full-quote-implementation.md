# Full Quote Frontend Integration Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Wire up the `/estimate/hybrid` endpoint to the frontend "Soumission Complète" tab with complexity presets, invoice-style output, and PDF export.

**Architecture:** Form with complexity presets (Simple/Modéré/Complexe) calls POST /estimate/hybrid, displays invoice-style result with work items and totals, exports client-facing PDF (no hours shown).

**Tech Stack:** Next.js 15, React Hook Form, Zod, @react-pdf/renderer, shadcn/ui components

**Design Doc:** `docs/plans/2026-02-01-full-quote-frontend-design.md`

---

## Phase 14A: Core Quote Generation

### Task 1: Add Hybrid Quote TypeScript Types

**Files:**
- Create: `frontend/src/types/hybrid-quote.ts`

**Step 1: Create types file**

```typescript
// frontend/src/types/hybrid-quote.ts

/**
 * Work item (labor task) from hybrid quote
 */
export interface WorkItem {
  name: string;
  labor_hours: number;
  source: "CBR" | "ML" | "MERGED";
}

/**
 * Material line item from hybrid quote
 */
export interface MaterialLineItem {
  material_id: number;
  quantity: number;
  unit_price: number;
  total: number;
  source: "CBR" | "ML" | "MERGED";
  confidence: number;
}

/**
 * Pricing tier (Basic/Standard/Premium)
 */
export interface PricingTier {
  tier: "Basic" | "Standard" | "Premium";
  total_price: number;
  materials_cost: number;
  labor_cost: number;
  description: string;
}

/**
 * Complexity preset values
 */
export interface ComplexityPreset {
  access_difficulty: number;
  roof_pitch: number;
  penetrations: number;
  material_removal: number;
  safety_concerns: number;
  timeline_constraints: number;
}

/**
 * Complexity preset definitions
 */
export const COMPLEXITY_PRESETS: Record<"simple" | "moderate" | "complex", ComplexityPreset> = {
  simple: {
    access_difficulty: 2,
    roof_pitch: 2,
    penetrations: 1,
    material_removal: 2,
    safety_concerns: 2,
    timeline_constraints: 2,
  },
  moderate: {
    access_difficulty: 5,
    roof_pitch: 4,
    penetrations: 5,
    material_removal: 4,
    safety_concerns: 5,
    timeline_constraints: 5,
  },
  complex: {
    access_difficulty: 8,
    roof_pitch: 6,
    penetrations: 8,
    material_removal: 6,
    safety_concerns: 8,
    timeline_constraints: 8,
  },
};

/**
 * Request body for POST /estimate/hybrid
 */
export interface HybridQuoteRequest {
  sqft: number;
  category: string;
  complexity_aggregate: number;
  access_difficulty: number;
  roof_pitch: number;
  penetrations: number;
  material_removal: number;
  safety_concerns: number;
  timeline_constraints: number;
  has_chimney: boolean;
  has_skylights: boolean;
  material_lines: number;
  labor_lines: number;
  has_subs: boolean;
  quoted_total?: number | null;
}

/**
 * Response from POST /estimate/hybrid
 */
export interface HybridQuoteResponse {
  work_items: WorkItem[];
  materials: MaterialLineItem[];
  total_labor_hours: number;
  total_materials_cost: number;
  total_price: number;
  overall_confidence: number;
  reasoning: string;
  pricing_tiers: PricingTier[];
  request_id: string | null;
  needs_review: boolean;
  cbr_cases_used: number;
  ml_confidence: "HIGH" | "MEDIUM" | "LOW";
  processing_time_ms: number;
}
```

**Step 2: Verify types compile**

Run: `cd /Users/aymanbaig/Desktop/Toiture-P1/frontend && npx tsc --noEmit src/types/hybrid-quote.ts`
Expected: No errors

**Step 3: Commit**

```bash
git add frontend/src/types/hybrid-quote.ts
git commit -m "feat(14A): add hybrid quote TypeScript types"
```

---

### Task 2: Add Hybrid Quote API Client

**Files:**
- Create: `frontend/src/lib/api/hybrid-quote.ts`

**Step 1: Create API client**

```typescript
// frontend/src/lib/api/hybrid-quote.ts

import type { HybridQuoteRequest, HybridQuoteResponse } from "@/types/hybrid-quote";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

/**
 * API error response structure
 */
interface ApiError {
  detail: string;
}

/**
 * Submit hybrid quote request to backend
 *
 * @param data - HybridQuoteRequest with all complexity factors
 * @returns HybridQuoteResponse with work items, materials, and pricing
 * @throws Error with detail message on failure
 */
export async function submitHybridQuote(
  data: HybridQuoteRequest
): Promise<HybridQuoteResponse> {
  const response = await fetch(`${API_URL}/estimate/hybrid`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    let errorMessage = "Failed to generate quote";
    try {
      const errorData: ApiError = await response.json();
      errorMessage = errorData.detail || errorMessage;
    } catch {
      errorMessage = response.statusText || errorMessage;
    }
    throw new Error(errorMessage);
  }

  return response.json();
}
```

**Step 2: Verify file compiles**

Run: `cd /Users/aymanbaig/Desktop/Toiture-P1/frontend && npx tsc --noEmit src/lib/api/hybrid-quote.ts`
Expected: No errors

**Step 3: Commit**

```bash
git add frontend/src/lib/api/hybrid-quote.ts
git commit -m "feat(14A): add hybrid quote API client"
```

---

### Task 3: Add French i18n Strings for Full Quote

**Files:**
- Modify: `frontend/src/lib/i18n/fr.ts`

**Step 1: Add new strings**

Add a new `fullQuote` section after `estimateur`:

```typescript
fullQuote: {
  // Form labels
  complexite: "Complexité du travail",
  simple: "Simple",
  modere: "Modéré",
  complexe: "Complexe",
  personnaliser: "Personnaliser les facteurs",

  // 6 factors
  accesDifficulte: "Difficulté d'accès",
  penteToit: "Pente du toit",
  penetrations: "Pénétrations",
  retraitMateriaux: "Retrait de matériaux",
  securite: "Préoccupations de sécurité",
  delai: "Contraintes de délai",

  // Features
  cheminee: "Cheminée",
  puitLumiere: "Puits de lumière",
  soustraitants: "Sous-traitants",

  // Output
  soumission: "SOUMISSION",
  travaux: "TRAVAUX",
  sommaire: "SOMMAIRE",
  materiaux: "Matériaux",
  mainOeuvre: "Main-d'œuvre",
  total: "TOTAL",
  heures: "hrs",

  // Confidence
  confiance: "Confiance",
  verificationRecommandee: "Vérification recommandée",

  // Actions
  exporterPdf: "Exporter PDF",
  envoyer: "Envoyer",
  sauvegarder: "Sauvegarder",

  // Reasoning
  raisonnement: "Raisonnement",

  // Loading/Error
  generation: "Génération de la soumission...",
  erreurGeneration: "Erreur lors de la génération",
},
```

**Step 2: Verify types**

Run: `cd /Users/aymanbaig/Desktop/Toiture-P1/frontend && npx tsc --noEmit`
Expected: No errors

**Step 3: Commit**

```bash
git add frontend/src/lib/i18n/fr.ts
git commit -m "feat(14A): add French i18n strings for full quote"
```

---

### Task 4: Create Complexity Presets Component

**Files:**
- Create: `frontend/src/components/estimateur/complexity-presets.tsx`

**Step 1: Create component**

```tsx
// frontend/src/components/estimateur/complexity-presets.tsx
"use client";

import { useState } from "react";
import { Label } from "@/components/ui/label";
import { Slider } from "@/components/ui/slider";
import { Button } from "@/components/ui/button";
import { ChevronDown, ChevronUp } from "lucide-react";
import { fr } from "@/lib/i18n/fr";
import { COMPLEXITY_PRESETS, type ComplexityPreset } from "@/types/hybrid-quote";

type PresetKey = "simple" | "moderate" | "complex";

interface ComplexityPresetsProps {
  value: ComplexityPreset;
  onChange: (value: ComplexityPreset) => void;
}

export function ComplexityPresets({ value, onChange }: ComplexityPresetsProps) {
  const [expanded, setExpanded] = useState(false);
  const [selectedPreset, setSelectedPreset] = useState<PresetKey>("moderate");

  const handlePresetChange = (preset: PresetKey) => {
    setSelectedPreset(preset);
    onChange(COMPLEXITY_PRESETS[preset]);
  };

  const handleFactorChange = (factor: keyof ComplexityPreset, newValue: number) => {
    onChange({ ...value, [factor]: newValue });
  };

  const presetLabels: Record<PresetKey, string> = {
    simple: fr.fullQuote.simple,
    moderate: fr.fullQuote.modere,
    complex: fr.fullQuote.complexe,
  };

  const factorConfig: Array<{
    key: keyof ComplexityPreset;
    label: string;
    max: number;
  }> = [
    { key: "access_difficulty", label: fr.fullQuote.accesDifficulte, max: 10 },
    { key: "roof_pitch", label: fr.fullQuote.penteToit, max: 8 },
    { key: "penetrations", label: fr.fullQuote.penetrations, max: 10 },
    { key: "material_removal", label: fr.fullQuote.retraitMateriaux, max: 8 },
    { key: "safety_concerns", label: fr.fullQuote.securite, max: 10 },
    { key: "timeline_constraints", label: fr.fullQuote.delai, max: 10 },
  ];

  return (
    <div className="space-y-4">
      <Label>{fr.fullQuote.complexite}</Label>

      {/* Preset buttons */}
      <div className="flex gap-2">
        {(["simple", "moderate", "complex"] as PresetKey[]).map((preset) => (
          <Button
            key={preset}
            type="button"
            variant={selectedPreset === preset ? "default" : "outline"}
            onClick={() => handlePresetChange(preset)}
            className="flex-1"
          >
            {presetLabels[preset]}
          </Button>
        ))}
      </div>

      {/* Expand/collapse button */}
      <Button
        type="button"
        variant="ghost"
        onClick={() => setExpanded(!expanded)}
        className="w-full justify-start text-muted-foreground"
      >
        {expanded ? <ChevronUp className="mr-2 h-4 w-4" /> : <ChevronDown className="mr-2 h-4 w-4" />}
        {fr.fullQuote.personnaliser}
      </Button>

      {/* Expanded factor sliders */}
      {expanded && (
        <div className="space-y-4 rounded-lg border p-4">
          {factorConfig.map(({ key, label, max }) => (
            <div key={key} className="space-y-2">
              <div className="flex justify-between">
                <Label className="text-sm">{label}</Label>
                <span className="text-sm text-muted-foreground">{value[key]}/{max}</span>
              </div>
              <Slider
                value={[value[key]]}
                onValueChange={([v]) => handleFactorChange(key, v)}
                max={max}
                step={1}
              />
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
```

**Step 2: Verify component compiles**

Run: `cd /Users/aymanbaig/Desktop/Toiture-P1/frontend && npx tsc --noEmit`
Expected: No errors

**Step 3: Commit**

```bash
git add frontend/src/components/estimateur/complexity-presets.tsx
git commit -m "feat(14A): add complexity presets component with 6-factor override"
```

---

### Task 5: Create Quote Result Display Component

**Files:**
- Create: `frontend/src/components/estimateur/quote-result.tsx`

**Step 1: Create component**

```tsx
// frontend/src/components/estimateur/quote-result.tsx
"use client";

import { useState } from "react";
import { AlertTriangle, ChevronDown, ChevronUp } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { fr } from "@/lib/i18n/fr";
import type { HybridQuoteResponse } from "@/types/hybrid-quote";

interface QuoteResultProps {
  quote: HybridQuoteResponse;
  category: string;
  sqft: number;
}

export function QuoteResult({ quote, category, sqft }: QuoteResultProps) {
  const [reasoningExpanded, setReasoningExpanded] = useState(false);

  // Get Standard tier (the one we show to clients)
  const standardTier = quote.pricing_tiers.find((t) => t.tier === "Standard");
  const displayPrice = standardTier?.total_price ?? quote.total_price;
  const materialsTotal = standardTier?.materials_cost ?? quote.total_materials_cost;
  const laborTotal = standardTier?.labor_cost ?? (displayPrice - materialsTotal);

  // Format currency
  const formatCurrency = (amount: number) =>
    new Intl.NumberFormat("fr-CA", {
      style: "currency",
      currency: "CAD",
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);

  // Format sqft
  const formatSqft = (sqft: number) =>
    new Intl.NumberFormat("fr-CA").format(sqft);

  const showWarning = quote.overall_confidence < 0.5;

  return (
    <Card className="mt-6">
      <CardContent className="pt-6">
        {/* Confidence warning */}
        {showWarning && (
          <div className="mb-4 flex items-start gap-3 rounded-lg bg-amber-50 border border-amber-200 p-4">
            <AlertTriangle className="h-5 w-5 text-amber-600 mt-0.5 flex-shrink-0" />
            <div>
              <p className="font-medium text-amber-800">
                {fr.fullQuote.confiance}: {Math.round(quote.overall_confidence * 100)}%
              </p>
              <p className="text-sm text-amber-700">
                {fr.fullQuote.verificationRecommandee}
              </p>
            </div>
          </div>
        )}

        {/* Invoice header */}
        <div className="text-center border-b-2 border-t-2 border-gray-800 py-2 mb-4">
          <h2 className="text-xl font-bold tracking-wide">{fr.fullQuote.soumission}</h2>
        </div>

        {/* Job info */}
        <div className="mb-4 text-sm">
          <p><strong>Catégorie:</strong> {category}</p>
          <p><strong>Superficie:</strong> {formatSqft(sqft)} pi²</p>
        </div>

        {/* Work items */}
        <div className="mb-4">
          <div className="border-b border-gray-300 pb-1 mb-2">
            <h3 className="font-semibold text-sm">{fr.fullQuote.travaux}</h3>
          </div>
          <ul className="space-y-1">
            {quote.work_items.map((item, idx) => (
              <li key={idx} className="flex justify-between text-sm">
                <span>• {item.name}</span>
                <span className="text-muted-foreground">{item.labor_hours.toFixed(1)} {fr.fullQuote.heures}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Summary */}
        <div className="mb-4">
          <div className="border-b border-gray-300 pb-1 mb-2">
            <h3 className="font-semibold text-sm">{fr.fullQuote.sommaire}</h3>
          </div>
          <div className="space-y-1 text-sm">
            <div className="flex justify-between">
              <span>{fr.fullQuote.materiaux}</span>
              <span>{formatCurrency(materialsTotal)}</span>
            </div>
            <div className="flex justify-between">
              <span>{fr.fullQuote.mainOeuvre} ({quote.total_labor_hours.toFixed(1)} {fr.fullQuote.heures})</span>
              <span>{formatCurrency(laborTotal)}</span>
            </div>
          </div>
        </div>

        {/* Total */}
        <div className="border-t-2 border-b-2 border-gray-800 py-2 mb-4">
          <div className="flex justify-between font-bold">
            <span>{fr.fullQuote.total}</span>
            <span>{formatCurrency(displayPrice)}</span>
          </div>
        </div>

        {/* Reasoning (collapsible) */}
        <div className="mb-4">
          <Button
            type="button"
            variant="ghost"
            onClick={() => setReasoningExpanded(!reasoningExpanded)}
            className="w-full justify-start text-muted-foreground"
          >
            {reasoningExpanded ? <ChevronUp className="mr-2 h-4 w-4" /> : <ChevronDown className="mr-2 h-4 w-4" />}
            💡 {fr.fullQuote.raisonnement}
          </Button>
          {reasoningExpanded && (
            <div className="mt-2 p-3 rounded-lg bg-muted text-sm">
              {quote.reasoning}
            </div>
          )}
        </div>

        {/* Action buttons placeholder */}
        <div className="flex gap-2 flex-wrap">
          <Button variant="outline" disabled>
            📄 {fr.fullQuote.exporterPdf}
          </Button>
          <Button variant="outline" disabled>
            📧 {fr.fullQuote.envoyer}
          </Button>
          <Button variant="outline" disabled>
            💾 {fr.fullQuote.sauvegarder}
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
```

**Step 2: Verify component compiles**

Run: `cd /Users/aymanbaig/Desktop/Toiture-P1/frontend && npx tsc --noEmit`
Expected: No errors

**Step 3: Commit**

```bash
git add frontend/src/components/estimateur/quote-result.tsx
git commit -m "feat(14A): add invoice-style quote result display component"
```

---

### Task 6: Update Full Quote Form Component

**Files:**
- Modify: `frontend/src/components/estimateur/full-quote-form.tsx`

**Step 1: Replace placeholder with working form**

Replace the entire file with:

```tsx
// frontend/src/components/estimateur/full-quote-form.tsx
"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
} from "@/components/ui/card";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Switch } from "@/components/ui/switch";
import { Button } from "@/components/ui/button";
import { Loader2 } from "lucide-react";
import { fr } from "@/lib/i18n/fr";
import { ComplexityPresets } from "./complexity-presets";
import { QuoteResult } from "./quote-result";
import { submitHybridQuote } from "@/lib/api/hybrid-quote";
import { COMPLEXITY_PRESETS, type ComplexityPreset, type HybridQuoteResponse } from "@/types/hybrid-quote";

// Allowed categories (must match backend)
const CATEGORIES = [
  "Bardeaux",
  "Elastomere",
  "EPDM",
  "TPO",
  "Tole",
  "Autre",
] as const;

// Form schema
const fullQuoteFormSchema = z.object({
  sqft: z.number().positive("Doit être positif").max(100000),
  category: z.enum(CATEGORIES),
  material_lines: z.number().int().min(0).max(100),
  labor_lines: z.number().int().min(0).max(50),
  has_subs: z.boolean(),
  has_chimney: z.boolean(),
  has_skylights: z.boolean(),
});

type FormData = z.infer<typeof fullQuoteFormSchema>;

export function FullQuoteForm() {
  const [complexity, setComplexity] = useState<ComplexityPreset>(COMPLEXITY_PRESETS.moderate);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<HybridQuoteResponse | null>(null);
  const [lastRequest, setLastRequest] = useState<{ category: string; sqft: number } | null>(null);

  const form = useForm<FormData>({
    resolver: zodResolver(fullQuoteFormSchema),
    defaultValues: {
      sqft: 1500,
      category: "Bardeaux",
      material_lines: 5,
      labor_lines: 2,
      has_subs: false,
      has_chimney: false,
      has_skylights: false,
    },
  });

  const onSubmit = async (data: FormData) => {
    setIsLoading(true);
    setError(null);
    setResult(null);

    // Calculate complexity aggregate
    const complexity_aggregate =
      complexity.access_difficulty +
      complexity.roof_pitch +
      complexity.penetrations +
      complexity.material_removal +
      complexity.safety_concerns +
      complexity.timeline_constraints;

    try {
      const response = await submitHybridQuote({
        sqft: data.sqft,
        category: data.category,
        complexity_aggregate,
        ...complexity,
        has_chimney: data.has_chimney,
        has_skylights: data.has_skylights,
        material_lines: data.material_lines,
        labor_lines: data.labor_lines,
        has_subs: data.has_subs,
      });

      setResult(response);
      setLastRequest({ category: data.category, sqft: data.sqft });
    } catch (err) {
      setError(err instanceof Error ? err.message : fr.fullQuote.erreurGeneration);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>{fr.estimateur.titreComplet}</CardTitle>
        <CardDescription>{fr.estimateur.descriptionComplet}</CardDescription>
      </CardHeader>
      <CardContent>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
            {/* Square footage */}
            <FormField
              control={form.control}
              name="sqft"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>{fr.estimateur.superficie}</FormLabel>
                  <FormControl>
                    <Input
                      type="number"
                      {...field}
                      onChange={(e) => field.onChange(parseFloat(e.target.value) || 0)}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            {/* Category */}
            <FormField
              control={form.control}
              name="category"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>{fr.estimateur.categorie}</FormLabel>
                  <Select onValueChange={field.onChange} defaultValue={field.value}>
                    <FormControl>
                      <SelectTrigger>
                        <SelectValue />
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

            {/* Complexity presets */}
            <ComplexityPresets value={complexity} onChange={setComplexity} />

            {/* Line counts */}
            <div className="grid grid-cols-2 gap-4">
              <FormField
                control={form.control}
                name="material_lines"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Lignes matériaux</FormLabel>
                    <FormControl>
                      <Input
                        type="number"
                        {...field}
                        onChange={(e) => field.onChange(parseInt(e.target.value) || 0)}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="labor_lines"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Lignes main-d'œuvre</FormLabel>
                    <FormControl>
                      <Input
                        type="number"
                        {...field}
                        onChange={(e) => field.onChange(parseInt(e.target.value) || 0)}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>

            {/* Feature toggles */}
            <div className="space-y-3">
              <FormField
                control={form.control}
                name="has_chimney"
                render={({ field }) => (
                  <FormItem className="flex items-center justify-between">
                    <FormLabel>{fr.fullQuote.cheminee}</FormLabel>
                    <FormControl>
                      <Switch checked={field.value} onCheckedChange={field.onChange} />
                    </FormControl>
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="has_skylights"
                render={({ field }) => (
                  <FormItem className="flex items-center justify-between">
                    <FormLabel>{fr.fullQuote.puitLumiere}</FormLabel>
                    <FormControl>
                      <Switch checked={field.value} onCheckedChange={field.onChange} />
                    </FormControl>
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="has_subs"
                render={({ field }) => (
                  <FormItem className="flex items-center justify-between">
                    <FormLabel>{fr.fullQuote.soustraitants}</FormLabel>
                    <FormControl>
                      <Switch checked={field.value} onCheckedChange={field.onChange} />
                    </FormControl>
                  </FormItem>
                )}
              />
            </div>

            {/* Submit button */}
            <Button type="submit" className="w-full" disabled={isLoading}>
              {isLoading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  {fr.fullQuote.generation}
                </>
              ) : (
                fr.estimateur.obtenirEstimation
              )}
            </Button>

            {/* Error display */}
            {error && (
              <div className="rounded-lg bg-destructive/10 border border-destructive/30 p-4 text-destructive text-sm">
                {error}
              </div>
            )}
          </form>
        </Form>

        {/* Result display */}
        {result && lastRequest && (
          <QuoteResult quote={result} category={lastRequest.category} sqft={lastRequest.sqft} />
        )}
      </CardContent>
    </Card>
  );
}
```

**Step 2: Verify component compiles**

Run: `cd /Users/aymanbaig/Desktop/Toiture-P1/frontend && npx tsc --noEmit`
Expected: No errors

**Step 3: Commit**

```bash
git add frontend/src/components/estimateur/full-quote-form.tsx
git commit -m "feat(14A): implement full quote form with complexity presets"
```

---

### Task 7: Verify Phase 14A End-to-End

**Files:** None (manual verification)

**Step 1: Start dev servers**

Run in separate terminals:
```bash
# Terminal 1: Backend
cd /Users/aymanbaig/Desktop/Toiture-P1/backend && python -m uvicorn app.main:app --reload --port 8000

# Terminal 2: Frontend
cd /Users/aymanbaig/Desktop/Toiture-P1/frontend && npm run dev
```

**Step 2: Verify functionality**

1. Navigate to http://localhost:3000/estimateur/complet
2. Fill in form with default values
3. Click "Obtenir l'estimation"
4. Verify:
   - Loading spinner appears
   - Quote result displays with work items
   - Materials total and labor total shown
   - Total price displayed
   - Reasoning collapsible works
   - Low confidence warning shows if confidence < 50%

**Step 3: Commit final verification**

```bash
git add -A
git commit -m "docs(14A): complete Phase 14A - core quote generation"
```

---

## Phase 14B: PDF Export

### Task 8: Install @react-pdf/renderer

**Files:**
- Modify: `frontend/package.json`

**Step 1: Install dependency**

Run: `cd /Users/aymanbaig/Desktop/Toiture-P1/frontend && npm install @react-pdf/renderer`

**Step 2: Verify installation**

Run: `cd /Users/aymanbaig/Desktop/Toiture-P1/frontend && npm ls @react-pdf/renderer`
Expected: Shows installed version

**Step 3: Commit**

```bash
git add frontend/package.json frontend/package-lock.json
git commit -m "chore(14B): install @react-pdf/renderer for PDF export"
```

---

### Task 9: Create PDF Quote Template

**Files:**
- Create: `frontend/src/lib/pdf/quote-template.tsx`

**Step 1: Create PDF template**

```tsx
// frontend/src/lib/pdf/quote-template.tsx
import {
  Document,
  Page,
  Text,
  View,
  StyleSheet,
} from "@react-pdf/renderer";
import type { HybridQuoteResponse } from "@/types/hybrid-quote";

// PDF styles
const styles = StyleSheet.create({
  page: {
    padding: 40,
    fontSize: 11,
    fontFamily: "Helvetica",
  },
  header: {
    marginBottom: 20,
    textAlign: "center",
  },
  companyName: {
    fontSize: 24,
    fontWeight: "bold",
    color: "#8B2323",
    marginBottom: 4,
  },
  subtitle: {
    fontSize: 10,
    color: "#666",
  },
  divider: {
    borderBottomWidth: 2,
    borderBottomColor: "#333",
    marginVertical: 10,
  },
  dividerLight: {
    borderBottomWidth: 1,
    borderBottomColor: "#ccc",
    marginVertical: 8,
  },
  sectionTitle: {
    fontSize: 12,
    fontWeight: "bold",
    marginBottom: 8,
    textTransform: "uppercase",
    letterSpacing: 1,
  },
  title: {
    fontSize: 16,
    fontWeight: "bold",
    textAlign: "center",
    marginVertical: 10,
    textTransform: "uppercase",
    letterSpacing: 2,
  },
  row: {
    flexDirection: "row",
    justifyContent: "space-between",
    marginBottom: 4,
  },
  label: {
    fontWeight: "bold",
  },
  workItem: {
    marginBottom: 4,
    paddingLeft: 10,
  },
  bullet: {
    marginRight: 6,
  },
  totalRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    fontWeight: "bold",
    fontSize: 14,
    paddingVertical: 8,
  },
  footer: {
    position: "absolute",
    bottom: 30,
    left: 40,
    right: 40,
    textAlign: "center",
    fontSize: 9,
    color: "#999",
  },
  jobInfo: {
    marginBottom: 15,
  },
});

interface QuotePDFProps {
  quote: HybridQuoteResponse;
  category: string;
  sqft: number;
}

export function QuotePDF({ quote, category, sqft }: QuotePDFProps) {
  // Get Standard tier
  const standardTier = quote.pricing_tiers.find((t) => t.tier === "Standard");
  const displayPrice = standardTier?.total_price ?? quote.total_price;
  const materialsTotal = standardTier?.materials_cost ?? quote.total_materials_cost;
  const laborTotal = standardTier?.labor_cost ?? (displayPrice - materialsTotal);

  // Format currency
  const formatCurrency = (amount: number) =>
    new Intl.NumberFormat("fr-CA", {
      style: "currency",
      currency: "CAD",
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);

  // Format number
  const formatNumber = (n: number) =>
    new Intl.NumberFormat("fr-CA").format(n);

  // Current date
  const today = new Date().toLocaleDateString("fr-CA");

  return (
    <Document>
      <Page size="LETTER" style={styles.page}>
        {/* Company header */}
        <View style={styles.header}>
          <Text style={styles.companyName}>Toiture LV</Text>
          <Text style={styles.subtitle}>Couvreur professionnel</Text>
        </View>

        <View style={styles.divider} />

        {/* Document title */}
        <Text style={styles.title}>Soumission</Text>

        <View style={styles.divider} />

        {/* Job info */}
        <View style={styles.jobInfo}>
          <View style={styles.row}>
            <Text style={styles.label}>Catégorie:</Text>
            <Text>{category}</Text>
          </View>
          <View style={styles.row}>
            <Text style={styles.label}>Superficie:</Text>
            <Text>{formatNumber(sqft)} pi²</Text>
          </View>
          <View style={styles.row}>
            <Text style={styles.label}>Date:</Text>
            <Text>{today}</Text>
          </View>
        </View>

        <View style={styles.dividerLight} />

        {/* Work items - NO HOURS for client view */}
        <View>
          <Text style={styles.sectionTitle}>Travaux</Text>
          {quote.work_items.map((item, idx) => (
            <View key={idx} style={styles.workItem}>
              <Text>
                <Text style={styles.bullet}>•</Text>
                {item.name}
              </Text>
            </View>
          ))}
        </View>

        <View style={styles.dividerLight} />

        {/* Summary */}
        <View>
          <Text style={styles.sectionTitle}>Sommaire</Text>
          <View style={styles.row}>
            <Text>Matériaux</Text>
            <Text>{formatCurrency(materialsTotal)}</Text>
          </View>
          <View style={styles.row}>
            <Text>Main-d'œuvre</Text>
            <Text>{formatCurrency(laborTotal)}</Text>
          </View>
        </View>

        <View style={styles.divider} />

        {/* Total */}
        <View style={styles.totalRow}>
          <Text>TOTAL</Text>
          <Text>{formatCurrency(displayPrice)}</Text>
        </View>

        <View style={styles.divider} />

        {/* Footer */}
        <Text style={styles.footer}>
          Toiture LV — Soumission générée par Cortex — {today}
        </Text>
      </Page>
    </Document>
  );
}
```

**Step 2: Verify component compiles**

Run: `cd /Users/aymanbaig/Desktop/Toiture-P1/frontend && npx tsc --noEmit`
Expected: No errors

**Step 3: Commit**

```bash
git add frontend/src/lib/pdf/quote-template.tsx
git commit -m "feat(14B): create PDF quote template for client export"
```

---

### Task 10: Create Quote Actions Component

**Files:**
- Create: `frontend/src/components/estimateur/quote-actions.tsx`

**Step 1: Create component with PDF export**

```tsx
// frontend/src/components/estimateur/quote-actions.tsx
"use client";

import { useState } from "react";
import { pdf } from "@react-pdf/renderer";
import { Button } from "@/components/ui/button";
import { Loader2 } from "lucide-react";
import { fr } from "@/lib/i18n/fr";
import { QuotePDF } from "@/lib/pdf/quote-template";
import type { HybridQuoteResponse } from "@/types/hybrid-quote";

interface QuoteActionsProps {
  quote: HybridQuoteResponse;
  category: string;
  sqft: number;
}

export function QuoteActions({ quote, category, sqft }: QuoteActionsProps) {
  const [isExporting, setIsExporting] = useState(false);

  const handleExportPDF = async () => {
    setIsExporting(true);
    try {
      const blob = await pdf(
        <QuotePDF quote={quote} category={category} sqft={sqft} />
      ).toBlob();

      // Generate filename
      const date = new Date().toISOString().split("T")[0];
      const filename = `Soumission-${category}-${date}.pdf`;

      // Trigger download
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error("PDF export error:", error);
    } finally {
      setIsExporting(false);
    }
  };

  return (
    <div className="flex gap-2 flex-wrap">
      <Button
        variant="outline"
        onClick={handleExportPDF}
        disabled={isExporting}
      >
        {isExporting ? (
          <Loader2 className="mr-2 h-4 w-4 animate-spin" />
        ) : (
          "📄 "
        )}
        {fr.fullQuote.exporterPdf}
      </Button>
      <Button variant="outline" disabled>
        📧 {fr.fullQuote.envoyer}
      </Button>
      <Button variant="outline" disabled>
        💾 {fr.fullQuote.sauvegarder}
      </Button>
    </div>
  );
}
```

**Step 2: Update quote-result.tsx to use QuoteActions**

Replace the action buttons placeholder in `quote-result.tsx`:

```tsx
// In quote-result.tsx imports, add:
import { QuoteActions } from "./quote-actions";

// Replace the disabled buttons div with:
<QuoteActions quote={quote} category={category} sqft={sqft} />
```

**Step 3: Verify components compile**

Run: `cd /Users/aymanbaig/Desktop/Toiture-P1/frontend && npx tsc --noEmit`
Expected: No errors

**Step 4: Commit**

```bash
git add frontend/src/components/estimateur/quote-actions.tsx
git add frontend/src/components/estimateur/quote-result.tsx
git commit -m "feat(14B): implement PDF export with client-facing template"
```

---

### Task 11: Verify Phase 14B End-to-End

**Files:** None (manual verification)

**Step 1: Test PDF export**

1. Navigate to http://localhost:3000/estimateur/complet
2. Generate a quote
3. Click "Exporter PDF"
4. Verify:
   - PDF downloads with correct filename (Soumission-{category}-{date}.pdf)
   - PDF shows work items WITHOUT labor hours
   - PDF shows materials total and labor total
   - PDF has Toiture LV branding
   - PDF is formatted professionally

**Step 2: Commit verification**

```bash
git add -A
git commit -m "docs(14B): complete Phase 14B - PDF export"
```

---

## Phase 14C: Save & Send (Future)

> **Note:** Phase 14C (Save to database + Email sending) requires backend endpoints that don't exist yet. This is documented but not implemented in this plan.

### Pending Tasks for 14C:
1. Create POST /quotes endpoint to save draft
2. Create POST /quotes/{id}/send endpoint for email
3. Create Supabase `quotes` table migration
4. Implement Save button functionality
5. Implement Send modal with email input
6. Show saved quotes in Historique tab

---

## Summary

**Phase 14A (Core Quote Generation):** 7 tasks
- Types, API client, i18n, complexity presets, quote result, form, verification

**Phase 14B (PDF Export):** 4 tasks
- Install library, PDF template, quote actions, verification

**Phase 14C (Save & Send):** Deferred - requires backend work

**Total Estimated Tasks:** 11 tasks for 14A + 14B

---

*Plan created: 2026-02-01*
