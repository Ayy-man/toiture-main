"use client";

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import type { SimilarCase } from "@/lib/api";
import { useLanguage } from "@/lib/i18n";

interface SimilarCasesProps {
  cases: SimilarCase[];
}

/**
 * Display a list of similar historical cases from CBR
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

  return (
    <Card>
      <CardHeader>
        <CardTitle>{t.casSimilaires.titre}</CardTitle>
        <CardDescription>{t.casSimilaires.description}</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {cases.map((caseItem, index) => (
            <div
              key={caseItem.case_id}
              className={index < cases.length - 1 ? "border-b pb-4" : ""}
            >
              <div className="flex items-center justify-between">
                <span className="font-medium">
                  {caseItem.category || t.casSimilaires.inconnu} ({caseItem.year || t.casSimilaires.na})
                </span>
                <span className="text-sm font-medium text-primary">
                  {(caseItem.similarity * 100).toFixed(0)}% {t.casSimilaires.correspondance}
                </span>
              </div>
              <div className="mt-1 grid grid-cols-2 gap-2 text-sm text-muted-foreground">
                <span>{caseItem.sqft?.toLocaleString() || t.casSimilaires.na} {t.casSimilaires.pi2}</span>
                <span className="text-right">
                  ${caseItem.total?.toLocaleString() || t.casSimilaires.na} {t.casSimilaires.total}
                </span>
                <span className="col-span-2 text-right">
                  ${caseItem.per_sqft?.toFixed(2) || t.casSimilaires.na}{t.casSimilaires.parPi2}
                </span>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
