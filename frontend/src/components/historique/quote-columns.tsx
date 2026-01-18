import { ColumnDef } from "@tanstack/react-table";
import type { Quote } from "@/types/quote";

/**
 * Column definitions for the quotes table.
 * Uses French locale formatting for numbers and dates.
 */
export const columns: ColumnDef<Quote>[] = [
  {
    accessorKey: "client_name",
    header: "Client",
    cell: ({ row }) => row.original.client_name || "-",
  },
  {
    accessorKey: "category",
    header: "Categorie",
    cell: ({ row }) => row.original.category || "-",
  },
  {
    accessorKey: "city",
    header: "Ville",
    cell: ({ row }) => row.original.city || "-",
  },
  {
    accessorKey: "sqft",
    header: "Superficie",
    cell: ({ row }) => {
      const sqft = row.original.sqft;
      if (sqft === null) return "-";
      return `${sqft.toLocaleString("fr-CA")} pi2`;
    },
  },
  {
    accessorKey: "total_price",
    header: "Prix",
    cell: ({ row }) => {
      const price = row.original.total_price;
      if (price === null) return "-";
      return new Intl.NumberFormat("fr-CA", {
        style: "currency",
        currency: "CAD",
      }).format(price);
    },
  },
  {
    accessorKey: "margin_percent",
    header: "Marge",
    cell: ({ row }) => {
      const margin = row.original.margin_percent;
      if (margin === null) return "-";
      return `${margin.toFixed(1)}%`;
    },
  },
  {
    accessorKey: "created_at",
    header: "Date",
    cell: ({ row }) => {
      const date = new Date(row.original.created_at);
      return date.toLocaleDateString("fr-CA");
    },
  },
];
