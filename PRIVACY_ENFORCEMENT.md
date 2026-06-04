# AMS JobAssist — Privacy Enforcement (Security Specification)

**Purpose**: Technical reference describing how the offline / data-protection
guarantees in AMS JobAssist are actually implemented in code.
**Audience**: DSGVO auditors, security reviewers, AMS IT staff, developers.
**Scope**: Tool 1 (CV Maker) backend. Tool 2 (Trainer Dashboard) is referenced
where relevant (e.g. the `ExportLog` audit table).
**Last revised**: 2026-05-12

---

## 1. What changed (May 2026)

An earlier revision of the network-blocking module took an "all or nothing"
approach: it monkey-patched `socket.socket`, `urllib.request.urlopen`,
`http.client.HTTPConnection.connect`, `ssl.wrap_socket`, and the entire
`requests` library to unconditionally raise `RuntimeError("Network access
blocked")` on any call.

That approach was correct in spirit (no data ever leaves the machine) but
broke the application: FastAPI / uvicorn cannot accept HTTP requests if the
`socket` module is poisoned, because the listening socket itself is a socket.
The server would refuse to start, or start and immediately become
unreachable on `http://127.0.0.1:8000`.

As of 2026-05-12, `tool-1-cv-maker/src/backend/privacy/network_block.py` has
been rewritten around a **loopback allowlist**:

- `127.0.0.0/8`, `::1`, and `localhost` (incl. `ip6-localhost`, `ip6-loopback`)
  remain fully functional so that FastAPI can bind, uvicorn can accept
  connections, and the browser UI can talk to the backend.
- Every other destination is rejected at the socket / DNS / HTTP layer.
- Offline mode is **on by default**. The check at the top of `app.py` reads
  `AMS_ENFORCE_OFFLINE` and treats anything except `"0" / "false" / "no"`
  as "enabled". Production deployments inherit the default; only developers
  who explicitly need outbound network set `AMS_ENFORCE_OFFLINE=0`.
- Proxy environment variables are wiped at startup to prevent the standard
  bypass where an attacker (or accidentally-set OS proxy) routes calls
  through an external proxy that looks like loopback.

The privacy guarantee is unchanged: **participant data never leaves the
machine.** The implementation is now compatible with a running web server.

---

## 2. One-paragraph summary

At startup, `enable_offline_mode()` monkey-patches four points in the Python
standard library so that any attempt to open a non-loopback socket, resolve a
non-loopback hostname, or issue an HTTP/HTTPS request to a non-loopback URL
fails fast with an exception. Loopback traffic is unaffected, so the FastAPI
server, the browser frontend, and any in-process tests that hit
`http://127.0.0.1` continue to work normally. The function is idempotent and
exposes a companion `verify_network_blocked()` that performs four positive /
negative tests and is used by the compliance checker. Defense in depth is
provided by also clearing `HTTP_PROXY` / `HTTPS_PROXY` / `ALL_PROXY` (and
their lowercase variants) from the process environment.

---

## 3. The four defense layers

All code below is taken verbatim from
`tool-1-cv-maker/src/backend/privacy/network_block.py`.

### 3.1 Layer 1 — Socket factory

`socket.socket` is replaced by a subclass whose `connect()` and
`connect_ex()` inspect the address and refuse anything that is not
loopback. This is the lowest-level enforcement point: every higher-level
network library (urllib, requests, httpx, aiohttp, smtplib, …) eventually
calls `socket.connect()`, so this layer alone catches most exfiltration
attempts.

```python
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

socket.socket = _LoopbackOnlySocket
```

Note that the class **inherits** from the original `socket.socket`, so the
listening side of the server (`bind`, `listen`, `accept`) is untouched —
those methods do not call `connect()`.

### 3.2 Layer 2 — DNS resolution (`socket.getaddrinfo`)

Even if a caller bypasses Layer 1 with a hardcoded IP, they typically obtain
that IP by resolving a hostname first. Layer 2 wraps `getaddrinfo` so that
any non-loopback hostname raises `socket.gaierror` (DNS lookup failed)
instead of returning the real address.

