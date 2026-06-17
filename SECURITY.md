# Security Policy

AMS JobAssist is an offline desktop application that handles potentially
sensitive participant data (course participants in vulnerable labour-market
situations). Security issues are taken seriously.

## Supported versions

| Version | Status |
|---|---|
| `main` branch | ✅ Supported — latest commits receive security fixes |
| Tagged releases ≤ 6 months old | ✅ Supported |
| Older tagged releases | ⚠️ Best-effort — please upgrade |

## Reporting a vulnerability

**Do not open a public GitHub issue.** Send a private report instead.

- Email: `security@ams-jobassist.example` *(replace with the maintainer's real address before publishing)*
- Subject line: `[security] short description`
- Encrypted reports welcome — request a PGP key in the first message

### What to include

1. **Affected version** — commit SHA or release tag
2. **Affected component** — Tool 1, Tool 2, packaging, or shared schema
3. **Reproduction steps** — minimum input required to trigger
4. **Suspected impact** — data exposure, privilege escalation, denial of service, etc.
5. **Suggested fix** — optional but appreciated

## Response timeline

| Severity | Acknowledgement | Patch or workaround |
|---|---|---|
| Critical (data leak, RCE, auth bypass) | within 72 hours | 30 days |
| High (DoS, persistent XSS, audit-log tampering) | within 5 working days | 60 days |
| Medium / low | within 10 working days | 90 days |

If you do not receive an acknowledgement within the window, please follow up.
The maintainer is one person and time-zone differences may delay replies.

## Disclosure policy

Coordinated disclosure. We will:

1. Confirm the vulnerability and assign a tracking ID
2. Develop and test a fix on a private branch
3. Coordinate a release date with you
4. Publish the fix, release notes, and a CVE if applicable
5. Credit the reporter in the release notes — unless you request anonymity

We ask reporters not to publicly disclose the issue until a patched release
is available. Typical window: 90 days from acknowledgement.

## Scope

### In scope

- Source code in this repository
- The published `.exe` artifacts produced by `build_all.bat`
- The documented API surface (`API_DOCUMENTATION.md`)
- DSGVO / GDPR compliance assertions in `PRIVACY_ENFORCEMENT.md`
- The bundled HuggingFace model download flow (`ai/local_llm.py`)

### Out of scope

- UI cosmetic issues that don't enable exfiltration
- Theoretical attacks requiring physical possession of an unlocked, logged-in
  trainer laptop (we recommend BitLocker — see `docs/DPIA.md`)
- Social engineering of the trainer (e.g. tricking a trainer into running
  `python eval(...)` from a participant-supplied script)
- Issues in third-party dependencies that are not exploitable through
  AMS JobAssist's documented usage
- Issues in user-supplied content (a participant typing a payload into the
  answer field — that text is escaped on every render path; the threat
  model is malicious *content*, not malicious *use*)

## Hardening assumptions documented in the code

- Tool 1 binds to `127.0.0.1` only. Exposing it on `0.0.0.0` would be a
  configuration mistake, not a vulnerability in JobAssist.
- Tool 2's API-key auth is enforced only when `AMS_TRAINER_API_KEY` is set in
  the environment. The startup warning tells the trainer this; we do not
  treat "trainer didn't set the env var" as a vulnerability.
- The Qwen2.5-3B GGUF model is **downloaded by the installer during setup** — it
  fetches the GGUF over HTTPS from HuggingFace and verifies it against the SHA-256
  pinned in `ai/local_llm.py`, then stores it in `data/models/` beside the app
  (this step can be skipped, leaving the app in rule-based mode). The same pinned-
  hash verification guards the in-app "download a different tier" path, which
  refuses any tier with no pin unless `AMS_ALLOW_UNPINNED_MODEL=1` is set (the
  `light`/0.5B tier is currently unpinned). **At runtime the app itself downloads
  nothing.** If you can produce a model artifact whose hash matches and that
  contains malicious behaviour, that is in scope.

## Hall of fame

Reporters who responsibly disclose security issues will be listed here with
their permission.

| Date | Reporter | Issue |
|---|---|---|
| — | — | No vulnerabilities reported yet |
