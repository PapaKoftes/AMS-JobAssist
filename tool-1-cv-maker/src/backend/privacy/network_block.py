"""
Offline network enforcement for Tool 1.

⚠️  SINGLE SOURCE OF TRUTH: this module is now a thin re-export of
`shared/utils/network_block.py`. The implementation (socket / DNS / urllib /
http.client loopback-only guards, UDP sendto guard, proxy-var wipe,
verify_network_blocked, temporarily_allow_network) lives there so both tools
share ONE copy and cannot drift. Previously Tool 1 had a duplicate that had
already drifted (it was missing the UDP `sendto` guard).

Import-order note: `enable_offline_mode()` monkey-patches socket primitives, so
it must run before anything caches them (see app.py). The shared module has no
heavy dependencies, so importing it here is safe at startup.
"""

# Ensure the repo root is importable so `shared.*` resolves even when the
# package isn't pip-installed (zip / portable runs).
import sys as _sys
from pathlib import Path as _Path
_repo_root = _Path(__file__).resolve().parents[4]
if str(_repo_root) not in _sys.path:
    _sys.path.insert(0, str(_repo_root))

from shared.utils.network_block import (  # noqa: F401  (re-export)
    NetworkBlocker,
    enable_offline_mode,
    verify_network_blocked,
    temporarily_allow_network,
    _network_blocker,
    _is_loopback,
)
