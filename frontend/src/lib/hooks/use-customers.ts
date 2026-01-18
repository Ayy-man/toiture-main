"use client";

import { useQuery } from "@tanstack/react-query";
import { useState, useDeferredValue } from "react";
import { searchCustomers, getCustomerDetail } from "@/lib/api/customers";

/**
 * Hook for searching customers with debounced input.
 * Uses useDeferredValue to prevent excessive re-renders during typing.
 */
export function useCustomerSearch() {
  const [searchTerm, setSearchTerm] = useState("");
  const deferredSearch = useDeferredValue(searchTerm);

  const query = useQuery({
    queryKey: ["customers", "search", deferredSearch],
    queryFn: () => searchCustomers(deferredSearch),
    enabled: deferredSearch.length >= 2,
    staleTime: 1000 * 60 * 5, // 5 minutes
  });

  return {
    searchTerm,
    setSearchTerm,
    results: query.data ?? [],
    isSearching: query.isFetching,
    isStale: query.isStale,
  };
}

/**
 * Hook for fetching customer details by ID.
 * Only fetches when customerId is provided.
 */
export function useCustomerDetail(customerId: string | null) {
  return useQuery({
    queryKey: ["customers", "detail", customerId],
    queryFn: () => getCustomerDetail(customerId!),
    enabled: !!customerId,
    staleTime: 1000 * 60 * 5, // 5 minutes
  });
}
