"use client";

import {
  flexRender,
  getCoreRowModel,
  useReactTable,
} from "@tanstack/react-table";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { useLanguage } from "@/lib/i18n";
import { columns } from "./quote-columns";
import type { Quote } from "@/types/quote";
import type { PaginationState } from "@/lib/hooks/use-quotes";

interface QuoteTableProps {
  data: Quote[];
  pagination: PaginationState;
  setPagination: (pagination: PaginationState) => void;
  pageCount: number;
  isFetching: boolean;
}

/**
 * Paginated quote table with server-side pagination.
 * Shows loading overlay during data fetches.
 */
export function QuoteTable({
  data,
  pagination,
  setPagination,
  pageCount,
  isFetching,
}: QuoteTableProps) {
  const { t } = useLanguage();
  const table = useReactTable({
    data,
    columns,
    pageCount,
    state: { pagination },
    onPaginationChange: (updater) => {
      const newState =
        typeof updater === "function" ? updater(pagination) : updater;
      setPagination(newState);
    },
    getCoreRowModel: getCoreRowModel(),
    manualPagination: true,
  });

  return (
    <div className="space-y-4">
      <div className="relative rounded-md border">
        {/* Loading overlay */}
        {isFetching && (
          <div className="absolute inset-0 bg-background/50 flex items-center justify-center z-10">
            <span className="text-muted-foreground">
              {t.common.chargement}
            </span>
          </div>
        )}

        <Table>
          <TableHeader>
            {table.getHeaderGroups().map((headerGroup) => (
              <TableRow key={headerGroup.id}>
                {headerGroup.headers.map((header) => (
                  <TableHead key={header.id}>
                    {header.isPlaceholder
                      ? null
                      : flexRender(
                          header.column.columnDef.header,
                          header.getContext()
                        )}
                  </TableHead>
                ))}
              </TableRow>
            ))}
          </TableHeader>
          <TableBody>
            {table.getRowModel().rows?.length ? (
              table.getRowModel().rows.map((row) => (
                <TableRow key={row.id}>
                  {row.getVisibleCells().map((cell) => (
                    <TableCell key={cell.id}>
                      {flexRender(
                        cell.column.columnDef.cell,
                        cell.getContext()
                      )}
                    </TableCell>
                  ))}
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell
                  colSpan={columns.length}
                  className="h-24 text-center"
                >
                  {t.historique.aucunResultat}
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>

      {/* Pagination controls */}
      <div className="flex items-center justify-between">
        <div className="text-sm text-muted-foreground">
          {t.common.page} {pagination.pageIndex + 1} {t.common.sur}{" "}
          {pageCount || 1}
        </div>
        <div className="flex gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() =>
              setPagination({
                ...pagination,
                pageIndex: pagination.pageIndex - 1,
              })
            }
            disabled={pagination.pageIndex === 0}
          >
            {t.common.precedent}
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() =>
              setPagination({
                ...pagination,
                pageIndex: pagination.pageIndex + 1,
              })
            }
            disabled={pagination.pageIndex >= pageCount - 1}
          >
            {t.common.suivant}
          </Button>
        </div>
      </div>
    </div>
  );
}
