"use client";

import { useState, useEffect } from "react";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from "@/components/ui/dialog";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import { Loader2, Send, Clock, Save } from "lucide-react";
import { useLanguage } from "@/lib/i18n";
import { RedFlagBanner } from "./red-flag-banner";
import {
  getRedFlags,
  sendSubmission,
  dismissFlags as dismissFlagsAPI,
  type RedFlag,
  type SendSubmissionRequest,
} from "@/lib/api/submissions";

interface SendDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  submissionId: string;
  onSendComplete?: (status: string) => void;
}

export function SendDialog({
  open,
  onOpenChange,
  submissionId,
  onSendComplete,
}: SendDialogProps) {
  const { t, locale } = useLanguage();

  const [sendOption, setSendOption] = useState<"now" | "schedule" | "draft">("now");
  const [recipientEmail, setRecipientEmail] = useState("");
  const [emailSubject, setEmailSubject] = useState("");
  const [emailBody, setEmailBody] = useState("");
  const [scheduledDate, setScheduledDate] = useState("");
  const [scheduledTime, setScheduledTime] = useState("09:00");
  const [redFlags, setRedFlags] = useState<RedFlag[]>([]);
  const [dismissedCategories, setDismissedCategories] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isSending, setIsSending] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Fetch red flags when dialog opens
  useEffect(() => {
    if (open && submissionId) {
      setIsLoading(true);
      setError(null);
      getRedFlags(submissionId)
        .then(setRedFlags)
        .catch((err) => {
          console.error("Failed to fetch red flags:", err);
          setRedFlags([]);
        })
        .finally(() => setIsLoading(false));
    }
  }, [open, submissionId]);

  function handleDismissFlag(category: string) {
    setDismissedCategories((prev) => [...prev, category]);
  }

  async function handleSend() {
    setIsSending(true);
    setError(null);

    try {
      // Log dismissed flags if any
      if (dismissedCategories.length > 0) {
        await dismissFlagsAPI(submissionId, dismissedCategories);
      }

      // Build scheduled datetime if scheduling
      let scheduledSendAt: string | undefined;
      if (sendOption === "schedule" && scheduledDate && scheduledTime) {
        // Combine date + time, assume America/Montreal timezone
        const dateTimeStr = `${scheduledDate}T${scheduledTime}:00`;
        scheduledSendAt = new Date(dateTimeStr).toISOString();
      }

      const request: SendSubmissionRequest = {
        send_option: sendOption,
        recipient_email: sendOption !== "draft" ? recipientEmail : undefined,
        email_subject: emailSubject || undefined,
        email_body: emailBody || undefined,
        scheduled_send_at: scheduledSendAt,
      };

      const result = await sendSubmission(submissionId, request);
      onSendComplete?.(result.send_status);
      onOpenChange(false);

      // Reset form
      setSendOption("now");
      setRecipientEmail("");
      setEmailSubject("");
      setEmailBody("");
      setScheduledDate("");
      setScheduledTime("09:00");
      setDismissedCategories([]);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Send failed");
    } finally {
      setIsSending(false);
    }
  }

  const showEmailFields = sendOption === "now" || sendOption === "schedule";

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>{t.sendDialog?.titre || "Envoyer la soumission"}</DialogTitle>
          <DialogDescription>
            {t.sendDialog?.description || "Choisissez comment envoyer cette soumission"}
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 py-4">
          {/* Red flag warnings */}
          {isLoading ? (
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <Loader2 className="h-4 w-4 animate-spin" />
              {t.common?.chargement || "Chargement..."}
            </div>
          ) : (
            <RedFlagBanner flags={redFlags} onDismiss={handleDismissFlag} />
          )}

          {/* Send option selection */}
          <RadioGroup
            value={sendOption}
            onValueChange={(v: string) => setSendOption(v as "now" | "schedule" | "draft")}
            className="space-y-3"
          >
            <div className="flex items-center space-x-3">
              <RadioGroupItem value="now" id="send-now" />
              <Label htmlFor="send-now" className="flex items-center gap-2 cursor-pointer">
                <Send className="h-4 w-4" />
                {t.sendDialog?.envoyerMaintenant || "Envoyer maintenant"}
              </Label>
            </div>
            <div className="flex items-center space-x-3">
              <RadioGroupItem value="schedule" id="send-schedule" />
              <Label htmlFor="send-schedule" className="flex items-center gap-2 cursor-pointer">
                <Clock className="h-4 w-4" />
                {t.sendDialog?.planifier || "Planifier l'envoi"}
              </Label>
            </div>
            <div className="flex items-center space-x-3">
              <RadioGroupItem value="draft" id="send-draft" />
              <Label htmlFor="send-draft" className="flex items-center gap-2 cursor-pointer">
                <Save className="h-4 w-4" />
                {t.sendDialog?.sauvegarderBrouillon || "Sauvegarder comme brouillon"}
              </Label>
            </div>
          </RadioGroup>

          {/* Schedule date+time picker */}
          {sendOption === "schedule" && (
            <div className="space-y-2">
              <Label>{t.sendDialog?.dateHeure || "Date et heure d'envoi"}</Label>
              <div className="flex gap-2">
                <Input
                  type="date"
                  value={scheduledDate}
                  onChange={(e) => setScheduledDate(e.target.value)}
                  min={new Date().toISOString().split("T")[0]}
                  className="flex-1"
                />
                <Input
                  type="time"
                  value={scheduledTime}
                  onChange={(e) => setScheduledTime(e.target.value)}
                  className="w-32"
                />
              </div>
            </div>
          )}

          {/* Email fields (shown for send now and schedule) */}
          {showEmailFields && (
            <div className="space-y-3">
              <div className="space-y-2">
                <Label>{t.sendDialog?.destinataire || "Destinataire"}</Label>
                <Input
                  type="email"
                  placeholder="client@example.com"
                  value={recipientEmail}
                  onChange={(e) => setRecipientEmail(e.target.value)}
                />
              </div>
              <div className="space-y-2">
                <Label>{t.sendDialog?.sujet || "Sujet (optionnel)"}</Label>
                <Input
                  placeholder={locale === "fr" ? "Votre soumission - Toiture LV" : "Your quote - Toiture LV"}
                  value={emailSubject}
                  onChange={(e) => setEmailSubject(e.target.value)}
                />
              </div>
              <div className="space-y-2">
                <Label>{t.sendDialog?.message || "Message (optionnel)"}</Label>
                <Textarea
                  placeholder={locale === "fr" ? "Message personnalise..." : "Custom message..."}
                  value={emailBody}
                  onChange={(e) => setEmailBody(e.target.value)}
                  rows={3}
                />
              </div>
            </div>
          )}

          {/* Error display */}
          {error && (
            <p className="text-sm text-destructive">{error}</p>
          )}
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            {t.sendDialog?.annuler || "Annuler"}
          </Button>
          <Button
            onClick={handleSend}
            disabled={isSending || (showEmailFields && !recipientEmail)}
          >
            {isSending ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                {t.common?.chargement || "Chargement..."}
              </>
            ) : (
              t.sendDialog?.confirmer || "Confirmer l'envoi"
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
