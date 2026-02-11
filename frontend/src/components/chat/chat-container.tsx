"use client";

import { useState, useRef, useEffect } from "react";
import { RotateCcw } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useLanguage } from "@/lib/i18n";
import { ChatMessage } from "./chat-message";
import { ChatInput } from "./chat-input";
import { SuggestionPills } from "./suggestion-pills";
import { ChatTypingIndicator } from "./chat-typing-indicator";

export interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: string;
}

export function ChatContainer() {
  const { t } = useLanguage();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Local state - no API calls (Plan 03 will add backend integration)
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "greeting",
      role: "assistant",
      content: t.chat.greeting,
      timestamp: new Date().toLocaleTimeString("fr-CA", { hour: "2-digit", minute: "2-digit" }),
    },
  ]);

  const [suggestions, setSuggestions] = useState<string[]>([
    "1200 pi2, bardeaux, pente raide",
    "2000 pi2, TPO, toit plat commercial",
    "800 pi2, reparation urgente, fuites",
  ]);

  const [isLoading, setIsLoading] = useState(false);
  const [sessionState, setSessionState] = useState("greeting");

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages.length]);

  const handleSend = (content: string) => {
    // Add user message
    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content,
      timestamp: new Date().toLocaleTimeString("fr-CA", { hour: "2-digit", minute: "2-digit" }),
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);
    setSuggestions([]); // Clear suggestions while processing

    // Mock assistant reply (Plan 03 will replace with API call)
    setTimeout(() => {
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: `J'ai compris: **${content}**. (Integration API en attente)`,
        timestamp: new Date().toLocaleTimeString("fr-CA", { hour: "2-digit", minute: "2-digit" }),
      };

      setMessages((prev) => [...prev, assistantMessage]);
      setIsLoading(false);
      setSessionState("collecting");

      // Show new suggestions after reply
      setSuggestions(["Oui, continuer", "Non, recommencer", "Plus d'options"]);
    }, 1000);
  };

  const handleSuggestionSelect = (suggestion: string) => {
    handleSend(suggestion);
  };

  const handleNewChat = () => {
    setMessages([
      {
        id: "greeting",
        role: "assistant",
        content: t.chat.greeting,
        timestamp: new Date().toLocaleTimeString("fr-CA", { hour: "2-digit", minute: "2-digit" }),
      },
    ]);
    setSuggestions([
      "1200 pi2, bardeaux, pente raide",
      "2000 pi2, TPO, toit plat commercial",
      "800 pi2, reparation urgente, fuites",
    ]);
    setSessionState("greeting");
  };

  return (
    <div className="flex flex-col h-[calc(100vh-4rem)]">
      {/* Fixed Header */}
      <div className="flex items-center justify-between border-b px-4 py-3 bg-background shrink-0">
        <div className="flex items-center gap-3">
          <h1 className="text-lg font-semibold">{t.chat.title}</h1>
          <Badge variant="outline" className="text-xs">
            {t.chat.sessionState}: {sessionState}
          </Badge>
        </div>
        <Button
          variant="ghost"
          size="sm"
          onClick={handleNewChat}
          className="gap-2"
        >
          <RotateCcw className="h-4 w-4" />
          {t.chat.newChat}
        </Button>
      </div>

      {/* Scrollable Message List */}
      <div className="flex-1 overflow-y-auto px-4 py-4">
        {messages.map((message) => (
          <ChatMessage
            key={message.id}
            role={message.role}
            content={message.content}
            timestamp={message.timestamp}
          />
        ))}

        {/* Typing Indicator */}
        <ChatTypingIndicator visible={isLoading} />

        {/* Auto-scroll anchor */}
        <div ref={messagesEndRef} />
      </div>

      {/* Suggestion Pills (above input) */}
      {suggestions.length > 0 && (
        <div className="px-4 py-2 shrink-0">
          <SuggestionPills
            suggestions={suggestions}
            onSelect={handleSuggestionSelect}
            disabled={isLoading}
          />
        </div>
      )}

      {/* Fixed Input */}
      <div className="px-4 py-3 border-t bg-background shrink-0">
        <ChatInput
          onSend={handleSend}
          disabled={isLoading}
          placeholder={t.chat.placeholder}
        />
      </div>
    </div>
  );
}
