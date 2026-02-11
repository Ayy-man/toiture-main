"use client";

import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

interface SuggestionPillsProps {
  suggestions: string[];
  onSelect: (suggestion: string) => void;
  disabled?: boolean;
}

export function SuggestionPills({ suggestions, onSelect, disabled = false }: SuggestionPillsProps) {
  if (suggestions.length === 0) return null;

  return (
    <div className="flex gap-2 overflow-x-auto flex-nowrap pb-2 [&::-webkit-scrollbar]:hidden [-ms-overflow-style:none] [scrollbar-width:none]">
      {suggestions.map((suggestion, index) => (
        <Badge
          key={index}
          variant="outline"
          className={cn(
            "cursor-pointer rounded-full px-3 py-1.5 whitespace-nowrap shrink-0 transition-colors",
            !disabled && "hover:bg-primary hover:text-primary-foreground",
            disabled && "opacity-50 cursor-not-allowed"
          )}
          onClick={() => !disabled && onSelect(suggestion)}
        >
          {suggestion}
        </Badge>
      ))}
    </div>
  );
}
