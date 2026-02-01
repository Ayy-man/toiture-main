"use client";

import { useLanguage } from "@/lib/i18n";
import { EstimateurTabs } from "@/components/estimateur/nav-tabs";
import { MaterialsForm } from "@/components/estimateur/materials-form";

export default function MateriauxPage() {
  const { t } = useLanguage();

  return (
    <div className="max-w-2xl">
      <h1 className="text-3xl font-bold tracking-tight mb-6">
        {t.nav.estimateur}
      </h1>
      <EstimateurTabs />
      <div className="mt-6">
        <MaterialsForm />
      </div>
    </div>
  );
}
