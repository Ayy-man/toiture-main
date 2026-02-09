# Phase 24: Export, Send & Red Flags - Research

**Researched:** 2026-02-10
**Domain:** DOCX export, email scheduling, automated warning system, multi-format document generation
**Confidence:** HIGH

## Summary

Phase 24 adds multi-format export (PDF + DOCX), flexible send options (immediate/scheduled/draft), and automated red flag warnings to catch risky submissions before sending. This extends the existing PDF export (Phase 14-03) with DOCX generation, integrates email delivery, and adds a rule-based warning system that surfaces risk patterns from job data.

The system requires DOCX generation library (docx npm package), email service integration (Resend/Sendgrid + QStash for scheduling on Vercel), backend red flag evaluation service, and frontend warning UI with dismissible alerts.

**Primary recommendation:** Use `docx` npm package for DOCX generation (pairs with existing @react-pdf/renderer), Resend for email delivery with Vercel Cron for scheduling, PostgreSQL JSONB for send tracking/drafts, and rule-based red flag evaluator service that checks 5 risk categories from submission data.

## Answer: What Do I Need to Know to PLAN This Phase Well?

### 1. EXISTING EXPORT INFRASTRUCTURE (Phase 14-03)

**Current PDF Export:**
- **Library:** `@react-pdf/renderer` v4.3.2 (already installed)
- **Location:** `/frontend/src/lib/pdf/quote-template.tsx`
- **Pattern:** Client-side generation, browser download
- **Template:** `QuotePDFDocument` component with LV branding
- **Format:** Standard tier pricing, work items (no hours), materials/labor summary
- **Language:** French (Quebec) with fr-CA locale formatting
- **Invoked from:** `QuoteActions` component (`quote-actions.tsx`)

**Key Decision:** Existing PDF excludes labor hours (client-facing). DOCX should match this for consistency.

**Template Structure (Current PDF):**
```
Header:
  - SOUMISSION title
  - Toiture LV subtitle
Job Info:
  - Date (YYYY-MM-DD)
  - Categorie
  - Superficie (pi²)
Work Items:
  - Bullet list (no hours shown)
Summary:
  - Materiaux: $X,XXX
  - Main-d'oeuvre: $X,XXX
  - TOTAL: $X,XXX
Footer:
  - "Cette soumission est valide pour 30 jours..."
```

**DOCX Must Match:** Same structure, same fields, bilingual support, LV logo placement.

### 2. DOCX GENERATION OPTIONS

**Research from Web Search:**

