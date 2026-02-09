"use client";

import { useState } from "react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { useLanguage } from "@/lib/i18n";
import type { UpsellSuggestion } from "@/types/submission";

interface UpsellDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  suggestions: UpsellSuggestion[];
  onCreateUpsell: (type: string) => Promise<void>;
  locale: string;
}

export function UpsellDialog({
  open,
  onOpenChange,
  suggestions,
  onCreateUpsell,
  locale,
}: UpsellDialogProps) {
  const { t } = useLanguage();
  const [loadingType, setLoadingType] = useState<string | null>(null);

  const handleCreate = async (type: string) => {
    setLoadingType(type);
    try {
      await onCreateUpsell(type);
    } catch (error) {
      console.error("Failed to create upsell:", error);
    } finally {
      setLoadingType(null);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>{t.submission.upsellSuggestions}</DialogTitle>
          <DialogDescription>
            {t.submission.upsellDescription}
          </DialogDescription>
        </DialogHeader>

        {/* Suggestions list */}
        <div className="space-y-3 py-4">
          {suggestions.map((suggestion) => {
            const name = locale === "fr" ? suggestion.name_fr : suggestion.name_en;
            const description =
              locale === "fr"
                ? suggestion.description_fr
                : suggestion.description_en;

            return (
              <div
                key={suggestion.type}
                className="flex items-start justify-between gap-4 rounded-lg border p-4"
              >
                <div className="flex-1 space-y-1">
                  <h4 className="text-sm font-medium">{name}</h4>
                  <p className="text-sm text-muted-foreground">{description}</p>
                </div>
                <Button
                  size="sm"
                  onClick={() => handleCreate(suggestion.type)}
                  disabled={loadingType !== null}
                  className="shrink-0"
                >
                  {loadingType === suggestion.type
                    ? t.common.chargement
                    : t.submission.createUpsell}
                </Button>
              </div>
            );
          })}
        </div>

        <DialogFooter>
          <Button
            variant="outline"
            onClick={() => onOpenChange(false)}
            disabled={loadingType !== null}
          >
            {t.submission.skipUpsells}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
