"use client";

import { useEffect, useState } from "react";
import { useSpring, useMotionValueEvent } from "framer-motion";

interface AnimatedPriceProps {
  value: number;
  prefix?: string;
  locale?: string;
  duration?: number;
  className?: string;
}

/**
 * Animated price component with counting effect.
 * Uses framer-motion spring animation to count from 0 to target value.
 */
export function AnimatedPrice({
  value,
  prefix = "$",
  locale = "fr-CA",
  duration = 1.5,
  className = "",
}: AnimatedPriceProps) {
  const [displayValue, setDisplayValue] = useState(0);
  const motionValue = useSpring(0, {
    stiffness: 50,
    damping: 15,
    duration: duration * 1000,
  });

  // Update displayed value on motion value change
  useMotionValueEvent(motionValue, "change", (latest) => {
    setDisplayValue(Math.round(latest));
  });

  // Set target value when value prop changes
  useEffect(() => {
    motionValue.set(value);
  }, [value, motionValue]);

  // Format currency
  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat(locale, {
      style: "currency",
      currency: "CAD",
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  return (
    <span className={className}>
      {formatCurrency(displayValue)}
    </span>
  );
}
