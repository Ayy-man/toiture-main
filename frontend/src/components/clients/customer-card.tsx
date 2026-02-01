"use client";

import {
  Card,
  CardHeader,
  CardTitle,
  CardContent,
} from "@/components/ui/card";
import { useLanguage } from "@/lib/i18n";
import { SegmentBadge } from "./segment-badge";
import type { CustomerDetail } from "@/types/customer";

interface CustomerCardProps {
  customer: CustomerDetail;
}

const currencyFormatter = new Intl.NumberFormat("fr-CA", {
  style: "currency",
  currency: "CAD",
});

export function CustomerCard({ customer }: CustomerCardProps) {
  const { t } = useLanguage();
  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="text-xl">{customer.name}</CardTitle>
          <SegmentBadge segment={customer.segment} />
        </div>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
          {customer.city && (
            <div>
              <div className="text-sm text-muted-foreground">Ville</div>
              <div className="font-medium">{customer.city}</div>
            </div>
          )}

          {customer.phone && (
            <div>
              <div className="text-sm text-muted-foreground">Telephone</div>
              <div className="font-medium">{customer.phone}</div>
            </div>
          )}

          {customer.email && (
            <div>
              <div className="text-sm text-muted-foreground">Courriel</div>
              <div className="font-medium truncate">{customer.email}</div>
            </div>
          )}

          <div>
            <div className="text-sm text-muted-foreground">
              {t.clients.historique}
            </div>
            <div className="font-medium">{customer.total_quotes}</div>
          </div>

          <div>
            <div className="text-sm text-muted-foreground">
              {t.clients.valeurVie}
            </div>
            <div className="font-medium">
              {currencyFormatter.format(customer.lifetime_value)}
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
