# AMS JobAssist — Data Retention Policy

**Purpose**: State exactly what AMS JobAssist keeps, how long, by what
mechanism, and how AMS can change it.
**Audience**: AMS trainers, AMS IT, AMS DPO.
**Code under review**: commit head of `AMS-JobAssist` as of 2026-05-12.
**Last revised**: 2026-05-13

---

## 1. Default retention windows

| Asset                                | Default retention                              | Mechanism                                                    |
| ------------------------------------ | ---------------------------------------------- | ------------------------------------------------------------ |
| Incomplete interview sessions        | **90 days** from `created_at`                  | `cleanup_old_sessions()` daily sweep                          |
| Autosave drafts (`answers` rows)     | Tied to parent session — deleted with session | SQLite `ON DELETE CASCADE` from `sessions`                    |
| Approved / locked CVs                | **Kept indefinitely** until manual deletion    | excluded from cleanup by `completed=1 OR approved=1 OR locked=1` |
| Exported files (PDF / DOCX / JSON)   | Lifetime of the parent session                 | filesystem; removed via `DataDeletion.delete_user_data()`     |
| `exports` audit table (Tool 1)        | Lifetime of the parent session                 | cascade delete with session row                                |
| `ExportLog` audit table (Tool 2)      | **90 days** (recommended), trainer-controlled  | manual deletion via Tool 2 admin                              |
| Application logs (stdout/stderr)     | Process lifetime only                          | not persisted to disk by default                              |
| Optional LLM weights                 | Indefinite                                     | not personal data; stored under `~/.cache/huggingface/`        |

The 90-day default was chosen to cover a typical AMS course (8–12 weeks)
plus a short follow-up window. See §6 for AMS-recommended adjustments.

---

## 2. The cleanup mechanism

Three components implement retention. They are deliberately layered so that
a failure in one is caught by the next.

### 2.1 The config knob — `config.py`

`tool-1-cv-maker/src/backend/config.py` (line 22):

```python
DATA_RETENTION_DAYS = int(os.environ.get("AMS_DATA_RETENTION_DAYS", "90"))
```

A value of `0` disables automatic retention (kept forever — not
recommended for production AMS installations). Any positive integer N
sets the cleanup threshold to N days.

### 2.2 The daily loop — `app.py`

`tool-1-cv-maker/src/backend/app.py` (lines 126–151) starts a background
task on FastAPI startup:

```python
async def _retention_loop(engine, days):
    while True:
        deleted = engine.cleanup_old_sessions(days)
        if deleted:
            logger.info(f"Data retention: removed {deleted} sessions older than {days} days")
        await asyncio.sleep(86_400)  # 24 h
```

The loop only starts if `DATA_RETENTION_DAYS > 0`. The first sweep runs
at startup; thereafter the sweep runs every 24 hours for as long as the
backend is running.

### 2.3 The actual delete — `interview/engine.py`

`tool-1-cv-maker/src/backend/interview/engine.py` (line 746):

```python
def cleanup_old_sessions(self, days_old: int = 90) -> int:
    result = self.db.execute_update(
        """DELETE FROM sessions
           WHERE created_at < datetime('now', '-' || ? || ' days')
             AND (completed IS NULL OR completed = 0)
             AND (locked IS NULL OR locked = 0)
             AND (approved IS NULL OR approved = 0)""",
        (days_old,)
    )
```

The query is the single source of truth for "which sessions get deleted":

- Older than `days_old` (compared to `created_at`).
- **Not** completed.
- **Not** locked by the trainer.
- **Not** approved by the trainer.

Foreign-key cascade then removes the matching rows from `answers`,
`cv_data`, and `exports`.

### 2.4 The admin endpoint — manual trigger

`tool-1-cv-maker/src/backend/api/interview.py` (line 752):

```
POST /api/interview/admin/cleanup-sessions?days_old=90
```

Returns:

```json
{"status": "success", "data": {"deleted": 7, "days_old": 90}}
```

Safe to call repeatedly. Use this to force a sweep without waiting for
the 24-hour loop tick — for example at the end of a course.

---

## 3. How to configure

### 3.1 Environment variable

Set before starting the backend:

```powershell
# Windows / PowerShell
$env:AMS_DATA_RETENTION_DAYS = "30"
python -m uvicorn app:app
```

```bash
# POSIX
AMS_DATA_RETENTION_DAYS=30 python -m uvicorn app:app
```

Recognised values:

- `0` — disable retention (keep forever). Not recommended.
- positive integer N — sweep daily, delete incomplete sessions older
  than N days.

The startup banner prints the current setting:

```
[OK] Data retention: sessions older than 30 days will be cleaned up daily
```

### 3.2 Packaged builds

Packaged AMS classroom builds ship with the default `AMS_DATA_RETENTION_DAYS=90`.
To change it, AMS IT edits the launcher script (`ams_jobassist.bat` on
Windows, `start_ams.sh` on POSIX) and adds the variable export above the
`uvicorn` line.

---

## 4. What gets KEPT

The cleanup query explicitly skips:

| Condition             | Why                                                                 |
| --------------------- | ------------------------------------------------------------------- |
| `completed = 1`       | The participant finished — the CV may still be in use                |
| `approved = 1`        | The trainer approved — part of the AMS course-record audit trail    |
| `locked = 1`          | The trainer locked the session — Art. 18 restriction                |

These sessions persist until either:

