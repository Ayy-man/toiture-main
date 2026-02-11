"use client";

import { motion } from "framer-motion";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { cn } from "@/lib/utils";
import type { SimilarCase } from "@/lib/api";
import { useLanguage } from "@/lib/i18n";

interface SimilarCasesProps {
  cases: SimilarCase[];
}

/**
 * Display similar historical cases as a grid of mini-cards.
 * Shows similarity percentage, category, sqft, and pricing.
 */
export function SimilarCases({ cases }: SimilarCasesProps) {
  const { t } = useLanguage();

  if (cases.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>{t.casSimilaires.titre}</CardTitle>
          <CardDescription>{t.casSimilaires.description}</CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">
            {t.casSimilaires.aucun}
          </p>
        </CardContent>
      </Card>
    );
  }

  // Get similarity badge color (same thresholds as confidence)
  const getSimilarityBadgeColor = (similarity: number) => {
    if (similarity >= 0.7) {
      return "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400";
    } else if (similarity >= 0.4) {
      return "bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400";
    } else {
      return "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400";
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>{t.casSimilaires.titre}</CardTitle>
        <CardDescription>{t.casSimilaires.description}</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
          {cases.map((caseItem, index) => (
            <motion.div
              key={caseItem.case_id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
            >
              <Card className="h-full">
                <CardContent className="pt-4 space-y-2">
                  {/* Category and Year */}
                  <div className="flex items-center justify-between">
                    <span className="font-medium text-sm">
                      {caseItem.category || t.casSimilaires.inconnu}
                    </span>
                    <span className="text-xs text-muted-foreground">
                      {caseItem.year || t.casSimilaires.na}
                    </span>
                  </div>

                  {/* Similarity Badge */}
                  <div className="flex justify-center">
                    <span
                      className={cn(
                        "inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold",
                        getSimilarityBadgeColor(caseItem.similarity)
                      )}
                    >
                      {(caseItem.similarity * 100).toFixed(0)}%{" "}
                      {t.casSimilaires.correspondance}
                    </span>
                  </div>

                  {/* Details */}
                  <div className="space-y-1 text-xs text-muted-foreground">
                    <div className="flex justify-between">
                      <span>{t.casSimilaires.pi2}</span>
                      <span className="font-medium">
                        {caseItem.sqft?.toLocaleString() || t.casSimilaires.na}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span>{t.casSimilaires.total}</span>
                      <span className="font-medium">
                        ${caseItem.total?.toLocaleString() || t.casSimilaires.na}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span>{t.casSimilaires.parPi2}</span>
                      <span className="font-medium">
                        ${caseItem.per_sqft?.toFixed(2) || t.casSimilaires.na}
                      </span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
