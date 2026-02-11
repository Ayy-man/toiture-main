"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { SubmissionStatusBadge } from "@/components/estimateur/submission-status-badge";
import { SubmissionEditor } from "@/components/estimateur/submission-editor";
import { CardSkeleton } from "@/components/shared/card-skeleton";
import { EmptyState } from "@/components/shared/empty-state";
import { listSubmissions, getSubmission } from "@/lib/api/submissions";
import type { SubmissionListItem, Submission } from "@/types/submission";
import { useLanguage } from "@/lib/i18n";
import { Loader2, RefreshCw, ArrowLeft, FileText } from "lucide-react";

interface SubmissionListProps {
  userRole?: "admin" | "estimator";
  userName?: string;
}

export function SubmissionList({
  userRole = "estimator",
  userName = "estimateur",
}: SubmissionListProps) {
  const { t } = useLanguage();
  const [submissions, setSubmissions] = useState<SubmissionListItem[]>([]);
  const [filteredSubmissions, setFilteredSubmissions] = useState<SubmissionListItem[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [selectedSubmission, setSelectedSubmission] = useState<Submission | null>(null);
  const [statusFilter, setStatusFilter] = useState<string>("all");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Load submissions list
  const loadSubmissions = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await listSubmissions();
      setSubmissions(data);
      setFilteredSubmissions(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load submissions");
    } finally {
      setLoading(false);
    }
  };

  // Load on mount
  useEffect(() => {
    loadSubmissions();
  }, []);

  // Filter submissions when status changes
  useEffect(() => {
    if (statusFilter === "all") {
      setFilteredSubmissions(submissions);
    } else {
      setFilteredSubmissions(
        submissions.filter((sub) => sub.status === statusFilter)
      );
    }
  }, [statusFilter, submissions]);

  // Load full submission when selected
  useEffect(() => {
    if (selectedId) {
      setLoading(true);
      getSubmission(selectedId)
        .then((sub) => setSelectedSubmission(sub))
        .catch((err) => {
          setError(err instanceof Error ? err.message : "Failed to load submission");
          setSelectedId(null);
        })
        .finally(() => setLoading(false));
    } else {
      setSelectedSubmission(null);
    }
  }, [selectedId]);

  // Handle submission update
  const handleUpdate = (updated: Submission) => {
    setSelectedSubmission(updated);
    // Update in list
    setSubmissions((prev) =>
      prev.map((sub) =>
        sub.id === updated.id
          ? {
              ...sub,
              status: updated.status,
              client_name: updated.client_name,
              total_price: updated.total_price,
            }
          : sub
      )
    );
  };

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
    }).format(new Date(dateString));
  };

  // Render single submission editor
  if (selectedId && selectedSubmission) {
    return (
      <div className="space-y-4">
        <Button
          variant="outline"
          onClick={() => setSelectedId(null)}
          className="mb-4"
        >
          <ArrowLeft className="mr-2 h-4 w-4" />
          {t.submission.backToList}
        </Button>
        <SubmissionEditor
          initialData={selectedSubmission}
          onUpdate={handleUpdate}
          userRole={userRole}
          userName={userName}
        />
      </div>
    );
  }

  // Render submissions list
  return (
    <div className="space-y-4">
      {/* Header with refresh button */}
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">{t.submission.submissions}</h2>
        <Button
          variant="outline"
          size="sm"
          onClick={loadSubmissions}
          disabled={loading}
        >
          <RefreshCw className={`h-4 w-4 mr-2 ${loading ? "animate-spin" : ""}`} />
          {t.submission.refresh}
        </Button>
      </div>

      {/* Status filter tabs */}
      <Tabs value={statusFilter} onValueChange={setStatusFilter}>
        <TabsList>
          <TabsTrigger value="all">{t.submission.allStatuses}</TabsTrigger>
          <TabsTrigger value="draft">{t.submission.statusDraft}</TabsTrigger>
          <TabsTrigger value="pending_approval">{t.submission.statusPending}</TabsTrigger>
          <TabsTrigger value="approved">{t.submission.statusApproved}</TabsTrigger>
          <TabsTrigger value="rejected">{t.submission.statusRejected}</TabsTrigger>
        </TabsList>

        <TabsContent value={statusFilter} className="space-y-3 mt-4">
          {loading && !submissions.length ? (
            <div className="space-y-3">
              <CardSkeleton />
              <CardSkeleton />
              <CardSkeleton />
            </div>
          ) : error ? (
            <div className="rounded-lg border border-destructive/50 bg-destructive/10 p-4 text-destructive">
              {error}
            </div>
          ) : filteredSubmissions.length === 0 ? (
            <EmptyState
              icon={FileText}
              title={t.submission.noSubmissions}
              description={t.historique.aucuneSoumissionDesc}
            />
          ) : (
            filteredSubmissions.map((sub) => (
              <Card
                key={sub.id}
                className="hover:bg-muted/50 cursor-pointer transition-colors"
                onClick={() => setSelectedId(sub.id)}
              >
                <CardHeader className="pb-3">
                  <div className="flex items-start justify-between">
                    <div className="space-y-1">
                      <div className="flex items-center gap-2">
                        <SubmissionStatusBadge status={sub.status} />
                        {sub.has_children && (
                          <Badge variant="outline" className="text-xs">
                            +{t.submission.upsells}
                          </Badge>
                        )}
                        {sub.upsell_type && (
                          <Badge variant="outline" className="text-xs">
                            {sub.upsell_type}
                          </Badge>
                        )}
                      </div>
                      <CardTitle className="text-lg">
                        {sub.client_name || "Sans nom"}
                      </CardTitle>
                      <p className="text-sm text-muted-foreground">
                        {sub.category} • {formatDate(sub.created_at)}
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="text-lg font-bold tabular-nums">
                        {formatCurrency(sub.total_price)}
                      </p>
                    </div>
                  </div>
                </CardHeader>
              </Card>
            ))
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
}
