"use client";

import Markdown from "react-markdown";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

interface ReasoningDisplayProps {
  reasoning: string | null;
  isStreaming?: boolean;
}

/**
 * Display LLM reasoning in markdown format with streaming support
 */
export function ReasoningDisplay({ reasoning, isStreaming = false }: ReasoningDisplayProps) {
  // Show card if streaming (even with empty reasoning) or if we have reasoning
  if (!reasoning && !isStreaming) {
    return null;
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          AI Reasoning
          {isStreaming && (
            <span className="inline-flex items-center gap-1 text-sm font-normal text-muted-foreground">
              <span className="animate-pulse">●</span>
              Generating...
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
              Analyzing estimate...
            </p>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
