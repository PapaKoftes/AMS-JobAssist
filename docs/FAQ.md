# AMS JobAssist - Frequently Asked Questions

**Version**: 1.0
**Date**: 2026-05-12
**Last Updated**: 2026-05-12

---

## Getting Started

### Q: Do I need internet to use AMS JobAssist?
**A**: No. Offline mode is **on by default** (`AMS_ENFORCE_OFFLINE=1`). The system runs entirely on the local machine. The built-in network block allowlists loopback (`127.0.0.1` / `localhost`), so the FastAPI server and the browser UI continue to work normally while outbound internet calls are blocked at the socket layer. This is enforced by design to protect participant data under DSGVO/GDPR.

### Q: What languages does the system support?
**A**: The UI is fully translated into **12 languages**:

| Code | Language | Code | Language |
|------|----------|------|----------|
| de | Deutsch (default) | tr | Türkçe |
| en | English | pl | Polski |
| bs | Bosanski | ro | Română |
| hr | Hrvatski | uk | Українська |
| sr | Srpski | ru | Русский |
| sk | Slovenčina | ar | العربية (RTL) |

Participants can answer in any language they prefer; the system normalizes content to German / English / native for the final CV. Arabic is rendered right-to-left throughout the UI.

### Q: How long does an interview take?
**A**: Typically **30-60 minutes**, depending on:
- Interview path chosen (unemployed ~45 min, student ~30 min)
- Detail level of answers
- Whether quick-fill suggestions are used

Participants can save and resume — they do not have to finish in one sitting.

### Q: Can I change the interview questions?
**A**: The 5 paths and their questions are hardcoded for v1.0 to guarantee consistent CV quality. Trainers can supplement with:
- Pre-interview conversations
- Live feedback during the session
- Inline edits in Tool 2 after the interview

Custom question editing is on the v1.1 roadmap.

---

## Tool 1 (CV Maker) Questions

### Q: My participant closed the tool. Can they resume later?
**A**: Yes. Autosave runs after every answer. To resume:
1. Re-open Tool 1 (launcher or directly at `http://localhost:8000`)
2. Enter the same session/user ID
3. The system shows the resume marker and continues from the next unanswered question

### Q: What if a participant enters the wrong session ID?
**A**: They start a fresh interview. The original session is still in the database. The trainer/admin can recover it via Tool 2 (search by name) or by querying the SQLite file directly.

**Prevention**: Hand out printed session-ID slips at the start of the class.

### Q: The system says the answer is "too short". How can I help?
**A**: The polish layer asks for more detail when an answer is below the minimum length / quality threshold. Encourage the participant to add:
- A concrete daily task
- A tool or system they used
- A person/role they helped

**Example**:
- Too short: "Worked in a factory" (4 words)
- Good: "Worked in automotive factory assembling car parts, quality-checking every 10th unit" (12 words)

### Q: Why did my raw answer get rewritten so much?
**A**: The polish layer applies professional CV conventions: action verbs, consistent structure, and skill normalization (e.g., "office work" -> "Microsoft Office (Word, Excel, Outlook)"). The original raw text is preserved in the database — Tool 2 shows raw vs. improved side-by-side as a teaching aid.

### Q: Is the AI required?
**A**: No. The local AI engine (**Qwen2.5-1.5B GGUF**, ~1.1 GB) is **optional**. Drop the model file into `tool-1-cv-maker/data/models/` to enable it. Without it, the system falls back to the deterministic rule-based polish layer. Both paths produce a valid CV; the AI just yields more natural phrasing.

### Q: What if my language isn't in the UI list?
**A**: Use the closest available language. Participant answers can still be typed in any language — the polish/translation pipeline handles input language detection. New UI languages are added based on demand.

---

## Tool 2 (Trainer Dashboard) Questions

### Q: Is Tool 2 finished or still under development?
**A**: Tool 2 is **feature-complete** as of v1.0. All of the following work end-to-end:
- Cohort and participant browsing with metrics
- Side-by-side raw vs. improved comparison
- Inline editing with full audit trail
- Bulk approve / reject across selected participants
- Bulk export to PDF, DOCX, or JSON ZIP
- Lock / unlock to prevent further participant edits
- API-key authentication (`AMS_TRAINER_API_KEY`)

### Q: How do I import participant CVs?
**A**:

**Single CV**:
1. Receive the `.json` export from the participant (Tool 1 -> Export -> JSON)
2. Tool 2 -> Import -> select file -> Import

**Batch import**:
1. Collect all `.json` files
2. ZIP them
3. Tool 2 -> Import -> select ZIP -> Import
4. Assign a cohort name in the import dialog

### Q: What does the quality score mean?
**A**: A 0.0-1.0 score reflecting CV-readiness:

| Score | Meaning | Example |
|-------|---------|---------|
| 0.60-0.65 | Weak | "Worked in retail" |
| 0.65-0.75 | Acceptable | "Managed retail store, served customers" |
| 0.75-0.85 | Good | "Managed 3-person retail team, improved sales 15%" |
| 0.85+ | Excellent | "Led team of 3, increased sales 15%, 98% CSAT" |

