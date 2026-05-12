# Tool 2 — Trainer Dashboard

**Trainer supervision tool for AMS course coordinators**

![Status](https://img.shields.io/badge/Status-In%20Development-yellow)

---

## Status

Core loop is functional: import JSON from Tool 1 → view participants → review CVs → export.

Several bugs are being actively fixed (lock persistence, approval status, cohort metrics). See [PLAN.md](../PLAN.md) for the full list.

---

## What It Does

AMS trainers use this tool to supervise participants who completed Tool 1:

- **Import participant data** — Upload JSON exports from Tool 1 (single file or ZIP)
- **Track progress** — See who has completed, who is still working, quality scores at a glance
- **Review CVs side-by-side** — Raw interview answers on the left, polished CV on the right
- **Edit inline** — Click any section, edit, save — no modal dialogs
- **Add notes** — Private trainer notes per participant (never shown to participant)
- **Approve / request changes** — Flag CVs as ready or needing revision
- **Batch export** — Download all approved CVs as a ZIP of PDFs or DOCXs
- **Cohort management** — Group participants by course, filter and report per cohort

---

## Relationship to Tool 1

```
Tool 1 (CV Maker)                    Tool 2 (Trainer Dashboard)
────────────────                     ─────────────────────────
Participant answers questions   →    Trainer imports participant JSON
CV generated offline            →    Trainer reviews before/after
JSON export                     →    Batch export all CVs as PDF/DOCX
```

Tool 2 is entirely optional. Tool 1 works completely standalone.

---

## Running (Development)

```bash
pip install -e tool-2-trainer-dashboard/
ams-trainer
# Open http://localhost:8001
```

Or without installing:
```bash
cd tool-2-trainer-dashboard/src/backend
uvicorn app:app --port 8001 --reload
```

---

## Running Tests

```bash
cd tool-2-trainer-dashboard
python -m pytest tests/ -q
```

---

## Current Structure

```
tool-2-trainer-dashboard/
├── pyproject.toml
├── frontend/
│   ├── index.html
│   ├── styles.css
│   └── js/
│       ├── app.js          Entry point, screen routing
│       ├── api.js          Fetch wrapper
│       ├── components.js   DOM builders (cards, comparison view, badges)
│       └── state.js        Client-side state
├── src/
│   └── backend/
│       ├── app.py          FastAPI app
│       ├── config.py       Settings (pydantic-settings)
│       ├── db.py           DatabaseManager
│       ├── models.py       CVSubmission, Cohort, TrainerNote, ExportLog
│       ├── api/routes.py   All REST endpoints
│       └── services/
│           └── cv_mapper.py  Normalises Tool 1 JSON (3 legacy shapes + canonical)
└── tests/
    ├── conftest.py
    ├── test_cv_mapper.py
    └── test_integration.py
```
