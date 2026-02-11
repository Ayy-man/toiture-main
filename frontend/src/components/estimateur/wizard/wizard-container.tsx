"use client";

import { useState, useMemo } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { motion, AnimatePresence } from "framer-motion";
import { Form } from "@/components/ui/form";
import { Button } from "@/components/ui/button";
import { ChevronLeft, ChevronRight, Check } from "lucide-react";
import { useLanguage } from "@/lib/i18n";
import {
  hybridQuoteFormSchema,
  type HybridQuoteFormData,
} from "@/lib/schemas/hybrid-quote";
import { submitHybridQuote } from "@/lib/api/hybrid-quote";
import type { HybridQuoteResponse, HybridQuoteRequest } from "@/types/hybrid-quote";
import { createSubmission } from "@/lib/api/submissions";
import type { Submission, LineItem as SubmissionLineItem } from "@/types/submission";
import { QuoteResult } from "../quote-result";
import { SubmissionEditor } from "../submission-editor";
import type { TierData, FactorConfig } from "../tier-selector";

// Import step components (will be created in Task 2)
import { StepBasics } from "./step-basics";
import { StepComplexity } from "./step-complexity";
import { StepCrew } from "./step-crew";
import { StepMaterials } from "./step-materials";
import { StepReview } from "./step-review";

/**
 * Build tier data from config (hardcoded for now, could be loaded from API later).
 * Moved from FullQuoteForm.
 */