Anything under 0.70 is a good candidate for trainer feedback.

### Q: Can I edit a participant's CV in Tool 2?
**A**: Yes. Click any section to edit inline; changes save instantly and are written to the `export_logs` audit table along with trainer ID and timestamp. The original Tool 1 record is left untouched so you always have the raw version.

### Q: How do I bulk-approve participants?
**A**:
1. Filter / select participants via checkboxes (or "Select All")
2. Click **Approve Selected**
3. Confirm in the dialog

The state change is atomic and written to the audit log.

### Q: How do I export CVs?
**A**:
1. Select participants
2. Click **Export Selected**
3. Choose format: PDF / DOCX / JSON (ZIP bundle for batch exports)
4. Choose language: de / en / native
5. Download

Filter by status = `Approved` to export only finished CVs.

### Q: Can I lock a CV so the participant cannot change it?
**A**: Yes. Use the lock/unlock toggle in Tool 2. Locked sessions still allow trainer edits but reject further participant submissions to the API.

---

## Data & Privacy (DSGVO / GDPR)

### Q: Where exactly is my participant data stored?
**A**: On the local machine, in two SQLite files:

| File | Path | Purpose |
|------|------|---------|
| Tool 1 DB | `tool-1-cv-maker/data/ams_jobassist.db` | Interview sessions, answers, polish output |
| Tool 2 DB | `tool-2-trainer-dashboard/data/ams_trainer.db` | Cohorts, approvals, edits, `export_logs` audit |
| Exports | `tool-1-cv-maker/data/exports/` | Generated PDF/DOCX files |
| AI model | `tool-1-cv-maker/data/models/` | Optional GGUF weights |

Nothing leaves the machine. No cloud, no telemetry, no auto-update.

### Q: How do I back up the database?
**A**: Just copy the `.db` files. SQLite is a single-file database.

```batch
copy tool-1-cv-maker\data\ams_jobassist.db    D:\backups\ams_jobassist_2026-05-12.db
copy tool-2-trainer-dashboard\data\ams_trainer.db D:\backups\ams_trainer_2026-05-12.db
```

For automation, schedule the copy with Windows Task Scheduler. To restore, close the tools first and replace the files.

### Q: Can I run this on a tablet?
**A**: **No.** AMS JobAssist is **desktop-only** (Windows). The UI is touch-friendly (44 px touch targets, focus rings, large hit areas) but is not designed for tablet form factors. Use a laptop or desktop with mouse/keyboard. The `.exe` artifacts are Windows builds; macOS / Linux / iPadOS / Android are not supported.

### Q: How do I fulfil a DSGVO Art. 20 data-portability request?
**A**: Tool 1 exposes:

```
GET /api/cv/{session_id}/my-data
```

This returns the complete participant record (raw answers, polished output, metadata) as machine-readable JSON. Hand the file to the participant.

### Q: How do I fulfil a DSGVO Art. 17 erasure request?
**A**: Use the deletion helper at `privacy/data_deletion.py`. It removes the participant's row from both databases and purges associated exports. Retention can also be automated via the `AMS_DATA_RETENTION_DAYS` environment variable — records older than the configured cutoff are purged on launcher start.

### Q: Can anyone access participant data?
**A**: Only someone with access to the Windows user account where the `.db` files live. To restrict further:
- Use separate Windows accounts per trainer
- Enable BitLocker on the drive (Windows Pro/Enterprise)
- Set `AMS_TRAINER_API_KEY` to require an API key on Tool 2 endpoints
- Lock the machine when unattended

---

## Export & Reporting

### Q: What formats can I export CVs in?
**A**:

| Format | Editable? | Best for |
|--------|-----------|----------|
| PDF    | No        | Sending to employers, archiving |
| DOCX   | Yes (Word) | Job-specific customization |
| JSON   | Machine-readable | Integrations, re-import, DSGVO Art. 20 |

Batch exports come as a single ZIP.

### Q: Can I export to Excel?
**A**: Use Tool 2 -> Reports -> Export Participants CSV, then open in Excel / LibreOffice / Google Sheets for pivot tables and custom reports.

### Q: Can I change the CV template / layout?
**A**: Layout is fixed in v1.0 for consistency. You can change language (de/en/native) and format (PDF/DOCX/JSON). For visual customization, export DOCX and edit in Word.

---

## Accessibility

### Q: What accessibility features ship with v1.0?
**A**: All of the following are active by default:

| Feature | Notes |
|---------|-------|
| Focus rings | High-contrast outlines on all interactive elements |
| 44 px touch targets | Meets WCAG 2.5.5 |
| RTL layout | Full mirroring for Arabic |
| Reduced-motion | Honours `prefers-reduced-motion` |
| Contrast preferences | Honours `prefers-contrast: more` |
| Print stylesheet | CVs print cleanly without UI chrome |
| Skip link | Keyboard users skip nav to main content |

---

## Trainer Features

