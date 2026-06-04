# API Endpoints (generated from OpenAPI — do not hand-edit)

> Regenerate with `python scripts/dump_openapi.py`. This is the
> authoritative route list; the prose in `API_DOCUMENTATION.md` is
> a guide that can drift.

## tool1 (45 endpoints)

| Method | Path | Summary |
|---|---|---|
| GET | `/` | Root |
| GET | `/api/admin/backup` | Admin Backup Tool1 |
| POST | `/api/ai/chat` | Ai Chat |
| POST | `/api/ai/download-cancel` | Ai Download Cancel |
| POST | `/api/ai/download-model` | Ai Download Model |
| GET | `/api/ai/download-status` | Ai Download Status |
| POST | `/api/ai/dump-extract` | Ai Dump Extract |
| GET | `/api/ai/dump-snapshot/{session_id}` | Ai Dump Snapshot |
| POST | `/api/ai/interview-coach` | Ai Interview Coach |
| POST | `/api/ai/interview-prep` | Ai Interview Prep |
| POST | `/api/ai/job-match` | Ai Job Match |
| GET | `/api/ai/knowledge/jobs` | Ai Knowledge Jobs |
| GET | `/api/ai/knowledge/search` | Ai Knowledge Search |
| GET | `/api/ai/knowledge/status` | Ai Knowledge Status |
| GET | `/api/ai/model-status` | Ai Model Status |
| GET | `/api/ai/model-tiers` | Ai Model Tiers |
| POST | `/api/ai/profile-summary` | Ai Profile Summary |
| POST | `/api/ats/score` | Ats Score |
| GET | `/api/cv/{session_id}` | Get Cv Metadata |
| DELETE | `/api/cv/{session_id}/erase` | Erase My Data |
| GET | `/api/cv/{session_id}/my-data` | Download My Data |
| POST | `/api/export/cover-letter` | Export Cover Letter |
| POST | `/api/export/docx` | Export Cv Docx |
| POST | `/api/export/europass` | Export Cv Europass |
| POST | `/api/export/json` | Export Cv Json |
| POST | `/api/export/pdf` | Export Cv Pdf |
| POST | `/api/interview/admin/cleanup-sessions` | Cleanup Sessions |
| POST | `/api/interview/ai/refresh` | Refresh Ai Detection |
| GET | `/api/interview/ai/status` | Get Ai Status |
| GET | `/api/interview/autosave-status/{session_id}` | Get Autosave Status |
| POST | `/api/interview/complete/{session_id}` | Complete Interview |
| POST | `/api/interview/follow-up` | Get Follow Up |
| GET | `/api/interview/next-question/{session_id}` | Get Next Question |
| POST | `/api/interview/preview` | Preview Answer |
| POST | `/api/interview/resume` | Resume Interview |
| POST | `/api/interview/skip-question` | Skip Question |
| POST | `/api/interview/start` | Start Interview |
| GET | `/api/interview/status/{session_id}` | Get Interview Status |
| POST | `/api/interview/submit-answer` | Submit Answer |
| GET | `/api/language-packs/available` | Get Available Languages |
| GET | `/api/language-packs/check/{language_code}` | Check Language Available |
| GET | `/api/language-packs/core` | Get Core Languages |
| GET | `/api/language-packs/info/{language_code}` | Get Language Info |
| GET | `/api/language-packs/stats` | Get Language Stats |
| GET | `/health` | Health Check |

## tool2 (14 endpoints)

| Method | Path | Summary |
|---|---|---|
| GET | `/api/admin/backup` | Admin Backup |
| POST | `/api/bulk-export` | Bulk Export |
| GET | `/api/cohorts/{cohort_id}/metrics` | Get Cohort Metrics |
| GET | `/api/export-all` | Export All Participants |
| POST | `/api/import-cvs` | Import Cvs |
| GET | `/api/participants` | List Participants |
| POST | `/api/participants/bulk-approve` | Bulk Approve |
| GET | `/api/participants/{participant_id}` | Get Participant |
| POST | `/api/participants/{participant_id}/approve` | Approve Submission |
| PATCH | `/api/participants/{participant_id}/cv-section` | Update Cv Section |
| POST | `/api/participants/{participant_id}/lock` | Lock Participant Cv |
| GET | `/api/participants/{participant_id}/status` | Get Participant Cv Status |
| POST | `/api/participants/{participant_id}/unlock` | Unlock Participant Cv |
| GET | `/health` | Health |
