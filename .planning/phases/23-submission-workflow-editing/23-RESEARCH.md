# Phase 23: Submission Workflow & Editing - Research

**Researched:** 2026-02-09
**Domain:** Quote submission workflow, approval systems, editable forms, upsell recommendations
**Confidence:** HIGH

## Summary

Phase 23 transforms static AI-generated quotes into editable submissions with multi-stage approval workflow, audit logging, and intelligent upsell suggestions. This requires both frontend (React Hook Form dynamic arrays with drag-and-drop) and backend (PostgreSQL workflow state tracking, notes storage, approval audit trail).

The system adds role-based permissions (admin vs estimator), workflow state machine (draft → pending → approved), timestamped notes with attribution, and parent-child submission relationships for upsells.

**Primary recommendation:** Use React Hook Form's `useFieldArray` with `@dnd-kit/sortable` for editable line items, PostgreSQL JSONB for notes/audit trail, iron-session role metadata for RBAC, and dedicated `submissions` table with `status` enum and parent_id for upsells.

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| react-hook-form | 7.71.1 (installed) | Dynamic form arrays | Official React Hook Form solution, already in use for Phase 22 forms |
| @dnd-kit/core | Latest (to install) | Drag-and-drop primitives | Modern, accessible, performant — recommended by shadcn/ui and Material UI community |
| @dnd-kit/sortable | Latest (to install) | Sortable list preset | Pairs with core, provides SortableContext and useSortable hook |
| @dnd-kit/utilities | Latest (to install) | Helper functions | Required by sortable for array manipulation |
| PostgreSQL JSONB | Built-in (Supabase) | Notes and audit log storage | Native JSON storage with indexing, fast queries, flexible schema |
| iron-session | 8.x (installed) | Role-based session metadata | Already in use for auth (Phase 7), extends SessionData interface |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| Zod | Latest (installed) | Schema validation | Already in use — extend for submissions with nested line items |
| TanStack Query | Latest (installed) | State management | Already in use — add mutations for edit/approve/finalize |
| shadcn/ui components | Latest (installed) | UI components | Already in use — leverage Dialog, Separator, Textarea for notes UI |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| @dnd-kit | react-beautiful-dnd | dnd-kit is more modern (2020+), actively maintained, better accessibility, smaller bundle |
| @dnd-kit | react-dnd | dnd-kit simpler API, better mobile support, better integration with React 18+ |
| PostgreSQL JSONB | Separate audit tables | JSONB faster for small audit logs (<1000 entries/submission), simpler queries, less joins |
| iron-session roles | NextAuth.js roles | iron-session already integrated, NextAuth overkill for 2-role system (admin/estimator) |

**Installation:**
```bash
# Frontend
cd frontend
pnpm add @dnd-kit/core @dnd-kit/sortable @dnd-kit/utilities

# Backend - no new dependencies needed (PostgreSQL/Supabase already available)
```

## Architecture Patterns

### Recommended Database Schema

