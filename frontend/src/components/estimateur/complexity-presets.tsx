"use client";

import { useState } from "react";
import { ChevronDown, Settings2 } from "lucide-react";
import { Slider } from "@/components/ui/slider";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { useLanguage } from "@/lib/i18n";

/**
 * Preset values for complexity factors.
 * From 14-CONTEXT.md complexity preset table.
 */
const PRESETS = {
  Simple: {
    access_difficulty: 2,
    roof_pitch: 2,
    penetrations: 1,
    material_removal: 2,
    safety_concerns: 2,
    timeline_constraints: 2,
  },
  Modere: {
    access_difficulty: 5,
    roof_pitch: 4,
    penetrations: 5,
    material_removal: 4,
    safety_concerns: 5,
    timeline_constraints: 5,
  },
  Complexe: {
    access_difficulty: 8,
    roof_pitch: 6,
    penetrations: 8,
    material_removal: 6,
    safety_concerns: 8,
    timeline_constraints: 8,
  },
} as const;

type PresetType = keyof typeof PRESETS;

/**
 * Complexity factor keys with min/max values from backend schema.
 * Labels come from translations.
 */
const FACTOR_CONFIG = [
  { key: "access_difficulty" as const, labelKey: "accessDifficulte", descKey: "accessDifficulteDesc", min: 0, max: 10 },
  { key: "roof_pitch" as const, labelKey: "penteToit", descKey: "penteToitDesc", min: 0, max: 8 },
  { key: "penetrations" as const, labelKey: "penetrations", descKey: "penetrationsDesc", min: 0, max: 10 },
  { key: "material_removal" as const, labelKey: "retraitMateriaux", descKey: "retraitMateriauxDesc", min: 0, max: 8 },
  { key: "safety_concerns" as const, labelKey: "securite", descKey: "securiteDesc", min: 0, max: 10 },
  { key: "timeline_constraints" as const, labelKey: "delai", descKey: "delaiDesc", min: 0, max: 10 },
] as const;

export interface ComplexityPresetsProps {
  value: {
    preset: PresetType | null;
    access_difficulty: number;
    roof_pitch: number;
    penetrations: number;
    material_removal: number;
    safety_concerns: number;
    timeline_constraints: number;
  };
  onChange: (value: ComplexityPresetsProps["value"]) => void;
}

/**
 * Complexity presets component with 6-factor override.
 *
 * Provides:
 * - Three presets: Simple, Modere, Complexe
 * - Collapsible custom sliders for each of 6 factors
 * - Auto-computed aggregate (sum of factors)
 * - Preset clears when any slider is manually adjusted
 */
export function ComplexityPresets({ value, onChange }: ComplexityPresetsProps) {
  const { t } = useLanguage();
  const [isExpanded, setIsExpanded] = useState(false);

  // Calculate aggregate as sum of all factors
  const aggregate =
    value.access_difficulty +
    value.roof_pitch +
    value.penetrations +
    value.material_removal +
    value.safety_concerns +
    value.timeline_constraints;

  // Determine current preset based on values
  const currentPreset = (Object.keys(PRESETS) as PresetType[]).find((preset) => {
    const presetValues = PRESETS[preset];
    return (
      value.access_difficulty === presetValues.access_difficulty &&
      value.roof_pitch === presetValues.roof_pitch &&
      value.penetrations === presetValues.penetrations &&
      value.material_removal === presetValues.material_removal &&
      value.safety_concerns === presetValues.safety_concerns &&
      value.timeline_constraints === presetValues.timeline_constraints
    );
  });

  /**
   * Handle preset selection.
   * Updates all 6 factors to preset values.
   */
  const handlePresetChange = (preset: PresetType) => {
    onChange({
      preset,
      ...PRESETS[preset],
    });
  };

  /**
   * Handle individual factor change.
   * Clears preset selection (switches to custom mode).
   */
  const handleFactorChange = (
    key: keyof Omit<ComplexityPresetsProps["value"], "preset">,
    newValue: number[]
  ) => {
    onChange({
      ...value,
      preset: null, // Clear preset when custom adjustment made
      [key]: newValue[0],
    });
  };

  return (
    <div className="space-y-5">
      {/* Preset Selection - Pill Style */}
      <div className="space-y-3">
        <label className="text-sm font-medium text-foreground">
          {t.fullQuote.niveauComplexite}
        </label>
        <div className="flex gap-2">
          {(Object.keys(PRESETS) as PresetType[]).map((preset) => {
            const isActive = currentPreset === preset;
            const presetLabels: Record<PresetType, string> = {
              Simple: t.fullQuote.presetSimple,
              Modere: t.fullQuote.presetModere,
              Complexe: t.fullQuote.presetComplexe,
            };
            return (
              <button
                key={preset}
                type="button"
                onClick={() => handlePresetChange(preset)}
                className={cn(
                  "flex-1 px-4 py-2.5 rounded-full text-sm font-medium transition-all duration-200",
                  isActive
                    ? "bg-primary text-primary-foreground shadow-md"
                    : "bg-muted text-muted-foreground hover:bg-muted/80"
                )}
              >
                {presetLabels[preset]}
              </button>
            );
          })}
        </div>
      </div>

      {/* Computed Aggregate - Progress Bar Style */}
      <div className="space-y-2">
        <div className="flex justify-between text-sm">
          <span className="text-muted-foreground">{t.fullQuote.scoreComplexite}</span>
          <span className="font-semibold text-foreground">{aggregate}/56</span>
        </div>
        <div className="h-2 bg-muted rounded-full overflow-hidden">
          <div
            className="h-full bg-primary transition-all duration-300 rounded-full"
            style={{ width: `${(aggregate / 56) * 100}%` }}
          />
        </div>
      </div>

      {/* Collapsible Custom Factors */}
      <div className="space-y-2">
        <Button
          type="button"
          variant="ghost"
          size="sm"
          onClick={() => setIsExpanded(!isExpanded)}
          className="w-full justify-between px-0 h-10 font-medium text-sm hover:bg-transparent"
          aria-expanded={isExpanded}
          aria-label="Toggle custom factors"
        >
          <span className="flex items-center gap-2">
            <Settings2 className="size-4 text-muted-foreground" />
            {t.fullQuote.personnaliserFacteurs}
          </span>
          <ChevronDown
            className={cn(
              "size-4 text-muted-foreground transition-transform duration-200",
              isExpanded && "rotate-180"
            )}
          />
        </Button>

        {isExpanded && (
          <div className="space-y-4 pt-2 pl-1">
            {FACTOR_CONFIG.map((factor) => {
              const currentValue = value[factor.key];
              const label = t.fullQuote[factor.labelKey as keyof typeof t.fullQuote] as string;
              const description = t.fullQuote[factor.descKey as keyof typeof t.fullQuote] as string;
              return (
                <div key={factor.key} className="space-y-2">
                  <div className="flex justify-between items-baseline">
                    <div className="space-y-0.5">
                      <label
                        htmlFor={`factor-${factor.key}`}
                        className="text-sm font-medium"
                      >
                        {label}
                      </label>
                      <p className="text-xs text-muted-foreground">
                        {description}
                      </p>
                    </div>
                    <span className="text-sm font-semibold text-primary tabular-nums">
                      {currentValue}
                    </span>
                  </div>
                  <Slider
                    id={`factor-${factor.key}`}
                    min={factor.min}
                    max={factor.max}
                    step={1}
                    value={[currentValue]}
                    onValueChange={(newValue) =>
                      handleFactorChange(factor.key, newValue)
                    }
                    aria-label={label}
                    className="py-1"
                  />
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
