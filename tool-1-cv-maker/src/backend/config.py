"""
AMS JobAssist CV Maker - Configuration

All settings can be overridden via environment variables:
  AMS_TOOL1_HOST, AMS_TOOL1_PORT, AMS_DEBUG, etc.
"""

import os
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
# AMS_DATA_DIR can relocate the data dir (e.g. onto an OS-encrypted volume).
# WARNING (DSGVO): the SQLite DB holds plaintext participant PII. Do NOT point
# this at a network share or any location that leaves the local, encrypted disk —
# doing so breaks the "data never leaves this machine" guarantee. If you must use
# a shared/backed-up location, it MUST be encrypted at rest (BitLocker/LUKS).
_custom_data = os.environ.get("AMS_DATA_DIR", "")
DB_DIR = Path(_custom_data) if _custom_data else BASE_DIR / "data"
LOG_DIR = BASE_DIR / "logs"
FRONTEND_DIR = BASE_DIR / "src" / "frontend"

# Data retention — purge OLD sessions (incomplete AND completed) older than this.
# DSGVO Art. 5(1)(e) storage limitation. Default: 365 days (covers the AMS course
# cycle + a reasonable trainer-review window). Set AMS_DATA_RETENTION_DAYS=0 to
# disable automatic purging (you then take on the deletion obligation manually).
DATA_RETENTION_DAYS = int(os.environ.get("AMS_DATA_RETENTION_DAYS", "365"))

# Access control for administrative / data-subject endpoints.
# Tool 1 is a single-user localhost tool, so sensitive endpoints (full-DB backup,
# data-subject export/erasure) are gated by: loopback client OR a matching API key.
# Set AMS_TOOL1_API_KEY to allow non-loopback (LAN) admin access; without it,
# those endpoints are reachable ONLY from the local machine.
API_KEY = os.environ.get("AMS_TOOL1_API_KEY", "")

# Database
DATABASE_URL = os.environ.get(
    "AMS_TOOL1_DB_URL",
    f"sqlite:///{DB_DIR}/ams_jobassist.db",
)
DB_ECHO = os.environ.get("AMS_DB_ECHO", "").lower() in ("1", "true", "yes")

# Server — configurable via env so ports don't conflict
HOST = os.environ.get("AMS_TOOL1_HOST", "127.0.0.1")
PORT = int(os.environ.get("AMS_TOOL1_PORT", "8000"))
DEBUG = os.environ.get("AMS_DEBUG", "").lower() in ("1", "true", "yes")

# Feature Flags
USE_OLLAMA = os.environ.get("AMS_USE_OLLAMA", "true").lower() in ("1", "true", "yes")
OLLAMA_HOST = os.environ.get("AMS_OLLAMA_HOST", "http://127.0.0.1:11434")
FALLBACK_RULES_ENABLED = True  # Fallback if Ollama unavailable

# Upload limits
MAX_UPLOAD_SIZE_MB = int(os.environ.get("AMS_MAX_UPLOAD_MB", "50"))


def _is_loopback_host(h: str) -> bool:
    h = (h or "").strip().lower()
    return h.startswith("127.") or h in ("localhost", "::1", "")


# Fail-closed: never bind a PII service to a non-loopback interface without a key.
# This prevents the "someone set HOST=0.0.0.0 to reach it from another PC" footgun
# from silently exposing the whole database to the LAN. Override intentionally by
# setting AMS_TOOL1_API_KEY (then admin endpoints require that key from remote).
if not _is_loopback_host(HOST) and not API_KEY:
    raise RuntimeError(
        f"AMS_TOOL1_HOST={HOST!r} is non-loopback but AMS_TOOL1_API_KEY is unset. "
        "Refusing to expose participant PII to the network without an API key. "
        "Set AMS_TOOL1_API_KEY, or bind to 127.0.0.1."
    )

# Paths - create if needed
DB_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)