**submissions table** (new):
```sql
CREATE TABLE submissions (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  created_at timestamptz DEFAULT now() NOT NULL,
  updated_at timestamptz DEFAULT now() NOT NULL,

  -- Source data (references estimate from Phase 13 hybrid quote)
  estimate_id uuid REFERENCES estimates(id),

  -- Workflow status
  status text NOT NULL DEFAULT 'draft',  -- enum: draft, pending_approval, approved, rejected
  finalized_at timestamptz,
  approved_at timestamptz,
  approved_by text,  -- user identifier from session

  -- Job metadata (denormalized for performance)
  client_name text,
  category text NOT NULL,
  sqft numeric(10,2),

  -- Editable line items (JSONB for flexibility)
  line_items jsonb NOT NULL,  -- [{id, type: 'material'|'labor', name, quantity, unit_price, total, order}]

  -- Notes and audit trail
  notes jsonb DEFAULT '[]'::jsonb,  -- [{id, text, created_by, created_at}]
  audit_log jsonb DEFAULT '[]'::jsonb,  -- [{action, user, timestamp, changes}]

  -- Upsell relationships
  parent_submission_id uuid REFERENCES submissions(id),  -- null for main submissions
  upsell_type text,  -- null for main, or: heating_cables, gutters, inspection, etc.

  -- Pricing tiers (from Phase 13)
  pricing_tiers jsonb NOT NULL,  -- [{tier, total_price, materials_cost, labor_cost, description}]
  selected_tier text DEFAULT 'Standard',  -- Basic, Standard, or Premium

  -- Computed totals (updated on line item changes)
  total_materials_cost numeric(10,2) NOT NULL,
  total_labor_cost numeric(10,2) NOT NULL,
  total_price numeric(10,2) NOT NULL,

  CONSTRAINT valid_status CHECK (status IN ('draft', 'pending_approval', 'approved', 'rejected')),
  CONSTRAINT valid_tier CHECK (selected_tier IN ('Basic', 'Standard', 'Premium'))
);

-- Indexes
CREATE INDEX idx_submissions_status ON submissions(status);
CREATE INDEX idx_submissions_created_at ON submissions(created_at DESC);
CREATE INDEX idx_submissions_parent ON submissions(parent_submission_id) WHERE parent_submission_id IS NOT NULL;
CREATE INDEX idx_submissions_estimate ON submissions(estimate_id);
CREATE INDEX idx_submissions_notes ON submissions USING gin(notes);
CREATE INDEX idx_submissions_audit ON submissions USING gin(audit_log);

-- Trigger for updated_at
CREATE TRIGGER update_submissions_updated_at
  BEFORE UPDATE ON submissions
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();  -- assumes function exists or create it
```

**Update estimates table** (existing):
```sql
-- Add submission_created flag to estimates table
ALTER TABLE estimates ADD COLUMN submission_created boolean DEFAULT false;
```

**JSONB structure examples:**

```typescript
// line_items field
type LineItem = {
  id: string;  // UUID for stable identity
  type: 'material' | 'labor';
  material_id?: number;  // references materials table if type=material
  name: string;
  quantity: number;
  unit_price: number;
  total: number;
  order: number;  // for drag-drop sorting
};

// notes field
type Note = {
  id: string;
  text: string;
  created_by: string;  // user identifier from session
  created_at: string;  // ISO timestamp
};

// audit_log field
type AuditEntry = {
  action: 'created' | 'edited' | 'finalized' | 'approved' | 'rejected' | 'note_added';
  user: string;
  timestamp: string;
  changes?: Record<string, { old: any; new: any }>;
};
```

### Pattern 1: Editable Line Items with Drag-and-Drop

**What:** Dynamic form array where users can add, remove, edit, and reorder line items.

**When to use:** Main submission editing UI after AI generates initial quote.

**Example:**
```typescript
// Source: https://react-hook-form.com/docs/usefieldarray + https://docs.dndkit.com/presets/sortable

import { useForm, useFieldArray } from 'react-hook-form';
import { DndContext, closestCenter, DragEndEvent } from '@dnd-kit/core';
import { SortableContext, verticalListSortingStrategy, useSortable, arrayMove } from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';

type LineItemFormData = {
  id: string;
  type: 'material' | 'labor';
  name: string;
  quantity: number;
  unit_price: number;
  total: number;
};

function EditableLineItems() {
  const { control, watch } = useForm<{ lineItems: LineItemFormData[] }>();
  const { fields, append, remove, move } = useFieldArray({
    control,
    name: 'lineItems',
  });

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event;
    if (active.id !== over?.id) {
      const oldIndex = fields.findIndex((f) => f.id === active.id);
      const newIndex = fields.findIndex((f) => f.id === over?.id);
      move(oldIndex, newIndex);
    }
  };

  return (
    <DndContext collisionDetection={closestCenter} onDragEnd={handleDragEnd}>
      <SortableContext items={fields.map(f => f.id)} strategy={verticalListSortingStrategy}>
        {fields.map((field, index) => (
          <SortableLineItem
            key={field.id}
            id={field.id}
            index={index}
            control={control}
            onRemove={() => remove(index)}
          />
        ))}
      </SortableContext>
      <Button onClick={() => append({ type: 'material', name: '', quantity: 1, unit_price: 0, total: 0 })}>
        Add Line Item
      </Button>
    </DndContext>
  );
}

function SortableLineItem({ id, index, control, onRemove }: { id: string; index: number; control: any; onRemove: () => void }) {
  const { attributes, listeners, setNodeRef, transform, transition } = useSortable({ id });
  const style = { transform: CSS.Transform.toString(transform), transition };

  return (
    <div ref={setNodeRef} style={style}>
      <div className="flex gap-2 items-center">
        <button {...attributes} {...listeners} className="cursor-grab">⋮⋮</button>
        <Controller control={control} name={`lineItems.${index}.name`} render={({ field }) => <Input {...field} />} />
        <Controller control={control} name={`lineItems.${index}.quantity`} render={({ field }) => <Input type="number" {...field} />} />
        <Controller control={control} name={`lineItems.${index}.unit_price`} render={({ field }) => <Input type="number" {...field} />} />
        <Button onClick={onRemove} variant="destructive" size="sm">Remove</Button>
      </div>
    </div>
  );
}
```