**Option 1: docx (RECOMMENDED)**
- **URL:** [GitHub - dolanmiu/docx](https://github.com/dolanmiu/docx)
- **NPM:** `docx` v9.5.1 (8 months old, 379 projects use it)
- **Pattern:** Declarative API similar to @react-pdf/renderer
- **Strengths:** TypeScript support, modern API, good documentation, works client-side + server-side
- **Example:**
```typescript
import { Document, Paragraph, TextRun, Table, TableRow, TableCell } from "docx";

const doc = new Document({
  sections: [{
    properties: {},
    children: [
      new Paragraph({
        text: "SOUMISSION",
        heading: HeadingLevel.HEADING_1,
        alignment: AlignmentType.CENTER,
      }),
      new Table({
        rows: [
          new TableRow({
            children: [
              new TableCell({ children: [new Paragraph("Materiaux")] }),
              new TableCell({ children: [new Paragraph("$7,500")] }),
            ],
          }),
        ],
      }),
    ],
  }],
});

const blob = await Packer.toBlob(doc);
```

**Option 2: Docxtemplater**
- **URL:** [docxtemplater.com](https://docxtemplater.com/)
- **Pattern:** Template-based (upload .docx template, fill placeholders)
- **Strengths:** Good for pre-designed templates, supports loops/conditions
- **Weakness:** Requires maintaining binary .docx template file, harder to version control
- **Cost:** Free for core, paid modules for images/tables

**Option 3: docx-templates**
- **NPM:** `docx-templates`
- **Pattern:** Similar to Docxtemplater (template-based)
- **Weakness:** Less active maintenance than docx

**DECISION:** Use `docx` package. Reasons:
1. Matches existing `@react-pdf/renderer` declarative pattern
2. No template files to maintain (code-based generation)
3. TypeScript support
4. Client-side compatible (same pattern as PDF)
5. Free and open-source

**Installation:**
```bash
cd frontend
pnpm add docx
```

**Implementation Pattern:**
```typescript
// /frontend/src/lib/docx/quote-template.ts
import { Document, Packer, Paragraph, Table, HeadingLevel } from "docx";
import type { HybridQuoteResponse } from "@/types/hybrid-quote";

export async function generateQuoteDOCX(
  quote: HybridQuoteResponse,
  category: string,
  sqft: number,
  date: string
): Promise<Blob> {
  const doc = new Document({
    sections: [/* ... */],
  });

  return await Packer.toBlob(doc);
}
```

### 3. EMAIL DELIVERY & SCHEDULING

**Research from Web Search:**

**Email Services Compatible with Vercel:**

**Option 1: Resend (RECOMMENDED)**
- **URL:** [resend.com](https://resend.com/)
- **Pricing:** 3,000 emails/month free, then $20/mo for 50k
- **API:** REST API, official Node.js SDK
- **Strengths:** Built for developers, simple API, good Vercel integration
- **Example:**
```typescript
import { Resend } from 'resend';

const resend = new Resend(process.env.RESEND_API_KEY);

await resend.emails.send({
  from: 'soumissions@toiturelv.com',
  to: 'client@example.com',
  subject: 'Votre soumission - Toiture LV',
  attachments: [
    { filename: 'soumission.pdf', content: pdfBuffer },
    { filename: 'soumission.docx', content: docxBuffer },
  ],
});
```

**Option 2: SendGrid**
- **URL:** [sendgrid.com](https://sendgrid.com/)
- **Pricing:** 100 emails/day free
- **Strengths:** Enterprise-grade, email analytics
- **Weakness:** More complex API, overkill for basic sending

**Option 3: Nodemailer + SMTP**
- **Pattern:** Traditional SMTP (Gmail, Outlook, etc.)
- **Weakness:** Vercel serverless functions have SMTP limitations (timeouts, connection issues)

**DECISION:** Use Resend. Reasons:
1. Developer-friendly API
2. Good free tier for MVP
3. Official Node.js SDK
4. Works well on Vercel serverless
5. Attachment support (PDF + DOCX)

**Installation:**
```bash
cd backend
pip install resend  # Python SDK for FastAPI
```

**Scheduling Options:**

**Option 1: Vercel Cron Jobs (RECOMMENDED for simple scheduling)**
- **URL:** [Vercel Cron Jobs](https://vercel.com/docs/cron-jobs)
- **Pattern:** Define schedule in `vercel.json`, hit API endpoint
- **Strengths:** Native Vercel integration, simple setup
- **Limitation:** Fixed schedules only (hourly, daily, etc.) — NOT per-submission custom dates
- **Use Case:** For background tasks (e.g., daily digest), NOT for "send this quote on Feb 15 at 10am"

**Option 2: QStash (RECOMMENDED for per-submission scheduling)**
- **URL:** [Upstash QStash](https://upstash.com/docs/qstash)
- **Pattern:** HTTP-based message queue with scheduling
- **Pricing:** 500 messages/day free
- **Strengths:** Schedule specific timestamps, works with Vercel Functions
- **Example:**
```typescript
import { Client } from "@upstash/qstash";

const qstash = new Client({ token: process.env.QSTASH_TOKEN });

await qstash.publishJSON({
  url: "https://yourapp.vercel.app/api/send-quote",
  body: { submissionId: "abc-123" },
  delay: 86400, // seconds (send in 24 hours)
});
```

**Option 3: node-schedule (NOT RECOMMENDED on Vercel)**
- **Limitation:** Vercel Functions are stateless — cron jobs reset between invocations
- **Only works:** On long-running servers (not serverless)

**DECISION:** Use QStash for scheduled sends. Reasons:
1. Works on Vercel serverless
2. Per-submission custom scheduling
3. Reliable HTTP-based delivery
4. Free tier sufficient for MVP

**Installation:**
```bash
cd frontend  # QStash client for Next.js API routes
pnpm add @upstash/qstash
```

**Send Workflow:**
```
User clicks "Send":
1. Frontend: POST /api/submissions/{id}/send with { sendOption, scheduledDate }
2. Backend: Generate PDF + DOCX blobs
3. If sendNow: Call Resend API immediately
4. If scheduled: Queue job via QStash with scheduledDate
5. QStash: Invoke /api/send-quote callback at scheduled time
6. Callback: Generate + send via Resend
7. Update submission.send_status in DB
```

### 4. SEND OPTIONS & DRAFT STATE

**Send Options (from roadmap):**
1. **Send now:** Immediate email delivery
2. **Schedule send:** Date + time picker, queue via QStash
3. **Save as draft:** Store submission without sending

**Database Schema Extension (extends Phase 23 submissions table):**
```sql
ALTER TABLE submissions ADD COLUMN send_status text DEFAULT 'draft';
ALTER TABLE submissions ADD COLUMN scheduled_send_at timestamptz;
ALTER TABLE submissions ADD COLUMN sent_at timestamptz;
ALTER TABLE submissions ADD COLUMN recipient_email text;
ALTER TABLE submissions ADD COLUMN email_subject text;
ALTER TABLE submissions ADD COLUMN email_body text;

CONSTRAINT valid_send_status CHECK (
  send_status IN ('draft', 'scheduled', 'sent', 'failed')
);
```

**Send Status States:**
- `draft`: Not sent (default for new submissions)
- `scheduled`: Queued via QStash, awaiting delivery
- `sent`: Successfully delivered via Resend
- `failed`: Delivery error (Resend/QStash failure)

**Frontend Send Dialog:**
```typescript
// /frontend/src/components/submissions/send-dialog.tsx
<Dialog>
  <RadioGroup value={sendOption}>
    <Radio value="now">Envoyer maintenant</Radio>
    <Radio value="schedule">Planifier l'envoi</Radio>
    <Radio value="draft">Sauvegarder comme brouillon</Radio>
  </RadioGroup>

  {sendOption === 'schedule' && (
    <DateTimePicker
      label="Date et heure d'envoi"
      value={scheduledDate}
      onChange={setScheduledDate}
    />
  )}

  <Input label="Destinataire" type="email" />
  <Textarea label="Message (optionnel)" />

  <Button onClick={handleSend}>Confirmer</Button>
</Dialog>
```

**Date-Time Picker:**
- Use `react-day-picker` (already popular with shadcn community) or `date-fns` (already installed)
- Pattern: Date picker + time input (HH:MM) in Quebec timezone (America/Montreal)

### 5. RED FLAG SYSTEM

**Goal:** Auto-flag submissions matching 5 warning patterns before sending.

**Red Flag Categories (from roadmap):**

1. **Budget mismatch:** Client expects below-standard work
2. **Geographic:** Distance > 60km from LV HQ
3. **Material risk:** Imported materials with 6+ week lead time
4. **Crew availability:** Multi-day during peak season (June-Sept)
5. **Low margin:** Calculated margin < 15%

**Implementation Pattern:**

**Backend Service:**
```python
# /backend/app/services/red_flag_evaluator.py

from typing import List, Dict, Any
from datetime import datetime

class RedFlag:
    def __init__(self, category: str, severity: str, message: str):
        self.category = category
        self.severity = severity  # "warning" or "critical"
        self.message = message

def evaluate_red_flags(
    submission: Dict[str, Any],
    request_data: Dict[str, Any]
) -> List[RedFlag]:
    """Evaluate submission for red flags before sending."""
    flags = []

    # 1. Budget mismatch
    if request_data.get("quoted_total"):
        predicted = submission["total_price"]
        quoted = request_data["quoted_total"]
        if quoted < predicted * 0.7:
            flags.append(RedFlag(
                category="budget_mismatch",
                severity="warning",
                message=f"Client quote (${quoted:,.0f}) is 30%+ below predicted (${predicted:,.0f})"
            ))

    # 2. Geographic distance
    if request_data.get("geographic_zone") == "red_flag":
        flags.append(RedFlag(
            category="geographic",
            severity="warning",
            message="Site is >60km from LV HQ (Abitibi/Côte-Nord zone)"
        ))

    # 3. Material risk
    if request_data.get("supply_chain_risk") == "import":
        flags.append(RedFlag(
            category="material_risk",
            severity="critical",
            message="Imported materials with 6+ week lead time"
        ))

    # 4. Crew availability (peak season)
    if request_data.get("duration_type") == "multi_day":
        now = datetime.now()
        if 6 <= now.month <= 9:  # June-Sept
            flags.append(RedFlag(
                category="crew_availability",
                severity="warning",
                message="Multi-day project during peak season (June-Sept)"
            ))

    # 5. Low margin
    materials_cost = submission["total_materials_cost"]
    labor_cost = submission.get("total_labor_cost", 0)
    total_price = submission["total_price"]
    costs = materials_cost + labor_cost
    margin = (total_price - costs) / total_price if total_price > 0 else 0

    if margin < 0.15:
        flags.append(RedFlag(
            category="low_margin",
            severity="critical",
            message=f"Margin is {margin*100:.1f}% (threshold: 15%)"
        ))

    return flags
```

**API Endpoint:**
```python
# /backend/app/routers/submissions.py

@router.get("/submissions/{id}/red-flags", response_model=List[RedFlagResponse])
async def get_submission_red_flags(id: str):
    """Evaluate red flags for a submission before sending."""
    submission = await get_submission_from_db(id)
    request_data = submission["request_data"]  # Original HybridQuoteRequest fields

    flags = evaluate_red_flags(submission, request_data)

    return [
        RedFlagResponse(
            category=f.category,
            severity=f.severity,
            message=f.message,
            dismissible=True
        )
        for f in flags
    ]
```

**Frontend Warning UI:**
```typescript
// /frontend/src/components/submissions/red-flag-banner.tsx

interface RedFlag {
  category: string;
  severity: "warning" | "critical";
  message: string;
  dismissible: boolean;
}

export function RedFlagBanner({ flags }: { flags: RedFlag[] }) {
  const [dismissed, setDismissed] = useState<Set<string>>(new Set());

  const visibleFlags = flags.filter(f => !dismissed.has(f.category));

  if (visibleFlags.length === 0) return null;

  return (
    <div className="space-y-2 mb-4">
      {visibleFlags.map((flag) => (
        <Alert
          key={flag.category}
          variant={flag.severity === "critical" ? "destructive" : "warning"}
        >
          <AlertTriangle className="h-4 w-4" />
          <AlertTitle>{t.redFlags[flag.category]}</AlertTitle>
          <AlertDescription>
            {flag.message}
            {flag.dismissible && (
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setDismissed(prev => new Set(prev).add(flag.category))}
              >
                Ignorer
              </Button>
            )}
          </AlertDescription>
        </Alert>
      ))}
    </div>
  );
}
```

**User Flow:**
1. User clicks "Send" on approved submission
2. Frontend: GET `/api/submissions/{id}/red-flags`
3. Backend: Evaluate 5 categories, return flags
4. Frontend: Show `RedFlagBanner` with dismissible alerts
5. User: Review warnings, dismiss if acceptable
6. User: Confirm send (warnings dismissed or ignored)
7. System: Proceed with email delivery

**Red Flag Storage (Audit Trail):**
```sql
-- Store dismissed flags in submission audit log
UPDATE submissions
SET audit_log = audit_log || jsonb_build_array(
  jsonb_build_object(
    'action', 'red_flags_dismissed',
    'user', 'steven@toiturelv.com',
    'timestamp', now(),
    'flags', '["budget_mismatch", "crew_availability"]'
  )
)
WHERE id = 'abc-123';
```

### 6. BILINGUAL TEMPLATE SUPPORT

**Requirement:** All export templates bilingual (FR/EN).

**Current i18n:**
- Existing i18n: `/frontend/src/lib/i18n/fr.ts` and `en.ts`
- Pattern: `useLanguage()` hook with `t.section.key` access
- Locale: Stored in localStorage as `"cortex-locale"`

**DOCX Template i18n:**
```typescript
// /frontend/src/lib/docx/quote-template.ts

import { useLanguage } from "@/lib/i18n";

export async function generateQuoteDOCX(
  quote: HybridQuoteResponse,
  category: string,
  sqft: number,
  date: string,
  locale: "fr" | "en"  // Pass locale from component
): Promise<Blob> {
  const t = locale === "fr" ? fr : en;

  const doc = new Document({
    sections: [{
      children: [
        new Paragraph({
          text: t.fullQuote.soumission,  // "SOUMISSION" or "QUOTE"
          heading: HeadingLevel.HEADING_1,
        }),
        // ...
      ],
    }],
  });

  return await Packer.toBlob(doc);
}
```

**Email i18n:**
- Detect recipient language preference (from client record or submission metadata)
- Generate email subject/body in appropriate language
- Attach both PDF and DOCX (both in same language)

**New i18n Keys Needed:**
```typescript
// fr.ts
export const fr = {
  // ... existing keys
  redFlags: {
    budgetMismatch: "Écart budgétaire",
    geographic: "Distance géographique",
    materialRisk: "Risque d'approvisionnement",
    crewAvailability: "Disponibilité de l'équipe",
    lowMargin: "Marge faible",
    ignorer: "Ignorer",
    redFlagsDetected: "Avertissements détectés",
  },
  sendDialog: {
    titre: "Envoyer la soumission",
    envoyerMaintenant: "Envoyer maintenant",
    planifier: "Planifier l'envoi",
    sauvegarderBrouillon: "Sauvegarder comme brouillon",
    dateHeure: "Date et heure d'envoi",
    destinataire: "Destinataire",
    message: "Message (optionnel)",
    confirmer: "Confirmer l'envoi",
    annuler: "Annuler",
  },
  exportFormats: {
    pdf: "PDF",
    docx: "DOCX (Word)",
    both: "PDF + DOCX",
  },
};
```

### 7. EXISTING DEPENDENCIES & PATTERNS

**Already Installed (No Changes Needed):**
- `@react-pdf/renderer` v4.3.2 — Keep for PDF generation
- `iron-session` v8.x — Extend for user identity in send logs
- `@tanstack/react-query` — Add mutations for send operations
- `zod` v4.3.5 — Add schemas for send request validation

**New Dependencies Required:**
```json
{
  "frontend": {
    "docx": "^9.5.1",
    "@upstash/qstash": "^2.x",
    "react-day-picker": "^9.x"  // or use existing date-fns for picker
  },
  "backend": {
    "resend": "^3.x"  // Python SDK
  }
}
```

**Environment Variables:**
```bash
# Backend (.env)
RESEND_API_KEY=re_xxxxx
QSTASH_TOKEN=qst_xxxxx
QSTASH_CURRENT_SIGNING_KEY=xxxxx
QSTASH_NEXT_SIGNING_KEY=xxxxx

# Frontend (.env.local)
NEXT_PUBLIC_API_URL=https://api.toiturelv.com
```

### 8. LOGO & BRANDING (LV)

**Requirement:** Both PDF and DOCX must include LV logo.

**Current PDF:** No logo yet (Phase 14-03 template shows text only: "Toiture LV")

**Logo Implementation:**

**Option 1: Embedded Base64**
```typescript
// /frontend/src/lib/assets/lv-logo.ts
export const LV_LOGO_BASE64 = "data:image/png;base64,iVBORw0KG...";
```

**Option 2: Public Asset**
```
/public/assets/lv-logo.png
```

**DOCX Logo Insertion:**
```typescript
import { ImageRun } from "docx";

new Paragraph({
  children: [
    new ImageRun({
      data: logoBuffer,  // Buffer from fetch or base64
      transformation: {
        width: 150,
        height: 75,
      },
    }),
  ],
  alignment: AlignmentType.CENTER,
});
```

**PDF Logo Insertion:**
```tsx
import { Image } from "@react-pdf/renderer";

<Image src={LV_LOGO_BASE64} style={{ width: 150, height: 75 }} />
```

**ACTION NEEDED:** Obtain LV logo file from Laurent/Amin (PNG or SVG preferred, min 300px width).

### 9. TESTING STRATEGY

**Unit Tests:**
- Red flag evaluator logic (5 categories)
- DOCX generation (structure validation)
- Email send logic (mock Resend API)

**Integration Tests:**
- Send now workflow (end-to-end)
- Scheduled send workflow (QStash callback)
- Red flag evaluation on real submissions

**Manual Tests:**
- Generate PDF + DOCX, compare formatting
- Send test email with attachments
- Schedule email for 1 minute in future, verify delivery
- Dismiss red flags, confirm audit log entry

### 10. EDGE CASES & ERROR HANDLING

**Edge Cases:**

1. **Submission edited after scheduling:** QStash holds stale data
   - **Solution:** Store submission_id in QStash payload, fetch latest data in callback

2. **Recipient email invalid:** Resend rejects
   - **Solution:** Validate email format before queuing, update send_status to "failed"

3. **QStash delivery failure:** Webhook never fires
   - **Solution:** QStash has automatic retries (3 attempts by default), log failures

4. **Multiple red flags (all critical):** Should send be blocked?
   - **Solution:** Warnings are dismissible — user decides. Audit log tracks dismissals.

5. **Timezone confusion:** User in Montreal, Vercel servers in UTC
   - **Solution:** Convert scheduledDate from America/Montreal to UTC before QStash

6. **Large attachments (PDF + DOCX > 10MB):** Email services have limits
   - **Solution:** Resend limit is 40MB — should not hit for typical quotes

**Error Handling:**
```typescript
// Send endpoint error handling
try {
  const pdfBlob = await generateQuotePDF(quote, ...);
  const docxBlob = await generateQuoteDOCX(quote, ...);

  if (sendOption === "now") {
    await resend.emails.send({ ... });
    await updateSendStatus(submissionId, "sent");
  } else if (sendOption === "schedule") {
    await qstash.publishJSON({ ... });
    await updateSendStatus(submissionId, "scheduled");
  }
} catch (error) {
  await updateSendStatus(submissionId, "failed");
  await logError(error);
  throw new Error("Email send failed");
}
```

## Key Decisions Summary

| Decision | Choice | Rationale |
|----------|--------|-----------|
| DOCX library | `docx` npm package | Declarative API, TypeScript support, matches PDF pattern |
| Email service | Resend | Developer-friendly, good Vercel integration, attachment support |
| Scheduling | QStash | Per-submission custom scheduling, works on Vercel serverless |
| Date picker | `react-day-picker` or `date-fns` | Already have `date-fns`, can build simple picker |
| Red flags storage | PostgreSQL JSONB audit log | Flexible schema, tracks dismissals with timestamps |
| Template pattern | Client-side generation | Same as PDF (Phase 14-03), fast UX |
| i18n approach | Locale parameter + existing i18n | Reuse existing translation infrastructure |
| Logo format | Base64 embedded | No external asset dependencies, works offline |

## Dependencies on Phase 23

**CRITICAL:** Phase 24 depends on Phase 23 being complete:

1. **submissions table exists** — Phase 23 creates table with line items, status workflow
2. **approval workflow implemented** — Only `approved` submissions can be sent
3. **audit_log JSONB column** — Red flag dismissals logged here
4. **client metadata captured** — Need recipient_email for send

**Phase 23 Deliverables Required:**
- `submissions` table with `status` column
- `POST /api/submissions` endpoint
- Approval flow (only Laurent can approve)
- Notes/audit trail JSONB columns

**If Phase 23 Not Complete:** Phase 24 can proceed with mockup submissions, but integration will be blocked.

## Out of Scope for Phase 24

**Explicitly NOT included:**
- Email tracking (open rates, click tracking) — future enhancement
- Bulk send (multiple submissions at once) — not in roadmap
- SMS notifications — not in roadmap
- Custom email templates per client — future enhancement
- Signature capture — future enhancement
- Payment links in email — future enhancement

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| QStash downtime prevents scheduled sends | Low | High | Add fallback: check for `scheduled` submissions daily via Vercel Cron |
| Resend API rate limits | Low | Medium | Free tier: 3,000/month — monitor usage, upgrade if needed |
| DOCX formatting inconsistencies | Medium | Low | Thorough manual testing, compare with PDF side-by-side |
| Red flags produce false positives | Medium | Low | Make all flags dismissible, log dismissals for tuning |
| Logo file missing at launch | High | Low | Use text-only template as fallback |

## Next Steps for Planning

**Ready to plan when:**
1. Phase 23 (Submission Workflow) is complete or near completion
2. LV logo file obtained from Laurent/Amin
3. Resend account created (need API key)
4. QStash account created (need token + signing keys)
5. Decision made on date-time picker approach (custom build vs library)

**Suggested Plan Structure:**
- **Plan 24-01:** DOCX generation (parallel to PDF, same template data)
- **Plan 24-02:** Email sending (Resend integration, send now + draft states)
- **Plan 24-03:** Scheduled send (QStash integration, date-time picker UI)
- **Plan 24-04:** Red flag system (evaluator service, frontend banner, audit logging)
- **Plan 24-05:** i18n completion (bilingual templates, email bodies, red flag messages)

## Sources

Sources consulted during research:

- [GitHub - dolanmiu/docx](https://github.com/dolanmiu/docx) — DOCX generation library
- [docx - npm](https://www.npmjs.com/package/docx) — NPM package details
- [Vercel Send Email: Tutorial with Code Snippets [2026]](https://mailtrap.io/blog/vercel-send-email/) — Email sending on Vercel
- [Building an Email Scheduler with Vercel Functions and QStash](https://upstash.com/blog/email-scheduler-qstash) — QStash scheduling pattern

---

**Research completed:** 2026-02-10
**Confidence level:** HIGH — All libraries researched, patterns validated, dependencies mapped
**Blockers:** Phase 23 completion, LV logo file, Resend/QStash accounts
