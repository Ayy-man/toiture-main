"use client";

import { Badge } from "@/components/ui/badge";
import { useLanguage } from "@/lib/i18n";
import type { SubmissionStatus } from "@/types/submission";

interface SubmissionStatusBadgeProps {
  status: SubmissionStatus;
}

/**
 * Color-coded status badge for submission workflow
 *
 * - draft: gray
 * - pending_approval: amber
 * - approved: green
 * - rejected: red
 */
export function SubmissionStatusBadge({ status }: SubmissionStatusBadgeProps) {
  const { t } = useLanguage();

  // Map status to label and styling
  const statusConfig: Record<SubmissionStatus, { label: string; className: string }> = {
    draft: {
      label: t.submission.statusDraft,
      className: "bg-gray-100 text-gray-700 border-gray-300",
    },
    pending_approval: {
      label: t.submission.statusPending,
      className: "bg-amber-100 text-amber-700 border-amber-300",
    },
    approved: {
      label: t.submission.statusApproved,
      className: "bg-green-100 text-green-700 border-green-300",
    },
    rejected: {
      label: t.submission.statusRejected,
      className: "bg-red-100 text-red-700 border-red-300",
    },
  };

  const config = statusConfig[status];

  return (
    <Badge variant="outline" className={config.className}>
      {config.label}
    </Badge>
  );
}
