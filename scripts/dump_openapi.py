#!/usr/bin/env python3
"""
Regenerate the authoritative API surface from the live FastAPI apps.

The hand-maintained API_DOCUMENTATION.md drifts (it documented endpoints that
don't exist and missed ~12 that do). This script dumps the REAL OpenAPI spec
from both apps so the route list, methods, and request/response schemas are
always generated from code, never hand-written.

Usage:
    python scripts/dump_openapi.py

Writes:
    docs/openapi-tool1.json
    docs/openapi-tool2.json
    docs/API_ENDPOINTS.generated.md   (a flat method+path+summary table)

This does NOT require a running server — it imports the app objects and calls
app.openapi() directly. Offline mode is enabled by the apps on import; that's
fine (no network needed).
"""
import json
import os
import sys
from pathlib import Path

# Windows consoles default to cp1252 and raise UnicodeEncodeError on the non-ASCII
# characters printed below (e.g. the "→" arrow), which crashed the script after it
# had already written its output files. Force UTF-8 so it runs everywhere.
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

REPO = Path(__file__).resolve().parents[1]
DOCS = REPO / "docs"
DOCS.mkdir(exist_ok=True)


_BASELINE_MODULES = set(sys.modules)


def _load_app(backend_dir: Path):
    """
    Import an `app` object from a backend dir. Both tools share top-level module
    names (`config`, `app`, `db`, `models`, …), so we purge every module imported
    since baseline before each load to avoid cross-tool contamination.
    """
    for name in list(sys.modules):
        if name not in _BASELINE_MODULES:
            del sys.modules[name]
    # Reset sys.path to baseline + this backend.
    while sys.path and sys.path[0] in (str(REPO),) or (sys.path and Path(sys.path[0]).name == "backend"):
        sys.path.pop(0)
    sys.path.insert(0, str(REPO))
    sys.path.insert(0, str(backend_dir))
    os.environ.setdefault("AMS_ENFORCE_OFFLINE", "1")
    import importlib
    mod = importlib.import_module("app")
    return mod.app


def _flatten(spec: dict) -> list[tuple[str, str, str]]:
    rows = []
    for path, methods in sorted(spec.get("paths", {}).items()):
        for method, op in methods.items():
            if method.lower() in ("get", "post", "put", "patch", "delete"):
                summary = op.get("summary") or (op.get("description", "").splitlines()[0] if op.get("description") else "")
                rows.append((method.upper(), path, summary))
    return rows


def main():
    targets = [
        ("tool1", REPO / "tool-1-cv-maker" / "src" / "backend"),
        ("tool2", REPO / "tool-2-trainer-dashboard" / "src" / "backend"),
    ]
    all_rows = {}
    for name, backend in targets:
        try:
            app = _load_app(backend)
            spec = app.openapi()
        except Exception as exc:
            print(f"[WARN] could not load {name}: {exc}")
            continue
        (DOCS / f"openapi-{name}.json").write_text(
            json.dumps(spec, indent=2, ensure_ascii=False), encoding="utf-8")
        all_rows[name] = _flatten(spec)
        print(f"[OK] {name}: {len(all_rows[name])} endpoints → docs/openapi-{name}.json")

    # Write a flat, human-readable endpoint table generated from code.
    lines = ["# API Endpoints (generated from OpenAPI — do not hand-edit)",
             "",
             "> Regenerate with `python scripts/dump_openapi.py`. This is the",
             "> authoritative route list; the prose in `API_DOCUMENTATION.md` is",
             "> a guide that can drift.",
             ""]
    for name, _ in targets:
        rows = all_rows.get(name, [])
        lines.append(f"## {name} ({len(rows)} endpoints)")
        lines.append("")
        lines.append("| Method | Path | Summary |")
        lines.append("|---|---|---|")
        for method, path, summary in rows:
            lines.append(f"| {method} | `{path}` | {summary} |")
        lines.append("")
    (DOCS / "API_ENDPOINTS.generated.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"[OK] wrote docs/API_ENDPOINTS.generated.md")


if __name__ == "__main__":
    main()
