"use client";

import { CheckCircle, Info, AlertTriangle } from "lucide-react";
import { cn } from "@/lib/utils";
import { useLanguage } from "@/lib/i18n";

interface ConfidenceBadgeProps {
  confidence: number; // 0-1 float
  className?: string;
}

/**
 * Confidence badge with color-coded indicator.
 * Shows green for HIGH (>=0.7), amber for MEDIUM (>=0.4), red for LOW (<0.4).
 */
export function ConfidenceBadge({ confidence, className }: ConfidenceBadgeProps) {
  const { t } = useLanguage();

  // Determine confidence level and styling
  const getConfidenceLevel = () => {
    if (confidence >= 0.7) {
      return {
        label: t.resultat.haute,
        icon: CheckCircle,
        colorClasses: "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400",
      };
    } else if (confidence >= 0.4) {
      return {
        label: t.resultat.moyenne,
        icon: Info,
        colorClasses: "bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400",
      };
    } else {
      return {
        label: t.resultat.faible,
        icon: AlertTriangle,
        colorClasses: "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400",
      };
    }
  };

  const { label, icon: Icon, colorClasses } = getConfidenceLevel();
  const percentage = Math.round(confidence * 100);

  return (
    <div
      className={cn(
        "inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-xs font-semibold",
        colorClasses,
        className
      )}
    >
      <Icon className="size-3.5" />
      <span>{percentage}%</span>
      <span>{label}</span>
    </div>
  );
}
