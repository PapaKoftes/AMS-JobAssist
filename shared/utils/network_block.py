"""
HARD-ENFORCED NETWORK BLOCKING FOR AMS JOBASSIST (shared)

Blocks all *external* network access while leaving loopback (127.0.0.1, ::1,
localhost) intact so a local FastAPI server can bind and accept connections.

This is the SHARED implementation used by both Tool 1 and Tool 2. Tool 1 has
its own historical copy under `privacy/network_block.py` (which also exposes
`temporarily_allow_network()` for the one explicit model download). Tool 2 has
no model download, so it uses this shared, download-free version.

⚠️  IMPORT ORDER WARNING  ⚠️
============================================================================
`enable_offline_mode()` monkey-patches `socket.socket`, `socket.getaddrinfo`,
`urllib.request.urlopen`, and `http.client.HTTP[S]Connection`. ANY module that
imported these names BEFORE `enable_offline_mode()` runs will still hold
references to the unblocked originals.

→ Call `enable_offline_mode()` BEFORE importing fastapi, uvicorn, requests,
  urllib3, or anything else that may pre-cache socket primitives.
============================================================================
"""

import socket
import urllib.request
import urllib.error
import urllib.parse
import http.client
import os
import logging

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Loopback allowlist
# ---------------------------------------------------------------------------
_LOOPBACK_HOSTNAMES = {"localhost", "ip6-localhost", "ip6-loopback", ""}
_LOOPBACK_IPV4_PREFIX = "127."
_LOOPBACK_IPV6 = {"::1", "0:0:0:0:0:0:0:1"}


def _is_loopback(host) -> bool:
    """Return True if `host` is loopback / localhost."""
    if host is None:
        return True  # AF_UNIX or default
    if isinstance(host, bytes):
        try:
            host = host.decode("ascii")
        except Exception:
            return False
    host = str(host).strip().lower()
    if host in _LOOPBACK_HOSTNAMES:
        return True
    if host.startswith(_LOOPBACK_IPV4_PREFIX):
        return True
    if host in _LOOPBACK_IPV6:
        return True
    return False


# Public alias — the single source of truth for "is this host local?", used by
# both tools' config + request-gate checks (previously hand-rolled in ~6 places
# with drift, e.g. some copies omitted Starlette's "testclient" peer name).
def is_loopback_host(host) -> bool:
    """True if `host` is loopback/localhost (incl. Starlette's TestClient peer)."""
    h = "" if host is None else str(host).strip().lower()
    return h == "testclient" or _is_loopback(h)


