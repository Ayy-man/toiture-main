"""Submission service for editable quote workflow with approval process.

This service handles the complete lifecycle of submissions:
- CRUD operations (create, read, update, list)
- State machine workflow (draft -> pending -> approved/rejected)
- Return-to-draft transitions (rejected/pending -> draft)
- Notes and audit trail management
- Upsell child submission creation
- Upsell suggestion retrieval

Business rules:
- Only draft submissions can be edited
- State transitions follow VALID_TRANSITIONS rules
- All mutations append audit entries
- Notes are timestamped and attributed
- Upsells inherit parent category and client name
"""

import json
import logging
import os
from datetime import datetime
from typing import Optional
from uuid import uuid4

from fastapi import HTTPException

from app.schemas.submission import (
    VALID_TRANSITIONS,
    AuditEntry,
    LineItem,
    Note,
    SubmissionCreate,
    SubmissionStatus,
    SubmissionUpdate,
)
from app.services.supabase_client import get_supabase

logger = logging.getLogger(__name__)


def _get_db():
    """Get Supabase client or raise 503 if not configured."""
    supabase = get_supabase()
    if supabase is None:
        raise HTTPException(
            status_code=503, detail="Database not configured. Check SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY."
        )
    return supabase


def _append_audit_entry(
    submission_id: str,
    action: str,
    user: str,
    changes: Optional[dict] = None,
    reason: Optional[str] = None,
) -> None:
    """Append audit entry to submission's audit log.

    Uses fetch-append-write pattern for JSONB operations.
    """
    supabase = _get_db()

    # Fetch current audit log
    result = supabase.table("submissions").select("audit_log").eq("id", submission_id).single().execute()
    current_log = result.data.get("audit_log", []) if result.data else []

    # Append new entry
    new_entry = {
        "action": action,
        "user": user,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "changes": changes,
        "reason": reason,
    }
    current_log.append(new_entry)

    # Write back
    supabase.table("submissions").update({"audit_log": current_log}).eq("id", submission_id).execute()


def create_submission(data: SubmissionCreate) -> dict:
    """Create new submission from hybrid quote output.

    Args:
        data: Submission creation data with line items and pricing tiers

    Returns:
        Created submission row as dict

    Raises:
        HTTPException: 503 if database not configured, 500 for other errors
    """
    supabase = _get_db()

    try:
        # Calculate totals from line items
        materials_cost = sum(item.total for item in data.line_items if item.type == "material")
        labor_cost = sum(item.total for item in data.line_items if item.type == "labor")
        total_price = materials_cost + labor_cost

        # Prepare submission data
        submission_data = {
            "category": data.category,
            "sqft": data.sqft,
            "client_name": data.client_name,
            "created_by": data.created_by,
            "estimate_id": data.estimate_id,
            "status": "draft",
            "line_items": [item.model_dump() for item in data.line_items],
            "pricing_tiers": data.pricing_tiers,
            "selected_tier": data.selected_tier,
            "total_materials_cost": materials_cost,
            "total_labor_cost": labor_cost,
            "total_price": total_price,
            "notes": [],
            "audit_log": [
                {
                    "action": "created",
                    "user": data.created_by or "unknown",
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "changes": None,
                    "reason": None,
                }
            ],
        }

        # Insert submission
        result = supabase.table("submissions").insert(submission_data).execute()

        logger.info(f"Created submission {result.data[0]['id']} for category {data.category}")
        return result.data[0]

    except Exception as e:
        logger.error(f"Failed to create submission: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create submission: {str(e)}")


