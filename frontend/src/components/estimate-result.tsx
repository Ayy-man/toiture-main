"use client";

import { motion } from "framer-motion";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import type { EstimateResponse } from "@/lib/api";
import { useLanguage } from "@/lib/i18n";
import { AnimatedPrice } from "@/components/estimateur/animated-price";
import { ConfidenceBadge } from "@/components/estimateur/confidence-badge";

interface EstimateResultProps {
  result: EstimateResponse;
}

/**
 * Display the estimate result with amount, range, and confidence
 */
export function EstimateResult({ result }: EstimateResultProps) {
  const { t } = useLanguage();

  // Map confidence string to number (0-1) for ConfidenceBadge
  const confidenceToNumber = (conf: "HIGH" | "MEDIUM" | "LOW"): number => {
    switch (conf) {
      case "HIGH":
        return 0.85;
      case "MEDIUM":
        return 0.55;
      case "LOW":
        return 0.25;
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
    >
      <Card>
        <CardHeader>
          <CardTitle>{t.resultat.estimation}</CardTitle>
          <CardDescription>
            ${result.range_low.toLocaleString()} - $
            {result.range_high.toLocaleString()}
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <AnimatedPrice
            value={result.estimate}
            className="text-4xl font-bold"
          />
          <div className="flex items-center gap-4">
            <ConfidenceBadge confidence={confidenceToNumber(result.confidence)} />
            <span className="text-sm text-muted-foreground">
              {t.resultat.modele}: {result.model}
            </span>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
}