class NetworkBlocker:
    """Enforces offline mode — external network blocked, loopback allowed."""

    def __init__(self):
        self._blocked = False
        self._original_socket = None
        self._original_getaddrinfo = None
        self._original_urlopen = None
        self._original_http_connection = None
        self._original_https_connection = None

    def enable_offline_mode(self) -> bool:
        if self._blocked:
            logger.warning("Network blocking already enabled (idempotent)")
            return True

        try:
            # ---- 1. Socket factory ----
            self._original_socket = socket.socket
            _orig_socket = self._original_socket

            class _LoopbackOnlySocket(_orig_socket):
                """Socket subclass that refuses to connect/send anywhere but loopback."""

                def connect(self, address):
                    host = address[0] if isinstance(address, tuple) else address
                    if not _is_loopback(host):
                        raise OSError(
                            f"Offline mode: refused connect to non-loopback host {host!r}"
                        )
                    return super().connect(address)

                def connect_ex(self, address):
                    host = address[0] if isinstance(address, tuple) else address
                    if not _is_loopback(host):
                        return 1
                    return super().connect_ex(address)

                # Also guard connectionless UDP sends (DNS-over-UDP, telemetry beacons).
                def sendto(self, data, *args):
                    address = args[-1] if args else None
                    host = address[0] if isinstance(address, tuple) else address
                    if address is not None and not _is_loopback(host):
                        raise OSError(
                            f"Offline mode: refused sendto non-loopback host {host!r}"
                        )
                    return super().sendto(data, *args)

            socket.socket = _LoopbackOnlySocket
            logger.info("✓ Socket layer guarded (loopback-only)")

            # ---- 2. DNS ----
            self._original_getaddrinfo = socket.getaddrinfo

            def _loopback_only_getaddrinfo(host, *args, **kwargs):
                if not _is_loopback(host):
                    raise socket.gaierror(
                        -2, f"Offline mode: cannot resolve non-loopback host {host!r}"
                    )
                return self._original_getaddrinfo(host, *args, **kwargs)

            socket.getaddrinfo = _loopback_only_getaddrinfo
            logger.info("✓ DNS resolution guarded (loopback-only)")

            # ---- 3. urllib ----
            self._original_urlopen = urllib.request.urlopen

            def _loopback_only_urlopen(url, *args, **kwargs):
                target = url
                if hasattr(url, "full_url"):
                    target = url.full_url
                if isinstance(target, str):
                    parsed = urllib.parse.urlparse(target)
                    if parsed.hostname and not _is_loopback(parsed.hostname):
                        raise urllib.error.URLError(
                            f"Offline mode: blocked HTTP request to {parsed.hostname}"
                        )
                return self._original_urlopen(url, *args, **kwargs)

            urllib.request.urlopen = _loopback_only_urlopen
            logger.info("✓ urllib.request guarded (loopback-only)")

            # ---- 4. http.client ----
            self._original_http_connection = http.client.HTTPConnection
            self._original_https_connection = http.client.HTTPSConnection
            _orig_http = self._original_http_connection
            _orig_https = self._original_https_connection

            class _GuardedHTTPConnection(_orig_http):
                def __init__(self, host, *a, **kw):
                    if not _is_loopback(host):
                        raise http.client.HTTPException(
                            f"Offline mode: blocked HTTP connect to {host!r}"
                        )
                    super().__init__(host, *a, **kw)

            class _GuardedHTTPSConnection(_orig_https):
                def __init__(self, host, *a, **kw):
                    if not _is_loopback(host):
                        raise http.client.HTTPException(
                            f"Offline mode: blocked HTTPS connect to {host!r}"
                        )
                    super().__init__(host, *a, **kw)

            http.client.HTTPConnection = _GuardedHTTPConnection
            http.client.HTTPSConnection = _GuardedHTTPSConnection
            logger.info("✓ http.client guarded (loopback-only)")

            # ---- 5. Wipe proxy env vars ----
            proxy_vars = ["http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY",
                          "ftp_proxy", "FTP_PROXY", "no_proxy", "NO_PROXY",
                          "all_proxy", "ALL_PROXY"]
            for var in proxy_vars:
                if var in os.environ:
                    os.environ.pop(var)

            self._blocked = True
            logger.warning("🔒 OFFLINE MODE ENABLED — external network blocked, loopback preserved")
            return True

        except Exception as e:
            logger.critical(f"Network blocking failed: {e}")
            raise RuntimeError(f"Cannot enable offline mode: {e}")

    def verify_network_blocked(self) -> bool:
        if not self._blocked:
            logger.error("Network blocking not enabled")
            return False
        try:
            socket.getaddrinfo("example.com", 80)
            logger.error("FAILED: external DNS lookup should have been blocked")
            return False
        except socket.gaierror:
            pass
        except Exception:
            pass
        try:
            socket.getaddrinfo("localhost", 80)
        except Exception as e:
            logger.error(f"FAILED: loopback DNS broken: {e}")
            return False
        return True


_network_blocker = NetworkBlocker()


def enable_offline_mode() -> bool:
    """Enable offline mode globally (loopback preserved). Call at startup."""
    return _network_blocker.enable_offline_mode()


def verify_network_blocked() -> bool:
    """Verify offline mode is active (convenience function for tests)."""
    return _network_blocker.verify_network_blocked()


import contextlib as _contextlib


@_contextlib.contextmanager
def temporarily_allow_network():
    """
    Temporarily restore real networking for ONE explicit, user-initiated
    operation: downloading the local AI model. Restores the original socket /
    urllib / http.client primitives for the duration, then re-installs the block.

    If offline mode was never enabled this is a no-op. Single-user localhost tool:
    the window is the user-triggered model download only.
    """
    nb = _network_blocker
    if not nb._blocked:
        yield
        return
    saved = (
        socket.socket, socket.getaddrinfo, urllib.request.urlopen,
        http.client.HTTPConnection, http.client.HTTPSConnection,
    )
    socket.socket = nb._original_socket
    socket.getaddrinfo = nb._original_getaddrinfo
    urllib.request.urlopen = nb._original_urlopen
    http.client.HTTPConnection = nb._original_http_connection
    http.client.HTTPSConnection = nb._original_https_connection
    logger.warning("🌐 Network temporarily ALLOWED for explicit model download")
    try:
        yield
    finally:
        (socket.socket, socket.getaddrinfo, urllib.request.urlopen,
         http.client.HTTPConnection, http.client.HTTPSConnection) = saved
        logger.warning("🔒 Network block RE-INSTATED after model download")
