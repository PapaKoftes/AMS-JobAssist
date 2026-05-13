"""
API routes for Tool 2 Trainer Dashboard

Endpoints for:
- Importing CVData from Tool 1
- Listing and reviewing participants (with pagination)
- Approving/rejecting CVs (with audit logging)
- Exporting CVs in bulk (single PDF/DOCX or zip of all participants)

Security:
- Input validation on all endpoints
- File size limits on imports
- Audit logging on all state-changing operations
"""

import io
import json
import logging
import os
import sys
import tempfile
import zipfile
from pathlib import Path
from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, HTTPException, UploadFile, File, Depends, Query
from fastapi.responses import StreamingResponse, FileResponse
from pydantic import BaseModel, field_validator
from sqlalchemy.orm import Session

from db import get_db
from models import Participant, CVSubmission, TrainerFeedback, ExportLog, CohortMetrics
from config import MAX_UPLOAD_SIZE_BYTES
from services.cv_mapper import normalise as normalise_cv

# ---------------------------------------------------------------------------
# Tool 1 exporter lazy loader.
# We cannot do a top-level import because Tool 2's empty export/ stub shadows
# Tool 1's real export package. Instead, we import lazily inside endpoints
# after forcibly inserting Tool 1's backend path and flushing cached stubs.
# ---------------------------------------------------------------------------
_TOOL1_BACKEND = str(
    Path(__file__).resolve()
    .parent.parent.parent.parent.parent  # up to AMS-JobAssist/
    / "tool-1-cv-maker" / "src" / "backend"
)


def _get_tool1_exporters():
    """
    Lazily import PDFExporter, DOCXExporter, CVData from Tool 1.
    Returns (PDFExporter, DOCXExporter, CVData) or raises ImportError.
    """
    # Ensure Tool 1 backend is first on sys.path
    if _TOOL1_BACKEND not in sys.path:
        sys.path.insert(0, _TOOL1_BACKEND)
    else:
        # Move it to front in case Tool 2's path took precedence
        sys.path.remove(_TOOL1_BACKEND)
        sys.path.insert(0, _TOOL1_BACKEND)

    # Flush any cached stub from Tool 2's empty export/ directory
    for _k in list(sys.modules.keys()):
        if _k == "export" or _k.startswith("export."):
            del sys.modules[_k]

    from export.pdf_export import PDFExporter  # noqa: PLC0415
    from export.docx_export import DOCXExporter  # noqa: PLC0415
    from cv.models import CVData  # noqa: PLC0415
    return PDFExporter, DOCXExporter, CVData

logger = logging.getLogger(__name__)
audit_logger = logging.getLogger("audit")

router = APIRouter(prefix="/api", tags=["Trainer Dashboard"])

# =====================================================
# Constants
# =====================================================

VALID_APPROVAL_STATUSES = {"pending", "approved", "rejected", "needs_changes"}
VALID_EXPORT_FORMATS = {"pdf", "docx", "json"}

# JSON-bomb defence: bound depth and total key count on imported CV JSON.
# A legitimate Tool 1 CV has depth ~6 and ~150 keys; bomb payloads explode
# either depth or breadth.
_JSON_MAX_DEPTH = 20
_JSON_MAX_KEYS  = 2000


def _validate_json_payload(obj, *, _depth: int = 0, _counter: list | None = None) -> None:
    """Raise ValueError if the JSON tree exceeds depth or total-key budgets."""
    if _counter is None:
        _counter = [0]
    if _depth > _JSON_MAX_DEPTH:
        raise ValueError(f"JSON nested deeper than {_JSON_MAX_DEPTH} levels — refusing to parse")
    if isinstance(obj, dict):
        _counter[0] += len(obj)
        if _counter[0] > _JSON_MAX_KEYS:
            raise ValueError(f"JSON has more than {_JSON_MAX_KEYS} keys — refusing to parse")
        for v in obj.values():
            _validate_json_payload(v, _depth=_depth + 1, _counter=_counter)
    elif isinstance(obj, list):
        _counter[0] += len(obj)
        if _counter[0] > _JSON_MAX_KEYS:
            raise ValueError(f"JSON has more than {_JSON_MAX_KEYS} elements — refusing to parse")
        for item in obj:
            _validate_json_payload(item, _depth=_depth + 1, _counter=_counter)
MAX_BULK_EXPORT = 500
DEFAULT_PAGE_SIZE = 50
MAX_PAGE_SIZE = 200


# =====================================================
# Request/Response Models (with validation)
# =====================================================

class ImportRequest(BaseModel):
    """Request body for importing CV data"""
    cohort_id: str
    force_overwrite: bool = False


class CVSubmissionResponse(BaseModel):
    """Response model for CV data"""
    submission_id: int
    participant_id: int
    user_id: str
    overall_quality: float
    approval_status: str
    version: int
    created_at: str
    cv_data: dict  # Full CVData JSON


class ParticipantResponse(BaseModel):
    """Response model for participant"""
    participant_id: int
    user_id: str
    name: Optional[str] = None
    email: Optional[str] = None
    cohort_id: Optional[str] = None
    status: str
    interview_path: Optional[str] = None
    first_imported_at: str
    last_updated_at: str
    completed_at: Optional[str] = None
    latest_submission: Optional[CVSubmissionResponse] = None


