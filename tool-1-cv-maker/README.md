# Tool 1 — CV Maker

**Standalone professional CV tool for AMS training participants and job seekers**

![Status](https://img.shields.io/badge/Status-Complete-brightgreen)
![Tests](https://img.shields.io/badge/Tests-730%20passing-brightgreen)
![Languages](https://img.shields.io/badge/Languages-14-blue)
![Offline](https://img.shields.io/badge/Runs-100%25%20Offline-orange)

---

## What It Does

A confidence scaffolding tool. It guides you through a short interview, then turns your rough answers into a professional CV — in German, English, or your own language — without ever connecting to the internet.

**The core promise**: you don't need to know how to write a CV. Just answer the questions.

---

## Who It's For

- Job seekers starting from scratch
- People returning after a career break
- Students and recent graduates
- Career changers
- Anyone who freezes in front of a blank page

---

## How to Run (Development)

```bash
# Install as editable package (sets up imports, no path hacks)
pip install -e tool-1-cv-maker/

# Start the server
ams-cv-maker

# Or, without installing:
cd tool-1-cv-maker/src/backend
uvicorn app:app --port 8000 --reload
```

Open `http://localhost:8000` in your browser.

---

## How to Run Tests

```bash
cd tool-1-cv-maker
python -m pytest tests/ -q
# Expected: 730 passed
```

---

## Interview Paths

| Path | Situation |
|------|-----------|
| `unemployed` | Looking for work or re-entering the workforce |
| `career-switch` | Changing fields or industries |
| `student` | Studying or about to graduate |
| `pause` | Returning after time away from work |
| `other` | Anything that doesn't fit the above |

Each path has a dedicated question set with good/bad examples built in.

---

## Language Support

Answers can be written in any of 14 languages:

| Code | Language | Code | Language |
|------|----------|------|----------|
| `de` | German | `pl` | Polish |
| `en` | English | `ro` | Romanian |
| `tr` | Turkish | `sk` | Slovak |
| `sr` | Serbian | `cs` | Czech |
| `bs` | Bosnian | `hu` | Hungarian |
| `hr` | Croatian | `fa` | Farsi |
| `ar` | Arabic | `ru` | Russian |

The system detects the input language automatically using a rule-based classifier (no AI, no internet). It then **normalises** the text to German and English using term-mapping and verb-enforcement — not machine translation. The output is clean, professional German; not a "live translation" from every input language.

---

## Features

| Feature | Status |
|---------|--------|
| Guided interview (5 paths) | ✅ |
| Examples for every question | ✅ |
| Auto-save + resume (localStorage + SQLite) | ✅ |
| Live split preview (raw → improved) | ✅ |
| 14-language detection and normalisation | ✅ |
| Quality scoring with human-readable feedback | ✅ |
| PDF export (reportlab) | ✅ |
| DOCX export (python-docx) | ✅ |
| Europass XML export | ✅ |
| JSON export (for Tool 2 import) | ✅ |
| Before/after review panel (for trainers) | ✅ |
| Inline export feedback (no alert()) | ✅ |
| Data loss guard on "Start Over" | ✅ |
| Privacy — all data stays on machine | ✅ |
| ATS keyword scoring (rule-based, offline) | ✅ |
| Cover letter generator (template-based) | ✅ |
| AI chat coach (knows your CV, fully offline) | ✅ |
| AI interview prep generator | ✅ |
| AI job match analyser | ✅ |
| Windows .exe packaging | 🔜 Pending |

---

## Output Formats

| Format | File | Use |
|--------|------|-----|
| PDF | `cv_<name>.pdf` | Print or send to employers |
| DOCX | `cv_<name>.docx` | Edit in Word |
| JSON | `cv_<name>.json` | Import into Tool 2 (Trainer Dashboard) |

All exports are in German by default. English export is available via the `language` parameter.

---

## API at a Glance

The backend is a FastAPI server (`app.py`). All endpoints are under `/api/`:

```
POST /api/interview/start              Start session, receive first question
GET  /api/interview/next-question/:id  Next question
POST /api/interview/submit-answer      Submit + get polished preview
POST /api/interview/skip-question      Skip current question
POST /api/interview/resume             Resume from saved session
GET  /api/interview/status/:id         Session progress
POST /api/interview/preview            Live preview (no save, debounced)
POST /api/interview/complete/:id       Finalize → build + persist CVData
GET  /api/cv/:id                       Retrieve CVData
POST /api/export/pdf                   Download PDF
POST /api/export/docx                  Download DOCX
POST /api/export/json                  Download JSON
```

Full documentation: [API_DOCUMENTATION.md](../API_DOCUMENTATION.md)

---

## Project Structure

```
tool-1-cv-maker/
├── requirements.txt
├── src/
│   ├── backend/
│   │   ├── app.py                   FastAPI app + lifespan
│   │   ├── db.py                    SQLite wrapper (ACID)
│   │   ├── schema.sql               Database DDL
│   │   ├── config.py                Paths, defaults
│   │   ├── api/interview.py         All REST endpoints
│   │   ├── interview/
│   │   │   ├── engine.py            State machine
│   │   │   ├── paths.py             Question definitions
│   │   │   └── autosave.py          Transaction-safe saves
│   │   ├── polish/
│   │   │   ├── engine.py            Verb enforcement, scoring
│   │   │   ├── language.py          14-language normaliser (rule-based)
│   │   │   └── ats.py               ATS keyword scoring (offline)
│   │   ├── cv/
│   │   │   ├── models.py            CVData / CVSection
│   │   │   ├── builder.py           Assembles CV from session
│   │   │   ├── storage.py           Persists CVData to DB
│   │   │   └── cover_letter.py      Template-based cover letter generator
│   │   └── export/
│   │       ├── pdf_export.py
│   │       ├── docx_export.py
│   │       └── json_export.py
│   └── frontend/
│       ├── index.html
│       ├── styles.css
│       └── app.js
└── tests/                           852 tests
    ├── conftest.py
    ├── test_interview_engine.py
    ├── test_autosave.py
    ├── test_polish.py
    ├── test_language.py
    ├── test_language_14core.py
    ├── test_language_translation.py
    ├── test_polish_multilingual.py
    ├── test_cv_builder.py
    ├── test_cv_storage.py
    ├── test_pdf_export.py
    ├── test_docx_export.py
    ├── test_json_export.py
    ├── test_export_14languages.py
    ├── test_e2e_multilingual_flow.py
    ├── test_api.py
    ├── test_interview_multilingual.py
    ├── test_privacy.py
    └── test_db.py
```

---

## Privacy

Everything runs locally. The network block in `privacy/network_block.py` patches Python's `socket` module to reject all non-localhost connections. This runs automatically when `PRIVACY_MODE = True` (default).

No data is ever sent outside the machine.