```python
self._original_getaddrinfo = socket.getaddrinfo

def _loopback_only_getaddrinfo(host, *args, **kwargs):
    if not _is_loopback(host):
        raise socket.gaierror(
            -2, f"Offline mode: cannot resolve non-loopback host {host!r}"
        )
    return self._original_getaddrinfo(host, *args, **kwargs)

socket.getaddrinfo = _loopback_only_getaddrinfo
```

`gaierror(-2)` corresponds to `EAI_NONAME`, which is the standard "name or
service not known" error — so callers handle it the same way they would
handle a real DNS failure on a disconnected machine.

### 3.3 Layer 3 — `urllib.request.urlopen`

`urllib.request.urlopen` is wrapped so it parses the target URL and rejects
any non-loopback hostname with `urllib.error.URLError` **before** opening a
connection. This is partly redundant with Layer 1 / 2 but produces a clearer
exception type for code that catches `URLError` specifically, and it
short-circuits before any DNS lookup happens.

```python
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
```

### 3.4 Layer 4 — `http.client.HTTPConnection` / `HTTPSConnection`

Code that builds its own HTTP request via `http.client` rather than going
through `urllib.request` would skip Layer 3. Layer 4 replaces both
`HTTPConnection` and `HTTPSConnection` with guarded subclasses that refuse
non-loopback hosts in the constructor — so the connection object cannot
even be instantiated for an external destination.

```python
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
```

### 3.5 Proxy environment hygiene

After the four layers are installed, the proxy-related environment variables
are unset so a malicious or misconfigured process cannot route traffic
through an external proxy (which from `urllib`'s perspective looks like a
plain HTTP destination):

```python
proxy_vars = ["http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY",
              "ftp_proxy", "FTP_PROXY", "no_proxy", "NO_PROXY",
              "all_proxy", "ALL_PROXY"]
for var in proxy_vars:
    if var in os.environ:
        os.environ.pop(var)
```

This is "belt and braces" — the four layers already block proxy hosts the
same way they block any other non-loopback host — but it removes one whole
class of misconfiguration.

---

## 4. What is allowed vs. blocked

The allowlist predicate `_is_loopback()` (lines 37–53 of `network_block.py`)
is the single source of truth.

| Destination                    | Resolved as | Effect    |
| ------------------------------ | ----------- | --------- |
| `localhost`                    | hostname    | ALLOWED   |
| `ip6-localhost`, `ip6-loopback`| hostname    | ALLOWED   |
| `127.0.0.1`                    | IPv4        | ALLOWED   |
| `127.0.0.2`, `127.255.255.254` | IPv4        | ALLOWED   |
| any other `127.x.x.x`          | IPv4        | ALLOWED   |
| `::1`                          | IPv6        | ALLOWED   |
| `0:0:0:0:0:0:0:1`              | IPv6        | ALLOWED   |
| `None` (e.g. AF_UNIX)          | n/a         | ALLOWED   |
| `0.0.0.0`                      | IPv4        | BLOCKED   |
| `10.x.x.x`, `192.168.x.x`      | IPv4 LAN    | BLOCKED   |
| `example.com`, any public DNS  | hostname    | BLOCKED   |
| public IPs (e.g. `8.8.8.8`)    | IPv4        | BLOCKED   |
| any IPv6 outside `::1`         | IPv6        | BLOCKED   |

The predicate is case-insensitive on hostnames and accepts both `bytes`
and `str`. A hostname of `None` is treated as loopback so that AF_UNIX
sockets (used internally on POSIX) continue to work.

Note: LAN addresses (`192.168.x.x`, `10.x.x.x`) are deliberately blocked.
Even though they do not reach the public internet, "stays on this machine"
is a stricter and clearer guarantee than "stays on this LAN", and AMS
classrooms commonly share a router.

---

## 5. How to verify in production

The module exposes `verify_network_blocked()` which performs four
independent checks against the live, patched runtime:

```python
def verify_network_blocked(self) -> bool:
    # Test 1: External DNS lookup must fail
    try:
        socket.getaddrinfo("example.com", 80)
        return False  # FAIL: should have raised
    except socket.gaierror:
        pass

    # Test 2: External HTTP request must fail
    try:
        urllib.request.urlopen("http://example.com", timeout=1)
        return False  # FAIL: should have raised
    except urllib.error.URLError:
        pass

    # Test 3: Loopback DNS must still work
    socket.getaddrinfo("localhost", 80)   # must not raise

    # Test 4: Proxy variables must be cleared
    for var in ("http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY"):
        if var in os.environ:
            return False

    return True
```

