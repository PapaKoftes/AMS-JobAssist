#!/usr/bin/env python3
"""
AMS-JobAssist - DEMO launcher (for sitting down with a reviewer).

Why this exists separately from launcher.py:
  The local AI model takes ~60-90s to load the first time. If you open the app
  and start typing immediately, the first answer hangs while the model loads -
  a terrible look in a live demo. This launcher starts BOTH tools, then WAITS
  and pre-warms the model, and only prints "READY" + opens the browser once the
  AI is actually loaded. So by the time you start the demo, everything is warm.

Usage:
    python start_demo.py            # start fresh-warmed demo
    python start_demo.py --reset    # wipe previous demo data first (clean slate)
    python start_demo.py --no-browser

Stop with Ctrl+C (both tools shut down cleanly).
"""
import os
import sys
import time

# Windows consoles default to cp1252 and CRASH on emoji/Unicode. Force UTF-8 with
# replacement so a stray glyph can never kill the launcher mid-demo.
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import json
import shutil
import signal
import subprocess
import urllib.request
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DEMO_DATA = ROOT / "demo-data"
TOOL1_BACKEND = ROOT / "tool-1-cv-maker" / "src" / "backend"
TOOL2_BACKEND = ROOT / "tool-2-trainer-dashboard" / "src" / "backend"
TOOL1_PORT = int(os.environ.get("AMS_TOOL1_PORT", "8000"))
TOOL2_PORT = int(os.environ.get("AMS_TOOL2_PORT", "8001"))
WARM_TIMEOUT = int(os.environ.get("AMS_DEMO_WARM_TIMEOUT", "240"))  # seconds


def _get(url, timeout=5):
    try:
        with urllib.request.urlopen(url, timeout=timeout) as r:
            return json.loads(r.read().decode())
    except Exception:
        return None


def _post(url, body, timeout=180):
    """POST JSON; returns parsed response or None. Used to PRIME first inference."""
    try:
        req = urllib.request.Request(
            url, data=json.dumps(body).encode(), method="POST",
            headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode())
    except Exception:
        return None


def _wait_health(port, name, timeout=40):
    deadline = time.time() + timeout
    while time.time() < deadline:
        if _get(f"http://127.0.0.1:{port}/health"):
            print(f"  [OK] {name} is serving on http://127.0.0.1:{port}")
            return True
        time.sleep(1)
    print(f"  [!!] {name} did not come up on port {port} - check the log.")
    return False


def _model_ready(port):
    data = _get(f"http://127.0.0.1:{port}/api/ai/model-status")
    if not data:
        return None  # endpoint not up yet
    d = data.get("data", data)
    local = d.get("local", d)
    return bool(local.get("local_model_available"))


def _model_present(port):
    data = _get(f"http://127.0.0.1:{port}/api/ai/model-status")
    if not data:
        return None
    d = data.get("data", data)
    local = d.get("local", d)
    return bool(local.get("model_exists_on_disk"))


def _start_tool(backend: Path, port: int, name: str, env: dict, log: Path):
    log.parent.mkdir(parents=True, exist_ok=True)
    fh = open(log, "w", encoding="utf-8")
    print(f"Starting {name} ...")
    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app:app",
         "--host", "127.0.0.1", "--port", str(port), "--log-level", "warning"],
        cwd=str(backend), env=env, stdout=fh, stderr=subprocess.STDOUT,
    )
    return proc, fh


