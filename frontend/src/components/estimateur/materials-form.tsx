"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Switch } from "@/components/ui/switch";
import { Slider } from "@/components/ui/slider";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { useLanguage } from "@/lib/i18n";
import { Calculator, Loader2, AlertCircle, Package } from "lucide-react";

const materialsSchema = z.object({
  sqft: z.number().min(100).max(100000),
  category: z.string().min(1),
  complexity: z.number().min(1).max(100),
  has_chimney: z.boolean(),
  has_skylights: z.boolean(),
  material_lines: z.number().min(0).max(100),
  labor_lines: z.number().min(0).max(50),
  has_subs: z.boolean(),
});

type MaterialsFormData = z.infer<typeof materialsSchema>;

interface MaterialPrediction {
  material_id: number;
  quantity: number;
  unit_price: number;
  total: number;
  confidence: "HIGH" | "MEDIUM" | "LOW";
}

interface MaterialsResponse {
  materials: MaterialPrediction[];
  total_materials_cost: number;
  model_info: string;
  applied_rules: string[];
}

const CATEGORIES = [
  { value: "Bardeaux", label: "Bardeaux" },
  { value: "Élastomère", label: "Élastomère" },
  { value: "Other", label: "Autre" },
  { value: "Service Call", label: "Appel de service" },
];