class ApprovalRequest(BaseModel):
    """Request to approve/reject a submission"""
    approval_status: str  # approved, rejected, needs_changes
    feedback: Optional[str] = None
    approved_by: str

    @field_validator("approval_status")
    @classmethod
    def valid_status(cls, v: str) -> str:
        if v not in VALID_APPROVAL_STATUSES:
            raise ValueError(f"approval_status must be one of: {', '.join(sorted(VALID_APPROVAL_STATUSES))}")
        return v

    @field_validator("approved_by")
    @classmethod
    def approved_by_not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v or len(v) > 255:
            raise ValueError("approved_by must be 1-255 characters")
        return v

    @field_validator("feedback")
    @classmethod
    def feedback_length(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and len(v) > 5000:
            raise ValueError("feedback exceeds 5000 character limit")
        return v


class CVSectionEditRequest(BaseModel):
    """Request to persist a trainer's inline edit to one CV section."""
    question_id: str
    edited_text: str
    language: str = "de"

    @field_validator("question_id")
    @classmethod
    def qid_not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v or len(v) > 100:
            raise ValueError("question_id must be 1-100 characters")
        return v

    @field_validator("edited_text")
    @classmethod
    def text_length(cls, v: str) -> str:
        if len(v) > 10_000:
            raise ValueError("edited_text exceeds 10 000 character limit")
        return v


class BulkApprovalRequest(BaseModel):
    """Request to bulk approve/reject participants"""
    participant_ids: List[int]
    approval_status: str
    feedback: Optional[str] = None
    approved_by: str

    @field_validator("approval_status")
    @classmethod
    def valid_status(cls, v: str) -> str:
        if v not in VALID_APPROVAL_STATUSES:
            raise ValueError(f"approval_status must be one of: {', '.join(sorted(VALID_APPROVAL_STATUSES))}")
        return v

    @field_validator("participant_ids")
    @classmethod
    def ids_not_empty(cls, v: List[int]) -> List[int]:
        if not v:
            raise ValueError("participant_ids must not be empty")
        if len(v) > MAX_BULK_EXPORT:
            raise ValueError(f"Too many participants (max {MAX_BULK_EXPORT})")
        return v


class BulkExportRequest(BaseModel):
    """Request to export multiple CVs"""
    participant_ids: List[int]
    format: str = "pdf"  # pdf, docx, json
    language: str = "de"
    include_feedback: bool = False

    @field_validator("format")
    @classmethod
    def valid_format(cls, v: str) -> str:
        if v not in VALID_EXPORT_FORMATS:
            raise ValueError(f"format must be one of: {', '.join(sorted(VALID_EXPORT_FORMATS))}")
        return v

    @field_validator("participant_ids")
    @classmethod
    def ids_not_empty(cls, v: List[int]) -> List[int]:
        if not v:
            raise ValueError("participant_ids must not be empty")
        if len(v) > MAX_BULK_EXPORT:
            raise ValueError(f"Too many participants (max {MAX_BULK_EXPORT})")
        return v


class PaginatedResponse(BaseModel):
    """Wrapper for paginated results"""
    items: list
    total: int
    page: int
    page_size: int
    total_pages: int


# =====================================================
# Endpoints
# =====================================================

@router.post("/import-cvs", tags=["Import"])
async def import_cvs(
    cohort_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Import CVData JSON from Tool 1.

    Supports:
    - Single JSON file (one CV)
    - ZIP file with multiple JSONs

    File size limited to MAX_UPLOAD_SIZE_MB.
    """
    try:
        logger.info(f"Importing CV data from {file.filename}")

        # Validate file extension
        if not file.filename:
            raise HTTPException(status_code=400, detail="Missing filename")

        if not (file.filename.endswith(".json") or file.filename.endswith(".zip")):
            raise HTTPException(status_code=400, detail="File must be .json or .zip")

        # Read file with size check
        contents = await file.read()
        if len(contents) > MAX_UPLOAD_SIZE_BYTES:
            raise HTTPException(
                status_code=413,
                detail=f"File too large ({len(contents) // (1024*1024)} MB). Max: {MAX_UPLOAD_SIZE_BYTES // (1024*1024)} MB"
            )

        if file.filename.endswith(".json"):
            # Single JSON file — guard against JSON bombs (depth + key count)
            try:
                cv_dict = json.loads(contents)
            except json.JSONDecodeError as e:
                raise HTTPException(status_code=400, detail=f"Invalid JSON: {e}")
            _validate_json_payload(cv_dict)

            participant_id = _import_single_cv(db, cohort_id, cv_dict)
            audit_logger.info(f"IMPORT single CV: cohort={cohort_id} user={cv_dict.get('user_id', 'unknown')}")

            return {
                "status": "success",
                "imported": 1,
                "participant_id": participant_id,
                "message": f"Imported 1 CV for cohort {cohort_id}"
            }

        elif file.filename.endswith(".zip"):
            count = 0
            errors = []

            try:
                with zipfile.ZipFile(io.BytesIO(contents)) as zf:
                    # Safety: limit number of entries
                    entries = [f for f in zf.namelist() if f.endswith(".json")]
                    if len(entries) > 1000:
                        raise HTTPException(status_code=400, detail="ZIP contains too many files (max 1000)")

                    for filename in entries:
                        try:
                            json_content = zf.read(filename)
                            cv_dict = json.loads(json_content)
                            _validate_json_payload(cv_dict)
                            _import_single_cv(db, cohort_id, cv_dict)
                            count += 1
                        except (json.JSONDecodeError, KeyError, ValueError) as e:
                            errors.append(f"{filename}: {e}")
                            logger.warning(f"Skipped invalid file {filename}: {e}")
            except zipfile.BadZipFile:
                raise HTTPException(status_code=400, detail="Invalid ZIP file")

            audit_logger.info(f"IMPORT batch: cohort={cohort_id} imported={count} errors={len(errors)}")

            result = {
                "status": "success",
                "imported": count,
                "message": f"Imported {count} CVs for cohort {cohort_id}"
            }
            if errors:
                result["errors"] = errors[:10]  # Return first 10 errors
                result["error_count"] = len(errors)
            return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Import error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Import failed: {str(e)}")


@router.get("/participants")
async def list_participants(
    cohort_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    search: Optional[str] = Query(None, max_length=200),
    min_quality: Optional[float] = Query(None, ge=0.0, le=1.0,
        description="Filter to participants whose latest CV quality >= this value"),
    max_quality: Optional[float] = Query(None, ge=0.0, le=1.0,
        description="Filter to participants whose latest CV quality <= this value"),
    page: int = Query(1, ge=1),
    page_size: int = Query(DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE),
    db: Session = Depends(get_db)
):
    """
    List participants with optional filtering and pagination.

    Query params:
    - cohort_id: Filter by cohort
    - status: Filter by approval status (pending/approved/rejected)
    - search: Search by name or email
    - min_quality: Only show participants with CV quality >= value (0.0–1.0)
    - max_quality: Only show participants with CV quality <= value (0.0–1.0)
    - page: Page number (default 1)
    - page_size: Items per page (default 50, max 200)
    """
    query = db.query(Participant)

    if cohort_id:
        query = query.filter(Participant.cohort_id == cohort_id)

    if status:
        if status not in VALID_APPROVAL_STATUSES:
            raise HTTPException(status_code=400, detail=f"Invalid status: {status}")
        query = query.filter(Participant.status == status)

    # Quality filter: join on latest submission quality
    if min_quality is not None or max_quality is not None:
        # Sub-query: latest submission per participant
        from sqlalchemy import func as _func
        latest_sub = (
            db.query(
                CVSubmission.participant_id,
                _func.max(CVSubmission.version).label("max_version"),
            )
            .group_by(CVSubmission.participant_id)
            .subquery()
        )
        quality_sub = (
            db.query(CVSubmission)
            .join(
                latest_sub,
                (CVSubmission.participant_id == latest_sub.c.participant_id)
                & (CVSubmission.version == latest_sub.c.max_version),
            )
            .subquery()
        )
        query = query.join(
            quality_sub, Participant.id == quality_sub.c.participant_id
        )
        if min_quality is not None:
            query = query.filter(quality_sub.c.overall_quality >= min_quality)
        if max_quality is not None:
            query = query.filter(quality_sub.c.overall_quality <= max_quality)

    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (Participant.name.ilike(search_pattern)) |
            (Participant.email.ilike(search_pattern))
        )

    # Get total count before pagination
    total = query.count()
    total_pages = max(1, (total + page_size - 1) // page_size)

    # Apply pagination
    participants = (
        query
        .order_by(Participant.last_updated_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    # For each participant, get their latest CV submission
    results = []
    for p in participants:
        latest_submission = (
            db.query(CVSubmission)
            .filter(CVSubmission.participant_id == p.id)
            .order_by(CVSubmission.version.desc())
            .first()
        )

        submission_data = None
        if latest_submission:
            submission_data = CVSubmissionResponse(
                submission_id=latest_submission.id,
                participant_id=latest_submission.participant_id,
                user_id=latest_submission.user_id,
                overall_quality=latest_submission.overall_quality or 0.0,
                approval_status=latest_submission.approval_status or "pending",
                version=latest_submission.version or 1,
                created_at=latest_submission.created_at.isoformat() if latest_submission.created_at else "",
                cv_data=latest_submission.cv_data_json or {}
            )

        results.append(ParticipantResponse(
            participant_id=p.id,
            user_id=p.user_id,
            name=p.name,
            email=p.email,
            cohort_id=p.cohort_id,
            status=p.status or "pending",
            interview_path=p.interview_path,
            first_imported_at=p.first_imported_at.isoformat() if p.first_imported_at else "",
            last_updated_at=p.last_updated_at.isoformat() if p.last_updated_at else "",
            completed_at=p.completed_at.isoformat() if p.completed_at else None,
            latest_submission=submission_data
        ))

    return {
        "items": [r.model_dump() for r in results],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }


@router.get("/participants/{participant_id}")
async def get_participant(
    participant_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific participant with their CV."""
    participant = db.query(Participant).filter(Participant.id == participant_id).first()
    if not participant:
        raise HTTPException(status_code=404, detail="Participant not found")

    latest_submission = (
        db.query(CVSubmission)
        .filter(CVSubmission.participant_id == participant_id)
        .order_by(CVSubmission.version.desc())
        .first()
    )

    submission_data = None
    if latest_submission:
        submission_data = CVSubmissionResponse(
            submission_id=latest_submission.id,
            participant_id=latest_submission.participant_id,
            user_id=latest_submission.user_id,
            overall_quality=latest_submission.overall_quality or 0.0,
            approval_status=latest_submission.approval_status or "pending",
            version=latest_submission.version or 1,
            created_at=latest_submission.created_at.isoformat() if latest_submission.created_at else "",
            cv_data=latest_submission.cv_data_json or {}
        )

    return ParticipantResponse(
        participant_id=participant.id,
        user_id=participant.user_id,
        name=participant.name,
        email=participant.email,
        cohort_id=participant.cohort_id,
        status=participant.status or "pending",
        interview_path=participant.interview_path,
        first_imported_at=participant.first_imported_at.isoformat() if participant.first_imported_at else "",
        last_updated_at=participant.last_updated_at.isoformat() if participant.last_updated_at else "",
        completed_at=participant.completed_at.isoformat() if participant.completed_at else None,
        latest_submission=submission_data
    )


@router.post("/participants/{participant_id}/approve")
async def approve_submission(
    participant_id: int,
    request: ApprovalRequest,
    db: Session = Depends(get_db)
):
    """
    Approve or reject a participant's CV submission.

    All approval actions are logged to the audit trail.
    """
    participant = db.query(Participant).filter(Participant.id == participant_id).first()
    if not participant:
        raise HTTPException(status_code=404, detail="Participant not found")

    # Get latest submission
    submission = (
        db.query(CVSubmission)
        .filter(CVSubmission.participant_id == participant_id)
        .order_by(CVSubmission.version.desc())
        .first()
    )

    if not submission:
        raise HTTPException(status_code=404, detail="No CV submission found")

    old_status = submission.approval_status

    # Update submission status
    submission.approval_status = request.approval_status
    submission.approval_timestamp = datetime.now()
    submission.approved_by = request.approved_by

    # Update participant status
    participant.status = request.approval_status
    participant.trainer_notes = request.feedback or ""
    participant.last_updated_at = datetime.now()

    if request.approval_status == "approved":
        participant.completed_at = datetime.now()

    try:
        db.add(submission)
        db.add(participant)

        # Create feedback record for audit trail
        feedback_record = TrainerFeedback(
            submission_id=submission.id,
            participant_id=participant_id,
            category="approval",
            feedback_text=f"Status changed: {old_status} → {request.approval_status}",
            suggestion=request.feedback,
        )
        db.add(feedback_record)

        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Approval commit failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to save approval")

    # Audit log
    audit_logger.info(
        f"APPROVAL: participant={participant_id} user={participant.user_id} "
        f"old_status={old_status} new_status={request.approval_status} "
        f"by={request.approved_by} feedback={request.feedback or '(none)'}"
    )

    return {
        "status": "success",
        "approval_status": submission.approval_status,
        "message": f"Submission {request.approval_status}"
    }


@router.patch("/participants/{participant_id}/cv-section")
async def update_cv_section(
    participant_id: int,
    request: CVSectionEditRequest,
    db: Session = Depends(get_db),
):
    """
    Persist a trainer's inline edit to one CV section.

    Finds the section by question_id inside cv_data_json and overwrites
    the text for the requested language.  Records the change in the
    TrainerFeedback audit trail.
    """
    participant = db.query(Participant).filter(Participant.id == participant_id).first()
    if not participant:
        raise HTTPException(status_code=404, detail="Participant not found")

    submission = (
        db.query(CVSubmission)
        .filter(CVSubmission.participant_id == participant_id)
        .order_by(CVSubmission.version.desc())
        .first()
    )
    if not submission:
        raise HTTPException(status_code=404, detail="No CV submission found")

    # Work on a mutable copy of the JSON blob
    cv_json = dict(submission.cv_data_json or {})
    CATEGORIES = ("background", "experience", "skills", "motivation", "training", "projects")
    updated = False

    # Check per-category lists (standard CVData shape)
    for cat in CATEGORIES:
        for sec in cv_json.get(cat, []):
            if sec.get("question_id") == request.question_id:
                sec[request.language] = request.edited_text
                sec["trainer_edited"] = True
                updated = True
                break
        if updated:
            break

    # Fallback: canonical top-level "sections" array
    if not updated:
        for sec in cv_json.get("sections", []):
            if sec.get("question_id") == request.question_id:
                sec[request.language] = request.edited_text
                sec["trainer_edited"] = True
                updated = True
                break

    if not updated:
        raise HTTPException(
            status_code=404,
            detail=f"Section '{request.question_id}' not found in CV data",
        )

    submission.cv_data_json = cv_json
    submission.updated_at = datetime.now()

    try:
        db.add(TrainerFeedback(
            submission_id=submission.id,
            participant_id=participant_id,
            category="inline_edit",
            feedback_text=f"Edited section: {request.question_id} [{request.language}]",
            suggestion=request.edited_text,
        ))
        db.add(submission)
        db.commit()
    except Exception as exc:
        db.rollback()
        logger.error(f"CV section update failed: {exc}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to save edit")

    audit_logger.info(
        f"INLINE_EDIT: participant={participant_id} section={request.question_id} "
        f"language={request.language}"
    )

    return {"status": "success", "message": "Section updated"}


@router.post("/participants/bulk-approve")
async def bulk_approve(
    request: BulkApprovalRequest,
    db: Session = Depends(get_db)
):
    """
    Bulk approve/reject multiple participants.

    All actions are logged individually to the audit trail.
    """
    success_count = 0
    errors = []

    for pid in request.participant_ids:
        participant = db.query(Participant).filter(Participant.id == pid).first()
        if not participant:
            errors.append(f"Participant {pid} not found")
            continue

        submission = (
            db.query(CVSubmission)
            .filter(CVSubmission.participant_id == pid)
            .order_by(CVSubmission.version.desc())
            .first()
        )
        if not submission:
            errors.append(f"No submission for participant {pid}")
            continue

        old_status = submission.approval_status
        submission.approval_status = request.approval_status
        submission.approval_timestamp = datetime.now()
        submission.approved_by = request.approved_by
        participant.status = request.approval_status
        participant.trainer_notes = request.feedback or ""
        participant.last_updated_at = datetime.now()

        if request.approval_status == "approved":
            participant.completed_at = datetime.now()

        # Audit trail record
        feedback_record = TrainerFeedback(
            submission_id=submission.id,
            participant_id=pid,
            category="bulk_approval",
            feedback_text=f"Bulk: {old_status} → {request.approval_status}",
            suggestion=request.feedback,
        )
        db.add(feedback_record)
        success_count += 1

        audit_logger.info(
            f"BULK_APPROVAL: participant={pid} {old_status} → {request.approval_status} by={request.approved_by}"
        )

    try:
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Bulk approval commit failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to save bulk approval")

    return {
        "status": "success",
        "approved": success_count,
        "errors": errors,
        "message": f"Processed {success_count} participants"
    }



@router.get("/participants/{participant_id}/status")
async def get_participant_cv_status(
    participant_id: int,
    db: Session = Depends(get_db)
):
    """
    Return the approval and lock status for a participant's CV.

    Response shape::

        {"approved": false, "locked": false, "approved_at": null, "approved_by": null}
    """
    participant = db.query(Participant).filter(Participant.id == participant_id).first()
    if not participant:
        raise HTTPException(status_code=404, detail="Participant not found")

    submission = (
        db.query(CVSubmission)
        .filter(CVSubmission.participant_id == participant_id)
        .order_by(CVSubmission.version.desc())
        .first()
    )

    approved = (submission.approval_status == "approved") if submission else False
    locked = bool(submission.cv_locked) if submission else False
    approved_at = (
        submission.approval_timestamp.isoformat()
        if submission and getattr(submission, "approval_timestamp", None)
        else None
    )
    approved_by = getattr(submission, "approved_by", None) if submission else None

    return {
        "participant_id": participant_id,
        "approved": approved,
        "locked": locked,
        "approved_at": approved_at,
        "approved_by": approved_by,
    }


class LockRequest(BaseModel):
    """Request body for lock / unlock operations."""

    locked_by: str

    @field_validator("locked_by")
    @classmethod
    def locked_by_not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v or len(v) > 255:
            raise ValueError("locked_by must be 1-255 characters")
        return v


@router.post("/participants/{participant_id}/lock")
async def lock_participant_cv(
    participant_id: int,
    request: LockRequest,
    db: Session = Depends(get_db)
):
    """
    Lock a participant's CV — prevents any further edits by the participant.

    Once locked, the interview engine rejects new answers for the linked session.
    Trainers can still edit inline via the dashboard.
    """
    participant = db.query(Participant).filter(Participant.id == participant_id).first()
    if not participant:
        raise HTTPException(status_code=404, detail="Participant not found")

    submission = (
        db.query(CVSubmission)
        .filter(CVSubmission.participant_id == participant_id)
        .order_by(CVSubmission.version.desc())
        .first()
    )
    if not submission:
        raise HTTPException(status_code=404, detail="No CV submission found")

    try:
        submission.cv_locked = True
        submission.approval_timestamp = datetime.now()
        submission.approved_by = request.locked_by
        participant.last_updated_at = datetime.now()

        feedback_record = TrainerFeedback(
            submission_id=submission.id,
            participant_id=participant_id,
            category="lock",
            feedback_text=f"CV locked by {request.locked_by}",
        )
        db.add(feedback_record)
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Lock commit failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to lock CV")

    audit_logger.info(
        f"LOCK: participant={participant_id} user={participant.user_id} by={request.locked_by}"
    )
    return {"status": "success", "locked": True, "participant_id": participant_id}


@router.post("/participants/{participant_id}/unlock")
async def unlock_participant_cv(
    participant_id: int,
    request: LockRequest,
    db: Session = Depends(get_db)
):
    """
    Unlock a previously locked CV so the participant can continue editing.
    """
    participant = db.query(Participant).filter(Participant.id == participant_id).first()
    if not participant:
        raise HTTPException(status_code=404, detail="Participant not found")

    submission = (
        db.query(CVSubmission)
        .filter(CVSubmission.participant_id == participant_id)
        .order_by(CVSubmission.version.desc())
        .first()
    )
    if not submission:
        raise HTTPException(status_code=404, detail="No CV submission found")

    try:
        submission.cv_locked = False
        participant.last_updated_at = datetime.now()

        feedback_record = TrainerFeedback(
            submission_id=submission.id,
            participant_id=participant_id,
            category="unlock",
            feedback_text=f"CV unlocked by {request.locked_by}",
        )
        db.add(feedback_record)
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Unlock commit failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to unlock CV")

    audit_logger.info(
        f"UNLOCK: participant={participant_id} user={participant.user_id} by={request.locked_by}"
    )
    return {"status": "success", "locked": False, "participant_id": participant_id}


@router.get("/cohorts/{cohort_id}/metrics")
async def get_cohort_metrics(
    cohort_id: str,
    db: Session = Depends(get_db)
):
    """Get summary metrics for a cohort."""
    participants = db.query(Participant).filter(Participant.cohort_id == cohort_id).all()

    total = len(participants)
    completed = sum(1 for p in participants if p.status == "approved")
    pending = sum(1 for p in participants if p.status in ("pending", "needs_changes"))
    rejected = sum(1 for p in participants if p.status == "rejected")

    # Get quality scores via join
    submissions = (
        db.query(CVSubmission.overall_quality)
        .join(Participant, CVSubmission.participant_id == Participant.id)
        .filter(Participant.cohort_id == cohort_id)
        .all()
    )

    if submissions:
        scores = [s[0] for s in submissions if s[0] is not None]
        avg_quality = sum(scores) / len(scores) if scores else 0
        min_quality = min(scores) if scores else 0
        max_quality = max(scores) if scores else 0
    else:
        avg_quality = min_quality = max_quality = 0

    return {
        "cohort_id": cohort_id,
        "total_participants": total,
        "completed": completed,
        "pending": pending,
        "rejected": rejected,
        "completion_rate": f"{(completed/total*100):.1f}%" if total > 0 else "0%",
        "avg_quality": f"{avg_quality:.2f}",
        "min_quality": f"{min_quality:.2f}",
        "max_quality": f"{max_quality:.2f}"
    }


@router.post("/bulk-export")
async def bulk_export(
    request: BulkExportRequest,
    db: Session = Depends(get_db)
):
    """
    Export multiple CVs in the requested format.

    - format=json  → single JSON bundle (always available)
    - format=pdf   → zip archive of individual PDFs (requires Tool 1)
    - format=docx  → zip archive of individual DOCX files (requires Tool 1)

    Returns a downloadable file (JSON, or a .zip for pdf/docx).
    """
    logger.info(
        f"Bulk export: {len(request.participant_ids)} participants, "
        f"format={request.format}, lang={request.language}"
    )
    audit_logger.info(
        f"EXPORT: {len(request.participant_ids)} participants "
        f"format={request.format} lang={request.language}"
    )

    if not request.participant_ids:
        raise HTTPException(status_code=400, detail="No participant IDs provided")

    # For binary formats we need the Tool 1 exporters — load lazily
    _PDFExporter = _DOCXExporter = _CVData = None
    if request.format in ("pdf", "docx"):
        try:
            _PDFExporter, _DOCXExporter, _CVData = _get_tool1_exporters()
        except ImportError as _e:
            raise HTTPException(
                status_code=501,
                detail=f"PDF/DOCX export requires Tool 1 backend. Error: {_e}",
            )

    try:
        participants = (
            db.query(Participant)
            .filter(Participant.id.in_(request.participant_ids))
            .all()
        )
        if not participants:
            raise HTTPException(status_code=404, detail="No participants found for given IDs")

        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")

        # ----------------------------------------------------------------
        # JSON export — single bundle file (no Tool 1 dependency)
        # ----------------------------------------------------------------
        if request.format == "json":
            export_records = []
            for p in participants:
                latest_sub = (
                    db.query(CVSubmission)
                    .filter(CVSubmission.participant_id == p.id)
                    .order_by(CVSubmission.version.desc())
                    .first()
                )
                export_records.append({
                    "participant_id": p.id,
                    "user_id": p.user_id,
                    "name": p.name,
                    "email": p.email,
                    "cohort_id": p.cohort_id,
                    "interview_path": p.interview_path,
                    "status": p.status,
                    "overall_quality": latest_sub.overall_quality if latest_sub else None,
                    "cv_data": latest_sub.cv_data_json if latest_sub else None,
                    "exported_at": datetime.utcnow().isoformat(),
                    "language": request.language,
                })

            bundle = {
                "export_timestamp": timestamp,
                "format": "json",
                "language": request.language,
                "participant_count": len(export_records),
                "participants": export_records,
            }
            json_bytes = json.dumps(bundle, ensure_ascii=False, indent=2).encode("utf-8")
            return StreamingResponse(
                io.BytesIO(json_bytes),
                media_type="application/json",
                headers={
                    "Content-Disposition": f'attachment; filename="ams_export_{timestamp}.json"'
                },
            )

        # ----------------------------------------------------------------
        # PDF / DOCX export — generate files via Tool 1, zip them up
        # ----------------------------------------------------------------
        ext  = request.format  # "pdf" or "docx"
        mime = "application/pdf" if ext == "pdf" else (
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

        zip_buffer = io.BytesIO()
        errors: list = []

        with zipfile.ZipFile(zip_buffer, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
            for p in participants:
                latest_sub = (
                    db.query(CVSubmission)
                    .filter(CVSubmission.participant_id == p.id)
                    .order_by(CVSubmission.version.desc())
                    .first()
                )
                if not latest_sub or not latest_sub.cv_data_json:
                    errors.append(f"Participant {p.id} ({p.user_id}): no CV data")
                    continue

                try:
                    cv_data = _CVData.from_dict(latest_sub.cv_data_json)
                except Exception as exc:
                    errors.append(f"Participant {p.id}: CVData parse error — {exc}")
                    continue

                # Export to a temporary file, then read into the zip
                safe_name = (p.name or p.user_id or str(p.id)).replace(" ", "_")
                out_filename = f"{safe_name}_{request.language}_{timestamp}.{ext}"

                try:
                    with tempfile.TemporaryDirectory() as tmpdir:
                        # Instantiate inside the temp dir so output_dir is always valid
                        exporter = _PDFExporter(output_dir=tmpdir) if ext == "pdf" else _DOCXExporter(output_dir=tmpdir)
                        out_path = exporter.export(
                            cv_data,
                            language=request.language,
                            filename=f"{safe_name}_{request.language}_{timestamp}",
                        )
                        if out_path and Path(out_path).exists():
                            zf.write(out_path, arcname=out_filename)
                            # Audit: record this export
                            try:
                                db.add(ExportLog(
                                    participant_id=p.id,
                                    submission_id=latest_sub.id if latest_sub else None,
                                    export_format=ext,
                                    export_language=request.language,
                                    file_path=out_filename,
                                    file_size=os.path.getsize(out_path),
                                ))
                            except Exception:
                                pass  # non-fatal — log already written via audit_logger
                        else:
                            errors.append(f"Participant {p.id}: export produced no file")
                except Exception as exc:
                    errors.append(f"Participant {p.id}: export error — {exc}")
                    logger.warning(f"Export failed for participant {p.id}: {exc}", exc_info=True)

        try:
            db.commit()
        except Exception:
            db.rollback()

        if errors:
            logger.warning(f"Bulk export completed with {len(errors)} errors: {errors}")

        zip_buffer.seek(0)
        zip_filename = f"ams_cv_export_{timestamp}.zip"
        return StreamingResponse(
            zip_buffer,
            media_type="application/zip",
            headers={
                "Content-Disposition": f'attachment; filename="{zip_filename}"',
                "X-Export-Errors": str(len(errors)),
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Bulk export error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")


@router.get("/export-all")
async def export_all_participants(
    format: str = Query("pdf", description="Export format: pdf, docx, or json"),
    language: str = Query("de", description="Output language: de or en"),
    cohort_id: Optional[str] = Query(None, description="Optionally filter by cohort"),
    db: Session = Depends(get_db),
):
    """
    Export ALL participants' CVs as a single zip archive (PDF or DOCX),
    or as a JSON bundle.

    - format=pdf   → zip of individual PDFs
    - format=docx  → zip of individual DOCX files
    - format=json  → single JSON bundle

    Optionally filter by cohort_id.
    """
    if format not in VALID_EXPORT_FORMATS:
        raise HTTPException(
            status_code=400,
            detail=f"format must be one of: {', '.join(sorted(VALID_EXPORT_FORMATS))}",
        )

    _PDFExporter2 = _DOCXExporter2 = _CVData2 = None
    if format in ("pdf", "docx"):
        try:
            _PDFExporter2, _DOCXExporter2, _CVData2 = _get_tool1_exporters()
        except ImportError as _e:
            raise HTTPException(
                status_code=501,
                detail=f"PDF/DOCX export requires Tool 1 backend. Error: {_e}",
            )

    query = db.query(Participant)
    if cohort_id:
        query = query.filter(Participant.cohort_id == cohort_id)
    participants = query.order_by(Participant.last_updated_at.desc()).all()

    if not participants:
        raise HTTPException(status_code=404, detail="No participants found")

    audit_logger.info(
        f"EXPORT_ALL: {len(participants)} participants "
        f"format={format} lang={language} cohort={cohort_id or 'all'}"
    )

    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")

    # ----------------------------------------------------------------
    # JSON bundle
    # ----------------------------------------------------------------
    if format == "json":
        records = []
        for p in participants:
            latest_sub = (
                db.query(CVSubmission)
                .filter(CVSubmission.participant_id == p.id)
                .order_by(CVSubmission.version.desc())
                .first()
            )
            records.append({
                "participant_id": p.id,
                "user_id": p.user_id,
                "name": p.name,
                "email": p.email,
                "cohort_id": p.cohort_id,
                "interview_path": p.interview_path,
                "status": p.status,
                "overall_quality": latest_sub.overall_quality if latest_sub else None,
                "cv_data": latest_sub.cv_data_json if latest_sub else None,
                "exported_at": datetime.utcnow().isoformat(),
                "language": language,
            })
        bundle = {
            "export_timestamp": timestamp,
            "format": "json",
            "language": language,
            "participant_count": len(records),
            "participants": records,
        }
        json_bytes = json.dumps(bundle, ensure_ascii=False, indent=2).encode("utf-8")
        return StreamingResponse(
            io.BytesIO(json_bytes),
            media_type="application/json",
            headers={
                "Content-Disposition": f'attachment; filename="ams_all_export_{timestamp}.json"'
            },
        )

    # ----------------------------------------------------------------
    # PDF / DOCX zip
    # ----------------------------------------------------------------
    exporter = _PDFExporter2() if format == "pdf" else _DOCXExporter2()
    ext = format

    zip_buffer = io.BytesIO()
    errors: list = []

    with zipfile.ZipFile(zip_buffer, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        for p in participants:
            latest_sub = (
                db.query(CVSubmission)
                .filter(CVSubmission.participant_id == p.id)
                .order_by(CVSubmission.version.desc())
                .first()
            )
            if not latest_sub or not latest_sub.cv_data_json:
                errors.append(f"Participant {p.id} ({p.user_id}): no CV data")
                continue

            try:
                cv_data = _CVData2.from_dict(latest_sub.cv_data_json)
            except Exception as exc:
                errors.append(f"Participant {p.id}: CVData parse error — {exc}")
                continue

            safe_name = (p.name or p.user_id or str(p.id)).replace(" ", "_")
            out_filename = f"{safe_name}_{language}_{timestamp}.{ext}"

            try:
                with tempfile.TemporaryDirectory() as tmpdir:
                    exporter.output_dir = Path(tmpdir)
                    out_path = exporter.export(
                        cv_data,
                        language=language,
                        filename=f"{safe_name}_{language}_{timestamp}",
                    )
                    if out_path and Path(out_path).exists():
                        zf.write(out_path, arcname=out_filename)
                        try:
                            db.add(ExportLog(
                                participant_id=p.id,
                                submission_id=latest_sub.id if latest_sub else None,
                                export_format=ext,
                                export_language=language,
                                file_path=out_filename,
                                file_size=os.path.getsize(out_path),
                            ))
                        except Exception:
                            pass
                    else:
                        errors.append(f"Participant {p.id}: export produced no file")
            except Exception as exc:
                errors.append(f"Participant {p.id}: export error — {exc}")
                logger.warning(f"Export failed for participant {p.id}: {exc}", exc_info=True)

    try:
        db.commit()
    except Exception:
        db.rollback()

    if errors:
        logger.warning(f"Export-all completed with {len(errors)} errors: {errors}")

    zip_buffer.seek(0)
    cohort_part = f"_{cohort_id}" if cohort_id else ""
    zip_filename = f"ams_all_cvs{cohort_part}_{timestamp}.zip"

    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={
            "Content-Disposition": f'attachment; filename="{zip_filename}"',
            "X-Export-Errors": str(len(errors)),
            "X-Export-Count": str(len(participants) - len(errors)),
        },
    )


# =====================================================
# Helper Functions
# =====================================================

def _import_single_cv(db: Session, cohort_id: str, cv_dict: dict) -> int:
    """
    Import a single CV from Tool 1.

    Accepts all Tool 1 export shapes (nested or flat) via cv_mapper.normalise().
    Returns: participant_id
    """
    try:
        cv_dict = normalise_cv(cv_dict)
    except ValueError as exc:
        raise ValueError(f"Cannot import CV: {exc}") from exc

    user_id = cv_dict.get("user_id")
    if not user_id or not isinstance(user_id, str):
        raise ValueError("CV data must contain a non-empty 'user_id' string")

    user_id = user_id.strip()
    if len(user_id) > 255:
        raise ValueError("user_id exceeds 255 character limit")

    # Check if participant exists
    participant = db.query(Participant).filter(Participant.user_id == user_id).first()

    if not participant:
        # Create new participant
        participant = Participant(
            user_id=user_id,
            cohort_id=cohort_id,
            name=cv_dict.get("name") or user_id,
            email=cv_dict.get("email"),
            interview_path=cv_dict.get("interview_path", "unknown"),
            status="pending"
        )
        db.add(participant)
        db.flush()  # Get the ID

    # Create/update CV submission
    latest_version = (
        db.query(CVSubmission)
        .filter(CVSubmission.participant_id == participant.id)
        .count()
    ) + 1

    quality = cv_dict.get("overall_quality", 0.0)
    if not isinstance(quality, (int, float)):
        quality = 0.0
    quality = max(0.0, min(1.0, float(quality)))

    submission = CVSubmission(
        participant_id=participant.id,
        user_id=user_id,
        cv_data_json=cv_dict,
        overall_quality=quality,
        ready_for_export=bool(cv_dict.get("ready_for_export", False)),
        version=latest_version,
        language_primary=cv_dict.get("language_output_primary", "de"),
        language_secondary=cv_dict.get("language_output_secondary", "en")
    )
    db.add(submission)
    db.commit()

    logger.info(f"Imported CV for user {user_id} (participant {participant.id}, v{latest_version})")
    return participant.id


# =====================================================
# Admin: SQLite backup
# =====================================================

@router.get("/admin/backup", tags=["Admin"])
async def admin_backup():
    """
    Stream the trainer SQLite database as a downloadable file.

    Intended for AMS IT to run a periodic backup. Returns the live `.db` file
    with a timestamped filename. Caller should have `AMS_TRAINER_API_KEY`
    configured to prevent unauthorised download.
    """
    from config import DATABASE_URL

    db_path = DATABASE_URL.replace("sqlite:///", "")
    if not os.path.exists(db_path):
        raise HTTPException(status_code=404, detail="Database file not found")

    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    filename = f"ams_trainer_backup_{timestamp}.db"
    audit_logger.info(f"BACKUP requested: path={db_path}")
    return FileResponse(
        path=db_path,
        filename=filename,
        media_type="application/octet-stream",
        headers={"X-Backup-Timestamp": timestamp},
    )
