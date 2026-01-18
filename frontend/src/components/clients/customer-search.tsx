"use client";

import { Input } from "@/components/ui/input";
import { Card } from "@/components/ui/card";
import { fr } from "@/lib/i18n/fr";
import { SegmentBadge } from "./segment-badge";
import type { CustomerResult } from "@/types/customer";

interface CustomerSearchProps {
  searchTerm: string;
  onSearchChange: (value: string) => void;
  results: CustomerResult[];
  isSearching: boolean;
  onSelectCustomer: (customerId: string) => void;
}

const currencyFormatter = new Intl.NumberFormat("fr-CA", {
  style: "currency",
  currency: "CAD",
});

export function CustomerSearch({
  searchTerm,
  onSearchChange,
  results,
  isSearching,
  onSelectCustomer,
}: CustomerSearchProps) {
  const showDropdown = searchTerm.length >= 2;
  const showNoResults = showDropdown && !isSearching && results.length === 0;

  return (
    <div className="relative w-full max-w-md">
      <Input
        type="text"
        placeholder={fr.clients.rechercher}
        value={searchTerm}
        onChange={(e) => onSearchChange(e.target.value)}
        className="w-full"
      />

      {showDropdown && (
        <Card className="absolute top-full left-0 right-0 mt-1 z-50 max-h-80 overflow-y-auto py-2">
          {isSearching && (
            <div className="px-4 py-2 text-sm text-muted-foreground">
              {fr.common.chargement}
            </div>
          )}

          {showNoResults && (
            <div className="px-4 py-2 text-sm text-muted-foreground">
              Aucun resultat
            </div>
          )}

          {!isSearching &&
            results.map((customer) => (
              <button
                key={customer.id}
                onClick={() => onSelectCustomer(customer.id)}
                className="w-full px-4 py-3 text-left hover:bg-muted/50 transition-colors flex items-center justify-between gap-4"
              >
                <div className="flex-1 min-w-0">
                  <div className="font-medium truncate">{customer.name}</div>
                  {customer.city && (
                    <div className="text-sm text-muted-foreground truncate">
                      {customer.city}
                    </div>
                  )}
                </div>
                <div className="flex items-center gap-3 shrink-0">
                  <span className="text-sm font-medium">
                    {currencyFormatter.format(customer.lifetime_value)}
                  </span>
                  <SegmentBadge segment={customer.segment} />
                </div>
              </button>
            ))}
        </Card>
      )}
    </div>
  );
}
