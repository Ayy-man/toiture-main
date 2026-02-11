"use client";

import { useLanguage } from "@/lib/i18n";
import { EstimateurTabs } from "@/components/estimateur/nav-tabs";
import { SubmissionList } from "@/components/estimateur/submission-list";

export default function SoumissionsPage() {
  const { t } = useLanguage();

  return (
    <div className="max-w-4xl">
      <h1 className="text-3xl font-bold tracking-tight mb-6">
        {t.nav.estimateur}
      </h1>
      <EstimateurTabs />
      <div className="mt-6">
        <SubmissionList />
      </div>
    </div>
  );
}