### Pattern 2: Workflow State Machine

**What:** PostgreSQL status enum with transition validation and audit logging.

**When to use:** Backend endpoint for status changes (draft → pending → approved).

**Example:**
```python
# Source: https://oneuptime.com/blog/post/2026-01-21-postgresql-audit-logging/view

from enum import Enum
from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class SubmissionStatus(str, Enum):
    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"

VALID_TRANSITIONS = {
    SubmissionStatus.DRAFT: [SubmissionStatus.PENDING_APPROVAL],
    SubmissionStatus.PENDING_APPROVAL: [SubmissionStatus.APPROVED, SubmissionStatus.REJECTED, SubmissionStatus.DRAFT],
    SubmissionStatus.APPROVED: [],  # Terminal state
    SubmissionStatus.REJECTED: [SubmissionStatus.DRAFT],
}

def transition_status(
    submission_id: str,
    current_status: SubmissionStatus,
    new_status: SubmissionStatus,
    user: str,
    reason: Optional[str] = None,
) -> dict:
    """Validate and execute status transition with audit logging."""

    # Validate transition
    if new_status not in VALID_TRANSITIONS[current_status]:
        raise ValueError(f"Invalid transition: {current_status} -> {new_status}")

    # Create audit entry
    audit_entry = {
        "action": f"status_changed_{new_status.value}",
        "user": user,
        "timestamp": datetime.utcnow().isoformat(),
        "changes": {
            "status": {"old": current_status.value, "new": new_status.value}
        },
        "reason": reason,
    }

    # Update database with JSONB append
    query = """
        UPDATE submissions
        SET
            status = $1,
            audit_log = audit_log || $2::jsonb,
            updated_at = NOW(),
            approved_at = CASE WHEN $1 = 'approved' THEN NOW() ELSE approved_at END,
            approved_by = CASE WHEN $1 = 'approved' THEN $3 ELSE approved_by END
        WHERE id = $4 AND status = $5
        RETURNING *
    """

    return supabase.rpc("execute_raw_sql", {
        "query": query,
        "params": [new_status.value, audit_entry, user, submission_id, current_status.value]
    })
```

### Pattern 3: Role-Based Access Control (RBAC) with iron-session

**What:** Extend SessionData interface to include user role, use dependency injection to check permissions.

**When to use:** Approval endpoints restricted to admin role (Laurent only).

**Example:**
```typescript
// frontend/src/lib/auth.ts
export interface SessionData {
  isAuthenticated: boolean;
  username?: string;  // NEW: user identifier
  role?: 'admin' | 'estimator';  // NEW: role for RBAC
}

// backend/app/dependencies.py (NEW FILE)
from enum import Enum
from fastapi import Header, HTTPException

class UserRole(str, Enum):
    ADMIN = "admin"
    ESTIMATOR = "estimator"

async def get_current_user_role(x_user_role: str = Header(None)) -> UserRole:
    """Extract user role from session header (set by Next.js middleware)."""
    if not x_user_role:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        return UserRole(x_user_role)
    except ValueError:
        raise HTTPException(status_code=403, detail="Invalid role")

async def require_admin(role: UserRole = Depends(get_current_user_role)) -> None:
    """Dependency that ensures user has admin role."""
    if role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")

# Usage in endpoint
@router.post("/submissions/{id}/approve")
async def approve_submission(id: str, _: None = Depends(require_admin)):
    # Only admins reach here
    pass
```

