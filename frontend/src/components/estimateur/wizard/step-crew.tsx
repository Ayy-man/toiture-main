"use client";

import { useFormContext } from "react-hook-form";
import {
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
import {
  Card,
  CardHeader,
  CardTitle,
  CardContent,
} from "@/components/ui/card";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Users, MapPin } from "lucide-react";
import { useLanguage } from "@/lib/i18n";
import type { HybridQuoteFormData } from "@/lib/schemas/hybrid-quote";

/**
 * Step 3: Crew - Employee counts, duration, geographic zone, premium level
 */
export function StepCrew() {
  const { t } = useLanguage();
  const form = useFormContext<HybridQuoteFormData>();

  // Watch values for crew total and conditional rendering
  const compagnons = form.watch("employee_compagnons") || 0;
  const apprentis = form.watch("employee_apprentis") || 0;
  const manoeuvres = form.watch("employee_manoeuvres") || 0;
  const totalCrew = compagnons + apprentis + manoeuvres;
  const durationType = form.watch("duration_type");

  return (
    <Card>
      <CardContent className="space-y-6 pt-6">
        {/* Crew & Duration Section */}
        <div className="space-y-4">
          <div className="flex items-center gap-2 pb-2">
            <div className="flex size-7 items-center justify-center rounded-lg bg-primary/10 text-primary">
              <Users className="size-3.5" />
            </div>
            <div className="text-sm font-semibold">{t.fullQuote.crewDuration}</div>
          </div>

          <div>
            <label className="text-sm font-medium mb-3 block">{t.fullQuote.totalCrew}</label>
            <div className="grid grid-cols-3 gap-3">
              <FormField
                control={form.control}
                name="employee_compagnons"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel className="text-xs font-medium">{t.fullQuote.compagnons}</FormLabel>
                    <FormControl>
                      <Input type="number" min={0} max={20} className="h-11" {...field}
                        onChange={(e) => field.onChange(parseInt(e.target.value) || 0)} />
                    </FormControl>
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="employee_apprentis"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel className="text-xs font-medium">{t.fullQuote.apprentis}</FormLabel>
                    <FormControl>
                      <Input type="number" min={0} max={20} className="h-11" {...field}
                        onChange={(e) => field.onChange(parseInt(e.target.value) || 0)} />
                    </FormControl>
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="employee_manoeuvres"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel className="text-xs font-medium">{t.fullQuote.manoeuvres}</FormLabel>
                    <FormControl>
                      <Input type="number" min={0} max={20} className="h-11" {...field}
                        onChange={(e) => field.onChange(parseInt(e.target.value) || 0)} />
                    </FormControl>
                  </FormItem>
                )}
              />
            </div>
            <div className="flex justify-between items-center pt-3 mt-3 border-t border-border/50">
              <span className="text-sm font-medium">{t.fullQuote.totalCrew}</span>
              <span className="text-sm font-semibold text-primary">
                {totalCrew} {t.fullQuote.workers}
              </span>
            </div>
          </div>

          <FormField
            control={form.control}
            name="duration_type"
            render={({ field }) => (
              <FormItem>
                <FormLabel className="text-sm font-medium">{t.fullQuote.projectDuration}</FormLabel>
                <FormControl>
                  <RadioGroup onValueChange={field.onChange} value={field.value} className="space-y-2">
                    <div className="flex items-center space-x-2">
                      <RadioGroupItem value="half_day" id="half_day" />
                      <label htmlFor="half_day" className="text-sm cursor-pointer">{t.fullQuote.halfDay}</label>
                    </div>
                    <div className="flex items-center space-x-2">
                      <RadioGroupItem value="full_day" id="full_day" />
                      <label htmlFor="full_day" className="text-sm cursor-pointer">{t.fullQuote.fullDay}</label>
                    </div>
                    <div className="flex items-center space-x-2">
                      <RadioGroupItem value="multi_day" id="multi_day" />
                      <label htmlFor="multi_day" className="text-sm cursor-pointer">{t.fullQuote.multiDay}</label>
                    </div>
                  </RadioGroup>
                </FormControl>
              </FormItem>
            )}
          />

          {durationType === 'multi_day' && (
            <FormField
              control={form.control}
              name="duration_days"
              render={({ field }) => (
                <FormItem>
                  <FormLabel className="text-sm font-medium">{t.fullQuote.numberOfDays}</FormLabel>
                  <FormControl>
                    <Input type="number" min={2} max={30} placeholder="3" className="h-11 max-w-32" {...field}
                      value={field.value ?? ''} onChange={(e) => field.onChange(e.target.valueAsNumber || undefined)} />
                  </FormControl>
                </FormItem>
              )}
            />
          )}
        </div>

        {/* Location & Client Section */}
        <div className="space-y-4 pt-6 border-t">
          <div className="flex items-center gap-2 pb-2">
            <div className="flex size-7 items-center justify-center rounded-lg bg-primary/10 text-primary">
              <MapPin className="size-3.5" />
            </div>
            <div className="text-sm font-semibold">{t.fullQuote.locationClient}</div>
          </div>

          <FormField
            control={form.control}
            name="geographic_zone"
            render={({ field }) => (
              <FormItem>
                <FormLabel className="text-sm font-medium">{t.fullQuote.geographicZone}</FormLabel>
                <Select onValueChange={field.onChange} value={field.value}>
                  <FormControl>
                    <SelectTrigger className="h-11">
                      <SelectValue placeholder={t.fullQuote.selectZone} />
                    </SelectTrigger>
                  </FormControl>
                  <SelectContent>
                    <SelectItem value="core">{t.fullQuote.zoneCore}</SelectItem>
                    <SelectItem value="secondary">{t.fullQuote.zoneSecondary}</SelectItem>
                    <SelectItem value="north_premium">{t.fullQuote.zoneNorthPremium}</SelectItem>
                    <SelectItem value="extended">{t.fullQuote.zoneExtended}</SelectItem>
                    <SelectItem value="red_flag">{t.fullQuote.zoneRedFlag}</SelectItem>
                  </SelectContent>
                </Select>
                <FormMessage />
              </FormItem>
            )}
          />
          <FormField
            control={form.control}
            name="premium_client_level"
            render={({ field }) => (
              <FormItem>
                <FormLabel className="text-sm font-medium">{t.fullQuote.premiumClientLevel}</FormLabel>
                <Select onValueChange={field.onChange} value={field.value}>
                  <FormControl>
                    <SelectTrigger className="h-11">
                      <SelectValue />
                    </SelectTrigger>
                  </FormControl>
                  <SelectContent>
                    <SelectItem value="standard">
                      {t.fullQuote.premiumStandard} — {t.fullQuote.premiumStandardDesc}
                    </SelectItem>
                    <SelectItem value="premium_1">
                      {t.fullQuote.premium1} — {t.fullQuote.premium1Desc} ({t.fullQuote.surchargeTBD})
                    </SelectItem>
                    <SelectItem value="premium_2">
                      {t.fullQuote.premium2} — {t.fullQuote.premium2Desc} ({t.fullQuote.surchargeTBD})
                    </SelectItem>
                    <SelectItem value="premium_3">
                      {t.fullQuote.premium3} — {t.fullQuote.premium3Desc} ({t.fullQuote.surchargeTBD})
                    </SelectItem>
                  </SelectContent>
                </Select>
                <FormMessage />
              </FormItem>
            )}
          />
        </div>
      </CardContent>
    </Card>
  );
}
