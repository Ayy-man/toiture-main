"use client";

import { useState } from "react";
import { ChevronDownIcon } from "lucide-react";
import { ToggleGroup, ToggleGroupItem } from "@/components/ui/toggle-group";
import { Slider } from "@/components/ui/slider";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

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
 * Complexity factor configuration.
 * French labels with min/max values from backend schema.
 */
const FACTORS = [
  {
    key: "access_difficulty" as const,
    label: "Difficulte d'acces",
    min: 0,
    max: 10,
  },
  {
    key: "roof_pitch" as const,
    label: "Pente du toit",
    min: 0,
    max: 8,
  },
  {
    key: "penetrations" as const,
    label: "Penetrations",
    min: 0,
    max: 10,
  },
  {
    key: "material_removal" as const,
    label: "Retrait de materiaux",
    min: 0,
    max: 8,
  },
  {
    key: "safety_concerns" as const,
    label: "Preoccupations de securite",
    min: 0,
    max: 10,
  },
  {
    key: "timeline_constraints" as const,
    label: "Contraintes de delai",
    min: 0,
    max: 10,
  },
];

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
  const [isExpanded, setIsExpanded] = useState(false);

  // Calculate aggregate as sum of all factors
  const aggregate =
    value.access_difficulty +
    value.roof_pitch +
    value.penetrations +
    value.material_removal +
    value.safety_concerns +
    value.timeline_constraints;

  /**
   * Handle preset selection.
   * Updates all 6 factors to preset values.
   */
  const handlePresetChange = (preset: string) => {
    if (!preset || !(preset in PRESETS)) {
      return;
    }

    const presetKey = preset as PresetType;
    onChange({
      preset: presetKey,
      ...PRESETS[presetKey],
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
    <div className="space-y-4">
      {/* Preset Selection */}
      <div className="space-y-2">
        <label className="text-sm font-medium">Complexite du travail</label>
        <ToggleGroup
          type="single"
          value={value.preset || ""}
          onValueChange={handlePresetChange}
          className="justify-start"
        >
          <ToggleGroupItem value="Simple" aria-label="Preset Simple">
            Simple
          </ToggleGroupItem>
          <ToggleGroupItem value="Modere" aria-label="Preset Modere">
            Modere
          </ToggleGroupItem>
          <ToggleGroupItem value="Complexe" aria-label="Preset Complexe">
            Complexe
          </ToggleGroupItem>
        </ToggleGroup>
      </div>

      {/* Computed Aggregate */}
      <div className="text-sm text-muted-foreground">
        Total: <span className="font-semibold text-foreground">{aggregate}</span>/56
      </div>

      {/* Collapsible Custom Factors */}
      <div className="space-y-3">
        <Button
          type="button"
          variant="ghost"
          size="sm"
          onClick={() => setIsExpanded(!isExpanded)}
          className="w-full justify-between p-0 h-auto font-medium text-sm"
          aria-expanded={isExpanded}
          aria-label="Toggle custom factors"
        >
          <span>Personnaliser les facteurs</span>
          <ChevronDownIcon
            className={cn(
              "size-4 transition-transform",
              isExpanded && "rotate-180"
            )}
          />
        </Button>

        {isExpanded && (
          <div className="space-y-4 pt-2">
            {FACTORS.map((factor) => {
              const currentValue = value[factor.key];
              return (
                <div key={factor.key} className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <label htmlFor={`factor-${factor.key}`}>
                      {factor.label}
                    </label>
                    <span className="text-muted-foreground">
                      {currentValue}/{factor.max}
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
                    aria-label={factor.label}
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
