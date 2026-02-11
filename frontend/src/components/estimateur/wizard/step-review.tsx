"use client";

import { useFormContext } from "react-hook-form";
import {
  Card,
  CardHeader,
  CardTitle,
  CardContent,
} from "@/components/ui/card";
import { FileText, Info } from "lucide-react";
import { useLanguage } from "@/lib/i18n";
import type { HybridQuoteFormData } from "@/lib/schemas/hybrid-quote";
import type { TierData } from "../tier-selector";
import type { FactorConfig } from "../factor-checklist";

interface StepReviewProps {
  tiers: TierData[];
  factorConfig: FactorConfig;
  isLoading: boolean;
}

/**
 * Step 5: Review - Read-only summary of all inputs
 */
export function StepReview({ tiers, factorConfig, isLoading }: StepReviewProps) {
  const { t } = useLanguage();
  const form = useFormContext<HybridQuoteFormData>();

  const values = form.getValues();

  // Find selected tier
  const selectedTier = tiers.find(tier => tier.tier === values.complexity_tier);

  // Calculate factor hours for display
  const getFactorHours = () => {
    let total = 0;

    // Roof pitch
    if (values.factor_roof_pitch) {
      const option = factorConfig.roof_pitch.options.find(o => o.key === values.factor_roof_pitch);
      total += option?.hours || 0;
    }

    // Access difficulty (checklist)
    values.factor_access_difficulty.forEach(key => {
      const option = factorConfig.access_difficulty.options.find(o => o.key === key);
      total += option?.hours || 0;
    });

    // Demolition
    if (values.factor_demolition) {
      const option = factorConfig.demolition.options.find(o => o.key === values.factor_demolition);
      total += option?.hours || 0;
    }

    // Penetrations
    total += values.factor_penetrations_count * factorConfig.penetrations.hours_per_item;

    // Security (checklist)
    values.factor_security.forEach(key => {
      const option = factorConfig.security.options.find(o => o.key === key);
      total += option?.hours || 0;
    });

    // Material removal
    if (values.factor_material_removal) {
      const option = factorConfig.material_removal.options.find(o => o.key === values.factor_material_removal);
      total += option?.hours || 0;
    }

    // Roof sections (above baseline)
    const sectionsAbove = Math.max(0, values.factor_roof_sections_count - factorConfig.roof_sections.baseline);
    total += sectionsAbove * factorConfig.roof_sections.hours_per_item_above;

    // Previous layers (above baseline)
    const layersAbove = Math.max(0, values.factor_previous_layers_count - factorConfig.previous_layers.baseline);
    total += layersAbove * factorConfig.previous_layers.hours_per_item_above;

    return total;
  };

  const factorHours = getFactorHours();

  // Get factor labels
  const getFactorLabel = (type: string, key: string) => {
    const config = factorConfig[type as keyof typeof factorConfig];
    if ('options' in config) {
      const option = config.options.find((o: { key: string; hours: number; label: string }) => o.key === key);
      return option?.label || key;
    }
    return key;
  };

  const totalCrew = (values.employee_compagnons || 0) + (values.employee_apprentis || 0) + (values.employee_manoeuvres || 0);

  return (
    <Card>
      <CardHeader className="pb-4">
        <div className="flex items-center gap-2">
          <div className="flex size-8 items-center justify-center rounded-lg bg-primary/10 text-primary">
            <FileText className="size-4" />
          </div>
          <div>
            <CardTitle className="text-lg">{t.wizard.step5}</CardTitle>
          </div>
        </div>
        <div className="flex items-start gap-2 mt-3 p-3 rounded-lg bg-blue-50 dark:bg-blue-950/30 border border-blue-200 dark:border-blue-900">
          <Info className="size-5 shrink-0 text-blue-600 dark:text-blue-400 mt-0.5" />
          <p className="text-sm text-blue-700 dark:text-blue-300">
            {t.wizard.reviewInstructions}
          </p>
        </div>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Project Section */}
        <div className="space-y-3">
          <h3 className="text-sm font-semibold text-foreground border-b pb-2">{t.wizard.step1}</h3>
          <dl className="grid grid-cols-2 gap-x-4 gap-y-3 text-sm">
            {values.created_by && (
              <>
                <dt className="text-muted-foreground">{t.estimateur.estimateurNom}</dt>
                <dd className="font-medium">{values.created_by}</dd>
              </>
            )}
            <dt className="text-muted-foreground">{t.estimateur.categorie}</dt>
            <dd className="font-medium">{values.category}</dd>
            <dt className="text-muted-foreground">{t.estimateur.superficie}</dt>
            <dd className="font-medium">{values.sqft} pi²</dd>
            <dt className="text-muted-foreground">{t.fullQuote.lignesMateriaux}</dt>
            <dd className="font-medium">{values.material_lines}</dd>
            <dt className="text-muted-foreground">{t.fullQuote.lignesMainOeuvre}</dt>
            <dd className="font-medium">{values.labor_lines}</dd>
            <dt className="text-muted-foreground">{t.fullQuote.caracteristiques}</dt>
            <dd className="font-medium">
              {[
                values.has_chimney && t.fullQuote.aCheminee,
                values.has_skylights && t.fullQuote.aLucarnes,
                values.has_subs && t.fullQuote.aSousTraitants
              ].filter(Boolean).join(', ') || '—'}
            </dd>
          </dl>
        </div>

        {/* Complexity Section */}
        <div className="space-y-3">
          <h3 className="text-sm font-semibold text-foreground border-b pb-2">{t.wizard.step2}</h3>
          <dl className="grid grid-cols-2 gap-x-4 gap-y-3 text-sm">
            <dt className="text-muted-foreground">{t.fullQuote.tierSelector}</dt>
            <dd className="font-medium">{selectedTier?.name || '—'}</dd>
            {values.factor_roof_pitch && (
              <>
                <dt className="text-muted-foreground">{t.fullQuote.factorRoofPitch}</dt>
                <dd className="font-medium">{getFactorLabel('roof_pitch', values.factor_roof_pitch)}</dd>
              </>
            )}
            {values.factor_access_difficulty.length > 0 && (
              <>
                <dt className="text-muted-foreground">{t.fullQuote.factorAccessDifficulty}</dt>
                <dd className="font-medium">{values.factor_access_difficulty.map(k => getFactorLabel('access_difficulty', k)).join(', ')}</dd>
              </>
            )}
            {values.factor_demolition && (
              <>
                <dt className="text-muted-foreground">{t.fullQuote.factorDemolition}</dt>
                <dd className="font-medium">{getFactorLabel('demolition', values.factor_demolition)}</dd>
              </>
            )}
            {values.factor_penetrations_count > 0 && (
              <>
                <dt className="text-muted-foreground">{t.fullQuote.factorPenetrations}</dt>
                <dd className="font-medium">{values.factor_penetrations_count}</dd>
              </>
            )}
            {values.factor_security.length > 0 && (
              <>
                <dt className="text-muted-foreground">{t.fullQuote.factorSecurity}</dt>
                <dd className="font-medium">{values.factor_security.map(k => getFactorLabel('security', k)).join(', ')}</dd>
              </>
            )}
            {values.factor_material_removal && (
              <>
                <dt className="text-muted-foreground">{t.fullQuote.factorMaterialRemoval}</dt>
                <dd className="font-medium">{getFactorLabel('material_removal', values.factor_material_removal)}</dd>
              </>
            )}
            {values.factor_roof_sections_count > 2 && (
              <>
                <dt className="text-muted-foreground">{t.fullQuote.factorRoofSections}</dt>
                <dd className="font-medium">{values.factor_roof_sections_count}</dd>
              </>
            )}
            {values.factor_previous_layers_count > 0 && (
              <>
                <dt className="text-muted-foreground">{t.fullQuote.factorPreviousLayers}</dt>
                <dd className="font-medium">{values.factor_previous_layers_count}</dd>
              </>
            )}
            <dt className="text-muted-foreground">{t.fullQuote.factorHoursLabel}</dt>
            <dd className="font-medium text-primary">{factorHours}h</dd>
            {values.manual_extra_hours > 0 && (
              <>
                <dt className="text-muted-foreground">{t.fullQuote.manualExtraHours}</dt>
                <dd className="font-medium text-primary">{values.manual_extra_hours}h</dd>
              </>
            )}
          </dl>
        </div>

        {/* Crew Section */}
        {totalCrew > 0 && (
          <div className="space-y-3">
            <h3 className="text-sm font-semibold text-foreground border-b pb-2">{t.wizard.step3}</h3>
            <dl className="grid grid-cols-2 gap-x-4 gap-y-3 text-sm">
              <dt className="text-muted-foreground">{t.fullQuote.totalCrew}</dt>
              <dd className="font-medium">{totalCrew} {t.fullQuote.workers}</dd>
              <dt className="text-muted-foreground">{t.fullQuote.projectDuration}</dt>
              <dd className="font-medium">
                {values.duration_type === 'half_day' && t.fullQuote.halfDay}
                {values.duration_type === 'full_day' && t.fullQuote.fullDay}
                {values.duration_type === 'multi_day' && `${t.fullQuote.multiDay} (${values.duration_days || '—'} ${t.fullQuote.numberOfDays.toLowerCase()})`}
              </dd>
              {values.geographic_zone && (
                <>
                  <dt className="text-muted-foreground">{t.fullQuote.geographicZone}</dt>
                  <dd className="font-medium">
                    {values.geographic_zone === 'core' && t.fullQuote.zoneCore}
                    {values.geographic_zone === 'secondary' && t.fullQuote.zoneSecondary}
                    {values.geographic_zone === 'north_premium' && t.fullQuote.zoneNorthPremium}
                    {values.geographic_zone === 'extended' && t.fullQuote.zoneExtended}
                    {values.geographic_zone === 'red_flag' && t.fullQuote.zoneRedFlag}
                  </dd>
                </>
              )}
              {values.premium_client_level !== 'standard' && (
                <>
                  <dt className="text-muted-foreground">{t.fullQuote.premiumClientLevel}</dt>
                  <dd className="font-medium">
                    {values.premium_client_level === 'premium_1' && t.fullQuote.premium1}
                    {values.premium_client_level === 'premium_2' && t.fullQuote.premium2}
                    {values.premium_client_level === 'premium_3' && t.fullQuote.premium3}
                  </dd>
                </>
              )}
            </dl>
          </div>
        )}

        {/* Equipment Section */}
        {(values.equipment_items.length > 0 || values.supply_chain_risk !== 'standard') && (
          <div className="space-y-3">
            <h3 className="text-sm font-semibold text-foreground border-b pb-2">{t.wizard.step4}</h3>
            <dl className="grid grid-cols-2 gap-x-4 gap-y-3 text-sm">
              {values.equipment_items.length > 0 && (
                <>
                  <dt className="text-muted-foreground">{t.fullQuote.toolsEquipment}</dt>
                  <dd className="font-medium">
                    {values.equipment_items.map(id => {
                      if (id === 'crane') return t.complexity.equipment.crane;
                      if (id === 'scaffolding') return t.complexity.equipment.scaffolding;
                      if (id === 'dumpster') return t.complexity.equipment.dumpster;
                      if (id === 'generator') return t.complexity.equipment.generator;
                      if (id === 'compressor') return t.complexity.equipment.compressor;
                      return id;
                    }).join(', ')}
                  </dd>
                </>
              )}
              {values.supply_chain_risk !== 'standard' && (
                <>
                  <dt className="text-muted-foreground">{t.fullQuote.supplyChainRisk}</dt>
                  <dd className="font-medium">
                    {values.supply_chain_risk === 'extended' && `${t.fullQuote.supplyExtended} (${t.fullQuote.supplyExtendedDesc})`}
                    {values.supply_chain_risk === 'import' && `${t.fullQuote.supplyImport} (${t.fullQuote.supplyImportDesc})`}
                  </dd>
                </>
              )}
            </dl>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
