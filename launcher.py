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

    def _start_tool(self, name: str, src_rel: str, port: int,
                    exe_basename: str = "", port_env_var: str = ""):
        """
        Start a tool. When running from a frozen launcher .exe, invoke the
        sibling per-tool .exe (exe_basename); from source, run uvicorn via Python.

        IMPORTANT: child stdout/stderr are redirected to per-tool log files,
        NOT subprocess.PIPE. Uvicorn logs every HTTP request; if we used PIPE
        and never drained it, the OS pipe buffer (~64 KB on Windows) would fill
        after a few dozen requests and the server would BLOCK FOREVER on its
        next log write — deadlocking the whole tool. Writing to a file drains
        naturally to disk with no buffer limit, and gives us logs for support.
        """
        print(f"  [>>] Starting {name}...")

        env = os.environ.copy()
        frozen = getattr(sys, "frozen", False)

        # ── Decide HOW to launch ──────────────────────────────────────────────
        # FROZEN (.exe distribution): we CANNOT run `sys.executable -m uvicorn`
        # — sys.executable is the launcher .exe, which has no -m/uvicorn and no
        # source tree. Instead invoke the bundled per-tool .exe (built from
        # build_tool{1,2}.spec, whose app.py __main__ runs uvicorn in-process),
        # located next to the launcher, with the port passed via env.
        if frozen:
            exe_dir = Path(sys.executable).resolve().parent
            exe_name = f"{exe_basename}.exe" if os.name == "nt" else exe_basename
            tool_exe = exe_dir / exe_name
            if not tool_exe.exists():
                print(f"  [!!] ERROR: {name} executable not found at {tool_exe}")
                return None
            # The tool reads its port from AMS_TOOL{1,2}_PORT.
            env[port_env_var] = str(port)
            cmd = [str(tool_exe)]
            cwd = str(exe_dir)
            log_base = exe_dir
        else:
            # SOURCE / dev: run uvicorn via the real Python interpreter.
            src_path = Path(src_rel)
            if not src_path.exists():
                print(f"  [!!] ERROR: {name} source not found at {src_rel}")
                return None
            env["PYTHONPATH"] = str(src_path.resolve())
            env[port_env_var] = str(port)
            cmd = [sys.executable, "-m", "uvicorn", "app:app",
                   "--host", "127.0.0.1", "--port", str(port)]
            cwd = str(src_path.resolve())
            log_base = src_path.resolve().parents[1]  # <tool>/

        # Per-tool log file (drains child output so the pipe can never fill).
        log_dir = log_base / "logs"
        try:
            log_dir.mkdir(parents=True, exist_ok=True)
            log_path = log_dir / "server.log"
            # Rotate if the log has grown large (RC-6: prevent unbounded growth).
            try:
                if log_path.exists() and log_path.stat().st_size > 10 * 1024 * 1024:
                    bak = log_dir / "server.log.1"
                    if bak.exists():
                        bak.unlink()
                    log_path.rename(bak)
            except Exception:
                pass
            log_handle = open(log_path, "a", buffering=1, encoding="utf-8", errors="replace")
        except Exception:
            # If we can't open a log file, fall back to discarding output —
            # anything is safer than an undrained PIPE that deadlocks the server.
            log_handle = subprocess.DEVNULL

        self._log_handles.append(log_handle)

        return subprocess.Popen(
            cmd,
            cwd=cwd,
            stdout=log_handle,
            stderr=subprocess.STDOUT,
            env=env,
        )

    def start_tool1(self):
        """Start Tool 1 (CV Maker) from source."""
        proc = self._start_tool("Tool 1", "tool-1-cv-maker/src/backend", TOOL1_PORT,
                                exe_basename="AMS-JobAssist-Tool1", port_env_var="AMS_TOOL1_PORT")
        if proc is None:
            return False
        self.tool1_process = proc
        return True

    def start_tool2(self):
        """Start Tool 2 (Trainer Dashboard) from source."""
        proc = self._start_tool("Tool 2", "tool-2-trainer-dashboard/src/backend", TOOL2_PORT,
                                exe_basename="AMS-JobAssist-Tool2", port_env_var="AMS_TOOL2_PORT")
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

    def _warm_model(self, port: int) -> None:
        """Best-effort: load the local AI model into memory before the user starts,
        so the first answer isn't slowed by the ~2.5 s cold model load. Never
        blocks the launch — any failure is silently ignored (rules mode still works).
        """
        try:
            url = f"http://localhost:{port}/api/ai/model-status"
            with urllib.request.urlopen(url, timeout=60) as resp:
                resp.read()
        except Exception:
            pass

    def open_browser(self):
        """Wait for Tool 1 to be healthy, then open the default browser.
        Tool 2 failure is a warning only — participants can still use Tool 1.
        """
        if not self._wait_for_ready(TOOL1_PORT, "Tool 1"):
            print("  [!!] CV-Ersteller konnte nicht gestartet werden.")
            print("  [!!] Bitte neu starten (Option 1 im Menü) oder neu installieren.")
            sys.exit(1)
        print(f"  [OK] Tool 1 bereit: http://localhost:{TOOL1_PORT}")
        print("  [>>] Lade KI-Modell vor (einmalig, ~3 s)...")
        self._warm_model(TOOL1_PORT)

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
        """
        Monitor running processes; auto-restart a crashed tool ONCE and write a
        visible LAST_ERROR file so a non-technical trainer has something to send
        for support (M18: previously a crash only printed to a console they may
        have closed).
        """
        restarts = {"tool1": 0, "tool2": 0}

        def _handle_crash(which, proc_attr, restart_fn):
            proc = getattr(self, proc_attr)
            if proc and proc.poll() is not None:
                self._write_last_error(which)
                if restarts[which] < 1:
                    restarts[which] += 1
                    print(f"[!!] {which} beendet — Neustart-Versuch {restarts[which]}…")
                    try:
                        restart_fn()
                    except Exception as _e:
                        print(f"[!!] {which} Neustart fehlgeschlagen: {_e}")
                else:
                    print(f"[!!] {which} ist erneut abgestürzt — kein weiterer Neustart.")

        while self.running:
            try:
                _handle_crash("tool1", "tool1_process", self.start_tool1)
                _handle_crash("tool2", "tool2_process", self.start_tool2)
                time.sleep(5)
            except KeyboardInterrupt:
                break

    def _write_last_error(self, which: str) -> None:
        """Write a support-friendly error file with the tail of the tool's log."""
        try:
            from pathlib import Path as _P
            tool_dir = ("tool-1-cv-maker" if which == "tool1" else "tool-2-trainer-dashboard")
            log = _P(tool_dir) / "logs" / "server.log"
            tail = ""
            if log.exists():
                tail = "\n".join(log.read_text(encoding="utf-8", errors="replace").splitlines()[-40:])
            out = _P("LAST_ERROR.txt")
            out.write_text(
                f"{which} wurde unerwartet beendet.\n\nLetzte Logzeilen:\n{tail}\n",
                encoding="utf-8")
        except Exception:
            pass

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
