# Auftragsverarbeitungsvertrag (AVV) — AMS JobAssist

**Template type**: Data Processing Agreement template per GDPR Art. 28
**Software**: AMS JobAssist v1.0
**Document version**: 1.0 (template — fill in parties before signature)
**Last revised**: 2026-05-13

> This template is provided for completeness. **In the current AMS JobAssist
> architecture the software maintainer is NOT a processor under Art. 28** —
> the maintainer never receives, sees, or has any technical means to access
> personal data, because the entire application runs on the AMS trainer's
> laptop and the network blocker (`PRIVACY_ENFORCEMENT.md` §3) prevents any
> outbound traffic. This document therefore primarily *confirms* the absence
> of processing, rather than authorising it.
>
> If AMS later procures hosted support, remote diagnostics, or a managed
> deployment from the maintainer, this template must be re-signed with the
> "Gegenstand der Vereinbarung" section rewritten to describe the actual
> processing.

---

## Parteien (Parties)

**Verantwortlicher (Controller)**
Arbeitsmarktservice Österreich
_(Adresse, UID, vertretungsbefugte Person — to be filled in by AMS)_

**Auftragsverarbeiter / [Verantwortlicher Anbieter] (Processor / Software maintainer)**
_(Name, Adresse, UID, vertretungsbefugte Person — to be filled in)_

— hereinafter "der Anbieter" / "the maintainer".

---

## Gegenstand der Vereinbarung (Subject of the Agreement)

The maintainer provides the AMS JobAssist software (Tool 1 — CV Maker, Tool 2 —
Trainer Dashboard) to AMS as an offline desktop application. The software is
delivered as installable binaries; no software-as-a-service component is
provided.

**The maintainer is not a processor** in the sense of Art. 4(8) GDPR for the
following reasons:

1. The software runs entirely on AMS-controlled hardware (the trainer's
   laptop) under AMS-controlled accounts.
2. The network egress blocker (`tool-1-cv-maker/src/backend/privacy/network_block.py`)
   prevents any non-loopback connection at the socket layer, so participant
   data has no technical path to the maintainer's systems.
3. No telemetry, crash reports, license check, or update channel is
   implemented. The maintainer receives nothing.

This agreement records that fact, defines the obligations that remain
nonetheless (maintenance updates, security disclosure, sub-processing if
ever activated), and serves as the documented confirmation that AMS — as
controller — has discharged its Art. 28 due-diligence obligation.

---

## Pflichten des Anbieters (Obligations of the maintainer)

The maintainer commits to:

1. **No data access.** The maintainer will not request, accept, or retain
   any personal data from AMS in connection with the software. If a
   participant's data is sent by mistake (e.g. attached to a support
   email), the maintainer will delete it without inspection and notify
   AMS in writing within 72 hours.
2. **Maintenance updates.** Security and bug-fix releases will be made
   available on the public repository (`github.com/.../AMS-JobAssist`) with
   release notes describing every change that touches the privacy
   surface area.
3. **Security disclosure.** Confirmed vulnerabilities affecting the
   privacy guarantees in `PRIVACY_ENFORCEMENT.md` will be reported to the
   AMS DPO contact (named in this AVV) before public disclosure, with at
   least 14 days' lead time for AMS to patch.
4. **Build reproducibility.** The packaged Windows / macOS / Linux binary
   will be reproducible from the public source tree at a tagged commit so
   AMS IT can verify that no undocumented code is included.
5. **No sub-contracting** of any maintenance activity that would require
   access to AMS data without prior written consent from AMS.

---

## Pflichten der AMS (Obligations of AMS)

AMS as controller commits to:

1. **Laptop security.** Mandate full-disk encryption (BitLocker, FileVault,
   or LUKS) on every device that runs AMS JobAssist (see DPIA §6.3 and
   §10).
2. **Trainer authentication.** Configure `AMS_TRAINER_API_KEY` to a strong
   random value (≥ 32 characters) on every trainer laptop and rotate the
   key per cohort (Tool 2 `config.py` line 47).
3. **Retention configuration.** Set `AMS_DATA_RETENTION_DAYS` to a value
   appropriate for the course cycle (default 90; see `RETENTION_POLICY.md`).
4. **Trainer training.** Ensure trainers know how to operate the
   participant-rights endpoints (Art. 15 export, Art. 17 deletion) and have
   read the consent text the participant signs.
5. **Course-end deletion.** Run a bulk export and then the deletion sweep
   at the end of each course cycle (see `RETENTION_POLICY.md` §
   "What AMS must do at course end").
6. **Compliance verification.** Run `ComplianceChecker.generate_compliance_report()`
   at least once per course start and retain the output for the DPO file.

---

## Sub-Auftragsverarbeitung (Sub-processing)

**No sub-processors are engaged** in the standard deployment of AMS
JobAssist.

The one exception is the optional download of the local LLM weights from
HuggingFace at install time. This is:

- a **one-time download** of model weights (a binary file) that occurs
  before any participant data exists on the laptop;
- **technically not personal-data processing** — the request transmits
  only the model identifier and standard HTTP headers (User-Agent, Accept);
- entirely **optional** — if AMS sets `AMS_DISABLE_AI=1` or simply does not
  run the one-time installer step, the rule-based polish layer is used
  exclusively and HuggingFace is never contacted.

