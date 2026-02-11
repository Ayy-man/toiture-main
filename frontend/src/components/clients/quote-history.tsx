import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import type { CustomerQuote } from "@/types/customer";

interface QuoteHistoryProps {
  quotes: CustomerQuote[];
}

const currencyFormatter = new Intl.NumberFormat("fr-CA", {
  style: "currency",
  currency: "CAD",
});

const dateFormatter = new Intl.DateTimeFormat("fr-CA", {
  year: "numeric",
  month: "short",
  day: "numeric",
});

export function QuoteHistory({ quotes }: QuoteHistoryProps) {
  if (quotes.length === 0) {
    return (
      <div className="text-center py-8 text-muted-foreground">
        Aucune soumission
      </div>
    );
  }

  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Date</TableHead>
          <TableHead>Categorie</TableHead>
          <TableHead>Superficie</TableHead>
          <TableHead className="text-right">Prix</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {quotes.map((quote) => (
          <TableRow key={quote.id} className="hover:bg-muted/50 transition-colors">
            <TableCell>
              {dateFormatter.format(new Date(quote.created_at))}
            </TableCell>
            <TableCell>{quote.category || "-"}</TableCell>
            <TableCell>
              {quote.sqft ? `${quote.sqft.toLocaleString("fr-CA")} pi2` : "-"}
            </TableCell>
            <TableCell className="text-right">
              {quote.total_price
                ? currencyFormatter.format(quote.total_price)
                : "-"}
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}
