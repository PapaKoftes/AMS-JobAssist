#!/usr/bin/env python3
"""
Build the tester hand-off ZIP — the ONE artifact you send to other people.

Includes exactly what a tester needs (source, the bundled 3B model, AMS-Start.bat,
docs) and excludes everything that must not ship:
  - dist/ + build/        → the broken frozen .exe (known crash) — a trap if included
  - *.db, logs, exports   → local test databases contain participant-style PII
  - .git, caches, eval JSONs, build debris

Usage:  python make_tester_package.py
Output: AMS-JobAssist-Tester.zip next to this script (~2 GB, model included).
"""
from __future__ import annotations

import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "AMS-JobAssist-Tester.zip"

# Top-level items to ship (dirs are walked recursively, then filtered).
INCLUDE = [
    "shared",
    "tool-1-cv-maker",
    "tool-2-trainer-dashboard",
    "launcher.py",
    "AMS-Start.bat",
    "requirements.txt",
    "FOR_MARKO.md",
    "README.md",
]

# Path fragments that must never ship (PII, broken builds, caches, debris).
EXCLUDE_PARTS = {
    ".git", "__pycache__", ".pytest_cache", "dist", "build", "node_modules",
    "logs", "exports", "backups", ".claude",
}
EXCLUDE_SUFFIXES = {".db", ".db-wal", ".db-shm", ".pyc", ".part", ".zip"}
EXCLUDE_NAMES = {
    "LAST_ERROR.txt", "buildlog.txt", "TEST_REPORT.html",
    # The 3B is the shipped default and auto-wins whenever present; the 1.5B
    # would be 1.1 GB of dead weight in the package.
    "qwen2.5-1.5b-instruct-q4_k_m.gguf",
}


def _excluded(rel: Path) -> bool:
    if any(p in EXCLUDE_PARTS for p in rel.parts):
        return True
    if rel.suffix.lower() in EXCLUDE_SUFFIXES:
        return True
    if rel.name in EXCLUDE_NAMES:
        return True
    return False


def main() -> int:
    model = ROOT / "tool-1-cv-maker" / "data" / "models" / "qwen2.5-3b-instruct-q4_k_m.gguf"
    if not model.exists():
        print("[FAIL] 3B model missing at", model)
        print("       The package would ship WITHOUT AI. Run download_3b_model.bat first.")
        return 1

    if OUT.exists():
        OUT.unlink()

    n = 0
    # ZIP_STORED for speed/size sanity: the GGUF is already compressed weights;
    # deflating 1.9 GB would take minutes for ~1% gain.
    with zipfile.ZipFile(OUT, "w", zipfile.ZIP_STORED) as z:
        for item in INCLUDE:
            p = ROOT / item
            if not p.exists():
                print(f"[FAIL] required item missing: {item}")
                return 1
            files = [p] if p.is_file() else sorted(f for f in p.rglob("*") if f.is_file())
            for f in files:
                rel = f.relative_to(ROOT)
                if _excluded(rel):
                    continue
                z.write(f, Path("AMS-JobAssist") / rel)
                n += 1

    size_gb = OUT.stat().st_size / 1e9
    print(f"[OK] {OUT.name}: {n} files, {size_gb:.2f} GB")
    print("     Send this ZIP. Tester: unzip -> install Python once -> AMS-Start.bat")
    # Final safety: assert the model made it in and no .db leaked.
    with zipfile.ZipFile(OUT) as z:
        names = z.namelist()
        assert any(name.endswith(".gguf") for name in names), "model not in zip!"
        leaked = [name for name in names if name.endswith(".db")]
        assert not leaked, f"DB files leaked: {leaked}"
    print("[OK] verified: model included, no databases leaked.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