This function is exercised by the test suite (`test_verify_network_blocked`
in `tests/test_privacy.py`) and is also called from
`ComplianceChecker.verify_all_requirements()` to populate the
`network_blocked` field of the compliance report.

Auditors who want to verify the running system manually can either:

1. Hit `GET /health` from the same machine over `http://127.0.0.1:<PORT>`
   (must return `200`), then attempt the same call against any external
   host from inside a Python REPL in the same process (must raise).
2. Call `verify_network_blocked()` directly via the Python REPL attached
   to the running process.

**Honest disclosure**: no third-party penetration test of the network
blocker has been conducted to date. The guarantees above are derived from
code review and the in-repo test suite. A pen-test against a packaged
release is planned but not scheduled.

---

## 6. How to disable for development

Offline mode is on by default. To run the backend with full outbound
network access — for example, while integrating a new optional AI engine —
set the environment variable before launching:

```powershell
$env:AMS_ENFORCE_OFFLINE = "0"
python -m uvicorn app:app
```

Or on POSIX:

```bash
AMS_ENFORCE_OFFLINE=0 python -m uvicorn app:app
```

Recognised "disabled" values are `"0"`, `"false"`, `"no"` (case-insensitive).
Anything else, including the empty string and the variable being unset, is
treated as **enabled**. The guard in `app.py` is:

```python
if os.environ.get("AMS_ENFORCE_OFFLINE", "1").lower() not in ("0", "false", "no"):
    from privacy.network_block import enable_offline_mode
    enable_offline_mode()
```

Packaged AMS classroom builds ship without `AMS_ENFORCE_OFFLINE` defined,
so they take the default-enabled path.

---

## 7. Right to erasure — `data_deletion.py`

DSGVO Article 17 ("Right to be forgotten") is implemented in
`tool-1-cv-maker/src/backend/privacy/data_deletion.py` via the `DataDeletion`
class. `delete_user_data(user_id, export_dir=None)`:

1. Verifies the user exists in the `users` table.
2. Counts related rows (sessions, answers) for the audit log.
3. Issues `DELETE FROM users WHERE user_id = ?`. SQLite foreign keys
   (`ON DELETE CASCADE`) propagate the deletion to `sessions`, `answers`,
   `cv_data`, and `exports`.
4. If `export_dir` is supplied, removes every file in that directory whose
   filename contains the `user_id` (this is how PDF / DOCX / JSON exports
   are named).
5. Re-queries the `users` table and returns `False` if any row is left.
6. Writes an audit-level WARNING log entry on success.

Companion helpers:

- `verify_user_deleted(user_id)` re-runs the four count queries
  (`users`, `sessions`, `answers`, and answer-cascade) and returns `True`
  only if all four return zero. Used by tests and by the compliance
  checker's deletion check.
- `get_user_data_size(user_id)` returns a deletion-preview dict
  (`sessions_to_delete`, `answers_to_delete`, `cv_records_to_delete`,
  `estimated_size_kb`) so the UI can show the participant exactly what
  will be removed before they confirm.

The operation is **irreversible**. There is no soft-delete column and no
trash bin. Once `delete_user_data()` returns `True`, the row is gone.

---

## 8. Right to data portability — `GET /api/cv/{session_id}/my-data`

DSGVO Article 20 ("Right to data portability") is served by the endpoint
defined in `tool-1-cv-maker/src/backend/app.py` (lines 327–363). It returns
a single JSON file containing:

- A `notice` field in German citing Article 20 DSGVO.
- The `session_id`.
- `raw_answers`: every row from the `answers` table for that session, in
  insertion order, with `question_id`, `answer_text`, and `created_at`.
- `cv_data`: the polished CV as a dict (the same shape that the export
  engines consume), or `null` if the user has not yet completed the
  interview.
- `exported_at`: ISO-8601 timestamp.

The response is served with
`Content-Disposition: attachment; filename=meine-daten-<session_id>.json`,
so the browser saves it directly. The data leaves the server only over
loopback (the participant is sitting at the same machine, by design) and is
not retained anywhere else — there is no log of the export beyond the
generic request log.

If the session has no answers, the endpoint returns `404` with a German
detail message rather than an empty file.

