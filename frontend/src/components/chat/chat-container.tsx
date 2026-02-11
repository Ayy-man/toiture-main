"use client";

import { useState, useRef, useEffect } from "react";
import { RotateCcw, ChevronDown, ChevronUp } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible";
import { useLanguage } from "@/lib/i18n";
import { ChatMessage } from "./chat-message";
import { ChatInput } from "./chat-input";
import { SuggestionPills } from "./suggestion-pills";
import { ChatTypingIndicator } from "./chat-typing-indicator";
import { QuoteSummaryCard } from "./quote-summary-card";
import { sendChatMessage, resetChatSession, generateSessionId } from "@/lib/api/chat";
import { createSubmission } from "@/lib/api/submissions";
import type { HybridQuoteResponseData } from "@/types/chat";
import type { HybridQuoteRequest } from "@/types/hybrid-quote";
import { useToast } from "@/hooks/use-toast";

export interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: string;
  quote?: HybridQuoteResponseData; // Present when quote is embedded in this message
}

export function ChatContainer() {
  const { t, locale } = useLanguage();
  const { toast } = useToast();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Session state
  const [sessionId] = useState(() => generateSessionId());
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
  const [extractedFields, setExtractedFields] = useState<Record<string, unknown>>({});
  const [currentQuote, setCurrentQuote] = useState<HybridQuoteResponseData | null>(null);
  const [selectedTier, setSelectedTier] = useState<"Basic" | "Standard" | "Premium" | undefined>();
  const [isCreatingSubmission, setIsCreatingSubmission] = useState(false);
  const [showExtractedFields, setShowExtractedFields] = useState(false);

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages.length]);

  const handleSend = async (content: string) => {
    // Add user message (optimistic)
    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content,
      timestamp: new Date().toLocaleTimeString("fr-CA", { hour: "2-digit", minute: "2-digit" }),
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);
    setSuggestions([]); // Clear suggestions while processing

    try {
      // Call backend chat endpoint
      const response = await sendChatMessage(sessionId, content, locale);

      // Add assistant reply
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: response.reply,
        timestamp: new Date().toLocaleTimeString("fr-CA", { hour: "2-digit", minute: "2-digit" }),
      };

      setMessages((prev) => [...prev, assistantMessage]);

      // Update extracted fields
      setExtractedFields(response.extracted_fields);

      // Update suggestions
      setSuggestions(response.suggestions);

      // Update session state
      setSessionState(response.session_state);

      // If quote was generated, add it as a special message
      if (response.quote) {
        setCurrentQuote(response.quote);
        const quoteMessage: Message = {
          id: (Date.now() + 2).toString(),
          role: "assistant",
          content: "", // Quote card is rendered separately
          timestamp: new Date().toLocaleTimeString("fr-CA", {
            hour: "2-digit",
            minute: "2-digit",
          }),
          quote: response.quote,
        };
        setMessages((prev) => [...prev, quoteMessage]);
      }
    } catch (error) {
      // Add error message as assistant reply
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content:
          locale === "fr"
            ? "Une erreur s'est produite. Veuillez reessayer."
            : "An error occurred. Please try again.",
        timestamp: new Date().toLocaleTimeString("fr-CA", {
          hour: "2-digit",
          minute: "2-digit",
        }),
      };

      setMessages((prev) => [...prev, errorMessage]);
      console.error("Chat error:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSuggestionSelect = (suggestion: string) => {
    handleSend(suggestion);
  };

  const handleNewChat = async () => {
    try {
      // Reset backend session
      await resetChatSession(sessionId);

      // Clear local state
      setMessages([
        {
          id: "greeting",
          role: "assistant",
          content: t.chat.greeting,
          timestamp: new Date().toLocaleTimeString("fr-CA", {
            hour: "2-digit",
            minute: "2-digit",
          }),
        },
      ]);
      setSuggestions([
        "1200 pi2, bardeaux, pente raide",
        "2000 pi2, TPO, toit plat commercial",
        "800 pi2, reparation urgente, fuites",
      ]);
      setSessionState("greeting");
      setExtractedFields({});
      setCurrentQuote(null);
      setSelectedTier(undefined);
    } catch (error) {
      console.error("Failed to reset session:", error);
      // Continue with local reset even if backend fails
    }
  };

  const handleSelectTier = (tier: "Basic" | "Standard" | "Premium") => {
    setSelectedTier(tier);
  };

  const handleCreateSubmission = async (tier: "Basic" | "Standard" | "Premium") => {
    if (!currentQuote) return;

    setIsCreatingSubmission(true);

    try {
      // Build line items from quote work_items and materials
      const lineItems = [
        ...currentQuote.work_items.map((item, idx) => ({
          type: "labor" as const,
          name: item.name,
          quantity: item.labor_hours,
          unit_price: 75, // Placeholder hourly rate
          total: item.labor_hours * 75,
          order: idx,
        })),
        ...currentQuote.materials.map((material, idx) => ({
          type: "material" as const,
          material_id: material.material_id,
          name: `Material ${material.material_id}`,
          quantity: material.quantity,
          unit_price: material.unit_price,
          total: material.total,
          order: currentQuote.work_items.length + idx,
        })),
      ];

      // Build submission payload
      const payload = {
        category: (extractedFields.category as string) || "Bardeaux",
        sqft: extractedFields.sqft as number | undefined,
        client_name:
          (extractedFields.client_name as string) ||
          `Chat Quote ${new Date().toLocaleDateString("fr-CA")}`,
        created_by: "chat-estimator",
        line_items: lineItems,
        pricing_tiers: currentQuote.pricing_tiers,
        selected_tier: tier,
      };

      // Call createSubmission from lib/api/submissions.ts
      const submission = await createSubmission(payload);

      // Add confirmation message to chat
      const confirmationMessage: Message = {
        id: Date.now().toString(),
        role: "assistant",
        content:
          locale === "fr"
            ? `✓ Soumission creee avec succes! ID: ${submission.id.slice(0, 8)}...`
            : `✓ Submission created successfully! ID: ${submission.id.slice(0, 8)}...`,
        timestamp: new Date().toLocaleTimeString("fr-CA", {
          hour: "2-digit",
          minute: "2-digit",
        }),
      };

      setMessages((prev) => [...prev, confirmationMessage]);

      // Show toast notification
      toast({
        title: t.chat.submissionCreated,
        description: `ID: ${submission.id.slice(0, 8)}...`,
      });
    } catch (error) {
      // Add error message to chat
      const errorMessage: Message = {
        id: Date.now().toString(),
        role: "assistant",
        content:
          locale === "fr"
            ? `Erreur lors de la creation de la soumission: ${error instanceof Error ? error.message : "Erreur inconnue"}`
            : `Error creating submission: ${error instanceof Error ? error.message : "Unknown error"}`,
        timestamp: new Date().toLocaleTimeString("fr-CA", {
          hour: "2-digit",
          minute: "2-digit",
        }),
      };

      setMessages((prev) => [...prev, errorMessage]);
      console.error("Submission creation error:", error);
    } finally {
      setIsCreatingSubmission(false);
    }
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
        <Button variant="ghost" size="sm" onClick={handleNewChat} className="gap-2">
          <RotateCcw className="h-4 w-4" />
          {t.chat.newChat}
        </Button>
      </div>

      {/* Extracted Fields Collapsible */}
      {Object.keys(extractedFields).length > 0 && (
        <div className="border-b px-4 py-2 bg-muted/30 shrink-0">
          <Collapsible open={showExtractedFields} onOpenChange={setShowExtractedFields}>
            <CollapsibleTrigger asChild>
              <Button variant="ghost" size="sm" className="w-full justify-between text-xs">
                <span>{t.chat.extractedFields}</span>
                {showExtractedFields ? (
                  <ChevronUp className="h-3 w-3" />
                ) : (
                  <ChevronDown className="h-3 w-3" />
                )}
              </Button>
            </CollapsibleTrigger>
            <CollapsibleContent>
              <div className="grid grid-cols-2 gap-2 mt-2 text-xs">
                {Object.entries(extractedFields).map(([key, value]) => (
                  <div key={key} className="flex gap-2">
                    <span className="font-medium text-muted-foreground">{key}:</span>
                    <span className="text-foreground">
                      {typeof value === "object" ? JSON.stringify(value) : String(value)}
                    </span>
                  </div>
                ))}
              </div>
            </CollapsibleContent>
          </Collapsible>
        </div>
      )}

      {/* Scrollable Message List */}
      <div className="flex-1 overflow-y-auto px-4 py-4">
        {messages.map((message) =>
          message.quote ? (
            // Render QuoteSummaryCard for quote messages
            <div key={message.id} className="my-4">
              <QuoteSummaryCard
                quote={message.quote}
                onSelectTier={handleSelectTier}
                onCreateSubmission={handleCreateSubmission}
                selectedTier={selectedTier}
                isCreatingSubmission={isCreatingSubmission}
              />
            </div>
          ) : (
            // Render regular ChatMessage
            <ChatMessage
              key={message.id}
              role={message.role}
              content={message.content}
              timestamp={message.timestamp}
            />
          )
        )}

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
