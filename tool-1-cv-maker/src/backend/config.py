"""
AMS JobAssist CV Maker - Configuration

All settings can be overridden via environment variables:
  AMS_TOOL1_HOST, AMS_TOOL1_PORT, AMS_DEBUG, etc.
"""

import os
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
# AMS_DATA_DIR lets IT teams point data/DB to a backed-up network location
_custom_data = os.environ.get("AMS_DATA_DIR", "")
DB_DIR = Path(_custom_data) if _custom_data else BASE_DIR / "data"
LOG_DIR = BASE_DIR / "logs"
FRONTEND_DIR = BASE_DIR / "src" / "frontend"

# Data retention — delete sessions older than this many days (0 = keep forever)
DATA_RETENTION_DAYS = int(os.environ.get("AMS_DATA_RETENTION_DAYS", "0"))

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

# Paths - create if needed
DB_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)
