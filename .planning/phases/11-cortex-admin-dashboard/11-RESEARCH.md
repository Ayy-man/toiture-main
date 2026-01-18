# Phase 11: Cortex Admin Dashboard - Research

**Researched:** 2026-01-18
**Domain:** Next.js Admin Dashboard with shadcn/ui, React Query, Recharts, FastAPI
**Confidence:** HIGH

## Summary

This phase transforms the existing simple estimate form into a professional 4-tab admin dashboard. The dashboard architecture uses shadcn/ui's Sidebar component for navigation with a dark sidebar (#1A1A1A) and brick red accents (#8B2323). Each tab (Estimateur, Historique, Apercu, Clients) represents a distinct functional area with its own data requirements and UI patterns.

The existing codebase provides strong foundations: React Query is already configured with 5-min staleTime, TanStack Table exists with a generic DataTable component, Recharts chart components are set up, and the Supabase client with RPC pattern is established. The streaming SSE implementation from Phase 9 is already working in the `/estimate/stream` endpoint.

**Primary recommendation:** Leverage existing patterns and components. Build the dashboard as a sidebar layout with route-based tab switching using Next.js App Router nested layouts. Use server-side pagination for Historique (8,293 records) and Supabase full-text search with GIN indexes for customer lookup.

## Standard Stack

The established libraries/tools for this domain:

### Core (Already Installed)
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Next.js | 16.1.3 | Framework | Already in use, App Router for layout/routing |
| shadcn/ui | latest | UI Components | Already in use, includes Sidebar component |
| Tailwind CSS | 4.x | Styling | Already configured with CSS variables |
| React Query | 5.90.x | Data fetching | Already configured with 5-min staleTime |
| TanStack Table | 8.21.x | Data tables | Already in use with generic DataTable |
| Recharts | 2.15.x | Charts | Already in use with ChartContainer wrapper |
| Supabase JS | 2.90.x | Database client | Already configured with RPC pattern |
| Zod | 4.3.x | Validation | Already in use for form schemas |
| date-fns | 4.1.x | Date utilities | Already installed |
| lucide-react | 0.562.x | Icons | Already in use |

### Supporting (May Need to Add)
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| next-themes | 0.4.x | Theme toggle | For dark/light mode (already used by shadcn) |
| @tanstack/react-query-devtools | 5.x | Debugging | Development only |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| shadcn/ui Sidebar | Custom sidebar | shadcn Sidebar is composable, handles mobile/desktop |
| URL-synced tabs | Client-side tabs state | URL-synced enables deep linking and browser back |
| Supabase full-text | External search (Algolia) | Supabase FTS is sufficient for <10k customers |
| Server-side pagination | Client-side pagination | Required for 8,293+ records performance |

**Installation:**
```bash
# shadcn/ui Sidebar component (if not installed)
npx shadcn@latest add sidebar

# May need Badge, Skeleton, Sheet components
npx shadcn@latest add badge skeleton sheet separator
```

## Architecture Patterns