### Q: Can I see who made which edits?
**A**: Yes. Every trainer edit, approval, lock, and export is recorded in the `export_logs` table of `ams_trainer.db` with trainer ID, action, target, and ISO timestamp. See the Administrator Guide for a sample SQL query.

### Q: Can multiple trainers review the same participants?
**A**: Yes, but there is no row-level locking. Last write wins on simultaneous edits. Best practice: assign participants to specific trainers (visible via the `assigned_to` field) or use the session-level lock toggle while reviewing.

### Q: Can I create custom reports?
**A**: Built-in reports cover cohort metrics, approval rates, and quality-score distribution. For anything bespoke, export the CSV or query the SQLite file directly with any SQL client.

---

## Technical

### Q: What ships in the v1.0 release?
**A**: Three reproducible Windows binaries built by `build_all.bat` (verified 2026-05-12):

| Artifact | Size | Purpose |
|----------|------|---------|
| `AMS-JobAssist-Launcher.exe` | ~8 MB | Starts/stops both tools, German tray UI |
| `AMS-JobAssist-Tool1.exe` | ~375 MB | Tool 1 server (includes optional AI deps) |
| `AMS-JobAssist-Tool2.exe` | ~46 MB | Tool 2 server |

All three PyInstaller specs are relocatable via `SPECPATH` and include the full set of `hiddenimports`. No Python install is required on target machines.

### Q: How big is the test suite?
**A**: **725 tests** total — 683 covering Tool 1, 42 covering Tool 2. They run via `pytest` from the repo root and cover the polish layer, interview engine, exports, DSGVO endpoints, audit logging, and bulk operations.

### Q: What are the minimum system requirements?
**A**:

| Resource | Minimum | Recommended |
|----------|---------|-------------|
| OS | Windows 10 | Windows 11 |
| RAM | 4 GB | 8 GB (16 GB if local AI is enabled) |
| Disk | 1 GB | 2 GB (plus ~1.1 GB if GGUF model is loaded) |
| Screen | 1024x768 | 1366x768 or higher |
| Browser | Edge / Chrome / Firefox | Edge or Chrome |

### Q: Can I run it on Mac or Linux?
**A**: Not officially. v1.0 distributes Windows `.exe` builds only. The Python source itself is portable; experienced users can run `uvicorn` directly on macOS/Linux, but this path is unsupported.

### Q: Can I run multiple instances on one machine?
**A**: Not on the same ports. The launcher auto-advances to the next free port if 8000 / 8001 are taken, but the two tools must not collide. For parallel classroom use, deploy on separate machines.

### Q: How big can the database get?
**A**: Practically unlimited:

| Participants | Approx. DB size |
|--------------|----------------|
| 100 | ~1 MB |
| 1,000 | ~10 MB |
| 10,000 | ~100 MB |

Performance stays good up to ~1 GB. Beyond that, archive old cohorts and start a fresh DB per training year.

---

## Troubleshooting (Quick)

### Q: Tools won't start.
**A**:
1. Wait 10-15 seconds for both `.exe` servers to boot
2. Check Task Manager for `AMS-JobAssist-Tool1.exe` / `Tool2.exe`
3. If a port is occupied the launcher auto-advances; check the console window for the actual port
4. Right-click the launcher and **Run as Administrator** if Windows blocks the bind

### Q: "Cannot connect to server".
**A**: Most often a firewall prompt. Allow Python / the `.exe` through Windows Defender Firewall on **Private** networks. The offline guard does **not** block loopback, so localhost always works once the firewall allows the bind.

### Q: Database error or "no such table".
**A**: Restore from a backup copy of the `.db` file. If no backup exists, delete the corrupted file — the launcher creates a fresh schema on next start. Re-import participants from JSON if available.

### Q: pip install fails on `llama-cpp-python` when building from source.
**A**: Skip the `[ai]` extra:

```
pip install -r requirements.txt
```

without the AI extra. The rule-based polish layer covers all functionality; only natural-language phrasing is reduced.

---

## Feature Requests & Support

### Q: What's planned beyond v1.0?
**A**:
- v1.1: Customizable interview questions, job-specific tailoring, finer-grained edit history
- v1.2: Additional UI languages, expanded reporting, optional CV templates
- v2.0: macOS / Linux builds, optional encrypted sync

### Q: I found a bug. How do I report it?
**A**: Open an issue with reproduction steps, the launcher console output, your Windows version, and a screenshot. The audit log (`export_logs`) in `ams_trainer.db` is often useful for trainer-side issues.

---

## Version History

**v1.0** (2026-05-12)
- 725 tests passing (683 Tool 1 + 42 Tool 2)
- Offline mode on by default with loopback allowlist
- 3 reproducible `.exe` artifacts via `build_all.bat`
- 12 UI languages including RTL Arabic
- DSGVO Art. 17 / Art. 20 endpoints
- Optional Qwen2.5-1.5B local AI with rule-based fallback
- Full accessibility pass (focus, touch, RTL, reduced-motion, print)

---

**Questions not answered here?**
See `ADMINISTRATOR_GUIDE.md` (installation / IT) or `TRAINER_QUICK_START.md` (classroom use).
