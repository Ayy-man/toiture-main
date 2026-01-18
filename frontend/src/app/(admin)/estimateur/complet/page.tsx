import { fr } from "@/lib/i18n/fr";
import { EstimateurTabs } from "@/components/estimateur/nav-tabs";
import { FullQuoteForm } from "@/components/estimateur/full-quote-form";

export default function CompletPage() {
  return (
    <div className="max-w-2xl">
      <h1 className="text-3xl font-bold tracking-tight mb-6">
        {fr.nav.estimateur}
      </h1>
      <EstimateurTabs />
      <div className="mt-6">
        <FullQuoteForm />
      </div>
    </div>
  );
}
