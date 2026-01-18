"use client";

import { useState } from "react";
import { fr } from "@/lib/i18n/fr";
import { useCustomerSearch, useCustomerDetail } from "@/lib/hooks/use-customers";
import { CustomerSearch } from "@/components/clients/customer-search";
import { CustomerCard } from "@/components/clients/customer-card";
import { QuoteHistory } from "@/components/clients/quote-history";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";

export default function ClientsPage() {
  const [selectedCustomerId, setSelectedCustomerId] = useState<string | null>(null);
  const { searchTerm, setSearchTerm, results, isSearching } = useCustomerSearch();
  const { data: customer, isLoading: isLoadingCustomer } = useCustomerDetail(selectedCustomerId);

  const handleSelectCustomer = (customerId: string) => {
    setSelectedCustomerId(customerId);
    setSearchTerm(""); // Clear search after selection
  };

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold tracking-tight">{fr.nav.clients}</h1>

      <CustomerSearch
        searchTerm={searchTerm}
        onSearchChange={setSearchTerm}
        results={results}
        isSearching={isSearching}
        onSelectCustomer={handleSelectCustomer}
      />

      {selectedCustomerId && isLoadingCustomer && (
        <Card>
          <CardContent className="py-8">
            <div className="text-center text-muted-foreground">
              {fr.common.chargement}
            </div>
          </CardContent>
        </Card>
      )}

      {customer && (
        <>
          <CustomerCard customer={customer} />

          <Card>
            <CardHeader>
              <CardTitle>{fr.clients.historique}</CardTitle>
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
