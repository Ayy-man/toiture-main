---
phase: 24-export-send-red-flags
plan: 02
subsystem: api
tags: [resend, email, red-flags, risk-assessment, backend]

# Dependency graph
requires:
  - phase: 23-submission-workflow-editing
    provides: Submission workflow with submissions table and router
provides:
  - Red flag evaluator service checking 5 risk categories
  - Email service using Resend SDK for quote delivery
  - Three new submission endpoints (red-flags, send, dismiss-flags)
  - SQL migration for send tracking columns
affects: [24-03-send-dialog-ui, submission-workflow, quote-delivery]

# Tech tracking
tech-stack:
  added: [resend>=3.0.0]
  patterns: [lazy-initialized email client, bilingual red flag messages, send status state machine]

key-files:
  created:
    - backend/app/schemas/red_flag.py
    - backend/app/services/red_flag_evaluator.py
    - backend/app/services/email_service.py
    - backend/sql/alter_submissions_send_columns.sql
  modified:
    - backend/app/routers/submissions.py
    - backend/requirements.txt

key-decisions:
  - "Lazy-init Resend client pattern for graceful degradation when RESEND_API_KEY not set"
  - "Bilingual red flag messages (fr/en) for i18n support"
  - "Send status enum: draft, scheduled, sent, failed"
  - "Audit trail for dismissed red flags in JSONB audit_log"
  - "PDF/DOCX attachments deferred to frontend generation (MVP sends body-only email)"

patterns-established:
  - "Red flag evaluation: 5 categories with severity (warning/critical) and bilingual messages"
  - "Send options: now (immediate), schedule (future), draft (save-only)"
  - "Cross-field validation in Pydantic with model_validator for send requirements"

# Metrics
duration: 3min
completed: 2026-02-09
---

# Phase 24 Plan 02: Backend Red Flags & Send Infrastructure Summary

**Red flag evaluator with 5 risk categories, Resend email service with lazy initialization, and 3 new submission endpoints for send workflow**

## Performance

- **Duration:** 3 min
- **Started:** 2026-02-09T20:00:21Z
- **Completed:** 2026-02-09T20:03:34Z
- **Tasks:** 2
- **Files modified:** 6 (3 created, 3 modified)

## Accomplishments
- Red flag evaluator checking budget mismatch, geographic distance, material risk, crew availability, and low margin
- Email service using Resend SDK with graceful error handling for quote delivery
- GET /submissions/{id}/red-flags endpoint returning bilingual risk warnings
- POST /submissions/{id}/send endpoint supporting now/schedule/draft options
- POST /submissions/{id}/dismiss-flags endpoint logging dismissed flags in audit trail
- SQL migration adding send_status, scheduled_send_at, sent_at, recipient_email columns

## Task Commits

Each task was committed atomically:

1. **Task 1: Red flag evaluator service, Pydantic schemas, and SQL migration** - `6873114` (feat)
2. **Task 2: Email service and submissions router send/red-flag endpoints** - `8628dee` (feat)

## Files Created/Modified

**Created:**
- `backend/app/schemas/red_flag.py` - Pydantic models for red flags, send requests, and dismissal
- `backend/app/services/red_flag_evaluator.py` - Rule-based red flag evaluation service
- `backend/app/services/email_service.py` - Resend email service with lazy initialization
- `backend/sql/alter_submissions_send_columns.sql` - Migration adding send tracking columns

**Modified:**
- `backend/app/routers/submissions.py` - Added 3 new endpoints (red-flags, send, dismiss-flags)
- `backend/requirements.txt` - Added resend>=3.0.0 dependency

## Decisions Made

**1. Lazy-init Resend client pattern**
- Rationale: Allows service to be imported without requiring RESEND_API_KEY, enabling graceful degradation and testing without API key
- Pattern: `get_resend_client()` returns None if API key not configured

**2. Bilingual red flag messages**
- Rationale: Quebec market is French-primary but system supports English, so all red flags have message_fr and message_en fields
- Implementation: RedFlagResponse model with both message fields

**3. Send status enum with 4 states**
- Rationale: Clear state machine for send workflow: draft (save-only), scheduled (future), sent (success), failed (error)
- Implementation: SendStatus enum and valid_send_status constraint in SQL

**4. Dismissed flags in audit_log**
- Rationale: Risk acknowledgment needs audit trail, JSONB audit_log already exists from Phase 23 for append-only history
- Implementation: dismiss_red_flags endpoint appends to audit_log with timestamp and categories

**5. PDF/DOCX attachments deferred**
- Rationale: MVP sends body-only email, frontend will generate PDF/DOCX in future iteration
- Note in code: "Note: PDF/DOCX generation happens on frontend for now"

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None - all imports verified successfully, schemas and services working as expected.

## User Setup Required

**External services require manual configuration.** See plan frontmatter `user_setup` section for:

**Service:** Resend
- **Why:** Email delivery for sending quotes to clients
- **Environment variable:** `RESEND_API_KEY`
  - Source: Resend Dashboard -> API Keys -> Create API Key
- **Dashboard config:**
  - Task: Create Resend account and verify domain (toiturelv.com or use onboarding@resend.dev for testing)
  - Location: https://resend.com/signup

**Verification:** After setting `RESEND_API_KEY`, test with POST /submissions/{id}/send with send_option: "now"

## Next Phase Readiness

- Backend infrastructure complete for send workflow
- Ready for Phase 24-03 (Send Dialog UI) to consume these endpoints
- SQL migration ready to run in Supabase SQL editor
- Red flags will warn estimators about risky submissions before sending
- Email service ready to deliver quotes when RESEND_API_KEY configured

**Blockers:** None - all code committed and verified

---
*Phase: 24-export-send-red-flags*
*Completed: 2026-02-09*

## Self-Check: PASSED

All files verified:
- FOUND: backend/app/schemas/red_flag.py
- FOUND: backend/app/services/red_flag_evaluator.py
- FOUND: backend/app/services/email_service.py
- FOUND: backend/sql/alter_submissions_send_columns.sql

All commits verified:
- FOUND: 6873114 (Task 1)
- FOUND: 8628dee (Task 2)

Verification timestamp: 2026-02-09T20:03:34Z
