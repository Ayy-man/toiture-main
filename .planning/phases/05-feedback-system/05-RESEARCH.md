# Phase 5: Feedback System - Research

**Researched:** 2026-01-18
**Domain:** Supabase PostgreSQL, FastAPI database integration, Next.js data tables
**Confidence:** HIGH

## Summary

This phase implements a feedback loop system where Laurent can review AI estimates and enter actual prices. The system requires:

1. **Supabase PostgreSQL** for storing estimates and feedback data
2. **Python supabase-py client** (v2.27+) for FastAPI backend integration
3. **@supabase/ssr package** for Next.js App Router server/client components
4. **shadcn/ui Data Table** with TanStack Table for the review queue interface

The standard approach is to use Supabase's official Python client for sync operations (since the existing estimate endpoint is sync), create two tables (`estimates` and `feedback`), implement RLS policies for security, and build a review queue with shadcn's data table component using TanStack Table for pagination and sorting.

**Primary recommendation:** Use sync supabase-py client with service role key for backend (no RLS needed for internal app), create proper UUID primary keys with timestamps, and build review queue with TanStack Table + shadcn DataTable following existing shadcn patterns in the codebase.

## Standard Stack

The established libraries/tools for this domain:

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| supabase (Python) | 2.27.2+ | Backend database client | Official Supabase Python client |
| @supabase/supabase-js | latest | Frontend database client | Official Supabase JS client |
| @supabase/ssr | latest | Server-side auth/client | Official SSR package for Next.js App Router |
| @tanstack/react-table | 8.x | Data table logic | Standard for shadcn data tables |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| pydantic | 2.7+ | Request/response schemas | Already in use, extend for feedback |
| zod | 4.x | Frontend validation | Already in use, extend for feedback forms |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| supabase-py sync | supabase-py async | Async requires code restructure; existing endpoints are sync |
| Service role key | RLS with user auth | RLS adds complexity; this is internal admin app |
| TanStack Table | Simple HTML table | Loses pagination, sorting, filtering features |

**Installation:**

Backend:
```bash
pip install supabase
```

Frontend:
```bash
pnpm add @supabase/supabase-js @supabase/ssr @tanstack/react-table
pnpm dlx shadcn@latest add table
```

## Architecture Patterns

### Recommended Project Structure

```
backend/
├── app/
│   ├── services/
│   │   └── supabase_client.py    # Supabase client singleton
│   ├── routers/
│   │   ├── estimate.py           # Extended to save estimates
│   │   └── feedback.py           # NEW: Review queue endpoints
│   └── schemas/
│       └── feedback.py           # NEW: Feedback Pydantic models

frontend/
├── src/
│   ├── lib/
│   │   └── supabase/
│   │       ├── client.ts         # Browser client
│   │       └── server.ts         # Server client
│   ├── app/
│   │   └── review/
│   │       └── page.tsx          # Review queue page
│   └── components/
│       └── review/
│           ├── columns.tsx       # TanStack Table columns
│           └── data-table.tsx    # Reusable DataTable component
```

### Pattern 1: Supabase Client Singleton (Backend)

**What:** Single Supabase client instance initialized at startup
**When to use:** FastAPI applications with sync endpoints
**Example:**
```python
# Source: https://supabase.com/docs/reference/python/initializing
import os
from supabase import create_client, Client

_supabase_client: Client | None = None

def get_supabase() -> Client:
    """Get or create Supabase client singleton."""
    global _supabase_client
    if _supabase_client is None:
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
        _supabase_client = create_client(url, key)
    return _supabase_client
```

### Pattern 2: Save Estimate After Prediction

**What:** Extend existing estimate endpoint to save to Supabase after successful prediction
**When to use:** When you need to capture all estimates for later review
**Example:**
```python
# Source: https://supabase.com/docs/reference/python/insert
def save_estimate(request: EstimateRequest, response: EstimateResponse) -> str:
    """Save estimate to Supabase, return estimate_id."""
    supabase = get_supabase()
    result = supabase.table("estimates").insert({
        "sqft": request.sqft,
        "category": request.category,
        "material_lines": request.material_lines,
        "labor_lines": request.labor_lines,
        "has_subs": request.has_subs,
        "complexity": request.complexity,
        "ai_estimate": response.estimate,
        "range_low": response.range_low,
        "range_high": response.range_high,
        "confidence": response.confidence,
        "model": response.model,
        "reasoning": response.reasoning,
    }).execute()
    return result.data[0]["id"]
```

