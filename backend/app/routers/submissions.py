"""Submissions router for editable quote workflow with approval process.

This router provides 14 endpoints for the complete submission lifecycle:
- POST /submissions: Create new submission
- GET /submissions: List submissions with filters
- GET /submissions/{id}: Get submission details
- PATCH /submissions/{id}: Update draft submission
- POST /submissions/{id}/finalize: Draft -> pending_approval
- POST /submissions/{id}/approve: Pending -> approved (admin only)
- POST /submissions/{id}/reject: Pending -> rejected (admin only)
- POST /submissions/{id}/return-to-draft: Rejected/pending -> draft
- POST /submissions/{id}/notes: Add note
- POST /submissions/{id}/upsells: Create upsell child
- GET /submissions/{id}/upsell-suggestions: Get upsell options
- GET /submissions/{id}/red-flags: Evaluate red flags (Phase 24)
- POST /submissions/{id}/send: Send/schedule/draft quote (Phase 24)
- POST /submissions/{id}/dismiss-flags: Log dismissed red flags (Phase 24)

Role-based access:
- Approve/reject endpoints require X-User-Role: admin header (403 for non-admin)
- Return-to-draft is available to all authenticated users
- All mutations track user via X-User-Name header for audit trail
"""

import logging
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Body, Header, HTTPException, Query

from app.schemas.red_flag import (
    DismissFlagsRequest,
    RedFlagResponse,
    SendSubmissionRequest,
)
from app.schemas.submission import (
    NoteCreate,
    SubmissionCreate,
    SubmissionResponse,
    SubmissionUpdate,
    UpsellCreate,
)
from app.services.email_service import send_quote_email
from app.services.red_flag_evaluator import evaluate_red_flags
from app.services.submission_service import (
    add_note,
    approve_submission,
    create_submission,
    create_upsell_submission,
    finalize_submission,
    get_submission,
    get_upsell_suggestions,
    list_submissions,
    reject_submission,
    return_to_draft_submission,
    update_submission,
)
from app.services.supabase_client import get_supabase

logger = logging.getLogger(__name__)

router = APIRouter(tags=["submissions"])


