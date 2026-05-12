"""
CV Mapper — normalise Tool 1 JSON exports into the flat dict that Tool 2's
database layer expects.

Since Tool 1 now exports canonical CVDocument JSON by default (schema_version "1.0"),
the primary path is: run migration → validate schema_version → return flat dict.

Legacy shapes are still handled for backward compatibility:

  Shape A (legacy default export)
  ─────────────────────────────────
  {
    "metadata": { "user_id": ..., "session_id": ..., "interview_path": ... },
    "quality_metrics": { "overall_quality": ..., "ready_for_export": ...,
                         "language_output_primary": ..., "language_output_secondary": ... },
    "content": { "background": [...], "experience": [...], ... }
  }

  Shape B (raw CVData export, export_raw_cvdata())
  ──────────────────────────────────────────────────
  {
    "metadata": { ... },
    "cvdata": { "user_id": ..., "session_id": ..., "interview_path": ...,
                "overall_quality": ..., "ready_for_export": ..., ... }
  }

  Shape C (legacy flat, no nesting)
  ───────────────────────────────────
  { "user_id": ..., "interview_path": ..., "overall_quality": ..., ... }

The mapper normalises all three shapes into Shape C so that
``_import_single_cv`` can call ``cv_dict.get("user_id")`` etc. without
caring about the original layout.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# Try to load the shared migration module.  It lives outside the tool-2 tree
# but is on sys.path when the whole repo is installed / run from root.
_REPO_ROOT = Path(__file__).resolve().parents[4]  # …/tool-2/src/backend/services → repo root
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

try:
    from shared.schema.migration import migrate as _migrate_schema, CURRENT_VERSION
    _HAS_MIGRATION = True
except ImportError:
    _HAS_MIGRATION = False
    CURRENT_VERSION = "1.0"
    logger.debug("shared.schema.migration not available; skipping version migration")


def normalise(raw: dict[str, Any]) -> dict[str, Any]:
    """
    Return a flat dict compatible with Tool 2's import logic.

    Primary path (Tool 1 ≥ current): the dict already has ``schema_version``
    and ``user_id`` at the root — run migration and return as-is.

    Legacy paths are still handled for backward compatibility with older exports.

    Raises ``ValueError`` if the payload cannot be mapped to a usable dict.
    """
    if not isinstance(raw, dict):
        raise ValueError("CV payload must be a JSON object (dict)")

    # ── Primary path: canonical CVDocument (schema_version present) ──────────
    if "schema_version" in raw:
        logger.debug(f"cv_mapper: canonical export (schema_version={raw['schema_version']})")
        if _HAS_MIGRATION:
            return _migrate_schema(raw)
        return dict(raw)

    # ── Legacy Shape B: has a top-level "cvdata" key ─────────────────────────
    if "cvdata" in raw and isinstance(raw["cvdata"], dict):
        logger.debug("cv_mapper: detected legacy Shape B (raw CVData export)")
        if _HAS_MIGRATION:
            return _migrate_schema(raw)
        flat = dict(raw["cvdata"])
        for k, v in raw.get("metadata", {}).items():
            flat.setdefault(k, v)
        return flat

    # ── Legacy Shape A: has "metadata" + "quality_metrics" + "content" ───────
    if "metadata" in raw and "quality_metrics" in raw:
        logger.debug("cv_mapper: detected legacy Shape A (nested export)")
        if _HAS_MIGRATION:
            return _migrate_schema(raw)
        meta: dict = raw.get("metadata", {})
        quality: dict = raw.get("quality_metrics", {})
        content: dict = raw.get("content", {})
        flat: dict[str, Any] = {}
        flat.update(meta)
        flat.update(quality)
        flat.update(content)
        return flat

    # ── Legacy Shape C: already flat ─────────────────────────────────────────
    if "user_id" in raw:
        logger.debug("cv_mapper: detected legacy Shape C (flat dict)")
        if _HAS_MIGRATION:
            return _migrate_schema(raw)
        return dict(raw)

    raise ValueError(
        "Unrecognised CV export format: expected 'user_id' at root, a "
        "'schema_version' field, or a legacy 'metadata'/'cvdata' structure."
    )
