"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useLanguage } from "@/lib/i18n";
import type { Note } from "@/types/submission";

interface NotesPanelProps {
  notes: Note[];
  onAddNote: (text: string) => Promise<void>;
  disabled?: boolean;
  isLoading?: boolean;
}

export function NotesPanel({
  notes,
  onAddNote,
  disabled = false,
  isLoading = false,
}: NotesPanelProps) {
  const { t } = useLanguage();
  const [noteText, setNoteText] = useState("");
  const [adding, setAdding] = useState(false);

  const handleSubmit = async () => {
    if (!noteText.trim()) return;

    setAdding(true);
    try {
      await onAddNote(noteText.trim());
      setNoteText("");
    } catch (error) {
      console.error("Failed to add note:", error);
    } finally {
      setAdding(false);
    }
  };

  // Sort notes by created_at DESC (most recent first)
  const sortedNotes = [...notes].sort((a, b) =>
    new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
  );

  // Format date with fr-CA locale
  const formatDate = (dateString: string) => {
    return new Intl.DateTimeFormat("fr-CA", {
      dateStyle: "medium",
      timeStyle: "short",
    }).format(new Date(dateString));
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center gap-2">
          <CardTitle>{t.submission.notes}</CardTitle>
          <Badge variant="outline">{notes.length}</Badge>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Notes list */}
        {sortedNotes.length === 0 ? (
          <p className="text-sm text-muted-foreground">{t.submission.noNotes}</p>
        ) : (
          <div className="space-y-3">
            {sortedNotes.map((note) => (
              <div
                key={note.id}
                className="rounded-lg bg-muted/30 p-3 space-y-1"
              >
                <p className="text-sm whitespace-pre-wrap">{note.text}</p>
                <div className="text-xs text-muted-foreground">
                  {t.submission.noteBy} {note.created_by} • {formatDate(note.created_at)}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Add note input */}
        <div className="space-y-2 pt-2 border-t">
          <Textarea
            rows={2}
            value={noteText}
            onChange={(e) => setNoteText(e.target.value)}
            placeholder={t.submission.notePlaceholder}
            disabled={disabled || isLoading || adding}
          />
          <Button
            onClick={handleSubmit}
            disabled={disabled || isLoading || adding || !noteText.trim()}
            size="sm"
          >
            {t.submission.addNote}
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
