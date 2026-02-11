"use client";

import { useLanguage } from "@/lib/i18n";
import { EstimateurTabs } from "@/components/estimateur/nav-tabs";
import { WizardContainer } from "@/components/estimateur/wizard/wizard-container";

export default function CompletPage() {
  const { t } = useLanguage();

  return (
    <div className="max-w-4xl">
      <h1 className="text-3xl font-bold tracking-tight mb-6">
        {t.nav.estimateur}
      </h1>
      <EstimateurTabs />
      <div className="mt-6">
        <WizardContainer />
      </div>
    </div>
  );
}
