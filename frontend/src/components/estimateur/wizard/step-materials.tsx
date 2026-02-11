"use client";

import { useFormContext } from "react-hook-form";
import {
  FormControl,
  FormField,
  FormItem,
  FormLabel,
} from "@/components/ui/form";
import {
  Card,
  CardHeader,
  CardTitle,
  CardContent,
} from "@/components/ui/card";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Checkbox } from "@/components/ui/checkbox";
import { Package, AlertCircle } from "lucide-react";
import { useLanguage } from "@/lib/i18n";
import type { HybridQuoteFormData } from "@/lib/schemas/hybrid-quote";

/**
 * Step 4: Materials - Equipment items and supply chain risk
 */
export function StepMaterials() {
  const { t } = useLanguage();
  const form = useFormContext<HybridQuoteFormData>();

  // Equipment options (hardcoded to avoid async load)
  const equipmentOptions = [
    { id: "crane", label: t.complexity.equipment.crane, dailyCost: 25 },
    { id: "scaffolding", label: t.complexity.equipment.scaffolding, dailyCost: 25 },
    { id: "dumpster", label: t.complexity.equipment.dumpster, dailyCost: 25 },
    { id: "generator", label: t.complexity.equipment.generator, dailyCost: 25 },
    { id: "compressor", label: t.complexity.equipment.compressor, dailyCost: 25 },
  ];

  const supplyRisk = form.watch("supply_chain_risk");

  return (
    <Card>
      <CardHeader className="pb-4">
        <div className="flex items-center gap-2">
          <div className="flex size-8 items-center justify-center rounded-lg bg-primary/10 text-primary">
            <Package className="size-4" />
          </div>
          <div>
            <CardTitle className="text-lg">{t.fullQuote.equipmentSupplyChain}</CardTitle>
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Equipment Checklist */}
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

        {/* Supply Chain Risk */}
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

        {/* Supply Chain Warning */}
        {(supplyRisk === 'extended' || supplyRisk === 'import') && (
          <div className="flex items-center gap-2 rounded-lg border border-yellow-500/50 bg-yellow-500/10 p-3">
            <AlertCircle className="size-5 shrink-0 text-yellow-600" />
            <p className="text-sm text-yellow-700 dark:text-yellow-400">
              {t.fullQuote.supplyWarning}
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