### Pattern 4: Timestamped Notes with JSONB Append

**What:** Notes stored as JSONB array, new notes appended atomically with PostgreSQL `||` operator.

**When to use:** Adding notes to submission without loading/parsing entire array.

**Example:**
```python
# Source: https://elephas.io/audit-logging-using-jsonb-in-postgres/

from datetime import datetime
import uuid

def add_note(submission_id: str, text: str, user: str):
    """Add timestamped note to submission."""

    note = {
        "id": str(uuid.uuid4()),
        "text": text,
        "created_by": user,
        "created_at": datetime.utcnow().isoformat(),
    }

    # Atomic JSONB append (no race conditions)
    supabase.table("submissions").update({
        "notes": supabase.rpc("jsonb_append", {"field": "notes", "value": note})
    }).eq("id", submission_id).execute()

    # Alternative: PostgreSQL raw SQL with || operator
    # UPDATE submissions SET notes = notes || '[{"id": "...", ...}]'::jsonb WHERE id = ?
```

### Pattern 5: Upsell Recommendation Engine

**What:** Rule-based upsell suggestions triggered after main submission finalized, creates child submissions linked to parent.

**When to use:** After user clicks "Finalize" on main submission, show dialog with suggested upsells.

**Example:**
```typescript
// Upsell rules (could be JSON config or database table)
const UPSELL_RULES: Record<string, string[]> = {
  'Bardeaux': ['heating_cables', 'gutters', 'ventilation', 'inspection_plan'],
  'Élastomère': ['drain_system', 'insulation', 'maintenance_contract', 'inspection_plan'],
  'Metal': ['gutters', 'snow_guards', 'warranty_extension', 'inspection_plan'],
  'Service Call': ['inspection_plan', 'maintenance_contract'],
};

function getUpsellSuggestions(category: string): Array<{ type: string; name: string; description: string }> {
  const types = UPSELL_RULES[category] || ['inspection_plan', 'maintenance_contract'];

  const upsellMeta: Record<string, { name: string; description: string }> = {
    heating_cables: { name: 'Heating Cables', description: 'Prevent ice dams in winter' },
    gutters: { name: 'Gutter System', description: 'Complete gutter installation' },
    ventilation: { name: 'Ventilation Upgrade', description: 'Improve attic airflow' },
    inspection_plan: { name: 'Annual Inspection', description: 'Yearly roof inspection service' },
    maintenance_contract: { name: 'Maintenance Contract', description: '2-year maintenance plan' },
    // ... more upsell types
  };

  return types.map(type => ({ type, ...upsellMeta[type] }));
}

// Backend: Create child submission
async function createUpsellSubmission(parentId: string, upsellType: string, user: string) {
  const parent = await getSubmission(parentId);

  // Generate new submission with pre-filled line items based on upsell type
  const lineItems = await generateUpsellLineItems(upsellType, parent.category, parent.sqft);

  const upsellSubmission = {
    parent_submission_id: parentId,
    upsell_type: upsellType,
    client_name: parent.client_name,
    category: parent.category,  // Inherit category
    status: 'draft',
    line_items: lineItems,
    pricing_tiers: calculateUpsellPricing(lineItems),  // Simpler pricing for upsells
    created_by: user,
  };

  return await supabase.table("submissions").insert(upsellSubmission).single();
}
```

### Anti-Patterns to Avoid