### Recommended Project Structure
```
frontend/src/
├── app/
│   ├── (admin)/                    # Route group for admin dashboard
│   │   ├── layout.tsx              # Sidebar layout wrapper
│   │   ├── estimateur/
│   │   │   ├── page.tsx            # Prix sub-view (default)
│   │   │   ├── materiaux/
│   │   │   │   └── page.tsx        # Materiaux sub-view
│   │   │   └── complet/
│   │   │       └── page.tsx        # Soumission Complete sub-view
│   │   ├── historique/
│   │   │   └── page.tsx            # Quote browser with pagination
│   │   ├── apercu/
│   │   │   └── page.tsx            # Business metrics dashboard
│   │   └── clients/
│   │       └── page.tsx            # Customer lookup
│   ├── login/                      # Existing auth
│   └── page.tsx                    # Redirect to /estimateur
├── components/
│   ├── admin/
│   │   ├── sidebar.tsx             # Admin sidebar navigation
│   │   ├── sidebar-nav.tsx         # Navigation items
│   │   └── mobile-nav.tsx          # Mobile sheet navigation
│   ├── estimateur/
│   │   ├── price-form.tsx          # Prix estimate form
│   │   ├── materials-form.tsx      # Materiaux prediction form
│   │   └── full-quote-form.tsx     # Complete submission form
│   ├── historique/
│   │   ├── quote-table.tsx         # Paginated quote browser
│   │   ├── quote-columns.tsx       # Column definitions
│   │   └── quote-filters.tsx       # Filter controls
│   ├── apercu/
│   │   ├── metrics-cards.tsx       # KPI stat cards
│   │   ├── revenue-chart.tsx       # Revenue by year/category
│   │   ├── margin-chart.tsx        # Margin analysis
│   │   ├── seasonality-chart.tsx   # Monthly trends
│   │   └── top-clients.tsx         # Top client list
│   └── clients/
│       ├── customer-search.tsx     # Search input
│       ├── customer-card.tsx       # Customer detail display
│       ├── segment-badge.tsx       # Customer segment badges
│       └── quote-history.tsx       # Customer quote history
├── lib/
│   ├── hooks/
│   │   ├── use-quotes.ts           # Quote fetching with pagination
│   │   ├── use-customers.ts        # Customer search
│   │   └── use-dashboard-metrics.ts # Dashboard aggregations
│   └── api/
│       ├── quotes.ts               # Quote API client
│       ├── customers.ts            # Customer API client
│       └── dashboard.ts            # Dashboard metrics API
└── types/
    ├── quote.ts                    # Quote types
    ├── customer.ts                 # Customer types
    └── dashboard.ts                # Dashboard metric types
```

### Pattern 1: Sidebar Layout with Route-Based Navigation
**What:** Use shadcn/ui SidebarProvider with Next.js nested layouts for persistent sidebar
**When to use:** Admin dashboards with multiple sections needing shared navigation
**Example:**
```typescript
// Source: shadcn/ui Sidebar docs + Next.js App Router patterns
// app/(admin)/layout.tsx
import { SidebarProvider, SidebarInset } from "@/components/ui/sidebar";
import { AdminSidebar } from "@/components/admin/sidebar";

export default function AdminLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <SidebarProvider defaultOpen>
      <AdminSidebar />
      <SidebarInset>
        <main className="flex-1 p-6">{children}</main>
      </SidebarInset>
    </SidebarProvider>
  );
}

// components/admin/sidebar.tsx
"use client";

import { usePathname } from "next/navigation";
import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
} from "@/components/ui/sidebar";
import {
  Calculator,
  History,
  LayoutDashboard,
  Users,
} from "lucide-react";
import Link from "next/link";

const navItems = [
  { title: "Estimateur", href: "/estimateur", icon: Calculator },
  { title: "Historique", href: "/historique", icon: History },
  { title: "Apercu", href: "/apercu", icon: LayoutDashboard },
  { title: "Clients", href: "/clients", icon: Users },
];

export function AdminSidebar() {
  const pathname = usePathname();

  return (
    <Sidebar
      variant="sidebar"
      collapsible="icon"
      className="bg-[#1A1A1A] text-white border-r-0"
    >
      <SidebarHeader className="p-4">
        <span className="text-xl font-bold text-[#8B2323]">
          Cortex
        </span>
      </SidebarHeader>
      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupLabel className="text-gray-400">
            Navigation
          </SidebarGroupLabel>
          <SidebarMenu>
            {navItems.map((item) => (
              <SidebarMenuItem key={item.href}>
                <SidebarMenuButton
                  asChild
                  isActive={pathname.startsWith(item.href)}
                  className="data-[active=true]:bg-[#8B2323]/20 data-[active=true]:text-[#8B2323]"
                >
                  <Link href={item.href}>
                    <item.icon className="h-4 w-4" />
                    <span>{item.title}</span>
                  </Link>
                </SidebarMenuButton>
              </SidebarMenuItem>
            ))}
          </SidebarMenu>
        </SidebarGroup>
      </SidebarContent>
    </Sidebar>
  );
}
```

