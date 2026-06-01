"""
AMS JobAssist Launcher
Starts Tool 1 (CV Maker) and Tool 2 (Trainer Dashboard) applications

Can be built into standalone .exe with:
    pyinstaller launcher.py --onefile --windowed

Port configuration:
    Set AMS_TOOL1_PORT and AMS_TOOL2_PORT environment variables to change defaults.
"""

import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
import webbrowser
import os
import signal
from pathlib import Path
from threading import Thread


def find_free_port(start_port: int) -> int:
    """Return the first available TCP port >= start_port."""
    port = start_port
    while True:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("127.0.0.1", port))
                return port
            except OSError:
                port += 1


# Configurable ports (env var or default); auto-advance if busy
TOOL1_PORT = find_free_port(int(os.environ.get("AMS_TOOL1_PORT", "8000")))
TOOL2_PORT = find_free_port(int(os.environ.get("AMS_TOOL2_PORT", "8001")))


class AMS_Launcher:
    def __init__(self):
        self.tool1_process = None
        self.tool2_process = None
        self.running = True
        self._log_handles = []  # open child-log file handles, closed on shutdown

    def _start_tool(self, name: str, src_rel: str, port: int):
        """
        Start a tool from source (uvicorn).
        Source always takes priority — stale .exe files are never used.

        IMPORTANT: child stdout/stderr are redirected to per-tool log files,
        NOT subprocess.PIPE. Uvicorn logs every HTTP request; if we used PIPE
        and never drained it, the OS pipe buffer (~64 KB on Windows) would fill
        after a few dozen requests and the server would BLOCK FOREVER on its
        next log write — deadlocking the whole tool. Writing to a file drains
        naturally to disk with no buffer limit, and gives us logs for support.
        """
        print(f"  [>>] Starting {name}...")

        src_path = Path(src_rel)
        if not src_path.exists():
            print(f"  [!!] ERROR: {name} source not found at {src_rel}")
            return None

        env = os.environ.copy()
        env["PYTHONPATH"] = str(src_path.resolve())

        # Per-tool log file (drains child output so the pipe can never fill)
        log_dir = src_path.resolve().parents[1] / "logs"  # <tool>/logs/
        try:
            log_dir.mkdir(parents=True, exist_ok=True)
            log_path = log_dir / "server.log"
            log_handle = open(log_path, "a", buffering=1, encoding="utf-8", errors="replace")
        except Exception:
            # If we can't open a log file, fall back to discarding output —
            # anything is safer than an undrained PIPE that deadlocks the server.
            log_handle = subprocess.DEVNULL

        self._log_handles.append(log_handle)

        return subprocess.Popen(
            [sys.executable, "-m", "uvicorn",
             "app:app", "--host", "127.0.0.1",
             "--port", str(port)],
            cwd=str(src_path.resolve()),
            stdout=log_handle,
            stderr=subprocess.STDOUT,
            env=env,
        )

    def start_tool1(self):
        """Start Tool 1 (CV Maker) from source."""
        proc = self._start_tool("Tool 1", "tool-1-cv-maker/src/backend", TOOL1_PORT)
        if proc is None:
            return False
        self.tool1_process = proc
        return True

    def start_tool2(self):
        """Start Tool 2 (Trainer Dashboard) from source."""
        proc = self._start_tool("Tool 2", "tool-2-trainer-dashboard/src/backend", TOOL2_PORT)
        if proc is None:
            return False
        self.tool2_process = proc
        return True

    def _wait_for_ready(self, port: int, label: str) -> bool:
        """Poll /health until the server responds or 30 s elapses."""
        url = f"http://localhost:{port}/health"
        deadline = time.time() + 30
        while time.time() < deadline:
            try:
                with urllib.request.urlopen(url, timeout=1) as resp:
                    if resp.status == 200:
                        return True
            except Exception:
                pass
            time.sleep(0.5)
        print(f"  [!!] {label} failed to start (timeout)")
        return False

    def open_browser(self):
        """Wait for Tool 1 to be healthy, then open the default browser.
        Tool 2 failure is a warning only — participants can still use Tool 1.
        """
        if not self._wait_for_ready(TOOL1_PORT, "Tool 1"):
            print("  [!!] CV-Ersteller konnte nicht gestartet werden.")
            print("  [!!] Bitte neu starten (Option 1 im Menü) oder neu installieren.")
            sys.exit(1)
        print(f"  [OK] Tool 1 bereit: http://localhost:{TOOL1_PORT}")

        # Tool 2 (Trainer Dashboard) is optional — failure does not block participants
        if not self._wait_for_ready(TOOL2_PORT, "Tool 2"):
            print("  [!!] Trainer-Dashboard konnte nicht gestartet werden (optional).")
            print(f"  [OK] CV-Ersteller läuft trotzdem: http://localhost:{TOOL1_PORT}")
        else:
            print(f"  [OK] Trainer-Dashboard bereit: http://localhost:{TOOL2_PORT}")

        print("  [>>] Öffne Browser...")
        webbrowser.open(f"http://localhost:{TOOL1_PORT}")

    def show_launcher_menu(self):
        """Show launcher menu (German)"""
        print("\n" + "=" * 60)
        print("  AMS JobAssist - gestartet")
        print("=" * 60)
        print(f"\n  [OK] CV-Ersteller:        http://localhost:{TOOL1_PORT}")
        print(f"  [OK] Trainer-Dashboard:   http://localhost:{TOOL2_PORT}")
        print("\n  Hinweise:")
        print("  - Teilnehmer nutzen den CV-Ersteller (Tool 1)")
        print("  - Trainer nutzen das Dashboard (Tool 2)")
        print("  - STRG+C stoppt beide Programme")
        print("=" * 60 + "\n")

    def monitor_processes(self):
        """Monitor running processes"""
        while self.running:
            try:
                if self.tool1_process and self.tool1_process.poll() is not None:
                    print("[!!] CV-Ersteller wurde unerwartet beendet")

                if self.tool2_process and self.tool2_process.poll() is not None:
                    print("[!!] Trainer-Dashboard wurde unerwartet beendet")

                time.sleep(5)
            except KeyboardInterrupt:
                break

    def shutdown(self):
        """Gracefully shutdown both tools"""
        print("\n\nBeende Programme...")
        self.running = False

        if self.tool1_process:
            try:
                self.tool1_process.terminate()
                self.tool1_process.wait(timeout=5)
                print("[OK] CV-Ersteller beendet")
            except (subprocess.TimeoutExpired, OSError):
                self.tool1_process.kill()

        if self.tool2_process:
            try:
                self.tool2_process.terminate()
                self.tool2_process.wait(timeout=5)
                print("[OK] Trainer-Dashboard beendet")
            except (subprocess.TimeoutExpired, OSError):
                self.tool2_process.kill()

        # Close child-log file handles
        for h in self._log_handles:
            try:
                if h not in (subprocess.DEVNULL, None):
                    h.close()
            except Exception:
                pass

        print("[OK] Alle Programme beendet")

    def run(self):
        """Main launcher routine"""
        try:
            print("\n  Starting AMS JobAssist Applications...\n")

            # Start both tools
            if not self.start_tool1():
                return 1

            if not self.start_tool2():
                print("  [!!] Trainer-Dashboard konnte nicht gestartet werden.")
                print("  [OK] CV-Ersteller läuft weiter — Teilnehmer können ihn nutzen.")

            # Open browser
            browser_thread = Thread(target=self.open_browser)
            browser_thread.daemon = True
            browser_thread.start()

            # Show menu
            self.show_launcher_menu()

            # Monitor processes
            self.monitor_processes()

        except KeyboardInterrupt:
            pass
        finally:
            self.shutdown()

        return 0