@router.post("/submissions", status_code=201)
async def create_submission_endpoint(data: SubmissionCreate):
    """Create a new submission from hybrid quote output.

    Creates a draft submission with line items, pricing tiers, and initial
    audit entry. The submission can then be edited before finalization.

    Returns:
        Created submission with full details
    """
    try:
        result = create_submission(data)
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Create submission endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/submissions")
async def list_submissions_endpoint(
    status: Optional[str] = None,
    limit: int = Query(default=50, le=200),
    offset: int = Query(default=0, ge=0),
):
    """List submissions with optional status filter and pagination.

    Query parameters:
        status: Filter by status (draft, pending_approval, approved, rejected)
        limit: Maximum results (default 50, max 200)
        offset: Number to skip for pagination

    Returns:
        Dict with items list and total count
    """
    try:
        result = list_submissions(status=status, limit=limit, offset=offset)
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"List submissions endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/submissions/{submission_id}")
async def get_submission_endpoint(submission_id: str):
    """Get single submission with full details including children.

    Returns submission with line items, notes, audit log, and any upsell
    child submissions linked to this parent.

    Args:
        submission_id: Submission UUID

    Returns:
        Full submission details with children list
    """
    try:
        result = get_submission(submission_id)
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get submission endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/submissions/{submission_id}")
async def update_submission_endpoint(
    submission_id: str,
    data: SubmissionUpdate,
    x_user_name: str = Header(default="unknown"),
):
    """Update line items, tier, or client name (draft only).

    Only draft submissions can be edited. Updates trigger automatic total
    recalculation and append audit entries.

    Args:
        submission_id: Submission UUID
        data: Update data (line_items, selected_tier, client_name)
        x_user_name: User making the update (from header)

    Returns:
        Updated submission

    Raises:
        400: If submission is not in draft status
        404: If submission not found
    """
    try:
        result = update_submission(submission_id, data, x_user_name)
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update submission endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/submissions/{submission_id}/finalize")
async def finalize_submission_endpoint(
    submission_id: str,
    x_user_name: str = Header(default="unknown"),
):
    """Finalize submission: draft -> pending_approval.

    Validates that line_items is not empty before transitioning to
    pending_approval status. Sets finalized_at timestamp.

    Args:
        submission_id: Submission UUID
        x_user_name: User finalizing (from header)

    Returns:
        Updated submission in pending_approval status

    Raises:
        400: If not in draft status or line_items empty
        404: If submission not found
    """
    try:
        result = finalize_submission(submission_id, x_user_name)
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Finalize submission endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/submissions/{submission_id}/approve")
async def approve_submission_endpoint(
    submission_id: str,
    x_user_name: str = Header(default="unknown"),
    x_user_role: str = Header(default="estimator"),
):
    """Approve submission (admin only): pending_approval -> approved.

    Requires admin role. Sets approved_at timestamp and approved_by user.
    Approved status is terminal - no further transitions allowed.

    Args:
        submission_id: Submission UUID
        x_user_name: Admin user approving (from header)
        x_user_role: User role (from header)

    Returns:
        Updated submission in approved status

    Raises:
        403: If user role is not admin
        400: If not in pending_approval status
        404: If submission not found
    """
    if x_user_role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required for approval")

    try:
        result = approve_submission(submission_id, x_user_name)
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Approve submission endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/submissions/{submission_id}/reject")
async def reject_submission_endpoint(
    submission_id: str,
    reason: Optional[str] = Body(default=None, embed=True),
    x_user_name: str = Header(default="unknown"),
    x_user_role: str = Header(default="estimator"),
):
    """Reject submission (admin only): pending_approval -> rejected.

    Requires admin role. Records optional rejection reason in audit log.
    Rejected submissions can be returned to draft for corrections.

    Args:
        submission_id: Submission UUID
        reason: Optional rejection reason
        x_user_name: Admin user rejecting (from header)
        x_user_role: User role (from header)

    Returns:
        Updated submission in rejected status

    Raises:
        403: If user role is not admin
        400: If not in pending_approval status
        404: If submission not found
    """
    if x_user_role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required for rejection")

    try:
        result = reject_submission(submission_id, x_user_name, reason)
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Reject submission endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/submissions/{submission_id}/return-to-draft")
async def return_to_draft_endpoint(
    submission_id: str,
    x_user_name: str = Header(default="unknown"),
):
    """Return submission to draft status: rejected|pending_approval -> draft.

    Allows any user to return a rejected or pending_approval submission
    back to draft for further editing. Clears finalized_at timestamp.
    The state machine VALID_TRANSITIONS validates that only rejected and
    pending_approval statuses can transition to draft.

    This endpoint does NOT require admin role - estimators need to fix
    rejected submissions and may need to correct pending submissions.

    Args:
        submission_id: Submission UUID
        x_user_name: User returning to draft (from header)

    Returns:
        Updated submission in draft status

    Raises:
        400: If current status cannot transition to draft
        404: If submission not found
    """
    try:
        result = return_to_draft_submission(submission_id, x_user_name)
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Return to draft endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/submissions/{submission_id}/notes")
async def add_note_endpoint(
    submission_id: str,
    data: NoteCreate,
):
    """Add timestamped note to submission.

    Notes are appended to the notes JSONB array and include UUID, text,
    user attribution, and ISO timestamp. An audit entry is also created.

    Args:
        submission_id: Submission UUID
        data: Note creation data (text, created_by)

    Returns:
        Updated submission with new note

    Raises:
        404: If submission not found
    """
    try:
        result = add_note(submission_id, data.text, data.created_by)
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Add note endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/submissions/{submission_id}/upsells")
async def create_upsell_endpoint(
    submission_id: str,
    data: UpsellCreate,
    x_user_name: str = Header(default="unknown"),
):
    """Create upsell child submission linked to parent.

    Creates a new draft submission with parent_submission_id reference.
    Inherits category and client_name from parent. Line items are empty
    for the estimator to fill later.

    Args:
        submission_id: Parent submission UUID
        data: Upsell creation data (upsell_type)
        x_user_name: User creating upsell (from header)

    Returns:
        Created child submission

    Raises:
        404: If parent submission not found
    """
    try:
        result = create_upsell_submission(
            submission_id, data.upsell_type, data.created_by or x_user_name
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Create upsell endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/submissions/{submission_id}/upsell-suggestions")
async def get_upsell_suggestions_endpoint(submission_id: str):
    """Get category-specific upsell suggestions for this submission.

    Fetches submission to determine category, then returns category-specific
    upsell rules from upsell_rules.json plus universal rules that apply to
    all categories.

    Args:
        submission_id: Submission UUID

    Returns:
        List of upsell suggestion objects with bilingual names/descriptions

    Raises:
        404: If submission not found
        500: If upsell rules file not found or invalid
    """
    try:
        # Fetch submission to get category
        submission = get_submission(submission_id)
        category = submission.get("category")

        if not category:
            raise HTTPException(status_code=400, detail="Submission has no category")

        # Get suggestions for this category
        suggestions = get_upsell_suggestions(category)
        return suggestions

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get upsell suggestions endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Phase 24: Red flags, send, and dismiss endpoints


@router.get("/submissions/{submission_id}/red-flags", response_model=List[RedFlagResponse])
async def get_red_flags(submission_id: str):
    """Evaluate red flags for a submission before sending.

    Checks 5 risk categories:
    - Budget mismatch: Client quoted 30%+ below predicted
    - Geographic: Site >60km from LV HQ
    - Material risk: Imported materials (6+ weeks)
    - Crew availability: Multi-day during peak season
    - Low margin: Margin <15%

    Args:
        submission_id: Submission UUID

    Returns:
        List of applicable red flags with bilingual messages

    Raises:
        404: If submission not found
        503: If database not available
    """
    supabase = get_supabase()
    if not supabase:
        raise HTTPException(503, "Database not available")

    try:
        result = supabase.table("submissions").select("*").eq("id", submission_id).single().execute()
        if not result.data:
            raise HTTPException(404, "Submission not found")

        submission = result.data
        # Extract request data fields that red flags check
        # Phase 22 fields are stored in the submission record
        request_data = {
            "quoted_total": submission.get("quoted_total"),
            "geographic_zone": submission.get("geographic_zone"),
            "supply_chain_risk": submission.get("supply_chain_risk"),
            "duration_type": submission.get("duration_type"),
        }

        flags = evaluate_red_flags(submission, request_data)
        return flags

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get red flags endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/submissions/{submission_id}/send")
async def send_submission(submission_id: str, request: SendSubmissionRequest):
    """Send, schedule, or save submission as draft.

    Send options:
    - now: Immediately send email via Resend API
    - schedule: Store scheduled_send_at for future delivery
    - draft: Save email details without sending

    Args:
        submission_id: Submission UUID
        request: Send request with send_option, recipient_email, etc.

    Returns:
        Dict with status and send_status fields

    Raises:
        400: If not approved or validation fails
        404: If submission not found
        503: If database not available
    """
    supabase = get_supabase()
    if not supabase:
        raise HTTPException(503, "Database not available")

    try:
        result = supabase.table("submissions").select("*").eq("id", submission_id).single().execute()
        if not result.data:
            raise HTTPException(404, "Submission not found")

        submission = result.data

        # Only approved submissions can be sent
        if submission.get("status") != "approved":
            raise HTTPException(400, "Only approved submissions can be sent")

        update_data = {
            "recipient_email": request.recipient_email,
            "email_subject": request.email_subject,
            "email_body": request.email_body,
        }

        if request.send_option == "draft":
            update_data["send_status"] = "draft"

        elif request.send_option == "now":
            if not request.recipient_email:
                raise HTTPException(400, "recipient_email required for send now")

            # Send email via Resend
            subject = request.email_subject or f"Soumission - Toiture LV - {submission.get('category', '')}"
            body = request.email_body or "<p>Veuillez trouver ci-joint votre soumission.</p><p>Toiture LV</p>"

            try:
                # Note: PDF/DOCX generation happens on frontend for now
                # Future iteration will pass attachments as base64 or generate server-side
                await send_quote_email(
                    to_email=request.recipient_email,
                    subject=subject,
                    body=body,
                )
                update_data["send_status"] = "sent"
                update_data["sent_at"] = datetime.utcnow().isoformat()
            except RuntimeError as e:
                update_data["send_status"] = "failed"
                # Log error in audit_log
                audit_entry = {
                    "action": "send_failed",
                    "timestamp": datetime.utcnow().isoformat(),
                    "error": str(e)
                }
                existing_audit = submission.get("audit_log", []) or []
                existing_audit.append(audit_entry)
                update_data["audit_log"] = existing_audit

        elif request.send_option == "schedule":
            if not request.recipient_email:
                raise HTTPException(400, "recipient_email required for scheduled send")
            if not request.scheduled_send_at:
                raise HTTPException(400, "scheduled_send_at required for scheduled send")

            update_data["send_status"] = "scheduled"
            update_data["scheduled_send_at"] = request.scheduled_send_at.isoformat()
            # Note: Actual scheduled delivery via QStash is out of scope for MVP
            # Scheduled submissions can be picked up by a future cron job

        supabase.table("submissions").update(update_data).eq("id", submission_id).execute()

        return {"status": "ok", "send_status": update_data.get("send_status", "draft")}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Send submission endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/submissions/{submission_id}/dismiss-flags")
async def dismiss_red_flags(submission_id: str, request: DismissFlagsRequest):
    """Log dismissed red flags in audit trail.

    Records which red flag categories were dismissed by which user,
    with timestamp. This creates an audit trail for risk acknowledgment.

    Args:
        submission_id: Submission UUID
        request: Dismissed categories and user attribution

    Returns:
        Dict with status and count of dismissed flags

    Raises:
        404: If submission not found
        503: If database not available
    """
    supabase = get_supabase()
    if not supabase:
        raise HTTPException(503, "Database not available")

    try:
        result = supabase.table("submissions").select("audit_log").eq("id", submission_id).single().execute()
        if not result.data:
            raise HTTPException(404, "Submission not found")

        audit_entry = {
            "action": "red_flags_dismissed",
            "timestamp": datetime.utcnow().isoformat(),
            "dismissed_by": request.dismissed_by,
            "categories": [c.value for c in request.dismissed_categories],
        }

        existing_audit = result.data.get("audit_log", []) or []
        existing_audit.append(audit_entry)

        supabase.table("submissions").update({"audit_log": existing_audit}).eq("id", submission_id).execute()

        return {"status": "ok", "dismissed": len(request.dismissed_categories)}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Dismiss red flags endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
