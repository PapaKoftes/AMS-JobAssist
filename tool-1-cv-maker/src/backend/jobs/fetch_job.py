"""
Opt-in single-URL job-ad fetcher for the "check a specific job" feature.

PRIVACY / SAFETY: this is the ONLY participant-facing outbound request in Tool 1,
and it runs ONLY on explicit per-action consent (see /api/jobs/fetch-and-match).
It GETs exactly the one job-ad URL the user pasted — it sends NO CV/personal data.

SSRF hardening (this is the security-critical part):
  * Resolve the host's IP ONCE, validate it is public/routable, then CONNECT TO
    THAT IP LITERAL — with the original hostname only as TLS SNI + Host header.
    This closes the classic TOCTOU/DNS-rebinding hole where a check-time lookup
    returns a public IP and the connect-time lookup returns 127.0.0.1.
  * EVERY redirect hop is re-resolved and re-validated the same way, with a hard
    redirect cap. robots.txt is fetched through the same validated path.
  * robots.txt is honoured (declines disallowed paths, incl. jobs.ams.at
    /public/emps/). Hard size cap + timeout. Only HTTP(S) + HTML/text accepted.
    No Accept-Encoding is sent, so there is no gzip-decompression-bomb surface.

Stdlib only (offline-friendly). Must be called inside
privacy.network_block.temporarily_allow_network() so the offline guard lets the
one request through.
"""
from __future__ import annotations

import http.client
import ipaddress
import re
import socket
import ssl
import urllib.parse
import urllib.robotparser
from html.parser import HTMLParser

USER_AGENT = "ams-jobassist (offline CV tool; single user-initiated fetch)"
_TIMEOUT = 10          # seconds, per socket op
_MAX_BYTES = 800_000   # hard cap on downloaded bytes
_MAX_TEXT = 20_000     # cap on extracted text handed to the matcher
_MAX_REDIRECTS = 4


class FetchError(Exception):
    """Any failure to obtain usable job text from the URL."""


class RobotsDisallowed(FetchError):
    """The site's robots.txt disallows fetching this path for our agent."""


def _ip_is_public(ip: str) -> bool:
    ip = ip.split("%", 1)[0]  # strip IPv6 zone id
    try:
        addr = ipaddress.ip_address(ip)
    except ValueError:
        return False
    return not (addr.is_private or addr.is_loopback or addr.is_link_local
                or addr.is_reserved or addr.is_multicast or addr.is_unspecified)


def _is_public_host(host: str) -> bool:
    """True only if EVERY resolved address for host is public (SSRF guard).

    Kept for callers/tests; the fetch path uses _resolve_public_ip so it connects
    to the exact validated address.
    """
    try:
        infos = socket.getaddrinfo(host, None)
    except Exception:
        return False
    return bool(infos) and all(_ip_is_public(i[4][0]) for i in infos)


def _resolve_public_ip(host: str):
    """Resolve host and return (ip, family). Raise FetchError if any address is
    non-public (fail closed) or resolution fails."""
    if not host:
        raise FetchError("non_public_host")
    try:
        infos = socket.getaddrinfo(host, None)
    except Exception as exc:
        raise FetchError("dns_failed") from exc
    if not infos:
        raise FetchError("dns_failed")
    # Fail closed: if ANY resolved address is non-public, refuse (defeats a
    # rebinding answer that mixes a public and a private record).
    for fam, _t, _p, _c, sockaddr in infos:
        if not _ip_is_public(sockaddr[0]):
            raise FetchError("non_public_host")
    fam, _t, _p, _c, sockaddr = infos[0]
    return sockaddr[0], fam


class _TextExtractor(HTMLParser):
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


