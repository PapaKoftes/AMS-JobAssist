"""
Pytest configuration for Tool 2 Trainer Dashboard tests

Provides:
- Isolated test database per session (temp file, not in-memory)
- Per-test session rollback for isolation
- FastAPI test client with dependency override
"""

import sys
import os
from pathlib import Path

# Add backend to path — same as app.py does
backend_path = Path(__file__).parent.parent / "src" / "backend"
sys.path.insert(0, str(backend_path))

# Change working directory to backend for proper imports
os.chdir(str(backend_path))
