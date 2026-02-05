"use client";

import Markdown from "react-markdown";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { useLanguage } from "@/lib/i18n";

interface ReasoningDisplayProps {
  reasoning: string | null;
  isStreaming?: boolean;
}

/**
 * Display LLM reasoning in markdown format with streaming support
 */
export function ReasoningDisplay({ reasoning, isStreaming = false }: ReasoningDisplayProps) {
  const { t } = useLanguage();

  // Show card if streaming (even with empty reasoning) or if we have reasoning
  if (!reasoning && !isStreaming) {
    return null;
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          {t.raisonnement.titre}
          {isStreaming && (
            <span className="inline-flex items-center gap-1 text-sm font-normal text-muted-foreground">
              <span className="animate-pulse">●</span>
              {t.raisonnement.enCours}
            </span>
          )}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="prose prose-sm max-w-none dark:prose-invert">
          {reasoning ? (
            <Markdown>{reasoning}</Markdown>
          ) : (
            <p className="text-muted-foreground animate-pulse">
              {t.raisonnement.analyse}
            </p>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