function useTierData(): { tiers: TierData[]; factorConfig: FactorConfig } {
  const { t } = useLanguage();

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
 * WizardContainer: 5-step wizard for full quote form.
 * Orchestrates form state, step navigation, progress bar, and submission.
 */
export function WizardContainer() {
  const { t, locale } = useLanguage();
  const [currentStep, setCurrentStep] = useState(0);
  const [direction, setDirection] = useState(1); // 1 = forward, -1 = backward
  const [result, setResult] = useState<HybridQuoteResponse | null>(null);
  const [submission, setSubmission] = useState<Submission | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const { tiers, factorConfig } = useTierData();

  // Form setup with defaults (same as FullQuoteForm)
  const form = useForm<HybridQuoteFormData>({
    resolver: zodResolver(hybridQuoteFormSchema) as any,
    defaultValues: {
      sqft: 1500,
      category: "Bardeaux",
      complexity_tier: 2,
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

  // Calculate total factor hours for display (mirrors backend calculation)
  const calculatedFactorHours = useMemo(() => {
    const factors = {
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

  const sqft = form.watch("sqft");
  const category = form.watch("category");

  // Per-step validation fields
  const stepValidationFields: Record<number, string[]> = {
    0: ["sqft", "category", "material_lines", "labor_lines"],
    1: ["complexity_tier"],
    2: [],
    3: [],
    4: [],
  };

  const totalSteps = 5;

  const handleNext = async () => {
    // Validate current step fields
    const fieldsToValidate = stepValidationFields[currentStep];
    if (fieldsToValidate && fieldsToValidate.length > 0) {
      const isValid = await form.trigger(fieldsToValidate as any);
      if (!isValid) return;
    }

    if (currentStep < totalSteps - 1) {
      setDirection(1);
      setCurrentStep(currentStep + 1);
    }
  };

  const handleBack = () => {
    if (currentStep > 0) {
      setDirection(-1);
      setCurrentStep(currentStep - 1);
    }
  };

  const jumpToStep = (step: number) => {
    if (step < currentStep && step >= 0) {
      setDirection(-1);
      setCurrentStep(step);
    }
  };

  /**
   * Handle form submission (moved from FullQuoteForm).
   */
  async function onSubmit(data: HybridQuoteFormData) {
    setIsLoading(true);
    setError(null);
    setResult(null);

    try {
      // Build request payload with tier-based fields
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

  const handleCreateSubmission = async () => {
    if (!result) return;

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
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create submission");
    }
  };

  // If result is set, show result/submission instead of wizard
  if (result || submission) {
    return (
      <div className="flex flex-col lg:flex-row lg:gap-8 lg:items-start">
        <div className="flex-1 max-w-2xl">
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
                onClick={handleCreateSubmission}
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
          ) : null}
        </div>
      </div>
    );
  }

  const stepLabels = [
    t.wizard.step1,
    t.wizard.step2,
    t.wizard.step3,
    t.wizard.step4,
    t.wizard.step5,
  ];

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
        {/* Progress Bar */}
        <div className="mb-8">
          {/* Desktop: Full step labels */}
          <div className="hidden sm:flex items-center justify-between">
            {stepLabels.map((label, index) => {
              const isCompleted = index < currentStep;
              const isCurrent = index === currentStep;
              const isFuture = index > currentStep;

              return (
                <div key={index} className="flex items-center flex-1">
                  <div className="flex flex-col items-center flex-1">
                    <button
                      type="button"
                      onClick={() => jumpToStep(index)}
                      disabled={index > currentStep}
                      className={`
                        flex size-10 items-center justify-center rounded-full text-sm font-semibold transition-all
                        ${isCompleted ? 'bg-primary text-primary-foreground cursor-pointer hover:opacity-80' : ''}
                        ${isCurrent ? 'bg-primary text-primary-foreground ring-4 ring-primary/20' : ''}
                        ${isFuture ? 'bg-muted text-muted-foreground cursor-not-allowed' : ''}
                      `}
                    >
                      {isCompleted ? <Check className="size-5" /> : index + 1}
                    </button>
                    <span className={`
                      mt-2 text-xs font-medium
                      ${isCompleted ? 'text-primary' : ''}
                      ${isCurrent ? 'font-semibold text-foreground' : ''}
                      ${isFuture ? 'text-muted-foreground' : ''}
                    `}>
                      {label}
                    </span>
                  </div>
                  {index < stepLabels.length - 1 && (
                    <div className={`
                      h-0.5 flex-1 mx-2
                      ${index < currentStep ? 'bg-primary' : 'bg-muted'}
                    `} />
                  )}
                </div>
              );
            })}
          </div>

          {/* Mobile: Current step only */}
          <div className="flex sm:hidden items-center justify-center">
            <div className="text-sm font-medium text-muted-foreground">
              {t.wizard.stepOf
                .replace("{current}", String(currentStep + 1))
                .replace("{total}", String(totalSteps))}
            </div>
            <div className="mx-4 h-0.5 flex-1 bg-muted">
              <div
                className="h-full bg-primary transition-all"
                style={{ width: `${((currentStep + 1) / totalSteps) * 100}%` }}
              />
            </div>
            <div className="text-sm font-semibold">
              {stepLabels[currentStep]}
            </div>
          </div>
        </div>

        {/* Step Content with Animation */}
        <div className="relative min-h-[400px]">
          <AnimatePresence mode="wait" initial={false}>
            <motion.div
              key={currentStep}
              initial={{ x: direction > 0 ? 300 : -300, opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              exit={{ x: direction > 0 ? -300 : 300, opacity: 0 }}
              transition={{ type: "spring", stiffness: 300, damping: 30 }}
            >
              {currentStep === 0 && <StepBasics />}
              {currentStep === 1 && (
                <StepComplexity
                  tiers={tiers}
                  factorConfig={factorConfig}
                  calculatedFactorHours={calculatedFactorHours}
                />
              )}
              {currentStep === 2 && <StepCrew />}
              {currentStep === 3 && <StepMaterials />}
              {currentStep === 4 && (
                <StepReview
                  tiers={tiers}
                  factorConfig={factorConfig}
                  isLoading={isLoading}
                />
              )}
            </motion.div>
          </AnimatePresence>
        </div>

        {/* Error Display */}
        {error && (
          <div className="flex items-center gap-2 rounded-lg border border-destructive/50 bg-destructive/10 p-4 text-destructive">
            <p className="text-sm font-medium">{error}</p>
          </div>
        )}

        {/* Navigation Buttons */}
        <div className="flex items-center justify-between gap-4 pt-4 border-t sticky bottom-0 bg-background py-4 sm:static sm:bg-transparent">
          <Button
            type="button"
            variant="outline"
            onClick={handleBack}
            disabled={currentStep === 0}
            className="flex-1 sm:flex-initial"
          >
            <ChevronLeft className="size-4 mr-2" />
            {t.wizard.back}
          </Button>

          {currentStep < totalSteps - 1 ? (
            <Button
              type="button"
              onClick={handleNext}
              className="flex-1 sm:flex-initial"
            >
              {t.wizard.next}
              <ChevronRight className="size-4 ml-2" />
            </Button>
          ) : (
            <Button
              type="submit"
              disabled={isLoading}
              className="flex-1 sm:flex-initial"
            >
              {isLoading ? t.fullQuote.enChargement : t.wizard.generateQuote}
            </Button>
          )}
        </div>
      </form>
    </Form>
  );
}
