"use client";

import { useFormContext } from "react-hook-form";
import {
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
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
} from "@/components/ui/card";
import { Calculator } from "lucide-react";
import { CATEGORIES } from "@/lib/schemas";
import { useLanguage } from "@/lib/i18n";
import type { HybridQuoteFormData } from "@/lib/schemas/hybrid-quote";

/**
 * Step 1: Basics - Project Details
 * Estimator, sqft, category, material/labor lines, client name, features
 */
export function StepBasics() {
  const { t } = useLanguage();
  const form = useFormContext<HybridQuoteFormData>();

  return (
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
        {/* Estimator Dropdown */}
        <FormField
          control={form.control}
          name="created_by"
          render={({ field }) => (
            <FormItem>
              <FormLabel className="text-sm font-medium">{t.estimateur.estimateurNom}</FormLabel>
              <Select
                onValueChange={field.onChange}
                value={field.value}
              >
                <FormControl>
                  <SelectTrigger className="h-11">
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

        {/* Client Name */}
        <FormField
          control={form.control}
          name="created_by"
          render={({ field }) => (
            <FormItem>
              <FormLabel className="text-sm font-medium">{t.submission.clientName}</FormLabel>
              <FormControl>
                <Input
                  type="text"
                  placeholder={t.submission.clientNamePlaceholder}
                  className="h-11"
                  {...field}
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        {/* Features Section */}
        <div className="space-y-3 pt-4 border-t">
          <div className="text-sm font-medium">{t.fullQuote.caracteristiques}</div>

          <FormField
            control={form.control}
            name="has_chimney"
            render={({ field }) => (
              <FormItem className="flex items-center justify-between rounded-lg border border-border/50 bg-muted/30 p-4 transition-colors hover:bg-muted/50">
                <div className="space-y-0.5">
                  <FormLabel className="text-sm font-medium cursor-pointer">{t.fullQuote.aCheminee}</FormLabel>
                  <FormDescription className="text-xs text-muted-foreground">{t.fullQuote.chemineeDescription}</FormDescription>
                </div>
                <FormControl>
                  <Switch checked={field.value} onCheckedChange={field.onChange} />
                </FormControl>
              </FormItem>
            )}
          />
          <FormField
            control={form.control}
            name="has_skylights"
            render={({ field }) => (
              <FormItem className="flex items-center justify-between rounded-lg border border-border/50 bg-muted/30 p-4 transition-colors hover:bg-muted/50">
                <div className="space-y-0.5">
                  <FormLabel className="text-sm font-medium cursor-pointer">{t.fullQuote.aLucarnes}</FormLabel>
                  <FormDescription className="text-xs text-muted-foreground">{t.fullQuote.lucarnesDescription}</FormDescription>
                </div>
                <FormControl>
                  <Switch checked={field.value} onCheckedChange={field.onChange} />
                </FormControl>
              </FormItem>
            )}
          />
          <FormField
            control={form.control}
            name="has_subs"
            render={({ field }) => (
              <FormItem className="flex items-center justify-between rounded-lg border border-border/50 bg-muted/30 p-4 transition-colors hover:bg-muted/50">
                <div className="space-y-0.5">
                  <FormLabel className="text-sm font-medium cursor-pointer">{t.fullQuote.aSousTraitants}</FormLabel>
                  <FormDescription className="text-xs text-muted-foreground">{t.fullQuote.sousTraitantsDescription}</FormDescription>
                </div>
                <FormControl>
                  <Switch checked={field.value} onCheckedChange={field.onChange} />
                </FormControl>
              </FormItem>
            )}
          />
        </div>
      </CardContent>
    </Card>
  );
}
