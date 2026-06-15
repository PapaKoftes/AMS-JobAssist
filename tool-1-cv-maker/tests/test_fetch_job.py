"""Tests for the opt-in single-URL job-ad fetcher (robots + SSRF + HTML strip)."""
import sys
from pathlib import Path

import pytest

BACKEND = Path(__file__).resolve().parent.parent / "src" / "backend"
sys.path.insert(0, str(BACKEND))

from jobs import fetch_job as F  # noqa: E402


# ── HTML → text ──────────────────────────────────────────────────────────────

def test_html_to_text_strips_script_and_collapses():
    html = """<html><head><title>x</title><style>.a{}</style></head>
    <body><h1>Koch  gesucht</h1><script>evil()</script>
    <p>Wir suchen einen   Koch (m/w).</p></body></html>"""
    text = F._html_to_text(html)
    assert "Koch gesucht" in text
    assert "Wir suchen einen Koch" in text
    assert "evil" not in text and ".a{}" not in text


# ── SSRF / host guards ───────────────────────────────────────────────────────

@pytest.mark.parametrize("host", ["localhost", "127.0.0.1", "10.0.0.5",
                                  "192.168.1.10", "169.254.169.254", "::1"])
def test_non_public_hosts_rejected(host):
    assert F._is_public_host(host) is False


def test_public_host_accepted(monkeypatch):
    monkeypatch.setattr(F.socket, "getaddrinfo",
                        lambda *a, **k: [(2, 1, 6, "", ("93.184.216.34", 0))])
    assert F._is_public_host("example.com") is True


def test_invalid_url_scheme_rejected():
    with pytest.raises(F.FetchError):
        F.fetch_job_text("ftp://example.com/job")
    with pytest.raises(F.FetchError):
        F.fetch_job_text("not a url")


def test_private_host_url_rejected():
    with pytest.raises(F.FetchError):
        F.fetch_job_text("http://127.0.0.1:8000/api/jobs")


# ── robots.txt ───────────────────────────────────────────────────────────────

def _public(monkeypatch):
    monkeypatch.setattr(F.socket, "getaddrinfo",
                        lambda *a, **k: [(2, 1, 6, "", ("93.184.216.34", 0))])


class _Robots:
    def __init__(self, allowed): self._allowed = allowed
    def set_url(self, u): pass
    def read(self): pass
    def can_fetch(self, ua, url): return self._allowed


def test_robots_disallowed(monkeypatch):
    _public(monkeypatch)
    monkeypatch.setattr(F.urllib.robotparser, "RobotFileParser", lambda: _Robots(False))
    with pytest.raises(F.RobotsDisallowed):
        F.fetch_job_text("https://jobs.ams.at/public/emps/12345")


# ── happy path (mocked network) ──────────────────────────────────────────────

class _Resp:
    def __init__(self, body, ctype="text/html; charset=utf-8", final=None):
        self._body = body if isinstance(body, bytes) else body.encode("utf-8")
        self.headers = {"Content-Type": ctype}
        self._final = final or "https://example.com/job"
    def geturl(self): return self._final
    def read(self, n=-1): return self._body
    def __enter__(self): return self
    def __exit__(self, *a): return False


def test_happy_path_returns_text(monkeypatch):
    _public(monkeypatch)
    monkeypatch.setattr(F.urllib.robotparser, "RobotFileParser", lambda: _Robots(True))
    html = "<html><body><h1>Lagermitarbeiter</h1><p>Stapler, Schichtarbeit, Wien.</p></body></html>"
    monkeypatch.setattr(F.urllib.request, "urlopen", lambda req, timeout=0: _Resp(html))
    text = F.fetch_job_text("https://example.com/job")
    assert "Lagermitarbeiter" in text and "Stapler" in text


def test_redirect_to_internal_host_blocked(monkeypatch):
    _public(monkeypatch)
    monkeypatch.setattr(F.urllib.robotparser, "RobotFileParser", lambda: _Robots(True))
    # urlopen "succeeds" but the final URL is an internal host → must be rejected
    monkeypatch.setattr(F.urllib.request, "urlopen",
                        lambda req, timeout=0: _Resp("<p>secret</p>", final="http://169.254.169.254/latest"))
    with pytest.raises(F.FetchError):
        F.fetch_job_text("https://example.com/job")


def test_non_html_content_rejected(monkeypatch):
    _public(monkeypatch)
    monkeypatch.setattr(F.urllib.robotparser, "RobotFileParser", lambda: _Robots(True))
    monkeypatch.setattr(F.urllib.request, "urlopen",
                        lambda req, timeout=0: _Resp(b"%PDF-1.4", ctype="application/pdf"))
    with pytest.raises(F.FetchError):
        F.fetch_job_text("https://example.com/job.pdf")


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
