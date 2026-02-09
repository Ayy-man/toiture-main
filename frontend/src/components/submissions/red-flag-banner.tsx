"use client";

import { useState } from "react";
import { AlertTriangle, X } from "lucide-react";
import { useLanguage } from "@/lib/i18n";
import { Button } from "@/components/ui/button";
import type { RedFlag } from "@/lib/api/submissions";

interface RedFlagBannerProps {
  flags: RedFlag[];
  onDismiss?: (category: string) => void;
}

export function RedFlagBanner({ flags, onDismiss }: RedFlagBannerProps) {
  const { locale } = useLanguage();
  const [dismissed, setDismissed] = useState<Set<string>>(new Set());

  const visibleFlags = flags.filter((f) => !dismissed.has(f.category));

  if (visibleFlags.length === 0) return null;

  function handleDismiss(category: string) {
    setDismissed((prev) => new Set(prev).add(category));
    onDismiss?.(category);
  }

  return (
    <div className="space-y-2 mb-4">
      {visibleFlags.map((flag) => {
        const isCritical = flag.severity === "critical";
        const message = locale === "fr" ? flag.message_fr : flag.message_en;

        return (
          <div
            key={flag.category}
            className={`flex items-start gap-3 rounded-lg border p-3 text-sm ${
              isCritical
                ? "border-destructive/50 bg-destructive/10 text-destructive"
                : "border-yellow-500/50 bg-yellow-500/10 text-yellow-700 dark:text-yellow-400"
            }`}
          >
            <AlertTriangle className="h-4 w-4 mt-0.5 flex-shrink-0" />
            <div className="flex-1">
              <p className="font-medium">{message}</p>
            </div>
            {flag.dismissible && (
              <Button
                variant="ghost"
                size="sm"
                className="h-6 w-6 p-0 flex-shrink-0"
                onClick={() => handleDismiss(flag.category)}
              >
                <X className="h-3 w-3" />
              </Button>
            )}
          </div>
        );
      })}
    </div>
  );
}
