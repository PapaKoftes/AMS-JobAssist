# AMS JobAssist — Master Plan

**This is the living checklist for everything that needs to be built, fixed, or improved.**  
Checkboxes are the only workflow signal. A box is checked when the work is done and verified — not when it is coded.

---

## STABILITY & CORRECTNESS

### Crash Fixes
- [x] `app.py` AI chat 500 — `cv_data.target_job` now uses `getattr(..., "target_job", "")` (also fixed at the cover-letter site)
- [x] `schema.sql` — `'europass'` is in the exports CHECK constraint (verified in 2026-05-12 audit; line 77)
- [x] `CVSubmission` model — `cv_locked` Boolean column persists across restarts (verified in 2026-05-12 audit; models.py:67)
- [x] `cv_mapper.py` — `parents[4]` is correct for resolving repo root (verified in 2026-05-12 audit; line 48)
- [x] Tool 2 `app.py` lifespan — repo root added to `sys.path` so `shared` imports work on fresh installs
- [x] Tool 1 `app.py` lifespan already had this; verified consistent across both tools

### Silent Wrong Behavior
- [x] `export/base.py validate_cv_data()` — already uses `not german AND not english` (passes if either present); over-validation claim was outdated
- [x] `api/interview.py` default language — both code (line 119) and docstring (line 198) now say `"de"`
- [x] `api/interview.py:635` — `_07` is part of the documented question-id convention, not a phantom
- [x] `routes.py` — no `cv_approved` field exists; `approval_status` + `cv_locked` are the real columns (verified 2026-05-12)
- [x] Frontend/backend quality key — `/complete` returns `overall_quality` and frontend reads `overall_quality`; `/preview` returns `score` for live polish (two different shapes by design)

### Thread Safety & Runtime
- [x] SQLite — Tool 1 uses `threading.local()` per-thread connections with `check_same_thread=True`; Tool 2 uses SQLAlchemy which manages thread safety internally
- [x] All API error responses — both tools now emit structured errors with `{status, error: {code, detail, request_id, session_id}}`
- [x] Structured logging — Tool 1 already had request_id middleware; Tool 2 middleware added 2026-05-12; every log line prefixed `[req_id]`

**Milestone: Zero crashes on any user action including edge cases (skipped sections, no AI model, concurrent users)** — ✅ all known crash sites closed

---

## INSTALL & CONFIGURATION

- [x] `tool-1-cv-maker/pyproject.toml` — `lingua-language-detector` is a runtime dep; `llama-cpp-python` is in `[ai]` optional extras
- [x] `tool-2-trainer-dashboard/pyproject.toml` — `reportlab` and `python-docx` are runtime deps
- [x] `shared/pyproject.toml` — installable package (`ams-shared`) referenced by both tools
- [x] `.env.example` — exists at repo root, documents every config variable
- [x] `DATA_DIR` configurable — `AMS_DATA_DIR` env var supported
- [x] Root `requirements.txt` — exists, installs `-e shared/`, `-e tool-1-cv-maker[ai,dev]`, `-e tool-2-trainer-dashboard[dev]` in one shot
- [x] `ams_jobassist.bat` step counter — verified 2026-05-12: labels `Schritt 1 von 6` through `Schritt 6 von 6` are correctly numbered

**Milestone: `pip install -e tool-1-cv-maker[ai]` and `pip install -e tool-2-trainer-dashboard` both work from scratch with zero manual steps**

---

## SECURITY & COMPLIANCE

- [x] Tool 2 auth — `AMS_TRAINER_API_KEY` warning at startup, enforced via API-key middleware
- [x] `ExportLog` — model exists in Tool 2 (`models.py:105`) and is written on every bulk export (`routes.py:1062, 1234`)
- [x] Trainer access log — audit middleware logs every state-changing call with API key + endpoint
- [x] `network_block.py` — rewritten 2026-05-12 to allowlist loopback (127.0.0.1, ::1, localhost) so the server keeps working while external network is blocked. Offline mode is now **on by default** (set `AMS_ENFORCE_OFFLINE=0` to disable for development).
- [ ] CSRF token — add FastAPI CSRF middleware to Tool 1 (low priority — Tool 1 is 127.0.0.1 only, no auth)
- [x] Consent screen — checkbox in HTML at `consentBlock`, blocks start button until ticked
- [x] Data retention — `AMS_DATA_RETENTION_DAYS` env var triggers daily cleanup of old sessions (drafts after 30d, all sessions after the ceiling); default 365 in Tool 1 / 90 in Tool 2 (set `0` to keep forever)
- [x] Participant data download — `GET /api/cv/{session_id}/my-data` exposes DSGVO Art. 20 portability; wired to `#myDataBtn`
- [ ] Document data retention policy in trainer guide

**Milestone: A DSGVO audit finds no gaps — consent, retention, portability, access log all present and documented**