def main():
    reset = "--reset" in sys.argv
    open_browser = "--no-browser" not in sys.argv

    if reset and DEMO_DATA.exists():
        print("Resetting demo data (clean slate) ...")
        shutil.rmtree(DEMO_DATA, ignore_errors=True)

    base_env = dict(os.environ)
    base_env["AMS_WARM_MODEL"] = "1"          # warm the model on startup
    base_env["AMS_DATADIR_ENCRYPTED"] = base_env.get("AMS_DATADIR_ENCRYPTED", "1")  # silence advisory for the demo box
    base_env["AMS_ENFORCE_OFFLINE"] = "1"     # prove offline during the demo

    env1 = dict(base_env, AMS_DATA_DIR=str(DEMO_DATA / "tool1"), AMS_TOOL1_PORT=str(TOOL1_PORT))
    env2 = dict(base_env, AMS_DATA_DIR=str(DEMO_DATA / "tool2"), AMS_TOOL2_PORT=str(TOOL2_PORT))

    p1, f1 = _start_tool(TOOL1_BACKEND, TOOL1_PORT, "CV-Ersteller (Tool 1)", env1, DEMO_DATA / "logs" / "tool1.log")
    p2, f2 = _start_tool(TOOL2_BACKEND, TOOL2_PORT, "Trainer-Dashboard (Tool 2)", env2, DEMO_DATA / "logs" / "tool2.log")
    procs = [p1, p2]

    try:
        print("\nWaiting for both tools to come up ...")
        up1 = _wait_health(TOOL1_PORT, "CV-Ersteller")
        up2 = _wait_health(TOOL2_PORT, "Trainer-Dashboard")
        if not (up1 and up2):
            print("\n[!!] One of the tools failed to start. See demo-data/logs/. Aborting.")
            return 1

        if _model_present(TOOL1_PORT) is False:
            print("\n[!!] No local AI model found on disk. The demo will run in RULES-ONLY mode")
            print("     (extraction/coach are reduced). Download the model first if you want full AI.")
        else:
            print("\nPre-warming the local AI model (this is the slow part - doing it NOW so the")
            print("demo is instant). Please wait ...")
            t0 = time.time()
            loaded = False
            while time.time() - t0 < WARM_TIMEOUT:
                if _model_ready(TOOL1_PORT):
                    print(f"\n  [OK] AI model loaded ({time.time()-t0:.0f}s).")
                    loaded = True
                    break
                dots = "." * (int(time.time() - t0) % 4)
                print(f"\r  loading model... {int(time.time()-t0)}s {dots}   ", end="", flush=True)
                time.sleep(2)
            if loaded:
                # The model object is loaded, but the FIRST real inference still
                # pays a large cold cost (~60-120s for the first generation). Pay
                # it NOW with a throwaway chat call so the demo's first dump is fast.
                print("  Priming the first inference (the genuinely slow part)...")
                t1 = time.time()
                r = _post(f"http://127.0.0.1:{TOOL1_PORT}/api/ai/chat",
                          {"message": "hallo", "language": "de"}, timeout=240)
                if r is not None:
                    print(f"  [OK] AI primed - inference path is warm ({time.time()-t1:.0f}s). "
                          "The demo will be fast.")
                else:
                    print("  [!!] Warm-up inference didn't finish - the FIRST AI step in the "
                          "demo may take ~1 min. After that it's fast.")
            else:
                print("\n  [!!] Model didn't load within the timeout - the first AI call in the "
                      "UI may be slow, but the demo will still work.")

        print("\n" + "=" * 60)
        print("  [ READY FOR THE DEMO ]")
        print("=" * 60)
        print(f"  Participant (CV-Ersteller):  http://localhost:{TOOL1_PORT}")
        print(f"  Trainer (Dashboard):         http://localhost:{TOOL2_PORT}")
        print("=" * 60)
        print("  Walkthrough script: DEMO_FRIDAY.md")
        print("  Stop the demo: press Ctrl+C in this window.")
        print("=" * 60 + "\n")

        if open_browser:
            webbrowser.open(f"http://localhost:{TOOL1_PORT}")

        # Keep running until interrupted; surface a crash if a tool dies.
        while True:
            time.sleep(2)
            for proc, name in ((p1, "CV-Ersteller"), (p2, "Trainer-Dashboard")):
                if proc.poll() is not None:
                    print(f"\n[!!] {name} stopped unexpectedly (see demo-data/logs/). Exiting.")
                    return 1
    except KeyboardInterrupt:
        print("\nShutting down ...")
    finally:
        for p in procs:
            try:
                p.terminate()
            except Exception:
                pass
        for p in procs:
            try:
                p.wait(timeout=5)
            except Exception:
                try:
                    p.kill()
                except Exception:
                    pass
        for fh in (f1, f2):
            try:
                fh.close()
            except Exception:
                pass
        print("Demo stopped. Both tools shut down.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
