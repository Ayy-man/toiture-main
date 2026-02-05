"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { ThumbsUp, ThumbsDown, Send, Loader2, CheckCircle } from "lucide-react";
import { useLanguage } from "@/lib/i18n";

interface FeedbackPanelProps {
  estimateId: string;
  inputParams: Record<string, unknown>;
  predictedPrice: number;
  predictedMaterials?: Array<Record<string, unknown>> | null;
}

export function FeedbackPanel({
  estimateId,
  inputParams,
  predictedPrice,
  predictedMaterials,
}: FeedbackPanelProps) {
  const { t } = useLanguage();
  const [selectedFeedback, setSelectedFeedback] = useState<
    "positive" | "negative" | null
  >(null);
  const [actualPrice, setActualPrice] = useState("");
  const [reason, setReason] = useState("");
  const [submitted, setSubmitted] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async () => {
    if (!selectedFeedback) return;

    // Validate required fields for negative feedback
    if (selectedFeedback === "negative" && (!actualPrice || !reason)) {
      setError("Veuillez remplir tous les champs obligatoires");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/feedback/quick`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            estimate_id: estimateId,
            input_params: inputParams,
            predicted_price: predictedPrice,
            predicted_materials: predictedMaterials,
            feedback: selectedFeedback,
            actual_price: actualPrice ? parseFloat(actualPrice) : null,
            reason: reason || null,
          }),
        }
      );

      if (!response.ok) {
        throw new Error(`Erreur ${response.status}`);
      }

      setSubmitted(true);
    } catch (err) {
      console.error("Feedback error:", err);
      setError("Erreur lors de l'envoi du feedback");
    } finally {
      setLoading(false);
    }
  };

  if (submitted) {
    return (
      <div className="flex items-center justify-center gap-2 py-4 text-green-600 font-medium">
        <CheckCircle className="h-5 w-5" />
        <span>Merci pour votre retour!</span>
      </div>
    );
  }

  return (
    <div className="border-t pt-4 mt-4">
      <p className="text-sm text-muted-foreground mb-3">
        Cette estimation était-elle utile?
      </p>

      <div className="flex gap-3 mb-4">
        <Button
          type="button"
          variant={selectedFeedback === "positive" ? "default" : "outline"}
          size="lg"
          onClick={() => setSelectedFeedback("positive")}
          className="flex-1"
        >
          <ThumbsUp className="mr-2 h-5 w-5" />
          Précise
        </Button>
        <Button
          type="button"
          variant={selectedFeedback === "negative" ? "destructive" : "outline"}
          size="lg"
          onClick={() => setSelectedFeedback("negative")}
          className="flex-1"
        >
          <ThumbsDown className="mr-2 h-5 w-5" />
          Imprécise
        </Button>
      </div>

      {selectedFeedback && (
        <div className="space-y-4 animate-in fade-in slide-in-from-top-2 duration-200">
          <div className="space-y-2">
            <Label htmlFor="actual_price">
              Quel était le vrai prix?
              {selectedFeedback === "negative" && (
                <span className="text-red-500 ml-1">*</span>
              )}
            </Label>
            <Input
              id="actual_price"
              type="number"
              placeholder="Ex: 15000"
              value={actualPrice}
              onChange={(e) => setActualPrice(e.target.value)}
              required={selectedFeedback === "negative"}
            />
          </div>

          {selectedFeedback === "negative" && (
            <div className="space-y-2">
              <Label htmlFor="reason">
                Pourquoi?
                <span className="text-red-500 ml-1">*</span>
              </Label>
              <Textarea
                id="reason"
                placeholder="Expliquez pourquoi l'estimation était imprécise..."
                value={reason}
                onChange={(e) => setReason(e.target.value)}
                rows={3}
                required
              />
            </div>
          )}

          {error && (
            <p className="text-sm text-red-500">{error}</p>
          )}

          <Button
            type="button"
            onClick={handleSubmit}
            disabled={
              loading ||
              (selectedFeedback === "negative" && (!actualPrice || !reason))
            }
            className="w-full"
          >
            {loading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Envoi...
              </>
            ) : (
              <>
                <Send className="mr-2 h-4 w-4" />
                Soumettre
              </>
            )}
          </Button>
        </div>
      )}
    </div>
  );
}
