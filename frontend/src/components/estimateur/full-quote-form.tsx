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
import {
  Accordion,
  AccordionItem,
  AccordionTrigger,
  AccordionContent,
} from "@/components/ui/accordion";
import { TierSelector, type TierData } from "./tier-selector";
import { FactorChecklist, type FactorValues, type FactorConfig } from "./factor-checklist";
import { QuoteResult } from "./quote-result";
import { SubmissionEditor } from "./submission-editor";
import {
  hybridQuoteFormSchema,
  type HybridQuoteFormData,
} from "@/lib/schemas/hybrid-quote";
import { submitHybridQuote } from "@/lib/api/hybrid-quote";
import type { HybridQuoteResponse, HybridQuoteRequest } from "@/types/hybrid-quote";
import { createSubmission } from "@/lib/api/submissions";
import type { Submission, LineItem as SubmissionLineItem } from "@/types/submission";
import { CATEGORIES } from "@/lib/schemas";
import { useLanguage } from "@/lib/i18n";
import { useToast } from "@/hooks/use-toast";
import { Loader2, Calculator, Layers, Wrench, AlertCircle, Users, MapPin, Package } from "lucide-react";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Checkbox } from "@/components/ui/checkbox";

/**
 * Build tier data from config (hardcoded for now, could be loaded from API later).
 */
function useTierData(): { tiers: TierData[]; factorConfig: FactorConfig } {
  const { locale, t } = useLanguage();

  // Tier data matching complexity_tiers_config.json
  const tiers: TierData[] = [
    {
      tier: 1,
      name: t.complexity.tiers.tier1.name,
      description: t.complexity.tiers.tier1.description,
      scoreRange: "0-16",
      hoursAdded: 0,
    },
    {
      tier: 2,
      name: t.complexity.tiers.tier2.name,
      description: t.complexity.tiers.tier2.description,
      scoreRange: "17-33",
      hoursAdded: 4,
    },
    {
      tier: 3,
      name: t.complexity.tiers.tier3.name,
      description: t.complexity.tiers.tier3.description,
      scoreRange: "34-50",
      hoursAdded: 8,
    },
    {
      tier: 4,
      name: t.complexity.tiers.tier4.name,
      description: t.complexity.tiers.tier4.description,
      scoreRange: "51-66",
      hoursAdded: 16,
    },
    {
      tier: 5,
      name: t.complexity.tiers.tier5.name,
      description: t.complexity.tiers.tier5.description,
      scoreRange: "67-83",
      hoursAdded: 24,
    },
    {
      tier: 6,
      name: t.complexity.tiers.tier6.name,
      description: t.complexity.tiers.tier6.description,
      scoreRange: "84-100",
      hoursAdded: 40,
    },
  ];

  // Factor config matching complexity_tiers_config.json, localized
  const factorConfig: FactorConfig = {
    roof_pitch: {
      options: [
        { key: "flat", hours: 0, label: t.complexity.factors.roofPitch.flat },
        { key: "low", hours: 1, label: t.complexity.factors.roofPitch.low },
        { key: "medium", hours: 2, label: t.complexity.factors.roofPitch.medium },
        { key: "steep", hours: 4, label: t.complexity.factors.roofPitch.steep },
        { key: "very_steep", hours: 8, label: t.complexity.factors.roofPitch.verySteep },
      ],
    },
    access_difficulty: {
      options: [
        { key: "no_crane", hours: 6, label: t.complexity.factors.accessDifficulty.noCrane },
        { key: "narrow_driveway", hours: 2, label: t.complexity.factors.accessDifficulty.narrowDriveway },
        { key: "street_blocking", hours: 3, label: t.complexity.factors.accessDifficulty.streetBlocking },
        { key: "high_elevation", hours: 4, label: t.complexity.factors.accessDifficulty.highElevation },
        { key: "difficult_terrain", hours: 2, label: t.complexity.factors.accessDifficulty.difficultTerrain },
        { key: "no_material_drop", hours: 3, label: t.complexity.factors.accessDifficulty.noMaterialDrop },
      ],
    },
    demolition: {
      options: [
        { key: "none", hours: 0, label: t.complexity.factors.demolition.none },
        { key: "single_layer", hours: 2, label: t.complexity.factors.demolition.singleLayer },
        { key: "multi_layer", hours: 6, label: t.complexity.factors.demolition.multiLayer },
        { key: "structural", hours: 10, label: t.complexity.factors.demolition.structural },
      ],
    },
    penetrations: {
      hours_per_item: 0.5,
      label: t.complexity.factors.penetrations.label,
    },
    security: {
      options: [
        { key: "harness", hours: 1, label: t.complexity.factors.security.harness },
        { key: "scaffolding", hours: 4, label: t.complexity.factors.security.scaffolding },
        { key: "guardrails", hours: 2, label: t.complexity.factors.security.guardrails },
        { key: "winter_safety", hours: 3, label: t.complexity.factors.security.winterSafety },
      ],
    },
    material_removal: {
      options: [
        { key: "none", hours: 0, label: t.complexity.factors.materialRemoval.none },
        { key: "standard", hours: 2, label: t.complexity.factors.materialRemoval.standard },
        { key: "heavy", hours: 4, label: t.complexity.factors.materialRemoval.heavy },
        { key: "hazardous", hours: 6, label: t.complexity.factors.materialRemoval.hazardous },
      ],
    },
    roof_sections: {
      hours_per_item_above: 1,
      baseline: 2,
      label: t.complexity.factors.roofSections.label,
    },
    previous_layers: {
      hours_per_item_above: 2,
      baseline: 1,
      label: t.complexity.factors.previousLayers.label,
    },
  };

  return { tiers, factorConfig };
}

