"use client";

import { useLanguage } from "@/lib/i18n";
import { EstimateForm } from "@/components/estimate-form";
import { EstimateurTabs } from "@/components/estimateur/nav-tabs";

export default function EstimateurPage() {
  const { t } = useLanguage();

  return (
    <div className="max-w-2xl">
      <h1 className="text-3xl font-bold tracking-tight mb-6">
        {t.nav.estimateur}
      </h1>
      <EstimateurTabs />
      <div className="mt-6">
        <EstimateForm />
      </div>
    </div>
  );
}
