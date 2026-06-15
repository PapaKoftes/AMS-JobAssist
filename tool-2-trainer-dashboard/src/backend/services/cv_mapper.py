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

# The canonical CVDocument Pydantic model is the cross-tool CONTRACT. We now
# validate every canonical import against it so malformed data is rejected at
# the boundary instead of silently stored.
try:
    from shared.schema.cv_schema import CVDocument as _CVDocument
    _HAS_SCHEMA = True
except ImportError:
    _HAS_SCHEMA = False
    logger.debug("shared.schema.cv_schema not available; canonical validation disabled")


def _validate_canonical(raw: dict) -> None:
    """
    Enforce the cross-tool contract: a canonical export (schema_version present)
    must satisfy the CVDocument Pydantic model. Raises ValueError on a structural
    mismatch so the import is rejected with a clear message rather than corrupting
    the trainer DB. No-op if the schema module isn't importable.
    """
    if not _HAS_SCHEMA:
        return
    try:
        # Pydantic v2 model_validate; tolerant of extra keys (model ignores them).
        _CVDocument.model_validate(raw)
    except Exception as exc:
        # Keep the message short — the full validation error can be huge.
        msg = str(exc).splitlines()[0] if str(exc) else exc.__class__.__name__
        raise ValueError(
            f"Canonical CV failed schema validation (cross-tool contract): {msg}"
        ) from exc


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
        migrated = _migrate_schema(raw) if _HAS_MIGRATION else dict(raw)
        # Enforce the cross-tool contract on the (migrated) canonical document.
        _validate_canonical(migrated)
        return migrated

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


# ── Canonical CVDocument → Tool 1 CVData dict ────────────────────────────────
# Tool 1 exports the canonical CVDocument (basics / experience / education /
# skills / custom_sections). Tool 1's PDF/DOCX exporters, however, render from
# the legacy CVData shape (identity + background/experience/skills/motivation/
# training/projects). Feeding canonical JSON straight into CVData.from_dict
# silently drops almost everything (name + 4 of 5 sections). This mapper
# rebuilds a faithful CVData-shaped dict so bulk PDF/DOCX export renders the
# full CV.

def _sec(category: str, entry: dict) -> dict:
    return {
        "category": category,
        "german": entry.get("german", "") or "",
        "english": entry.get("english", "") or "",
        "native": entry.get("native", "") or "",
        "detected_skills": entry.get("detected_skills", []) or [],
        "quality_score": entry.get("quality_score", 0.0) or 0.0,
    }


def canonical_to_cvdata_dict(canon: dict) -> dict:
    """Convert a canonical CVDocument dict into the flat CVData dict that Tool 1's
    CVData.from_dict expects. Returns the input unchanged if it is not canonical."""
    if not isinstance(canon, dict) or "schema_version" not in canon:
        return canon  # not canonical — leave as-is for legacy handling

    basics = canon.get("basics") or {}

    experience = [_sec("experience", e) for e in (canon.get("experience") or []) if not e.get("hidden")]
    # Canonical folds background + training into education; route them to background.
    background = [_sec("background", e) for e in (canon.get("education") or []) if not e.get("hidden")]
    # Canonical custom_sections carry a heading ("Motivation"/"Projekte"/…). Split
    # them back into the right CVData buckets instead of collapsing everything into
    # motivation (which lost the projects/training distinction on the trainer side).
    motivation: list[dict] = []
    projects: list[dict] = []
    training: list[dict] = []
    for e in (canon.get("custom_sections") or []):
        if e.get("hidden"):
            continue
        heading = (e.get("heading") or "").lower()
        if "projekt" in heading or "project" in heading:
            projects.append(_sec("projects", e))
        elif "weiterbild" in heading or "training" in heading or "kurs" in heading or "course" in heading:
            training.append(_sec("training", e))
        else:
            motivation.append(_sec("motivation", e))

    # Skills: canonical SkillGroups, else synthesise one section from all_skills.
    skills: list[dict] = []
    for grp in (canon.get("skills") or []):
        items = grp.get("items") or grp.get("skills") or []
        text = ", ".join(items) if items else (grp.get("german") or grp.get("name") or "")
        if text:
            skills.append({"category": "skills", "german": text, "english": text, "native": ""})
    all_skills = canon.get("all_skills") or []
    if not skills and all_skills:
        text = ", ".join(all_skills)
        skills.append({"category": "skills", "german": text, "english": text, "native": ""})

    return {
        "session_id": canon.get("session_id", 0),
        "user_id": canon.get("user_id", ""),
        "interview_path": canon.get("interview_path", "other"),
        "language_input": canon.get("language_input", "de"),
        "language_output_primary": canon.get("language_output_primary", "de"),
        "identity": {
            "full_name": basics.get("full_name", "") or "",
            "location": basics.get("location", "") or "",
            "contact_email": basics.get("email"),
            "contact_phone": basics.get("phone"),
            "date_of_birth": basics.get("date_of_birth"),
            "nationality": basics.get("nationality"),
            "photo": basics.get("photo"),
        },
        "background": background,
        "experience": experience,
        "skills": skills,
        "motivation": motivation,
        "training": training,
        "projects": projects,
        "all_skills": all_skills,
        # Carry language proficiencies (CEFR) and the target job — without these the
        # trainer's re-exported PDF dropped the SPRACHEN section and the Zielberuf.
        "languages": [
            {"language": (l.get("language") or ""), "code": (l.get("code") or ""),
             "level": (l.get("level") or "")}
            for l in (canon.get("languages") or [])
        ],
        "target_job": canon.get("target_job", "") or "",
        "overall_quality": canon.get("overall_quality", 0.0) or 0.0,
        # Fail closed: a canonical doc missing the flag must NOT read as export-ready
        # (it would tell the trainer an incomplete CV is finished).
        "ready_for_export": canon.get("ready_for_export", False),
    }
