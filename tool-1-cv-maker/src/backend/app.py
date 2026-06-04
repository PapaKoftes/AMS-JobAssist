"""
AMS JobAssist CV Maker - FastAPI Application
Main entry point for Tool 1
"""

import os
import uuid
import logging
import time
from contextlib import asynccontextmanager
from typing import Optional
from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from pathlib import Path
from starlette.middleware.base import BaseHTTPMiddleware

# Offline mode is ON by default — network_block allowlists loopback so the
# server itself keeps working while external network access is blocked.
# To disable (e.g. for development with external API access), set
# AMS_ENFORCE_OFFLINE=0.
if os.environ.get("AMS_ENFORCE_OFFLINE", "1").lower() not in ("0", "false", "no"):
    try:
        from privacy.network_block import enable_offline_mode
        enable_offline_mode()
    except Exception as _e:
        logging.getLogger(__name__).warning(f"Could not enable offline mode: {_e}")

# Then init app
from config import HOST, PORT, FRONTEND_DIR, DEBUG, DB_DIR
from db import DatabaseManager
from cv.storage import CVStorage
from cv.builder import CVBuilder
from export.json_export import JSONExporter
from export.pdf_export import PDFExporter
from export.docx_export import DOCXExporter
from export.europass_export import EuropassExporter
from api.interview import router as interview_router, init_interview_routes

logger = logging.getLogger(__name__)

# Export output directory (alongside the database)
EXPORTS_DIR = DB_DIR / "exports"
EXPORTS_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================================
# Request / Response Models
# ============================================================================

class ExportRequest(BaseModel):
    """Request body for export endpoints."""
    session_id: int
    language: str = "de"
    filename: Optional[str] = None
    force: bool = False   # bypass quality gate (for trainer use)


class ATSScoreRequest(BaseModel):
    """Request body for ATS scoring."""
    session_id: int
    job_description: str = ""


class CoverLetterRequest(BaseModel):
    """Request body for cover-letter generation."""
    session_id: int
    job_title: str = ""
    employer_name: str = ""
    tone: str = "formal"        # formal | friendly | neutral
    language: str = "de"        # de | en
    force: bool = False   # bypass quality gate (for trainer use)


