"use client";

import { useState } from "react";
import { ChevronDown, SlidersHorizontal } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Input } from "@/components/ui/input";
import { cn } from "@/lib/utils";
import { useLanguage } from "@/lib/i18n";

/**
 * Factor values interface for 8 granular complexity factors.
 */
export interface FactorValues {
  roof_pitch: string | null;             // flat|low|medium|steep|very_steep
  access_difficulty: string[];            // selected checklist items
  demolition: string | null;              // none|single_layer|multi_layer|structural
  penetrations_count: number;             // 0+
  security: string[];                     // selected checklist items
  material_removal: string | null;        // none|standard|heavy|hazardous
  roof_sections_count: number;            // 1+
  previous_layers_count: number;          // 0+
}

/**
 * Configuration for a single factor option.
 */
export interface FactorOption {
  key: string;
  hours: number;
  label: string;  // Pre-localized
}

/**
 * Configuration for all complexity factors.
 */
export interface FactorConfig {
  roof_pitch: { options: FactorOption[] };
  access_difficulty: { options: FactorOption[] };
  demolition: { options: FactorOption[] };
  penetrations: { hours_per_item: number; label: string };
  security: { options: FactorOption[] };
  material_removal: { options: FactorOption[] };
  roof_sections: { hours_per_item_above: number; baseline: number; label: string };
  previous_layers: { hours_per_item_above: number; baseline: number; label: string };
}

/**
 * Props for the FactorChecklist component.
 */
export interface FactorChecklistProps {
  value: FactorValues;
  onChange: (value: FactorValues) => void;
  config: FactorConfig;           // Factor config (localized by parent)
  totalHours: number;             // Pre-computed total for display
}

/**
 * Collapsible factor checklist with 8 granular complexity inputs.
 *
 * Displays:
 * - 3 dropdown factors (roof_pitch, demolition, material_removal)
 * - 2 checklist factors (access_difficulty, security)
 * - 3 number inputs (penetrations_count, roof_sections_count, previous_layers_count)
 *
 * Each factor shows dynamic "+X hours" badge.
 * Collapsed by default, shows running total in header.
 */
