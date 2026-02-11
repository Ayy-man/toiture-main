"use client";

import { useState } from "react";
import { Users } from "lucide-react";
import { useLanguage } from "@/lib/i18n";
import { useCustomerSearch, useCustomerDetail } from "@/lib/hooks/use-customers";
import { CustomerSearch } from "@/components/clients/customer-search";
import { CustomerCard } from "@/components/clients/customer-card";
import { QuoteHistory } from "@/components/clients/quote-history";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { CardSkeleton } from "@/components/shared/card-skeleton";
import { EmptyState } from "@/components/shared/empty-state";

export default function ClientsPage() {
  const { t } = useLanguage();
  const [selectedCustomerId, setSelectedCustomerId] = useState<string | null>(null);
  const { searchTerm, setSearchTerm, results, isSearching } = useCustomerSearch();
  const { data: customer, isLoading: isLoadingCustomer } = useCustomerDetail(selectedCustomerId);

  const handleSelectCustomer = (customerId: string) => {
    setSelectedCustomerId(customerId);
    setSearchTerm(""); // Clear search after selection
  };

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold tracking-tight">{t.nav.clients}</h1>

      <CustomerSearch
        searchTerm={searchTerm}
        onSearchChange={setSearchTerm}
        results={results}
        isSearching={isSearching}
        onSelectCustomer={handleSelectCustomer}
      />

      {!selectedCustomerId && (
        <EmptyState
          icon={Users}
          title={t.clients.rechercher}
          description="Search for a client above to view their details and quote history"
        />
      )}

      {selectedCustomerId && isLoadingCustomer && <CardSkeleton />}

      {customer && (
        <>
          <CustomerCard customer={customer} />

          <Card>
            <CardHeader>
              <CardTitle>{t.clients.historique}</CardTitle>
            </CardHeader>
            <CardContent>
              <QuoteHistory quotes={customer.quotes} />
            </CardContent>
          </Card>
        </>
      )}
    </div>
  );
}
