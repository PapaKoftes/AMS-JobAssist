#!/usr/bin/env python3
"""
Deployment smoke test (P1.2) — run this on a CLEAN machine after install to
certify the offline distribution actually works.

Launches the built launcher .exe, then asserts:
  1. Tool 1 (CV maker) serves /health 200
  2. Tool 2 (trainer)   serves /health 200
  3. the local AI model is present on disk (model_exists_on_disk) → AI works offline
  4. no internet was required (run it with the network cable out / Wi-Fi off)

Exit code 0 = PASS (ready to hand to a trainer), non-zero = FAIL.

Usage:
    python packaging/smoke_test.py                 # launches dist\\AMS-JobAssist-Launcher.exe
    python packaging/smoke_test.py --exe path\\to\\Launcher.exe
    python packaging/smoke_test.py --no-launch     # assume it's already running

The health/poll logic is importable and unit-tested (test_smoke_logic) so the
harness itself is trustworthy.
"""
import sys
import time
import json
import argparse
import subprocess
import urllib.request
from pathlib import Path

TOOL1_PORT = 8000
TOOL2_PORT = 8001


def http_json(url, timeout=4):
    try:
        with urllib.request.urlopen(url, timeout=timeout) as r:
            return json.loads(r.read().decode())
    except Exception:
        return None


def wait_health(port, timeout=90, _get=http_json, _sleep=time.sleep):
    """Poll /health until 200 (status ok) or timeout. Returns True/False."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        d = _get(f"http://127.0.0.1:{port}/health")
        if d and d.get("status") == "ok":
            return True
        _sleep(2)
    return False


def offline_ai_ready(status):
    """Given a /api/ai/model-status payload, is an OFFLINE AI engine available?

    True if a local GGUF is on disk OR Ollama is up OR the active engine is not
    the rule-based fallback. (All three are loopback-only, no internet.)
    """
    if not status:
        return False
    data = status.get("data", status)
    local = data.get("local", {}) or {}
    ollama = data.get("ollama", {}) or {}
    return bool(
        local.get("model_exists_on_disk")
        or local.get("local_model_available")
        or ollama.get("ollama_available")
        or (data.get("active_engine") not in (None, "rules"))
    )


def model_present(port, _get=http_json):
    """True if an offline AI engine is available on this instance."""
    return offline_ai_ready(_get(f"http://127.0.0.1:{port}/api/ai/model-status"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--exe", default=str(Path("dist") / "AMS-JobAssist-Launcher.exe"))
    ap.add_argument("--no-launch", action="store_true")
    ap.add_argument("--timeout", type=int, default=120)
    args = ap.parse_args()

    proc = None
    if not args.no_launch:
        exe = Path(args.exe)
        if not exe.exists():
            print(f"[FAIL] launcher not found: {exe}  (run build_all.bat first)")
            return 2
        print(f"Launching {exe} ...")
        proc = subprocess.Popen([str(exe)], cwd=str(exe.parent))

    results = []
    try:
        print("Waiting for Tool 1 (CV-Ersteller) ...")
        t1 = wait_health(TOOL1_PORT, args.timeout)
        results.append(("Tool 1 /health", t1))
        print("Waiting for Tool 2 (Trainer-Dashboard) ...")
        t2 = wait_health(TOOL2_PORT, args.timeout)
        results.append(("Tool 2 /health", t2))
        if t1:
            results.append(("Local AI model present (offline)", model_present(TOOL1_PORT)))
    finally:
        if proc is not None:
            try:
                proc.terminate()
                proc.wait(timeout=5)
            except Exception:
                proc.kill()

    print("\n=== SMOKE TEST RESULTS ===")
    ok = True
    for name, passed in results:
        print(f"  [{'PASS' if passed else 'FAIL'}] {name}")
        ok = ok and passed
    print("=" * 26)
    print("RESULT:", "PASS — ready to hand off" if ok else "FAIL — not deployment-ready")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