---

## TEST COVERAGE

- [x] `cv/models.py to_canonical()` — covered by the `shared` import path tests
- [x] `export/base.py validate_cv_data()` — covered by export tests with optional sections empty
- [x] Europass export end-to-end test — present in test_export.py
- [x] Tool 2 lock/unlock round-trip test — present in test_integration.py
- [x] Tool 2 approval status test — present in test_integration.py
- [x] `cv_mapper.py` path resolution test — present in test_cv_mapper.py
- [x] `polish/engine.py` skill normalization — covered by multilingual tests (Turkish, Arabic, Bosnian)
- [x] Tool 2 `conftest.py` — proper fixtures with test DB, test client, three import shapes
- [x] `api/interview.py _generate_follow_up()` — covered by API tests
- [x] AI endpoint tests — model-absent fallback path covered (test_e2e_flow, test_offline)
- [ ] `test_e2e_flow.py` — add AI chat round-trip to end-to-end test

**Milestone: Tool 2 test coverage reaches parity with Tool 1 — every route has at least one test** — ✅ achieved

---

## DEAD CODE

- [x] `interview/engine.py` — `_assess_answer()` and `_get_suggestion()` already removed
- [x] `polish/engine.py` — redundant `_extract_skills()` already removed; only `_extract_skills_multilang()` remains
- [x] `polish/engine.py` — naming inconsistency fixed: local wrapper renamed `polish_with_ollama` → `ai_polish` (no longer shadows the imported symbol)
- [x] `routes.py` — no duplicate `import zipfile`/`import io` inside handlers (verified 2026-05-12)
- [x] `tests/conftest.py` — uses `execute_update()` correctly for INSERTs

---

## INTERVIEW ENGINE

- [ ] Conversational follow-up via AI — after each answer, local model asks one specific targeted follow-up (not started; the earlier 501 skeleton was removed)
- [ ] Context-aware follow-ups — AI reads last 3 answers before generating follow-up
- [ ] Smart quick-fill — change from pre-filled answers to sentence starters Maria completes
- [ ] ATS target job in question 2 — tailor every subsequent follow-up toward that job's keywords
- [ ] Skill surfacing pass before completion — AI reviews all answers and surfaces missed skills
- [ ] Gap handling nuance — `pause` path: dedicated questions that reframe gaps without shame
- [ ] Photo upload removed from interview — DOCX placeholder instead
- [ ] Answer word count live indicator — "12 words — more detail helps"
- [ ] Undo last answer — go back button that reopens previous question with original answer
- [ ] Estimated time remaining — "about 8 minutes left" based on path + completion rate
- [ ] Progress persistence display on resume — "You answered 7 of 9 questions last time"

**Milestone: A first-time user with no coaching completes the interview and produces a quality-scored CV without trainer correction**

---

## CV OUTPUT & EXPORT

- [x] Unambiguous completion screen — quality score, three download buttons, what-to-do-next
- [ ] Explain the transformation — expandable "here's what changed and why" after each answer is polished
- [ ] Split-screen live CV — left: current question, right: CV building in real time (partial: live CV panel exists)
- [x] Cover letter personalisation via AI — `/api/ai/cover-letter` endpoint exists; uses CV context + job posting
- [ ] DOCX as primary editable format — clean template, sensible styles, editable in Word/LibreOffice without reformatting

**Milestone: Maria downloads her CV, opens it in Word, and can edit it without reformatting anything**

---

## AI FEATURES

- [x] Offline-safe AI status in UI — `aiBadge` shows "Regelbasiert" when no model loaded
- [ ] Interview question practice mode — AI asks generated interview questions, gives feedback on typed answers
- [ ] Live AMS eAMS-Konto job feed — connect `match_job_description()` to AMS Open Data / eAMS API
- [ ] In-app model download progress — bytes / total percentage, not just "please wait"
- [ ] Model auto-load on startup — if model file exists, warm it in background so it's ready when needed

**Milestone: With model loaded, full AI loop works — polishing, chat coach, interview prep, job match — all from one session, all offline**

---

## TRAINER DASHBOARD (TOOL 2)

- [ ] Cohort creation and management UI — backend supports it; frontend UI still needed
- [x] Session stats dashboard — `GET /api/cohorts/{id}/metrics` exists; frontend renders it
- [ ] Notes field per participant — private trainer notes, never shown to participant
- [x] Bulk approve with single click — `POST /api/participants/bulk-approve` + UI button wired
- [x] Export audit log — `ExportLog` table populated on every export
- [ ] Class overview print view — one-page printable summary
- [ ] Before/after comparison print stylesheet — printable for classroom use

**Milestone: A trainer runs a full cohort from first participant login to final bulk export with zero workarounds**

---

## ACCESSIBILITY

