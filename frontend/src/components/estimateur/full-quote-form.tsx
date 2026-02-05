"use client";

import { useState } from "react";
import { useForm, Controller } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
  FormDescription,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Switch } from "@/components/ui/switch";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
} from "@/components/ui/card";
import { ComplexityPresets } from "./complexity-presets";
import { QuoteResult } from "./quote-result";
import {
  hybridQuoteFormSchema,
  type HybridQuoteFormData,
} from "@/lib/schemas/hybrid-quote";
import { submitHybridQuote } from "@/lib/api/hybrid-quote";
import type { HybridQuoteResponse, HybridQuoteRequest } from "@/types/hybrid-quote";
import { CATEGORIES } from "@/lib/schemas";
import { useLanguage } from "@/lib/i18n";
import { Loader2, Calculator, Layers, Wrench, AlertCircle } from "lucide-react";

/**
 * Full quote form with complexity presets and invoice-style result display.
 * Submits to /estimate/hybrid endpoint with 6 complexity factors.
 */
export function FullQuoteForm() {
  const { t } = useLanguage();
  const [result, setResult] = useState<HybridQuoteResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Form setup with Modere preset defaults
  const form = useForm<HybridQuoteFormData>({
    resolver: zodResolver(hybridQuoteFormSchema),
    defaultValues: {
      sqft: 1500,
      category: "Bardeaux",
      // Modere preset values
      complexity_aggregate: 28, // Sum of Modere factors
      access_difficulty: 5,
      roof_pitch: 4,
      penetrations: 5,
      material_removal: 4,
      safety_concerns: 5,
      timeline_constraints: 5,
      material_lines: 5,
      labor_lines: 2,
      has_chimney: false,
      has_skylights: false,
      has_subs: false,
    },
  });

  // Watch sqft and category for QuoteResult props
  const sqft = form.watch("sqft");
  const category = form.watch("category");

  /**
   * Handle form submission.
   * Computes complexity_aggregate and submits to hybrid quote endpoint.
   */
  async function onSubmit(data: HybridQuoteFormData) {
    setIsLoading(true);
    setError(null);
    setResult(null);

    try {
      // Build request payload
      const request: HybridQuoteRequest = {
        sqft: data.sqft,
        category: data.category,
        complexity_aggregate: data.complexity_aggregate,
        access_difficulty: data.access_difficulty,
        roof_pitch: data.roof_pitch,
        penetrations: data.penetrations,
        material_removal: data.material_removal,
        safety_concerns: data.safety_concerns,
        timeline_constraints: data.timeline_constraints,
        has_chimney: data.has_chimney,
        has_skylights: data.has_skylights,
        material_lines: data.material_lines,
        labor_lines: data.labor_lines,
        has_subs: data.has_subs,
        quoted_total: data.quoted_total,
      };

      // Submit to API
      const response = await submitHybridQuote(request);
      setResult(response);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : t.fullQuote.erreur
      );
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="space-y-6 max-w-3xl">
      <Form {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
          {/* Project Details Section */}
          <Card className="card-hover">
            <CardHeader className="pb-4">
              <div className="flex items-center gap-2">
                <div className="flex size-8 items-center justify-center rounded-lg bg-primary/10 text-primary">
                  <Calculator className="size-4" />
                </div>
                <div>
                  <CardTitle className="text-lg">{t.fullQuote.titre}</CardTitle>
                  <CardDescription className="text-sm">{t.fullQuote.description}</CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Primary inputs - side by side on larger screens */}
              <div className="grid gap-4 sm:grid-cols-2">
                {/* Square Footage */}
                <FormField
                  control={form.control}
                  name="sqft"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel className="text-sm font-medium">{t.estimateur.superficie}</FormLabel>
                      <FormControl>
                        <Input
                          type="number"
                          placeholder="1500"
                          className="h-11"
                          {...field}
                          onChange={(e) =>
                            field.onChange(e.target.valueAsNumber || "")
                          }
                        />
                      </FormControl>
                      <FormDescription className="text-xs text-muted-foreground">
                        {t.fullQuote.superficieDescription}
                      </FormDescription>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                {/* Category */}
                <FormField
                  control={form.control}
                  name="category"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel className="text-sm font-medium">{t.estimateur.categorie}</FormLabel>
                      <Select
                        onValueChange={field.onChange}
                        defaultValue={field.value}
                      >
                        <FormControl>
                          <SelectTrigger className="h-11">
                            <SelectValue placeholder={t.fullQuote.categoriePlaceholder} />
                          </SelectTrigger>
                        </FormControl>
                        <SelectContent>
                          {CATEGORIES.map((cat) => (
                            <SelectItem key={cat} value={cat}>
                              {cat}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                      <FormDescription className="text-xs text-muted-foreground">
                        {t.fullQuote.categorieDescription}
                      </FormDescription>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </div>

              {/* Secondary inputs - material and labor lines */}
              <div className="grid gap-4 sm:grid-cols-2">
                {/* Material Lines */}
                <FormField
                  control={form.control}
                  name="material_lines"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel className="text-sm font-medium">{t.fullQuote.lignesMateriaux}</FormLabel>
                      <FormControl>
                        <Input
                          type="number"
                          placeholder="5"
                          className="h-11"
                          {...field}
                          onChange={(e) =>
                            field.onChange(e.target.valueAsNumber || "")
                          }
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                {/* Labor Lines */}
                <FormField
                  control={form.control}
                  name="labor_lines"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel className="text-sm font-medium">{t.fullQuote.lignesMainOeuvre}</FormLabel>
                      <FormControl>
                        <Input
                          type="number"
                          placeholder="2"
                          className="h-11"
                          {...field}
                          onChange={(e) =>
                            field.onChange(e.target.valueAsNumber || "")
                          }
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </div>
            </CardContent>
          </Card>

          {/* Complexity Section */}
          <Card className="card-hover">
            <CardHeader className="pb-4">
              <div className="flex items-center gap-2">
                <div className="flex size-8 items-center justify-center rounded-lg bg-primary/10 text-primary">
                  <Layers className="size-4" />
                </div>
                <div>
                  <CardTitle className="text-lg">{t.fullQuote.complexiteProjet}</CardTitle>
                  <CardDescription className="text-sm">
                    {t.fullQuote.complexiteDescription}
                  </CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              {/* Complexity Presets with Controller */}
              <Controller
                control={form.control}
                name="access_difficulty"
                render={() => (
                  <ComplexityPresets
                    value={{
                      preset: null, // Will be determined by matching values
                      access_difficulty: form.watch("access_difficulty"),
                      roof_pitch: form.watch("roof_pitch"),
                      penetrations: form.watch("penetrations"),
                      material_removal: form.watch("material_removal"),
                      safety_concerns: form.watch("safety_concerns"),
                      timeline_constraints: form.watch("timeline_constraints"),
                    }}
                    onChange={(value) => {
                      // Update all 6 factors and aggregate
                      form.setValue("access_difficulty", value.access_difficulty);
                      form.setValue("roof_pitch", value.roof_pitch);
                      form.setValue("penetrations", value.penetrations);
                      form.setValue("material_removal", value.material_removal);
                      form.setValue("safety_concerns", value.safety_concerns);
                      form.setValue("timeline_constraints", value.timeline_constraints);

                      // Compute aggregate
                      const aggregate =
                        value.access_difficulty +
                        value.roof_pitch +
                        value.penetrations +
                        value.material_removal +
                        value.safety_concerns +
                        value.timeline_constraints;
                      form.setValue("complexity_aggregate", aggregate);
                    }}
                  />
                )}
              />
            </CardContent>
          </Card>

          {/* Features Section */}
          <Card className="card-hover">
            <CardHeader className="pb-4">
              <div className="flex items-center gap-2">
                <div className="flex size-8 items-center justify-center rounded-lg bg-primary/10 text-primary">
                  <Wrench className="size-4" />
                </div>
                <div>
                  <CardTitle className="text-lg">{t.fullQuote.caracteristiques}</CardTitle>
                  <CardDescription className="text-sm">
                    {t.fullQuote.caracteristiquesDescription}
                  </CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-3">
              {/* Has Chimney */}
              <FormField
                control={form.control}
                name="has_chimney"
                render={({ field }) => (
                  <FormItem className="flex items-center justify-between rounded-lg border border-border/50 bg-muted/30 p-4 transition-colors hover:bg-muted/50">
                    <div className="space-y-0.5">
                      <FormLabel className="text-sm font-medium cursor-pointer">
                        {t.fullQuote.aCheminee}
                      </FormLabel>
                      <FormDescription className="text-xs text-muted-foreground">
                        {t.fullQuote.chemineeDescription}
                      </FormDescription>
                    </div>
                    <FormControl>
                      <Switch
                        checked={field.value}
                        onCheckedChange={field.onChange}
                      />
                    </FormControl>
                  </FormItem>
                )}
              />

              {/* Has Skylights */}
              <FormField
                control={form.control}
                name="has_skylights"
                render={({ field }) => (
                  <FormItem className="flex items-center justify-between rounded-lg border border-border/50 bg-muted/30 p-4 transition-colors hover:bg-muted/50">
                    <div className="space-y-0.5">
                      <FormLabel className="text-sm font-medium cursor-pointer">
                        {t.fullQuote.aLucarnes}
                      </FormLabel>
                      <FormDescription className="text-xs text-muted-foreground">
                        {t.fullQuote.lucarnesDescription}
                      </FormDescription>
                    </div>
                    <FormControl>
                      <Switch
                        checked={field.value}
                        onCheckedChange={field.onChange}
                      />
                    </FormControl>
                  </FormItem>
                )}
              />

              {/* Has Subcontractors */}
              <FormField
                control={form.control}
                name="has_subs"
                render={({ field }) => (
                  <FormItem className="flex items-center justify-between rounded-lg border border-border/50 bg-muted/30 p-4 transition-colors hover:bg-muted/50">
                    <div className="space-y-0.5">
                      <FormLabel className="text-sm font-medium cursor-pointer">
                        {t.fullQuote.aSousTraitants}
                      </FormLabel>
                      <FormDescription className="text-xs text-muted-foreground">
                        {t.fullQuote.sousTraitantsDescription}
                      </FormDescription>
                    </div>
                    <FormControl>
                      <Switch
                        checked={field.value}
                        onCheckedChange={field.onChange}
                      />
                    </FormControl>
                  </FormItem>
                )}
              />
            </CardContent>
          </Card>

          {/* Error Display */}
          {error && (
            <div className="flex items-center gap-2 rounded-lg border border-destructive/50 bg-destructive/10 p-4 text-destructive">
              <AlertCircle className="size-5 shrink-0" />
              <p className="text-sm font-medium">{error}</p>
            </div>
          )}

          {/* Submit Button */}
          <Button
            type="submit"
            size="lg"
            className="w-full h-12 text-base font-semibold"
            disabled={isLoading}
          >
            {isLoading ? (
              <>
                <Loader2 className="mr-2 size-5 animate-spin" />
                {t.fullQuote.enChargement}
              </>
            ) : (
              <>
                <Calculator className="mr-2 size-5" />
                {t.fullQuote.generer}
              </>
            )}
          </Button>
        </form>
      </Form>

      {/* Quote Result Display */}
      {result && (
        <QuoteResult
          quote={result}
          category={category}
          sqft={sqft}
          inputParams={form.getValues()}
        />
      )}
    </div>
  );
}
