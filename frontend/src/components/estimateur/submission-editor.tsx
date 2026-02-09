"use client";

import { useState, useMemo } from "react";
import { MaterialSelector, type SelectedMaterial } from "@/components/estimateur/material-selector";
import { SortableLineItem } from "@/components/estimateur/sortable-line-item";
import { NotesPanel } from "@/components/estimateur/notes-panel";
import { UpsellDialog } from "@/components/estimateur/upsell-dialog";
import { SubmissionStatusBadge } from "@/components/estimateur/submission-status-badge";
import {
  updateSubmission,
  finalizeSubmission,
  approveSubmission,
  rejectSubmission,
  returnToDraft,
  addNote,
  createUpsell,
  getUpsellSuggestions,
} from "@/lib/api/submissions";
import type { Submission, LineItem, UpsellSuggestion } from "@/types/submission";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { DndContext, closestCenter, type DragEndEvent } from "@dnd-kit/core";
import { SortableContext, verticalListSortingStrategy } from "@dnd-kit/sortable";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { AlertCircle, Loader2 } from "lucide-react";
import { useLanguage } from "@/lib/i18n";
import { useToast } from "@/hooks/use-toast";

interface SubmissionEditorProps {
  initialData: Submission;
  onUpdate: (submission: Submission) => void;
  userRole?: "admin" | "estimator";
  userName?: string;
}