def main():
    """Entry point"""
    import argparse
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--tool1-only", action="store_true",
                        help="Start only Tool 1 (CV maker) and open its URL")
    parser.add_argument("--open-trainer", action="store_true",
                        help="Start both tools and open the trainer dashboard URL")
    args, _ = parser.parse_known_args()

    launcher = AMS_Launcher()

    def signal_handler(sig, frame):
        launcher.shutdown()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    if args.tool1_only:
        # Participant shortcut: start Tool 1 only, open CV maker URL
        if not launcher.start_tool1():
            sys.exit(1)
        if launcher._wait_for_ready(TOOL1_PORT, "Tool 1"):
            print(f"  [OK] CV-Ersteller bereit: http://localhost:{TOOL1_PORT}")
            webbrowser.open(f"http://localhost:{TOOL1_PORT}")
        launcher.show_launcher_menu()
        launcher.monitor_processes()
        launcher.shutdown()
        return

    if args.open_trainer:
        # Trainer shortcut: start both, open trainer dashboard URL
        launcher.start_tool1()
        launcher.start_tool2()
        if launcher._wait_for_ready(TOOL1_PORT, "Tool 1"):
            print(f"  [OK] CV-Ersteller bereit: http://localhost:{TOOL1_PORT}")
        if launcher._wait_for_ready(TOOL2_PORT, "Tool 2"):
            print(f"  [OK] Trainer-Dashboard bereit: http://localhost:{TOOL2_PORT}")
            webbrowser.open(f"http://localhost:{TOOL2_PORT}")
        launcher.show_launcher_menu()
        launcher.monitor_processes()
        launcher.shutdown()
        return

    exit_code = launcher.run()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
