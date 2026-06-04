"""
AMS JobAssist Trainer Dashboard - Configuration

All settings can be overridden via environment variables:
  AMS_TOOL2_HOST, AMS_TOOL2_PORT, AMS_DEBUG, etc.
"""

import os
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
# AMS_DATA_DIR lets IT teams point data/DB to a backed-up network location
_custom_data = os.environ.get("AMS_DATA_DIR", "")
DB_DIR = Path(_custom_data) if _custom_data else BASE_DIR / "data"
LOG_DIR = BASE_DIR / "logs"
FRONTEND_DIR = BASE_DIR / "frontend"

# Data retention — delete participant records older than this many days (0 = keep forever)
DATA_RETENTION_DAYS = int(os.environ.get("AMS_DATA_RETENTION_DAYS", "90"))

# If frontend is at src/frontend (development layout), check both paths
if not FRONTEND_DIR.exists():
    FRONTEND_DIR = BASE_DIR / "src" / "frontend"

# Database (separate from Tool 1)
DATABASE_URL = os.environ.get(
    "AMS_TOOL2_DB_URL",
    f"sqlite:///{DB_DIR}/ams_trainer.db",
)
DB_ECHO = os.environ.get("AMS_DB_ECHO", "").lower() in ("1", "true", "yes")

# Server — configurable via env so ports don't conflict
HOST = os.environ.get("AMS_TOOL2_HOST", "127.0.0.1")
PORT = int(os.environ.get("AMS_TOOL2_PORT", "8001"))
DEBUG = os.environ.get("AMS_DEBUG", "").lower() in ("1", "true", "yes")

# Upload limits
MAX_UPLOAD_SIZE_MB = int(os.environ.get("AMS_MAX_UPLOAD_MB", "50"))
MAX_UPLOAD_SIZE_BYTES = MAX_UPLOAD_SIZE_MB * 1024 * 1024

# Authentication
# Set AMS_TRAINER_API_KEY to a strong random string (min 32 chars) for networked use.
# FAIL-CLOSED: when unset, the dashboard does NOT run wide open — the API is served
# only to loopback clients (see AuthenticationMiddleware), and binding to a
# non-loopback interface without a key is refused at startup below.
import warnings as _warnings
API_KEY = os.environ.get("AMS_TRAINER_API_KEY", "")
AUTH_ENABLED = bool(API_KEY)


def _is_loopback_host(h: str) -> bool:
    h = (h or "").strip().lower()
    return h.startswith("127.") or h in ("localhost", "::1", "")


if not AUTH_ENABLED:
    if not _is_loopback_host(HOST):
        raise RuntimeError(
            f"AMS_TOOL2_HOST={HOST!r} is non-loopback but AMS_TRAINER_API_KEY is unset. "
            "Refusing to expose aggregated participant PII to the network without an API key. "
            "Set AMS_TRAINER_API_KEY, or bind to 127.0.0.1."
        )
    _warnings.warn(
        "AMS_TRAINER_API_KEY is not set — trainer dashboard API is restricted to the "
        "local machine only. Set the variable to allow authenticated remote access.",
        stacklevel=2,
    )

# Paths - create if needed
DB_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)
FRONTEND_DIR.mkdir(parents=True, exist_ok=True)
