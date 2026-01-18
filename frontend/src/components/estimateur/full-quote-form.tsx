import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
} from "@/components/ui/card";
import { fr } from "@/lib/i18n/fr";
import { Info } from "lucide-react";

export function FullQuoteForm() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>{fr.estimateur.titreComplet}</CardTitle>
        <CardDescription>{fr.estimateur.descriptionComplet}</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="flex items-start gap-3 rounded-lg bg-amber-50 border border-amber-200 p-4">
          <Info className="h-5 w-5 text-amber-600 mt-0.5 flex-shrink-0" />
          <div>
            <p className="font-medium text-amber-800">
              {fr.estimateur.bientotDisponible}
            </p>
            <p className="text-sm text-amber-700 mt-1">
              {fr.estimateur.fonctionnalitePhase10}
            </p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