- the participant exercises Art. 17 erasure via the in-app delete button,
- the trainer manually deletes the row from the dashboard, or
- AMS performs the end-of-course bulk deletion (§7).

The optional photo, polished CV (`cv_data`), and exports follow the
session: kept as long as the session is kept, deleted when the session
is deleted.

---

## 5. What gets DELETED on retention sweep

Every 24 hours (or on admin trigger), the sweep removes:

- All `sessions` rows older than the threshold that are **not** completed,
  approved, or locked.
- All `answers` rows for those sessions (autosave drafts) — via cascade.
- All `cv_data` rows for those sessions (partial polish output) — via cascade.
- All `exports` rows for those sessions — via cascade.

This is the rough-input cleanup. A participant who abandons the interview
after typing a few answers, then never returns, will have their typed
text removed automatically 90 days later. No trainer action is required.

Files on disk (PDF / DOCX exports) are **not** removed by the sweep — the
sweep operates on the database only. If exports were generated for a
session that the sweep removes, the file paths are forgotten but the
files themselves remain on the trainer's filesystem and must be cleaned
up manually or as part of the end-of-course routine in §7.

---

## 6. Recommendation for AMS

| Deployment                       | `AMS_DATA_RETENTION_DAYS` |
| -------------------------------- | ------------------------- |
| Standard AMS course (8–12 weeks) | **90** (default)           |
| Short workshop (1–2 weeks)       | 30                        |
| Shared / kiosk laptop            | 1, plus manual deletion at end of every session |
| Single trainer's personal laptop | 90 — let the participant decide via Art. 17 |
| Audit / DPO test deployment      | 0 (disable sweep) — but commit to manual deletion |

90 days is the standard course-cycle recommendation. It is short enough
that abandoned drafts do not accumulate across cohorts, and long enough
that a participant returning after a brief gap finds their work intact.

---

## 7. What AMS must do at course end

The automatic sweep handles *incomplete* sessions. Completed, approved,
and locked sessions accumulate and need explicit AMS action at the close
of a course cycle.

The recommended end-of-course routine:

1. **Bulk export.** In Tool 2 (Trainer Dashboard), select all participants
   and click "Bulk Export." This produces a folder of PDF/DOCX files plus
   a `summary.json` for the AMS course record.
2. **Verify the export.** Open at least three PDFs to confirm content
   integrity.
3. **Move the export folder.** Copy the export folder to AMS's secure
   long-term storage (per AMS records-retention policy, this is typically
   the central AMS network drive — not the trainer's laptop).
4. **Per-participant deletion.** For each participant, call:

   ```
   POST /api/users/{user_id}/delete
   ```

   This invokes `DataDeletion.delete_user_data()` (see
   `PRIVACY_ENFORCEMENT.md` §7), which cascades through `sessions`,
   `answers`, `cv_data`, and `exports`, and additionally removes export
   files matching the `user_id` if the trainer passes an `export_dir`.
5. **Verify deletion.** The endpoint returns `True` only after re-running
   `verify_user_deleted(user_id)`. Spot-check by re-querying the dashboard
   participant list.
6. **Force-sweep stale sessions.** Run the admin endpoint with a small
   threshold to clear anything left behind:

   ```
   POST /api/interview/admin/cleanup-sessions?days_old=1
   ```

7. **Rotate the trainer API key.** Generate a new `AMS_TRAINER_API_KEY`
   for the next cohort and update the launcher.

After step 7, the trainer laptop holds no personal data from the
completed cohort. The maintainer's compliance position (no data ever
received — see `DPA_TEMPLATE.md`) is unchanged.

---

## 8. Manual / per-user deletion

Outside the end-of-course routine, two paths exist for deleting a
single participant's data:

- **Participant-initiated (Art. 17).** The participant clicks the
  "Daten löschen" button on the consent page or after viewing their
  data. The frontend calls the deletion endpoint; the backend invokes
  `DataDeletion.delete_user_data(user_id)`. Irreversible — see
  `PRIVACY_ENFORCEMENT.md` §7.
- **Trainer-initiated.** The trainer deletes a participant row from the
  dashboard. Same underlying call.

Both paths write an audit-level WARNING log entry (filtered by
`PrivacyFilter`) recording that a deletion occurred — without revealing
who the participant was.

---

## 9. What this policy does **not** cover

- **Backups.** AMS JobAssist does not create backups. If AMS IT
  configures a system-level backup of the trainer laptop, that backup
  may contain `ams_jobassist.db` and the export folder. AMS IT must
  ensure those backups are governed by their own retention policy and
  the participant's Art. 17 erasure request propagates to them.
- **Exported files copied off the laptop.** Once a trainer or
  participant has emailed a PDF or saved it to a USB stick, AMS
  JobAssist has no further control. AMS organisational policy must
  cover that downstream lifecycle.
- **Logs printed to a terminal.** The application does not write log
  files to disk by default. If AMS IT redirects the process output to a
  file, the `PrivacyFilter` still applies, but the file is then subject
  to AMS IT's own log-retention rules.

---

**File**: `AMS-JobAssist/docs/RETENTION_POLICY.md`
**Related**:
- `AMS-JobAssist/PRIVACY_ENFORCEMENT.md` §10 — retention loop in detail
- `AMS-JobAssist/docs/DPIA.md` §5 — data minimisation
- `AMS-JobAssist/docs/DPA_TEMPLATE.md` § Pflichten der AMS — controller obligations
