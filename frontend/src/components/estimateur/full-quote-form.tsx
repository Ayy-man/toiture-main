"use client";

import { useState, useMemo } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
  FormDescription,
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
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
} from "@/components/ui/card";
import { TierSelector, type TierData } from "./tier-selector";
import { FactorChecklist, type FactorValues, type FactorConfig } from "./factor-checklist";
import { QuoteResult } from "./quote-result";
import {
  hybridQuoteFormSchema,
  type HybridQuoteFormData,
} from "@/lib/schemas/hybrid-quote";
import { submitHybridQuote } from "@/lib/api/hybrid-quote";
import type { HybridQuoteResponse, HybridQuoteRequest } from "@/types/hybrid-quote";
import { CATEGORIES } from "@/lib/schemas";
import { useLanguage } from "@/lib/i18n";
import { Loader2, Calculator, Layers, Wrench, AlertCircle } from "lucide-react";

/**
 * Build tier data from config (hardcoded for now, could be loaded from API later).
 */
function useTierData(): { tiers: TierData[]; factorConfig: FactorConfig } {
  const { locale } = useLanguage();

  // Tier data matching complexity_tiers_config.json
  const tiers: TierData[] = [
    {
      tier: 1,
      name: locale === 'fr' ? "Simple / Standard" : "Simple / Standard",
      description: locale === 'fr'
        ? "Maison plain-pied, toit plat a faible pente (0-4/12), acces facile par entree, pas de grue, 1-2 sections, materiaux standards"
        : "Single-story house, flat to low pitch (0-4/12), easy driveway access, no crane, 1-2 sections, standard materials",
      scoreRange: "0-16",
      hoursAdded: 0,
    },
    {
      tier: 2,
      name: locale === 'fr' ? "Modere" : "Moderate",
      description: locale === 'fr'
        ? "Maison 2 etages, pente 4/12 a 6/12, bon acces rue, quelques penetrations, 2-3 sections, arrachage standard"
        : "Two-story house, 4/12 to 6/12 pitch, good street access, some penetrations, 2-3 sections, standard tear-off",
      scoreRange: "17-33",
      hoursAdded: 4,
    },
    {
      tier: 3,
      name: locale === 'fr' ? "Complexe" : "Complex",
      description: locale === 'fr'
        ? "2 etages avec forte pente (6/12-8/12), acces limite, penetrations multiples, 3-4 sections, arrachage multi-couches"
        : "Two-story with steep pitch (6/12-8/12), limited access, multiple penetrations, 3-4 sections, multi-layer tear-off",
      scoreRange: "34-50",
      hoursAdded: 8,
    },
    {
      tier: 4,
      name: locale === 'fr' ? "Haute complexite" : "High Complexity",
      description: locale === 'fr'
        ? "3 etages ou pente 8/12+, acces difficile (grue recommandee), penetrations nombreuses, 4+ sections, equipement securite requis"
        : "Three-story or 8/12+ pitch, difficult access (crane recommended), many penetrations, 4+ sections, safety equipment required",
      scoreRange: "51-66",
      hoursAdded: 16,
    },
    {
      tier: 5,
      name: locale === 'fr' ? "Tres haute complexite" : "Very High Complexity",
      description: locale === 'fr'
        ? "3 etages, pente 10/12+, grue requise, acces extreme (centre-ville), penetrations etendues, 5+ sections, couches multiples"
        : "Three-story, 10/12+ pitch, crane required, extreme access (downtown), extensive penetrations, 5+ sections, multiple layers",
      scoreRange: "67-83",
      hoursAdded: 24,
    },
    {
      tier: 6,
      name: locale === 'fr' ? "Extreme" : "Extreme",
      description: locale === 'fr'
        ? "Commercial/haute elevation, pente extreme, grue obligatoire, acces dangereux (echafaudage + harnais), travaux structuraux, conditions hivernales"
        : "Commercial/high-rise, extreme pitch, crane mandatory, hazardous access (scaffolding + harness), structural work, winter conditions",
      scoreRange: "84-100",
      hoursAdded: 40,
    },
  ];

  // Factor config matching complexity_tiers_config.json, localized
  const factorConfig: FactorConfig = {
    roof_pitch: {
      options: [
        { key: "flat", hours: 0, label: locale === 'fr' ? "Plat (0-2/12)" : "Flat (0-2/12)" },
        { key: "low", hours: 1, label: locale === 'fr' ? "Faible (3/12-4/12)" : "Low (3/12-4/12)" },
        { key: "medium", hours: 2, label: locale === 'fr' ? "Moyen (5/12-6/12)" : "Medium (5/12-6/12)" },
        { key: "steep", hours: 4, label: locale === 'fr' ? "Forte (7/12-8/12)" : "Steep (7/12-8/12)" },
        { key: "very_steep", hours: 8, label: locale === 'fr' ? "Tres forte (9/12+)" : "Very Steep (9/12+)" },
      ],
    },
    access_difficulty: {
      options: [
        { key: "no_crane", hours: 6, label: locale === 'fr' ? "Pas d'acces pour grue" : "No crane access" },
        { key: "narrow_driveway", hours: 2, label: locale === 'fr' ? "Entree etroite" : "Narrow driveway" },
        { key: "street_blocking", hours: 3, label: locale === 'fr' ? "Blocage de rue requis" : "Street blocking required" },
        { key: "high_elevation", hours: 4, label: locale === 'fr' ? "Haute elevation (3+ etages)" : "High elevation (3+ stories)" },
        { key: "difficult_terrain", hours: 2, label: locale === 'fr' ? "Terrain difficile" : "Difficult terrain" },
        { key: "no_material_drop", hours: 3, label: locale === 'fr' ? "Pas de zone de depot" : "No material drop zone" },
      ],
    },
    demolition: {
      options: [
        { key: "none", hours: 0, label: locale === 'fr' ? "Aucun" : "None" },
        { key: "single_layer", hours: 2, label: locale === 'fr' ? "Une couche" : "Single layer" },
        { key: "multi_layer", hours: 6, label: locale === 'fr' ? "Multi-couches" : "Multi-layer" },
        { key: "structural", hours: 10, label: locale === 'fr' ? "Structural" : "Structural" },
      ],
    },
    penetrations: {
      hours_per_item: 0.5,
      label: locale === 'fr'
        ? "Nombre de penetrations (events, tuyaux, puits de lumiere)"
        : "Number of penetrations (vents, pipes, skylights)",
    },
    security: {
      options: [
        { key: "harness", hours: 1, label: locale === 'fr' ? "Harnais de securite" : "Safety harness" },
        { key: "scaffolding", hours: 4, label: locale === 'fr' ? "Echafaudage" : "Scaffolding" },
        { key: "guardrails", hours: 2, label: locale === 'fr' ? "Garde-corps" : "Guardrails" },
        { key: "winter_safety", hours: 3, label: locale === 'fr' ? "Securite hivernale" : "Winter safety" },
      ],
    },
    material_removal: {
      options: [
        { key: "none", hours: 0, label: locale === 'fr' ? "Aucun" : "None" },
        { key: "standard", hours: 2, label: locale === 'fr' ? "Standard" : "Standard" },
        { key: "heavy", hours: 4, label: locale === 'fr' ? "Lourd" : "Heavy" },
        { key: "hazardous", hours: 6, label: locale === 'fr' ? "Dangereux (amiante)" : "Hazardous (asbestos)" },
      ],
    },
    roof_sections: {
      hours_per_item_above: 1,
      baseline: 2,
      label: locale === 'fr' ? "Nombre de sections de toit" : "Number of roof sections",
    },
    previous_layers: {
      hours_per_item_above: 2,
      baseline: 1,
      label: locale === 'fr' ? "Nombre de couches precedentes" : "Number of previous layers",
    },
  };

  return { tiers, factorConfig };
}

