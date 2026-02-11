"use client";

import { useFormContext } from "react-hook-form";
import {
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormDescription,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import {
  Card,
  CardHeader,
  CardTitle,
  CardContent,
} from "@/components/ui/card";
import { Layers } from "lucide-react";
import { useLanguage } from "@/lib/i18n";
import type { HybridQuoteFormData } from "@/lib/schemas/hybrid-quote";
import { TierSelector, type TierData } from "../tier-selector";
import { FactorChecklist, type FactorConfig } from "../factor-checklist";

interface StepComplexityProps {
  tiers: TierData[];
  factorConfig: FactorConfig;
  calculatedFactorHours: number;
}

/**
 * Step 2: Complexity - Tier selector, factor checklist, manual extra hours
 */
export function StepComplexity({ tiers, factorConfig, calculatedFactorHours }: StepComplexityProps) {
  const { t } = useLanguage();
  const form = useFormContext<HybridQuoteFormData>();

  return (
    <Card>
      <CardHeader className="pb-4">
        <div className="flex items-center gap-2">
          <div className="flex size-8 items-center justify-center rounded-lg bg-primary/10 text-primary">
            <Layers className="size-4" />
          </div>
          <div>
            <CardTitle className="text-lg">{t.fullQuote.complexiteProjet}</CardTitle>
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
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
      </CardContent>
    </Card>
  );
}