export function MaterialsForm() {
  const { t } = useLanguage();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<MaterialsResponse | null>(null);

  const form = useForm<MaterialsFormData>({
    resolver: zodResolver(materialsSchema),
    defaultValues: {
      sqft: 2500,
      category: "Bardeaux",
      complexity: 50,
      has_chimney: false,
      has_skylights: false,
      material_lines: 10,
      labor_lines: 5,
      has_subs: false,
    },
  });

  const onSubmit = async (data: MaterialsFormData) => {
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/estimate/materials`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(data),
        }
      );

      if (!response.ok) {
        throw new Error(`Erreur ${response.status}`);
      }

      const responseData: MaterialsResponse = await response.json();
      setResult(responseData);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erreur inconnue");
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (value: number) =>
    new Intl.NumberFormat("fr-CA", {
      style: "currency",
      currency: "CAD",
    }).format(value);

  const getConfidenceBadge = (confidence: string) => {
    const colors = {
      HIGH: "bg-green-100 text-green-800",
      MEDIUM: "bg-yellow-100 text-yellow-800",
      LOW: "bg-red-100 text-red-800",
    };
    const labels = {
      HIGH: "Élevée",
      MEDIUM: "Moyenne",
      LOW: "Faible",
    };
    return (
      <span
        className={`px-2 py-1 rounded-full text-xs font-medium ${colors[confidence as keyof typeof colors]}`}
      >
        {labels[confidence as keyof typeof labels]}
      </span>
    );
  };

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Package className="h-5 w-5" />
            {t.estimateur.titreMateriaux}
          </CardTitle>
          <CardDescription>{t.estimateur.descriptionMateriaux}</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
            {/* Main inputs */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="sqft">{t.estimateur.superficie}</Label>
                <Input
                  id="sqft"
                  type="number"
                  {...form.register("sqft", { valueAsNumber: true })}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="category">{t.estimateur.categorie}</Label>
                <Select
                  value={form.watch("category")}
                  onValueChange={(v) => form.setValue("category", v)}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {CATEGORIES.map((cat) => (
                      <SelectItem key={cat.value} value={cat.value}>
                        {cat.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="material_lines">
                  {t.fullQuote.lignesMateriaux}
                </Label>
                <Input
                  id="material_lines"
                  type="number"
                  {...form.register("material_lines", { valueAsNumber: true })}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="labor_lines">
                  {t.fullQuote.lignesMainOeuvre}
                </Label>
                <Input
                  id="labor_lines"
                  type="number"
                  {...form.register("labor_lines", { valueAsNumber: true })}
                />
              </div>
            </div>

            {/* Complexity slider */}
            <div className="space-y-3">
              <div className="flex justify-between">
                <Label>{t.fullQuote.complexite}</Label>
                <span className="text-sm text-muted-foreground">
                  {form.watch("complexity")}
                </span>
              </div>
              <Slider
                value={[form.watch("complexity")]}
                onValueChange={([v]) => form.setValue("complexity", v)}
                min={1}
                max={100}
                step={1}
              />
            </div>

            {/* Toggles */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="flex items-center justify-between rounded-lg border p-3">
                <Label htmlFor="has_chimney" className="cursor-pointer">
                  {t.fullQuote.aCheminee}
                </Label>
                <Switch
                  id="has_chimney"
                  checked={form.watch("has_chimney")}
                  onCheckedChange={(v) => form.setValue("has_chimney", v)}
                />
              </div>

              <div className="flex items-center justify-between rounded-lg border p-3">
                <Label htmlFor="has_skylights" className="cursor-pointer">
                  {t.fullQuote.aLucarnes}
                </Label>
                <Switch
                  id="has_skylights"
                  checked={form.watch("has_skylights")}
                  onCheckedChange={(v) => form.setValue("has_skylights", v)}
                />
              </div>

              <div className="flex items-center justify-between rounded-lg border p-3">
                <Label htmlFor="has_subs" className="cursor-pointer">
                  {t.fullQuote.aSousTraitants}
                </Label>
                <Switch
                  id="has_subs"
                  checked={form.watch("has_subs")}
                  onCheckedChange={(v) => form.setValue("has_subs", v)}
                />
              </div>
            </div>

            {/* Error message */}
            {error && (
              <div className="flex items-center gap-2 rounded-lg bg-red-50 border border-red-200 p-3 text-red-700">
                <AlertCircle className="h-5 w-5" />
                <span>{error}</span>
              </div>
            )}

            {/* Submit button */}
            <Button type="submit" disabled={loading} className="w-full">
              {loading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Calcul en cours...
                </>
              ) : (
                <>
                  <Calculator className="mr-2 h-4 w-4" />
                  Calculer les matériaux
                </>
              )}
            </Button>
          </form>
        </CardContent>
      </Card>

      {/* Results */}
      {result && (
        <Card>
          <CardHeader>
            <CardTitle>Matériaux prédits</CardTitle>
            <CardDescription>{result.model_info}</CardDescription>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>ID Matériau</TableHead>
                  <TableHead className="text-right">Quantité</TableHead>
                  <TableHead className="text-right">Prix unitaire</TableHead>
                  <TableHead className="text-right">Total</TableHead>
                  <TableHead className="text-center">Confiance</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {result.materials.map((mat) => (
                  <TableRow key={mat.material_id}>
                    <TableCell className="font-mono">
                      #{mat.material_id}
                    </TableCell>
                    <TableCell className="text-right tabular-nums">
                      {mat.quantity.toFixed(2)}
                    </TableCell>
                    <TableCell className="text-right tabular-nums">
                      {formatCurrency(mat.unit_price)}
                    </TableCell>
                    <TableCell className="text-right tabular-nums font-medium">
                      {formatCurrency(mat.total)}
                    </TableCell>
                    <TableCell className="text-center">
                      {getConfidenceBadge(mat.confidence)}
                    </TableCell>
                  </TableRow>
                ))}
                <TableRow className="bg-muted/50 font-bold">
                  <TableCell colSpan={3}>Coût total des matériaux</TableCell>
                  <TableCell className="text-right tabular-nums">
                    {formatCurrency(result.total_materials_cost)}
                  </TableCell>
                  <TableCell />
                </TableRow>
              </TableBody>
            </Table>

            {result.applied_rules.length > 0 && (
              <div className="mt-4 p-3 bg-blue-50 rounded-lg">
                <p className="text-sm font-medium text-blue-800 mb-2">
                  Règles appliquées:
                </p>
                <ul className="text-sm text-blue-700 list-disc list-inside">
                  {result.applied_rules.map((rule, i) => (
                    <li key={i}>{rule}</li>
                  ))}
                </ul>
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
