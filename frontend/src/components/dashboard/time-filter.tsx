"use client";

import { ToggleGroup, ToggleGroupItem } from "@/components/ui/toggle-group";
import type { TimePeriod } from "@/types/analytics";

interface TimeFilterProps {
  value: TimePeriod;
  onChange: (value: TimePeriod) => void;
}

export function TimeFilter({ value, onChange }: TimeFilterProps) {
  return (
    <ToggleGroup
      type="single"
      value={value}
      onValueChange={(newValue) => {
        // Don't call onChange if the user deselects (empty string)
        if (newValue) {
          onChange(newValue as TimePeriod);
        }
      }}
      variant="outline"
    >
      <ToggleGroupItem value="7d" aria-label="Last 7 days">
        7 Days
      </ToggleGroupItem>
      <ToggleGroupItem value="30d" aria-label="Last 30 days">
        30 Days
      </ToggleGroupItem>
      <ToggleGroupItem value="all" aria-label="All time">
        All Time
      </ToggleGroupItem>
    </ToggleGroup>
  );
}