# ============================================================================
# App lifecycle
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle: startup and shutdown."""
    # Ensure the repo root (parent of tool-1-cv-maker) is on sys.path so that
    # `from shared.schema.cv_schema import CVDocument` works on fresh installs
    # where ams-shared may not be pip-installed yet.
    import sys
    _repo_root = str(Path(__file__).resolve().parents[3])  # backend→src→tool-1-cv-maker→AMS-JobAssist
    if _repo_root not in sys.path:
        sys.path.insert(0, _repo_root)

    # Configure structured logging.
    # NOTE: We do NOT put %(session_id)s in the root format because records
    # emitted during startup (before any request) don't have that field and
    # Python 3.14's logging raises KeyError.  Session ID is logged per-request
    # in the request_logging_middleware instead.
    _root = logging.getLogger()
    if not _root.handlers:
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        )

    # Startup — use the ABSOLUTE db path under DB_DIR so the location is
    # deterministic regardless of cwd, and so the /api/admin/backup endpoint
    # (which reads DB_DIR/ams_jobassist.db) always points at the live database.
    db_manager = DatabaseManager(str(DB_DIR / "ams_jobassist.db"))
    db_manager.initialize()
    app.state.db_manager = db_manager
    app.state.db = db_manager  # alias used by _log_export()

    # CV pipeline components
    app.state.cv_storage = CVStorage(db_manager)
    app.state.cv_builder = CVBuilder(db_manager)

    # Export engines (all share the same output directory)
    app.state.json_exporter = JSONExporter(output_dir=str(EXPORTS_DIR))
    app.state.pdf_exporter = PDFExporter(output_dir=str(EXPORTS_DIR))
    app.state.docx_exporter = DOCXExporter(output_dir=str(EXPORTS_DIR))
    app.state.europass_exporter = EuropassExporter(output_dir=str(EXPORTS_DIR))

    # Expand verb/skill data if the seed expansion module is available.
    # Uses INSERT OR IGNORE — safe to run on every startup (idempotent).
    try:
        from db_seed_expansion import apply_expansion, apply_ats_expansion
        counts = apply_expansion(db_manager)
        if any(v > 0 for v in counts.values()):
            logger.info(f"Seed expansion applied: {counts}")
            print(f"[OK] Seed data expanded: {counts}")
        # Also expand ATS keyword bank in memory
        apply_ats_expansion()
    except ImportError:
        pass  # Module not present yet — skip
    except Exception as _exc:
        logger.warning(f"Seed expansion failed (non-fatal): {_exc}")

    init_interview_routes(db_manager)
    logger.info("Database initialized")
    logger.info("Interview routes initialized")
    logger.info(f"Serving at http://{HOST}:{PORT}")
    print("[OK] Database initialized")
    print("[OK] Interview routes initialized")
    print(f"[OK] Exports directory: {EXPORTS_DIR}")
    print(f"[OK] Serving at http://{HOST}:{PORT}")

    # ---- Data retention -------------------------------------------------------
    # Run once at startup, then every 24 h in the background.
    from config import DATA_RETENTION_DAYS
    from interview.engine import InterviewEngine as _IE

    async def _retention_loop(engine: _IE, days: int) -> None:
        """Delete old sessions on startup, then once every 24 hours."""
        import asyncio as _asyncio
        while True:
            try:
                deleted = engine.cleanup_old_sessions(days)
                if deleted:
                    logger.info(f"Data retention: removed {deleted} sessions older than {days} days")
            except Exception as _exc:
                logger.warning(f"Data retention cleanup failed (non-fatal): {_exc}")
            await _asyncio.sleep(86_400)  # 24 h

    _retention_task = None
    if DATA_RETENTION_DAYS > 0:
        from api.interview import _engine as _iv_engine
        if _iv_engine is not None:
            import asyncio as _asyncio
            _retention_task = _asyncio.create_task(
                _retention_loop(_iv_engine, DATA_RETENTION_DAYS)
            )
            print(f"[OK] Data retention: sessions older than {DATA_RETENTION_DAYS} days will be cleaned up daily")
        else:
            logger.warning("Data retention configured but interview engine not ready — skipping background task")

    # ---- Warm the local AI model in the background ----------------------------
    # The first AI request otherwise pays a ~10-20s cold load of the ~1GB GGUF
    # on the request path. Warming in a daemon thread keeps startup instant and
    # the model resident before the first participant arrives. is_ready() only
    # loads an existing model (it never triggers a download) and is idempotent.
    if os.environ.get("AMS_WARM_MODEL", "1").lower() not in ("0", "false", "no"):
        import threading as _threading

        def _warm_model():
            try:
                from ai import local_llm
                if local_llm.model_exists():
                    if local_llm.is_ready():
                        logger.info("Local AI model warmed on startup")
                    else:
                        logger.info("Local model present but could not be warmed")
            except Exception as _exc:
                logger.warning(f"Model warm-up skipped (non-fatal): {_exc}")

        _threading.Thread(target=_warm_model, name="ams-model-warm", daemon=True).start()
        print("[OK] Local AI model warming in background")

    yield

    # Shutdown
    if _retention_task is not None:
        _retention_task.cancel()
    if hasattr(app.state, "db_manager") and app.state.db_manager:
        app.state.db_manager.close()
        logger.info("Database connection closed")


app = FastAPI(
    title="AMS JobAssist - CV Maker",
    description="Offline CV building tool for AMS participants",
    lifespan=lifespan,
)


# ============================================================================
# CSRF protection middleware
# Mirrors the CSRFMiddleware in Tool 2.
# Rejects state-changing requests whose Origin header points to a different
# host — only a real browser cross-site attack would set a foreign Origin.
# Non-browser clients (Python, curl, Electron) never send Origin so they
# are always allowed (no browser cross-origin risk for a localhost tool).
# ============================================================================

class _CSRFMiddleware(BaseHTTPMiddleware):
    _SAFE = {"GET", "HEAD", "OPTIONS"}

    async def dispatch(self, request: Request, call_next):
        if request.method in self._SAFE:
            return await call_next(request)

        origin = request.headers.get("origin", "")
        if not origin:
            # Non-browser client — allow
            return await call_next(request)

        host = request.headers.get("host", "")
        from config import PORT as _PORT
        allowed = {
            f"http://{host}",
            f"https://{host}",
            f"http://localhost:{_PORT}",
            f"http://127.0.0.1:{_PORT}",
        }

        if origin not in allowed:
            logger.warning(f"CSRF: rejected {request.method} from origin {origin!r}")
            return JSONResponse(status_code=403, content={"detail": "Cross-origin request rejected"})

        return await call_next(request)


app.add_middleware(_CSRFMiddleware)


@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    """
    Attach a unique request ID to every request for structured logging and debugging.
    Logs method, path, duration, and status code at INFO level.
    """
    req_id = str(uuid.uuid4())[:8]
    request.state.request_id = req_id
    start = time.monotonic()
    try:
        response = await call_next(request)
    except Exception as exc:
        duration_ms = int((time.monotonic() - start) * 1000)
        logger.error(f"[{req_id}] UNHANDLED {request.method} {request.url.path} ({duration_ms}ms): {exc}")
        raise
    duration_ms = int((time.monotonic() - start) * 1000)
    logger.info(f"[{req_id}] {request.method} {request.url.path} → {response.status_code} ({duration_ms}ms)")
    response.headers["X-Request-ID"] = req_id
    # Security headers — CSP locks scripts/styles to same origin (no CDN), prevents
    # clickjacking, MIME-sniffing, referrer leakage, and disables flashy permissions.
    response.headers.setdefault(
        "Content-Security-Policy",
        "default-src 'self'; "
        "script-src 'self'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data: blob:; "
        "font-src 'self'; "
        "connect-src 'self'; "
        "frame-ancestors 'none'; "
        "base-uri 'self'; "
        "form-action 'self'"
    )
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault("Referrer-Policy", "no-referrer")
    response.headers.setdefault("Permissions-Policy", "geolocation=(), microphone=(), camera=(), payment=()")
    # Never let the browser cache the app shell / static assets. Without this,
    # FastAPI's StaticFiles sends no cache-control and browsers heuristic-cache
    # styles.css / app.js / index.html — so UI changes silently don't appear
    # until a manual hard-refresh. Force revalidation on every load.
    _p = request.url.path
    if _p == "/" or _p.startswith("/static"):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    return response


# ============================================================================
# Structured error responses
# ============================================================================

from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as _StarletteHTTPException


def _error_body(request: Request, status_code: int, detail: str, error_code: Optional[str] = None) -> dict:
    """Build a consistent error response envelope."""
    from api.interview import _current_session_id
    return {
        "status": "error",
        "error": {
            "code": error_code or f"HTTP_{status_code}",
            "detail": detail,
            "request_id": getattr(getattr(request, "state", None), "request_id", None),
            "session_id": _current_session_id.get(None),
        },
    }


@app.exception_handler(_StarletteHTTPException)
async def http_exception_handler(request: Request, exc: _StarletteHTTPException):
    body = _error_body(request, exc.status_code, str(exc.detail))
    return JSONResponse(status_code=exc.status_code, content=body)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = [f"{' → '.join(str(l) for l in e['loc'])}: {e['msg']}" for e in exc.errors()]
    body = _error_body(request, 422, "; ".join(errors), error_code="VALIDATION_ERROR")
    return JSONResponse(status_code=422, content=body)


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception on {request.method} {request.url.path}: {exc}", exc_info=True)
    body = _error_body(request, 500, "Internal server error — please try again", error_code="INTERNAL_ERROR")
    return JSONResponse(status_code=500, content=body)


def get_db_manager(request: Request) -> DatabaseManager:
    """FastAPI dependency: get DatabaseManager from app.state."""
    return request.app.state.db_manager


# ============================================================================
# Register API routes
# ============================================================================

app.include_router(interview_router)
from api.language_packs import router as language_packs_router
app.include_router(language_packs_router)


# ============================================================================
# Health check
# ============================================================================

@app.get("/health", tags=["Health"])
async def health_check():
    """Simple liveness probe."""
    return {"status": "ok"}


# ============================================================================
# CV Management
# ============================================================================

@app.get("/api/cv/{session_id}", tags=["CV"])
async def get_cv_metadata(session_id: int, request: Request):
    """Return CV metadata for a completed session."""
    cv_storage: CVStorage = request.app.state.cv_storage
    cv_data = cv_storage.get_cv_data(session_id)
    if cv_data is None:
        raise HTTPException(status_code=404, detail="CV not found for this session")

    return {
        "status": "success",
        "data": {
            "session_id": cv_data.session_id,
            "user_id": cv_data.user_id,
            "interview_path": cv_data.interview_path,
            "language_input": cv_data.language_input,
            "language_output_primary": cv_data.language_output_primary,
            "language_output_secondary": cv_data.language_output_secondary,
            "overall_quality": cv_data.overall_quality,
            "ready_for_export": cv_data.ready_for_export,
            "all_skills": cv_data.all_skills or [],
        },
    }


@app.get("/api/admin/backup", tags=["Admin"])
async def admin_backup_tool1():
    """
    Stream Tool 1's SQLite database as a downloadable file.

    Intended for periodic backup by AMS IT. Returns the live `.db` file with a
    timestamped filename. Because Tool 1 has no auth, this endpoint binds to
    127.0.0.1 only — never expose this port externally.
    """
    from datetime import datetime as _dt
    from fastapi.responses import FileResponse

    db_path = DB_DIR / "ams_jobassist.db"
    if not db_path.exists():
        raise HTTPException(status_code=404, detail="Database file not found")

    timestamp = _dt.utcnow().strftime("%Y%m%d_%H%M%S")
    filename = f"ams_jobassist_backup_{timestamp}.db"
    logger.info(f"BACKUP requested: {db_path}")
    return FileResponse(
        path=str(db_path),
        filename=filename,
        media_type="application/octet-stream",
        headers={"X-Backup-Timestamp": timestamp},
    )


@app.get("/api/cv/{session_id}/my-data", tags=["DSGVO"])
async def download_my_data(session_id: int, request: Request):
    """
    DSGVO data portability — download all raw answers and CV data as JSON.

    Allows the participant to export everything stored about them in one file.
    No processing: raw answers + polished CV + metadata, nothing else.
    """
    db_manager: DatabaseManager = request.app.state.db_manager
    cv_storage: CVStorage = request.app.state.cv_storage

    # Get raw answers
    raw_answers = db_manager.execute_query(
        "SELECT question_id, answer_text, created_at FROM answers WHERE session_id = ? ORDER BY id",
        (session_id,)
    )
    if not raw_answers:
        raise HTTPException(status_code=404, detail="Keine Daten für diese Sitzung gefunden.")

    # Get CV data if built
    cv_data = cv_storage.get_cv_data(session_id)
    cv_dict = cv_data.to_dict() if cv_data else None

    import json as _json
    from fastapi.responses import Response
    payload = {
        "notice": "Diese Datei enthält alle Ihre in AMS JobAssist gespeicherten Daten (Art. 20 DSGVO).",
        "session_id": session_id,
        "raw_answers": raw_answers,
        "cv_data": cv_dict,
        "exported_at": __import__("datetime").datetime.now().isoformat(),
    }
    return Response(
        content=_json.dumps(payload, ensure_ascii=False, indent=2),
        media_type="application/json",
        headers={"Content-Disposition": f"attachment; filename=meine-daten-{session_id}.json"},
    )


# ============================================================================
# Export Endpoints
# ============================================================================

def _get_ready_cv(session_id: int, request: Request, force: bool = False):
    """Shared helper: fetch CVData or raise HTTP errors."""
    cv_storage: CVStorage = request.app.state.cv_storage
    cv_data = cv_storage.get_cv_data(session_id)
    if cv_data is None:
        raise HTTPException(status_code=404, detail="CV not found — complete the interview first")
    if not force and not cv_data.ready_for_export:
        raise HTTPException(status_code=400, detail="CV quality too low for export (add more detail, or use force=true)")
    return cv_data


def _log_export(request: Request, session_id: int, export_type: str, path: Optional[str], language: str = "de") -> None:
    """Non-fatal: write an export record to the exports table."""
    try:
        import os as _os
        file_size = _os.path.getsize(path) if path and _os.path.exists(path) else None
        db: DatabaseManager = request.app.state.db
        db.execute_update(
            """INSERT INTO exports (session_id, export_type, file_path, file_size, export_language)
               VALUES (?, ?, ?, ?, ?)""",
            (session_id, export_type, path, file_size, language),
        )
    except Exception as _exc:
        logger.warning(f"export_log: could not write export record (non-fatal): {_exc}")


def _persist_cover_letter(request: Request, session_id, letter_dict: dict,
                          tone: str, job_title: str, employer_name: str) -> None:
    """Non-fatal: store the generated cover letter so trainers can review it."""
    try:
        db: DatabaseManager = request.app.state.db
        db.execute_update(
            """INSERT INTO cover_letters
               (session_id, text, language, tone, job_title, employer_name, word_count)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (session_id, letter_dict.get("text", ""), letter_dict.get("language", "de"),
             tone, job_title or None, employer_name or None,
             letter_dict.get("word_count")),
        )
    except Exception as _exc:
        logger.warning(f"cover_letter_log: could not persist (non-fatal): {_exc}")


