"use client";

import type { TopClient } from "@/types/dashboard";

interface TopClientsProps {
  clients: TopClient[] | undefined;
  isLoading: boolean;
}

/**
 * Format value as CAD currency.
 */
function formatCurrency(value: number): string {
  return new Intl.NumberFormat("fr-CA", {
    style: "currency",
    currency: "CAD",
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(value);
}

/**
 * Skeleton placeholder for loading state.
 */
function ClientSkeleton() {
  return (
    <div className="space-y-3">
      {Array.from({ length: 5 }).map((_, i) => (
        <div key={i} className="flex items-center gap-3">
          <div className="h-6 w-6 animate-pulse rounded-full bg-muted" />
          <div className="h-4 flex-1 animate-pulse rounded bg-muted" />
          <div className="h-4 w-20 animate-pulse rounded bg-muted" />
        </div>
      ))}
    </div>
  );
}

export function TopClients({ clients, isLoading }: TopClientsProps) {
  if (isLoading) {
    return <ClientSkeleton />;
  }

  if (!clients?.length) {
    return (
      <div className="flex h-[200px] items-center justify-center text-muted-foreground">
        Aucun client trouve
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {clients.map((client, index) => (
        <div
          key={client.name}
          className="flex items-center gap-3 rounded-lg p-2 hover:bg-muted/50 transition-colors"
        >
          <div className="flex h-6 w-6 items-center justify-center rounded-full bg-primary/10 text-xs font-medium text-primary">
            {index + 1}
          </div>
          <div className="flex-1 truncate font-medium">{client.name}</div>
          <div className="text-right">
            <div className="text-sm font-medium">{formatCurrency(client.total_spent)}</div>
            <div className="text-xs text-muted-foreground">
              {client.quote_count} soumission{client.quote_count > 1 ? "s" : ""}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