def get_submission(submission_id: str) -> dict:
    """Get submission by ID with children (upsells).

    Args:
        submission_id: Submission UUID

    Returns:
        Submission row with children list attached

    Raises:
        HTTPException: 404 if not found, 503 if database not configured
    """
    supabase = _get_db()

    try:
        # Fetch main submission
        result = supabase.table("submissions").select("*").eq("id", submission_id).single().execute()

        if not result.data:
            raise HTTPException(status_code=404, detail=f"Submission {submission_id} not found")

        submission = result.data

        # Fetch children (upsells linked to this parent)
        children_result = (
            supabase.table("submissions")
            .select("*")
            .eq("parent_submission_id", submission_id)
            .execute()
        )
        submission["children"] = children_result.data if children_result.data else []

        logger.info(f"Retrieved submission {submission_id} with {len(submission['children'])} children")
        return submission

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get submission {submission_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get submission: {str(e)}")


def list_submissions(
    status: Optional[str] = None, limit: int = 50, offset: int = 0
) -> dict:
    """List submissions with optional status filter and pagination.

    Args:
        status: Optional status filter (draft, pending_approval, approved, rejected)
        limit: Maximum number of results (default 50, max 200)
        offset: Number of results to skip for pagination

    Returns:
        Dict with items list and total count

    Raises:
        HTTPException: 503 if database not configured
    """
    supabase = _get_db()

    try:
        # Build query
        query = supabase.table("submissions").select("*", count="exact")

        # Apply status filter if provided
        if status:
            query = query.eq("status", status)

        # Apply ordering and pagination
        query = query.order("created_at", desc=True).range(offset, offset + limit - 1)

        result = query.execute()

        logger.info(
            f"Listed {len(result.data)} submissions (status={status}, offset={offset}, limit={limit})"
        )

        return {"items": result.data, "total": result.count}

    except Exception as e:
        logger.error(f"Failed to list submissions: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list submissions: {str(e)}")


def update_submission(submission_id: str, data: SubmissionUpdate, user: str) -> dict:
    """Update draft submission (line items, tier, or client name).

    Only allowed for submissions in draft status.

    Args:
        submission_id: Submission UUID
        data: Update data (line_items, selected_tier, client_name)
        user: User making the update

    Returns:
        Updated submission row

    Raises:
        HTTPException: 400 if not draft, 404 if not found, 503 if database not configured
    """
    supabase = _get_db()

    try:
        # Fetch current submission to check status
        current = supabase.table("submissions").select("*").eq("id", submission_id).single().execute()

        if not current.data:
            raise HTTPException(status_code=404, detail=f"Submission {submission_id} not found")

        if current.data["status"] != "draft":
            raise HTTPException(
                status_code=400,
                detail=f"Cannot update submission in {current.data['status']} status. Only draft submissions can be edited.",
            )

        # Build update data
        update_data = {}
        changes = {}

        if data.line_items is not None:
            # Recalculate totals when line items change
            materials_cost = sum(item.total for item in data.line_items if item.type == "material")
            labor_cost = sum(item.total for item in data.line_items if item.type == "labor")
            total_price = materials_cost + labor_cost

            update_data["line_items"] = [item.model_dump() for item in data.line_items]
            update_data["total_materials_cost"] = materials_cost
            update_data["total_labor_cost"] = labor_cost
            update_data["total_price"] = total_price

            changes["line_items"] = {
                "old": f"{len(current.data['line_items'])} items",
                "new": f"{len(data.line_items)} items",
            }

        if data.selected_tier is not None:
            update_data["selected_tier"] = data.selected_tier
            changes["selected_tier"] = {"old": current.data["selected_tier"], "new": data.selected_tier}

        if data.client_name is not None:
            update_data["client_name"] = data.client_name
            changes["client_name"] = {
                "old": current.data.get("client_name"),
                "new": data.client_name,
            }

        # Apply update
        result = supabase.table("submissions").update(update_data).eq("id", submission_id).execute()

        # Append audit entry
        _append_audit_entry(submission_id, "edited", user, changes=changes)

        logger.info(f"Updated submission {submission_id} by {user}")
        return result.data[0]

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update submission {submission_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update submission: {str(e)}")


def finalize_submission(submission_id: str, user: str) -> dict:
    """Finalize submission: draft -> pending_approval.

    Args:
        submission_id: Submission UUID
        user: User finalizing the submission

    Returns:
        Updated submission row

    Raises:
        HTTPException: 400 if not draft or line_items empty, 404 if not found
    """
    supabase = _get_db()

    try:
        # Fetch current submission
        current = supabase.table("submissions").select("*").eq("id", submission_id).single().execute()

        if not current.data:
            raise HTTPException(status_code=404, detail=f"Submission {submission_id} not found")

        if current.data["status"] != "draft":
            raise HTTPException(
                status_code=400,
                detail=f"Cannot finalize submission in {current.data['status']} status",
            )

        if not current.data.get("line_items") or len(current.data["line_items"]) == 0:
            raise HTTPException(
                status_code=400, detail="Cannot finalize submission with empty line items"
            )

        # Update status
        update_data = {
            "status": "pending_approval",
            "finalized_at": datetime.utcnow().isoformat() + "Z",
        }
        result = supabase.table("submissions").update(update_data).eq("id", submission_id).execute()

        # Append audit entry
        _append_audit_entry(
            submission_id,
            "finalized",
            user,
            changes={"status": {"old": "draft", "new": "pending_approval"}},
        )

        logger.info(f"Finalized submission {submission_id} by {user}")
        return result.data[0]

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to finalize submission {submission_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to finalize submission: {str(e)}")


def approve_submission(submission_id: str, user: str) -> dict:
    """Approve submission: pending_approval -> approved (admin only).

    Args:
        submission_id: Submission UUID
        user: Admin user approving the submission

    Returns:
        Updated submission row

    Raises:
        HTTPException: 400 if not pending_approval, 404 if not found
    """
    supabase = _get_db()

    try:
        # Fetch current submission
        current = supabase.table("submissions").select("*").eq("id", submission_id).single().execute()

        if not current.data:
            raise HTTPException(status_code=404, detail=f"Submission {submission_id} not found")

        if current.data["status"] != "pending_approval":
            raise HTTPException(
                status_code=400,
                detail=f"Cannot approve submission in {current.data['status']} status",
            )

        # Update status
        update_data = {
            "status": "approved",
            "approved_at": datetime.utcnow().isoformat() + "Z",
            "approved_by": user,
        }
        result = supabase.table("submissions").update(update_data).eq("id", submission_id).execute()

        # Append audit entry
        _append_audit_entry(
            submission_id,
            "approved",
            user,
            changes={"status": {"old": "pending_approval", "new": "approved"}},
        )

        logger.info(f"Approved submission {submission_id} by {user}")
        return result.data[0]

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to approve submission {submission_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to approve submission: {str(e)}")


def reject_submission(submission_id: str, user: str, reason: Optional[str] = None) -> dict:
    """Reject submission: pending_approval -> rejected (admin only).

    Args:
        submission_id: Submission UUID
        user: Admin user rejecting the submission
        reason: Optional rejection reason

    Returns:
        Updated submission row

    Raises:
        HTTPException: 400 if not pending_approval, 404 if not found
    """
    supabase = _get_db()

    try:
        # Fetch current submission
        current = supabase.table("submissions").select("*").eq("id", submission_id).single().execute()

        if not current.data:
            raise HTTPException(status_code=404, detail=f"Submission {submission_id} not found")

        if current.data["status"] != "pending_approval":
            raise HTTPException(
                status_code=400,
                detail=f"Cannot reject submission in {current.data['status']} status",
            )

        # Update status
        update_data = {"status": "rejected"}
        result = supabase.table("submissions").update(update_data).eq("id", submission_id).execute()

        # Append audit entry with reason
        _append_audit_entry(
            submission_id,
            "rejected",
            user,
            changes={"status": {"old": "pending_approval", "new": "rejected"}},
            reason=reason,
        )

        logger.info(f"Rejected submission {submission_id} by {user} (reason: {reason})")
        return result.data[0]

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to reject submission {submission_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to reject submission: {str(e)}")


def return_to_draft_submission(submission_id: str, user: str) -> dict:
    """Return submission to draft status: rejected|pending_approval -> draft.

    Allows estimators to fix rejected submissions or make corrections to
    pending submissions before approval.

    Args:
        submission_id: Submission UUID
        user: User returning the submission to draft

    Returns:
        Updated submission row

    Raises:
        HTTPException: 400 if invalid status, 404 if not found
    """
    supabase = _get_db()

    try:
        # Fetch current submission
        current = supabase.table("submissions").select("*").eq("id", submission_id).single().execute()

        if not current.data:
            raise HTTPException(status_code=404, detail=f"Submission {submission_id} not found")

        current_status = current.data["status"]

        # Validate transition is allowed per state machine
        try:
            current_state = SubmissionStatus(current_status)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid current status: {current_status}")

        if SubmissionStatus.DRAFT not in VALID_TRANSITIONS.get(current_state, []):
            raise HTTPException(
                status_code=400,
                detail=f"Cannot return to draft from {current_status} status. Only rejected or pending_approval submissions can be returned to draft.",
            )

        # Update status and clear finalized_at
        update_data = {"status": "draft", "finalized_at": None}
        result = supabase.table("submissions").update(update_data).eq("id", submission_id).execute()

        # Append audit entry
        _append_audit_entry(
            submission_id,
            "returned_to_draft",
            user,
            changes={"status": {"old": current_status, "new": "draft"}},
        )

        logger.info(f"Returned submission {submission_id} to draft by {user} (was {current_status})")
        return result.data[0]

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to return submission {submission_id} to draft: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to return submission to draft: {str(e)}")


def add_note(submission_id: str, text: str, user: str) -> dict:
    """Add timestamped note to submission.

    Args:
        submission_id: Submission UUID
        text: Note content
        user: User adding the note

    Returns:
        Updated submission row

    Raises:
        HTTPException: 404 if not found, 503 if database not configured
    """
    supabase = _get_db()

    try:
        # Fetch current notes
        result = supabase.table("submissions").select("notes").eq("id", submission_id).single().execute()

        if not result.data:
            raise HTTPException(status_code=404, detail=f"Submission {submission_id} not found")

        current_notes = result.data.get("notes", [])

        # Append new note
        new_note = {
            "id": str(uuid4()),
            "text": text,
            "created_by": user,
            "created_at": datetime.utcnow().isoformat() + "Z",
        }
        current_notes.append(new_note)

        # Write back
        update_result = (
            supabase.table("submissions").update({"notes": current_notes}).eq("id", submission_id).execute()
        )

        # Append audit entry
        _append_audit_entry(submission_id, "note_added", user)

        logger.info(f"Added note to submission {submission_id} by {user}")
        return update_result.data[0]

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to add note to submission {submission_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to add note: {str(e)}")


def create_upsell_submission(parent_id: str, upsell_type: str, user: str) -> dict:
    """Create upsell child submission linked to parent.

    Args:
        parent_id: Parent submission UUID
        upsell_type: Type of upsell (e.g., heating_cables, gutters)
        user: User creating the upsell

    Returns:
        Created child submission row

    Raises:
        HTTPException: 404 if parent not found, 503 if database not configured
    """
    supabase = _get_db()

    try:
        # Fetch parent submission
        parent_result = supabase.table("submissions").select("*").eq("id", parent_id).single().execute()

        if not parent_result.data:
            raise HTTPException(status_code=404, detail=f"Parent submission {parent_id} not found")

        parent = parent_result.data

        # Create child submission (inherits category and client from parent)
        child_data = {
            "parent_submission_id": parent_id,
            "upsell_type": upsell_type,
            "category": parent["category"],
            "client_name": parent.get("client_name"),
            "created_by": user,
            "status": "draft",
            "line_items": [],  # Estimator will fill this later
            "pricing_tiers": [],
            "selected_tier": "Standard",
            "total_materials_cost": 0,
            "total_labor_cost": 0,
            "total_price": 0,
            "notes": [],
            "audit_log": [
                {
                    "action": "created",
                    "user": user,
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "changes": {"upsell_type": upsell_type, "parent_id": parent_id},
                    "reason": None,
                }
            ],
        }

        # Insert child submission
        child_result = supabase.table("submissions").insert(child_data).execute()

        # Append audit entry to parent
        _append_audit_entry(
            parent_id, "upsell_created", user, changes={"child_id": child_result.data[0]["id"]}
        )

        logger.info(f"Created upsell submission {child_result.data[0]['id']} for parent {parent_id}")
        return child_result.data[0]

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create upsell for parent {parent_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create upsell: {str(e)}")


def get_upsell_suggestions(category: str) -> list:
    """Get category-specific upsell suggestions from rules JSON.

    Args:
        category: Job category (e.g., Bardeaux, Elastomere, Metal)

    Returns:
        List of upsell suggestion objects with bilingual names/descriptions

    Raises:
        HTTPException: 500 if rules file not found or invalid
    """
    try:
        # Load upsell rules from JSON config
        rules_path = os.path.join(os.path.dirname(__file__), "..", "models", "upsell_rules.json")

        with open(rules_path, "r", encoding="utf-8") as f:
            rules = json.load(f)

        # Get category-specific rules
        category_rules = rules.get("rules", {}).get(category, [])

        # Get universal rules (apply to all categories)
        universal_rules = rules.get("universal", [])

        # Combine and return
        suggestions = category_rules + universal_rules

        logger.info(
            f"Retrieved {len(suggestions)} upsell suggestions for category {category} "
            f"({len(category_rules)} category + {len(universal_rules)} universal)"
        )

        return suggestions

    except FileNotFoundError:
        logger.error(f"Upsell rules file not found at {rules_path}")
        raise HTTPException(status_code=500, detail="Upsell rules configuration not found")
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in upsell rules file: {e}")
        raise HTTPException(status_code=500, detail="Invalid upsell rules configuration")
    except Exception as e:
        logger.error(f"Failed to load upsell suggestions: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to load upsell suggestions: {str(e)}")
