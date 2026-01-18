import { fr } from "@/lib/i18n/fr";
import { EstimateForm } from "@/components/estimate-form";

export default function EstimateurPage() {
  return (
    <div className="max-w-2xl">
      <h1 className="text-3xl font-bold tracking-tight mb-6">
        {fr.nav.estimateur}
      </h1>
      <EstimateForm />
    </div>
  );
}
