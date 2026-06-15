"""Tests for the opt-in single-URL job-ad fetcher (robots + SSRF + HTML strip)."""
import ipaddress
import sys
from pathlib import Path

import pytest

BACKEND = Path(__file__).resolve().parent.parent / "src" / "backend"
sys.path.insert(0, str(BACKEND))

from jobs import fetch_job as F  # noqa: E402


def _public_dns(monkeypatch):
    """getaddrinfo that resolves IP literals to themselves and names to a public IP
    — so SSRF guards on redirects to internal IPs are actually exercised."""
    def fake(host, *a, **k):
        try:
            ipaddress.ip_address(host)
            ip = host
        except ValueError:
            ip = "93.184.216.34"  # example.com, public
        return [(2, 1, 6, "", (ip, 0))]
    monkeypatch.setattr(F.socket, "getaddrinfo", fake)


def _mock_http(monkeypatch, routes):
    """Patch the single network seam. routes: path -> (status, headers, body)."""
    def fake_get(scheme, host, ip, family, port, path):
        # robots default: allow (404) unless a route is given
        if path == "/robots.txt" and "/robots.txt" not in routes:
            return (404, {}, None)
        if path not in routes:
            return (404, {}, None)
        return routes[path]
    monkeypatch.setattr(F, "_http_get", fake_get)


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
    _public_dns(monkeypatch)
    assert F._is_public_host("example.com") is True


def test_invalid_url_scheme_rejected():
    with pytest.raises(F.FetchError):
        F.fetch_job_text("ftp://example.com/job")
    with pytest.raises(F.FetchError):
        F.fetch_job_text("not a url")


def test_private_host_url_rejected(monkeypatch):
    _public_dns(monkeypatch)  # resolves 127.0.0.1 -> 127.0.0.1 (non-public)
    with pytest.raises(F.FetchError):
        F.fetch_job_text("http://127.0.0.1:8000/api/jobs")


# ── robots.txt ───────────────────────────────────────────────────────────────

def test_robots_disallowed(monkeypatch):
    _public_dns(monkeypatch)
    robots = b"User-agent: *\nDisallow: /public/emps/\n"
    _mock_http(monkeypatch, {
        "/robots.txt": (200, {"content-type": "text/plain"}, robots),
        "/public/emps/12345": (200, {"content-type": "text/html"}, b"<p>job</p>"),
    })
    with pytest.raises(F.RobotsDisallowed):
        F.fetch_job_text("https://jobs.ams.at/public/emps/12345")


# ── happy path ───────────────────────────────────────────────────────────────

def test_happy_path_returns_text(monkeypatch):
    _public_dns(monkeypatch)
    html = b"<html><body><h1>Lagermitarbeiter</h1><p>Stapler, Schichtarbeit, Wien.</p></body></html>"
    _mock_http(monkeypatch, {"/job": (200, {"content-type": "text/html; charset=utf-8"}, html)})
    text = F.fetch_job_text("https://example.com/job")
    assert "Lagermitarbeiter" in text and "Stapler" in text


def test_redirect_to_internal_host_blocked(monkeypatch):
    _public_dns(monkeypatch)
    _mock_http(monkeypatch, {
        "/job": (302, {"location": "http://169.254.169.254/latest/meta-data"}, None),
    })
    # the redirect target is link-local → re-validation must reject it
    with pytest.raises(F.FetchError):
        F.fetch_job_text("https://example.com/job")


def test_redirect_cap(monkeypatch):
    _public_dns(monkeypatch)
    # a public host that just keeps redirecting to itself
    _mock_http(monkeypatch, {
        "/loop": (302, {"location": "https://example.com/loop"}, None),
    })
    with pytest.raises(F.FetchError):
        F.fetch_job_text("https://example.com/loop")


def test_non_html_content_rejected(monkeypatch):
    _public_dns(monkeypatch)
    _mock_http(monkeypatch, {"/job.pdf": (200, {"content-type": "application/pdf"}, b"%PDF-1.4")})
    with pytest.raises(F.FetchError):
        F.fetch_job_text("https://example.com/job.pdf")


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