### Pattern 3: Supabase Browser Client (Frontend)

**What:** Create browser client for client components
**When to use:** Client-side data fetching in React components
**Example:**
```typescript
// Source: https://supabase.com/docs/guides/auth/server-side/nextjs
import { createBrowserClient } from '@supabase/ssr'

export function createClient() {
  return createBrowserClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
  )
}
```

### Pattern 4: TanStack Table with shadcn

**What:** Define columns and create reusable DataTable component
**When to use:** Any table with sorting, filtering, pagination needs
**Example:**
```typescript
// Source: https://ui.shadcn.com/docs/components/data-table
// columns.tsx
import { ColumnDef } from "@tanstack/react-table"

export type Estimate = {
  id: string
  created_at: string
  sqft: number
  category: string
  ai_estimate: number
  laurent_price: number | null
  reviewed: boolean
}

export const columns: ColumnDef<Estimate>[] = [
  { accessorKey: "created_at", header: "Date" },
  { accessorKey: "category", header: "Category" },
  { accessorKey: "sqft", header: "Sqft" },
  { accessorKey: "ai_estimate", header: "AI Estimate" },
  { accessorKey: "laurent_price", header: "Laurent Price" },
  { accessorKey: "reviewed", header: "Status" },
]
```

### Anti-Patterns to Avoid

- **Creating new Supabase client per request:** Creates httpx client overhead; use singleton pattern
- **Using async client with sync endpoints:** Mixing async/sync causes issues; stay consistent
- **Storing prices as strings:** Use numeric types for calculations
- **Querying without indexes:** Add indexes on `reviewed` and `created_at` columns

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| UUID generation | Custom ID logic | PostgreSQL `gen_random_uuid()` | Built-in, guaranteed unique |
| Timestamp handling | Manual datetime | PostgreSQL `now()` default | Consistent timezone handling |
| Data table pagination | Custom pagination logic | TanStack Table `getPaginationRowModel()` | Battle-tested, handles edge cases |
| Form validation | Manual validation | Zod + react-hook-form | Already in codebase |
| Database connection pooling | Manual pooling | Supabase built-in Supavisor | Handles scaling automatically |

**Key insight:** Supabase provides PostgreSQL with many built-in features (UUIDs, timestamps, RLS) that eliminate custom code. TanStack Table handles complex table state management that would take weeks to build correctly.

## Common Pitfalls

### Pitfall 1: Forgetting to Enable RLS

**What goes wrong:** Without RLS, tables are inaccessible via anon key; with RLS but no policies, all queries return empty
**Why it happens:** Supabase security-first approach blocks by default
**How to avoid:** For internal admin app with service role key, RLS not needed. If using anon key, create explicit policies.
**Warning signs:** Empty arrays returned from queries that should have data

### Pitfall 2: Using getSession() Instead of getUser() on Server

**What goes wrong:** Session can be spoofed; security vulnerability
**Why it happens:** getSession reads from cookies without validation
**How to avoid:** Always use `supabase.auth.getUser()` on server side for auth checks
**Warning signs:** Auth bypasses in testing

### Pitfall 3: Not Handling Insert Return Data

**What goes wrong:** Insert succeeds but you don't get the created record ID
**Why it happens:** Supabase returns data by default, but you need to access it correctly
**How to avoid:** Access `result.data[0]["id"]` after insert
**Warning signs:** Undefined IDs after inserts

### Pitfall 4: Numeric Precision Loss

**What goes wrong:** Currency values lose precision
**Why it happens:** Using `real` instead of `numeric` type
**How to avoid:** Use `numeric(10,2)` for money fields
**Warning signs:** Prices like $1234.5678 instead of $1234.57

### Pitfall 5: TanStack Table Without Proper Type Safety

**What goes wrong:** Runtime errors when column accessors don't match data shape
**Why it happens:** Loose typing in column definitions
**How to avoid:** Define explicit TypeScript types for table data; use `ColumnDef<YourType>`
**Warning signs:** "Cannot read property of undefined" errors in table cells

## Code Examples

Verified patterns from official sources:

### Database Schema (SQL)