---

## 9. Audit logging — `ExportLog`

Tool 2 (the trainer dashboard) maintains an `ExportLog` table for every
file a trainer exports. Schema is defined in
`tool-2-trainer-dashboard/src/backend/models.py` (lines 105–121):

| Column            | Type         | Purpose                                  |
| ----------------- | ------------ | ---------------------------------------- |
| `id`              | Integer PK   |                                          |
| `participant_id`  | Integer, idx | which participant                        |
| `submission_id`   | Integer, idx | which submission revision                |
| `export_format`   | String(50)   | `pdf` / `docx` / `json`                  |
| `export_language` | String(5)    | output language                          |
| `file_path`       | String(255)  | on-disk path of the exported file        |
| `file_size`       | Integer      | bytes                                    |
| `exported_at`     | DateTime     | server-local timestamp, defaults to now  |
| `exported_by`     | String(255)  | trainer identifier                       |

Tool 1 also writes its own export records via `_log_export()` in
`app.py` into the `exports` table (`session_id`, `export_type`,
`file_path`, `file_size`, `export_language`). The Tool 1 log does not have
a `who exported` field because Tool 1 is single-user — the participant
themselves is always the actor.

There is intentionally no off-machine audit sink. The logs are part of the
same SQLite database that the rest of the data lives in, and they are
covered by the same `delete_user_data()` cascade.

---

## 10. Data retention — `AMS_DATA_RETENTION_DAYS`

Long-lived participant data is undesirable from a DSGVO standpoint
(Article 5(1)(e), "storage limitation"). The retention loop in
`app.py` lifespan (lines 126–151) handles this:

```python
from config import DATA_RETENTION_DAYS

async def _retention_loop(engine, days):
    while True:
        deleted = engine.cleanup_old_sessions(days)
        if deleted:
            logger.info(f"Data retention: removed {deleted} sessions older than {days} days")
        await asyncio.sleep(86_400)  # 24 h
```

`DATA_RETENTION_DAYS` resolves from the environment variable
`AMS_DATA_RETENTION_DAYS`. **Default: `365` days** (a finite ceiling, not
"forever"). Set it to `0` to disable automatic purging (you then take on the
deletion obligation manually). The cleanup runs once at startup and then every
24 hours. `cleanup_old_sessions()` enforces a **two-tier** policy: abandoned
drafts are purged after 30 days, and **every** session — completed, approved
and locked included — is purged once it passes the `DATA_RETENTION_DAYS`
ceiling. Foreign-key cascades remove answers, CV data, consent records, and
export records along with them. (Earlier versions kept approved/locked CVs
indefinitely; that inverted storage limitation and has been fixed.)

Recommended classroom settings:

- **AMS instructor workstations**: `AMS_DATA_RETENTION_DAYS=30`. A
  participant's data survives long enough to finish a multi-session
  course but does not accumulate across cohorts.
- **Shared / kiosk installations**: `AMS_DATA_RETENTION_DAYS=1` or
  manual deletion after each participant.
- **Single-user installations**: leave unset; the participant manages
  their own deletion via the UI.

---

## 11. Encryption at rest — `AMS_DATADIR_ENCRYPTED` / `AMS_REQUIRE_ENCRYPTION` / `AMS_DB_KEY`

DSGVO Art. 32(1)(a) names encryption as a key technical measure. The SQLite
database holds participant PII; at the file level it is plaintext, so the data
directory **must** sit on an encrypted volume.

Supported controls (in order of preference):

1. **OS full-disk encryption (recommended): BitLocker (Windows) / LUKS (Linux).**
   Encrypt the volume that holds the data dir, then assert it with
   `AMS_DATADIR_ENCRYPTED=1`. To make this mandatory (an AMS-IT policy can refuse
   to run otherwise) also set `AMS_REQUIRE_ENCRYPTION=1` — the app then **refuses
   to start** unless encryption is asserted.
2. **Application-level SQLCipher (optional).** Install a SQLCipher build of the
   driver (`pysqlcipher3`) and set `AMS_DB_KEY` to a strong key. The DB file is
   then encrypted by the engine. Without the driver, `AMS_DB_KEY` is ignored and
   a startup warning is emitted.

