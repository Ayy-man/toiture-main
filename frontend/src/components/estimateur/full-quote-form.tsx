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
import { fr } from "@/lib/i18n/fr";

/**
 * Full quote form with complexity presets and invoice-style result display.
 * Submits to /estimate/hybrid endpoint with 6 complexity factors.
 */
export function FullQuoteForm() {
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
        err instanceof Error ? err.message : fr.fullQuote.erreur
      );
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>{fr.fullQuote.titre}</CardTitle>
          <CardDescription>{fr.fullQuote.description}</CardDescription>
        </CardHeader>
        <CardContent>
          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
              {/* Square Footage */}
              <FormField
                control={form.control}
                name="sqft"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>{fr.estimateur.superficie}</FormLabel>
                    <FormControl>
                      <Input
                        type="number"
                        placeholder="1500"
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

              {/* Category */}
              <FormField
                control={form.control}
                name="category"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>{fr.estimateur.categorie}</FormLabel>
                    <Select
                      onValueChange={field.onChange}
                      defaultValue={field.value}
                    >
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue placeholder="Selectionnez une categorie" />
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
                    <FormMessage />
                  </FormItem>
                )}
              />

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

              {/* Material Lines */}
              <FormField
                control={form.control}
                name="material_lines"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>{fr.fullQuote.lignesMateriaux}</FormLabel>
                    <FormControl>
                      <Input
                        type="number"
                        placeholder="5"
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
                    <FormLabel>{fr.fullQuote.lignesMainOeuvre}</FormLabel>
                    <FormControl>
                      <Input
                        type="number"
                        placeholder="2"
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

              {/* Has Chimney */}
              <FormField
                control={form.control}
                name="has_chimney"
                render={({ field }) => (
                  <FormItem className="flex flex-row items-center justify-between rounded-lg border p-4">
                    <div className="space-y-0.5">
                      <FormLabel className="text-base">
                        {fr.fullQuote.aCheminee}
                      </FormLabel>
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
                  <FormItem className="flex flex-row items-center justify-between rounded-lg border p-4">
                    <div className="space-y-0.5">
                      <FormLabel className="text-base">
                        {fr.fullQuote.aLucarnes}
                      </FormLabel>
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
                  <FormItem className="flex flex-row items-center justify-between rounded-lg border p-4">
                    <div className="space-y-0.5">
                      <FormLabel className="text-base">
                        {fr.fullQuote.aSousTraitants}
                      </FormLabel>
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

              {/* Error Display */}
              {error && (
                <p className="text-sm font-medium text-destructive">{error}</p>
              )}

              {/* Submit Button */}
              <Button type="submit" className="w-full" disabled={isLoading}>
                {isLoading ? fr.fullQuote.enChargement : fr.fullQuote.generer}
              </Button>
            </form>
          </Form>
        </CardContent>
      </Card>

      {/* Quote Result Display */}
      {result && (
        <QuoteResult quote={result} category={category} sqft={sqft} />
      )}
    </div>
  );
}