```sql
-- Source: https://supabase.com/docs/guides/database/tables
-- Run in Supabase SQL Editor

-- Estimates table: stores all AI predictions
CREATE TABLE estimates (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  created_at timestamptz DEFAULT now() NOT NULL,

  -- Input fields (from EstimateRequest)
  sqft numeric(10,2) NOT NULL,
  category text NOT NULL,
  material_lines integer NOT NULL,
  labor_lines integer NOT NULL,
  has_subs boolean NOT NULL DEFAULT false,
  complexity integer NOT NULL,

  -- AI output fields (from EstimateResponse)
  ai_estimate numeric(10,2) NOT NULL,
  range_low numeric(10,2) NOT NULL,
  range_high numeric(10,2) NOT NULL,
  confidence text NOT NULL CHECK (confidence IN ('HIGH', 'MEDIUM', 'LOW')),
  model text NOT NULL,
  reasoning text,

  -- Review status
  reviewed boolean NOT NULL DEFAULT false
);

-- Feedback table: stores Laurent's review
CREATE TABLE feedback (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  created_at timestamptz DEFAULT now() NOT NULL,
  estimate_id uuid NOT NULL REFERENCES estimates(id) ON DELETE CASCADE,

  -- Laurent's input
  laurent_price numeric(10,2) NOT NULL,

  -- Computed fields
  price_difference numeric(10,2) GENERATED ALWAYS AS (laurent_price - ai_estimate) STORED,

  -- Join estimate for computed column
  ai_estimate numeric(10,2) NOT NULL
);

-- Indexes for query performance
CREATE INDEX idx_estimates_reviewed ON estimates(reviewed);
CREATE INDEX idx_estimates_created_at ON estimates(created_at DESC);
CREATE INDEX idx_feedback_estimate_id ON feedback(estimate_id);
```

### Backend: Supabase Service (Python)

```python
# Source: https://supabase.com/docs/reference/python/initializing
# backend/app/services/supabase_client.py

import os
from supabase import create_client, Client

_client: Client | None = None

def init_supabase() -> None:
    """Initialize Supabase client at startup."""
    global _client
    url = os.environ.get("SUPABASE_URL", "")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
    if url and key:
        _client = create_client(url, key)

def get_supabase() -> Client | None:
    """Get Supabase client (may be None if not configured)."""
    return _client

def close_supabase() -> None:
    """Clean up Supabase client."""
    global _client
    _client = None
```

### Backend: Feedback Router (Python)

```python
# Source: https://supabase.com/docs/reference/python/select
# backend/app/routers/feedback.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from backend.app.services.supabase_client import get_supabase

router = APIRouter(prefix="/feedback", tags=["feedback"])

class EstimateListItem(BaseModel):
    id: str
    created_at: str
    sqft: float
    category: str
    ai_estimate: float
    reviewed: bool

class SubmitFeedbackRequest(BaseModel):
    estimate_id: str
    laurent_price: float

@router.get("/pending", response_model=List[EstimateListItem])
def get_pending_estimates():
    """Get estimates pending review."""
    supabase = get_supabase()
    if not supabase:
        raise HTTPException(503, "Database not configured")

    result = supabase.table("estimates") \
        .select("id, created_at, sqft, category, ai_estimate, reviewed") \
        .eq("reviewed", False) \
        .order("created_at", desc=True) \
        .execute()

    return result.data

@router.post("/submit")
def submit_feedback(request: SubmitFeedbackRequest):
    """Submit Laurent's price and mark estimate as reviewed."""
    supabase = get_supabase()
    if not supabase:
        raise HTTPException(503, "Database not configured")

    # Get the estimate to include ai_estimate in feedback
    estimate = supabase.table("estimates") \
        .select("ai_estimate") \
        .eq("id", request.estimate_id) \
        .single() \
        .execute()

    if not estimate.data:
        raise HTTPException(404, "Estimate not found")

    # Insert feedback
    supabase.table("feedback").insert({
        "estimate_id": request.estimate_id,
        "laurent_price": request.laurent_price,
        "ai_estimate": estimate.data["ai_estimate"],
    }).execute()

    # Mark estimate as reviewed
    supabase.table("estimates") \
        .update({"reviewed": True}) \
        .eq("id", request.estimate_id) \
        .execute()

    return {"status": "success"}
```

### Frontend: Supabase Client Setup

```typescript
// Source: https://supabase.com/docs/guides/auth/server-side/nextjs
// frontend/src/lib/supabase/client.ts

import { createBrowserClient } from '@supabase/ssr'

export function createClient() {
  return createBrowserClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
  )
}
```

