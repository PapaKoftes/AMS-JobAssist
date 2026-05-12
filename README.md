<p align="center">
  <img src="docs/img/banner.png" alt="AMS JobAssist" width="100%">
</p>

# AMS JobAssist

**An offline CV builder for AMS course participants — with a trainer dashboard for supervision.**
Built for AMS Wien classroom use. Runs entirely on the trainer's laptop. No cloud, no data leaves the device.

![Status](https://img.shields.io/badge/Status-Demo--ready-brightgreen)
![Tests](https://img.shields.io/badge/Tests-725%20passing-brightgreen)
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

## Quick start (developers)

```bash
git clone https://github.com/PapaKoftes/AMS-JobAssist
cd AMS-JobAssist
pip install -r requirements.txt
python launcher.py
```

The launcher starts both servers and opens your browser to the CV maker on `http://localhost:8000`. The trainer dashboard is on `http://localhost:8001`.

**Or build the Windows .exe bundle** (no Python needed on the target machine):

```bat
build_all.bat
```

This produces three standalone executables in `dist/`:

| File | Size | What it does |
|---|---|---|
| `AMS-JobAssist-Launcher.exe` | 8 MB | Starts both tools, opens browser |
| `AMS-JobAssist-Tool1.exe` | 375 MB | Participant CV maker (includes optional LLM runtime) |
| `AMS-JobAssist-Tool2.exe` | 46 MB | Trainer dashboard |

For non-technical users, the project also ships `ams_jobassist.bat` — a German menu that handles install / start / uninstall / data-deletion through `pip` rather than a packaged exe.

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
│   └── tests/                683 tests
├── tool-2-trainer-dashboard/ Trainer interface
│   ├── src/backend/          FastAPI + SQLAlchemy + audit middleware
│   ├── frontend/             Vanilla JS table view + side-by-side compare
│   └── tests/                42 tests
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
| Multi-language input | ✅ | Detected automatically (12 supported, with German polish at output) |
| Live preview | ✅ | See your CV growing as you answer |
| Quality scoring | ✅ | Encouraging feedback ("a little more detail helps") |
| Quick-fill chips | ✅ | One-tap starters for common answers |
| Date helper | ✅ | "approximate" allowed — no shame on forgotten dates |
| Photo upload | ✅ | Optional — Austrian-style CV with photo |
| Resume after close | ✅ | Browser session restores from where you left off |
| PDF / DOCX / Europass / JSON export | ✅ | All four formats, deterministic output |
| Cover letter generator | ✅ | AI-assisted, downloadable as TXT |
| ATS / job match | ✅ | Paste a job listing, see matched + missing keywords |
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
| Notes per participant | 🚧 | Backend supports it; frontend UI pending |
| Cohort creation UI | 🚧 | Backend done; frontend UI pending |

### Accessibility

| Feature | Status |
|---|---|
| Skip-navigation link | ✅ |
| Visible `:focus-visible` indicators | ✅ |
| 44×44 px touch targets | ✅ |
| RTL layout for Arabic | ✅ |
| `prefers-reduced-motion` honoured | ✅ |
| `prefers-contrast: more` honoured | ✅ |
| Font-size scaler | ✅ |
| `aria-live` for save status, quality, preview | ✅ |
| Print stylesheet | ✅ |
| Full screen-reader audit | 🚧 |
| WCAG AA automated scan (axe / Lighthouse) | 🚧 |

---

## Privacy & DSGVO

This is not a marketing claim — it is enforced at the socket layer.

- **Default-on offline mode.** `tool-1/privacy/network_block.py` monkey-patches `socket.socket`, `socket.getaddrinfo`, `urllib.request.urlopen`, and `http.client.{HTTP,HTTPS}Connection` to refuse any non-loopback destination. Loopback (127.0.0.1, ::1, localhost) is allowlisted so the FastAPI server itself keeps working. Disable only with `AMS_ENFORCE_OFFLINE=0` for development.
- **Per-machine SQLite.** Each laptop has its own `ams_jobassist.db`. No central server, no cloud sync.
- **Consent screen.** The "Create my CV" button is disabled until the participant ticks the box acknowledging local-only storage.
- **DSGVO Art. 20 portability.** Endpoint `GET /api/cv/{session_id}/my-data` returns every byte stored about the participant as a JSON download. Wired to the 🔒 *Meine Daten herunterladen* button.
- **DSGVO Art. 17 right to be forgotten.** `privacy/data_deletion.py` cascades from `users` → sessions → answers → cv_data → exported files, then verifies deletion.
- **Configurable retention.** Set `AMS_DATA_RETENTION_DAYS=90` and incomplete sessions older than that are deleted daily. Approved CVs are kept.
- **Trainer audit trail.** Every state-changing call in Tool 2 is logged with timestamp + API-key identity. Every export writes an `ExportLog` row.

---

## Running tests

```bash
# Tool 1 — 683 tests
cd tool-1-cv-maker
python -m pytest tests/ --ignore=tests/demo_test.py -q

# Tool 2 — 42 tests
cd ../tool-2-trainer-dashboard
python -m pytest tests/ -q
```

---

## Documentation map

| Document | Audience | Purpose |
|---|---|---|
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

## Status

- **Tool 1 (CV Maker):** ✅ Production-ready
- **Tool 2 (Trainer Dashboard):** ✅ All spec features wired with audit/auth
- **Windows .exe build:** ✅ Reproducible — 3 artifacts produced from `build_all.bat`
- **Tests:** ✅ 725 passing
- **Accessibility quick wins:** ✅ Focus rings, touch targets, RTL, print stylesheet, contrast/motion preferences
- **AMS trainer sign-off:** ⏳ Pending — see [TRAINER_DECISIONS_CHECKLIST.md](docs/TRAINER_DECISIONS_CHECKLIST.md)
- **Pilot in a real classroom:** ⏳ Pending an AMS partner

License: MIT — open for AMS centres and any other employment service to use and modify.
