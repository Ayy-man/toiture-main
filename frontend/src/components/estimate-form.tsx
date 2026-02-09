"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import {
  Form,
  FormControl,
  FormDescription,
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
import { Slider } from "@/components/ui/slider";
import { Switch } from "@/components/ui/switch";
import { Button } from "@/components/ui/button";
import {
  estimateFormSchema,
  type EstimateFormData,
  CATEGORIES,
} from "@/lib/schemas";
import { submitEstimateStream, type EstimateResponse } from "@/lib/api";
import { EstimateResult } from "@/components/estimate-result";
import { SimilarCases } from "@/components/similar-cases";
import { ReasoningDisplay } from "@/components/reasoning-display";
import { FeedbackPanel } from "@/components/estimateur/feedback-panel";
import { useLanguage } from "@/lib/i18n";

/**
 * Main estimate form component with all 6 input fields
 * Handles form validation, API submission, and result display
 */
export function EstimateForm() {
  const { t } = useLanguage();
  const [result, setResult] = useState<EstimateResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isStreamingReasoning, setIsStreamingReasoning] = useState(false);
  const [streamedReasoning, setStreamedReasoning] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [estimateId, setEstimateId] = useState<string>("");
  const [submittedParams, setSubmittedParams] = useState<EstimateFormData | null>(null);

  const form = useForm<EstimateFormData>({
    resolver: zodResolver(estimateFormSchema),
    defaultValues: {
      sqft: 1500,
      category: "Bardeaux",
      material_lines: 5,
      labor_lines: 2,
      has_subs: false,
      complexity: 10,
      created_by: undefined,
    },
  });

  async function onSubmit(data: EstimateFormData) {
    setIsLoading(true);
    setError(null);
    setResult(null);
    setStreamedReasoning("");
    setIsStreamingReasoning(false);
    setEstimateId(crypto.randomUUID());
    setSubmittedParams(data);

    try {
      await submitEstimateStream(data, {
        onEstimate: (estimateData) => {
          // Show estimate immediately
          setResult({
            ...estimateData,
            reasoning: null,
          });
          setIsLoading(false);
          setIsStreamingReasoning(true);
        },
        onReasoningChunk: (chunk) => {
          setStreamedReasoning((prev) => prev + chunk);
        },
        onDone: (reasoning) => {
          setIsStreamingReasoning(false);
          if (reasoning) {
            setResult((prev) => prev ? { ...prev, reasoning } : null);
          }
        },
        onError: (errorMsg) => {
          setError(errorMsg);
          setIsLoading(false);
          setIsStreamingReasoning(false);
        },
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : t.estimateur.erreurGenerique);
      setIsLoading(false);
      setIsStreamingReasoning(false);
    }
  }

  return (
    <div className="space-y-8">
      <Form {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
          {/* Estimator Dropdown */}
          <FormField
            control={form.control}
            name="created_by"
            render={({ field }) => (
              <FormItem>
                <FormLabel>{t.estimateur.estimateurNom}</FormLabel>
                <Select
                  onValueChange={field.onChange}
                  value={field.value}
                >
                  <FormControl>
                    <SelectTrigger>
                      <SelectValue placeholder={t.estimateur.selectEstimateur} />
                    </SelectTrigger>
                  </FormControl>
                  <SelectContent>
                    <SelectItem value="Steven">Steven</SelectItem>
                    <SelectItem value="Laurent">Laurent</SelectItem>
                    <SelectItem value="Autre">{t.estimateur.autre}</SelectItem>
                  </SelectContent>
                </Select>
                <FormMessage />
              </FormItem>
            )}
          />

          {/* Square Footage */}
          <FormField
            control={form.control}
            name="sqft"
            render={({ field }) => (
              <FormItem>
                <FormLabel>{t.estimateur.superficieTotale}</FormLabel>
                <FormControl>
                  <Input
                    type="number"
                    placeholder="1500"
                    {...field}
                    onChange={(e) => field.onChange(e.target.valueAsNumber || "")}
                  />
                </FormControl>
                <FormDescription>
                  {t.estimateur.superficieDescription}
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
                <FormLabel>{t.estimateur.categorie}</FormLabel>
                <Select
                  onValueChange={field.onChange}
                  defaultValue={field.value}
                >
                  <FormControl>
                    <SelectTrigger>
                      <SelectValue placeholder={t.estimateur.selectCategorie} />
                    </SelectTrigger>
                  </FormControl>
                  <SelectContent>
                    {CATEGORIES.map((category) => (
                      <SelectItem key={category} value={category}>
                        {category}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                <FormDescription>{t.estimateur.typeToiture}</FormDescription>
                <FormMessage />
              </FormItem>
            )}
          />

          {/* Material Lines */}
          <FormField
            control={form.control}
            name="material_lines"
            render={({ field }) => (
              <FormItem>
                <FormLabel>{t.estimateur.lignesMateriaux}</FormLabel>
                <FormControl>
                  <Input
                    type="number"
                    placeholder="5"
                    {...field}
                    onChange={(e) => field.onChange(e.target.valueAsNumber || "")}
                  />
                </FormControl>
                <FormDescription>
                  {t.estimateur.nbLignesMateriaux}
                </FormDescription>
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
                <FormLabel>{t.estimateur.lignesMainOeuvre}</FormLabel>
                <FormControl>
                  <Input
                    type="number"
                    placeholder="2"
                    {...field}
                    onChange={(e) => field.onChange(e.target.valueAsNumber || "")}
                  />
                </FormControl>
                <FormDescription>{t.estimateur.nbLignesMainOeuvre}</FormDescription>
                <FormMessage />
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
                  <FormLabel className="text-base">{t.estimateur.sousTraitants}</FormLabel>
                  <FormDescription>
                    {t.estimateur.sousTraitantsQuestion}
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

          {/* Complexity */}
          <FormField
            control={form.control}
            name="complexity"
            render={({ field }) => (
              <FormItem>
                <FormLabel>{t.estimateur.complexiteLabel}: {field.value}</FormLabel>
                <FormControl>
                  <Slider
                    min={1}
                    max={100}
                    step={1}
                    value={[field.value]}
                    onValueChange={(vals) => field.onChange(vals[0])}
                  />
                </FormControl>
                <FormDescription>
                  {t.estimateur.complexiteDescription}
                </FormDescription>
                <FormMessage />
              </FormItem>
            )}
          />

          {/* Error Display */}
          {error && (
            <p className="text-sm font-medium text-destructive">{error}</p>
          )}

          {/* Submit Button */}
          <Button type="submit" className="w-full" disabled={isLoading}>
            {isLoading ? t.estimateur.obtenirEnCours : t.estimateur.obtenirEstimation}
          </Button>
        </form>
      </Form>

      {/* Results Display */}
      {result && (
        <div className="space-y-6">
          <EstimateResult result={result} />
          <SimilarCases cases={result.similar_cases} />
          <ReasoningDisplay
            reasoning={streamedReasoning || result.reasoning}
            isStreaming={isStreamingReasoning}
          />
          {/* Feedback Panel */}
          <FeedbackPanel
            estimateId={estimateId}
            inputParams={submittedParams || {}}
            predictedPrice={result.estimate}
            predictedMaterials={null}
          />
        </div>
      )}
    </div>
  );
}