### Frontend: Review Data Table

```typescript
// Source: https://ui.shadcn.com/docs/components/data-table
// frontend/src/components/review/columns.tsx

"use client"

import { ColumnDef } from "@tanstack/react-table"
import { Button } from "@/components/ui/button"

export type PendingEstimate = {
  id: string
  created_at: string
  sqft: number
  category: string
  ai_estimate: number
  reviewed: boolean
}

export const columns: ColumnDef<PendingEstimate>[] = [
  {
    accessorKey: "created_at",
    header: "Date",
    cell: ({ row }) => {
      return new Date(row.getValue("created_at")).toLocaleDateString()
    },
  },
  {
    accessorKey: "category",
    header: "Category",
  },
  {
    accessorKey: "sqft",
    header: "Sqft",
    cell: ({ row }) => {
      return row.getValue<number>("sqft").toLocaleString()
    },
  },
  {
    accessorKey: "ai_estimate",
    header: "AI Estimate",
    cell: ({ row }) => {
      const amount = row.getValue<number>("ai_estimate")
      return new Intl.NumberFormat("en-CA", {
        style: "currency",
        currency: "CAD",
      }).format(amount)
    },
  },
  {
    id: "actions",
    cell: ({ row }) => {
      return (
        <Button variant="outline" size="sm">
          Review
        </Button>
      )
    },
  },
]
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| @supabase/auth-helpers | @supabase/ssr | 2024 | Simplified server-side auth |
| createServerComponentClient | createServerClient | 2024 | Unified API |
| NEXT_PUBLIC_SUPABASE_ANON_KEY | NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY | 2025 | Naming clarification (both work) |
| supabase-py async experimental | supabase-py async stable (v2.2+) | 2024 | Async now production ready |

**Deprecated/outdated:**
- `@supabase/auth-helpers-nextjs`: Replaced by `@supabase/ssr`
- `createClientComponentClient`, `createServerComponentClient`: Replaced by unified `createBrowserClient`/`createServerClient`

## Open Questions

Things that couldn't be fully resolved:

1. **Analytics query complexity**
   - What we know: Supabase supports PostgreSQL aggregations
   - What's unclear: Exact analytics queries for feedback analysis
   - Recommendation: Design schema to support common aggregations; defer complex analytics to Phase 6+

2. **Optimistic updates for review queue**
   - What we know: TanStack Query supports optimistic updates
   - What's unclear: Whether to use React Query or keep simple fetch
   - Recommendation: Start with simple fetch; add React Query if UX needs improvement

## Sources

### Primary (HIGH confidence)
- [Supabase Python Docs - Installing](https://supabase.com/docs/reference/python/installing) - Installation, client setup
- [Supabase Python Docs - Insert](https://supabase.com/docs/reference/python/insert) - Insert operations
- [Supabase Python Docs - Select](https://supabase.com/docs/reference/python/select) - Query operations
- [Supabase Python Docs - Update](https://supabase.com/docs/reference/python/update) - Update operations
- [supabase-py GitHub](https://github.com/supabase/supabase-py) - Version 2.27.2, Jan 2026
- [shadcn/ui Data Table](https://ui.shadcn.com/docs/components/data-table) - TanStack Table integration
- [Supabase SSR Setup for Next.js](https://supabase.com/docs/guides/auth/server-side/nextjs) - Server/client patterns

### Secondary (MEDIUM confidence)
- [Supabase Tables and Data](https://supabase.com/docs/guides/database/tables) - Schema design
- [Supabase UUID Guide](https://supabase.com/blog/choosing-a-postgres-primary-key) - Primary key strategies
- [Supabase RLS](https://supabase.com/docs/guides/database/postgres/row-level-security) - Security policies
- [FastAPI + Supabase Discussion](https://github.com/orgs/supabase/discussions/33811) - Client management patterns

### Tertiary (LOW confidence)
- Various Medium articles on FastAPI + Supabase integration patterns

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - Official Supabase documentation and GitHub releases
- Architecture: HIGH - Based on existing codebase patterns and official docs
- Pitfalls: MEDIUM - Mix of official docs and community discussions
- Code examples: HIGH - Adapted from official documentation

**Research date:** 2026-01-18
**Valid until:** 2026-02-18 (30 days - stable libraries)
