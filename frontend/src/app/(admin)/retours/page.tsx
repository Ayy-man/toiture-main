"use client";

import { useState, useEffect } from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible";
import { useLanguage } from "@/lib/i18n";
import {
  MessageSquare,
  ThumbsUp,
  ThumbsDown,
  TrendingDown,
  TrendingUp,
  Calendar,
  ChevronDown,
  ChevronUp,
  Loader2,
  AlertCircle,
  Package,
} from "lucide-react";

// Types
interface FeedbackEntry {
  id: string;
  estimate_id: string;
  created_at: string;
  input_params: Record<string, unknown>;
  predicted_price: number;
  predicted_materials?: Array<Record<string, unknown>> | null;
  feedback: "positive" | "negative";
  actual_price: number | null;
  reason: string | null;
  category: string | null;
  sqft: number | null;
  price_gap: number | null;
  price_gap_percent: number | null;
}

interface FeedbackSummary {
  total_count: number;
  positive_count: number;
  negative_count: number;
  approval_rate: number;
  avg_gap_absolute: number | null;
  avg_gap_percent: number | null;
  weekly_count: number;
}

interface FeedbackListResponse {
  items: FeedbackEntry[];
  total: number;
  page: number;
  limit: number;
  has_more: boolean;
}

const API_URL = process.env.NEXT_PUBLIC_API_URL;