If neither is configured the app logs a loud **"PII stored UNENCRYPTED at rest"**
advisory at startup. Do **not** point `AMS_DATA_DIR` at a network share unless
that share is itself encrypted.

---

## 11. Privacy-filtered logging — `privacy/logging_rules.py`

*(Note: the spec previously referred to this file as
`privacy_filter.py`; the actual filename on disk is `logging_rules.py`.
The class inside is `PrivacyFilter`.)*

`PrivacyFilter` is a `logging.Filter` subclass that redacts PII from log
records **before** they reach any handler. The patterns are compiled once
at class-definition time:

| Pattern                                                              | Replacement   |
| -------------------------------------------------------------------- | ------------- |
| `[\w\.-]+@[\w\.-]+\.\w+`                                             | `[EMAIL]`     |
| `\+?[\d\s\-\(\)]{10,}` (phone)                                       | `[PHONE]`     |
| `\d{1,4}[-/.]\d{1,2}[-/.]\d{1,4}` (date)                             | `[DATE]`      |
| `https?://(?!localhost)[^\s]+`                                       | `[URL]`       |
| 16-digit card numbers                                                 | `[CARD]`      |
| `\d{3}-\d{2}-\d{4}` (SSN)                                            | `[SSN]`       |
| 11-digit German tax ID                                                | `[TAX_ID]`    |
| `[a-f0-9]{32,}` (hash-like)                                          | `[HEX_ID]`    |
| Standard UUID                                                         | `[UUID]`      |
| `/home/<user>` or `C:\Users\<user>`                                  | `[HOME_DIR]` / `[USER_DIR]` |
| German postal addresses                                               | `[ADDRESS]`   |

`filter()` redacts `record.msg`, `record.args` (both dict and tuple
shapes), and `record.exc_text`, then returns `True` so the line is still
emitted — just with the sensitive substrings replaced.

`enable_global_privacy_filtering()` attaches a `PrivacyFilter` to the root
logger so the filter applies to every child logger created anywhere in the
codebase.

**Known limitations** (documented honestly for the audit):

- The "URL" pattern explicitly carves out `localhost`, but other loopback
  forms (`127.0.0.1`, `::1`) are not carved out and will be redacted as
  `[URL]`. This is harmless (loopback URLs are not PII) but means logs
  about the server's own endpoints look noisier than they need to.
- The phone regex (10+ digits with separators) can match long numeric IDs
  that are not phone numbers and replace them with `[PHONE]`. This is a
  deliberate false-positive trade-off in favour of privacy.
- The filter does not redact free-text content that the user *typed*
  unless that content matches one of the regexes. Interview answers are
  not logged by the application code at all, which is the intended
  defence; the filter is a backstop for unintentional logging.

---

## 12. Compliance checker — `privacy/compliance.py`

`ComplianceChecker` ties the above pieces together. It accepts a
`db_manager`, a `network_blocker`, and a `privacy_filter`, and exposes:

- `verify_all_requirements()` — returns a dict with one boolean per check
  and an `overall_compliant` aggregate. Checks performed:
  1. `network_blocked` — calls `verify_network_blocked()`.
  2. `logging_filtered` — confirms `PrivacyFilter.PII_PATTERNS` is
     non-empty and the filter is wired in.
  3. `database_schema` — confirms the required tables exist
     (`users`, `sessions`, `interview_questions`, `answers`, `cv_data`,
     `exports`, `skills_dictionary`, `verb_replacements`).
  4. `deletion_mechanism` — confirms the deletion code path is reachable
     (does not actually delete anything).
  5. `no_remote_sync` — checks for the presence of Dropbox / OneDrive /
     Nextcloud / Google Drive markers and known cloud-credential env vars.
     Currently this is a soft warning, not a hard fail, because the
     presence of `AWS_ACCESS_KEY_ID` on the user's machine does not
     necessarily mean AMS JobAssist is using it.
  6. `foreign_keys_enabled` — runs `PRAGMA foreign_keys = ON` and
     verifies the pragma stuck. Required for the deletion cascade.
  7. `audit_logging` — confirms the root logger has at least one handler.

- `generate_compliance_report()` — returns a human-readable plain-text
  report with one section per check, the overall verdict, and a
  recommendation listing the names of any failed checks. This is what
  gets handed to an auditor on request.

The checker is intentionally read-only. It tells you whether the system is
in a compliant state; it never tries to "fix" anything autonomously.