export function SubmissionEditor({
  initialData,
  onUpdate,
  userRole = "estimator",
  userName = "estimateur",
}: SubmissionEditorProps) {
  const { t, locale } = useLanguage();
  const { toast } = useToast();

  const [submission, setSubmission] = useState<Submission>(initialData);
  const [lineItems, setLineItems] = useState<LineItem[]>(initialData.line_items);
  const [clientName, setClientName] = useState<string>(initialData.client_name || "");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showUpsellDialog, setShowUpsellDialog] = useState(false);
  const [upsellSuggestions, setUpsellSuggestions] = useState<UpsellSuggestion[]>([]);
  const [showMaterialSelector, setShowMaterialSelector] = useState(false);
  const [showRejectDialog, setShowRejectDialog] = useState(false);
  const [rejectReason, setRejectReason] = useState("");

  // Derived state
  const isDraft = submission.status === "draft";
  const isPending = submission.status === "pending_approval";
  const isRejected = submission.status === "rejected";
  const isAdmin = userRole === "admin";

  // Computed totals
  const { totalMaterials, totalLabor, grandTotal } = useMemo(() => {
    const materials = lineItems
      .filter((item) => item.type === "material")
      .reduce((sum, item) => sum + item.total, 0);
    const labor = lineItems
      .filter((item) => item.type === "labor")
      .reduce((sum, item) => sum + item.total, 0);
    return {
      totalMaterials: materials,
      totalLabor: labor,
      grandTotal: materials + labor,
    };
  }, [lineItems]);

  // Format currency
  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat("fr-CA", {
      style: "currency",
      currency: "CAD",
    }).format(value);
  };

  // Format date
  const formatDate = (dateString: string) => {
    return new Intl.DateTimeFormat("fr-CA", {
      dateStyle: "medium",
      timeStyle: "short",
    }).format(new Date(dateString));
  };

  // Line item handlers
  const handleUpdateItem = (index: number, field: keyof LineItem, value: string | number) => {
    const updated = [...lineItems];
    if (field === "quantity" || field === "unit_price") {
      updated[index] = {
        ...updated[index],
        [field]: value,
        total: field === "quantity"
          ? (value as number) * updated[index].unit_price
          : updated[index].quantity * (value as number),
      };
    } else {
      updated[index] = { ...updated[index], [field]: value };
    }
    setLineItems(updated);
  };

  const handleRemoveItem = (index: number) => {
    const updated = lineItems.filter((_, i) => i !== index);
    // Reorder remaining items
    const reordered = updated.map((item, i) => ({ ...item, order: i }));
    setLineItems(reordered);
  };

  const handleAddItem = (type: "material" | "labor") => {
    const newItem: LineItem = {
      id: crypto.randomUUID(),
      type,
      name: "",
      quantity: 1,
      unit_price: 0,
      total: 0,
      order: lineItems.length,
    };
    setLineItems([...lineItems, newItem]);
  };

  const handleAddFromMaterials = (materials: SelectedMaterial[]) => {
    const newItems: LineItem[] = materials.map((m, i) => ({
      id: crypto.randomUUID(),
      type: "material" as const,
      material_id: m.id > 0 ? m.id : undefined,
      name: m.name,
      quantity: 1,
      unit_price: m.sell_price || 0,
      total: m.sell_price || 0,
      order: lineItems.length + i,
    }));
    setLineItems((prev) => [...prev, ...newItems]);
    setShowMaterialSelector(false);
  };

  // Drag-drop handler
  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event;
    if (active.id !== over?.id) {
      const oldIndex = lineItems.findIndex((li) => li.id === active.id);
      const newIndex = lineItems.findIndex((li) => li.id === over?.id);
      const newItems = [...lineItems];
      const [moved] = newItems.splice(oldIndex, 1);
      newItems.splice(newIndex, 0, moved);
      const reordered = newItems.map((item, i) => ({ ...item, order: i }));
      setLineItems(reordered);
    }
  };

  // Action handlers
  const handleSave = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const updated = await updateSubmission(
        submission.id,
        {
          line_items: lineItems.map(({ id, ...rest }) => rest),
          client_name: clientName || undefined,
        },
        userName
      );
      setSubmission(updated);
      onUpdate(updated);
      toast({
        title: t.submission.submissionUpdated,
        description: formatDate(updated.updated_at),
      });
    } catch (err) {
      const message = err instanceof Error ? err.message : "Failed to save";
      setError(message);
      toast({
        title: "Error",
        description: message,
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleFinalize = async () => {
    if (lineItems.length === 0) {
      setError(t.submission.noLineItems);
      return;
    }

    if (!confirm(t.submission.confirmFinalize)) return;

    setIsLoading(true);
    setError(null);
    try {
      const updated = await finalizeSubmission(submission.id, userName);
      setSubmission(updated);
      onUpdate(updated);

      // Fetch upsell suggestions
      const suggestions = await getUpsellSuggestions(submission.id);
      setUpsellSuggestions(suggestions);
      setShowUpsellDialog(true);

      toast({
        title: t.submission.submissionFinalized,
        description: t.submission.approvalRequired,
      });
    } catch (err) {
      const message = err instanceof Error ? err.message : "Failed to finalize";
      setError(message);
      toast({
        title: "Error",
        description: message,
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleApprove = async () => {
    if (!confirm(t.submission.confirmApprove)) return;

    setIsLoading(true);
    setError(null);
    try {
      const updated = await approveSubmission(submission.id, userName, "admin");
      setSubmission(updated);
      onUpdate(updated);
      toast({
        title: t.submission.submissionApproved,
        description: formatDate(updated.updated_at),
      });
    } catch (err) {
      const message = err instanceof Error ? err.message : "Failed to approve";
      setError(message);
      toast({
        title: "Error",
        description: message,
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleReject = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const updated = await rejectSubmission(
        submission.id,
        rejectReason || undefined,
        userName,
        "admin"
      );
      setSubmission(updated);
      onUpdate(updated);
      setShowRejectDialog(false);
      setRejectReason("");
      toast({
        title: t.submission.submissionRejected,
        description: formatDate(updated.updated_at),
      });
    } catch (err) {
      const message = err instanceof Error ? err.message : "Failed to reject";
      setError(message);
      toast({
        title: "Error",
        description: message,
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleReturnToDraft = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const updated = await returnToDraft(submission.id, userName);
      setSubmission(updated);
      setLineItems(updated.line_items);
      onUpdate(updated);
      toast({
        title: t.submission.submissionReturnedToDraft,
        description: formatDate(updated.updated_at),
      });
    } catch (err) {
      const message = err instanceof Error ? err.message : "Failed to return to draft";
      setError(message);
      toast({
        title: "Error",
        description: message,
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleAddNote = async (text: string) => {
    const updated = await addNote(submission.id, text, userName);
    setSubmission(updated);
    onUpdate(updated);
    toast({
      title: t.submission.noteAdded,
    });
  };

  const handleCreateUpsell = async (type: string) => {
    try {
      const upsell = await createUpsell(submission.id, type, userName);
      // Refresh submission to get updated children list
      const updated = { ...submission, children: [...(submission.children || []), upsell] };
      setSubmission(updated);
      onUpdate(updated);
      toast({
        title: t.submission.upsellCreated,
        description: type,
      });
    } catch (err) {
      const message = err instanceof Error ? err.message : "Failed to create upsell";
      toast({
        title: "Error",
        description: message,
        variant: "destructive",
      });
    }
  };

  return (
    <div className="space-y-6">
      {/* Header with status + metadata */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <SubmissionStatusBadge status={submission.status} />
          <span className="text-sm text-muted-foreground">
            {submission.category} | {submission.sqft} pi²
          </span>
        </div>
        <span className="text-xs text-muted-foreground">
          {formatDate(submission.created_at)}
        </span>
      </div>

      {/* Client name input */}
      <div className="space-y-2">
        <Label>{t.submission.clientName}</Label>
        <Input
          value={clientName}
          onChange={(e) => setClientName(e.target.value)}
          disabled={!isDraft}
          placeholder={t.submission.clientNamePlaceholder}
        />
      </div>

      {/* Line Items Card */}
      <Card>
        <CardHeader>
          <CardTitle>{t.submission.editLineItems}</CardTitle>
        </CardHeader>
        <CardContent>
          {/* Column headers */}
          <div className="hidden sm:grid grid-cols-[40px_60px_1fr_80px_100px_100px_40px] gap-2 text-xs font-medium text-muted-foreground mb-2">
            <span></span>
            <span>{t.submission.lineItemType}</span>
            <span>{t.submission.lineItemName}</span>
            <span>{t.submission.lineItemQuantity}</span>
            <span>{t.submission.lineItemUnitPrice}</span>
            <span>{t.submission.lineItemTotal}</span>
            <span></span>
          </div>

          {lineItems.length === 0 ? (
            <p className="text-sm text-muted-foreground py-4 text-center">
              {t.submission.noLineItems}
            </p>
          ) : (
            <DndContext collisionDetection={closestCenter} onDragEnd={handleDragEnd}>
              <SortableContext
                items={lineItems.map((li) => li.id)}
                strategy={verticalListSortingStrategy}
              >
                <div className="space-y-2">
                  {lineItems.map((item, index) => (
                    <SortableLineItem
                      key={item.id}
                      id={item.id}
                      index={index}
                      item={item}
                      onUpdate={handleUpdateItem}
                      onRemove={handleRemoveItem}
                      disabled={!isDraft}
                    />
                  ))}
                </div>
              </SortableContext>
            </DndContext>
          )}

          {/* Add buttons */}
          {isDraft && (
            <div className="flex gap-2 mt-4">
              <Button
                variant="outline"
                size="sm"
                onClick={() => handleAddItem("material")}
              >
                + {t.submission.addMaterial}
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => handleAddItem("labor")}
              >
                + {t.submission.addLabor}
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setShowMaterialSelector(true)}
              >
                {t.submission.addFromMaterials}
              </Button>
            </div>
          )}

          {/* Totals */}
          <div className="mt-4 pt-4 border-t space-y-1">
            <div className="flex justify-between text-sm">
              <span>{t.submission.totalMaterials}</span>
              <span className="font-medium tabular-nums">
                {formatCurrency(totalMaterials)}
              </span>
            </div>
            <div className="flex justify-between text-sm">
              <span>{t.submission.totalLabor}</span>
              <span className="font-medium tabular-nums">
                {formatCurrency(totalLabor)}
              </span>
            </div>
            <hr className="my-2" />
            <div className="flex justify-between text-lg font-bold">
              <span>{t.submission.grandTotal}</span>
              <span className="tabular-nums">{formatCurrency(grandTotal)}</span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* MaterialSelector Dialog */}
      <Dialog open={showMaterialSelector} onOpenChange={setShowMaterialSelector}>
        <DialogContent className="max-w-lg">
          <DialogHeader>
            <DialogTitle>{t.submission.addFromMaterials}</DialogTitle>
          </DialogHeader>
          <MaterialSelector
            selectedMaterials={[]}
            onSelectionChange={(materials: SelectedMaterial[]) => {
              handleAddFromMaterials(materials);
            }}
          />
        </DialogContent>
      </Dialog>

      {/* Notes Panel */}
      <NotesPanel
        notes={submission.notes}
        onAddNote={handleAddNote}
        disabled={isLoading}
      />

      {/* Error display */}
      {error && (
        <div className="flex items-center gap-2 rounded-lg border border-destructive/50 bg-destructive/10 p-4 text-destructive">
          <AlertCircle className="size-5 shrink-0" />
          <p className="text-sm">{error}</p>
        </div>
      )}

      {/* Action buttons */}
      <div className="flex gap-3 pt-4 border-t">
        {isDraft && (
          <>
            <Button onClick={handleSave} disabled={isLoading}>
              {isLoading ? <Loader2 className="mr-2 size-4 animate-spin" /> : null}
              {t.submission.save}
            </Button>
            <Button
              variant="secondary"
              onClick={handleFinalize}
              disabled={isLoading || lineItems.length === 0}
            >
              {t.submission.finalize}
            </Button>
          </>
        )}
        {isPending && isAdmin && (
          <>
            <Button
              onClick={handleApprove}
              disabled={isLoading}
              className="bg-green-600 hover:bg-green-700"
            >
              {t.submission.approve}
            </Button>
            <Button
              variant="destructive"
              onClick={() => setShowRejectDialog(true)}
              disabled={isLoading}
            >
              {t.submission.reject}
            </Button>
          </>
        )}
        {isPending && !isAdmin && (
          <p className="text-sm text-muted-foreground italic">
            {t.submission.awaitingApproval}
          </p>
        )}
        {(isRejected || (isPending && !isAdmin)) && (
          <Button variant="outline" onClick={handleReturnToDraft} disabled={isLoading}>
            {t.submission.returnToDraft}
          </Button>
        )}
      </div>

      {/* Child submissions (upsells) */}
      {submission.children && submission.children.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>{t.submission.childSubmissions}</CardTitle>
          </CardHeader>
          <CardContent>
            {submission.children.map((child) => (
              <div
                key={child.id}
                className="flex items-center justify-between p-2 rounded border mb-2"
              >
                <div>
                  <SubmissionStatusBadge status={child.status} />
                  <span className="ml-2 text-sm">{child.upsell_type}</span>
                </div>
                <span className="text-sm font-medium">
                  {formatCurrency(child.total_price)}
                </span>
              </div>
            ))}
          </CardContent>
        </Card>
      )}

      {/* Reject Dialog */}
      <Dialog open={showRejectDialog} onOpenChange={setShowRejectDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{t.submission.reject}</DialogTitle>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label>{t.submission.rejectReason}</Label>
              <Textarea
                value={rejectReason}
                onChange={(e) => setRejectReason(e.target.value)}
                placeholder={t.submission.rejectReasonPlaceholder}
                rows={3}
              />
            </div>
          </div>
          <div className="flex justify-end gap-2">
            <Button
              variant="outline"
              onClick={() => setShowRejectDialog(false)}
              disabled={isLoading}
            >
              Cancel
            </Button>
            <Button
              variant="destructive"
              onClick={handleReject}
              disabled={isLoading}
            >
              {t.submission.reject}
            </Button>
          </div>
        </DialogContent>
      </Dialog>

      {/* Upsell Dialog */}
      <UpsellDialog
        open={showUpsellDialog}
        onOpenChange={setShowUpsellDialog}
        suggestions={upsellSuggestions}
        onCreateUpsell={handleCreateUpsell}
        locale={locale}
      />
    </div>
  );
}
