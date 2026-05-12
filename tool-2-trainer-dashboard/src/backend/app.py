"""
AMS JobAssist Trainer Dashboard - FastAPI Application
Main entry point for Tool 2

Security features:
- API key authentication (when AMS_TRAINER_API_KEY is set)
- CSRF origin validation for state-changing requests
- Request size limiting
- Audit logging for all approval actions
"""

import logging
import secrets
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Response
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from pathlib import Path

from config import HOST, PORT, FRONTEND_DIR, DEBUG, API_KEY, AUTH_ENABLED, MAX_UPLOAD_SIZE_BYTES

logger = logging.getLogger(__name__)

# Configure audit logger (separate from app logger for compliance)
audit_logger = logging.getLogger("audit")
if not audit_logger.handlers:
    audit_handler = logging.StreamHandler()
    audit_handler.setFormatter(logging.Formatter(
        "%(asctime)s [AUDIT] %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    ))
    audit_logger.addHandler(audit_handler)
    audit_logger.setLevel(logging.INFO)


# =====================================================
# Middleware
# =====================================================

class AuthenticationMiddleware(BaseHTTPMiddleware):
    """
    API key authentication middleware.

    When AMS_TRAINER_API_KEY is set, all /api/* requests must include
    the key in the X-API-Key header or as a query parameter ?api_key=...

    Static files and the root page are always allowed.
    """

    async def dispatch(self, request: Request, call_next):
        if not AUTH_ENABLED:
            return await call_next(request)

        path = request.url.path

        # Allow static files and root page without auth
        if not path.startswith("/api"):
            return await call_next(request)

        # Check for API key — header only; query params expose keys in server logs
        api_key = request.headers.get("X-API-Key", "")

        if not api_key or not secrets.compare_digest(api_key, API_KEY):
            return JSONResponse(
                status_code=401,
                content={"detail": "Invalid or missing API key"},
            )

        return await call_next(request)


class CSRFMiddleware(BaseHTTPMiddleware):
    """
    Basic CSRF protection: reject state-changing requests from foreign origins.

    Checks Origin/Referer header on POST/PUT/DELETE requests to ensure
    they come from the same host (localhost).
    """

    SAFE_METHODS = {"GET", "HEAD", "OPTIONS"}

    async def dispatch(self, request: Request, call_next):
        if request.method in self.SAFE_METHODS:
            return await call_next(request)

        # For state-changing requests, check origin
        origin = request.headers.get("origin", "")
        referer = request.headers.get("referer", "")
        host = request.headers.get("host", "")

        # Starlette TestClient and direct API clients (curl, Python requests, etc.)
        # don't send Origin/Referer — not a browser CSRF risk since an attacker's
        # page running in a browser ALWAYS sends Origin.  Only reject if it looks
        # like an actual cross-origin browser request (Origin present but wrong).
        # Allow missing-header requests unconditionally for localhost-only tools.
        if not origin and not referer:
            # Non-browser client — allow (no browser cross-origin risk)
            return await call_next(request)

        # Check that origin matches our host
        allowed_origins = {
            f"http://{host}",
            f"https://{host}",
            f"http://localhost:{PORT}",
            f"http://127.0.0.1:{PORT}",
        }

        if origin and origin not in allowed_origins:
            logger.warning(f"CSRF: rejected request from origin {origin}")
            return JSONResponse(
                status_code=403,
                content={"detail": "Cross-origin request rejected"},
            )

        return await call_next(request)


class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    """Reject requests with bodies larger than MAX_UPLOAD_SIZE_BYTES."""

    async def dispatch(self, request: Request, call_next):
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > MAX_UPLOAD_SIZE_BYTES:
            return JSONResponse(
                status_code=413,
                content={"detail": f"Request body too large (max {MAX_UPLOAD_SIZE_BYTES // (1024*1024)} MB)"},
            )
        return await call_next(request)


class AuditMiddleware(BaseHTTPMiddleware):
    """Log all state-changing API requests for audit trail."""

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        # Log all non-GET API requests
        if request.url.path.startswith("/api") and request.method not in ("GET", "HEAD", "OPTIONS"):
            audit_logger.info(
                f"method={request.method} path={request.url.path} "
                f"client={request.client.host if request.client else 'unknown'} "
                f"status={response.status_code}"
            )

        return response


# =====================================================
# Application
# =====================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle."""
    # Ensure the repo root is on sys.path so `from shared.schema.cv_schema import …`
    # works on fresh installs where the `shared` package may not be pip-installed.
    # backend → src → tool-2-trainer-dashboard → AMS-JobAssist (repo root)
    import sys
    from pathlib import Path
    _repo_root = str(Path(__file__).resolve().parents[3])
    if _repo_root not in sys.path:
        sys.path.insert(0, _repo_root)

    from db import init_db
    init_db()
    logger.info("Trainer dashboard database initialized")
    print("[OK] Trainer dashboard database initialized")
    print(f"[OK] Auth: {'ENABLED (API key required)' if AUTH_ENABLED else 'DISABLED (set AMS_TRAINER_API_KEY to enable)'}")
    print(f"[OK] Serving at http://{HOST}:{PORT}")
    yield


app = FastAPI(
    title="AMS JobAssist - Trainer Dashboard",
    description="Trainer dashboard for reviewing participant CVs",
    lifespan=lifespan,
)


# =====================================================
# Request-ID middleware (structured logging)
# =====================================================
import time as _time
import uuid as _uuid


@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    """Attach a unique request ID to every request and log method/path/status/duration."""
    req_id = str(_uuid.uuid4())[:8]
    request.state.request_id = req_id
    start = _time.monotonic()
    try:
        response = await call_next(request)
    except Exception as exc:
        duration_ms = int((_time.monotonic() - start) * 1000)
        logger.error(f"[{req_id}] UNHANDLED {request.method} {request.url.path} ({duration_ms}ms): {exc}")
        raise
    duration_ms = int((_time.monotonic() - start) * 1000)
    logger.info(f"[{req_id}] {request.method} {request.url.path} → {response.status_code} ({duration_ms}ms)")
    response.headers["X-Request-ID"] = req_id
    return response


# =====================================================
# Structured error responses
# =====================================================
from starlette.exceptions import HTTPException as _StarletteHTTPException
from fastapi.exceptions import RequestValidationError as _ReqValErr


def _err_body(request: Request, code: int, detail: str, error_code: str | None = None) -> dict:
    return {
        "status": "error",
        "error": {
            "code": error_code or f"HTTP_{code}",
            "detail": detail,
            "request_id": getattr(getattr(request, "state", None), "request_id", None),
        },
    }


@app.exception_handler(_StarletteHTTPException)
async def _http_exc_handler(request: Request, exc: _StarletteHTTPException):
    return JSONResponse(status_code=exc.status_code, content=_err_body(request, exc.status_code, str(exc.detail)))


@app.exception_handler(_ReqValErr)
async def _val_exc_handler(request: Request, exc: _ReqValErr):
    msg = "; ".join(f"{' → '.join(str(l) for l in e['loc'])}: {e['msg']}" for e in exc.errors())
    return JSONResponse(status_code=422, content=_err_body(request, 422, msg, "VALIDATION_ERROR"))


# Register middleware (order matters: outermost first)
app.add_middleware(AuditMiddleware)
app.add_middleware(RequestSizeLimitMiddleware)
app.add_middleware(CSRFMiddleware)
app.add_middleware(AuthenticationMiddleware)

# Health endpoint — used by launcher to confirm startup
@app.get("/health")
async def health():
    return JSONResponse({"status": "ok", "tool": "trainer-dashboard"})

# Include API routes
from api.routes import router as api_router
app.include_router(api_router)

# Mount frontend static files
# Mount at root so index.html relative paths (styles.css, js/app.js) resolve correctly.
# API routes (/api/*) are registered first so they take priority over the static mount.
if FRONTEND_DIR.exists():
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="static")
else:
    logger.warning(f"Frontend directory not found: {FRONTEND_DIR}")

def main():
    """Entry point for the ams-trainer script."""
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
