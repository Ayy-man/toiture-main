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

/**
 * Main estimate form component with all 6 input fields
 * Handles form validation, API submission, and result display
 */
export function EstimateForm() {
  const [result, setResult] = useState<EstimateResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isStreamingReasoning, setIsStreamingReasoning] = useState(false);
  const [streamedReasoning, setStreamedReasoning] = useState("");
  const [error, setError] = useState<string | null>(null);

  const form = useForm<EstimateFormData>({
    resolver: zodResolver(estimateFormSchema),
    defaultValues: {
      sqft: 1500,
      category: "Bardeaux",
      material_lines: 5,
      labor_lines: 2,
      has_subs: false,
      complexity: 10,
    },
  });

  async function onSubmit(data: EstimateFormData) {
    setIsLoading(true);
    setError(null);
    setResult(null);
    setStreamedReasoning("");
    setIsStreamingReasoning(false);

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
      setError(err instanceof Error ? err.message : "An error occurred");
      setIsLoading(false);
      setIsStreamingReasoning(false);
    }
  }

  return (
    <div className="space-y-8">
      <Form {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
          {/* Square Footage */}
          <FormField
            control={form.control}
            name="sqft"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Square Footage</FormLabel>
                <FormControl>
                  <Input
                    type="number"
                    placeholder="1500"
                    {...field}
                    onChange={(e) => field.onChange(e.target.valueAsNumber || "")}
                  />
                </FormControl>
                <FormDescription>
                  Total roof area in square feet
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
                <FormLabel>Category</FormLabel>
                <Select
                  onValueChange={field.onChange}
                  defaultValue={field.value}
                >
                  <FormControl>
                    <SelectTrigger>
                      <SelectValue placeholder="Select a category" />
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
                <FormDescription>Type of roofing job</FormDescription>
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
                <FormLabel>Material Lines</FormLabel>
                <FormControl>
                  <Input
                    type="number"
                    placeholder="5"
                    {...field}
                    onChange={(e) => field.onChange(e.target.valueAsNumber || "")}
                  />
                </FormControl>
                <FormDescription>
                  Number of material line items
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
                <FormLabel>Labor Lines</FormLabel>
                <FormControl>
                  <Input
                    type="number"
                    placeholder="2"
                    {...field}
                    onChange={(e) => field.onChange(e.target.valueAsNumber || "")}
                  />
                </FormControl>
                <FormDescription>Number of labor line items</FormDescription>
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
                  <FormLabel className="text-base">Subcontractors</FormLabel>
                  <FormDescription>
                    Will this job involve subcontractors?
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
                <FormLabel>Complexity: {field.value}</FormLabel>
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
                  Job complexity (1 = simple, 100 = very complex)
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
            {isLoading ? "Getting Estimate..." : "Get Estimate"}
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
        </div>
      )}
    </div>
  );
}