export default function RetoursPage() {
  const { t } = useLanguage();

  // State
  const [summary, setSummary] = useState<FeedbackSummary | null>(null);
  const [feedback, setFeedback] = useState<FeedbackEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expandedRow, setExpandedRow] = useState<string | null>(null);

  // Filters
  const [typeFilter, setTypeFilter] = useState<string>("all");
  const [categoryFilter, setCategoryFilter] = useState<string>("all");
  const [periodFilter, setPeriodFilter] = useState<string>("all");
  const [sortBy, setSortBy] = useState<string>("date");
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(false);

  // Fetch summary
  useEffect(() => {
    async function fetchSummary() {
      try {
        const res = await fetch(`${API_URL}/feedback/summary`);
        if (!res.ok) throw new Error("Failed to fetch summary");
        const data: FeedbackSummary = await res.json();
        setSummary(data);
      } catch (err) {
        console.error("Summary fetch error:", err);
      }
    }
    fetchSummary();
  }, []);

  // Fetch feedback list
  useEffect(() => {
    async function fetchFeedback() {
      setLoading(true);
      setError(null);

      try {
        const params = new URLSearchParams();
        if (typeFilter !== "all") params.append("type", typeFilter);
        if (categoryFilter !== "all") params.append("category", categoryFilter);
        if (periodFilter !== "all") {
          const now = new Date();
          if (periodFilter === "7d") {
            const since = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
            params.append("since", since.toISOString().split("T")[0]);
          } else if (periodFilter === "30d") {
            const since = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);
            params.append("since", since.toISOString().split("T")[0]);
          }
        }
        params.append("sort", sortBy);
        params.append("page", page.toString());
        params.append("limit", "20");

        const res = await fetch(`${API_URL}/feedback?${params.toString()}`);
        if (!res.ok) throw new Error("Failed to fetch feedback");
        const data: FeedbackListResponse = await res.json();
        setFeedback(data.items);
        setHasMore(data.has_more);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Unknown error");
      } finally {
        setLoading(false);
      }
    }
    fetchFeedback();
  }, [typeFilter, categoryFilter, periodFilter, sortBy, page]);

  // Format currency
  const formatCurrency = (value: number | null) => {
    if (value === null) return "-";
    return new Intl.NumberFormat("fr-CA", {
      style: "currency",
      currency: "CAD",
      maximumFractionDigits: 0,
    }).format(value);
  };

  // Format date
  const formatDate = (dateStr: string) => {
    return new Intl.DateTimeFormat("fr-CA", {
      year: "numeric",
      month: "short",
      day: "numeric",
    }).format(new Date(dateStr));
  };

  // Get gap color class
  const getGapColor = (gapPercent: number | null) => {
    if (gapPercent === null) return "text-muted-foreground";
    const absGap = Math.abs(gapPercent);
    if (absGap <= 10) return "text-green-600";
    if (absGap <= 20) return "text-yellow-600";
    return "text-red-600";
  };

  // Categories for filter
  const categories = ["Bardeaux", "Élastomère", "Other", "Service Call"];

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-2xl font-bold">{t.retours.titre}</h1>
        <p className="text-muted-foreground">{t.retours.description}</p>
      </div>

      {/* Summary Cards */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              {t.retours.totalRetours}
            </CardTitle>
            <MessageSquare className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {summary?.total_count ?? "-"}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              {t.retours.tauxApprobation}
            </CardTitle>
            <ThumbsUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {summary?.approval_rate !== undefined
                ? `${summary.approval_rate.toFixed(1)}%`
                : "-"}
            </div>
            <p className="text-xs text-muted-foreground">
              {summary
                ? `${summary.positive_count} ${t.retours.positif.toLowerCase()} / ${summary.negative_count} ${t.retours.negatif.toLowerCase()}`
                : ""}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              {t.retours.ecartMoyen}
            </CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {summary?.avg_gap_percent !== null
                ? `${summary?.avg_gap_percent?.toFixed(1)}%`
                : "-"}
            </div>
            <p className="text-xs text-muted-foreground">
              {summary?.avg_gap_absolute !== null
                ? formatCurrency(summary?.avg_gap_absolute ?? null)
                : ""}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              {t.retours.retoursSemaine}
            </CardTitle>
            <Calendar className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {summary?.weekly_count ?? "-"}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Filters */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-base">{t.retours.filtres}</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-4">
            {/* Type Filter */}
            <div className="space-y-1">
              <label className="text-xs text-muted-foreground">
                {t.retours.typeFeedback}
              </label>
              <Select value={typeFilter} onValueChange={setTypeFilter}>
                <SelectTrigger className="w-[140px]">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">{t.retours.tous}</SelectItem>
                  <SelectItem value="positive">{t.retours.positif}</SelectItem>
                  <SelectItem value="negative">{t.retours.negatif}</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {/* Category Filter */}
            <div className="space-y-1">
              <label className="text-xs text-muted-foreground">
                {t.retours.categorie}
              </label>
              <Select value={categoryFilter} onValueChange={setCategoryFilter}>
                <SelectTrigger className="w-[160px]">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">
                    {t.retours.toutesCategories}
                  </SelectItem>
                  {categories.map((cat) => (
                    <SelectItem key={cat} value={cat.toLowerCase()}>
                      {cat}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Period Filter */}
            <div className="space-y-1">
              <label className="text-xs text-muted-foreground">
                {t.retours.periode}
              </label>
              <Select value={periodFilter} onValueChange={setPeriodFilter}>
                <SelectTrigger className="w-[150px]">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">{t.retours.toutTemps}</SelectItem>
                  <SelectItem value="7d">{t.retours.derniers7Jours}</SelectItem>
                  <SelectItem value="30d">
                    {t.retours.derniers30Jours}
                  </SelectItem>
                </SelectContent>
              </Select>
            </div>

            {/* Sort */}
            <div className="space-y-1">
              <label className="text-xs text-muted-foreground">
                {t.retours.trier}
              </label>
              <Select value={sortBy} onValueChange={setSortBy}>
                <SelectTrigger className="w-[150px]">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="date">{t.retours.dateRecente}</SelectItem>
                  <SelectItem value="gap">{t.retours.ecartPlusGrand}</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Main Table */}
      <Card>
        <CardContent className="p-0">
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
            </div>
          ) : error ? (
            <div className="flex items-center justify-center gap-2 py-12 text-destructive">
              <AlertCircle className="h-5 w-5" />
              <span>{error}</span>
            </div>
          ) : feedback.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-12 text-center">
              <MessageSquare className="h-12 w-12 text-muted-foreground/50 mb-4" />
              <p className="text-lg font-medium">{t.retours.aucunRetour}</p>
              <p className="text-sm text-muted-foreground mt-1">
                {t.retours.aucunRetourDesc}
              </p>
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-[100px]">{t.retours.date}</TableHead>
                  <TableHead>{t.retours.categorie}</TableHead>
                  <TableHead className="text-right">
                    {t.retours.superficie}
                  </TableHead>
                  <TableHead className="text-right">
                    {t.retours.prixEstime}
                  </TableHead>
                  <TableHead className="text-right">
                    {t.retours.vraiPrix}
                  </TableHead>
                  <TableHead className="text-right">{t.retours.ecart}</TableHead>
                  <TableHead className="text-center">
                    {t.retours.verdict}
                  </TableHead>
                  <TableHead>{t.retours.raison}</TableHead>
                  <TableHead className="w-[40px]"></TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {feedback.map((entry) => (
                  <Collapsible
                    key={entry.id}
                    open={expandedRow === entry.id}
                    onOpenChange={(open) =>
                      setExpandedRow(open ? entry.id : null)
                    }
                    asChild
                  >
                    <>
                      <TableRow className="cursor-pointer hover:bg-muted/50">
                        <TableCell className="font-medium">
                          {formatDate(entry.created_at)}
                        </TableCell>
                        <TableCell>{entry.category || "-"}</TableCell>
                        <TableCell className="text-right tabular-nums">
                          {entry.sqft?.toLocaleString() || "-"}
                        </TableCell>
                        <TableCell className="text-right tabular-nums">
                          {formatCurrency(entry.predicted_price)}
                        </TableCell>
                        <TableCell className="text-right tabular-nums">
                          {formatCurrency(entry.actual_price)}
                        </TableCell>
                        <TableCell
                          className={`text-right tabular-nums font-medium ${getGapColor(entry.price_gap_percent)}`}
                        >
                          {entry.price_gap !== null && entry.price_gap_percent !== null
                            ? `${entry.price_gap > 0 ? "+" : ""}${formatCurrency(entry.price_gap)} (${entry.price_gap_percent > 0 ? "+" : ""}${entry.price_gap_percent.toFixed(1)}%)`
                            : "-"}
                        </TableCell>
                        <TableCell className="text-center">
                          {entry.feedback === "positive" ? (
                            <ThumbsUp className="h-5 w-5 text-green-600 mx-auto" />
                          ) : (
                            <ThumbsDown className="h-5 w-5 text-red-600 mx-auto" />
                          )}
                        </TableCell>
                        <TableCell className="max-w-[200px] truncate">
                          {entry.reason || "-"}
                        </TableCell>
                        <TableCell>
                          <CollapsibleTrigger asChild>
                            <Button variant="ghost" size="sm">
                              {expandedRow === entry.id ? (
                                <ChevronUp className="h-4 w-4" />
                              ) : (
                                <ChevronDown className="h-4 w-4" />
                              )}
                            </Button>
                          </CollapsibleTrigger>
                        </TableCell>
                      </TableRow>
                      <CollapsibleContent asChild>
                        <TableRow className="bg-muted/30">
                          <TableCell colSpan={9} className="p-4">
                            <ExpandedDetails entry={entry} t={t} />
                          </TableCell>
                        </TableRow>
                      </CollapsibleContent>
                    </>
                  </Collapsible>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>

        {/* Pagination */}
        {feedback.length > 0 && (
          <div className="flex items-center justify-between border-t p-4">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page === 1}
            >
              {t.common.precedent}
            </Button>
            <span className="text-sm text-muted-foreground">
              {t.common.page} {page}
            </span>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setPage((p) => p + 1)}
              disabled={!hasMore}
            >
              {t.common.suivant}
            </Button>
          </div>
        )}
      </Card>

      {/* Insights Section */}
      {summary && summary.total_count > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>{t.retours.insights}</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid gap-6 md:grid-cols-3">
              {/* Under-estimated categories */}
              <div>
                <h4 className="text-sm font-medium flex items-center gap-2 mb-3">
                  <TrendingDown className="h-4 w-4 text-red-600" />
                  {t.retours.categoriesSousEstimees}
                </h4>
                <InsightsList feedback={feedback} type="under" t={t} />
              </div>

              {/* Over-estimated categories */}
              <div>
                <h4 className="text-sm font-medium flex items-center gap-2 mb-3">
                  <TrendingUp className="h-4 w-4 text-blue-600" />
                  {t.retours.categoriesSurestimees}
                </h4>
                <InsightsList feedback={feedback} type="over" t={t} />
              </div>

              {/* Missing materials */}
              <div>
                <h4 className="text-sm font-medium flex items-center gap-2 mb-3">
                  <Package className="h-4 w-4 text-amber-600" />
                  {t.retours.materiauxManquants}
                </h4>
                <MissingMaterialsList feedback={feedback} t={t} />
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

// Expanded row details component
function ExpandedDetails({
  entry,
  t,
}: {
  entry: FeedbackEntry;
  t: ReturnType<typeof useLanguage>["t"];
}) {
  return (
    <div className="grid gap-4 md:grid-cols-2">
      {/* Input Parameters */}
      <div>
        <h4 className="text-sm font-medium mb-2">{t.retours.parametresEntree}</h4>
        <div className="rounded-lg bg-background p-3 text-sm space-y-1">
          {Object.entries(entry.input_params).map(([key, value]) => (
            <div key={key} className="flex justify-between">
              <span className="text-muted-foreground">{key}:</span>
              <span className="font-mono">{String(value)}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Materials if available */}
      {entry.predicted_materials && entry.predicted_materials.length > 0 && (
        <div>
          <h4 className="text-sm font-medium mb-2">{t.retours.listeMateriaux}</h4>
          <div className="rounded-lg bg-background p-3 text-sm max-h-[150px] overflow-y-auto">
            {entry.predicted_materials.map((mat, idx) => (
              <div key={idx} className="flex justify-between py-1 border-b last:border-0">
                <span>#{String(mat.material_id || mat.id || idx)}</span>
                <span className="font-mono">
                  {String(mat.quantity || "-")} × {String(mat.unit_price || "-")}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Full Reason */}
      {entry.reason && (
        <div className="md:col-span-2">
          <h4 className="text-sm font-medium mb-2">{t.retours.raisonComplete}</h4>
          <div className="rounded-lg bg-background p-3 text-sm">
            {entry.reason}
          </div>
        </div>
      )}
    </div>
  );
}

// Insights list component
function InsightsList({
  feedback,
  type,
  t,
}: {
  feedback: FeedbackEntry[];
  type: "under" | "over";
  t: ReturnType<typeof useLanguage>["t"];
}) {
  // Calculate category insights
  const categoryStats: Record<string, { count: number; totalGap: number }> = {};

  feedback.forEach((entry) => {
    if (!entry.category || entry.price_gap === null) return;

    const isUnder = entry.price_gap > 0; // actual > predicted = under-estimated
    if ((type === "under" && isUnder) || (type === "over" && !isUnder)) {
      if (!categoryStats[entry.category]) {
        categoryStats[entry.category] = { count: 0, totalGap: 0 };
      }
      categoryStats[entry.category].count++;
      categoryStats[entry.category].totalGap += Math.abs(entry.price_gap);
    }
  });

  const sortedCategories = Object.entries(categoryStats)
    .sort((a, b) => b[1].count - a[1].count)
    .slice(0, 3);

  if (sortedCategories.length === 0) {
    return <p className="text-sm text-muted-foreground">{t.retours.aucunesDonnees}</p>;
  }

  return (
    <ul className="space-y-2">
      {sortedCategories.map(([category, stats]) => (
        <li
          key={category}
          className="flex justify-between items-center text-sm p-2 rounded bg-muted/50"
        >
          <span>{category}</span>
          <span className="text-muted-foreground">{stats.count}x</span>
        </li>
      ))}
    </ul>
  );
}

// Missing materials list component
function MissingMaterialsList({
  feedback,
  t,
}: {
  feedback: FeedbackEntry[];
  t: ReturnType<typeof useLanguage>["t"];
}) {
  // Parse reasons for material mentions
  const materialMentions: Record<string, number> = {};
  const materialKeywords = [
    "bardeau",
    "membrane",
    "clou",
    "solin",
    "ventilation",
    "faîtière",
    "noue",
    "larmier",
    "sous-couche",
    "scellant",
  ];

  feedback.forEach((entry) => {
    if (!entry.reason) return;
    const reasonLower = entry.reason.toLowerCase();

    materialKeywords.forEach((keyword) => {
      if (reasonLower.includes(keyword)) {
        materialMentions[keyword] = (materialMentions[keyword] || 0) + 1;
      }
    });
  });

  const sortedMaterials = Object.entries(materialMentions)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 5);

  if (sortedMaterials.length === 0) {
    return <p className="text-sm text-muted-foreground">{t.retours.aucunesDonnees}</p>;
  }

  return (
    <ul className="space-y-2">
      {sortedMaterials.map(([material, count]) => (
        <li
          key={material}
          className="flex justify-between items-center text-sm p-2 rounded bg-muted/50"
        >
          <span className="capitalize">{material}</span>
          <span className="text-muted-foreground">{count}x</span>
        </li>
      ))}
    </ul>
  );
}