### Pattern 2: Server-Side Pagination with React Query
**What:** Use `manualPagination` in TanStack Table with React Query for fetching
**When to use:** Tables with 1000+ records where client-side pagination is inefficient
**Example:**
```typescript
// Source: TanStack Table pagination guide + React Query docs
// lib/hooks/use-quotes.ts
"use client";

import { useQuery, keepPreviousData } from "@tanstack/react-query";
import { useState } from "react";

interface QuoteFilters {
  category?: string;
  city?: string;
  minSqft?: number;
  maxSqft?: number;
  minPrice?: number;
  maxPrice?: number;
  startDate?: string;
  endDate?: string;
}

interface PaginationState {
  pageIndex: number;
  pageSize: number;
}

export function useQuotes(initialFilters?: QuoteFilters) {
  const [pagination, setPagination] = useState<PaginationState>({
    pageIndex: 0,
    pageSize: 20,
  });
  const [filters, setFilters] = useState<QuoteFilters>(initialFilters ?? {});

  const query = useQuery({
    queryKey: ["quotes", pagination, filters],
    queryFn: async () => {
      const params = new URLSearchParams({
        page: String(pagination.pageIndex + 1),
        per_page: String(pagination.pageSize),
        ...Object.fromEntries(
          Object.entries(filters)
            .filter(([_, v]) => v !== undefined)
            .map(([k, v]) => [k, String(v)])
        ),
      });

      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/quotes?${params}`
      );
      if (!response.ok) throw new Error("Failed to fetch quotes");
      return response.json();
    },
    placeholderData: keepPreviousData, // Prevents flicker on page change
    staleTime: 1000 * 60 * 5,
  });

  return {
    ...query,
    pagination,
    setPagination,
    filters,
    setFilters,
    pageCount: query.data?.total_pages ?? 0,
  };
}
```

### Pattern 3: Debounced Search with Full-Text Search
**What:** Debounce search input, use Supabase FTS for customer lookup
**When to use:** Search inputs with API calls, prevents excessive requests
**Example:**
```typescript
// Source: Standard React debounce pattern + Supabase FTS docs
// lib/hooks/use-customers.ts
"use client";

import { useQuery } from "@tanstack/react-query";
import { useState, useDeferredValue } from "react";

