"""
CV Schema Migration — version-aware upgrade of serialised CV dicts.

Usage
-----
    from shared.schema.migration import migrate

    raw = json.load(f)
    upgraded = migrate(raw)   # idempotent if already current version
    doc = CVDocument(**upgraded)

Versioning convention
---------------------
Every ``CVDocument`` written by current code carries ``schema_version = "1.0"``.
If a future version introduces breaking changes, add a new ``_migrate_X_to_Y``
function and extend the ``MIGRATIONS`` registry below.

All migration functions are pure: they return a new dict and do not mutate
their input.
"""

from __future__ import annotations

import copy
import logging
from typing import Any

logger = logging.getLogger(__name__)

CURRENT_VERSION = "1.0"


# ── Migration registry ────────────────────────────────────────────────────────
# Maps (from_version, to_version) → migration function.
# Functions receive a full cv dict and return an upgraded copy.

def _migrate_legacy_to_1_0(raw: dict[str, Any]) -> dict[str, Any]:
    """
    Upgrade pre-schema (no schema_version) or legacy Tool 1 exports to 1.0.

    Handles:
    - Shape A: {metadata, quality_metrics, content}
    - Shape B: {metadata, cvdata}
    - Shape C: flat dict with user_id at root

    After this function, the dict has ``schema_version = "1.0"`` and all
    CVDocument fields at the top level (no nesting).
    """
    out = copy.deepcopy(raw)

    # ── Shape B: {metadata, cvdata} ──────────────────────────────────────────
    if "cvdata" in out and isinstance(out["cvdata"], dict):
        cvdata = out.pop("cvdata")
        meta = out.pop("metadata", {})
        out.update(cvdata)
        for k, v in meta.items():
            out.setdefault(k, v)

    # ── Shape A: {metadata, quality_metrics, content} ────────────────────────
    elif "quality_metrics" in out or "content" in out:
        meta = out.pop("metadata", {})
        quality = out.pop("quality_metrics", {})
        content = out.pop("content", {})
        out.update(meta)
        out.update(quality)
        out.update(content)

    # Ensure top-level fields that CVDocument requires
    out.setdefault("schema_version", CURRENT_VERSION)
    out.setdefault("user_id", out.pop("user_id", "unknown"))
    out.setdefault("session_id", str(out.get("session_id", "")))

    # Rename legacy field if present
    if "language_input" not in out and "language" in out:
        out["language_input"] = out.pop("language")

    # Stamp version
    out["schema_version"] = CURRENT_VERSION
    return out


MIGRATIONS: dict[tuple[str, str], Any] = {
    ("legacy", "1.0"): _migrate_legacy_to_1_0,
}


# ── Public API ────────────────────────────────────────────────────────────────

def detect_version(raw: dict[str, Any]) -> str:
    """
    Detect the schema version of a raw CV dict.

    Returns "legacy" if no ``schema_version`` key is present.
    """
    return raw.get("schema_version", "legacy")


def migrate(raw: dict[str, Any]) -> dict[str, Any]:
    """
    Upgrade ``raw`` to the current schema version.

    Idempotent: if ``raw`` is already at ``CURRENT_VERSION`` it is returned
    unchanged (a shallow copy is still returned so callers can mutate freely).

    Args:
        raw: Deserialised CV dict (from JSON.loads or similar).

    Returns:
        Upgraded dict ready to be passed to ``CVDocument(**result)``.

    Raises:
        ValueError: If no migration path exists for the detected version.
    """
    if not isinstance(raw, dict):
        raise ValueError("CV payload must be a dict")

    version = detect_version(raw)

    if version == CURRENT_VERSION:
        logger.debug(f"cv already at schema version {CURRENT_VERSION}; no migration needed")
        return dict(raw)

    # Walk the migration chain
    path = _resolve_path(version, CURRENT_VERSION)
    if path is None:
        raise ValueError(
            f"No migration path from schema version '{version}' to '{CURRENT_VERSION}'. "
            f"Known migrations: {list(MIGRATIONS.keys())}"
        )

    result = raw
    for (from_v, to_v) in path:
        fn = MIGRATIONS[(from_v, to_v)]
        logger.info(f"Migrating CV schema: {from_v} → {to_v}")
        result = fn(result)

    return result


def _resolve_path(
    from_version: str, to_version: str
) -> list[tuple[str, str]] | None:
    """Return the ordered list of migration steps needed, or None if unreachable."""
    # Simple BFS — the migration graph is tiny in practice
    from collections import deque

    queue: deque[tuple[str, list]] = deque([(from_version, [])])
    visited: set[str] = {from_version}

    while queue:
        current, path = queue.popleft()
        if current == to_version:
            return path
        for (src, dst) in MIGRATIONS:
            if src == current and dst not in visited:
                visited.add(dst)
                queue.append((dst, path + [(src, dst)]))

    return None
