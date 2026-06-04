# AMS JobAssist — API Documentation

**Version**: 1.0  
**Audience**: Developers and AMS IT integrating with the tool  
**Last reviewed**: 2026-05-12 (corrections added 2026-06-04)

> ⚠️ **CORRECTION NOTICE — This document predates security hardening (2026-06).**
> Several sections are now inaccurate. Read these corrections first:
>
> **Endpoints that do NOT exist (will return 404, not 501):**
> - `POST /api/interview/conversational/start`
> - `POST /api/interview/conversational/turn`
>
> **New required fields — calls without them will fail:**
> - `POST /api/interview/start` now requires `"consent_given": true` in the
>   request body → 403 without it.
> - `GET /api/cv/{session_id}/my-data` now requires ownership proof:
>   `X-Session-Token: <token>` header (from start response) or `X-User-Id: <uid>` → 404 without it.
> - `DELETE /api/cv/{session_id}/erase` — **THIS ENDPOINT NOW EXISTS** (the doc
>   says it doesn't — that statement is wrong). Same ownership proof required.
>
> **Endpoints NOT documented here (they exist and work):**
> - `DELETE /api/cv/{session_id}/erase` — Art. 17 erasure
> - `GET /api/admin/backup` — full SQLite snapshot (loopback-or-API-key gated)
> - `POST /api/ai/dump-extract` — free-form dump extraction (core AI feature)
> - `GET /api/ai/dump-snapshot/{session_id}` — resume snapshot
> - `GET /api/ai/model-tiers`, `GET /api/ai/download-status`, `POST /api/ai/download-cancel`
> - `GET /api/ai/knowledge/status`, `/jobs`, `/search`
> - `POST /api/ai/interview-coach`
> - Tool 2: `GET /api/admin/backup`, `POST /api/participants/bulk-approve`,
>   `POST /api/participants/{id}/lock`, `POST /api/participants/{id}/unlock`,
>   `GET /api/export-all`
>
> **Tool 2 import:** `POST /api/import-cvs` now accepts `?force_overwrite=true`
> and returns HTTP 409 when re-importing a locked/approved/trainer-edited CV
> without it.
>
> **ExportRequest** now accepts `"anonymise": true` (name→initials, drops
> photo/DOB/nationality) on all four export endpoints.
>
> **Authoritative route list**: `docs/API_ENDPOINTS.generated.md` (generated
> from code by `scripts/dump_openapi.py`; regenerated in CI so it can't drift),
> plus `docs/openapi-tool1.json` / `docs/openapi-tool2.json`. Or read the live
> FastAPI `/docs` page at `http://localhost:8000/docs` and `:8001/docs`.

---

## Overview

AMS JobAssist is a two-tool offline desktop application that exposes two FastAPI
servers on the local machine. Tool 1 (CV Maker, port `8000`) drives the
participant interview, polishes raw answers, and emits CV exports. Tool 2
(Trainer Dashboard, port `8001`) imports those exports, lets a trainer review
and approve them, and produces bulk PDF / DOCX / JSON bundles. Both servers
emit JSON unless an endpoint explicitly returns a file. Network access from the
process is blocked by default (`AMS_ENFORCE_OFFLINE=1`).

### Base URLs

| Tool | Base URL |
|---|---|
| Tool 1 — CV Maker | `http://localhost:8000` |
| Tool 2 — Trainer Dashboard | `http://localhost:8001` |

### Conventions

- Request and response bodies use `Content-Type: application/json` unless
  explicitly multipart (file upload) or a binary download.
- Timestamps are ISO 8601 in UTC (`2026-05-12T14:32:00`).
- Language codes are ISO 639-1 (`de`, `en`, `tr`, `pl`, `ro`, `uk`, `ru`, `ar`,
  `bs`, `hr`, `sr`, `sk`).
- `session_id` is an **integer** (DB autoincrement). `participant_id` and
  `submission_id` are also integers. There is no `sess_…` string prefix.
- Every response carries an `X-Request-ID` header (8-char hex) for support /
  log correlation. Both Tool 1 and Tool 2 emit it.

---

## Authentication

| Tool | Mechanism |
|---|---|
| Tool 1 | **None.** Loopback-only; CSRF middleware rejects requests whose `Origin` points to another host. Non-browser clients (curl, Python) send no `Origin` and are accepted. |
| Tool 2 | **Optional API key.** When the environment variable `AMS_TRAINER_API_KEY` is set, every `/api/*` request must include `X-API-Key: <key>`. Static files and `/health` are always public. When the variable is unset, the dashboard is open on loopback. |

Both tools enforce CSRF on state-changing methods (`POST`, `PATCH`, `DELETE`):
if an `Origin` header is present, it must match the server's own host.

---

## Error response format

All errors from both tools share a structured envelope:

```json
{
  "status": "error",
  "error": {
    "code": "VALIDATION_ERROR",
    "detail": "answer_text: cannot be empty",
    "request_id": "a1b2c3d4",
    "session_id": 17
  }
}
```

`session_id` is present only on Tool 1 responses where an active session is in
the request's context. `request_id` mirrors the value in the `X-Request-ID`
response header.

| Status | Meaning |
|---|---|
| 200 | OK |
| 400 | Bad request — invalid path, semantic error, or unprocessable input the route handler caught explicitly |
| 401 | Missing / wrong `X-API-Key` (Tool 2 only, when auth enabled) |
| 403 | CSRF rejected (cross-origin browser request) |
| 404 | Session, participant, or section not found |
| 413 | Upload too large (Tool 2 imports) |
| 422 | Pydantic validation failed (`code: VALIDATION_ERROR`) |
| 500 | Unhandled server error |
| 501 | Feature is a known WIP skeleton (conversational interview, missing Tool 1 backend for PDF/DOCX bulk export) |
| 503 | Subsystem not initialised |

---

# Tool 1 — CV Maker (`localhost:8000`)

## Interview

### `POST /api/interview/start`

Start a new interview session.

**Request body**

| Field | Type | Required | Notes |
|---|---|---|---|
| `user_id` | string | yes | 1–255 chars after trim |
| `interview_path` | string | yes | one of `unemployed`, `career-switch`, `student`, `pause`, `other` |
| `language` | string | no | default `"de"` |
| `user_native_language` | string\|null | no | ISO 639-1 |

**Response** `200`

```json
{
  "status": "success",
  "data": {
    "session_id": 42,
    "interview_path": "unemployed",
    "first_question": { "id": "id_full_name", "text": "...", "examples": {...} },
    "progress": { "current": 1, "total": 18 }
  }
}
```

The exact shape of `data` is whatever `InterviewEngine.start_interview` returns
— the wrapper above always wraps it in `{"status":"success","data":…}`.

```bash
curl -X POST http://localhost:8000/api/interview/start \
  -H "Content-Type: application/json" \
  -d '{"user_id":"u_001","interview_path":"unemployed","language":"de"}'
```

---

### `GET /api/interview/next-question/{session_id}`

Return the next pending question, or `status: "complete"` if all answered.

**Response (in-progress)** `200`

```json
{
  "status": "success",
  "data": {
    "question": { "id": "exp_01_employer", "text": "...", "examples": {...} },
    "progress": { "current": 4, "total": 18 }
  }
}
```

**Response (interview finished)** `200`

```json
{ "status": "complete", "data": { "message": "All questions answered" } }
```

Errors: `404` if session does not exist.

---

### `POST /api/interview/submit-answer`

**Request body**

| Field | Type | Constraints |
|---|---|---|
| `session_id` | integer | |
| `question_id` | string | |
| `answer_text` | string | non-empty after trim, ≤ 10 000 chars |

**Response** `200`

```json
{
  "status": "success",
  "data": {
    "accepted": true,
    "polished_text": "...",
    "quality_score": 0.74,
    "detected_language": "de",
    "next_question": { ... }
  }
}
```

Errors: `400` validation, `500` on unexpected engine errors.

---

### `POST /api/interview/skip-question`

**Request body**

```json
{ "session_id": 42, "question_id": "exp_03_dates" }
```

**Response** `200` — same shape as `next-question` (either a new question or
`status: "complete"`).

---

### `POST /api/interview/resume`

Restore a paused session and return the next question to ask. Uses crash
recovery to bring the session to a consistent state.

```json
{ "session_id": 42 }
```

Returns `{"status":"success","data": {...next_question_payload...}}`.

---

### `GET /api/interview/status/{session_id}`

```json
{
  "status": "success",
  "data": {
    "session_id": 42,
    "interview_path": "unemployed",
    "answered_count": 9,
    "total_questions": 18,
    "progress": 0.5,
    "status": "in_progress",
    "last_update": "2026-05-12T14:32:00"
  }
}
```

`404` if not found.

---

### `GET /api/interview/autosave-status/{session_id}`

Returns autosave metadata (last save timestamp, queued writes). Shape passed
through from `AutosaveManager.get_autosave_status`.

---

### `POST /api/interview/preview`

Live-polish a free-text answer for the on-screen preview pane. **Does not save
anything** — there's no `session_id` and no DB write.

**Request body**

| Field | Type | Notes |
|---|---|---|
| `answer_text` | string | non-empty, ≤ 10 000 chars |
| `category` | string | default `"experience"` |
| `language` | string | optional ISO 639-1 hint from the UI |

**Response** `200`

```json
{
  "status": "success",
  "data": {
    "polished_text": "Arbeitete als Maschinenbediener bei ...",
    "quality_score": 0.62,
    "quality_label": "Gut — noch ein Detail macht es besser",
    "detected_language": "de",
    "changes": ["..."],
    "suggestions": ["..."]
  }
}
```

Note: this endpoint exposes `score` (in `quality_score`), distinct from the
`overall_quality` field returned by `/complete` and `/status`.

---

### `POST /api/interview/follow-up`

Generate one targeted follow-up question for an answer the user just
submitted. Uses the local LLM when available, otherwise a rule-based probe.
Returns `null` when the answer is already detailed enough.

```json
{
  "session_id": 42,
  "question_id": "exp_01_employer",
  "answer_text": "Ich war Kellner.",
  "language": "de"
}
```

**Response** `200`

```json
{ "status": "success", "data": { "follow_up": "Was waren Ihre wichtigsten Aufgaben dabei?" } }
```

`follow_up` is `null` when no probe is needed.

---

### `POST /api/interview/complete/{session_id}`

Finalise the interview: build the full `CVData`, persist it to `cv_data`, and
optionally surface extra skills via the local LLM.

**Response** `200`

```json
{
  "status": "success",
  "data": {
    "session_id": 42,
    "overall_quality": 0.78,
    "quality_interpretation": {
      "label": "⭐⭐ Gut",
      "tip": "Ihr Lebenslauf ist gut. Einige Details könnten noch helfen.",
      "score": 0.78
    },
    "ready_for_export": true,
    "sections_count": 11,
    "all_skills": ["Kundenkontakt", "Kassensysteme", "..."],
    "surfaced_skills": ["..."],
    "message": "Interview complete. CV is ready for export."
  }
}
```

Errors: `400` if no answers in the session; `404` session not found.

---

### Conversational interview (WIP)

| Endpoint | Status |
|---|---|
| `POST /api/interview/conversational/start` | `501` — placeholder skeleton |
| `POST /api/interview/conversational/turn` | `501` — placeholder skeleton |

Both endpoints reject every call with `501 Not Implemented`. The standard
guided interview at `/api/interview/start` is the only working entry point.
They exist so the frontend can display a "coming soon" banner without
404-ing.

---

## CV / Export

### `GET /api/cv/{session_id}`

CV metadata for a completed session.

**Response** `200`

```json
{
  "status": "success",
  "data": {
    "session_id": 42,
    "user_id": "u_001",
    "interview_path": "unemployed",
    "language_input": "de",
    "language_output_primary": "de",
    "language_output_secondary": "en",
    "overall_quality": 0.78,
    "ready_for_export": true,
    "all_skills": ["..."]
  }
}
```

`404` if no CV has been built for this session.

---

### `POST /api/export/json` · `POST /api/export/pdf` · `POST /api/export/docx` · `POST /api/export/europass`

All four share the same request schema. Each returns the rendered file as a
`FileResponse`. The response is **not** the JSON envelope — it is the binary
attachment.

**Request body (`ExportRequest`)**

| Field | Type | Default | Notes |
|---|---|---|---|
| `session_id` | integer | — | required |
| `language` | string | `"de"` | |
| `filename` | string\|null | `null` | server picks a name if omitted |
| `force` | boolean | `false` | bypass the `ready_for_export` quality gate (trainer use) |

**Errors**

- `404` — CV not yet built (call `/api/interview/complete/{id}` first).
- `400` — CV quality too low and `force` is `false`.
- `500` — exporter raised an error.

Each successful export is logged to the `exports` table (non-fatal if logging
fails).

```bash
curl -X POST http://localhost:8000/api/export/pdf \
  -H "Content-Type: application/json" \
  -d '{"session_id":42,"language":"de"}' \
  -o cv.pdf
```

Response `Content-Type`:

| Endpoint | Media type |
|---|---|
| `/api/export/json` | `application/json` |
| `/api/export/pdf` | `application/pdf` |
| `/api/export/docx` | `application/vnd.openxmlformats-officedocument.wordprocessingml.document` |
| `/api/export/europass` | `application/xml` |

---

### `POST /api/export/cover-letter`

Generate a template-based cover letter, optionally enhanced by the local LLM.

**Request body (`CoverLetterRequest`)**

| Field | Type | Default |
|---|---|---|
| `session_id` | integer | — |
| `job_title` | string | `""` |
| `employer_name` | string | `""` |
| `tone` | string | `"formal"` — also `friendly`, `neutral` |
| `language` | string | `"de"` — also `en` |
| `force` | boolean | `false` |

**Response** `200` (note: returns JSON, not a file)

```json
{
  "status": "success",
  "data": {
    "salutation": "Sehr geehrte Damen und Herren,",
    "body": "...",
    "closing": "Mit freundlichen Grüßen",
    "ai_enhanced": true
  }
}
```

---

### `POST /api/ats/score`

Score the CV against a job description, or against the built-in keyword bank if
`job_description` is empty.

```json
{ "session_id": 42, "job_description": "We are hiring a warehouse operator..." }
```

**Response** `200`

```json
{
  "status": "success",
  "data": {
    "score": 0.62,
    "grade": "B",
    "matched_keywords": ["lager", "kommissionieren"],
    "missing_keywords": ["gabelstapler"],
    "suggestions": ["Erwähnen Sie Ihren Staplerschein, falls vorhanden."]
  }
}
```

---

## AI / Coaching

All AI endpoints are designed never to return a hard error when the local model
is unavailable. They fall back to rule-based content and tag the response with
`source: "rules"` or `ai_mode: false`.

### `POST /api/ai/chat`

```json
{ "session_id": 42, "message": "Wie kann ich meine Erfahrung besser darstellen?", "language": "de" }
```

`200` → `{"status":"success","data":{"reply":"...","ai_mode":true}}`

When the model is not loaded, `reply` contains a friendly "install the model"
hint and `ai_mode: false`.

---

### `POST /api/ai/interview-coach`

In-interview assistance for a stuck participant. Request body includes the
current question being answered for context.

```json
{
  "session_id": 42,
  "message": "Ich weiß nicht was ich schreiben soll",
  "language": "de",
  "question_id": "exp_01_employer",
  "question_text": "Wo haben Sie zuletzt gearbeitet?"
}
```

`200` → `{"status":"success","data":{"reply":"...","source":"ai"|"rules"}}`

---

### `POST /api/ai/interview-prep`

Likely interview questions an employer would ask, based on the CV and target
job. Falls back to a path-aware question bank.

```json
{ "session_id": 42 }
```

`200`

```json
{
  "status": "success",
  "data": {
    "questions": ["Warum haben Sie sich für diesen Beruf entschieden?", "..."],
    "target_job": "Lagerarbeiter",
    "source": "ai"
  }
}
```

---

### `POST /api/ai/job-match`

Match the CV against a job description; never returns 503.

```json
{ "session_id": 42, "job_description": "min. 20 Zeichen…" }
```

`400` if the job description is shorter than 20 characters. `404` if the CV
hasn't been built.

`200`

```json
{
  "status": "success",
  "data": {
    "analysis": "✅ Gute Übereinstimmung (72%) ...",
    "source": "rules",
    "score": 0.72
  }
}
```

---

### `POST /api/ai/profile-summary`

Encouraging plain-language profile summary for the participant.

```json
{ "session_id": 42, "language": "de" }
```

`200` → `{"status":"success","data":{"summary":"Sie haben ...","source":"ai"}}`
`404` if no CV exists.

---

### `GET /api/ai/model-status`

```json
{
  "status": "success",
  "data": {
    "active_engine": "local",
    "local": { "local_model_available": true, "model_name": "Qwen2.5-1.5B-Instruct", "model_exists_on_disk": true },
    "ollama": { "ollama_available": false }
  }
}
```

`active_engine` is `"local"`, `"ollama"`, or `"rules"`.

---

### `POST /api/ai/download-model`

Trigger an async download of the local model.

```json
{ "confirm": true }
```

- `confirm: false` → returns `{"status":"confirm_required","data":{"message":"Download Qwen2.5-1.5B-Instruct (~1.1 GB)?","url":"..."}}`
- `confirm: true` → starts a background thread and returns `{"status":"success","data":{"message":"Download gestartet.","poll":"/api/ai/model-status"}}`
- `503` if the AI module is missing entirely.

---

### `GET /api/interview/ai/status` · `POST /api/interview/ai/refresh`

Older AI-status endpoints kept for the frontend badge. Same payload shape as
`/api/ai/model-status` but returned as `{ollama_available, mode, model, engine, description}`. `refresh` forces re-detection.

---

## DSGVO

### `GET /api/cv/{session_id}/my-data`

Article 20 data portability — every raw answer plus the polished CV plus
metadata, returned as a downloadable JSON file the participant can keep.

Response is a JSON file:

```json
{
  "notice": "Diese Datei enthält alle Ihre in AMS JobAssist gespeicherten Daten (Art. 20 DSGVO).",
  "session_id": 42,
  "raw_answers": [ { "question_id": "...", "answer_text": "...", "created_at": "..." } ],
  "cv_data": { ... full CVData ... },
  "exported_at": "2026-05-12T14:32:00"
}
```

`404` if the session has no stored data.

Data deletion is performed by the **admin** endpoint below (it removes
sessions ≥ N days old, including all their answers). Per-user erasure should
be triggered by deleting the relevant rows; there is no dedicated
`DELETE /api/cv/{id}` route in the current build.

---

## Admin

### `POST /api/interview/admin/cleanup-sessions?days_old=90`

Delete incomplete sessions older than `days_old` (default 90). Approved or
locked sessions are not touched. Runs automatically once at startup and every
24 h via the background retention task, but can be invoked manually too.

```json
{ "status": "success", "data": { "deleted": 7, "days_old": 90 } }
```

---

### `GET /health`

Liveness probe used by the launcher.

```json
{ "status": "ok" }
```

---

# Tool 2 — Trainer Dashboard (`localhost:8001`)

All routes are mounted under `/api`. Add `-H "X-API-Key: <key>"` when
`AMS_TRAINER_API_KEY` is set in the environment.

## Health

### `GET /health`

```json
{ "status": "ok", "tool": "trainer-dashboard" }
```

Public (does not require API key).

---

## Import

### `POST /api/import-cvs?cohort_id=<cohort>`

Multipart upload of a single `.json` (one CV) or `.zip` (many CVs).

| Form / query field | Notes |
|---|---|
| `cohort_id` (query) | string — required |
| `file` (multipart) | `.json` or `.zip`, max `MAX_UPLOAD_SIZE_BYTES` |

**Response (single JSON)** `200`

```json
{
  "status": "success",
  "imported": 1,
  "participant_id": 101,
  "message": "Imported 1 CV for cohort Batch-2026-Q2"
}
```

**Response (zip)** `200`

```json
{
  "status": "success",
  "imported": 12,
  "message": "Imported 12 CVs for cohort Batch-2026-Q2",
  "errors": ["bad_file.json: Expecting value: line 1 column 1 (char 0)"],
  "error_count": 1
}
```

Errors: `400` bad filename or invalid JSON/ZIP; `413` file > size limit;
`400` ZIP with > 1000 entries.

```bash
curl -X POST "http://localhost:8001/api/import-cvs?cohort_id=Batch-2026-Q2" \
  -H "X-API-Key: $AMS_TRAINER_API_KEY" \
  -F "file=@cv_export.json"
```

---

## Participants

### `GET /api/participants`

Paginated, filterable list.

**Query parameters**

| Name | Type | Default | Notes |
|---|---|---|---|
| `cohort_id` | string | — | exact match |
| `status` | string | — | one of `pending`, `approved`, `rejected`, `needs_changes` |
| `search` | string | — | matches name or email (case-insensitive `LIKE`), max 200 chars |
| `min_quality` | float | — | latest CV quality ≥ value (0.0–1.0) |
| `max_quality` | float | — | latest CV quality ≤ value (0.0–1.0) |
| `page` | int | 1 | |
| `page_size` | int | 50 | max 200 |

**Response** `200`

```json
{
  "items": [
    {
      "participant_id": 101,
      "user_id": "u_001",
      "name": "Max Mustermann",
      "email": "max@example.com",
      "cohort_id": "Batch-2026-Q2",
      "status": "pending",
      "interview_path": "unemployed",
      "first_imported_at": "2026-05-12T14:32:00",
      "last_updated_at": "2026-05-12T14:45:00",
      "completed_at": null,
      "latest_submission": {
        "submission_id": 215,
        "participant_id": 101,
        "user_id": "u_001",
        "overall_quality": 0.78,
        "approval_status": "pending",
        "version": 1,
        "created_at": "2026-05-12T14:32:00",
        "cv_data": { "...full CVData JSON..." }
      }
    }
  ],
  "total": 45,
  "page": 1,
  "page_size": 50,
  "total_pages": 1
}
```

---

### `GET /api/participants/{participant_id}`

Single participant with the latest submission. Same shape as one `items[]`
entry above. `404` if not found.

---

### `POST /api/participants/{participant_id}/approve`

Approve, reject, or mark "needs changes". The endpoint name is `approve` but
it handles all three outcomes via the `approval_status` field. Writes an
audit record (`TrainerFeedback` row + `audit` log line).

**Request body (`ApprovalRequest`)**

| Field | Type | Constraints |
|---|---|---|
| `approval_status` | string | `approved` \| `rejected` \| `needs_changes` \| `pending` |
| `feedback` | string\|null | ≤ 5 000 chars |
| `approved_by` | string | 1–255 chars |

**Response** `200`

```json
{ "status": "success", "approval_status": "approved", "message": "Submission approved" }
```

`404` if participant or submission missing.

---

### `PATCH /api/participants/{participant_id}/cv-section`

Persist a trainer's inline edit to a single CV section. The endpoint finds
the section by `question_id` inside the stored `cv_data_json` and overwrites
the text for the requested language, setting `trainer_edited: true` on the
section.

**Request body (`CVSectionEditRequest`)**

| Field | Type | Constraints |
|---|---|---|
| `question_id` | string | 1–100 chars |
| `edited_text` | string | ≤ 10 000 chars |
| `language` | string | default `"de"` |

**Response** `200`

```json
{ "status": "success", "message": "Section updated" }
```

`404` if the participant, submission, or section is not found.

---

### `POST /api/participants/bulk-approve`

**Request body (`BulkApprovalRequest`)**

| Field | Type | Constraints |
|---|---|---|
| `participant_ids` | int[] | 1–500 entries |
| `approval_status` | string | same set as single approval |
| `feedback` | string\|null | |
| `approved_by` | string | 1–255 chars |

**Response** `200`

```json
{
  "status": "success",
  "approved": 3,
  "errors": ["No submission for participant 999"],
  "message": "Processed 3 participants"
}
```

---

## Lock / status

### `GET /api/participants/{participant_id}/status`

```json
{
  "participant_id": 101,
  "approved": false,
  "locked": false,
  "approved_at": null,
  "approved_by": null
}
```

### `POST /api/participants/{participant_id}/lock`

Locks the participant's latest submission so the participant can't edit
further. Trainers can still inline-edit.

```json
{ "locked_by": "Anna Schmidt" }
```

`200` → `{"status":"success","locked":true,"participant_id":101}`

### `POST /api/participants/{participant_id}/unlock`

Mirror of `lock`. Same body, returns `locked: false`.

---

## Export

### `POST /api/bulk-export`

Export selected participants in one shot.

**Request body (`BulkExportRequest`)**

| Field | Type | Default | Notes |
|---|---|---|---|
| `participant_ids` | int[] | — | 1–500 entries |
| `format` | string | `"pdf"` | `pdf` \| `docx` \| `json` |
| `language` | string | `"de"` | |
| `include_feedback` | boolean | `false` | |

**Response**

- `format=json` → single JSON bundle, `Content-Type: application/json`.
- `format=pdf` or `format=docx` → ZIP archive of individual files, `Content-Type: application/zip`. The response also includes `X-Export-Errors: N`.

Errors: `400` empty list; `404` no matching participants; `501` if the Tool 1
exporter backend is not importable from this Tool 2 process (only relevant for
`pdf` / `docx`).

```bash
curl -X POST http://localhost:8001/api/bulk-export \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $AMS_TRAINER_API_KEY" \
  -d '{"participant_ids":[101,102,103],"format":"pdf","language":"de"}' \
  -o batch.zip
```

### `GET /api/export-all`

Export every participant (optionally filtered by cohort) in one archive.

**Query parameters**

| Name | Default | Notes |
|---|---|---|
| `format` | `pdf` | `pdf` \| `docx` \| `json` |
| `language` | `de` | |
| `cohort_id` | — | optional |

Response semantics match `/api/bulk-export`. Adds an `X-Export-Count` header.
`404` if no participants exist (or none in the cohort).

---

## Metrics

### `GET /api/cohorts/{cohort_id}/metrics`

```json
{
  "cohort_id": "Batch-2026-Q2",
  "total_participants": 15,
  "completed": 12,
  "pending": 2,
  "rejected": 1,
  "completion_rate": "80.0%",
  "avg_quality": "0.78",
  "min_quality": "0.42",
  "max_quality": "0.93"
}
```

Note: `completion_rate` and the quality fields are pre-formatted strings, not
numbers. Counts are integers.

---

## Versioning

There is **no version prefix** on either tool's API paths. AMS JobAssist
ships as a single `.exe` bundle — the front-end, both backends, and any
optional local model travel together. The endpoint surface documented above is
the contract for that release; changes will be cut in a new bundle rather than
served alongside the old one. If you embed integrations against these
endpoints, pin them to the bundle version you tested with.

---

## Quick reference

| Tool | Method | Path |
|---|---|---|
| 1 | GET | `/health` |
| 1 | POST | `/api/interview/start` |
| 1 | GET | `/api/interview/next-question/{session_id}` |
| 1 | POST | `/api/interview/submit-answer` |
| 1 | POST | `/api/interview/skip-question` |
| 1 | POST | `/api/interview/resume` |
| 1 | GET | `/api/interview/status/{session_id}` |
| 1 | GET | `/api/interview/autosave-status/{session_id}` |
| 1 | POST | `/api/interview/preview` |
| 1 | POST | `/api/interview/follow-up` |
| 1 | POST | `/api/interview/complete/{session_id}` |
| 1 | POST | `/api/interview/conversational/start` (501) |
| 1 | POST | `/api/interview/conversational/turn` (501) |
| 1 | GET | `/api/interview/ai/status` |
| 1 | POST | `/api/interview/ai/refresh` |
| 1 | POST | `/api/interview/admin/cleanup-sessions` |
| 1 | GET | `/api/cv/{session_id}` |
| 1 | GET | `/api/cv/{session_id}/my-data` (DSGVO) |
| 1 | POST | `/api/export/json` |
| 1 | POST | `/api/export/pdf` |
| 1 | POST | `/api/export/docx` |
| 1 | POST | `/api/export/europass` |
| 1 | POST | `/api/export/cover-letter` |
| 1 | POST | `/api/ats/score` |
| 1 | POST | `/api/ai/chat` |
| 1 | POST | `/api/ai/interview-coach` |
| 1 | POST | `/api/ai/interview-prep` |
| 1 | POST | `/api/ai/job-match` |
| 1 | POST | `/api/ai/profile-summary` |
| 1 | GET | `/api/ai/model-status` |
| 1 | POST | `/api/ai/download-model` |
| 2 | GET | `/health` |
| 2 | POST | `/api/import-cvs?cohort_id=...` |
| 2 | GET | `/api/participants` |
| 2 | GET | `/api/participants/{id}` |
| 2 | POST | `/api/participants/{id}/approve` |
| 2 | PATCH | `/api/participants/{id}/cv-section` |
| 2 | POST | `/api/participants/bulk-approve` |
| 2 | GET | `/api/participants/{id}/status` |
| 2 | POST | `/api/participants/{id}/lock` |
| 2 | POST | `/api/participants/{id}/unlock` |
| 2 | POST | `/api/bulk-export` |
| 2 | GET | `/api/export-all` |
| 2 | GET | `/api/cohorts/{cohort_id}/metrics` |
