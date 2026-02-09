"use client";

import { Check } from "lucide-react";
import { cn } from "@/lib/utils";
import { useLanguage } from "@/lib/i18n";

/**
 * Tier data structure for the 6-tier complexity system.
 */
export interface TierData {
  tier: number;       // 1-6
  name: string;       // Localized tier name
  description: string; // Localized description
  scoreRange: string; // e.g., "0-16"
  hoursAdded: number; // e.g., 0, 4, 8, 16, 24, 40
}

/**
 * Props for the TierSelector component.
 */
export interface TierSelectorProps {
  value: number | null;           // Currently selected tier (1-6) or null
  onChange: (tier: number) => void; // Called when user clicks a tier
  tiers: TierData[];               // Tier data (from config, localized by parent)
}

/**
 * Visual tier selector component with 6 clickable cards in a 2x3 grid.
 *
 * Each card shows tier name, score range, and hours added.
 * Selected tier is highlighted with primary color styling.
 * Responsive: 2 columns on mobile, 3 columns on sm+ screens.
 */
export function TierSelector({ value, onChange, tiers }: TierSelectorProps) {
  const { t } = useLanguage();

  // Find selected tier description for display below grid
  const selectedTier = tiers.find((tier) => tier.tier === value);

  return (
    <div className="space-y-4">
      {/* Section Label */}
      <label className="text-sm font-medium text-foreground">
        {t.fullQuote.niveauComplexite}
      </label>

      {/* Tier Cards Grid - 3 cols always, compact cards */}
      <div className="grid grid-cols-3 gap-2">
        {tiers.map((tier) => {
          const isSelected = value === tier.tier;

          return (
            <div
              key={tier.tier}
              onClick={() => onChange(tier.tier)}
              className={cn(
                "rounded-xl border px-3 py-3 cursor-pointer transition-all duration-200 text-center",
                isSelected
                  ? "border-primary bg-primary/5 shadow-md ring-1 ring-primary/20"
                  : "border-border/50 hover:border-border hover:bg-muted/30"
              )}
              role="button"
              tabIndex={0}
              aria-pressed={isSelected}
              onKeyDown={(e) => {
                if (e.key === "Enter" || e.key === " ") {
                  e.preventDefault();
                  onChange(tier.tier);
                }
              }}
            >
              {/* Tier Number Badge */}
              <div
                className={cn(
                  "size-6 rounded-full flex items-center justify-center text-xs font-semibold mx-auto",
                  isSelected
                    ? "bg-primary text-primary-foreground"
                    : "bg-muted text-muted-foreground"
                )}
              >
                {isSelected ? <Check className="size-3" /> : tier.tier}
              </div>

              {/* Tier Name */}
              <h3 className="text-xs font-semibold mt-1.5 text-foreground leading-tight">
                {tier.name}
              </h3>

              {/* Score Range */}
              <p className="text-[10px] text-muted-foreground mt-0.5">
                {tier.scoreRange} pts
              </p>

              {/* Hours Added (only show if > 0) */}
              {tier.hoursAdded > 0 && (
                <p className="text-[10px] font-medium text-primary mt-0.5">
                  +{tier.hoursAdded}h
                </p>
              )}
            </div>
          );
        })}
      </div>

      {/* Selected Tier Description */}
      {selectedTier && (
        <p className="text-sm text-muted-foreground">
          {selectedTier.description}
        </p>
      )}
    </div>
  );
}
