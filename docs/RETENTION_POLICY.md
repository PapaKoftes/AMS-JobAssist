# AMS JobAssist — Data Retention Policy

**Purpose**: State exactly what AMS JobAssist keeps, how long, by what
mechanism, and how AMS can change it.  
**Audience**: AMS trainers, AMS IT, AMS DPO.  
**Code under review**: commit `0808801` and later.  
**Last revised**: 2026-06-04 (corrected: default, mechanism, endpoint, "kept indefinitely" removed)

---

## 1. Default retention windows

| Asset | Default retention | Mechanism |
|---|---|---|
| Incomplete/abandoned sessions | **30 days** from `created_at` | Tier-1 sweep in `cleanup_old_sessions()` |
| Completed / approved / locked CVs | **365 days** from `created_at` (hard ceiling) | Tier-2 sweep in `cleanup_old_sessions()` — **no session is kept indefinitely** |
| `answers`, `cv_data`, `consent_records`, `cover_letters`, `ats_scores`, `exports` | Same lifetime as parent session | Deleted **explicitly** by `cleanup_old_sessions()` (not via FK cascade — see §2.3) |
| Exported files (PDF / DOCX / JSON on disk) | Lifetime of session | Removed by `DataDeletion.delete_user_data()` — NOT by the daily sweep |
| `ExportLog` audit table (Tool 2) | 90 days (recommended), trainer-controlled | Manual deletion via Tool 2 admin |
| Application logs (stdout/stderr) | Process lifetime only | Not persisted to disk by default |
| Local LLM weights | Indefinite | Not personal data |

The **365-day** ceiling for completed CVs was chosen to cover the AMS course
cycle (8–12 weeks) plus a reasonable trainer-review and appeal window, while
giving a finite storage-limitation guarantee. Abandoned drafts are purged sooner
(30 days) because they contain only partial PII with no completed CV value.

---

## 2. The cleanup mechanism

### 2.1 The config knob — `config.py`

`tool-1-cv-maker/src/backend/config.py` (line 27):

```python
DATA_RETENTION_DAYS = int(os.environ.get("AMS_DATA_RETENTION_DAYS", "365"))
```

A value of `0` disables automatic retention (not recommended).
Positive integer N sets the hard ceiling to N days; drafts are swept after
`min(30, N)` days.

### 2.2 The daily loop — `app.py`

```python
async def _retention_loop(engine, days):
    while True:
        deleted = engine.cleanup_old_sessions(days)
        await asyncio.sleep(86_400)   # 24 h
```

First sweep runs at startup; thereafter every 24 hours.

### 2.3 The actual delete — `interview/engine.py`

`cleanup_old_sessions()` uses a **two-tier purge with explicit child deletes**.

**Why explicit, not FK cascade:** SQLite's `PRAGMA foreign_keys` is
per-connection and is OFF by default on worker threads. Relying on
`ON DELETE CASCADE` from a worker thread silently orphans child PII
rows — a genuine Art. 17/5(1)(e) gap. The function therefore deletes
`answers`, `cv_data`, `consent_records`, `cover_letters`, `ats_scores`,
and `exports` explicitly before removing the parent `sessions` row,
regardless of FK state.

**Tier 1 — abandoned drafts** (purged after `draft_days_old`, default 30):

```sql
DELETE FROM sessions
WHERE created_at < datetime('now', '-30 days')
  AND (completed IS NULL OR completed = 0)
  AND (locked IS NULL OR locked = 0)
  AND (approved IS NULL OR approved = 0)
```

**Tier 2 — hard ceiling for all sessions** (purged after `days_old`, default 365):

```sql
DELETE FROM sessions
WHERE created_at < datetime('now', '-365 days')
```

This includes completed, approved, and locked sessions. No session is
kept indefinitely.

### 2.4 The admin endpoint — manual trigger

```
POST /api/interview/admin/cleanup-sessions?days_old=365&draft_days_old=30
```

Returns:
```json
{"status": "success", "data": {"deleted": 7, "days_old": 365}}
```