If AMS chooses to skip the LLM, this section becomes inapplicable. If AMS
chooses to enable it, the download is performed on AMS's own infrastructure
(the trainer's laptop) by AMS personnel, and HuggingFace acts only as a
software distribution service, not as a sub-processor of personal data.

---

## Datenschutzverletzung (Breach notification)

Should the maintainer become aware of any incident that could plausibly
affect the privacy guarantees in `PRIVACY_ENFORCEMENT.md` (for example: a
discovered bypass of the network blocker, a regression in
`DataDeletion.delete_user_data()`, an SQLite injection vector in the
trainer dashboard), the maintainer will:

1. Notify the AMS DPO contact within **24 hours** of becoming aware.
2. Provide the technical description, affected code paths, exploitation
   prerequisites, and a draft mitigation.
3. Coordinate with AMS on the disclosure timeline so AMS has the legally
   required window under Art. 33 / Art. 34 GDPR to assess whether onward
   notification to the supervisory authority and / or data subjects is
   required.

Because the maintainer holds no personal data, the maintainer's role in a
breach is technical disclosure — not data-subject notification.

---

## Vertragslaufzeit und Beendigung (Term and termination)

This agreement is effective from signature and runs for as long as AMS
deploys AMS JobAssist. Either party may terminate with 90 days' written
notice. On termination:

1. The maintainer ceases security-update support (with at least 90 days'
   handover to allow AMS to fork and self-maintain).
2. AMS retains the right to continue using the version it has under the
   software's open-source licence (MIT).
3. No data needs to be returned or destroyed because the maintainer holds
   none.

---

## Schlussbestimmungen (Final provisions)

- **Applicable law**: Austrian law (österreichisches Recht), with the
  exception of conflict-of-law rules.
- **Venue**: Vienna (Gerichtsstand Wien).
- **Language**: This template is bilingual; in case of conflict between
  the German section headings and the English explanatory text, the
  German section heading governs.
- **Severability**: Should any clause be unenforceable, the remainder
  remains in effect.
- **Amendments**: Material amendments must be in writing and signed by
  both parties.

---

## Anlage 1: Liste der Datenkategorien (Annex 1: List of data categories)

The categories below mirror DPIA §3.1. They are listed here so that the
controller's Art. 30 record-of-processing references this annex by name.

| Category               | Examples                                            | Optional? |
| ---------------------- | --------------------------------------------------- | --------- |
| Identifying data       | First name, last name                               | no        |
| Contact data           | Phone, email, postal address                        | yes       |
| Location               | City, country                                       | no        |
| Employment history     | Employer name, role, dates, daily tasks, tools     | no        |
| Education              | Institution, qualification, dates                   | no        |
| Skills                 | Free text + normalised labels                       | no        |
| Languages              | Language and self-assessed level                    | yes       |
| Photo                  | Headshot uploaded by participant                    | yes       |
| Derived quality scores | 0–1 score per answer; not persisted                  | n/a       |

Special categories under Art. 9 are **not requested** by the application.
Should a participant voluntarily include them in a free-text answer, the
application treats them as ordinary text and the Art. 17 erasure path
remains available.

---

## Anlage 2: Technisch-organisatorische Maßnahmen (Annex 2: Technical and organisational measures)

The TOM below are implemented in code and verifiable via
`ComplianceChecker.generate_compliance_report()`.

- **Offline-by-default network policy.** Four-layer egress blocker
  (`privacy/network_block.py`) covers `socket.connect`, `getaddrinfo`,
  `urllib.request.urlopen`, and `http.client.HTTP(S)Connection`. Proxy
  environment variables are unset at startup.
- **Loopback-only binding.** FastAPI binds to `127.0.0.1` only.
- **Authentication on trainer dashboard.** `AMS_TRAINER_API_KEY` Bearer
  token required on every Tool 2 endpoint.
- **Privacy-filtered logging.** `PrivacyFilter` redacts emails, phones,
  dates, addresses, UUIDs, and tax IDs from the root logger.
- **Audit log of exports.** `ExportLog` table in Tool 2 records every
  export (who, when, format, file size). `exports` table in Tool 1
  records every participant-initiated export.
- **Foreign-key cascade for erasure.** SQLite `PRAGMA foreign_keys = ON`
  is enforced; `DataDeletion.delete_user_data()` performs the cascade and
  verifies it post-deletion.
- **Bounded retention.** `AMS_DATA_RETENTION_DAYS` (default 90) drives
  the 24-hour cleanup loop in `app.py` and the admin endpoint
  `POST /api/interview/admin/cleanup-sessions`.
- **Recommended encryption at rest.** Full-disk encryption is a
  prerequisite at the OS layer; not implemented inside the application.
- **Compliance self-check.** `privacy/compliance.py` produces a
  human-readable report covering all of the above.

---

## Unterschriften (Signatures)

| Role                                | Name              | Signature | Date       |
| ----------------------------------- | ----------------- | --------- | ---------- |
| AMS (Verantwortlicher)              | _to be filled in_ |           |            |
| Anbieter (Software maintainer)      | _to be filled in_ |           |            |

---

**File**: `AMS-JobAssist/docs/DPA_TEMPLATE.md`
**Related**: `AMS-JobAssist/docs/DPIA.md`, `AMS-JobAssist/PRIVACY_ENFORCEMENT.md`
