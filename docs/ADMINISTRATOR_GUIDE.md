# AMS JobAssist - Administrator Guide

**Version**: 1.0
**Date**: 2026-05-12
**Audience**: AMS IT staff installing and operating the tool in a classroom

---

## Table of Contents

1. [Overview](#overview)
2. [System Requirements](#system-requirements)
3. [Installation](#installation)
4. [Configuration](#configuration)
5. [Database & Storage Layout](#database--storage-layout)
6. [Backup & Recovery](#backup--recovery)
7. [Audit Log](#audit-log)
8. [Security & Offline Mode](#security--offline-mode)
9. [DSGVO / GDPR Operations](#dsgvo--gdpr-operations)
10. [Troubleshooting](#troubleshooting)
11. [Updating](#updating)

---

## Overview

AMS JobAssist v1.0 ships as three reproducible Windows executables, built end-to-end by `build_all.bat` (last verified 2026-05-12). No Python install on the target machine is required for the `.exe` path.

| Artifact | Approx. size | Purpose |
|----------|--------------|---------|
| `dist\AMS-JobAssist-Launcher.exe` | ~8 MB | Tray launcher; starts/stops both tools, German menu |
| `dist\AMS-JobAssist-Tool1.exe` | ~375 MB | Participant CV maker (FastAPI server, optional local AI) |
| `dist\AMS-JobAssist-Tool2.exe` | ~46 MB | Trainer dashboard (FastAPI server) |

All three PyInstaller specs use `SPECPATH` so the build is relocatable; the `hiddenimports` list is complete and reviewed.

For non-developer classroom installs we also ship `ams_jobassist.bat`, a German-language menu wrapping install / start / uninstall / delete-data.

---

## System Requirements

| Resource | Minimum | Recommended |
|----------|---------|-------------|
| OS | Windows 10 (64-bit) | Windows 11 |
| CPU | Any x64 from 2015+ | 4+ cores |
| RAM | 4 GB | 8 GB (16 GB if optional GGUF AI is loaded) |
| Disk | 1 GB free | 2 GB free + ~1.1 GB for optional GGUF |
| Display | 1024x768 | 1366x768 or higher |
| Browser | Edge / Chrome / Firefox (current) | Edge or Chrome |
| Network | None required | None required (offline by default) |

Tablets, smartphones, macOS, and Linux are **not** supported in v1.0.

---

## Installation

### Path A - Windows installer (recommended for classroom IT)

No Python required. No admin rights required.

**Option 1 — Setup.exe (if available)**

1. Copy `AMS-JobAssist-Setup.exe` onto the target machine (USB stick or LAN share).
2. Double-click. The installer wizard runs in German (English also available).
3. Accept defaults or change the install directory.
4. Optionally create a Desktop shortcut.
5. Click "Fertigstellen" — AMS JobAssist launches automatically.

Uninstall via Windows Settings > Apps > AMS JobAssist, or Start Menu > AMS JobAssist > Deinstallieren.

**Option 2 — Batch installer**

1. Copy the `dist\` folder onto the target machine.
2. Double-click `install.bat` inside `dist\`.
3. Follow the German prompts (creates Start Menu entry + Add/Remove Programs registration).

Uninstall via Add/Remove Programs or `uninstall.bat` in the install directory.

**Option 3 — Run directly (no install)**

1. Copy the `dist\` folder onto the target machine.
2. Double-click `AMS-JobAssist-Launcher.exe`.
3. No shortcuts, no registry entries — just runs.

### Path A-alt - German menu (`ams_jobassist.bat`, requires Python)

Hand this path to trainers who already have Python installed.

1. Copy the release folder onto the target machine (USB stick or LAN share).
2. Double-click `ams_jobassist.bat`. A German menu appears:
   - **Installieren und Starten** — runs pip install + launches
   - **Starten** — launches (if already installed)
   - **Deinstallieren** — removes pip packages
   - **Daten loeschen** — wipes both `.db` files (with double confirmation)
3. Pick **Installieren und Starten** the first time.
4. The launcher opens the default browser to `http://localhost:8000` (Tool 1) and `http://localhost:8001` (Tool 2).

### Path B - Developer / build from source

Use this if you want to rebuild the `.exe` artifacts or contribute changes.

```powershell
git clone <repo-url>
cd AMS-JobAssist
pip install -r requirements.txt
build_all.bat
```

`requirements.txt` at the repo root installs **everything** for both tools and the launcher in one shot. Build artifacts land in `dist/`. The build is reproducible and is verified by CI on every push.

If `llama-cpp-python` fails to compile (common on machines without MSVC build tools), skip the `[ai]` extra — the tool still runs in rule-based mode.

### First-run checks

After `Starten`, confirm:

- Launcher tray icon visible
- `http://localhost:8000` shows the Tool 1 welcome screen
- `http://localhost:8001` shows the Tool 2 login (API key required if `AMS_TRAINER_API_KEY` is set)
- `tool-1-cv-maker/data/ams_jobassist.db` and `tool-2-trainer-dashboard/data/ams_trainer.db` were created

---

## Configuration

All configuration is driven by environment variables. Set them in the shell that launches `ams_jobassist.bat` or via Windows **System Properties -> Environment Variables**.

| Variable | Default | Purpose |
|----------|---------|---------|
| `AMS_TOOL1_PORT` | `8000` | Bind port for Tool 1 (CV maker) |
| `AMS_TOOL2_PORT` | `8001` | Bind port for Tool 2 (dashboard) |
| `AMS_DATA_DIR` | per-tool `data/` | Override DB + exports root |
| `AMS_TRAINER_API_KEY` | _(unset)_ | If set, Tool 2 requires this header |
| `AMS_DATA_RETENTION_DAYS` | _(unset)_ | If set, records older than N days are purged on startup |
| `AMS_MODEL_TIER` | _(auto-detect)_ | AI model tier: `light` (~400 MB), `medium` (~1.1 GB), `full` (~2 GB) |
| `AMS_ENFORCE_OFFLINE` | `1` | Block outbound network at socket layer (loopback allowlisted) |

If a port is occupied the launcher auto-advances to the next free port and prints the actual URL in the console — do not assume 8000/8001.

---

## Database & Storage Layout

```
AMS-JobAssist/
+-- tool-1-cv-maker/
|   +-- data/
|       +-- ams_jobassist.db        # sessions, answers, polish output
|       +-- exports/                # generated PDF / DOCX bundles
|       +-- models/                 # optional Qwen2.5-1.5B GGUF (~1.1 GB)
|       +-- knowledge/              # Austrian job knowledge base (berufe.json)
+-- tool-2-trainer-dashboard/
|   +-- data/
|       +-- ams_trainer.db          # cohorts, approvals, audit log
+-- dist/
    +-- AMS-JobAssist-Launcher.exe
    +-- AMS-JobAssist-Tool1.exe
    +-- AMS-JobAssist-Tool2.exe
```

Both databases are plain SQLite, single-file. They can be opened with any SQL client (DB Browser for SQLite is free and works well).

To relocate data — e.g., onto an encrypted drive — set `AMS_DATA_DIR=D:\AMS-Daten\` before launching. The tools will create / read the `.db` files there.

---

## Backup & Recovery

### Backups

**Just copy the `.db` files.** Both databases are single SQLite files; no dump/restore tooling needed.

```batch
@echo off
set STAMP=%date:~-4%%date:~-7,2%%date:~-10,2%
set DEST=D:\AMS-Backups\
mkdir "%DEST%" >nul 2>&1
copy /Y "tool-1-cv-maker\data\ams_jobassist.db"     "%DEST%ams_jobassist_%STAMP%.db"
copy /Y "tool-2-trainer-dashboard\data\ams_trainer.db" "%DEST%ams_trainer_%STAMP%.db"
```

Wire that into Windows Task Scheduler for nightly backups. Recommended retention: 4 weeks rolling, plus monthly archives.

### Recovery

1. Close the launcher (both servers must be stopped to release file locks).
2. Replace the corrupt / lost `.db` file with the backup copy at the same path.
3. Start the launcher.
4. Spot-check in Tool 2 that cohorts and approvals are intact.

### Integrity check

```
sqlite3 tool-2-trainer-dashboard\data\ams_trainer.db "PRAGMA integrity_check;"
```

Should return `ok`. Anything else: restore from backup.

---

## Audit Log

Every trainer action that affects a participant is written to `ams_trainer.db` in the `export_logs` table.

Sample query — show the last 50 audit events:

```sql
SELECT created_at, trainer_id, action, target_session_id, details
FROM export_logs
ORDER BY created_at DESC
LIMIT 50;
```

Common `action` values:
- `edit_section` — inline edit in the dashboard
- `approve` / `reject` — status change
- `bulk_approve` / `bulk_export`
- `lock` / `unlock`
- `export_pdf` / `export_docx` / `export_json`
- `delete_participant`

Hand this table to AMS data-protection officers on request — it provides a tamper-evident timeline of every administrative action.

---

## Security & Offline Mode

### Offline by default

`AMS_ENFORCE_OFFLINE=1` is the default. The Python socket layer is monkey-patched at startup to refuse any non-loopback connection. **Loopback (`127.0.0.1`, `::1`, `localhost`) is explicitly allowlisted** so the FastAPI server, the browser, and inter-tool calls all continue to work.

To intentionally re-enable outbound networking (e.g., for an admin maintenance task), launch with:

```
set AMS_ENFORCE_OFFLINE=0
```

This is *not* recommended for classroom use.

### API-key auth on Tool 2

Set `AMS_TRAINER_API_KEY` to any string. Tool 2 will then require the `X-API-Key` header on all API endpoints. The browser UI prompts for it on first load and stores it in `sessionStorage`.

### File-system access

Both `.db` files inherit Windows ACLs from their parent folder. To restrict trainer-only access:

1. Move the data folder onto an NTFS volume.
2. Grant the trainer Windows account `Modify` and remove inherited permissions for `Users`.
3. Optionally enable BitLocker on the drive (Windows Pro / Enterprise).

---

## DSGVO / GDPR Operations

### Art. 20 - Right to data portability

```
GET http://localhost:8000/api/cv/{session_id}/my-data
```

Returns the participant's complete record (raw answers, polished output, metadata) as JSON. Save the response and hand it to the participant.

### Art. 17 - Right to erasure

Run the deletion helper:

```
python privacy/data_deletion.py --session-id <SESSION_ID>
```

This removes the participant from both `ams_jobassist.db` and `ams_trainer.db`, purges any export files for that session, and writes a `delete_participant` audit entry to `export_logs`.

### Retention automation

Set `AMS_DATA_RETENTION_DAYS=365` (or whatever your AMS policy mandates). On every launcher start, records older than the cutoff are automatically purged and the action is logged.

### Where data lives — one-page summary for your DPO

| Category | Location | Encryption at rest | Auto-delete |
|----------|----------|--------------------|-------------|
| Interview answers | `tool-1-cv-maker/data/ams_jobassist.db` | BitLocker (if enabled) | via retention env |
| Approvals & edits | `tool-2-trainer-dashboard/data/ams_trainer.db` | BitLocker (if enabled) | via retention env |
| Generated CVs | `tool-1-cv-maker/data/exports/` | BitLocker (if enabled) | purged on Art. 17 |
| AI model | `tool-1-cv-maker/data/models/` | n/a (no personal data) | manual |

No data ever leaves the machine in the default configuration.

---

## Troubleshooting

### Port conflict (8000 or 8001 already in use)

The launcher auto-advances to the next free port and prints the actual URL. If you need a specific port, set `AMS_TOOL1_PORT` / `AMS_TOOL2_PORT` and stop the conflicting process:

```
netstat -ano | findstr :8000
taskkill /PID <pid> /F
```

### Missing GGUF model file

If `tool-1-cv-maker/data/models/` is empty or the file is the wrong shape, Tool 1 logs a warning and runs the **rule-based polish + knowledge base** pipeline. All features still work — verb enforcement, skill normalization, ATS optimization, and Austrian job knowledge are all rule-based. The LLM only adds natural phrasing on top. To enable AI: drop the Qwen2.5-1.5B-Instruct GGUF (~1.1 GB) into that folder and restart.

### `pip install` fails on `llama-cpp-python`

This typically happens on machines without MSVC build tools. Skip the AI extra:

```
pip install -r requirements.txt
```

(no `[ai]`). Rule-based polish covers all functionality.

### "Cannot connect to localhost"

Almost always Windows Defender Firewall blocking the bind. Allow Python / the `.exe` through the Private profile. Offline mode does **not** block loopback — it never blocks `127.0.0.1`.

### Database appears corrupted

1. Stop the launcher.
2. Run `PRAGMA integrity_check;` (see [Backup & Recovery](#backup--recovery)).
3. Restore from the most recent backup `.db` file.
4. If no backup exists, delete the corrupt `.db` and let the launcher recreate the schema. Re-import participants from JSON exports if available.

### Slow startup

- 10-15 s cold-start is normal (PyInstaller unpacks into temp).
- Add `dist\*.exe` and the `data\` folder to your AV exclusion list.
- Use SSD storage for `data/` if HDD-bound.

### Browser doesn't auto-open

Look at the launcher console for the bound URL (auto-advanced port). Open it manually.

---

## Updating

The system does **not** auto-update — it cannot, because it is offline by default.

To roll a new release:

1. Back up both `.db` files (see [Backup & Recovery](#backup--recovery)).
2. Stop the launcher.
3. Replace the contents of `dist\` with the new release artifacts (or run `build_all.bat` if updating from source).
4. Restart the launcher. The schema migrates automatically on first read.
5. Spot-check in Tool 2 that previous cohorts and approvals are intact.
6. If anything looks wrong, roll back by restoring the `.db` backups and the previous `dist\` folder.

Test new releases in a staging install before rolling to a classroom.

---

## Support Checklist

Before opening a support ticket, gather:

- [ ] Launcher console output (full text or screenshot)
- [ ] Windows version (`winver`)
- [ ] RAM / disk free
- [ ] Output of `PRAGMA integrity_check;` on both `.db` files
- [ ] Last 20 rows of `export_logs` (Tool 2 issues only)
- [ ] Steps to reproduce
- [ ] Whether `AMS_ENFORCE_OFFLINE`, `AMS_TRAINER_API_KEY`, `AMS_DATA_DIR`, `AMS_DATA_RETENTION_DAYS` are set, and to what

---

## Version History

**v1.0** (2026-05-12)
- 3 reproducible Windows `.exe` artifacts (`build_all.bat` verified end-to-end)
- Offline mode default-on with loopback allowlist
- 549-test suite (507 Tool 1 + 42 Tool 2)
- 12 UI languages incl. RTL Arabic; polish pipeline detects 14+ input languages
- Tiered AI models: light (~400 MB), medium (~1.1 GB), full (~2 GB) — local LLM primary engine
- DSGVO Art. 17 / Art. 20 endpoints and retention env var
- Full `export_logs` audit trail in `ams_trainer.db`
- Optional Qwen2.5-1.5B local AI with rule-based fallback

---

**Contact**: your AMS internal IT distribution channel
