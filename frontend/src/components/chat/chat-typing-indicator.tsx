"use client";

import { Bot } from "lucide-react";

interface TypingIndicatorProps {
  visible: boolean;
}

export function ChatTypingIndicator({ visible }: TypingIndicatorProps) {
  if (!visible) return null;

  return (
    <div className="flex gap-3 mb-4">
      {/* Avatar */}
      <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-muted">
        <Bot className="h-4 w-4" />
      </div>

      {/* Typing bubble */}
      <div className="flex flex-col gap-1 items-start">
        <div className="rounded-2xl rounded-bl-md bg-muted px-4 py-3">
          <div className="flex gap-1 items-center">
            <span
              className="h-2 w-2 rounded-full bg-foreground/40 animate-bounce"
              style={{ animationDelay: "0s", animationDuration: "1s" }}
            />
            <span
              className="h-2 w-2 rounded-full bg-foreground/40 animate-bounce"
              style={{ animationDelay: "0.15s", animationDuration: "1s" }}
            />
            <span
              className="h-2 w-2 rounded-full bg-foreground/40 animate-bounce"
              style={{ animationDelay: "0.3s", animationDuration: "1s" }}
            />
          </div>
        </div>
      </div>
    </div>
  );
}