Safe to call repeatedly. Use this to force a sweep without waiting for
the 24-hour loop tick.

---

## 3. How to configure

```powershell
# Windows / PowerShell
$env:AMS_DATA_RETENTION_DAYS = "90"
python -m uvicorn app:app
```

Recognised values:
- `0` — disable retention (not recommended; you take on the manual deletion obligation).
- Positive integer N — hard ceiling at N days; drafts purged at min(30, N).

---

## 4. What gets KEPT (temporarily)

Sessions younger than the configured ceiling are kept while still in use.
**No session is exempt from eventual automatic deletion** — only the
ceiling differs by type (30 days for drafts, 365 for completed records).

---

## 5. What gets DELETED on retention sweep

Every 24 hours the sweep removes:

- All `sessions` rows older than the draft threshold that are not completed/approved/locked.
- All `sessions` rows older than the hard ceiling, **including** completed/approved/locked CVs.
- All child rows (`answers`, `cv_data`, `consent_records`, `cover_letters`, `ats_scores`, `exports`) for every deleted session — deleted **explicitly** to avoid FK-off orphaning.

Export files on disk (PDF/DOCX) are **not** removed by the sweep —
only database rows are. Use `DataDeletion.delete_user_data()` or the
Art. 17 erasure endpoint to remove files.

---

## 6. Recommended settings for AMS

| Deployment | `AMS_DATA_RETENTION_DAYS` |
|---|---|
| Standard AMS course (8–12 weeks) | **90** (completed CVs deleted ~3 months after creation) |
| Short workshop (1–2 weeks) | 30 |
| Shared / kiosk laptop | 1 (daily) |
| DPO test deployment | 0 (disable sweep; commit to manual deletion) |

---

## 7. What AMS must do at course end

The automatic sweep handles *everything* eventually, but for timely
post-course hygiene:

1. **Bulk export.** In Tool 2, select all participants → Bulk Export
   (PDF/DOCX/JSON ZIP).
2. **Verify the export.** Open at least three PDFs.
3. **Move the export folder** to AMS secure long-term storage.
4. **Per-participant erasure.** For each participant, invoke the
   Art. 17 endpoint:

   ```
   DELETE /api/cv/{session_id}/erase
   Headers: X-Session-Token: <token>  (or X-User-Id: <user_id>)
   ```

   This calls `DataDeletion.delete_user_data()`, which removes the user
   record, all sessions, answers, CV data, consent records, and export files.

   > ⚠️ **There is no CLI for this.** The documented
   > `python privacy/data_deletion.py --session-id …` command **does not
   > exist** (no `__main__` block in that file). Use the HTTP endpoint above.

5. **Verify deletion.** The endpoint returns `{"erased": true}` only
   after `verify_user_deleted()` confirms. Spot-check via the dashboard.
6. **Force-sweep stragglers:**

   ```
   POST /api/interview/admin/cleanup-sessions?days_old=1
   ```

7. **Rotate the trainer API key** for the next cohort.

---

## 8. Manual / per-user deletion

- **Participant-initiated (Art. 17).** Participant clicks "Meine Daten
  löschen" in the UI. Frontend calls `DELETE /api/cv/{session_id}/erase`
  with the session token; backend invokes `DataDeletion.delete_user_data()`.
- **Trainer-initiated.** Trainer can use the same endpoint with the
  participant's user_id as proof.

Both paths write an audit-level WARNING log recording the deletion event
without revealing PII.

---

## 9. Foreign-key and cascade notes (technical)

**Do not rely on `ON DELETE CASCADE` for retention sweeps.** The SQLite
`PRAGMA foreign_keys = ON` setting is applied only on the initialisation
connection; worker threads get a fresh connection with FK OFF. The
`cleanup_old_sessions()` function explicitly deletes child rows to avoid
this, and is tested with FK deliberately disabled (see
`tests/test_remediation.py::test_retention_purges_completed_records_and_children`).

`DataDeletion.delete_user_data()` also uses explicit `DELETE` statements
rather than cascade for the same reason.