def _http_get(scheme: str, host: str, ip: str, family: int, port: int, path: str):
    """One GET to the PINNED ip (TLS SNI/Host = host). No redirect following.

    Returns (status:int, headers:dict, body:bytes|None). Body only read for 2xx.
    Separated out as the single network seam (tests mock this).
    """
    sock = None
    try:
        sock = socket.create_connection((ip, port), timeout=_TIMEOUT)
        if scheme == "https":
            ctx = ssl.create_default_context()
            sock = ctx.wrap_socket(sock, server_hostname=host)  # validate cert against host
        conn = http.client.HTTPConnection(host, port, timeout=_TIMEOUT)
        conn.sock = sock  # use our pinned/wrapped socket
        conn.request("GET", path or "/", headers={
            "User-Agent": USER_AGENT, "Accept": "text/html,text/plain", "Host": host,
        })
        resp = conn.getresponse()
        headers = {k.lower(): v for k, v in resp.getheaders()}
        status = resp.status
        body = None
        if 200 <= status < 300:
            body = resp.read(_MAX_BYTES + 1)
        else:
            resp.read(1)  # drain a little
        return status, headers, body
    except FetchError:
        raise
    except ssl.SSLError as exc:
        raise FetchError("tls_failed") from exc
    except Exception as exc:
        raise FetchError("fetch_failed") from exc
    finally:
        try:
            if sock is not None:
                sock.close()
        except Exception:
            pass


def _split(url: str):
    """Validate scheme + return (scheme, host, port, path_with_query). Raise on bad."""
    p = urllib.parse.urlparse(url)
    if p.scheme not in ("http", "https") or not p.netloc or not p.hostname:
        raise FetchError("invalid_url")
    port = p.port or (443 if p.scheme == "https" else 80)
    path = p.path or "/"
    if p.query:
        path += "?" + p.query
    return p.scheme, p.hostname, port, path


def _robots_allows(scheme: str, host: str, port: int, url: str) -> bool:
    """Fetch robots.txt through the pinned/validated path and check our agent."""
    try:
        ip, family = _resolve_public_ip(host)
        status, headers, body = _http_get(scheme, host, ip, family, port, "/robots.txt")
    except FetchError:
        return True  # no reachable robots.txt → default allow
    if not body or status >= 400:
        return True
    rp = urllib.robotparser.RobotFileParser()
    try:
        rp.parse(body.decode("utf-8", errors="replace").splitlines())
    except Exception:
        return True
    return rp.can_fetch(USER_AGENT, url)


def fetch_job_text(url: str) -> str:
    """Fetch and return the visible text of a single job-ad URL.

    Resolves+validates the host (and every redirect hop), connects to the vetted
    IP literal, honours robots.txt, caps size. Raises RobotsDisallowed / FetchError.
    MUST be called inside temporarily_allow_network().
    """
    scheme, host, port, path = _split((url or "").strip())

    # robots.txt for the ORIGINAL host/path.
    if not _robots_allows(scheme, host, port, url):
        raise RobotsDisallowed("robots_disallowed")

    seen = 0
    cur_scheme, cur_host, cur_port, cur_path = scheme, host, port, path
    cur_url = url
    while True:
        ip, family = _resolve_public_ip(cur_host)       # re-validate EVERY hop
        status, headers, body = _http_get(cur_scheme, cur_host, ip, family, cur_port, cur_path)

        if status in (301, 302, 303, 307, 308):
            seen += 1
            if seen > _MAX_REDIRECTS:
                raise FetchError("too_many_redirects")
            loc = headers.get("location")
            if not loc:
                raise FetchError("bad_redirect")
            cur_url = urllib.parse.urljoin(cur_url, loc)
            cur_scheme, cur_host, cur_port, cur_path = _split(cur_url)  # re-checks scheme
            continue

        if not (200 <= status < 300) or body is None:
            raise FetchError(f"http_{status}")

        ctype = headers.get("content-type", "")
        if "html" not in ctype.lower() and "text" not in ctype.lower():
            raise FetchError("not_html")
        if len(body) > _MAX_BYTES:
            body = body[:_MAX_BYTES]
        charset = "utf-8"
        m = re.search(r"charset=([\w\-]+)", ctype, re.IGNORECASE)
        if m:
            charset = m.group(1)
        try:
            html = body.decode(charset, errors="replace")
        except (LookupError, TypeError):
            html = body.decode("utf-8", errors="replace")
        text = _html_to_text(html)
        if len(text) < 40:
            raise FetchError("too_little_text")
        return text[:_MAX_TEXT]