export function FactorChecklist({
  value,
  onChange,
  config,
  totalHours,
}: FactorChecklistProps) {
  const { t } = useLanguage();
  const [isExpanded, setIsExpanded] = useState(false);

  /**
   * Update a single factor value while preserving others.
   */
  const updateFactor = <K extends keyof FactorValues>(
    key: K,
    newValue: FactorValues[K]
  ) => {
    onChange({
      ...value,
      [key]: newValue,
    });
  };

  /**
   * Calculate hours for a specific factor.
   */
  const getFactorHours = (factorKey: string): number => {
    switch (factorKey) {
      case "roof_pitch": {
        if (!value.roof_pitch) return 0;
        const option = config.roof_pitch.options.find(
          (o) => o.key === value.roof_pitch
        );
        return option?.hours || 0;
      }
      case "access_difficulty": {
        return value.access_difficulty.reduce((sum, key) => {
          const option = config.access_difficulty.options.find((o) => o.key === key);
          return sum + (option?.hours || 0);
        }, 0);
      }
      case "demolition": {
        if (!value.demolition) return 0;
        const option = config.demolition.options.find(
          (o) => o.key === value.demolition
        );
        return option?.hours || 0;
      }
      case "penetrations": {
        return value.penetrations_count * config.penetrations.hours_per_item;
      }
      case "security": {
        return value.security.reduce((sum, key) => {
          const option = config.security.options.find((o) => o.key === key);
          return sum + (option?.hours || 0);
        }, 0);
      }
      case "material_removal": {
        if (!value.material_removal) return 0;
        const option = config.material_removal.options.find(
          (o) => o.key === value.material_removal
        );
        return option?.hours || 0;
      }
      case "roof_sections": {
        const above = Math.max(
          0,
          value.roof_sections_count - config.roof_sections.baseline
        );
        return above * config.roof_sections.hours_per_item_above;
      }
      case "previous_layers": {
        const above = Math.max(
          0,
          value.previous_layers_count - config.previous_layers.baseline
        );
        return above * config.previous_layers.hours_per_item_above;
      }
      default:
        return 0;
    }
  };

  return (
    <div className="space-y-2">
      {/* Collapsible Header Button */}
      <Button
        type="button"
        variant="ghost"
        size="sm"
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full justify-between px-0 h-10 font-medium text-sm hover:bg-transparent"
        aria-expanded={isExpanded}
        aria-label="Toggle factor adjustments"
      >
        <span className="flex items-center gap-2">
          <SlidersHorizontal className="size-4 text-muted-foreground" />
          {t.fullQuote.personnaliserFacteurs || "Advanced Adjustments"} (
          {totalHours > 0 ? `+${totalHours}h` : "0h"})
        </span>
        <ChevronDown
          className={cn(
            "size-4 text-muted-foreground transition-transform duration-200",
            isExpanded && "rotate-180"
          )}
        />
      </Button>

      {/* Expanded Factor Inputs */}
      {isExpanded && (
        <div className="space-y-4 pt-2 pl-1">
          {/* 1. Roof Pitch (Dropdown) */}
          <div className="space-y-2">
            <div className="flex justify-between items-baseline">
              <label className="text-sm font-medium">
                {t.fullQuote.penteToit || "Roof Pitch"}
              </label>
              {value.roof_pitch && (
                <span className="text-xs text-primary font-medium">
                  +{getFactorHours("roof_pitch")}h
                </span>
              )}
            </div>
            <Select
              value={value.roof_pitch || ""}
              onValueChange={(val) => updateFactor("roof_pitch", val || null)}
            >
              <SelectTrigger className="w-full">
                <SelectValue placeholder="Select pitch..." />
              </SelectTrigger>
              <SelectContent>
                {config.roof_pitch.options.map((option) => (
                  <SelectItem key={option.key} value={option.key}>
                    {option.label} — +{option.hours}h
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* 2. Access Difficulty (Checklist) */}
          <div className="space-y-2">
            <div className="flex justify-between items-baseline">
              <label className="text-sm font-medium">
                {t.fullQuote.accessDifficulte || "Access Difficulty"}
              </label>
              {value.access_difficulty.length > 0 && (
                <span className="text-xs text-primary font-medium">
                  +{getFactorHours("access_difficulty")}h
                </span>
              )}
            </div>
            <div className="space-y-2 pl-1">
              {config.access_difficulty.options.map((option) => {
                const isChecked = value.access_difficulty.includes(option.key);
                return (
                  <div key={option.key} className="flex items-center gap-2">
                    <Checkbox
                      id={`access-${option.key}`}
                      checked={isChecked}
                      onCheckedChange={(checked) => {
                        if (checked) {
                          updateFactor("access_difficulty", [
                            ...value.access_difficulty,
                            option.key,
                          ]);
                        } else {
                          updateFactor(
                            "access_difficulty",
                            value.access_difficulty.filter((k) => k !== option.key)
                          );
                        }
                      }}
                    />
                    <label
                      htmlFor={`access-${option.key}`}
                      className="text-sm cursor-pointer flex-1"
                    >
                      {option.label}
                    </label>
                    <span className="text-xs text-primary">+{option.hours}h</span>
                  </div>
                );
              })}
            </div>
          </div>

          {/* 3. Demolition (Dropdown) */}
          <div className="space-y-2">
            <div className="flex justify-between items-baseline">
              <label className="text-sm font-medium">Demolition</label>
              {value.demolition && (
                <span className="text-xs text-primary font-medium">
                  +{getFactorHours("demolition")}h
                </span>
              )}
            </div>
            <Select
              value={value.demolition || ""}
              onValueChange={(val) => updateFactor("demolition", val || null)}
            >
              <SelectTrigger className="w-full">
                <SelectValue placeholder="Select demolition type..." />
              </SelectTrigger>
              <SelectContent>
                {config.demolition.options.map((option) => (
                  <SelectItem key={option.key} value={option.key}>
                    {option.label} — +{option.hours}h
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* 4. Penetrations Count (Number Input) */}
          <div className="space-y-2">
            <div className="flex justify-between items-baseline">
              <label className="text-sm font-medium">
                {config.penetrations.label}
              </label>
              {value.penetrations_count > 0 && (
                <span className="text-xs text-primary font-medium">
                  +{getFactorHours("penetrations")}h
                </span>
              )}
            </div>
            <Input
              type="number"
              min={0}
              max={100}
              value={value.penetrations_count}
              onChange={(e) =>
                updateFactor(
                  "penetrations_count",
                  parseInt(e.target.value) || 0
                )
              }
              className="w-full"
            />
          </div>

          {/* 5. Security (Checklist) */}
          <div className="space-y-2">
            <div className="flex justify-between items-baseline">
              <label className="text-sm font-medium">
                {t.fullQuote.securite || "Security"}
              </label>
              {value.security.length > 0 && (
                <span className="text-xs text-primary font-medium">
                  +{getFactorHours("security")}h
                </span>
              )}
            </div>
            <div className="space-y-2 pl-1">
              {config.security.options.map((option) => {
                const isChecked = value.security.includes(option.key);
                return (
                  <div key={option.key} className="flex items-center gap-2">
                    <Checkbox
                      id={`security-${option.key}`}
                      checked={isChecked}
                      onCheckedChange={(checked) => {
                        if (checked) {
                          updateFactor("security", [...value.security, option.key]);
                        } else {
                          updateFactor(
                            "security",
                            value.security.filter((k) => k !== option.key)
                          );
                        }
                      }}
                    />
                    <label
                      htmlFor={`security-${option.key}`}
                      className="text-sm cursor-pointer flex-1"
                    >
                      {option.label}
                    </label>
                    <span className="text-xs text-primary">+{option.hours}h</span>
                  </div>
                );
              })}
            </div>
          </div>

          {/* 6. Material Removal (Dropdown) */}
          <div className="space-y-2">
            <div className="flex justify-between items-baseline">
              <label className="text-sm font-medium">
                {t.fullQuote.retraitMateriaux || "Material Removal"}
              </label>
              {value.material_removal && (
                <span className="text-xs text-primary font-medium">
                  +{getFactorHours("material_removal")}h
                </span>
              )}
            </div>
            <Select
              value={value.material_removal || ""}
              onValueChange={(val) =>
                updateFactor("material_removal", val || null)
              }
            >
              <SelectTrigger className="w-full">
                <SelectValue placeholder="Select material removal..." />
              </SelectTrigger>
              <SelectContent>
                {config.material_removal.options.map((option) => (
                  <SelectItem key={option.key} value={option.key}>
                    {option.label} — +{option.hours}h
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* 7. Roof Sections Count (Number Input) */}
          <div className="space-y-2">
            <div className="flex justify-between items-baseline">
              <label className="text-sm font-medium">
                {config.roof_sections.label}
              </label>
              {value.roof_sections_count > config.roof_sections.baseline && (
                <span className="text-xs text-primary font-medium">
                  +{getFactorHours("roof_sections")}h
                </span>
              )}
            </div>
            <Input
              type="number"
              min={1}
              max={20}
              value={value.roof_sections_count}
              onChange={(e) =>
                updateFactor(
                  "roof_sections_count",
                  parseInt(e.target.value) || 1
                )
              }
              className="w-full"
            />
          </div>

          {/* 8. Previous Layers Count (Number Input) */}
          <div className="space-y-2">
            <div className="flex justify-between items-baseline">
              <label className="text-sm font-medium">
                {config.previous_layers.label}
              </label>
              {value.previous_layers_count > config.previous_layers.baseline && (
                <span className="text-xs text-primary font-medium">
                  +{getFactorHours("previous_layers")}h
                </span>
              )}
            </div>
            <Input
              type="number"
              min={0}
              max={10}
              value={value.previous_layers_count}
              onChange={(e) =>
                updateFactor(
                  "previous_layers_count",
                  parseInt(e.target.value) || 0
                )
              }
              className="w-full"
            />
          </div>

          {/* Running Total */}
          <div className="flex justify-between pt-3 border-t">
            <span className="text-sm font-medium">
              {t.fullQuote.totalFacteurs || "Total Adjustments"}
            </span>
            <span className="text-sm font-semibold text-primary">
              +{totalHours}h
            </span>
          </div>
        </div>
      )}
    </div>
  );
}
