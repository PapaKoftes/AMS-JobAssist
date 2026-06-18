# AMS JobAssist — Data Protection Impact Assessment (DPIA)

**Document type**: Datenschutz-Folgenabschätzung per GDPR Art. 35
**Template**: Adapted from the EDPB Guidelines on DPIA (WP248 rev.01)
**Controller**: Arbeitsmarktservice Österreich (AMS), or the AMS regional office
deploying the software
**Processor**: None (see §8 — Recipients)
**Software**: AMS JobAssist v1.0 (Tool 1 — CV Maker, Tool 2 — Trainer Dashboard)
**Code under review**: commit head of `AMS-JobAssist` repository as of 2026-05-12
**Document version**: 1.0 (draft for AMS DPO review)
**Last revised**: 2026-05-13

> AMS course participants include long-term unemployed adults, asylum-seekers in
> labour-market integration programmes, persons with reduced earning capacity,
> and minors enrolled in basic-qualification courses. This population falls
> within the scope of GDPR Art. 35(3)(b) ("processing on a large scale of
> special categories of data, or of data relating to vulnerable natural
> persons") and Art. 35(3)(a) ("systematic and extensive evaluation … which
> produce[s] … significant effects"). A DPIA is therefore mandatory.

---

## 1. Scope and purpose

### 1.1 What AMS JobAssist is

AMS JobAssist is an offline-first desktop application used inside AMS training
classrooms in Austria. It consists of two coupled tools that share a SQLite
database on a single trainer laptop:

- **Tool 1 — CV Maker.** A guided interview UI for AMS course participants.
  The participant answers one question per screen (name, location, work
  history, education, skills, optional photo). The application normalises
  free-text input ("office work" → "Microsoft Office (Word, Excel, Outlook)"),
  fixes grammar, and renders a finished CV in PDF, DOCX, or Europass-style
  JSON.
- **Tool 2 — Trainer Dashboard.** A supervisor UI used by the AMS trainer to
  view all participants in the current cohort side-by-side, edit polished CVs
  inline, and bulk-export at the end of the course.

Both tools run on the trainer's laptop. The participant uses the trainer's
laptop (or a classroom laptop on the same machine) and reaches the UI over
loopback (`http://127.0.0.1`).

### 1.2 Who uses it

| Role               | What they do                                              | Volume per cohort |
| ------------------ | --------------------------------------------------------- | ----------------- |
| Course participant | Completes the guided interview, reviews their own CV      | 8 – 20            |
| AMS trainer        | Supervises, edits, approves, exports                       | 1 – 2             |
| AMS IT / DPO       | Configures retention, runs compliance check, audits       | rare              |

### 1.3 Why a DPIA

Per GDPR Art. 35(1), a DPIA is required where processing is "likely to result
in a high risk to the rights and freedoms of natural persons." AMS JobAssist
processes career-history data belonging to vulnerable adults, who are
required by their AMS course agreement to participate. The combination of
mandatory participation + vulnerable population + the possibility that the
data ends up in employer-facing documents triggers Art. 35(3)(b).

### 1.4 Purpose limitation

The sole purpose is the production of a CV (Lebenslauf) document that the
participant can take with them and submit to employers. The data is **not**
used for:

- profiling or automated decision-making affecting the participant's AMS
  benefits;
- training of any AI model (the local AI engine is a frozen weights file —
  see §2.3);
- matching the participant against jobs in any AMS-internal database;
- onward transfer to employers, recruiters, or third parties.

---

## 2. Description of processing operations

### 2.1 Participant flow

```
[Browser at 127.0.0.1]
    │
    │  1. Participant opens consent screen, ticks the Art. 6(1)(a) checkbox
    │  2. Selects an interview path (unemployed / career switch / student /
    │     career pause / other)
    │  3. Types free-text answers, one question per screen
    │     │
    │     ▼
    │   autosave (interview/autosave.py) writes each answer to the
    │   `answers` table in SQLite immediately
    │     │
    │     ▼
    │   polish layer (backend/polish/) rewrites the text:
    │     verb_enforcement, structure_validation, skill_normalization,
    │     language_normalization, confidence_flagging
    │     │
    │     ▼
    │   live preview is rendered to the right pane
    │
    │  4. On completion the participant downloads PDF/DOCX/JSON
    │     via /api/export/{session_id}/{format}
    │
    │  5. Optionally the participant invokes
    │     GET  /api/cv/{session_id}/my-data   (Art. 20 portability)
    │          — requires X-Session-Token or X-User-Id header (IDOR protection)
    │     DELETE /api/cv/{session_id}/erase   (Art. 17 erasure)
    │          — same ownership proof required; calls DataDeletion.delete_user_data()
    │     NOTE: there is NO CLI for erasure — the documented
    │           "python privacy/data_deletion.py --session-id …" does not exist.
```

### 2.2 Trainer flow

```
[Browser at 127.0.0.1 on the same laptop]
    │
    │  1. Trainer authenticates with AMS_TRAINER_API_KEY (Bearer header)
    │  2. JSON import: trainer imports per-participant export JSON produced
    │     by Tool 1 into Tool 2's database
    │     (tool-2-trainer-dashboard/src/backend/import_manager/)
    │  3. Side-by-side review (raw answer vs. polished version)
    │  4. Inline edit → Art. 16 rectification
    │  5. Lock / approve → Art. 18 restriction
    │  6. Bulk export at end of course → PDFs written to disk,
    │     one `ExportLog` row written per file
```

### 2.3 The AI / polish layer

The "polish" step uses a local rule-based engine
(`tool-1-cv-maker/src/backend/polish/`) plus a local LLM
(Qwen2.5-3B-Instruct, Q4_K_M, ~1.9 GB). The LLM weights are **downloaded once
during installation** — the installer fetches the GGUF from HuggingFace over
HTTPS and verifies it by SHA-256, then stores it in `data/models` beside the
executable. This is a **one-time, install-time download performed by the
installer**; **at runtime the model is loaded entirely in-process and the app
fetches nothing.** No participant data ever reaches HuggingFace, OpenAI,
Anthropic, or any other remote service — the only model-related network event is
that one install-time weight download, and the running app performs **no network
egress for the model.** Runtime network egress is enforced by the four-layer
block documented in `PRIVACY_ENFORCEMENT.md` §3.

If the LLM is unavailable, the rule-based engine produces the same shape of
output (deterministic substitution tables for verbs and skills). This is the
fallback referenced in the risk matrix (§9).

---

## 3. Data categories

### 3.1 Personal data processed

| Category               | Examples                                            | Provenance              | Optional? |
| ---------------------- | --------------------------------------------------- | ----------------------- | --------- |
| Identifying data       | First name, last name                               | typed by participant    | no        |
| Contact data           | Phone number, email, postal address                 | typed by participant    | yes       |
| Location               | City, country                                       | typed by participant    | no        |
| Employment history     | Employer name, role, dates, daily tasks, tools used | typed by participant    | no        |
| Education              | Institution, qualification, dates                   | typed by participant    | no        |
| Skills                 | Free-text plus normalised skill labels              | typed + derived         | no        |
| Languages              | Language and self-assessed level                    | typed by participant    | yes       |
| Photo                  | Headshot uploaded by the participant                | uploaded by participant | yes       |
| Derived quality scores | 0–1 score per answer, "Good / needs detail / vague" | derived by polish layer | n/a       |

### 3.2 What is **not** processed

- Special categories under Art. 9 are **not** asked for. The interview
  questions in `interview/paths.py` do not request data on health, religion,
  ethnicity, trade-union membership, sexual orientation, political views, or
  biometric data. The photo, if provided, is treated as identifying data
  rather than biometric — it is not run through any face recognition or
  feature extraction.
- The participant **may** voluntarily write Art. 9 information into a
  free-text field (e.g. "I took a break from work because of cancer
  treatment"). In that case the polish layer treats the text as ordinary work
  history. The participant retains full Art. 17 erasure rights and is shown a
  live preview before any export, so they see exactly what would appear on
  the CV and can edit it out.
- Criminal-conviction data (Art. 10) is **not** asked for and there is no
  field that elicits it.

### 3.3 Sensitive context that may surface

AMS course populations include asylum-seekers and persons returning to work
after caring responsibilities, illness, or detention. Their work-history
field will naturally contain context (gaps, country of previous employment,
language fluency) that an employer reading the finished CV could use to
infer protected attributes. AMS JobAssist does not flag, derive, or
emphasise such context — it transcribes it as-is. This is documented to the
participant on the consent screen.

---

## 4. Legal basis

### 4.1 Primary basis — Art. 6(1)(b) GDPR

Performance of a contract: the participant has a course agreement with AMS,
one element of which is producing a CV. Processing under this basis is
limited to what is necessary for the course's stated goal (an employer-ready
CV).

### 4.2 Secondary basis — Art. 6(1)(a) GDPR (explicit consent)

In addition, the application shows a consent screen before the interview
starts. The checkbox text reads (German):

> *„Ich willige ein, dass meine Eingaben lokal auf diesem Gerät verarbeitet
> werden, um einen Lebenslauf zu erstellen. Die Daten verlassen dieses
> Gerät nicht. Ich kann meine Daten jederzeit über die Funktion ‚Daten
> löschen' entfernen lassen."*

Consent is logged with a timestamp on the `users` row. The participant can
withdraw consent at any time via the in-app deletion button, which calls
`DataDeletion.delete_user_data()` (see `PRIVACY_ENFORCEMENT.md` §7).

### 4.3 Why two bases

Art. 6(1)(b) covers the trainer's professional use of the data inside the
classroom even if a participant later withdraws consent. Art. 6(1)(a) covers
the optional fields (photo, contact details, free-text personal context) and
gives the participant a clear withdrawal path. The two bases do not overlap
problematically: erasure removes the record under either basis.

### 4.4 Children

If a minor (under 16, the Austrian digital-consent threshold per § 4 Abs. 4
DSG) is enrolled in a basic-qualification course, the AMS trainer must
obtain written consent from a parent or legal guardian outside the
application before the interview begins. The application does not implement
a separate parental-consent flow because AMS minors are usually enrolled
through the AMS contract route (Art. 6(1)(b)), and a digital consent layer
on top would create the false impression that the child's tick alone is
sufficient.

---

## 5. Data minimisation

| Practice                                  | Implementation                                                              |
| ----------------------------------------- | --------------------------------------------------------------------------- |
| Only typed text is stored                 | autosave (`interview/autosave.py`) writes nothing the user did not type     |
| Quality scores are not stored             | derived at request time in `interview/engine.py`, never persisted           |
| Photo is optional                         | the photo upload field has a "skip" button on every step                    |
| Approximate dates are accepted            | the date field accepts `"~2015"` or `"keine Angabe"`                        |
| Default retention is bounded              | `AMS_DATA_RETENTION_DAYS` default `365` in Tool 1 (`config.py`), `90` in Tool 2; abandoned drafts purged after 30d, all sessions after the ceiling |
| No tracking, telemetry, or analytics      | network is blocked at the socket layer (`privacy/network_block.py`)         |
| No analytics IDs, cookies, or fingerprint | the frontend uses session-scoped IDs only; no third-party JS is loaded      |
| No backup of polished CVs to cloud        | export goes to a local folder chosen by the user; cloud sync is out of band |

Tool 1's 365-day default gives a hard ceiling covering the course cycle plus a
reasonable trainer-review and appeal window; abandoned drafts are purged sooner
(30 days), and every session (incomplete, completed, or locked) is purged once
past the ceiling. Tool 2 (trainer dashboard) defaults to a shorter 90-day
ceiling. All are configurable per installation — see `RETENTION_POLICY.md`.

---

## 6. Storage and security

### 6.1 Storage

| Asset                                | Location                                                    |
| ------------------------------------ | ----------------------------------------------------------- |
| Tool 1 database                      | `tool-1-cv-maker/src/backend/data/ams_jobassist.db` (SQLite) |
| Tool 2 database                      | `tool-2-trainer-dashboard/data/ams_trainer.db`              |
| Generated exports (PDF / DOCX / JSON) | folder chosen by the trainer per export                     |
| LLM weights                           | `data/models/` beside the executable (no personal data; downloaded once by the installer, never fetched at runtime) |
| Logs                                 | stderr / stdout of the local process; no log file by default |

Both databases use explicit child-row deletes (NOT `ON DELETE CASCADE` —
SQLite FK enforcement is per-connection and off on worker threads;
`cleanup_old_sessions()` and `DataDeletion.delete_user_data()` delete child
rows explicitly to guarantee no orphaned PII). Schema also
deletes (`PRIVACY_ENFORCEMENT.md` §7).

### 6.2 Security controls

| Layer                                | Mechanism                                                              |
| ------------------------------------ | ---------------------------------------------------------------------- |
| Network egress                       | 4-layer loopback allowlist in `privacy/network_block.py`               |
| Trainer dashboard auth               | `AMS_TRAINER_API_KEY` Bearer token (Tool 2 `config.py` line 47)        |
| Tool 1 single-user                   | bound to `127.0.0.1` only                                              |
| Logs                                 | regex `PrivacyFilter` in `privacy/logging_rules.py` redacts PII        |
| Audit trail (trainer)                | `ExportLog` table in Tool 2 `models.py` (lines 105–121)                |
| Audit trail (participant)            | `exports` table in Tool 1 SQLite schema                                |
| Compliance self-check                | `privacy/compliance.py` → `generate_compliance_report()`               |

### 6.3 What is **not** implemented (flagged residual risk)

> **At-rest encryption of the SQLite database is not implemented.** The
> database file is readable by anyone with filesystem access to the
> trainer's laptop. This is a deliberate scope decision: full-disk
> encryption is one OS-level setting away (BitLocker on Windows, FileVault
> on macOS, LUKS on Linux) and is dramatically more robust than
> application-level SQLite encryption, which would require shipping
> SQLCipher and managing a passphrase the trainer would inevitably write
> on a sticky note.
>
> The mitigation is therefore organisational: AMS must mandate full-disk
> encryption on every device that runs AMS JobAssist. This is recorded as
> **residual risk R-1** in §9.

---

## 7. Data subject rights — implementation map

| Article    | Right                       | Implementation                                                                                                                                          |
| ---------- | --------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Art. 13/14 | Information                 | Consent screen shown on first launch; this DPIA published on the public repo.                                                                           |
| Art. 15    | Access                      | `GET /api/cv/{session_id}/my-data` — see `PRIVACY_ENFORCEMENT.md` §8. Returns full raw answers + polished CV as a JSON download.                        |
| Art. 16    | Rectification               | Tool 1: participant can re-open any step and re-answer. Tool 2: trainer inline-edits any field of the polished CV (no modal, immediate save).           |
| Art. 17    | Erasure                     | `DataDeletion.delete_user_data(user_id)` in `privacy/data_deletion.py`. ON DELETE CASCADE removes all related rows. Verified by `verify_user_deleted()`. |
| Art. 18    | Restriction                 | The trainer's "Lock" action sets `locked = 1` on the session row, which blocks further polish-layer rewrites and excludes the session from cleanup.     |
| Art. 19    | Notification of rectification | N/A — no recipients (§8).                                                                                                                              |
| Art. 20    | Portability                 | `GET /api/cv/{session_id}/my-data` returns machine-readable JSON. The `cv_data` block is identical to what export consumes.                              |
| Art. 21    | Objection                   | Withdraw consent → delete data. There is no profiling to object to.                                                                                     |
| Art. 22    | Automated decision-making   | N/A — the polish layer rewrites text but does not make any decision affecting the data subject's rights or interests. The participant approves the CV before any export. |

### 7.1 Response time

All rights are exercisable from inside the running application and take
effect synchronously (within seconds). The GDPR's one-month statutory
deadline is therefore comfortably met.

### 7.2 Identity verification

The application's threat model assumes the participant is physically at
the same laptop where the data was entered. The `session_id` returned to
the participant's browser is the verification token. AMS IT must ensure
laptops are not shared between participants without logout.

---

## 8. Recipients

**There are none.**

- No processor under Art. 28 — see `DPA_TEMPLATE.md`. The maintainer of
  the software does not receive personal data because no telemetry,
  crash report, or "phone home" channel exists.
- No joint controller under Art. 26.
- No cross-border transfer under Chapter V. All processing happens on the
  trainer's laptop in Austria (or wherever the AMS regional office is).
- No automated transmission to employers. The participant or the trainer
  manually attaches the finished PDF to an email or upload form outside
  AMS JobAssist.

The local LLM weights are downloaded once by the installer at install time (from
HuggingFace over HTTPS, SHA-256-verified); **at runtime the shipped product
downloads nothing**, so there is no runtime model download channel and no
transmission of any data — participant or otherwise —
to HuggingFace or any other host. This is documented in `DPA_TEMPLATE.md` §
Sub-Auftragsverarbeitung.

---

## 9. Risk assessment matrix

Likelihood and impact are scored 1 (low) – 3 (high). Residual risk after
mitigation is recorded in the final column.

| ID   | Risk                                                            | Likelihood | Impact | Mitigation                                                                                                                          | Residual |
| ---- | --------------------------------------------------------------- | ---------- | ------ | ----------------------------------------------------------------------------------------------------------------------------------- | -------- |
| R-1  | Laptop theft / loss exposes the SQLite database                  | 2          | 3      | Full-disk encryption (BitLocker) mandated by AMS; 365-day retention default (30d for drafts); AMS_REQUIRE_ENCRYPTION gate; optional SQLCipher via AMS_DB_KEY | medium   |
| R-2  | Trainer misuses access (curiosity, gossip)                       | 2          | 2      | `AMS_TRAINER_API_KEY` Bearer auth on Tool 2; `ExportLog` audit table records who exported what when; trainers sign confidentiality   | low      |
| R-3  | AI hallucination — polish layer invents an employer / skill      | 2          | 2      | Rule-based fallback always available; live preview shows the participant the polished text; trainer must approve before bulk export | low      |
| R-4  | Unsigned `.exe` is replaced with a trojaned copy                 | 1          | 3      | Code-signing certificate procurement is pending; until then AMS IT distributes the binary over a trusted internal channel only      | medium   |
| R-5  | Participant accidentally writes Art. 9 data into free text       | 2          | 2      | Consent screen warns this is possible; live preview shows what will appear on CV; Art. 17 erasure available at any time              | low      |
| R-6  | Network blocker is bypassed by a future code change              | 1          | 3      | `verify_network_blocked()` runs at startup; `ComplianceChecker` exposes it; CI suite has 7 dedicated tests                            | low      |
| R-7  | Retention loop fails silently and data accumulates               | 1          | 2      | `_retention_loop` logs every sweep; admin endpoint `POST /api/interview/admin/cleanup-sessions` allows manual trigger                 | low      |
| R-8  | Trainer exports a CV to a personal cloud-synced folder           | 2          | 3      | Out of scope of the application; covered organisationally — AMS IT disables OneDrive/Dropbox on classroom laptops                   | medium   |
| R-9  | Participant data leaks via crash log / stderr                    | 1          | 2      | `PrivacyFilter` redacts emails, phones, dates, addresses from the root logger; interview content is not logged in normal operation   | low      |
| R-10 | Trainer's `AMS_TRAINER_API_KEY` is weak or shared                | 2          | 3      | Documentation mandates 32+ char random key; startup warning if empty; AMS IT to rotate per cohort                                    | medium   |
| R-11 | Photo upload contains EXIF GPS metadata revealing home address   | 2          | 1      | EXIF stripping recommended for future release; currently the photo is embedded as-is in PDF/DOCX                                     | medium   |

### 9.1 Aggregate verdict

Of 11 identified risks, 6 are low, 5 are medium, and none are high after
mitigation. The DPIA conclusion is **acceptable to proceed**, conditional
on the residual-risk recommendations in §10.

---

## 10. Residual risks and recommendations to AMS

The following are **not** implemented inside AMS JobAssist and must be
addressed at the AMS organisational level before the tool is deployed at
scale.

1. **Mandate full-disk encryption (R-1, R-8).** Every laptop running AMS
   JobAssist must have BitLocker (Windows), FileVault (macOS), or LUKS
   (Linux) enabled. AMS IT must verify this during device provisioning.
2. **Procure a code-signing certificate (R-4).** The Windows installer
   should be signed with an AMS-controlled certificate so that participants
   and trainers can verify provenance via the standard OS UAC dialog.
3. **DPO sign-off on the examples list.** The good/bad examples shown in
   the interview UI (`interview/paths.py`) and the skill normalisation
   dictionary (`polish/skill_normalization.py`) should be reviewed by the
   AMS DPO to ensure no example accidentally elicits Art. 9 data or
   stigmatises a population.
4. **Disable cloud sync on classroom laptops (R-8).** OneDrive, Dropbox,
   Google Drive, and Nextcloud clients should be removed from images used
   for AMS course laptops, or at minimum configured not to sync the export
   folder.
5. **Rotate trainer API keys per cohort (R-10).** AMS IT should ship a
   freshly generated `AMS_TRAINER_API_KEY` per course start and revoke the
   previous one.
6. **Screen-reader and keyboard-navigation audit.** The DPIA does not
   cover accessibility, but AMS trainers reported participants with
   literacy challenges. A WCAG 2.1 AA audit of the interview UI is
   recommended before broad rollout.
7. **External penetration test of a packaged release.** Documented as a
   known gap in `PRIVACY_ENFORCEMENT.md` §5 and §15. Should be commissioned
   before the first production deployment.
8. **EXIF stripping (R-11).** A small code change in the photo-upload
   handler to drop GPS/EXIF metadata before storage. Tracked as a
   follow-up.

---

## 11. Approval

This DPIA was prepared by the maintainers of AMS JobAssist for review by
the AMS Datenschutzbeauftragte/r (DPO). It is not authoritative until
signed below.

| Role                          | Name               | Signature | Date       |
| ----------------------------- | ------------------ | --------- | ---------- |
| AMS Datenschutzbeauftragte/r   | _to be filled in_  |           |            |
| Maintainer (AMS JobAssist)     | _to be filled in_  |           |            |
| AMS IT-Sicherheitsbeauftragte/r| _to be filled in_  |           |            |

**Document version**: 1.0
**Next scheduled review**: 12 months after first production deployment, or
on material change to the processing operations (whichever is sooner).

---

**File**: `AMS-JobAssist/docs/DPIA.md`
**Related documents**:
- `AMS-JobAssist/PRIVACY_ENFORCEMENT.md` — technical privacy controls
- `AMS-JobAssist/docs/DPA_TEMPLATE.md` — processor agreement template
- `AMS-JobAssist/docs/RETENTION_POLICY.md` — retention windows and mechanism