- **Loading entire line_items array to add one item:** Use React Hook Form's `append()` method, not array spread.
- **Updating notes without atomic append:** Always use PostgreSQL JSONB `||` operator or `jsonb_set()` to avoid race conditions.
- **Hard-coding role checks in components:** Use dependency injection (FastAPI `Depends`) or middleware for RBAC.
- **Storing computed totals without recalculating:** Trigger recalculation on every line item change (watch fields, recompute total).
- **Creating upsells before finalize:** Only suggest upsells AFTER main submission finalized (UX pattern).

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Drag-and-drop reordering | Custom mouse event handlers | @dnd-kit/sortable | Handles accessibility, touch, keyboard nav, collision detection, edge cases |
| Audit trail storage | Custom CSV/log files | PostgreSQL JSONB with triggers | ACID guarantees, queryable, indexable, no file I/O overhead |
| Role-based permissions | if/else checks scattered in code | FastAPI Depends + middleware | Centralized, testable, prevents security bugs from missed checks |
| Workflow state validation | Manual status checks | State machine with VALID_TRANSITIONS dict | Prevents invalid transitions, documents allowed flows |
| Dynamic form arrays | Manual array mutation | React Hook Form useFieldArray | Handles validation, dirty tracking, reset, registration automatically |

**Key insight:** Workflow systems have deceptive complexity — transitions, permissions, audit requirements, rollback scenarios. Use battle-tested patterns (state machines, JSONB audit logs, declarative RBAC) rather than ad-hoc if/else logic that becomes unmaintainable.

## Common Pitfalls

### Pitfall 1: useFieldArray key prop mistakes

**What goes wrong:** Using array index as key instead of `field.id` causes form state to break on reorder/remove.

**Why it happens:** React's reconciliation algorithm loses track of which component is which when keys change.

**How to avoid:**
```typescript
// WRONG
{fields.map((field, index) => <LineItem key={index} {...field} />)}

// CORRECT
{fields.map((field, index) => <LineItem key={field.id} {...field} />)}
// field.id is stable, auto-generated by useFieldArray
```

**Warning signs:** Form inputs show wrong values after drag-drop, removing wrong item when clicking delete.

### Pitfall 2: Race conditions in JSONB updates

**What goes wrong:** Two users add notes simultaneously, one note gets lost because of read-modify-write race.

**Why it happens:** Application reads JSONB array, appends in memory, writes back — loses concurrent writes.

**How to avoid:**
```sql
-- WRONG (read-modify-write in application)
const notes = await getSubmission(id).notes;
notes.push(newNote);
await updateSubmission(id, { notes });

-- CORRECT (atomic append in PostgreSQL)
UPDATE submissions
SET notes = notes || $1::jsonb
WHERE id = $2;
```

**Warning signs:** Missing notes, audit log entries disappear, users report "my note vanished".

### Pitfall 3: Forgetting to recalculate totals

**What goes wrong:** User edits quantity/price, but total doesn't update. Submitted data has mismatched totals.

**Why it happens:** Computed field (`total = quantity * unit_price`) not recalculated on input change.

**How to avoid:**
```typescript
// Watch quantity and unit_price fields, compute total on every change
const quantity = watch(`lineItems.${index}.quantity`);
const unitPrice = watch(`lineItems.${index}.unit_price`);

useEffect(() => {
  const total = quantity * unitPrice;
  setValue(`lineItems.${index}.total`, total);
}, [quantity, unitPrice, index, setValue]);

// Or: use Zod schema with .transform() to auto-calculate
const lineItemSchema = z.object({
  quantity: z.number().positive(),
  unit_price: z.number().nonnegative(),
}).transform((data) => ({
  ...data,
  total: data.quantity * data.unit_price,
}));
```

**Warning signs:** Total field shows stale value, backend validation rejects submission, invoice totals wrong.

### Pitfall 4: Invalid workflow transitions

**What goes wrong:** Estimator approves their own submission (should require admin), or approved submission transitions back to draft.

**Why it happens:** No explicit state machine, scattered `if (status === 'X')` checks, roles not validated.

**How to avoid:**
- Define `VALID_TRANSITIONS` dict mapping current status to allowed next states
- Use FastAPI `Depends(require_admin)` for approval endpoints
- Validate transitions in backend before UPDATE, return 403 if invalid

**Warning signs:** Submissions in impossible states, audit log shows unauthorized actions, security audit failures.

### Pitfall 5: Parent-child submission orphans

**What goes wrong:** Main submission deleted but child upsells remain, or upsell references non-existent parent.

**Why it happens:** No foreign key constraint with ON DELETE behavior, or constraint missing CASCADE/RESTRICT.

