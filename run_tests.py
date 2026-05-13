#!/usr/bin/env python
"""
Cross-tool test runner.

Runs Tool 1 and Tool 2 pytest suites in isolated subprocesses so the two
`tests/conftest.py` modules don't collide on pytest's plugin manager.

Usage:
    python run_tests.py            # both suites
    python run_tests.py tool1      # Tool 1 only
    python run_tests.py tool2      # Tool 2 only
    python run_tests.py -v         # both, verbose

Exit code is 0 iff all selected suites pass.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
SUITES = {
    "tool1": (REPO_ROOT / "tool-1-cv-maker" / "tests",
              ["--ignore=" + str(REPO_ROOT / "tool-1-cv-maker" / "tests" / "demo_test.py")]),
    "tool2": (REPO_ROOT / "tool-2-trainer-dashboard" / "tests", []),
}


def run_suite(name: str, extra_args: list[str]) -> int:
    path, ignores = SUITES[name]
    if not path.exists():
        print(f"[SKIP] {name}: {path} does not exist")
        return 0
    cmd = [sys.executable, "-m", "pytest", str(path), "-q", *ignores, *extra_args]
    print(f"\n[{name}] {' '.join(cmd)}")
    return subprocess.run(cmd, cwd=REPO_ROOT).returncode


def main(argv: list[str]) -> int:
    selected = []
    extra: list[str] = []
    for a in argv:
        if a in SUITES:
            selected.append(a)
        else:
            extra.append(a)
    if not selected:
        selected = list(SUITES.keys())
    rc = 0
    for name in selected:
        rc |= run_suite(name, extra)
    print("\n" + ("ALL SUITES PASSED" if rc == 0 else "FAILURES"))
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
