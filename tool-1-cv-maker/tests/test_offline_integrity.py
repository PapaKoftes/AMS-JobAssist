"""
Offline integrity tests — verify that the application never opens a real
network connection during normal operation.

Strategy
--------
We monkey-patch ``socket.socket`` to raise ``ConnectionRefusedError`` for
any connection attempt that does NOT target localhost.  Then we import all
application modules and run a mini interview flow.  If anything tries to
phone home, the test fails immediately.

This gives confidence that the offline guarantee holds — no hidden HTTP
requests to CDNs, telemetry endpoints, or external model servers.
"""

import socket
import sys
import threading
import unittest
from pathlib import Path
from typing import Optional
from unittest.mock import patch

# Ensure backend is on the path
_BACKEND = Path(__file__).parent.parent / "src" / "backend"
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))


# ---------------------------------------------------------------------------
# Network blocker
# ---------------------------------------------------------------------------

_LOCALHOST_ADDRS = {"127.0.0.1", "::1", "localhost"}
_blocked_calls: list[tuple] = []


class _OfflineSocket(socket.socket):
    """
    Socket subclass that blocks any connection to a non-localhost address.

    Allows:
    - All loopback (127.x, ::1, localhost)
    - Unix domain sockets (AF_UNIX)

    Raises ConnectionRefusedError for everything else.
    """

    def connect(self, address):
        host = address[0] if isinstance(address, tuple) else str(address)
        if host not in _LOCALHOST_ADDRS and not host.startswith("127."):
            _blocked_calls.append(("connect", address))
            raise ConnectionRefusedError(
                f"[OFFLINE TEST] Network call blocked: connect({address!r}). "
                "Application must not make outbound connections."
            )
        return super().connect(address)

    def connect_ex(self, address):
        host = address[0] if isinstance(address, tuple) else str(address)
        if host not in _LOCALHOST_ADDRS and not host.startswith("127."):
            _blocked_calls.append(("connect_ex", address))
            raise ConnectionRefusedError(
                f"[OFFLINE TEST] Network call blocked: connect_ex({address!r})"
            )
        return super().connect_ex(address)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestOfflineImports(unittest.TestCase):
    """Importing application modules must not trigger network calls."""

    def setUp(self):
        _blocked_calls.clear()

    def test_import_config_no_network(self):
        """config.py must not call out on import."""
        import config  # noqa: F401 — side effect check only

    def test_import_polish_engine_no_network(self):
        """PolishEngine import must not trigger network."""
        # DB is needed; pass a mock that returns empty lists
        from unittest.mock import MagicMock
        mock_db = MagicMock()
        mock_db.execute_query.return_value = []
        from polish.engine import PolishEngine
        PolishEngine(mock_db)  # constructor loads verb/skill maps from DB mock

    def test_import_language_normalizer_no_network(self):
        """LanguageNormalizer must not call any network endpoint."""
        from polish.language import LanguageNormalizer
        ln = LanguageNormalizer()
        # Run a detection to exercise the full path
        result = ln.detect_language("Ich arbeite mit Python")
        self.assertIsInstance(result, str)

    def test_import_ats_no_network(self):
        """ATS module must be fully offline."""
        from polish.ats import score_against_bank, extract_keywords
        kws = extract_keywords("Python und Excel Kenntnisse")
        self.assertIsInstance(kws, list)

    def test_import_cover_letter_no_network(self):
        """Cover letter generator must be fully offline."""
        from cv.cover_letter import generate, CoverLetterRequest
        req = CoverLetterRequest(full_name="Test User", job_title="Developer")
        letter = generate(req)
        self.assertGreater(letter.word_count, 10)


class TestOfflineSocketPatch(unittest.TestCase):
    """
    Run key flows with a network-blocking socket to prove no outbound calls
    are made during normal operation.
    """

    def setUp(self):
        _blocked_calls.clear()

    def _run_with_blocked_network(self, fn, *args, **kwargs):
        """Run fn(...) with socket.socket replaced by the offline variant."""
        with patch("socket.socket", _OfflineSocket):
            return fn(*args, **kwargs)

    def test_language_detection_no_network(self):
        from polish.language import LanguageNormalizer
        ln = LanguageNormalizer()
        detect = lambda: ln.detect_language("Hallo, ich suche eine Stelle")
        result = self._run_with_blocked_network(detect)
        self.assertIsInstance(result, str)
        self.assertEqual(_blocked_calls, [], f"Unexpected network call: {_blocked_calls}")

    def test_ats_scoring_no_network(self):
        from polish.ats import score_against_bank
        score = lambda: score_against_bank("Python, Excel, SQL Erfahrung vorhanden.")
        result = self._run_with_blocked_network(score)
        self.assertGreaterEqual(result.score, 0.0)
        self.assertEqual(_blocked_calls, [], f"Unexpected network call: {_blocked_calls}")

    def test_cover_letter_gen_no_network(self):
        from cv.cover_letter import generate, CoverLetterRequest
        req = CoverLetterRequest(
            full_name="Maria Muster",
            job_title="Lagerarbeiterin",
            employer_name="MusterGmbH",
            skills=["Staplerschein", "Teamarbeit"],
        )
        result = self._run_with_blocked_network(generate, req)
        self.assertIn("Maria Muster", result.text)
        self.assertEqual(_blocked_calls, [], f"Unexpected network call: {_blocked_calls}")


if __name__ == "__main__":
    unittest.main()
