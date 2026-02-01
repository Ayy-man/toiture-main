"use client";

import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
} from "@/components/ui/card";
import { useLanguage } from "@/lib/i18n";
import { Info } from "lucide-react";

export function MaterialsForm() {
  const { t } = useLanguage();
  return (
    <Card>
      <CardHeader>
        <CardTitle>{t.estimateur.titreMateriaux}</CardTitle>
        <CardDescription>{t.estimateur.descriptionMateriaux}</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="flex items-start gap-3 rounded-lg bg-amber-50 border border-amber-200 p-4">
          <Info className="h-5 w-5 text-amber-600 mt-0.5 flex-shrink-0" />
          <div>
            <p className="font-medium text-amber-800">
              {t.estimateur.bientotDisponible}
            </p>
            <p className="text-sm text-amber-700 mt-1">
              {t.estimateur.fonctionnalitePhase10}
            </p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