def _persist_ats_score(request: Request, session_id, result, suggestions: list,
                       job_description: str = "") -> None:
    """Non-fatal: store an ATS analysis result so trainers can review/compare."""
    try:
        import json as _json
        db: DatabaseManager = request.app.state.db
        db.execute_update(
            """INSERT INTO ats_scores
               (session_id, score, grade, matched_keywords, missing_keywords,
                suggestions, job_description_snippet)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (session_id, result.score, result.grade,
             _json.dumps(result.matched_keywords, ensure_ascii=False),
             _json.dumps(result.missing_keywords, ensure_ascii=False),
             _json.dumps(suggestions, ensure_ascii=False),
             (job_description or "")[:200] or None),
        )
    except Exception as _exc:
        logger.warning(f"ats_score_log: could not persist (non-fatal): {_exc}")


@app.post("/api/export/json", tags=["Export"])
async def export_cv_json(body: ExportRequest, request: Request):
    """Export CV as JSON (for Tool 2 import or download)."""
    cv_data = _get_ready_cv(body.session_id, request, force=body.force)
    exporter: JSONExporter = request.app.state.json_exporter
    path = exporter.export(cv_data, language=body.language, filename=body.filename)
    if not path:
        raise HTTPException(status_code=500, detail="JSON export failed")
    _log_export(request, body.session_id, "json", path, body.language)
    return FileResponse(path, media_type="application/json", filename=Path(path).name)


@app.post("/api/export/pdf", tags=["Export"])
async def export_cv_pdf(body: ExportRequest, request: Request):
    """Export CV as PDF."""
    cv_data = _get_ready_cv(body.session_id, request, force=body.force)
    exporter: PDFExporter = request.app.state.pdf_exporter
    path = exporter.export(cv_data, language=body.language, filename=body.filename)
    if not path:
        raise HTTPException(status_code=500, detail="PDF export failed")
    _log_export(request, body.session_id, "pdf", path, body.language)
    return FileResponse(path, media_type="application/pdf", filename=Path(path).name)


@app.post("/api/export/docx", tags=["Export"])
async def export_cv_docx(body: ExportRequest, request: Request):
    """Export CV as DOCX (Word document)."""
    cv_data = _get_ready_cv(body.session_id, request, force=body.force)
    exporter: DOCXExporter = request.app.state.docx_exporter
    path = exporter.export(cv_data, language=body.language, filename=body.filename)
    if not path:
        raise HTTPException(status_code=500, detail="DOCX export failed")
    _log_export(request, body.session_id, "docx", path, body.language)
    return FileResponse(
        path,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename=Path(path).name,
    )


@app.post("/api/export/cover-letter", tags=["Export"])
def export_cover_letter(body: CoverLetterRequest, request: Request):
    """
    Generate a cover letter for a completed CV.

    Uses the CV's identity, skills, and experience sections to produce
    a template-based letter in the requested language and tone.
    Optionally targeted at a specific job title / employer.
    """
    cv_data = _get_ready_cv(body.session_id, request, force=body.force)
    from cv.cover_letter import generate_from_cv_data
    letter = generate_from_cv_data(
        cv_data,
        job_title=body.job_title,
        employer_name=body.employer_name,
        tone=body.tone,
        language=body.language,
    )

    letter_dict = letter.to_dict()

    # Optionally enhance the template-generated body with the local AI model.
    # This smooths out template seams and adds natural flow while keeping all facts.
    from ai.local_llm import is_ready
    if is_ready():
        try:
            from ai.local_llm import chat as llm_chat
            raw_body = letter_dict.get("text", "")
            if raw_body:
                enhanced = llm_chat(
                    system=(
                        "Du bist ein professioneller Bewerbungsschreiber bei AMS Österreich. "
                        "Verbessere das folgende Anschreiben: flüssigere Formulierung, "
                        "keine Wiederholungen, maximal eine DIN-A4-Seite. "
                        "Behalte alle Fakten, Namen und Daten bei. Gib nur das verbesserte Anschreiben zurück."
                    ),
                    user=raw_body,
                    max_tokens=600,
                )
                if enhanced and len(enhanced) > 100:
                    letter_dict["text"] = enhanced
                    letter_dict["word_count"] = len(enhanced.split())
                    letter_dict["ai_enhanced"] = True
        except Exception as _exc:
            logger.warning(f"AI cover letter enhancement failed (using template): {_exc}")

    _log_export(request, body.session_id, "cover-letter", None, body.language)
    _persist_cover_letter(request, body.session_id, letter_dict,
                          body.tone, body.job_title, body.employer_name)
    return {
        "status": "success",
        "data": letter_dict,
    }


# ============================================================================
# ATS Scoring
# ============================================================================

@app.post("/api/ats/score", tags=["ATS"])
async def ats_score(body: ATSScoreRequest, request: Request):
    """
    Score the CV against a job description (or the full ATS bank if no JD provided).
    Returns score, grade, matched/missing keywords, and suggestions.
    """
    cv_storage: CVStorage = request.app.state.cv_storage
    cv_data = cv_storage.get_cv_data(body.session_id)
    if cv_data is None:
        raise HTTPException(status_code=404, detail="CV not found — complete the interview first")

    from polish.ats import score_against_job, score_against_bank, validate_cv_structure
    # Build full CV text from all sections
    texts = []
    for section_list in [cv_data.background, cv_data.experience, cv_data.skills,
                         cv_data.motivation, cv_data.training, cv_data.projects]:
        for s in section_list:
            texts.append(s.english or s.german or "")
    cv_text = " ".join(t for t in texts if t)

    if body.job_description:
        result = score_against_job(cv_text, body.job_description)
    else:
        result = score_against_bank(cv_text)

    structural_warnings = validate_cv_structure(cv_data)
    all_suggestions = result.suggestions + structural_warnings

    _persist_ats_score(request, body.session_id, result, all_suggestions,
                       body.job_description or "")

    return {
        "status": "success",
        "data": {
            "score": result.score,
            "grade": result.grade,
            "matched_keywords": result.matched_keywords,
            "missing_keywords": result.missing_keywords,
            "suggestions": all_suggestions,
        }
    }


# ============================================================================
# Europass Export
# ============================================================================

@app.post("/api/export/europass", tags=["Export"])
async def export_cv_europass(body: ExportRequest, request: Request):
    """Export CV as Europass-compatible XML."""
    cv_data = _get_ready_cv(body.session_id, request, force=body.force)
    exporter: EuropassExporter = request.app.state.europass_exporter
    path = exporter.export(cv_data, language=body.language, filename=body.filename)
    if not path:
        raise HTTPException(status_code=500, detail="Europass XML export failed")
    _log_export(request, body.session_id, "europass", path, body.language)
    return FileResponse(path, media_type="application/xml", filename=Path(path).name)


# ============================================================================
# AI Chat + Coaching endpoints
# ============================================================================

class ChatRequest(BaseModel):
    session_id: Optional[int] = None
    message: str
    language: str = "de"

class JobMatchRequest(BaseModel):
    session_id: int
    job_description: str

class InterviewPrepRequest(BaseModel):
    session_id: int

class DumpExtractRequest(BaseModel):
    session_id: int
    text: str
    language: str = "de"
    expect: Optional[str] = None  # gap being answered: contact|target_job|experience|education|skills|name

class ModelDownloadRequest(BaseModel):
    confirm: bool = False
    tier: Optional[str] = None  # "light", "medium", or "full"

class ProfileSummaryRequest(BaseModel):
    session_id: int
    language: str = "de"   # Language for the output summary

class InterviewCoachRequest(BaseModel):
    session_id: Optional[int] = None
    message: str
    language: str = "de"
    question_id: Optional[str] = None   # current question being answered
    question_text: Optional[str] = None # text of the current question (for context)


@app.post("/api/ai/chat", tags=["AI"])
def ai_chat(body: ChatRequest, request: Request):
    """
    Coach chat — context-aware conversation with the AI.
    Knows the user's CV if session_id is provided.
    Falls back to a helpful message if model not available.
    """
    try:
        from ai.local_llm import coach_chat, is_ready
    except ImportError:
        return {"status": "success", "data": {"reply": "KI-Modell nicht verfügbar. Bitte installieren Sie das Modell.", "ai_mode": False}}

    cv_context: dict = {}
    if body.session_id:
        try:
            cv_storage: CVStorage = request.app.state.cv_storage
            cv_data = cv_storage.get_cv_data(body.session_id)
            if cv_data:
                sections_summary = "; ".join(
                    f"{s.category}: {(s.german or s.english or '')[:80]}"
                    for s in (cv_data.background + cv_data.experience + cv_data.skills)[:5]
                    if s.german or s.english
                )
                cv_context = {
                    "name": (cv_data.identity.full_name if cv_data.identity else "") or "",
                    "target_job": getattr(cv_data, "target_job", "") or "",
                    "path": getattr(cv_data, "interview_path", "") or "",
                    "sections_summary": sections_summary,
                }
        except Exception:
            pass

    if not is_ready():
        # Graceful fallback — tell the user what to do
        return {"status": "success", "data": {
            "reply": (
                "Das lokale KI-Modell ist noch nicht geladen. "
                "Bitte installieren Sie es über Einstellungen → Modell herunterladen."
            ),
            "ai_mode": False,
        }}

    reply = coach_chat(body.message, cv_context, body.language)
    if not reply:
        reply = "Ich konnte Ihre Frage gerade nicht beantworten. Bitte versuchen Sie es erneut."

    return {"status": "success", "data": {"reply": reply, "ai_mode": True}}


@app.post("/api/ai/interview-coach", tags=["AI"])
def ai_interview_coach(body: InterviewCoachRequest, request: Request):
    """
    In-interview coaching assistant.

    Helps the user answer the CURRENT question — explains what's being asked,
    gives examples, and offers gentle prompts when they're stuck.
    Works during the interview (not just post-completion).
    Always returns something useful — gracefully degrades to rule-based tips.
    """
    language = body.language or "de"
    question_text = body.question_text or ""
    question_id = body.question_id or ""
    user_message = body.message.strip()

    # -------------------------------------------------------------------------
    # Try AI (local LLM → Ollama)
    # -------------------------------------------------------------------------
    ai_reply = None
    try:
        from ai.local_llm import coach_chat, is_ready
        if is_ready():
            system_prompt = (
                "Du bist ein einfühlsamer Karriereberater bei AMS Österreich. "
                "Du hilfst einer Person, eine Interviewfrage für ihren Lebenslauf zu beantworten. "
                "Antworte auf Sprachniveau B1. Sei ermutigend, nie wertend. "
                "Keine Fachbegriffe. Kurz und klar (maximal 3 Sätze). "
                "Sprache des Benutzers: " + language + ". "
            )
            if question_text:
                system_prompt += f'Aktuelle Frage: "{question_text}"'
            context = {
                "question": question_text,
                "question_id": question_id,
                "coaching_mode": True,
            }
            ai_reply = coach_chat(user_message, context, language)
    except Exception:
        pass

    if ai_reply:
        return {"status": "success", "data": {"reply": ai_reply, "source": "ai"}}

    # -------------------------------------------------------------------------
    # Rule-based fallback — question-aware tips
    # -------------------------------------------------------------------------
    # Map common user "stuck" phrases → helpful responses
    _STUCK_TRIGGERS = [
        "weiß nicht", "keine ahnung", "nichts besonderes", "i don't know",
        "bilmiyorum", "لا أعرف", "не знаю", "neviem", "ne znam",
        "nie wiem", "nu știu", "не знаю",
    ]
    user_lower = user_message.lower()
    is_stuck = any(t in user_lower for t in _STUCK_TRIGGERS)

    # Question-category-based tips
    _TIPS = {
        "de": {
            "experience":  "Denken Sie an Ihren typischen Arbeitstag: Was haben Sie gemacht? Welche Werkzeuge haben Sie benutzt? Wie viele Personen haben Sie betreut?",
            "skills":      "Welche Programme oder Maschinen haben Sie bedient? Welche Sprachen sprechen Sie? Was können Sie besonders gut?",
            "background":  "Wo haben Sie zuerst gearbeitet oder gelernt? Wie viele Jahre waren Sie dabei? Was war Ihre wichtigste Aufgabe?",
            "identity":    "Schreiben Sie einfach Ihren vollständigen Namen — so wie er in Ihrem Ausweis steht.",
            "default":     "Denken Sie an ein konkretes Beispiel aus Ihrem Leben — auch kleine Dinge zählen.",
        },
        "en": {
            "experience":  "Think about a typical workday: what did you do? What tools did you use? How many people did you help?",
            "skills":      "Which programs or machines did you use? Which languages do you speak? What are you especially good at?",
            "background":  "Where did you first work or study? For how long? What was your most important task?",
            "identity":    "Simply write your full name — as it appears on your ID.",
            "default":     "Think of a concrete example from your life — small things count too.",
        },
        "tr": {
            "experience":  "Tipik bir iş gününü düşünün: ne yaptınız? Hangi araçları kullandınız? Kaç kişiye yardım ettiniz?",
            "skills":      "Hangi programları veya makineleri kullandınız? Hangi dilleri konuşuyorsunuz?",
            "background":  "İlk nerede çalıştınız veya eğitim aldınız? Ne kadar süre? En önemli göreviniz ne idi?",
            "default":     "Hayatınızdan somut bir örnek düşünün — küçük şeyler de önemlidir.",
        },
        "ar": {
            "experience":  "فكر في يوم عمل عادي: ماذا فعلت؟ ما الأدوات التي استخدمتها؟ كم شخصًا ساعدت؟",
            "skills":      "ما البرامج أو الآلات التي استخدمتها؟ ما اللغات التي تتحدثها؟",
            "background":  "أين عملت أو تعلمت لأول مرة؟ لكم من الوقت؟ ما كانت مهمتك الأهم؟",
            "default":     "فكر في مثال ملموس من حياتك — الأشياء الصغيرة تحسب أيضًا.",
        },
    }

    # Determine category from question_id
    cat = "default"
    if "exp" in question_id or "_employer" in question_id or "_title" in question_id:
        cat = "experience"
    elif "skill" in question_id or "u_07" in question_id:
        cat = "skills"
    elif "bg" in question_id or "id_" in question_id:
        cat = "background" if "id_" not in question_id else "identity"
    elif "st_" in question_id or "cs_" in question_id or "p_" in question_id:
        cat = "experience"

    tips = _TIPS.get(language, _TIPS["de"])
    tip = tips.get(cat, tips["default"])

    if is_stuck:
        _stuck_intros = {
            "de": "Das ist ganz normal! Hier ein Tipp: ",
            "en": "That's completely fine! Here's a tip: ",
            "tr": "Bu çok normal! İşte bir ipucu: ",
            "ar": "هذا طبيعي تمامًا! إليك نصيحة: ",
        }
        intro = _stuck_intros.get(language, _stuck_intros["de"])
        reply = intro + tip
    else:
        _general = {
            "de": f"Gute Frage! {tip}",
            "en": f"Good question! {tip}",
            "tr": f"İyi soru! {tip}",
            "ar": f"سؤال جيد! {tip}",
        }
        reply = _general.get(language, _general["de"])

    return {"status": "success", "data": {"reply": reply, "source": "rules"}}


@app.post("/api/ai/dump-extract", tags=["AI"])
def ai_dump_extract(body: DumpExtractRequest, request: Request):
    """
    Free-form "dump" mode: the participant writes everything about themselves in
    one block (any language); we extract structured CV fields, store them as
    answers (so the normal build/export pipeline works), and report what was
    captured and what's still missing — so the assistant can ask only about the
    gaps. Rules-first with AI assist; never fails the request.
    """
    from ai.local_llm import extract_cv_fields
    db: DatabaseManager = request.app.state.db_manager
    sid = body.session_id

    def _save(qid: str, txt: str):
        if txt and txt.strip():
            try:
                db.save_answer(session_id=sid, question_id=qid, answer_text=txt.strip())
            except Exception as _e:
                logger.warning(f"dump-extract save {qid} failed: {_e}")

    def _register_and_save(qid: str, category: str, txt: str):
        # Register a synthetic question so the CV builder reads the right
        # category (it joins answers→interview_questions for category).
        try:
            db.execute_update(
                """INSERT INTO interview_questions
                   (question_id, question_text, category, interview_path, question_order,
                    hint, good_example, bad_example, min_length)
                   VALUES (?, ?, ?, 'dump', 100, '', '', '', 0)
                   ON CONFLICT(question_id) DO UPDATE SET category = excluded.category""",
                (qid, "(dump)", category),
            )
        except Exception as _e:
            logger.warning(f"dump-extract register {qid} failed: {_e}")
        _save(qid, txt)

    # What's already on file (so multi-turn conversation APPENDS, never blanks).
    try:
        _rows = db.execute_query(
            "SELECT question_id, answer_text FROM answers WHERE session_id = ?", (sid,)) or []
        existing = {r["question_id"]: (r.get("answer_text") or "") for r in _rows}
    except Exception:
        existing = {}
    def _have(qid):
        v = existing.get(qid, "")
        return bool(v) and v.strip() and v.strip() != "[SKIPPED]"

    def _next_idx(prefix):
        n = 0
        while f"{prefix}{n}" in existing:
            n += 1
        return n

    txt = (body.text or "").strip()
    captured = {"name": "", "city": "", "phone": "", "email": "",
                "target_job": "", "experiences": [], "education": [], "skills": [], "motivation": []}

    if body.expect:
        # Targeted reply to one gap question — categorise it directly (fast, no
        # reliance on the small model) so the answer lands in the right section.
        import re as _re
        exp = body.expect
        if exp == "name":
            captured["name"] = txt[:80]
            _save("id_name", txt[:80])
        elif exp == "contact":
            f = extract_cv_fields(txt, body.language)  # reuse the email/phone regex
            parts = [p for p in (f.get("city"), f.get("phone"), f.get("email")) if p] or [txt]
            captured.update({"city": f.get("city", ""), "phone": f.get("phone", ""), "email": f.get("email", "")})
            _save("id_contact", ", ".join(parts))
        elif exp == "target_job":
            captured["target_job"] = txt[:120]
            _save("id_target_job", txt[:120])
        elif exp in ("experience", "experience_detail"):
            captured["experiences"] = [txt[:600]]
            _register_and_save(f"dump_exp_{_next_idx('dump_exp_')}", "experience", txt[:600])
        elif exp == "education":
            captured["education"] = [txt[:400]]
            _register_and_save(f"dump_edu_{_next_idx('dump_edu_')}", "background", txt[:400])
        elif exp == "motivation":
            captured["motivation"] = [txt[:400]]
            _register_and_save(f"dump_mot_{_next_idx('dump_mot_')}", "motivation", txt[:400])
        elif exp == "skills":
            new = [s.strip() for s in _re.split(r"[,\n;|]", txt) if len(s.strip()) > 1]
            captured["skills"] = new
            prev = existing.get("dump_skills_0", "")
            merged = [s.strip() for s in (prev.split(",") if prev else []) if s.strip()]
            for s in new:
                if s not in merged:
                    merged.append(s)
            _register_and_save("dump_skills_0", "skills", ", ".join(merged))
        else:
            # unknown hint: treat as more experience
            captured["experiences"] = [txt[:600]]
            _register_and_save(f"dump_exp_{_next_idx('dump_exp_')}", "experience", txt[:600])
    else:
        # Initial free-form dump — full AI-assisted extraction.
        captured = extract_cv_fields(txt, body.language)
        if captured["name"]:
            _save("id_name", captured["name"])
        contact_parts = [p for p in (captured["city"], captured["phone"], captured["email"]) if p]
        if contact_parts:
            _save("id_contact", ", ".join(contact_parts))
        if captured["target_job"]:
            _save("id_target_job", captured["target_job"])
        ei = _next_idx("dump_exp_")
        for item in captured["experiences"][:6]:
            _register_and_save(f"dump_exp_{ei}", "experience", item); ei += 1
        di = _next_idx("dump_edu_")
        for item in captured["education"][:4]:
            _register_and_save(f"dump_edu_{di}", "background", item); di += 1
        if captured["skills"]:
            prev = existing.get("dump_skills_0", "")
            merged = [s.strip() for s in (prev.split(",") if prev else []) if s.strip()]
            for s in captured["skills"][:12]:
                if s and s not in merged:
                    merged.append(s)
            _register_and_save("dump_skills_0", "skills", ", ".join(merged))

    # Re-read what's on file now and decide what to still ask about.
    try:
        _rows2 = db.execute_query(
            "SELECT question_id, answer_text FROM answers WHERE session_id = ?", (sid,)) or []
        now = {r["question_id"]: (r.get("answer_text") or "") for r in _rows2}
    except Exception:
        now = existing
    def _has(qid):
        v = now.get(qid, "")
        return bool(v) and v.strip() and v.strip() != "[SKIPPED]"
    n_exp = sum(1 for k in now if k.startswith("dump_exp_") and now[k].strip())
    has_edu = any(k.startswith("dump_edu_") and now[k].strip() for k in now)

    # Ordered gaps the assistant should still ask about. experience_detail is
    # asked only ONCE (when there's a single thin experience and we haven't dug
    # deeper yet); after a 2nd experience entry exists, we stop probing it.
    missing = []
    if not _has("id_name"):       missing.append("name")
    if n_exp == 0:                missing.append("experience")
    elif n_exp == 1:             missing.append("experience_detail")
    if not _has("dump_skills_0"): missing.append("skills")
    if not _has("id_target_job"): missing.append("target_job")
    if not has_edu:               missing.append("education")
    if not _has("id_contact"):    missing.append("contact")

    return {"status": "success", "data": {"captured": captured, "missing": missing}}


@app.get("/api/ai/dump-snapshot/{session_id}", tags=["AI"])
async def ai_dump_snapshot(session_id: int, request: Request):
    """
    Reconstruct the captured/missing snapshot for a session from stored answers.

    Used on RESUME so the living-CV sheet can be repainted and the conversation
    can pick up at the right gap, instead of dropping the participant into the
    legacy per-question flow with an empty CV.
    """
    import re as _re
    db: DatabaseManager = request.app.state.db_manager
    try:
        rows = db.execute_query(
            "SELECT question_id, answer_text FROM answers WHERE session_id = ? ORDER BY id",
            (session_id,)) or []
    except Exception:
        rows = []
    now = {r["question_id"]: (r.get("answer_text") or "") for r in rows}

    def _has(qid):
        v = now.get(qid, "")
        return bool(v) and v.strip() and v.strip() != "[SKIPPED]"

    # Parse the combined contact line into city / phone / email.
    city = phone = email = ""
    blob = now.get("id_contact", "") or ""
    if blob:
        m = _re.search(r"[\w.+-]+@[\w-]+\.[\w.-]+", blob)
        if m:
            email = m.group(0); blob = blob.replace(email, " ")
        m = _re.search(r"(?<!\w)(\+?\d[\d\s/().\-]{6,}\d)", blob)
        if m:
            phone = m.group(1).strip(); blob = blob.replace(m.group(1), " ")
        rest = [p.strip(" ,;·") for p in _re.split(r"[,\n;]", blob) if p.strip(" ,;·")]
        if rest:
            city = rest[0]

    def _collect(prefix):
        out = []
        for k in sorted(now.keys()):
            if k.startswith(prefix) and now[k].strip() and now[k].strip() != "[SKIPPED]":
                out.append(now[k].strip())
        return out

    skills_raw = now.get("dump_skills_0", "") or ""
    skills = [s.strip() for s in skills_raw.split(",") if s.strip()]

    captured = {
        "name": (now.get("id_name", "") or "").strip(),
        "city": city, "phone": phone, "email": email,
        "target_job": (now.get("id_target_job", "") or "").strip(),
        "experiences": _collect("dump_exp_"),
        "education": _collect("dump_edu_"),
        "skills": skills,
        "motivation": _collect("dump_mot_"),
    }

    n_exp = len(captured["experiences"])
    has_edu = bool(captured["education"])
    missing = []
    if not _has("id_name"):       missing.append("name")
    if n_exp == 0:                missing.append("experience")
    elif n_exp == 1:             missing.append("experience_detail")
    if not _has("dump_skills_0"): missing.append("skills")
    if not _has("id_target_job"): missing.append("target_job")
    if not has_edu:               missing.append("education")
    if not _has("id_contact"):    missing.append("contact")

    has_any = bool(captured["name"] or captured["target_job"] or captured["experiences"]
                   or captured["skills"] or captured["education"] or blob)
    return {"status": "success",
            "data": {"captured": captured, "missing": missing, "has_content": has_any}}


@app.post("/api/ai/interview-prep", tags=["AI"])
def ai_interview_prep(body: InterviewPrepRequest, request: Request):
    """Generate likely interview questions from the completed CV.

    Tries local LLM first, then Ollama, then falls back to a path-aware
    rule-based question bank.  Never returns 503 — always gives useful content.
    """
    cv_data = None
    try:
        cv_storage: CVStorage = request.app.state.cv_storage
        cv_data = cv_storage.get_cv_data(body.session_id)
    except AttributeError:
        pass  # cv_storage not yet initialized — fall through to rule-based path

    summary = ""
    target_job = ""
    interview_path = "unemployed"
    if cv_data:
        sections = cv_data.background + cv_data.experience + cv_data.skills
        summary = "\n".join(
            (s.german or s.english or "")[:120]
            for s in sections[:6] if s.german or s.english
        )
        target_job = getattr(cv_data, "target_job", "") or ""
        interview_path = getattr(cv_data, "interview_path", "unemployed") or "unemployed"

    # Try AI first
    try:
        from ai.local_llm import generate_interview_prep, is_ready
        if is_ready():
            result = generate_interview_prep(summary, target_job)
            if result:
                # The model returns a numbered block ("1. … 2. …"); split it into
                # a clean list of questions so the UI shows them one per line
                # (matching the rule-based fallback shape).
                import re as _re
                if isinstance(result, str):
                    lines = [l.strip() for l in result.splitlines() if l.strip()]
                    questions = [_re.sub(r"^\s*\d+[\.\)]\s*", "", l).strip() for l in lines]
                    questions = [q for q in questions if len(q) > 5]
                else:
                    questions = result
                if questions:
                    return {"status": "success", "data": {"questions": questions, "target_job": target_job, "source": "ai"}}
    except Exception:
        pass

    # Rule-based fallback — path-aware question bank
    _PREP_QUESTIONS = {
        "unemployed": [
            "Warum haben Sie sich für diesen Beruf entschieden?",
            "Was sind Ihre größten beruflichen Stärken?",
            "Beschreiben Sie eine schwierige Situation und wie Sie sie gemeistert haben.",
            "Was erwarten Sie von Ihrem neuen Arbeitgeber?",
            "Wo sehen Sie sich in 3 Jahren?",
        ],
        "career-switch": [
            "Warum möchten Sie in diesen neuen Bereich wechseln?",
            "Welche Fähigkeiten aus Ihrem bisherigen Beruf sind für die neue Stelle wertvoll?",
            "Wie haben Sie sich auf den Wechsel vorbereitet?",
            "Was motiviert Sie, etwas Neues auszuprobieren?",
            "Welche Herausforderungen erwarten Sie beim Wechsel?",
        ],
        "student": [
            "Was haben Sie in Ihrer Ausbildung besonders gelernt?",
            "Welche praktischen Erfahrungen haben Sie bereits gesammelt?",
            "Warum ist Ihnen dieser Beruf wichtig?",
            "Wie gehen Sie mit Feedback und Kritik um?",
            "Was sind Ihre Ziele nach der Ausbildung?",
        ],
        "pause": [
            "Was haben Sie während Ihrer Pause gemacht?",
            "Wie haben Sie sich für die Rückkehr in den Beruf vorbereitet?",
            "Was motiviert Sie, jetzt wieder zu arbeiten?",
            "Was waren Ihre Hauptverantwortlichkeiten vor der Pause?",
            "Welche neuen Fähigkeiten haben Sie während der Pause entwickelt?",
        ],
        "other": [
            "Erzählen Sie mir von sich und Ihrem beruflichen Hintergrund.",
            "Was suchen Sie in Ihrer nächsten Stelle?",
            "Was sind Ihre wichtigsten beruflichen Stärken?",
            "Wie gehen Sie mit neuen Aufgaben um?",
            "Warum möchten Sie für dieses Unternehmen arbeiten?",
        ],
    }
    questions = _PREP_QUESTIONS.get(interview_path, _PREP_QUESTIONS["other"])
    if target_job:
        questions = [f"[Für die Stelle: {target_job}] " + q for q in questions[:3]] + questions[3:]

    return {"status": "success", "data": {"questions": questions, "target_job": target_job, "source": "rules"}}


@app.post("/api/ai/job-match", tags=["AI"])
def ai_job_match(body: JobMatchRequest, request: Request):
    """Match CV against a job description and give actionable feedback.

    Tries local LLM first, then Ollama, then falls back to rule-based ATS
    keyword matching.  Never returns 503.
    """
    if not body.job_description or len(body.job_description.strip()) < 20:
        raise HTTPException(status_code=400, detail="Stellenbeschreibung zu kurz (min. 20 Zeichen).")

    cv_data = None
    try:
        cv_storage: CVStorage = request.app.state.cv_storage
        cv_data = cv_storage.get_cv_data(body.session_id)
    except AttributeError:
        pass  # cv_storage not yet initialized — fall through to fallback

    if cv_data is None:
        raise HTTPException(status_code=404, detail="CV nicht gefunden.")

    sections = cv_data.background + cv_data.experience + cv_data.skills
    summary = "\n".join(
        (s.german or s.english or "")[:120]
        for s in sections[:6] if s.german or s.english
    )

    # Try AI
    try:
        from ai.local_llm import match_job_description, is_ready
        if is_ready():
            result = match_job_description(summary, body.job_description)
            if result:
                return {"status": "success", "data": {"analysis": result, "source": "ai"}}
    except Exception:
        pass

    # Rule-based fallback — ATS keyword overlap
    try:
        from polish.ats import score_against_job as _ats_score
        # Build plain text from CV sections for the ATS scorer
        cv_text = "\n".join(
            f"{s.category}: {(s.german or s.english or '')}"
            for s in sections if (s.german or s.english)
        )
        ats_result = _ats_score(cv_text, body.job_description).to_dict()
        score = ats_result.get("score", 0.5)
        matched = ats_result.get("matched_keywords", [])
        missing = ats_result.get("missing_keywords", [])

        lines = []
        pct = int(score * 100)
        if score >= 0.7:
            lines.append(f"✅ Gute Übereinstimmung ({pct}%) — Ihr CV passt gut zur Stelle.")
        elif score >= 0.45:
            lines.append(f"◎ Mittlere Übereinstimmung ({pct}%) — einige Anpassungen empfohlen.")
        else:
            lines.append(f"⚠ Geringe Übereinstimmung ({pct}%) — bitte passen Sie Ihren CV an.")
        if matched:
            lines.append(f"Gefundene Übereinstimmungen: {', '.join(matched[:8])}")
        if missing:
            lines.append(f"Fehlende Stichworte: {', '.join(missing[:6])}")
        lines.append("Tipp: Erwähnen Sie konkrete Tools, Ergebnisse und Erfahrungen passend zur Stelle.")
        analysis = "\n".join(lines)
        return {"status": "success", "data": {"analysis": analysis, "source": "rules", "score": score}}
    except Exception as _e:
        logger.warning(f"ATS fallback failed: {_e}")
        analysis = (
            "Ihr CV wurde mit der Stellenbeschreibung verglichen.\n"
            "Tipp: Stellen Sie sicher, dass Ihr CV die wichtigsten Begriffe aus der Stellenanzeige enthält.\n"
            "Erwähnen Sie konkrete Erfahrungen, Werkzeuge und Ergebnisse."
        )
        return {"status": "success", "data": {"analysis": analysis, "source": "rules"}}


@app.get("/api/ai/model-status", tags=["AI"])
async def ai_model_status():
    """Return AI model status. Priority: Local LLM > Ollama > rule-based."""
    try:
        from ai.local_llm import get_status as local_status
        local = local_status()
    except ImportError:
        local = {"local_model_available": False}

    try:
        from ai.ollama import get_status as ollama_status
        ollama = ollama_status()
    except ImportError:
        ollama = {"ollama_available": False}

    if local.get("local_model_available"):
        active = "local"
    elif ollama.get("ollama_available"):
        active = "ollama"
    else:
        active = "rules"

    # Knowledge base status
    knowledge = {"loaded": False, "jobs": 0}
    try:
        from ai.knowledge import get_stats
        knowledge = get_stats()
    except ImportError:
        pass

    return {"status": "success", "data": {
        "active_engine": active,
        "local": local,
        "ollama": ollama,
        "knowledge": knowledge,
        "architecture": "rules-first",  # Signal the new architecture
    }}


@app.post("/api/ai/download-model", tags=["AI"])
async def ai_download_model(body: ModelDownloadRequest):
    """
    Trigger model download in the background.
    Supports tiered models: "light" (~400MB), "medium" (~1.1GB), "full" (~2GB).
    Returns immediately — poll /api/ai/model-status to track progress.
    """
    try:
        from ai.local_llm import MODEL_TIERS, get_available_tiers, download_model, model_exists
    except ImportError:
        raise HTTPException(status_code=503, detail="AI module not available")

    tier = body.tier or "medium"
    if tier not in MODEL_TIERS:
        raise HTTPException(status_code=400, detail=f"Unknown tier: {tier}. Choose: light, medium, full")

    config = MODEL_TIERS[tier]

    if not body.confirm:
        return {"status": "confirm_required", "data": {
            "message": f"Download {config['name']} (~{config['size_mb']} MB)?",
            "tier": tier,
            "tiers": get_available_tiers(),
            "url": config["url"],
        }}

    import threading

    # Check if THIS specific tier already exists
    from pathlib import Path
    tier_path = Path(__file__).resolve().parents[1] / "data" / "models" / config["filename"]
    if tier_path.exists() and tier_path.stat().st_size > 10_000_000:
        return {"status": "success", "data": {"message": f"Modell '{config['name']}' bereits vorhanden."}}

    def _bg_download():
        download_model(tier=tier)

    t = threading.Thread(target=_bg_download, daemon=True)
    t.start()

    return {"status": "success", "data": {
        "message": f"Download von '{config['name']}' gestartet (~{config['size_mb']} MB). Bitte warten.",
        "tier": tier,
        "poll": "/api/ai/model-status",
    }}


@app.get("/api/ai/model-tiers", tags=["AI"])
async def ai_model_tiers():
    """List all available model tiers with download status."""
    try:
        from ai.local_llm import get_available_tiers
        return {"status": "success", "data": {"tiers": get_available_tiers()}}
    except ImportError:
        return {"status": "success", "data": {"tiers": []}}


@app.get("/api/ai/download-status", tags=["AI"])
async def ai_download_status():
    """
    Live progress of the current/last model download.

    Poll this after POST /api/ai/download-model. Returns status
    (idle/downloading/verifying/done/error/cancelled), bytes downloaded/total,
    percent, and any error message.
    """
    try:
        from ai.local_llm import get_download_status
        return {"status": "success", "data": get_download_status()}
    except ImportError:
        return {"status": "success", "data": {"status": "idle", "percent": 0}}


@app.post("/api/ai/download-cancel", tags=["AI"])
async def ai_download_cancel():
    """
    Stop an in-flight model download. The partial file is kept so a later
    download resumes from where it stopped.
    """
    try:
        from ai.local_llm import cancel_download
        cancel_download()
        return {"status": "success", "data": {"message": "Download wird gestoppt."}}
    except ImportError:
        raise HTTPException(status_code=503, detail="AI module not available")


# ============================================================================
# Knowledge Base (RAG) endpoints
# ============================================================================

@app.get("/api/ai/knowledge/status", tags=["AI"])
async def ai_knowledge_status():
    """Return knowledge base status — how many jobs, verbs, skills loaded."""
    try:
        from ai.knowledge import get_stats, is_loaded
        return {"status": "success", "data": get_stats()}
    except ImportError:
        return {"status": "success", "data": {"loaded": False, "jobs": 0}}


@app.get("/api/ai/knowledge/jobs", tags=["AI"])
async def ai_knowledge_jobs():
    """List all jobs in the knowledge base (for admin/debug)."""
    try:
        from ai.knowledge import get_all_jobs, get_job_categories
        return {"status": "success", "data": {
            "jobs": get_all_jobs(),
            "categories": get_job_categories(),
        }}
    except ImportError:
        return {"status": "success", "data": {"jobs": [], "categories": {}}}


@app.get("/api/ai/knowledge/search", tags=["AI"])
async def ai_knowledge_search(q: str = ""):
    """Search the knowledge base for a job matching the query text."""
    if not q or len(q.strip()) < 2:
        raise HTTPException(status_code=400, detail="Suchbegriff zu kurz (min. 2 Zeichen).")
    try:
        from ai.knowledge import find_job, get_context_for_prompt
        job = find_job(q)
        if not job:
            return {"status": "success", "data": {"match": None}}
        return {"status": "success", "data": {
            "match": job,
            "context": get_context_for_prompt(q, "experience"),
        }}
    except ImportError:
        return {"status": "success", "data": {"match": None}}


@app.post("/api/ai/profile-summary", tags=["AI"])
def ai_profile_summary(body: ProfileSummaryRequest, request: Request):
    """
    Generate a short, encouraging plain-language summary of the user's CV profile.

    Helps participants understand their own strengths and what makes them stand out.
    Returns a rule-based fallback summary when AI is not available.
    """
    cv_storage: CVStorage = request.app.state.cv_storage
    cv_data = cv_storage.get_cv_data(body.session_id)
    if not cv_data:
        raise HTTPException(status_code=404, detail="CV nicht gefunden — bitte zuerst das Interview abschließen.")

    # Build a compact profile snapshot for the model
    name = (cv_data.identity.full_name if cv_data.identity else "") or "der/die Teilnehmer/in"
    target = getattr(cv_data, "target_job", "") or ""
    skills = ", ".join(cv_data.all_skills[:10]) if getattr(cv_data, "all_skills", None) else ""
    sections = cv_data.background + cv_data.experience + cv_data.skills
    content_lines = [
        (s.german or s.english or "")[:120]
        for s in sections[:8] if s.german or s.english
    ]

    try:
        from ai.local_llm import chat as llm_chat, is_ready as _ready
        if _ready():
            target_clause = f"Zielberuf: {target}. " if target else ""
            skills_clause = f"Bekannte Fähigkeiten: {skills}. " if skills else ""
            content_block = "\n".join(f"- {l}" for l in content_lines)
            summary = llm_chat(
                system=(
                    "Du bist ein einfühlsamer Karriereberater bei AMS Österreich. "
                    "Deine Aufgabe: Schreibe eine kurze, ermutigende Zusammenfassung (3-4 Sätze) "
                    "für die Person selbst — was macht sie aus, was sind ihre Stärken. "
                    "Einfache Sprache, Niveau B1/B2. Nicht bewertend, positiv. "
                    "Beginne mit 'Sie haben...' oder 'Ihre Erfahrung...' — direkt, keine Einleitung."
                ),
                user=(
                    f"Name: {name}. {target_clause}{skills_clause}\n"
                    f"Lebenslauf-Auszug:\n{content_block}"
                ),
                max_tokens=350,
            )
            if summary and len(summary) > 50:
                return {"status": "success", "data": {"summary": summary, "source": "ai"}}
    except Exception as _exc:
        logger.warning(f"AI profile summary failed (using fallback): {_exc}")

    # Rule-based fallback: assemble a summary from the CV content directly
    lines = []
    if name and name != "der/die Teilnehmer/in":
        lines.append(f"{name} hat Berufserfahrung und praktische Fähigkeiten.")
    if skills:
        lines.append(f"Bekannte Fähigkeiten: {skills}.")
    if target:
        lines.append(f"Zielberuf: {target}.")
    if content_lines:
        lines.append(content_lines[0])
    fallback = " ".join(lines) if lines else "Ihr Profil wurde erstellt und ist bereit zum Herunterladen."

    return {"status": "success", "data": {"summary": fallback, "source": "rules"}}


# ============================================================================
# Static files + SPA root
# ============================================================================

# Mount frontend static files
if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


@app.get("/")
async def root():
    """Serve main UI"""
    return FileResponse(FRONTEND_DIR / "index.html")


def main():
    """Entry point for the ams-cv-maker script."""
    import uvicorn
    uvicorn.run(
        "app:app",
        host=HOST,
        port=PORT,
        reload=DEBUG,
        log_level="info",
    )


if __name__ == "__main__":
    main()
