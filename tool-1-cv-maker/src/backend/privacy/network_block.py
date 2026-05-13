"""
HARD-ENFORCED NETWORK BLOCKING FOR AMS JOBASSIST

Blocks all *external* network access while leaving loopback (127.0.0.1, ::1,
localhost) intact so the FastAPI server itself can bind and accept connections.

⚠️  IMPORT ORDER WARNING  ⚠️
============================================================================
`enable_offline_mode()` monkey-patches `socket.socket`, `socket.getaddrinfo`,
`urllib.request.urlopen`, and `http.client.HTTP[S]Connection`. ANY module
that imported these names BEFORE `enable_offline_mode()` runs will still
hold references to the unblocked originals.

→ Call `enable_offline_mode()` BEFORE importing fastapi, uvicorn, requests,
  urllib3, or anything else that may pre-cache socket primitives.

→ In `app.py` this is enforced by placing the call near the top of the file
  (before fastapi / uvicorn imports). If you add new top-level imports
  earlier than line ~20 of `app.py`, audit them for socket caching.
============================================================================

Enforcement points:
1. Python socket layer  — blocks all non-loopback TCP/UDP connections
2. DNS resolution       — only `localhost` / loopback IPs resolve
3. urllib/http library  — non-loopback URLs raise URLError
4. Proxy env variables  — wiped (prevents proxy bypass)

Design: defense in depth. Loopback is allowed because the offline-first
guarantee in this app is "your data never leaves this machine" — loopback
*is* this machine.
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
        """
        Block all external network access. Loopback (127.0.0.1 / ::1 / localhost)
        is preserved so the local FastAPI server keeps working.

        Returns:
            True if blocking succeeded, False if already blocked.
        """
        if self._blocked:
            logger.warning("Network blocking already enabled (idempotent)")
            return True

        try:
            # ---- 1. Socket factory: wrap so connect() to non-loopback fails ----
            self._original_socket = socket.socket

            _orig_socket = self._original_socket

            class _LoopbackOnlySocket(_orig_socket):
                """Socket subclass that refuses to connect anywhere but loopback."""

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
                        return 1  # EPERM-ish — emulate failed connect
                    return super().connect_ex(address)

            socket.socket = _LoopbackOnlySocket
            logger.info("✓ Socket layer guarded (loopback-only)")

            # ---- 2. DNS: only loopback names resolve ----
            self._original_getaddrinfo = socket.getaddrinfo

            def _loopback_only_getaddrinfo(host, *args, **kwargs):
                if not _is_loopback(host):
                    raise socket.gaierror(
                        -2, f"Offline mode: cannot resolve non-loopback host {host!r}"
                    )
                return self._original_getaddrinfo(host, *args, **kwargs)

            socket.getaddrinfo = _loopback_only_getaddrinfo
            logger.info("✓ DNS resolution guarded (loopback-only)")

            # ---- 3. urllib HTTP opener ----
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

            # ---- 4. http.client direct usage ----
            self._original_http_connection = http.client.HTTPConnection
            self._original_https_connection = http.client.HTTPSConnection

            _orig_http  = self._original_http_connection
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

            http.client.HTTPConnection  = _GuardedHTTPConnection
            http.client.HTTPSConnection = _GuardedHTTPSConnection
            logger.info("✓ http.client guarded (loopback-only)")

            # ---- 5. Wipe proxy env vars (defence in depth) ----
            proxy_vars = ["http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY",
                          "ftp_proxy", "FTP_PROXY", "no_proxy", "NO_PROXY", "all_proxy", "ALL_PROXY"]
            for var in proxy_vars:
                if var in os.environ:
                    os.environ.pop(var)
                    logger.debug(f"Cleared proxy env: {var}")

            self._blocked = True
            logger.warning("🔒 OFFLINE MODE ENABLED — external network blocked, loopback preserved")
            return True

        except Exception as e:
            logger.critical(f"Network blocking failed: {e}")
            raise RuntimeError(f"Cannot enable offline mode: {e}")

    def verify_network_blocked(self) -> bool:
        """
        Verify that *external* network access is blocked while loopback works.

        Returns True if all expected behaviors hold.
        """
        if not self._blocked:
            logger.error("Network blocking not enabled")
            return False

        # Test 1: External DNS lookup must fail
        try:
            socket.getaddrinfo("example.com", 80)
            logger.error("FAILED: external DNS lookup should have been blocked")
            return False
        except socket.gaierror:
            logger.debug("✓ External DNS blocked")
        except Exception as e:
            logger.debug(f"✓ External DNS blocked ({type(e).__name__})")

        # Test 2: External HTTP request must fail
        try:
            urllib.request.urlopen("http://example.com", timeout=1)
            logger.error("FAILED: external HTTP request should have been blocked")
            return False
        except urllib.error.URLError:
            logger.debug("✓ External HTTP blocked")
        except Exception as e:
            logger.debug(f"✓ External HTTP blocked ({type(e).__name__})")

        # Test 3: Loopback DNS must still work
        try:
            socket.getaddrinfo("localhost", 80)
            logger.debug("✓ Loopback DNS preserved")
        except Exception as e:
            logger.error(f"FAILED: loopback DNS broken: {e}")
            return False

        # Test 4: Proxy variables must be cleared
        for var in ("http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY"):
            if var in os.environ:
                logger.error(f"FAILED: proxy variable {var} should have been cleared")
                return False

        logger.info("✓ Network blocking verification: ALL TESTS PASSED")
        return True


# Global instance for easy access
_network_blocker = NetworkBlocker()


def enable_offline_mode() -> bool:
    """
    Enable offline mode globally.

    Call at application startup before any external-network code runs.
    Loopback (127.0.0.1 / ::1 / localhost) is preserved so the FastAPI
    server keeps working.
    """
    return _network_blocker.enable_offline_mode()


def verify_network_blocked() -> bool:
    """Verify offline mode is active (convenience function for tests)."""
    return _network_blocker.verify_network_blocked()