- [x] ARIA labels on key interactive elements — `aria-live`, `aria-required`, `aria-describedby` on quality/save status/inputs
- [x] Semantic HTML — `role="banner"`, `role="main"`, proper heading levels, `<label>` associations
- [x] Skip navigation link — `.skip-link` is first focusable element
- [x] Right-to-left text support — `document.documentElement.dir = 'rtl'` when Arabic selected
- [x] Font size controls — A+ button scales via `--font-scale` CSS variable
- [ ] Keyboard navigation full audit — Tab/Enter/Escape/arrows confirmed across all screens
- [x] Visible focus indicators — `*:focus-visible` rule with 3 px orange outline added in styles.css
- [ ] Screen reader announcements — `aria-live` regions for live preview, quality changes, save confirmations, AI responses
- [x] High contrast mode — `@media (prefers-contrast: more)` block added; strengthens borders and text contrast
- [ ] Color blindness — no information by color alone; quality indicators use icon + text, never color only
- [ ] Dyslexia-friendly font option — toggle for OpenDyslexic or system sans-serif alternative
- [x] Reduced motion — `@media (prefers-reduced-motion: reduce)` collapses all transitions/animations
- [ ] Zoom-friendly layout — fully usable at 200% browser zoom, no horizontal scroll
- [x] Touch targets — `.btn`, `.lang-btn`, `.path-button`, `.quick-fill-btn`, `.ai-coach-quick-btn` all `min-height: 44px`
- [ ] Error messages — never color alone; icon + descriptive text + `aria-describedby` on input
- [ ] Timeout warnings — warn 2 minutes before session expiry, dismissable notice
- [ ] Voice input — browser `SpeechRecognition` API on answer textarea; no server required
- [ ] Touch spacing — gap between quick-fill buttons for users with tremor

**Milestone: WCAG 2.1 AA verified by automated scan (axe or Lighthouse) — zero critical violations**

---

## PACKAGING & DEPLOYMENT

- [x] PyInstaller specs — rewritten 2026-05-12 to be relocatable (uses `SPECPATH`), with complete `hiddenimports` (uvicorn lifecycle, pydantic_core, starlette, reportlab, docx, sqlalchemy dialects, llama_cpp) and `datas` (frontend, shared, Tool 1 export package for Tool 2)
- [x] `build_all.bat` — rewritten 2026-05-12 to fix `--buildpath` (was invalid) → `--workpath`, pin CWD to repo root via `pushd %~dp0`, wipe stale artifacts, add `--noconfirm --clean`
- [x] Application icon — generated `packaging/icon.ico` (multi-resolution 16/32/48/64/128/256), bundled in all three .exe files
- [x] Run a full build on a developer machine and inspect the dist tree (verified 2026-05-12: Launcher 8.2 MB, Tool 1 375 MB, Tool 2 46 MB; all build without errors)
- [ ] Bundled model `.zip` — separate download with Qwen model pre-placed; for air-gapped centers
- [ ] `Dockerfile` — one-instance classroom server; `docker run` and all participants connect via browser
- [ ] SQLite backup endpoint — `GET /api/admin/backup` downloads current database file
- [ ] In-app update checker — compare local version to GitHub latest tag; show notice, no auto-update
- [ ] Verify Windows 7, 10, 11 compatibility on real machines
- [ ] Installer test on fresh Windows VM — no Python, no prior tools

**Milestone: A non-technical AMS trainer installs and runs the tool from a USB stick on a fresh Windows laptop in under 10 minutes**

---

## MULTILINGUAL UI

- [x] UI chrome translated for all 12 active languages — buttons, labels, headers, status messages, errors (de, en, bs, hr, sr, tr, pl, ro, uk, ru, ar, sk)
- [x] Language selector on start screen — participant picks once, everything adjusts
- [x] Multilingual quality feedback messages — `qualityShort/Ok/Good` keys per language
- [x] RTL layout switch automatic when Arabic selected — `document.documentElement.dir = 'rtl'`
- [ ] Add Farsi/Persian to reach 14-language claim, OR adjust the "14 languages" marketing to "12 UI languages, 14 polish languages"

**Milestone: A Turkish-speaking participant completes the entire interview without reading a word of German** — ✅ for the 12 supported UI languages

---

## QUALITY OF LIFE

- [x] Answer autosave visual feedback — `saveStatus` element shows "Wird gespeichert…" → "Gespeichert ✓"
- [ ] In-app keyboard shortcut reference — `?` button with shortcut list
- [ ] Session health indicator in Tool 2 — status dot showing whether Tool 1 server is reachable
- [x] Participant search in Tool 2 — filter by name/cohort/date/quality/completion (backend supports it; frontend wires the search box)
- [x] Print stylesheet for completed CV — `@media print` rules added: strips chrome (header/footer/banners/AI widgets/buttons), keeps CV/review content readable, avoids page-break inside sections
