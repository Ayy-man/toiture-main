"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { ChevronDown } from "lucide-react";
import Markdown from "react-markdown";
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible";
import { cn } from "@/lib/utils";
import { useLanguage } from "@/lib/i18n";

interface ReasoningDisplayProps {
  reasoning: string | null;
  isStreaming?: boolean;
  processingTime?: number; // in seconds
}

/**
 * Collapsible AI reasoning display with streaming animation.
 * Auto-expands while streaming, shows processing time.
 */
export function ReasoningDisplay({
  reasoning,
  isStreaming = false,
  processingTime,
}: ReasoningDisplayProps) {
  const { t } = useLanguage();
  const [isOpen, setIsOpen] = useState(isStreaming);

  // Auto-expand when streaming starts
  useEffect(() => {
    if (isStreaming) {
      setIsOpen(true);
    }
  }, [isStreaming]);

  // Show component if streaming or if we have reasoning
  if (!reasoning && !isStreaming) {
    return null;
  }

  return (
    <Collapsible open={isOpen} onOpenChange={setIsOpen}>
      <CollapsibleTrigger className="w-full flex items-center justify-between rounded-lg border p-4 hover:bg-accent/50 transition-colors">
        <div className="flex items-center gap-3">
          <span className="font-medium">
            {t.raisonnement.titre}
          </span>
          {isStreaming && (
            <div className="flex items-center gap-1">
              {[0, 1, 2].map((i) => (
                <motion.span
                  key={i}
                  className="inline-block h-2 w-2 rounded-full bg-primary"
                  animate={{ opacity: [0.3, 1, 0.3] }}
                  transition={{ duration: 1, repeat: Infinity, delay: i * 0.2 }}
                />
              ))}
            </div>
          )}
          {processingTime && !isStreaming && (
            <span className="text-xs text-muted-foreground">
              {t.fullQuote.analyzedIn.replace(
                "{seconds}",
                processingTime.toFixed(1)
              )}
            </span>
          )}
        </div>
        <ChevronDown
          className={cn(
            "h-4 w-4 transition-transform duration-200",
            isOpen && "rotate-180"
          )}
        />
      </CollapsibleTrigger>
      <CollapsibleContent className="pt-3">
        <div className="prose prose-sm max-w-none dark:prose-invert border rounded-lg p-4 bg-muted/30">
          {reasoning ? (
            <Markdown>{reasoning}</Markdown>
          ) : (
            <p className="text-muted-foreground animate-pulse">
              {t.raisonnement.analyse}
            </p>
          )}
        </div>
      </CollapsibleContent>
    </Collapsible>
  );
}
