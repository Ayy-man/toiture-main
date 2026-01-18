"use client";

import { useState } from "react";
import { useQuery, keepPreviousData } from "@tanstack/react-query";
import { fetchQuotes } from "@/lib/api/quotes";
import type { QuoteFilters, PaginatedQuotes } from "@/types/quote";

export interface PaginationState {
  pageIndex: number;
  pageSize: number;
}

/**
 * Hook for fetching paginated quotes with filters.
 * Uses React Query with keepPreviousData to prevent flicker on page changes.
 */
export function useQuotes() {
  const [pagination, setPagination] = useState<PaginationState>({
    pageIndex: 0,
    pageSize: 20,
  });
  const [filters, setFilters] = useState<QuoteFilters>({});

  const query = useQuery<PaginatedQuotes>({
    queryKey: ["quotes", pagination, filters],
    queryFn: () =>
      fetchQuotes(pagination.pageIndex + 1, pagination.pageSize, filters),
    placeholderData: keepPreviousData,
    staleTime: 1000 * 60 * 5, // 5 minutes
  });

  const pageCount = query.data?.total_pages ?? 0;

  return {
    ...query,
    pagination,
    setPagination,
    filters,
    setFilters,
    pageCount,
  };
}