**How to avoid:**
```sql
-- Add CASCADE to delete upsells when parent deleted
ALTER TABLE submissions
  ADD CONSTRAINT fk_parent_submission
  FOREIGN KEY (parent_submission_id)
  REFERENCES submissions(id)
  ON DELETE CASCADE;

-- Or RESTRICT to prevent deletion if upsells exist
-- ON DELETE RESTRICT  -- throws error if children exist
```

**Warning signs:** Database queries return null parent, upsell list shows broken references, "submission not found" errors.

## Code Examples

Verified patterns from official sources:

### React Hook Form useFieldArray with validation
```typescript
// Source: https://react-hook-form.com/docs/usefieldarray

import { useForm, useFieldArray } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';

const lineItemSchema = z.object({
  type: z.enum(['material', 'labor']),
  name: z.string().min(1, 'Name required'),
  quantity: z.number().positive('Must be positive'),
  unit_price: z.number().nonnegative('Must be non-negative'),
  total: z.number().nonnegative(),
});

const formSchema = z.object({
  lineItems: z.array(lineItemSchema).min(1, 'At least one line item required'),
});

function EditSubmissionForm() {
  const form = useForm({
    resolver: zodResolver(formSchema),
    defaultValues: { lineItems: [] },
  });

  const { fields, append, remove } = useFieldArray({
    control: form.control,
    name: 'lineItems',
  });

  return (
    <form onSubmit={form.handleSubmit(onSubmit)}>
      {fields.map((field, index) => (
        <div key={field.id}>
          <Input {...form.register(`lineItems.${index}.name`)} />
          <Input type="number" {...form.register(`lineItems.${index}.quantity`, { valueAsNumber: true })} />
          <Button onClick={() => remove(index)}>Remove</Button>
        </div>
      ))}
      <Button onClick={() => append({ type: 'material', name: '', quantity: 1, unit_price: 0, total: 0 })}>
        Add Item
      </Button>
    </form>
  );
}
```

### PostgreSQL JSONB audit logging trigger
```sql
-- Source: https://wiki.postgresql.org/wiki/Audit_trigger

CREATE OR REPLACE FUNCTION audit_submission_changes()
RETURNS TRIGGER AS $$
BEGIN
  -- Append audit entry to audit_log JSONB array
  NEW.audit_log = COALESCE(NEW.audit_log, '[]'::jsonb) || jsonb_build_array(
    jsonb_build_object(
      'action', TG_OP,
      'user', current_user,
      'timestamp', now(),
      'old_data', CASE WHEN TG_OP = 'UPDATE' THEN to_jsonb(OLD) ELSE NULL END,
      'new_data', to_jsonb(NEW)
    )
  );

  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER submissions_audit_trigger
  BEFORE UPDATE ON submissions
  FOR EACH ROW
  EXECUTE FUNCTION audit_submission_changes();
```

