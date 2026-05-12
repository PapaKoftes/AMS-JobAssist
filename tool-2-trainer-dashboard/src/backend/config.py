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
DATA_RETENTION_DAYS = int(os.environ.get("AMS_DATA_RETENTION_DAYS", "0"))

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
# REQUIRED in production: set AMS_TRAINER_API_KEY to a strong random string (min 32 chars).
# Without it the dashboard is accessible to anyone on the network — acceptable only for
# single-machine offline use.
import warnings as _warnings
API_KEY = os.environ.get("AMS_TRAINER_API_KEY", "")
AUTH_ENABLED = bool(API_KEY)
if not AUTH_ENABLED:
    _warnings.warn(
        "AMS_TRAINER_API_KEY is not set — trainer dashboard has no authentication. "
        "Set the variable before deploying in a shared environment.",
        stacklevel=2,
    )

# Paths - create if needed
DB_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)
FRONTEND_DIR.mkdir(parents=True, exist_ok=True)