/**
 * Full quote form with tier selector and factor checklist.
 * Submits to /estimate/hybrid endpoint with tier-based complexity.
 */
export function FullQuoteForm() {
  const { t } = useLanguage();
  const [result, setResult] = useState<HybridQuoteResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const { tiers, factorConfig } = useTierData();

  // Form setup with Tier 2 (Moderate) defaults
  const form = useForm<HybridQuoteFormData>({
    resolver: zodResolver(hybridQuoteFormSchema),
    defaultValues: {
      sqft: 1500,
      category: "Bardeaux",
      complexity_tier: 2,  // Default to Moderate
      factor_roof_pitch: null,
      factor_access_difficulty: [],
      factor_demolition: null,
      factor_penetrations_count: 0,
      factor_security: [],
      factor_material_removal: null,
      factor_roof_sections_count: 2,
      factor_previous_layers_count: 0,
      manual_extra_hours: 0,
      material_lines: 5,
      labor_lines: 2,
      has_chimney: false,
      has_skylights: false,
      has_subs: false,
      created_by: undefined,
    },
  });

  // Watch sqft and category for QuoteResult props
  const sqft = form.watch("sqft");
  const category = form.watch("category");

  // Calculate total factor hours for display (mirrors backend calculation)
  const calculatedFactorHours = useMemo(() => {
    const factors: FactorValues = {
      roof_pitch: form.watch("factor_roof_pitch"),
      access_difficulty: form.watch("factor_access_difficulty"),
      demolition: form.watch("factor_demolition"),
      penetrations_count: form.watch("factor_penetrations_count"),
      security: form.watch("factor_security"),
      material_removal: form.watch("factor_material_removal"),
      roof_sections_count: form.watch("factor_roof_sections_count"),
      previous_layers_count: form.watch("factor_previous_layers_count"),
    };

    let total = 0;

    // Roof pitch
    if (factors.roof_pitch) {
      const option = factorConfig.roof_pitch.options.find(o => o.key === factors.roof_pitch);
      total += option?.hours || 0;
    }

    // Access difficulty (checklist)
    factors.access_difficulty.forEach(key => {
      const option = factorConfig.access_difficulty.options.find(o => o.key === key);
      total += option?.hours || 0;
    });

    // Demolition
    if (factors.demolition) {
      const option = factorConfig.demolition.options.find(o => o.key === factors.demolition);
      total += option?.hours || 0;
    }

    // Penetrations
    total += factors.penetrations_count * factorConfig.penetrations.hours_per_item;

    // Security (checklist)
    factors.security.forEach(key => {
      const option = factorConfig.security.options.find(o => o.key === key);
      total += option?.hours || 0;
    });

    // Material removal
    if (factors.material_removal) {
      const option = factorConfig.material_removal.options.find(o => o.key === factors.material_removal);
      total += option?.hours || 0;
    }

    // Roof sections (above baseline)
    const sectionsAbove = Math.max(0, factors.roof_sections_count - factorConfig.roof_sections.baseline);
    total += sectionsAbove * factorConfig.roof_sections.hours_per_item_above;

    // Previous layers (above baseline)
    const layersAbove = Math.max(0, factors.previous_layers_count - factorConfig.previous_layers.baseline);
    total += layersAbove * factorConfig.previous_layers.hours_per_item_above;

    return total;
  }, [
    form.watch("factor_roof_pitch"),
    form.watch("factor_access_difficulty"),
    form.watch("factor_demolition"),
    form.watch("factor_penetrations_count"),
    form.watch("factor_security"),
    form.watch("factor_material_removal"),
    form.watch("factor_roof_sections_count"),
    form.watch("factor_previous_layers_count"),
    factorConfig,
  ]);

  /**
   * Handle form submission.
   * Builds request with tier + factor fields and submits to hybrid quote endpoint.
   */
  async function onSubmit(data: HybridQuoteFormData) {
    setIsLoading(true);
    setError(null);
    setResult(null);

    try {
      // Build request payload with new tier-based fields
      const request: HybridQuoteRequest = {
        sqft: data.sqft,
        category: data.category,
        complexity_tier: data.complexity_tier,
        factor_roof_pitch: data.factor_roof_pitch || undefined,
        factor_access_difficulty: data.factor_access_difficulty.length > 0 ? data.factor_access_difficulty : undefined,
        factor_demolition: data.factor_demolition || undefined,
        factor_penetrations_count: data.factor_penetrations_count || undefined,
        factor_security: data.factor_security.length > 0 ? data.factor_security : undefined,
        factor_material_removal: data.factor_material_removal || undefined,
        factor_roof_sections_count: data.factor_roof_sections_count > 2 ? data.factor_roof_sections_count : undefined,
        factor_previous_layers_count: data.factor_previous_layers_count > 0 ? data.factor_previous_layers_count : undefined,
        manual_extra_hours: data.manual_extra_hours > 0 ? data.manual_extra_hours : undefined,
        has_chimney: data.has_chimney,
        has_skylights: data.has_skylights,
        material_lines: data.material_lines,
        labor_lines: data.labor_lines,
        has_subs: data.has_subs,
        quoted_total: data.quoted_total,
      };

      // Submit to API
      const response = await submitHybridQuote(request);
      setResult(response);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : t.fullQuote.erreur
      );
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="flex flex-col lg:flex-row lg:gap-8 lg:items-start">
      {/* Left Column - Form */}
      <div className="flex-1 max-w-2xl space-y-6">
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
          {/* Project Details Section */}
          <Card className="card-hover">
            <CardHeader className="pb-4">
              <div className="flex items-center gap-2">
                <div className="flex size-8 items-center justify-center rounded-lg bg-primary/10 text-primary">
                  <Calculator className="size-4" />
                </div>
                <div>
                  <CardTitle className="text-lg">{t.fullQuote.titre}</CardTitle>
                  <CardDescription className="text-sm">{t.fullQuote.description}</CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Estimator Dropdown */}
              <FormField
                control={form.control}
                name="created_by"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel className="text-sm font-medium">{t.estimateur.estimateurNom}</FormLabel>
                    <Select
                      onValueChange={field.onChange}
                      value={field.value}
                    >
                      <FormControl>
                        <SelectTrigger className="h-11">
                          <SelectValue placeholder={t.estimateur.selectEstimateur} />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        <SelectItem value="Steven">Steven</SelectItem>
                        <SelectItem value="Laurent">Laurent</SelectItem>
                        <SelectItem value="Autre">{t.estimateur.autre}</SelectItem>
                      </SelectContent>
                    </Select>
                    <FormMessage />
                  </FormItem>
                )}
              />

              {/* Primary inputs - side by side on larger screens */}
              <div className="grid gap-4 sm:grid-cols-2">
                {/* Square Footage */}
                <FormField
                  control={form.control}
                  name="sqft"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel className="text-sm font-medium">{t.estimateur.superficie}</FormLabel>
                      <FormControl>
                        <Input
                          type="number"
                          placeholder="1500"
                          className="h-11"
                          {...field}
                          onChange={(e) =>
                            field.onChange(e.target.valueAsNumber || "")
                          }
                        />
                      </FormControl>
                      <FormDescription className="text-xs text-muted-foreground">
                        {t.fullQuote.superficieDescription}
                      </FormDescription>
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
                      <FormLabel className="text-sm font-medium">{t.estimateur.categorie}</FormLabel>
                      <Select
                        onValueChange={field.onChange}
                        defaultValue={field.value}
                      >
                        <FormControl>
                          <SelectTrigger className="h-11">
                            <SelectValue placeholder={t.fullQuote.categoriePlaceholder} />
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
                      <FormDescription className="text-xs text-muted-foreground">
                        {t.fullQuote.categorieDescription}
                      </FormDescription>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </div>

              {/* Secondary inputs - material and labor lines */}
              <div className="grid gap-4 sm:grid-cols-2">
                {/* Material Lines */}
                <FormField
                  control={form.control}
                  name="material_lines"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel className="text-sm font-medium">{t.fullQuote.lignesMateriaux}</FormLabel>
                      <FormControl>
                        <Input
                          type="number"
                          placeholder="5"
                          className="h-11"
                          {...field}
                          onChange={(e) =>
                            field.onChange(e.target.valueAsNumber || "")
                          }
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                {/* Labor Lines */}
                <FormField
                  control={form.control}
                  name="labor_lines"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel className="text-sm font-medium">{t.fullQuote.lignesMainOeuvre}</FormLabel>
                      <FormControl>
                        <Input
                          type="number"
                          placeholder="2"
                          className="h-11"
                          {...field}
                          onChange={(e) =>
                            field.onChange(e.target.valueAsNumber || "")
                          }
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </div>
            </CardContent>
          </Card>

          {/* Complexity Section */}
          <Card className="card-hover">
            <CardHeader className="pb-4">
              <div className="flex items-center gap-2">
                <div className="flex size-8 items-center justify-center rounded-lg bg-primary/10 text-primary">
                  <Layers className="size-4" />
                </div>
                <div>
                  <CardTitle className="text-lg">{t.fullQuote.complexiteProjet}</CardTitle>
                  <CardDescription className="text-sm">
                    {t.fullQuote.complexiteDescription}
                  </CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Tier Selector */}
              <TierSelector
                value={form.watch("complexity_tier")}
                onChange={(tier) => form.setValue("complexity_tier", tier)}
                tiers={tiers}
              />

              {/* Factor Checklist */}
              <FactorChecklist
                value={{
                  roof_pitch: form.watch("factor_roof_pitch"),
                  access_difficulty: form.watch("factor_access_difficulty"),
                  demolition: form.watch("factor_demolition"),
                  penetrations_count: form.watch("factor_penetrations_count"),
                  security: form.watch("factor_security"),
                  material_removal: form.watch("factor_material_removal"),
                  roof_sections_count: form.watch("factor_roof_sections_count"),
                  previous_layers_count: form.watch("factor_previous_layers_count"),
                }}
                onChange={(factors) => {
                  form.setValue("factor_roof_pitch", factors.roof_pitch);
                  form.setValue("factor_access_difficulty", factors.access_difficulty);
                  form.setValue("factor_demolition", factors.demolition);
                  form.setValue("factor_penetrations_count", factors.penetrations_count);
                  form.setValue("factor_security", factors.security);
                  form.setValue("factor_material_removal", factors.material_removal);
                  form.setValue("factor_roof_sections_count", factors.roof_sections_count);
                  form.setValue("factor_previous_layers_count", factors.previous_layers_count);
                }}
                config={factorConfig}
                totalHours={calculatedFactorHours}
              />

              {/* Manual extra hours input */}
              <FormField
                control={form.control}
                name="manual_extra_hours"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel className="text-sm font-medium">{t.fullQuote.manualExtraHours}</FormLabel>
                    <FormControl>
                      <Input type="number" min={0} step={0.5} className="h-11" {...field}
                        onChange={(e) => field.onChange(e.target.valueAsNumber || 0)} />
                    </FormControl>
                    <FormDescription className="text-xs text-muted-foreground">
                      {t.fullQuote.manualExtraHoursDesc}
                    </FormDescription>
                  </FormItem>
                )}
              />
            </CardContent>
          </Card>

          {/* Features Section */}
          <Card className="card-hover">
            <CardHeader className="pb-4">
              <div className="flex items-center gap-2">
                <div className="flex size-8 items-center justify-center rounded-lg bg-primary/10 text-primary">
                  <Wrench className="size-4" />
                </div>
                <div>
                  <CardTitle className="text-lg">{t.fullQuote.caracteristiques}</CardTitle>
                  <CardDescription className="text-sm">
                    {t.fullQuote.caracteristiquesDescription}
                  </CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-3">
              {/* Has Chimney */}
              <FormField
                control={form.control}
                name="has_chimney"
                render={({ field }) => (
                  <FormItem className="flex items-center justify-between rounded-lg border border-border/50 bg-muted/30 p-4 transition-colors hover:bg-muted/50">
                    <div className="space-y-0.5">
                      <FormLabel className="text-sm font-medium cursor-pointer">
                        {t.fullQuote.aCheminee}
                      </FormLabel>
                      <FormDescription className="text-xs text-muted-foreground">
                        {t.fullQuote.chemineeDescription}
                      </FormDescription>
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

              {/* Has Skylights */}
              <FormField
                control={form.control}
                name="has_skylights"
                render={({ field }) => (
                  <FormItem className="flex items-center justify-between rounded-lg border border-border/50 bg-muted/30 p-4 transition-colors hover:bg-muted/50">
                    <div className="space-y-0.5">
                      <FormLabel className="text-sm font-medium cursor-pointer">
                        {t.fullQuote.aLucarnes}
                      </FormLabel>
                      <FormDescription className="text-xs text-muted-foreground">
                        {t.fullQuote.lucarnesDescription}
                      </FormDescription>
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

              {/* Has Subcontractors */}
              <FormField
                control={form.control}
                name="has_subs"
                render={({ field }) => (
                  <FormItem className="flex items-center justify-between rounded-lg border border-border/50 bg-muted/30 p-4 transition-colors hover:bg-muted/50">
                    <div className="space-y-0.5">
                      <FormLabel className="text-sm font-medium cursor-pointer">
                        {t.fullQuote.aSousTraitants}
                      </FormLabel>
                      <FormDescription className="text-xs text-muted-foreground">
                        {t.fullQuote.sousTraitantsDescription}
                      </FormDescription>
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
            </CardContent>
          </Card>

          {/* Error Display */}
          {error && (
            <div className="flex items-center gap-2 rounded-lg border border-destructive/50 bg-destructive/10 p-4 text-destructive">
              <AlertCircle className="size-5 shrink-0" />
              <p className="text-sm font-medium">{error}</p>
            </div>
          )}

          {/* Submit Button */}
          <Button
            type="submit"
            size="lg"
            className="w-full h-12 text-base font-semibold"
            disabled={isLoading}
          >
            {isLoading ? (
              <>
                <Loader2 className="mr-2 size-5 animate-spin" />
                {t.fullQuote.enChargement}
              </>
            ) : (
              <>
                <Calculator className="mr-2 size-5" />
                {t.fullQuote.generer}
              </>
            )}
          </Button>
        </form>
      </Form>
      </div>

      {/* Right Column - Result (sticky on desktop) */}
      <div className="lg:w-[420px] lg:sticky lg:top-4 mt-6 lg:mt-0">
        {result ? (
          <QuoteResult
            quote={result}
            category={category}
            sqft={sqft}
            inputParams={form.getValues()}
          />
        ) : (
          <div className="hidden lg:flex flex-col items-center justify-center rounded-xl border border-dashed border-border/50 bg-muted/20 p-8 text-center min-h-[400px]">
            <Calculator className="size-12 text-muted-foreground/40 mb-4" />
            <p className="text-muted-foreground text-sm">
              {t.fullQuote.resultPlaceholder || "Your quote will appear here"}
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
