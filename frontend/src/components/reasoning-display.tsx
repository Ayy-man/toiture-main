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
}

/**
 * Display LLM reasoning in markdown format
 */
export function ReasoningDisplay({ reasoning }: ReasoningDisplayProps) {
  if (!reasoning) {
    return null;
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>AI Reasoning</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="prose prose-sm max-w-none dark:prose-invert">
          <Markdown>{reasoning}</Markdown>
        </div>
      </CardContent>
    </Card>
  );
}