/**
 * Full quote form with tier selector and factor checklist.
 * Submits to /estimate/hybrid endpoint with tier-based complexity.
 */
export function FullQuoteForm() {
  const { t, locale } = useLanguage();
  const { toast } = useToast();
  const [result, setResult] = useState<HybridQuoteResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [submission, setSubmission] = useState<Submission | null>(null);

  const { tiers, factorConfig } = useTierData();

  // Equipment items from equipment_config.json (hardcoded to avoid async load)
  const equipmentOptions = [
    { id: "crane", label: t.complexity.equipment.crane, dailyCost: 25 },
    { id: "scaffolding", label: t.complexity.equipment.scaffolding, dailyCost: 25 },
    { id: "dumpster", label: t.complexity.equipment.dumpster, dailyCost: 25 },
    { id: "generator", label: t.complexity.equipment.generator, dailyCost: 25 },
    { id: "compressor", label: t.complexity.equipment.compressor, dailyCost: 25 },
  ];

  // Form setup with Tier 2 (Moderate) defaults
  const form = useForm<HybridQuoteFormData>({
    resolver: zodResolver(hybridQuoteFormSchema) as any,
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
      employee_compagnons: 0,
      employee_apprentis: 0,
      employee_manoeuvres: 0,
      duration_type: 'full_day' as const,
      duration_days: undefined,
      geographic_zone: undefined,
      premium_client_level: 'standard' as const,
      equipment_items: [] as string[],
      supply_chain_risk: 'standard' as const,
    },
  });

  // Watch sqft and category for QuoteResult props
  const sqft = form.watch("sqft");
  const category = form.watch("category");

  // Watch values for crew total and conditional rendering
  const compagnons = form.watch("employee_compagnons") || 0;
  const apprentis = form.watch("employee_apprentis") || 0;
  const manoeuvres = form.watch("employee_manoeuvres") || 0;
  const totalCrew = compagnons + apprentis + manoeuvres;
  const durationType = form.watch("duration_type");
  const supplyRisk = form.watch("supply_chain_risk");

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
        // Phase 22 new fields
        employee_compagnons: data.employee_compagnons > 0 ? data.employee_compagnons : undefined,
        employee_apprentis: data.employee_apprentis > 0 ? data.employee_apprentis : undefined,
        employee_manoeuvres: data.employee_manoeuvres > 0 ? data.employee_manoeuvres : undefined,
        duration_type: data.duration_type,
        duration_days: data.duration_type === 'multi_day' ? data.duration_days : undefined,
        geographic_zone: data.geographic_zone || undefined,
        premium_client_level: data.premium_client_level !== 'standard' ? data.premium_client_level : undefined,
        equipment_items: data.equipment_items.length > 0 ? data.equipment_items : undefined,
        supply_chain_risk: data.supply_chain_risk !== 'standard' ? data.supply_chain_risk : undefined,
      };

      // Submit to API
      const response = await submitHybridQuote(request);
      setResult(response);
      toast({
        title: t.fullQuote.titre,
        description: `${t.fullQuote.total}: ${new Intl.NumberFormat("fr-CA", { style: "currency", currency: "CAD" }).format(response.total_price)}`,
      });
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : t.fullQuote.erreur;
      setError(errorMessage);
      toast({
        title: t.fullQuote.erreur,
        description: errorMessage,
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="flex flex-col lg:flex-row lg:gap-8 lg:items-start">
      {/* Left Column - Form */}
      <div className="flex-1 max-w-2xl space-y-4">
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
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

          {/* Collapsible Sections — Accordion inside a single Card */}
          <Card>
            <Accordion type="multiple" defaultValue={["complexity"]}>
              {/* ── Complexity ── */}
              <AccordionItem value="complexity" className="px-6">
                <AccordionTrigger className="hover:no-underline">
                  <div className="flex items-center gap-3">
                    <div className="flex size-7 items-center justify-center rounded-lg bg-primary/10 text-primary">
                      <Layers className="size-3.5" />
                    </div>
                    <div className="text-left">
                      <div className="text-sm font-semibold leading-tight">{t.fullQuote.complexiteProjet}</div>
                      <div className="text-xs text-muted-foreground">
                        {tiers.find(tier => tier.tier === form.watch("complexity_tier"))?.name || "—"}
                        {calculatedFactorHours > 0 && ` · +${calculatedFactorHours}h`}
                      </div>
                    </div>
                  </div>
                </AccordionTrigger>
                <AccordionContent className="space-y-4">
                  <TierSelector
                    value={form.watch("complexity_tier")}
                    onChange={(tier) => form.setValue("complexity_tier", tier)}
                    tiers={tiers}
                  />
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
                </AccordionContent>
              </AccordionItem>

              {/* ── Crew & Duration ── */}
              <AccordionItem value="crew" className="px-6">
                <AccordionTrigger className="hover:no-underline">
                  <div className="flex items-center gap-3">
                    <div className="flex size-7 items-center justify-center rounded-lg bg-primary/10 text-primary">
                      <Users className="size-3.5" />
                    </div>
                    <div className="text-left">
                      <div className="text-sm font-semibold leading-tight">{t.fullQuote.crewDuration}</div>
                      <div className="text-xs text-muted-foreground">
                        {totalCrew > 0 ? `${totalCrew} ${t.fullQuote.workers}` : "—"}
                        {durationType && ` · ${durationType === 'half_day' ? t.fullQuote.halfDay : durationType === 'full_day' ? t.fullQuote.fullDay : t.fullQuote.multiDay}`}
                      </div>
                    </div>
                  </div>
                </AccordionTrigger>
                <AccordionContent className="space-y-6">
                  <div>
                    <label className="text-sm font-medium mb-3 block">{t.fullQuote.totalCrew}</label>
                    <div className="grid grid-cols-3 gap-3">
                      <FormField
                        control={form.control}
                        name="employee_compagnons"
                        render={({ field }) => (
                          <FormItem>
                            <FormLabel className="text-xs font-medium">{t.fullQuote.compagnons}</FormLabel>
                            <FormControl>
                              <Input type="number" min={0} max={20} className="h-11" {...field}
                                onChange={(e) => field.onChange(parseInt(e.target.value) || 0)} />
                            </FormControl>
                          </FormItem>
                        )}
                      />
                      <FormField
                        control={form.control}
                        name="employee_apprentis"
                        render={({ field }) => (
                          <FormItem>
                            <FormLabel className="text-xs font-medium">{t.fullQuote.apprentis}</FormLabel>
                            <FormControl>
                              <Input type="number" min={0} max={20} className="h-11" {...field}
                                onChange={(e) => field.onChange(parseInt(e.target.value) || 0)} />
                            </FormControl>
                          </FormItem>
                        )}
                      />
                      <FormField
                        control={form.control}
                        name="employee_manoeuvres"
                        render={({ field }) => (
                          <FormItem>
                            <FormLabel className="text-xs font-medium">{t.fullQuote.manoeuvres}</FormLabel>
                            <FormControl>
                              <Input type="number" min={0} max={20} className="h-11" {...field}
                                onChange={(e) => field.onChange(parseInt(e.target.value) || 0)} />
                            </FormControl>
                          </FormItem>
                        )}
                      />
                    </div>
                    <div className="flex justify-between items-center pt-3 mt-3 border-t border-border/50">
                      <span className="text-sm font-medium">{t.fullQuote.totalCrew}</span>
                      <span className="text-sm font-semibold text-primary">
                        {totalCrew} {t.fullQuote.workers}
                      </span>
                    </div>
                  </div>

                  <FormField
                    control={form.control}
                    name="duration_type"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel className="text-sm font-medium">{t.fullQuote.projectDuration}</FormLabel>
                        <FormControl>
                          <RadioGroup onValueChange={field.onChange} value={field.value} className="space-y-2">
                            <div className="flex items-center space-x-2">
                              <RadioGroupItem value="half_day" id="half_day" />
                              <label htmlFor="half_day" className="text-sm cursor-pointer">{t.fullQuote.halfDay}</label>
                            </div>
                            <div className="flex items-center space-x-2">
                              <RadioGroupItem value="full_day" id="full_day" />
                              <label htmlFor="full_day" className="text-sm cursor-pointer">{t.fullQuote.fullDay}</label>
                            </div>
                            <div className="flex items-center space-x-2">
                              <RadioGroupItem value="multi_day" id="multi_day" />
                              <label htmlFor="multi_day" className="text-sm cursor-pointer">{t.fullQuote.multiDay}</label>
                            </div>
                          </RadioGroup>
                        </FormControl>
                      </FormItem>
                    )}
                  />

                  {durationType === 'multi_day' && (
                    <FormField
                      control={form.control}
                      name="duration_days"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel className="text-sm font-medium">{t.fullQuote.numberOfDays}</FormLabel>
                          <FormControl>
                            <Input type="number" min={2} max={30} placeholder="3" className="h-11 max-w-32" {...field}
                              value={field.value ?? ''} onChange={(e) => field.onChange(e.target.valueAsNumber || undefined)} />
                          </FormControl>
                        </FormItem>
                      )}
                    />
                  )}
                </AccordionContent>
              </AccordionItem>

              {/* ── Location & Client ── */}
              <AccordionItem value="location" className="px-6">
                <AccordionTrigger className="hover:no-underline">
                  <div className="flex items-center gap-3">
                    <div className="flex size-7 items-center justify-center rounded-lg bg-primary/10 text-primary">
                      <MapPin className="size-3.5" />
                    </div>
                    <div className="text-left">
                      <div className="text-sm font-semibold leading-tight">{t.fullQuote.locationClient}</div>
                      <div className="text-xs text-muted-foreground">
                        {form.watch("geographic_zone") ? t.fullQuote[`zone${form.watch("geographic_zone")?.charAt(0).toUpperCase()}${form.watch("geographic_zone")?.slice(1)}` as keyof typeof t.fullQuote] || form.watch("geographic_zone") : "—"}
                        {form.watch("premium_client_level") && form.watch("premium_client_level") !== 'standard' && ` · ${form.watch("premium_client_level")}`}
                      </div>
                    </div>
                  </div>
                </AccordionTrigger>
                <AccordionContent className="space-y-6">
                  <FormField
                    control={form.control}
                    name="geographic_zone"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel className="text-sm font-medium">{t.fullQuote.geographicZone}</FormLabel>
                        <Select onValueChange={field.onChange} value={field.value}>
                          <FormControl>
                            <SelectTrigger className="h-11">
                              <SelectValue placeholder={t.fullQuote.selectZone} />
                            </SelectTrigger>
                          </FormControl>
                          <SelectContent>
                            <SelectItem value="core">{t.fullQuote.zoneCore}</SelectItem>
                            <SelectItem value="secondary">{t.fullQuote.zoneSecondary}</SelectItem>
                            <SelectItem value="north_premium">{t.fullQuote.zoneNorthPremium}</SelectItem>
                            <SelectItem value="extended">{t.fullQuote.zoneExtended}</SelectItem>
                            <SelectItem value="red_flag">{t.fullQuote.zoneRedFlag}</SelectItem>
                          </SelectContent>
                        </Select>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  <FormField
                    control={form.control}
                    name="premium_client_level"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel className="text-sm font-medium">{t.fullQuote.premiumClientLevel}</FormLabel>
                        <Select onValueChange={field.onChange} value={field.value}>
                          <FormControl>
                            <SelectTrigger className="h-11">
                              <SelectValue />
                            </SelectTrigger>
                          </FormControl>
                          <SelectContent>
                            <SelectItem value="standard">
                              {t.fullQuote.premiumStandard} — {t.fullQuote.premiumStandardDesc}
                            </SelectItem>
                            <SelectItem value="premium_1">
                              {t.fullQuote.premium1} — {t.fullQuote.premium1Desc} ({t.fullQuote.surchargeTBD})
                            </SelectItem>
                            <SelectItem value="premium_2">
                              {t.fullQuote.premium2} — {t.fullQuote.premium2Desc} ({t.fullQuote.surchargeTBD})
                            </SelectItem>
                            <SelectItem value="premium_3">
                              {t.fullQuote.premium3} — {t.fullQuote.premium3Desc} ({t.fullQuote.surchargeTBD})
                            </SelectItem>
                          </SelectContent>
                        </Select>
                        <FormDescription className="text-xs text-muted-foreground">
                          {t.fullQuote.placeholderPricing}
                        </FormDescription>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                </AccordionContent>
              </AccordionItem>

              {/* ── Equipment & Supply Chain ── */}
              <AccordionItem value="equipment" className="px-6">
                <AccordionTrigger className="hover:no-underline">
                  <div className="flex items-center gap-3">
                    <div className="flex size-7 items-center justify-center rounded-lg bg-primary/10 text-primary">
                      <Package className="size-3.5" />
                    </div>
                    <div className="text-left">
                      <div className="text-sm font-semibold leading-tight">{t.fullQuote.equipmentSupplyChain}</div>
                      <div className="text-xs text-muted-foreground">
                        {(form.watch("equipment_items")?.length || 0) > 0
                          ? `${form.watch("equipment_items")?.length} selected`
                          : "—"}
                      </div>
                    </div>
                  </div>
                </AccordionTrigger>
                <AccordionContent className="space-y-6">
                  <div>
                    <label className="text-sm font-medium mb-3 block">{t.fullQuote.toolsEquipment}</label>
                    <div className="space-y-2">
                      {equipmentOptions.map((item) => {
                        const currentItems = form.watch("equipment_items") || [];
                        const isChecked = currentItems.includes(item.id);
                        return (
                          <div
                            key={item.id}
                            className="flex items-center justify-between rounded-lg border border-border/50 bg-muted/30 px-4 py-3 transition-colors hover:bg-muted/50"
                          >
                            <div className="flex items-center gap-3">
                              <Checkbox
                                id={`equipment-${item.id}`}
                                checked={isChecked}
                                onCheckedChange={(checked) => {
                                  const current = form.getValues("equipment_items") || [];
                                  if (checked) {
                                    form.setValue("equipment_items", [...current, item.id]);
                                  } else {
                                    form.setValue("equipment_items", current.filter((x: string) => x !== item.id));
                                  }
                                }}
                              />
                              <label htmlFor={`equipment-${item.id}`} className="text-sm cursor-pointer">
                                {item.label}
                              </label>
                            </div>
                            <span className="text-xs font-medium text-primary">
                              ${item.dailyCost}{t.fullQuote.dailyCost}
                            </span>
                          </div>
                        );
                      })}
                    </div>
                    <p className="text-xs text-muted-foreground mt-2">
                      {t.fullQuote.placeholderPricing}
                    </p>
                  </div>

                  <FormField
                    control={form.control}
                    name="supply_chain_risk"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel className="text-sm font-medium">{t.fullQuote.supplyChainRisk}</FormLabel>
                        <FormControl>
                          <RadioGroup onValueChange={field.onChange} value={field.value} className="space-y-2">
                            <div className="flex items-center space-x-2">
                              <RadioGroupItem value="standard" id="supply_standard" />
                              <label htmlFor="supply_standard" className="text-sm cursor-pointer">
                                {t.fullQuote.supplyStandard} ({t.fullQuote.supplyStandardDesc})
                              </label>
                            </div>
                            <div className="flex items-center space-x-2">
                              <RadioGroupItem value="extended" id="supply_extended" />
                              <label htmlFor="supply_extended" className="text-sm cursor-pointer">
                                {t.fullQuote.supplyExtended} ({t.fullQuote.supplyExtendedDesc})
                              </label>
                            </div>
                            <div className="flex items-center space-x-2">
                              <RadioGroupItem value="import" id="supply_import" />
                              <label htmlFor="supply_import" className="text-sm cursor-pointer">
                                {t.fullQuote.supplyImport} ({t.fullQuote.supplyImportDesc})
                              </label>
                            </div>
                          </RadioGroup>
                        </FormControl>
                      </FormItem>
                    )}
                  />

                  {(supplyRisk === 'extended' || supplyRisk === 'import') && (
                    <div className="flex items-center gap-2 rounded-lg border border-yellow-500/50 bg-yellow-500/10 p-3">
                      <AlertCircle className="size-5 shrink-0 text-yellow-600" />
                      <p className="text-sm text-yellow-700 dark:text-yellow-400">
                        {t.fullQuote.supplyWarning}
                      </p>
                    </div>
                  )}
                </AccordionContent>
              </AccordionItem>

              {/* ── Features ── */}
              <AccordionItem value="features" className="border-b-0 px-6">
                <AccordionTrigger className="hover:no-underline">
                  <div className="flex items-center gap-3">
                    <div className="flex size-7 items-center justify-center rounded-lg bg-primary/10 text-primary">
                      <Wrench className="size-3.5" />
                    </div>
                    <div className="text-left">
                      <div className="text-sm font-semibold leading-tight">{t.fullQuote.caracteristiques}</div>
                      <div className="text-xs text-muted-foreground">
                        {[form.watch("has_chimney"), form.watch("has_skylights"), form.watch("has_subs")].filter(Boolean).length}/3 active
                      </div>
                    </div>
                  </div>
                </AccordionTrigger>
                <AccordionContent className="space-y-3">
                  <FormField
                    control={form.control}
                    name="has_chimney"
                    render={({ field }) => (
                      <FormItem className="flex items-center justify-between rounded-lg border border-border/50 bg-muted/30 p-4 transition-colors hover:bg-muted/50">
                        <div className="space-y-0.5">
                          <FormLabel className="text-sm font-medium cursor-pointer">{t.fullQuote.aCheminee}</FormLabel>
                          <FormDescription className="text-xs text-muted-foreground">{t.fullQuote.chemineeDescription}</FormDescription>
                        </div>
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
                      <FormItem className="flex items-center justify-between rounded-lg border border-border/50 bg-muted/30 p-4 transition-colors hover:bg-muted/50">
                        <div className="space-y-0.5">
                          <FormLabel className="text-sm font-medium cursor-pointer">{t.fullQuote.aLucarnes}</FormLabel>
                          <FormDescription className="text-xs text-muted-foreground">{t.fullQuote.lucarnesDescription}</FormDescription>
                        </div>
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
                      <FormItem className="flex items-center justify-between rounded-lg border border-border/50 bg-muted/30 p-4 transition-colors hover:bg-muted/50">
                        <div className="space-y-0.5">
                          <FormLabel className="text-sm font-medium cursor-pointer">{t.fullQuote.aSousTraitants}</FormLabel>
                          <FormDescription className="text-xs text-muted-foreground">{t.fullQuote.sousTraitantsDescription}</FormDescription>
                        </div>
                        <FormControl>
                          <Switch checked={field.value} onCheckedChange={field.onChange} />
                        </FormControl>
                      </FormItem>
                    )}
                  />
                </AccordionContent>
              </AccordionItem>
            </Accordion>
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
        {result && !submission ? (
          <>
            <QuoteResult
              quote={result}
              category={category}
              sqft={sqft || 0}
              inputParams={form.getValues()}
            />
            <Button
              className="w-full mt-4"
              onClick={async () => {
                // Convert HybridQuoteResponse to submission line items
                const standardTier = result.pricing_tiers.find(t => t.tier === "Standard");
                const hourlyRate = result.total_labor_hours > 0
                  ? (standardTier?.labor_cost || 0) / result.total_labor_hours
                  : 0;

                const lineItems: Omit<SubmissionLineItem, 'id'>[] = [
                  ...result.work_items.map((wi, i) => ({
                    type: 'labor' as const,
                    name: wi.name,
                    quantity: wi.labor_hours,
                    unit_price: Math.round(hourlyRate * 100) / 100,
                    total: Math.round(wi.labor_hours * hourlyRate * 100) / 100,
                    order: i,
                  })),
                  ...result.materials.map((mat, i) => ({
                    type: 'material' as const,
                    material_id: mat.material_id,
                    name: `Material #${mat.material_id}`,
                    quantity: mat.quantity,
                    unit_price: mat.unit_price,
                    total: mat.total,
                    order: result.work_items.length + i,
                  })),
                ];

                try {
                  const sub = await createSubmission({
                    category,
                    sqft,
                    created_by: form.getValues("created_by") || "estimateur",
                    line_items: lineItems,
                    pricing_tiers: result.pricing_tiers,
                    selected_tier: "Standard",
                  });
                  setSubmission(sub);
                  toast({
                    title: t.submission.submissionCreated,
                    description: t.submission.statusDraft,
                  });
                } catch (err) {
                  const errorMessage = err instanceof Error ? err.message : "Failed to create submission";
                  setError(errorMessage);
                  toast({
                    title: t.common.erreur,
                    description: errorMessage,
                    variant: "destructive",
                  });
                }
              }}
            >
              {t.submission.createSubmission}
            </Button>
          </>
        ) : submission ? (
          <SubmissionEditor
            initialData={submission}
            onUpdate={(updated) => setSubmission(updated)}
            userRole="estimator"
            userName={form.getValues("created_by") || "estimateur"}
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