---

## 13. Test coverage — `tests/test_privacy.py`

The privacy machinery is covered by **28 unit tests** in
`tool-1-cv-maker/tests/test_privacy.py`, split across four test classes:

**Network blocking** (7 tests):
- `test_network_blocker_initialization`
- `test_enable_offline_mode`
- `test_enable_offline_mode_idempotent`
- `test_external_socket_connect_blocked`
- `test_external_dns_blocked`
- `test_external_http_blocked`
- `test_verify_network_blocked`

**Privacy filter** (8 tests):
- `test_privacy_filter_initialization`
- `test_email_redaction`
- `test_phone_number_redaction`
- `test_date_redaction`
- `test_uuid_redaction`
- `test_logging_filter_integration`
- `test_redaction_statistics`
- `test_multiple_pii_types`

**Data deletion** (7 tests):
- `test_data_deletion_initialization`
- `test_get_user_data_size`
- `test_verify_user_deleted`
- `test_delete_nonexistent_user_returns_false`
- `test_delete_user_with_no_data`
- `test_complete_user_deletion`
- `test_cascade_delete_sessions_and_answers`

**Compliance checker** (6 tests):
- `test_compliance_checker_initialization`
- `test_network_blocked_check`
- `test_logging_filtered_check`
- `test_database_schema_check`
- `test_overall_compliance`
- `test_compliance_report_generation`

The suite is part of the standard CI run. Adding a new privacy-relevant
code path without a corresponding test is treated as a review-blocking
defect.

---

## 14. Summary table

| Guarantee                                | Implementation                              | Verified by                                  |
| ---------------------------------------- | ------------------------------------------- | -------------------------------------------- |
| No external network at runtime            | 4-layer monkey-patch + proxy env wipe       | `verify_network_blocked()`, 7 unit tests     |
| Loopback (server itself) keeps working    | `_is_loopback()` allowlist                  | `test_verify_network_blocked` Test 3         |
| PII not leaked through logs               | `PrivacyFilter` on root logger              | 8 redaction tests                            |
| Article 17 — Right to erasure             | `DataDeletion.delete_user_data()` + cascade | 7 deletion tests                             |
| Article 20 — Right to portability         | `GET /api/cv/{session_id}/my-data`          | Manual; covered by interview/export tests    |
| Article 5(1)(e) — Storage limitation      | `AMS_DATA_RETENTION_DAYS` + 24h cleanup loop| Inspected at startup logs                    |
| Audit trail for exports                   | `exports` (Tool 1) + `ExportLog` (Tool 2)   | Written on every export call                 |
| Compliance verifiable on demand           | `ComplianceChecker.generate_compliance_report()` | 6 compliance tests                           |

---

## 15. Things that are NOT yet verified

For the avoidance of doubt:

- No external penetration test has been performed against a packaged build.
- The compliance checker's `no_remote_sync` check is a soft warning, not a
  hard fail. A trainer running the tool on a workstation that *also* has
  Dropbox installed will get a clean compliance report; the tool itself
  does not write to Dropbox, but the audit log does not currently prove
  that.
- The DSGVO Article 20 export endpoint is not rate-limited. On a single-
  user offline tool this is acceptable; in a multi-user deployment it
  would need an additional control.
- The `PrivacyFilter` is a regex backstop, not a guarantee. It cannot
  redact PII that is not pattern-matchable (e.g. a participant's free-text
  description of their family situation logged in a future code change).
  The primary defence is that interview content is never passed to the
  logger in the first place.

These are documented here rather than hidden so an auditor can plan
follow-up work.

---

**File**: `AMS-JobAssist/PRIVACY_ENFORCEMENT.md`
**Code under review**:
- `tool-1-cv-maker/src/backend/privacy/network_block.py`
- `tool-1-cv-maker/src/backend/privacy/data_deletion.py`
- `tool-1-cv-maker/src/backend/privacy/logging_rules.py`
- `tool-1-cv-maker/src/backend/privacy/compliance.py`
- `tool-1-cv-maker/src/backend/app.py` (startup guard, retention loop, `/my-data` endpoint)
- `tool-2-trainer-dashboard/src/backend/models.py` (`ExportLog`)
- `tool-1-cv-maker/tests/test_privacy.py`