### dnd-kit sortable with React Hook Form
```typescript
// Source: https://docs.dndkit.com/presets/sortable

import { DndContext, closestCenter } from '@dnd-kit/core';
import { SortableContext, verticalListSortingStrategy, useSortable } from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';

function SortableLineItems() {
  const { fields, move } = useFieldArray({ control, name: 'lineItems' });

  const handleDragEnd = (event) => {
    const { active, over } = event;
    if (active.id !== over.id) {
      const oldIndex = fields.findIndex((f) => f.id === active.id);
      const newIndex = fields.findIndex((f) => f.id === over.id);
      move(oldIndex, newIndex);  // useFieldArray's move method
    }
  };

  return (
    <DndContext collisionDetection={closestCenter} onDragEnd={handleDragEnd}>
      <SortableContext items={fields.map(f => f.id)} strategy={verticalListSortingStrategy}>
        {fields.map((field, index) => (
          <SortableRow key={field.id} id={field.id} index={index} />
        ))}
      </SortableContext>
    </DndContext>
  );
}

function SortableRow({ id, index }) {
  const { attributes, listeners, setNodeRef, transform, transition } = useSortable({ id });

  return (
    <div ref={setNodeRef} style={{ transform: CSS.Transform.toString(transform), transition }}>
      <button {...attributes} {...listeners}>⋮⋮ Drag</button>
      {/* Form fields here */}
    </div>
  );
}
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| react-beautiful-dnd | @dnd-kit | 2020-2021 | Better accessibility, smaller bundle, React 18+ support |
| CSV audit logs | PostgreSQL JSONB | 2020+ | Queryable, atomic, indexable, no file I/O |
| Separate audit tables | JSONB in same table | 2022+ | Faster queries (no joins), simpler schema for <1k audit entries |
| Separate notes tables | JSONB array in submission | 2023+ | Same rationale — simplicity for small datasets |
| Manual role checks | Dependency injection | FastAPI 0.65+ (2021) | Centralized, testable, secure by default |

**Deprecated/outdated:**
- **react-beautiful-dnd**: Maintenance mode since 2021, use @dnd-kit instead
- **NextAuth.js for simple auth**: Overkill for 2-role system, iron-session lighter weight
- **Separate audit tables for small datasets**: JSONB simpler when <10k audit entries per record

## Open Questions

1. **Role assignment workflow**
   - What we know: System needs admin (Laurent) vs estimator roles
   - What's unclear: How are roles assigned? Manual env var mapping (username → role)? Future user management UI?
   - Recommendation: Start with manual role mapping in backend config file (e.g., `ADMIN_USERS=laurent@toiturelv.ca`), add UI later if needed

2. **Submission locking after finalize**
   - What we know: "Finalize" button locks submission
   - What's unclear: Can admin unlock for corrections? Or create new version/revision?
   - Recommendation: Start with strict locking (no edits after finalize), add "Create Revision" button if Laurent needs corrections

3. **Upsell generation timing**
   - What we know: After finalize, suggest upsells
   - What's unclear: Auto-generate drafts or show preview dialog first?
   - Recommendation: Show preview dialog with checkboxes — user selects which upsells to create, avoids cluttering submission list

4. **Material database integration**
   - What we know: Phase 20 materials table exists, should be used for adding items
   - What's unclear: How to handle custom materials (not in database)?
   - Recommendation: Allow custom materials with `material_id: null` and free-form name entry, track in analytics which custom materials are commonly used

## Sources

### Primary (HIGH confidence)
- React Hook Form useFieldArray: https://react-hook-form.com/docs/usefieldarray (official docs)
- @dnd-kit sortable: https://docs.dndkit.com/presets/sortable (official docs)
- PostgreSQL JSONB audit patterns: https://wiki.postgresql.org/wiki/Audit_trigger (PostgreSQL wiki)
- PostgreSQL audit logging 2026: https://oneuptime.com/blog/post/2026-01-21-postgresql-audit-logging/view
- iron-session with Next.js: https://github.com/vvo/iron-session (official GitHub)

### Secondary (MEDIUM confidence)
- [Row Ordering/DnD Guide - Material React Table](https://www.material-react-table.com/docs/guides/row-ordering-dnd)
- [Top 5 Drag-and-Drop Libraries for React in 2026](https://puckeditor.com/blog/top-5-drag-and-drop-libraries-for-react)
- [Approval workflow patterns - Kissflow](https://kissflow.com/workflow/approval-process/)
- [FastAPI RBAC Implementation - Permit.io](https://www.permit.io/blog/fastapi-rbac-full-implementation-tutorial)
- [Audit Logging using JSONB in Postgres - Elephas](https://elephas.io/audit-logging-using-jsonb-in-postgres/)

### Tertiary (LOW confidence - WebSearch only)
- Upsell recommendation patterns: https://docs.upsellwp.com/setup-and-customisation/recommendation-engine (Shopify-focused, patterns apply)

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - All libraries in active use, official docs verified
- Architecture patterns: HIGH - PostgreSQL JSONB and RBAC patterns well-documented and current
- Workflow state machine: HIGH - Standard database pattern, verified in multiple sources
- Upsell recommendations: MEDIUM - Rule-based approach verified, but AI-powered alternatives exist (not needed for Phase 23)

**Research date:** 2026-02-09
**Valid until:** 30 days (stable technologies — React Hook Form, PostgreSQL, FastAPI)

**Next phase dependencies:**
- Phase 24 (Export, Send & Red Flags) will need submission status = 'approved' to enable sending
- Phase 25 (UI Polish) may need dark mode styling for submission editor
