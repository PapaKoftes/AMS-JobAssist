<p align="center">
  <img src="docs/img/banner.png" alt="AMS JobAssist" width="100%">
</p>

# AMS JobAssist

**An offline CV builder for AMS course participants — with a trainer dashboard for supervision.**
Built for AMS Wien classroom use — currently a polished demonstrator awaiting pilot validation. Runs entirely on the trainer's laptop. No cloud, no data leaves the device.

![Status](https://img.shields.io/badge/Status-Demo--ready-brightgreen)
![Tests](https://img.shields.io/badge/Tests-856%20passing-brightgreen)
![Build](https://img.shields.io/badge/Windows%20.exe-3%20artifacts-blue)
![Languages](https://img.shields.io/badge/UI-12%20languages-blue)
![License](https://img.shields.io/badge/License-MIT-blue)
![Privacy](https://img.shields.io/badge/Privacy-DSGVO%20compliant-brightgreen)
![Offline](https://img.shields.io/badge/Network-100%25%20offline-orange)

---

## What it does in one sentence

A participant who has never written a CV in their life sits down for 15 minutes, answers questions in their native language, and walks away with a polished German PDF/DOCX/Europass CV that a trainer has supervised in real time.

<p align="center">
  <img src="docs/img/workflow.png" alt="Participant workflow" width="100%">
</p>

---

## Quick start

### Double-click `START.bat`

That's it. The script auto-detects the best way to run:

- **Pre-built `.exe` files in `dist/`?** → Runs them directly. No Python needed.
- **Python installed?** → Installs dependencies and runs from source.
- **Neither?** → Tells you exactly what to download.

The browser opens automatically to the CV maker on `http://localhost:8000`. The trainer dashboard is on `http://localhost:8001`.

### For developers

```bash
git clone https://github.com/PapaKoftes/AMS-JobAssist
cd AMS-JobAssist
pip install -r requirements.txt
python launcher.py
```

### Build standalone `.exe` files

```bat
build_all.bat
```

Produces standalone executables in `dist/` (no Python needed on target machine):

| File | Size | What it does |
|---|---|---|
| `AMS-JobAssist-Launcher.exe` | 8 MB | Starts both tools, opens browser |
| `AMS-JobAssist-Tool1.exe` | 375 MB | Participant CV maker (includes optional LLM runtime) |
| `AMS-JobAssist-Tool2.exe` | 46 MB | Trainer dashboard |
| `install.bat` | 8 KB | Batch installer — Start Menu + Add/Remove Programs |

### Install / uninstall options

| Method | How | What you get |
|---|---|---|
| **`START.bat`** | Double-click at repo root | Auto-detects best method, handles everything |
| **Run directly** | Double-click `dist\AMS-JobAssist-Launcher.exe` | Works instantly, no install step |
| **Batch installer** | Run `dist\install.bat` | Start Menu + Desktop shortcut + Add/Remove Programs |
| **Inno Setup** | Install [Inno Setup](https://jrsoftware.org/isinfo.php), run `build_all.bat` | Full `Setup.exe` with wizard, German UI, clean uninstall |

All install methods are per-user (no admin rights needed). Uninstall preserves user data by default.

---

## The numbers

<p align="center">
  <img src="docs/img/stats.png" alt="Project stats" width="100%">
</p>

---

## Architecture

<p align="center">
  <img src="docs/img/architecture.png" alt="Two-tool architecture" width="100%">
</p>

Two FastAPI servers, each with its own SQLite database, talking to a vanilla-JS frontend. Tool 1 is the participant interface; Tool 2 is the trainer interface. They are intentionally decoupled — the trainer dashboard imports participant data via a JSON file the trainer drops in, so the two databases never share storage and Tool 1 can run with zero network exposure.

```
AMS-JobAssist/
├── tool-1-cv-maker/          Participant interface
│   ├── src/backend/          FastAPI + SQLite + interview/polish/export engines
│   ├── src/frontend/         Vanilla JS, 12-language UI, live preview
│   └── tests/                852 tests
├── tool-2-trainer-dashboard/ Trainer interface
│   ├── src/backend/          FastAPI + SQLAlchemy + audit middleware
│   ├── frontend/             Vanilla JS table view + side-by-side compare
│   └── tests/                57 tests
├── shared/schema/            Canonical CV Pydantic schema (Tool 1 ↔ Tool 2)
├── packaging/                3 PyInstaller specs + icon.ico
├── docs/                     Trainer guide · admin guide · screenshots
├── build_all.bat             Reproducible Windows build
├── launcher.py               Single-process starter
└── ams_jobassist.bat         End-user German menu (install/start/uninstall)
```

---

## Feature matrix

### For participants

| Feature | Status | Notes |
|---|---|---|
| 5 interview paths | ✅ | Unemployed · career switch · student · pause · other |
| Multi-language input | ✅ | 12 UI languages; detects 14+ input languages. **Non-German dumps are translated to German first** (translate-first) before extraction, so Arabic/Russian/Turkish/Polish input no longer collapses. (UI strings: DE/EN complete; the other 10 still ~⅓ German-fallback — see limitations.) |
| Live preview | ✅ | See your CV growing as you answer |
| Quality scoring | ✅ | Encouraging feedback ("a little more detail helps") |
| Quick-fill chips | ✅ | One-tap starters for common answers |
| Date helper | ✅ | "approximate" allowed — no shame on forgotten dates |
| Photo upload | ✅ | Optional — Austrian-style CV with photo |
| Resume after close | ✅ | Browser session restores from where you left off |
| PDF / DOCX / JSON export | ✅ | Austrian tabellarischer Lebenslauf; deterministic output. PDF now embeds a bundled Unicode font (DejaVuSans) so Cyrillic / Turkish / Polish names render correctly (no tofu). User text is XML-escaped before rendering. (Arabic-script names need a Naskh font — see limitations.) |
| Europass-style XML export | ⚠️ | Approximate Europass V3 shape — **not XSD-validated**; treat as an interop experiment, not a guaranteed-importable file |
| Cover letter generator | ✅ | ÖNORM A 1080-style Bewerbungsschreiben with signature block; downloadable as TXT |
| Application email generator | ✅ | Ready-to-send German Bewerbungs-E-Mail (subject + body, data prefilled); mailto: open + copy. Closes the "now actually apply" step |
| Guided step-by-step interview | ✅ | "📋 Lieber Schritt für Schritt?" switches the free conversation to one-question-at-a-time (and back); both modes feed the same CV + progress chips |
| Path-aware openings | ✅ | The chosen situation (arbeitslos / Umstieg / Studium / Pause) changes the conversation's opening question |
| AMS job-search bridge | ✅ | "🔎 Passende Jobs beim AMS finden" opens jobs.ams.at pre-filled with the target job (transparency notice; the app itself transmits nothing). Shows a non-destructive "also search as <canonical Beruf>" hint from a 53-occupation taxonomy |
| Check a specific job from a URL | ✅ (opt-in) | Off by default. With explicit per-action consent, fetches ONE pasted job-ad URL (sends no personal data), honours robots.txt + SSRF guards, strips to text, runs the fit-check. robots-disallowed pages (incl. jobs.ams.at /public/emps/) fall back to manual paste |
| Bewerbungs-Check (hire-readiness) | ✅ | Weighted checklist of what Austrian recruiters/systems filter on (contact, German level, licence, photo, quantified experience, job keywords) with a score + prioritised concrete fixes; auto-runs on completion |
| Editable skills | ✅ | Skill extraction is best-effort (the weakest field, ~0.40 F1) — the completion screen lets the user remove a wrong auto-detected skill or add a missing one; edits persist to the CV (exports + checks) |
| ATS / job match (optional) | ⚠️ | Rough keyword heuristic. NOTE: most AMS-target roles (trades/care/retail/gastro) are filled by SMEs via email/eJob-Room and read by humans — ATS optimisation is low-value for this clientele; keep as an optional check, not a headline |
| AI chat coach | ✅ (optional) | Knows your CV; falls back to rule-based if no model |
| Interview prep generator | ✅ (optional) | Practise questions for the actual job interview |
| DSGVO data download | ✅ | Article 20 — download everything stored about you |
| Loopback-only network | ✅ | Default-on; data physically cannot leave the machine |

### For trainers

| Feature | Status | Notes |
|---|---|---|
| Participant list | ✅ | Cohort filter, status filter, name search, pagination |
| Side-by-side compare | ✅ | What the participant wrote vs. what the CV says |
| Inline edit | ✅ | Click → edit → save instantly. Audit trail per change. |
| Bulk approve | ✅ | "Approve all ready CVs" with one click |
| Bulk export | ✅ | PDF / DOCX / JSON zipped for all selected participants |
| Lock / unlock CV | ✅ | Trainer can freeze a CV against further participant edits |
| Cohort metrics | ✅ | Completion rate, average quality, last-active timestamps |
| Per-export audit log | ✅ | `ExportLog` table records who downloaded whose CV, when |
| API-key auth | ✅ | `AMS_TRAINER_API_KEY` env var enables it |
| Request-size limit + CSRF | ✅ | Hardened middleware stack |
| Notes per participant | ✅ | Standalone save button, never shown to participant |
| Cohort creation UI | 🚧 | Backend done; frontend UI pending |

### Accessibility

| Feature | Status |
|---|---|
| **Read-aloud (text-to-speech)** | ✅ 🔊 on every advisor message; offline (browser Web Speech API), speaks in the selected language |
| Skip-navigation link | ✅ |
| Visible `:focus-visible` indicators | ✅ |
| **Focus management on screen/panel change** | ✅ focus moves to the new screen heading |
| **WCAG AA text contrast** | ✅ grey hint/example + warning text darkened to ≥4.5:1 (palette unchanged) |
| **`aria-pressed` on language/path toggles + `<html lang>` sync** | ✅ |
| 44×44 px touch targets | ✅ |
| RTL layout for Arabic | ✅ logical CSS properties flip with direction |
| `prefers-reduced-motion` / `prefers-contrast: more` honoured | ✅ |
| Font-size scaler | ✅ (single 1.3× step — multi-step is a nice-to-have) |
| `aria-live` for save status, quality, preview | ✅ |
| Print stylesheet | ✅ |
| Full screen-reader audit (NVDA/JAWS) | 🚧 |
| WCAG AA automated scan (axe / Lighthouse) | 🚧 |

---

## Privacy & DSGVO

This is not a marketing claim — it is enforced at the socket layer.

- **Default-on offline mode.** `tool-1/privacy/network_block.py` monkey-patches `socket.socket`, `socket.getaddrinfo`, `urllib.request.urlopen`, and `http.client.{HTTP,HTTPS}Connection` to refuse any non-loopback destination. Strict loopback-only (127.0.0.1, ::1, localhost) — no cloud allowlist, no exceptions. Disable only with `AMS_ENFORCE_OFFLINE=0` for development.
- **Per-machine SQLite.** Each laptop has its own `ams_jobassist.db`. No central server, no cloud sync.
- **Consent screen.** The "Create my CV" button is disabled until the participant ticks the box acknowledging local-only storage.
- **DSGVO Art. 20 portability.** Endpoint `GET /api/cv/{session_id}/my-data` returns every byte stored about the participant as a JSON download. Wired to the 🔒 *Meine Daten herunterladen* button.
- **DSGVO Art. 17 right to be forgotten.** `privacy/data_deletion.py` cascades from `users` → sessions → answers → cv_data → exported files, then verifies deletion.
- **Configurable retention.** Set `AMS_DATA_RETENTION_DAYS=90` and incomplete sessions older than that are deleted daily. Approved CVs are kept.
- **Trainer audit trail.** Every state-changing call in Tool 2 is logged with timestamp + API-key identity. Every export writes an `ExportLog` row.
- **The one opt-in outbound path is hardened.** The "check a specific job from a URL" feature is off by default and runs only on explicit per-action consent. It resolves the host once, **connects to the validated IP literal** (defeating DNS-rebinding/TOCTOU), re-validates every redirect hop, honours `robots.txt`, caps size/timeout, and sends no personal data. Everything else stays loopback-blocked.
- **Local-only CV endpoints.** Every endpoint that serves or mutates a CV by `session_id` (read, export, ATS, Bewerbungs-Check, skills edit, job-match) is gated to loopback — a process or page reaching `127.0.0.1:PORT` cannot read or rewrite another session's PII.
- **No markup/injection into exports.** User/AI text is XML-escaped before it enters the PDF renderer.

---

## Running tests

```bash
# Tool 1 — 852 tests
cd tool-1-cv-maker
python -m pytest tests/ --ignore=tests/demo_test.py -q

# Tool 2 — 57 tests
cd ../tool-2-trainer-dashboard
python -m pytest tests/ -q

# Packaging — 13 tests
cd .. && python -m pytest packaging/ -q
```

---

## Documentation map

| Document | Audience | Purpose |
|---|---|---|
| [FOR_MARKO.md](FOR_MARKO.md) | External reviewer | 5-min install + what to try + feedback questions |
| [DEMO_GUIDE.md](DEMO_GUIDE.md) | You, running the demo | Step-by-step script for showing the tool |
| [PITCH.md](PITCH.md) | AMS leadership | One-page case for adoption |
| [docs/AMS_INSTRUCTOR_GUIDE.md](docs/AMS_INSTRUCTOR_GUIDE.md) | AMS trainers | What it does for them, plain-language |
| [docs/ADMINISTRATOR_GUIDE.md](docs/ADMINISTRATOR_GUIDE.md) | AMS IT | Install, configure, data paths |
| [docs/TRAINER_DECISIONS_CHECKLIST.md](docs/TRAINER_DECISIONS_CHECKLIST.md) | AMS subject experts | Pre-launch sign-off items |
| [docs/FAQ.md](docs/FAQ.md) | Everyone | Common questions |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Developers | Module map, data flow, deployment |
| [API_DOCUMENTATION.md](API_DOCUMENTATION.md) | Developers / IT | REST contract |
| [PRIVACY_ENFORCEMENT.md](PRIVACY_ENFORCEMENT.md) | DSGVO auditors | How offline is enforced |
| [PLAN.md](PLAN.md) | Maintainers | Living checklist of everything done / pending |
| [PROGRESS.md](PROGRESS.md) | Maintainers | Phase milestones |
| [docs/screenshots/README.md](docs/screenshots/README.md) | Anyone running the demo | Screenshot capture checklist |

---

## Known limitations

Honest about what this is and isn't:

- **Desktop only.** Windows 10/11 is the target platform. The UI is touch-friendly (44 px targets, RTL Arabic) but designed for keyboard + mouse. Tablet form factor is not optimised yet.
- **No multi-trainer real-time collaboration.** Tool 2 is single-trainer-at-a-time on one machine. There is no central server, no shared state across laptops.
- **No central admin server.** Each laptop is independent. Backups are per-machine (one-click via `GET /api/admin/backup`).
- **Interview examples are placeholders.** The good/bad example chips next to each question contain Mina-authored sample text. Real AMS sign-off and anonymised real-cohort samples are needed before classroom pilot.
- **UI translation coverage is uneven.** German and English are complete and author-quality. The other 10 languages are ~⅓ German-fallback — the interactive interview core (the conversation prompts, status messages, Bewerbungs-Check, skills editor) still falls back to German for them. The fallback mechanism is correct; the missing strings need a native translator (they are deliberately not machine-fabricated).
- **Arabic-script names still render as boxes in the PDF.** The exporter now bundles DejaVuSans (Latin + Cyrillic + Latin-extended), so Russian/Ukrainian/Serbian/Turkish/Polish names render correctly. Arabic needs a Naskh Arabic TTF that can't be fetched in an offline build — the font-registration hook is in place, so dropping one into `tool-1-cv-maker/data/fonts/` enables it. DOCX RTL direction for Arabic is also pending.
- **Translate-first measured; gold set is small for non-German.** Non-German dumps are translated to German before extraction. Measured lift: Arabic/Russian core-field F1 **0.00 → 0.75**, overall macro-F1 0.765 → 0.808. Turkish/Polish dipped slightly (0.27 → 0.20) but on only one case each — the gold dataset has just 1–2 cases per non-German language, so per-language numbers are noisy and more gold cases are needed for a firm read.
- **Rules-first AI architecture.** The rule engine (117 German verbs, 70 English verbs, 428 multilingual skills) does the heavy lifting — verb enforcement, skill normalization, ATS optimization. A local knowledge base (25 Austrian jobs from AMS Berufslexikon with 197 verbs, 171 skills, 75 example phrases) provides domain context. The local LLM (3 tiers: light/medium/full) only enhances already-polished text for natural flow. Runs in-process (llama-cpp); Ollama is an opt-in alternative (AMS_USE_OLLAMA=1); falls back to rule output as-is.
- **Authenticode code-signing is not yet applied** to the `.exe` artifacts. Windows SmartScreen will warn on first run. A signing certificate is on the to-do list.
- **Full WCAG 2.1 AA automated audit (axe-core / Lighthouse) has not been run.** The CSS scaffolding (focus rings, touch targets, prefers-reduced-motion / prefers-contrast / RTL / print stylesheet, skip-link) is in place but not externally verified. Screen-reader testing with NVDA / JAWS is pending.
- **Cohort creation UI and per-participant trainer-notes UI are pending** in Tool 2. The backend supports both (cohort filters, `trainer_notes` column); the frontend table view doesn't yet expose them.
- **Conversational LLM interview is not implemented.** It was a 501-skeleton placeholder; that placeholder has been removed and will return when the feature is actually built.
- **The maintainer is one person** (MIT license, no organisation backing). For a real AMS deployment, expect either a service contract with the maintainer or an AMS-internal fork.

---

## Status

- **Tool 1 (CV Maker):** ✅ Production-ready
- **Tool 2 (Trainer Dashboard):** ✅ All spec features wired with audit/auth; import is now lossless (languages + target job preserved)
- **Windows .exe build:** ✅ Reproducible — 3 artifacts from `build_all.bat` (now also bundles `data/fonts`)
- **Tests:** ✅ 922 (852 Tool 1 + 57 Tool 2 + 13 packaging), 0 failures
- **Security:** ✅ Audited & remediated — SSRF-hardened opt-in fetch, PDF injection-escaped, CV endpoints loopback-gated, inference serialized, input capped
- **Accessibility:** ✅ Read-aloud, focus management, AA contrast, ARIA states, RTL — automated WCAG scan + screen-reader audit still pending
- **AMS trainer sign-off:** ⏳ Pending — see [TRAINER_DECISIONS_CHECKLIST.md](docs/TRAINER_DECISIONS_CHECKLIST.md)
- **Pilot in a real classroom:** ⏳ Pending an AMS partner

### Capability confidence

How sure we are each capability does what it claims, and why:

| Capability | Confidence | Basis |
|---|---|---|
| Conversational profile → structured CV (German/English) | **High** | Gold-set core-field F1 ≈ 0.84 (DE) / 0.90 (EN); 852 tests |
| Same, for non-Latin input (Arabic/Russian) | **Medium-High** | Translate-first measured: Arabic/Russian core-field F1 **0.00 → 0.75**, overall macro-F1 0.765 → 0.808. (Turkish/Polish noisy on a 1-case-each sample — gold set needs more non-German cases.) |
| PDF / DOCX / JSON / Europass export | **High** | Live-verified real files incl. Cyrillic name + embedded Unicode font; 294 export tests |
| Bewerbungs-Check (hire-readiness) | **High** | Weighted, deterministic, gated on real fields; live-verified 90% on a complete CV |
| Cover letter / application email | **High** | Template-based ÖNORM/email; correct salutation + no placeholder leakage live-verified |
| AMS job-search bridge + occupation suggestion | **High** | Deep-link builds offline; 53-occupation taxonomy; Programmierer→Softwareentwickler fix verified |
| Check a specific job from a URL | **High (mechanics)** | SSRF/robots/consent unit-tested; depends on the target site allowing fetch |
| Skill extraction & editing | **Medium** | Extraction ≈ 0.40 F1 (weakest field) — mitigated by the editable-skills UI so the user corrects it |
| German level (CEFR) honesty | **High** | Only emits a band when stated; native-language wording supported; never fabricates |
| Trainer review/edit/export (Tool 2) | **High** | Round-trip verified faithful (languages + target job survive); 57 tests |
| Offline / privacy guarantee | **High** | Socket-layer enforced; audited; only opt-in fetch reaches the net, and that is IP-pinned |
| Read-aloud / accessibility | **Medium-High** | Live-verified (TTS, focus, contrast, ARIA); formal WCAG + screen-reader audit pending |
| Standalone `.exe` (no Python) | **Medium** | Previously verified loading the model + extracting; needs a rebuild with this session's changes (fonts) + re-smoke before shipping |

License: MIT — open for AMS centres and any other employment service to use and modify.
