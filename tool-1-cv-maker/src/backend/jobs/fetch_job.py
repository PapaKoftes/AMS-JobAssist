"""
Opt-in single-URL job-ad fetcher for the "check a specific job" feature.

PRIVACY / SAFETY: this is the ONLY participant-facing outbound request in Tool 1,
and it runs ONLY on explicit per-action consent (see the /api/jobs/fetch-and-match
endpoint). It GETs exactly the one job-ad URL the user pasted — it sends NO CV or
personal data. It:
  * honours the site's robots.txt (declines disallowed paths — incl. jobs.ams.at
    /public/emps/, which the AMS robots.txt blocks for non-LinkedIn agents),
  * guards against SSRF (rejects non-public / loopback / private / link-local hosts),
  * makes a single request with a short timeout and a hard size cap,
  * accepts only HTML/text and strips it to visible text,
  * identifies itself with a clear User-Agent.

Stdlib only (offline-friendly). Must be called inside
privacy.network_block.temporarily_allow_network() so the offline guard lets the
one request through.
"""
from __future__ import annotations

import ipaddress
import re
import socket
import urllib.parse
import urllib.request
import urllib.robotparser
from html.parser import HTMLParser

# Identifies the tool honestly; robotparser also matches rules against this.
USER_AGENT = "ams-jobassist (offline CV tool; single user-initiated fetch)"
_TIMEOUT = 10          # seconds
_MAX_BYTES = 800_000   # hard cap on downloaded bytes
_MAX_TEXT = 20_000     # cap on extracted text handed to the matcher


class FetchError(Exception):
    """Any failure to obtain usable job text from the URL."""


class RobotsDisallowed(FetchError):
    """The site's robots.txt disallows fetching this path for our agent."""


def _is_public_host(host: str) -> bool:
    """True only if every resolved address is a public, routable IP (SSRF guard)."""
    if not host:
        return False
    try:
        infos = socket.getaddrinfo(host, None)
    except Exception:
        return False
    if not infos:
        return False
    for info in infos:
        ip = info[4][0]
        # Strip IPv6 zone id if present (e.g. "fe80::1%eth0").
        ip = ip.split("%", 1)[0]
        try:
            addr = ipaddress.ip_address(ip)
        except ValueError:
            return False
        if (addr.is_private or addr.is_loopback or addr.is_link_local
                or addr.is_reserved or addr.is_multicast or addr.is_unspecified):
            return False
    return True


class _TextExtractor(HTMLParser):
    """Collect visible text, skipping script/style/head/etc."""
    _SKIP = {"script", "style", "noscript", "head", "svg", "template"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self._skip_depth = 0
        self.parts: list[str] = []

    def handle_starttag(self, tag, attrs):
        if tag in self._SKIP:
            self._skip_depth += 1

    def handle_endtag(self, tag):
        if tag in self._SKIP and self._skip_depth:
            self._skip_depth -= 1

    def handle_data(self, data):
        if self._skip_depth == 0:
            t = data.strip()
            if t:
                self.parts.append(t)


def _html_to_text(html: str) -> str:
    parser = _TextExtractor()
    try:
        parser.feed(html)
    except Exception:
        pass
    return re.sub(r"\s{2,}", " ", " ".join(parser.parts)).strip()


def fetch_job_text(url: str) -> str:
    """Fetch and return the visible text of a single job-ad URL.

    Honours robots.txt and SSRF guards. Raises RobotsDisallowed / FetchError on any
    problem. MUST be called inside temporarily_allow_network().
    """
    url = (url or "").strip()
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        raise FetchError("invalid_url")

    host = parsed.hostname or ""
    if not _is_public_host(host):
        raise FetchError("non_public_host")

    # robots.txt — decline if the site disallows our agent on this path.
    rp = urllib.robotparser.RobotFileParser()
    rp.set_url(f"{parsed.scheme}://{parsed.netloc}/robots.txt")
    try:
        rp.read()
    except Exception:
        pass  # no reachable robots.txt → default allow
    if not rp.can_fetch(USER_AGENT, url):
        raise RobotsDisallowed("robots_disallowed")

    req = urllib.request.Request(
        url, headers={"User-Agent": USER_AGENT, "Accept": "text/html,text/plain"})
    try:
        with urllib.request.urlopen(req, timeout=_TIMEOUT) as resp:
            # Re-check the FINAL url after redirects — a redirect could point at an
            # internal host (SSRF via redirect).
            final_host = urllib.parse.urlparse(resp.geturl()).hostname or ""
            if not _is_public_host(final_host):
                raise FetchError("redirect_to_non_public_host")
            ctype = resp.headers.get("Content-Type", "")
            if "html" not in ctype.lower() and "text" not in ctype.lower():
                raise FetchError("not_html")
            raw = resp.read(_MAX_BYTES + 1)
    except FetchError:
        raise
    except Exception as exc:
        raise FetchError("fetch_failed") from exc

    if len(raw) > _MAX_BYTES:
        raw = raw[:_MAX_BYTES]

    charset = "utf-8"
    m = re.search(r"charset=([\w\-]+)", ctype, re.IGNORECASE)
    if m:
        charset = m.group(1)
    try:
        html = raw.decode(charset, errors="replace")
    except (LookupError, TypeError):
        html = raw.decode("utf-8", errors="replace")

    text = _html_to_text(html)
    if len(text) < 40:
        raise FetchError("too_little_text")
    return text[:_MAX_TEXT]