export function useCustomerSearch() {
  const [searchTerm, setSearchTerm] = useState("");
  const deferredSearch = useDeferredValue(searchTerm);

  const query = useQuery({
    queryKey: ["customers", "search", deferredSearch],
    queryFn: async () => {
      if (!deferredSearch || deferredSearch.length < 2) return [];

      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/customers/search?q=${encodeURIComponent(deferredSearch)}`
      );
      if (!response.ok) throw new Error("Search failed");
      return response.json();
    },
    enabled: deferredSearch.length >= 2,
    staleTime: 1000 * 60 * 5,
  });

  return {
    searchTerm,
    setSearchTerm,
    results: query.data ?? [],
    isSearching: query.isFetching,
    isStale: searchTerm !== deferredSearch,
  };
}
```

### Pattern 4: French (Quebec) Localization Pattern
**What:** Centralize French translations in constants, use throughout UI
**When to use:** All user-facing text in the dashboard
**Example:**
```typescript
// lib/i18n/fr.ts
export const fr = {
  nav: {
    estimateur: "Estimateur",
    historique: "Historique",
    apercu: "Apercu",
    clients: "Clients",
  },
  estimateur: {
    prix: "Prix",
    materiaux: "Materiaux",
    soumissionComplete: "Soumission Complete",
    superficie: "Superficie (pi2)",
    categorie: "Categorie",
    obtenirEstimation: "Obtenir l'estimation",
    enChargement: "Chargement...",
  },
  historique: {
    titre: "Historique des soumissions",
    filtres: "Filtres",
    categorie: "Categorie",
    ville: "Ville",
    dateDebut: "Date debut",
    dateFin: "Date fin",
    exporter: "Exporter CSV",
    aucunResultat: "Aucun resultat",
  },
  apercu: {
    titre: "Tableau de bord",
    revenuTotal: "Revenu total",
    nombreSoumissions: "Nombre de soumissions",
    margeMovenne: "Marge moyenne",
    clientsActifs: "Clients actifs",
  },
  clients: {
    rechercher: "Rechercher un client...",
    valeurVie: "Valeur a vie",
    segment: "Segment",
    historique: "Historique des soumissions",
  },
  common: {
    chargement: "Chargement...",
    erreur: "Une erreur s'est produite",
    reessayer: "Reessayer",
    page: "Page",
    sur: "sur",
    precedent: "Precedent",
    suivant: "Suivant",
  },
} as const;

// Usage in component
import { fr } from "@/lib/i18n/fr";

<Button>{fr.estimateur.obtenirEstimation}</Button>
```

### Anti-Patterns to Avoid
- **Client-side pagination for 8000+ records:** Use server-side pagination with LIMIT/OFFSET or cursor-based
- **Fetching all data on mount:** Use lazy loading, pagination, and staleTime
- **Nested API calls in components:** Use React Query with proper queryKey dependencies
- **Inline French strings:** Centralize in translation file for maintainability
- **Re-rendering entire sidebar on navigation:** Use Next.js nested layouts for partial rendering

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Collapsible sidebar | Custom collapse logic | shadcn/ui Sidebar `collapsible="icon"` | Handles mobile, desktop, keyboard, persistence |
| Data table pagination | Manual page tracking | TanStack Table `manualPagination` | Handles edge cases, keyboard nav, a11y |
| Search debouncing | setTimeout/clearTimeout | `useDeferredValue` or React Query | Concurrent mode aware, cancellation handled |
| CSV export | Manual string building | react-csv or native Blob | Handles escaping, special chars, encoding |
| Theme persistence | localStorage manual | next-themes with shadcn | SSR-safe, flash prevention |
| Chart responsiveness | Manual resize handlers | Recharts ResponsiveContainer | Handles resize observer, cleanup |
| Form state | useState per field | react-hook-form (already used) | Validation, dirty state, performance |

**Key insight:** The existing codebase already has most patterns established. Extend rather than replace.

## Common Pitfalls

### Pitfall 1: OFFSET-based pagination performance degradation
**What goes wrong:** Query time increases linearly as user pages deeper (page 400+ takes seconds)
**Why it happens:** PostgreSQL must scan and discard OFFSET rows before returning LIMIT rows
**How to avoid:** For Historique with 8,293 records, OFFSET/LIMIT is acceptable (max ~400 pages of 20). Monitor query times. If degradation occurs, switch to cursor-based pagination using indexed column (created_at + id).
**Warning signs:** `/quotes` endpoint response time > 500ms on deep pages

### Pitfall 2: N+1 queries for customer lifetime value
**What goes wrong:** Fetching customer, then fetching their quotes separately in a loop
**Why it happens:** Natural to query customer first, then aggregate quotes
**How to avoid:** Create Supabase RPC function that computes lifetime value in single query with JOIN and aggregation
**Warning signs:** Customer detail page makes multiple sequential API calls

### Pitfall 3: SSE connection not closing on component unmount
**What goes wrong:** EventSource connections accumulate, causing memory leaks and server load
**Why it happens:** Missing cleanup in useEffect when using EventSource
**How to avoid:** Always close EventSource in cleanup function. Existing code in estimate-form.tsx handles this correctly - follow that pattern.
**Warning signs:** Browser DevTools shows multiple open SSE connections

### Pitfall 4: Sidebar state flash on page load
**What goes wrong:** Sidebar briefly shows wrong state (open/closed) on hydration
**Why it happens:** Server renders default state, client hydrates with persisted state
**How to avoid:** shadcn/ui SidebarProvider uses cookies for persistence, ensuring server and client match
**Warning signs:** Sidebar "jumps" on initial page load

### Pitfall 5: React Query cache invalidation on mutations
**What goes wrong:** Data becomes stale after creating new estimate, user sees old data
**Why it happens:** Mutations don't automatically invalidate related queries
**How to avoid:** Use `queryClient.invalidateQueries` after mutations, or use optimistic updates
**Warning signs:** User must refresh page to see new data

### Pitfall 6: French accent encoding in CSV export
**What goes wrong:** "Elastomere" instead of "Elastomere", question marks or garbled text
**Why it happens:** Wrong character encoding or missing BOM for Excel
**How to avoid:** Use UTF-8 encoding with BOM (`\uFEFF` prefix) for Excel compatibility
**Warning signs:** Downloaded CSV shows encoding issues in Excel

## Code Examples

Verified patterns from official sources and existing codebase:

### Custom CSS Variables for Brick Red Theme
```typescript
// Source: shadcn/ui theming docs + existing globals.css pattern
// Add to globals.css in :root and .dark

:root {
  /* Brick red accent for sidebar */
  --brick-red: oklch(0.45 0.18 25);
  --brick-red-foreground: oklch(0.98 0 0);

  /* Dark sidebar colors */
  --sidebar-dark: oklch(0.15 0 0);
  --sidebar-dark-foreground: oklch(0.9 0 0);
  --sidebar-dark-accent: oklch(0.45 0.18 25);
  --sidebar-dark-muted: oklch(0.25 0 0);
}

@theme inline {
  --color-brick-red: var(--brick-red);
  --color-brick-red-foreground: var(--brick-red-foreground);
  --color-sidebar-dark: var(--sidebar-dark);
  --color-sidebar-dark-foreground: var(--sidebar-dark-foreground);
  --color-sidebar-dark-accent: var(--sidebar-dark-accent);
  --color-sidebar-dark-muted: var(--sidebar-dark-muted);
}
```

### FastAPI Paginated Endpoint
```python
# Source: FastAPI docs + SQLModel pagination pattern
# backend/app/routers/quotes.py

from fastapi import APIRouter, Query
from pydantic import BaseModel
from typing import List, Optional
from app.services.supabase_client import get_supabase

router = APIRouter(prefix="/quotes", tags=["quotes"])

class QuoteItem(BaseModel):
    id: str
    client_name: str
    category: str
    city: str
    sqft: float
    total_price: float
    created_at: str

class PaginatedQuotes(BaseModel):
    items: List[QuoteItem]
    total: int
    page: int
    per_page: int
    total_pages: int

@router.get("", response_model=PaginatedQuotes)
def get_quotes(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    category: Optional[str] = None,
    city: Optional[str] = None,
    min_sqft: Optional[float] = None,
    max_sqft: Optional[float] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
):
    """Get paginated quotes with optional filters."""
    supabase = get_supabase()
    if supabase is None:
        return PaginatedQuotes(items=[], total=0, page=page, per_page=per_page, total_pages=0)

    # Build query with filters
    query = supabase.table("quotes").select("*", count="exact")

    if category:
        query = query.eq("category", category)
    if city:
        query = query.ilike("city", f"%{city}%")
    if min_sqft:
        query = query.gte("sqft", min_sqft)
    if max_sqft:
        query = query.lte("sqft", max_sqft)
    if min_price:
        query = query.gte("total_price", min_price)
    if max_price:
        query = query.lte("total_price", max_price)
    if start_date:
        query = query.gte("created_at", start_date)
    if end_date:
        query = query.lte("created_at", end_date)

    # Apply pagination
    offset = (page - 1) * per_page
    query = query.order("created_at", desc=True).range(offset, offset + per_page - 1)

    result = query.execute()

    total = result.count or 0
    total_pages = (total + per_page - 1) // per_page

    return PaginatedQuotes(
        items=[QuoteItem(**item) for item in result.data],
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages,
    )
```

### Customer Search with Full-Text Search
```python
# Source: Supabase FTS docs
# backend/app/routers/customers.py

from fastapi import APIRouter, Query
from typing import List
from pydantic import BaseModel

router = APIRouter(prefix="/customers", tags=["customers"])

class CustomerResult(BaseModel):
    id: str
    name: str
    city: str
    total_quotes: int
    lifetime_value: float
    segment: str  # "VIP", "Regular", "New"

@router.get("/search", response_model=List[CustomerResult])
def search_customers(
    q: str = Query(..., min_length=2),
    limit: int = Query(10, le=50),
):
    """Search customers by name using full-text search."""
    supabase = get_supabase()
    if supabase is None:
        return []

    # Uses PostgreSQL full-text search with GIN index
    # Requires: CREATE INDEX customers_name_fts ON customers USING GIN (to_tsvector('french', name));
    result = supabase.rpc(
        "search_customers",
        {"search_query": q, "result_limit": limit}
    ).execute()

    return [CustomerResult(**item) for item in result.data]
```

### TanStack Table with Server-Side Pagination
```typescript
// Source: TanStack Table docs + existing DataTable pattern
// components/historique/quote-table.tsx
"use client";

import {
  ColumnDef,
  flexRender,
  getCoreRowModel,
  useReactTable,
} from "@tanstack/react-table";
import { useQuotes } from "@/lib/hooks/use-quotes";
import { Button } from "@/components/ui/button";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { fr } from "@/lib/i18n/fr";

interface Quote {
  id: string;
  client_name: string;
  category: string;
  city: string;
  sqft: number;
  total_price: number;
  created_at: string;
}

const columns: ColumnDef<Quote>[] = [
  { accessorKey: "client_name", header: "Client" },
  { accessorKey: "category", header: "Categorie" },
  { accessorKey: "city", header: "Ville" },
  {
    accessorKey: "sqft",
    header: "Superficie",
    cell: ({ row }) => `${row.original.sqft.toLocaleString("fr-CA")} pi2`,
  },
  {
    accessorKey: "total_price",
    header: "Prix",
    cell: ({ row }) =>
      new Intl.NumberFormat("fr-CA", {
        style: "currency",
        currency: "CAD",
      }).format(row.original.total_price),
  },
  {
    accessorKey: "created_at",
    header: "Date",
    cell: ({ row }) =>
      new Date(row.original.created_at).toLocaleDateString("fr-CA"),
  },
];

export function QuoteTable() {
  const { data, pagination, setPagination, pageCount, isFetching } = useQuotes();

  const table = useReactTable({
    data: data?.items ?? [],
    columns,
    pageCount,
    state: { pagination },
    onPaginationChange: setPagination,
    getCoreRowModel: getCoreRowModel(),
    manualPagination: true,
  });

  return (
    <div className="space-y-4">
      <div className="rounded-md border">
        <Table>
          <TableHeader>
            {table.getHeaderGroups().map((headerGroup) => (
              <TableRow key={headerGroup.id}>
                {headerGroup.headers.map((header) => (
                  <TableHead key={header.id}>
                    {flexRender(
                      header.column.columnDef.header,
                      header.getContext()
                    )}
                  </TableHead>
                ))}
              </TableRow>
            ))}
          </TableHeader>
          <TableBody>
            {table.getRowModel().rows.map((row) => (
              <TableRow key={row.id}>
                {row.getVisibleCells().map((cell) => (
                  <TableCell key={cell.id}>
                    {flexRender(cell.column.columnDef.cell, cell.getContext())}
                  </TableCell>
                ))}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>

      <div className="flex items-center justify-between">
        <span className="text-sm text-muted-foreground">
          {fr.common.page} {pagination.pageIndex + 1} {fr.common.sur} {pageCount}
        </span>
        <div className="flex gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => table.previousPage()}
            disabled={!table.getCanPreviousPage()}
          >
            {fr.common.precedent}
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => table.nextPage()}
            disabled={!table.getCanNextPage()}
          >
            {fr.common.suivant}
          </Button>
        </div>
      </div>

      {isFetching && (
        <div className="absolute inset-0 bg-background/50 flex items-center justify-center">
          <span className="text-muted-foreground">{fr.common.chargement}</span>
        </div>
      )}
    </div>
  );
}
```

### CSV Export with BOM for French Characters
```typescript
// Source: Standard CSV export pattern with UTF-8 BOM
// lib/utils/csv-export.ts

export function exportToCSV(
  data: Record<string, unknown>[],
  filename: string
): void {
  if (data.length === 0) return;

  const headers = Object.keys(data[0]);
  const csvContent = [
    headers.join(","),
    ...data.map((row) =>
      headers
        .map((header) => {
          const value = row[header];
          // Escape quotes and wrap in quotes if contains comma
          const str = String(value ?? "").replace(/"/g, '""');
          return str.includes(",") || str.includes('"') || str.includes("\n")
            ? `"${str}"`
            : str;
        })
        .join(",")
    ),
  ].join("\n");

  // UTF-8 BOM for Excel French character support
  const BOM = "\uFEFF";
  const blob = new Blob([BOM + csvContent], {
    type: "text/csv;charset=utf-8;",
  });

  const link = document.createElement("a");
  link.href = URL.createObjectURL(blob);
  link.download = `${filename}.csv`;
  link.click();
  URL.revokeObjectURL(link.href);
}
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| keepPreviousData flag | `placeholderData: keepPreviousData` | React Query v5 | Use new API for pagination |
| CSS-in-JS theme toggle | CSS variables with next-themes | 2024 | Better performance, no runtime |
| Client-side pagination | Server-side with manualPagination | Always for >1k rows | Required for 8,293 records |
| Manual resize handlers | ResponsiveContainer | Standard | Built-in cleanup |

**Deprecated/outdated:**
- `keepPreviousData: true` option in React Query (use `placeholderData: keepPreviousData` instead)
- Tailwind config file for shadcn/ui v2.0+ (use inline `@theme` in globals.css)

## Open Questions

Things that couldn't be fully resolved:

1. **Quotes and Customers table schema in Supabase**
   - What we know: Estimates table exists, feedback endpoints exist
   - What's unclear: Whether historical quotes data is already in Supabase or needs migration
   - Recommendation: Verify table structure, may need to create quotes/customers tables and seed with historical data

2. **Full-text search index existence**
   - What we know: Supabase supports PostgreSQL FTS with GIN indexes
   - What's unclear: Whether customers table has FTS index on name field
   - Recommendation: Plan includes creating GIN index if not exists

3. **Dashboard metrics computation method**
   - What we know: RPC pattern is established for analytics
   - What's unclear: Whether metrics should be computed on-demand or cached/materialized
   - Recommendation: Start with RPC functions, add materialized views if performance issues

## Sources

### Primary (HIGH confidence)
- [shadcn/ui Sidebar Component](https://ui.shadcn.com/docs/components/sidebar) - Sidebar API, variants, mobile handling
- [shadcn/ui Theming](https://ui.shadcn.com/docs/theming) - CSS variables, custom colors
- [TanStack Table Pagination Guide](https://tanstack.com/table/v8/docs/guide/pagination) - Server-side pagination
- [TanStack Query Paginated Queries](https://tanstack.com/query/latest/docs/framework/react/guides/paginated-queries) - keepPreviousData pattern
- [Supabase Full-Text Search](https://supabase.com/docs/guides/database/full-text-search) - PostgreSQL FTS with GIN

### Secondary (MEDIUM confidence)
- [Next.js App Router Layouts](https://nextjs.org/learn/dashboard-app/creating-layouts-and-pages) - Nested layout pattern
- [FastAPI Pagination Patterns](https://sqlmodel.tiangolo.com/tutorial/fastapi/limit-and-offset/) - OFFSET/LIMIT implementation

### Tertiary (LOW confidence - validate)
- Community articles on OFFSET pagination performance - may need cursor-based for very deep pages
- react-csv library status - last update 4 years ago, may prefer native implementation

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - All libraries already installed and working
- Architecture: HIGH - Patterns match existing codebase conventions
- Pitfalls: MEDIUM - Based on common issues, project-specific edge cases may exist
- Backend endpoints: MEDIUM - Schema details need verification

**Research date:** 2026-01-18
**Valid until:** 2026-02-18 (30 days - stable stack, minimal churn expected)
