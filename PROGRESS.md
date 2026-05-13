# AMS JobAssist — Progress & Milestones

**Last Updated**: 2026-05-12
**Current Phase**: AMS pilot prep (Phase 6)
**Test Suite**: 725 tests passing (683 Tool 1 + 42 Tool 2)

---

## Phase 1 — Interview Engine + 5 Paths ✅ COMPLETE

Goal: A guided interview that never freezes the user and always saves progress.

| Milestone | Status | Notes |
|-----------|--------|-------|
| SQLite database layer | ✅ Done | ACID, DSGVO-compliant, safe migrations |
| Interview engine core | ✅ Done | Session state machine, autosave, resume |
| 5 interview paths | ✅ Done | unemployed, career-switch, student, pause, other |
| Re-ask trigger | ✅ Done | < 5 word answers get gentle prompt for detail |
| Example injector | ✅ Done | Every question shows one good + one bad example |
| Quick-fill starters | ✅ Done | Pre-fill textarea, user edits before submitting |
| Conversational follow-ups | 🚧 Planned | Skeleton removed — will be built when feature is actually needed |
| Autosave + resume | ✅ Done | localStorage + server validation, banner on return |

---

## Phase 2 — Polish Layer + 14-Language Normalisation ✅ COMPLETE

Goal: Any-language input → clean German CV output, with quality signals the user can actually understand.

| Milestone | Status | Notes |
|-----------|--------|-------|
| Verb enforcement | ✅ Done | Strong action verbs surfaced/back-translated |
| Structure validation | ✅ Done | Sentence shape + punctuation scoring |
| Skill normalization | ✅ Done | "office work" → "Microsoft Office (Word, Excel, Outlook)" |
| Language detection | ✅ Done | Lingua-based detection across 12 active UI languages: de, en, bs, hr, sr, tr, pl, ro, uk, ru, ar, sk |
| Term-mapping translation | ✅ Done | Reverse map English → German, no internet/AI needed |
| Confidence flagging | ✅ Done | Low-confidence sections marked for trainer review |
| Quality scoring | ✅ Done | ⭐⭐⭐ / ⚠️ / ❌ with human-readable tip |
| Gentle re-ask UX | ✅ Done | "Can you add a detail?" not "insufficient input" |

---

## Phase 3 — UI + Trainer Dashboard ✅ COMPLETE

Goal: One question per screen for the participant; one approve-or-edit loop for the trainer.

| Milestone | Status | Notes |
|-----------|--------|-------|
| One-question-per-screen UI | ✅ Done | Vanilla JS SPA, no build step |
| Split-screen live CV | ✅ Done | Left: question. Right: CV rendering in real time |
| Progress bar | ✅ Done | "Step 3 of 8", visible motivation |
| Autosave visual feedback | ✅ Done | "Saved ✓" indicator after every answer |
| Live preview (debounced) | ✅ Done | 600ms debounce → polished version on right |
| Participant list view | ✅ Done | Status at a glance, filter by status |
| Side-by-side before/after | ✅ Done | Raw answer vs polished output, teaching tool |
| Inline editing | ✅ Done | Click → edit → save, no modals |
| Approve / lock flow | ✅ Done | Lock prevents participant overwrites |
| Bulk PDF/DOCX export | ✅ Done | Streaming ZIP of approved CVs |
| Session cleanup endpoint | ✅ Done | Trainer can purge abandoned sessions |
| Cohort filtering backend | ✅ Done | `cohort_id` column + analytics endpoint |
| **Cohort creation UI** | 🚧 Pending | Backend ready, small frontend piece left |
| **Trainer notes UI** | 🚧 Pending | Backend ready, small frontend piece left |

---

## Phase 4 — Exports + AI Features ✅ COMPLETE

Goal: Professional outputs in every format AMS asks for, plus AI helpers that gracefully degrade.

| Milestone | Status | Notes |
|-----------|--------|-------|
| PDF export | ✅ Done | Austrian Tabellarischer Lebenslauf, reportlab |
| DOCX export | ✅ Done | 2cm margins, borderless tables, edit in Word/LibreOffice |
| JSON export | ✅ Done | Canonical shape consumed by Tool 2 |
| Europass XML export | ✅ Done | Validated against Europass schema |
| ATS keyword scoring | ✅ Done | Paste job ad → match % + missing skills |
| Cover letter generator | ✅ Done | Company + role → draft letter |
| Local LLM engine | ✅ Done | Qwen2.5-1.5B-Instruct Q4_K_M, llama-cpp-python, CPU-only |
| Ollama fallback | ✅ Done | Used automatically if local model absent and Ollama running |
| Rule-based fallback | ✅ Done | Always-works tier — core loop never breaks |
| AI chat coach | ✅ Done | Knows user's CV, answers specific questions |
| Interview prep generator | ✅ Done | 5 tailored questions from CV + target job |
| Job-match analyser | ✅ Done | ✅ matches / ⚠️ gaps / 💡 one concrete fix |
| Model status + in-app download | ✅ Done | UI shows active tier; one-click 1.1 GB pull |

---

## Phase 5 — Packaging + Hardening ✅ COMPLETE

Goal: Ship a fresh-VM-ready Windows distribution; tighten everything operationally.

| Milestone | Status | Notes |
|-----------|--------|-------|
| Relocatable PyInstaller specs | ✅ Done | `packaging/launcher.spec`, `build_tool1.spec`, `build_tool2.spec` — no hard-coded paths |
| Icon | ✅ Done | `packaging/icon.ico` generated and wired into all 3 specs |
| `build_all.bat` | ✅ Done | Single-command build of all 3 executables |
| Launcher .exe | ✅ Done | ~8 MB, opens browser + chooses Tool 1 / Tool 2 |
| Tool 1 .exe | ✅ Done | ~375 MB (includes reportlab, python-docx, llama-cpp-python wheels) |
| Tool 2 .exe | ✅ Done | ~46 MB |
| Structured logging | ✅ Done | `request_id` propagated through every log line |
| Structured error responses | ✅ Done | Both tools return `{error, code, request_id}` JSON shape |
| `ExportLog` wired in Tool 2 | ✅ Done | Audit trail for every PDF/DOCX/ZIP export |
| Offline mode default-on | ✅ Done | `network_block.py` allowlists loopback; everything else fails fast |
| Tool 2 lifespan path fix | ✅ Done | `sys.path` adjustment so frozen .exe finds bundled modules |

---

## Phase 6 — AMS Pilot Prep 🚧 IN PROGRESS

Goal: Get the artifacts and sign-offs needed to put this in front of real AMS trainers and participants.

| Milestone | Status | Notes |
|-----------|--------|-------|
| `TRAINER_DECISIONS_CHECKLIST.md` filled in | 🚧 Pending | Drafted, awaiting Marko sign-off on paths/skills/compliance |
| Fresh-VM smoke test | 🚧 Pending | Run all 3 .exe on a clean Windows VM, no Python installed |
| Full WCAG AA automated scan | 🚧 Pending | axe-core / Lighthouse — accessibility CSS layer already in place |
| Demo screenshots | 🚧 Pending | User to capture during walkthrough — 5–8 hero images for README/PITCH |
| AMS Instructor Guide final pass | 🚧 Pending | Already drafted in `docs/AMS_INSTRUCTOR_GUIDE.md`, needs trainer review |
| Marko feedback round | 🚧 Pending | Schedule classroom session once smoke test + checklist done |

---

## What Changed in May 2026 Audit

Concrete stability wins from the recent pass — everything below landed since 2026-05-01:

- **AI chat 500 fix**: defensive `getattr(cv_data, "target_job", None)` in the chat endpoint — old CVs without `target_job` no longer crash the coach.
- **Tool 2 lifespan fix**: `sys.path` adjustment in the FastAPI lifespan so the frozen .exe resolves bundled `services.cv_mapper` correctly.
- **`network_block.py` rewrite**: now an explicit loopback allowlist (`127.0.0.1`, `::1`, `localhost`). Previously the block was too narrow and offline mode silently leaked DNS. Offline now actually works.
- **Polish engine naming cleanup**: `polish_with_ollama()` → `ai_polish()` everywhere — accurate name now that the function dispatches across all three AI tiers, not just Ollama.
- **PyInstaller specs relocatable**: all 3 specs use repo-relative paths and a complete `hiddenimports` list (reportlab fonts, python-docx, llama-cpp internals, ssl certs).
- **Accessibility CSS layer**: visible focus rings, 44px touch targets, `prefers-reduced-motion`, AA contrast pass on quality badges, print stylesheet for PDF fallback.
- **Structured logging in both tools**: `request_id` UUID set in middleware, included in every log record + every error response — trainers can quote one ID and we can find the full request trace.

---

## Test Suite

**Total: 725 passing** — run from each tool's directory with `python -m pytest tests/ -q`.

| Tool | Tests | Test files |
|------|-------|-----------|
| Tool 1 (CV maker) | 683 | 22 files — interview, polish, language (×3), CV, exports (×4), AI, ATS, privacy, e2e (×2), API |
| Tool 2 (Trainer dashboard) | 42 | 2 files — `test_cv_mapper.py`, `test_integration.py` |

---

## Next Sprint Targets (unblock AMS pilot)

1. **Get Marko to sign off on `TRAINER_DECISIONS_CHECKLIST.md`** — interview paths, forbidden wording, ESCO skill subset. Blocks classroom run.
2. **Fresh-VM smoke test** — clean Windows 11 VM, no Python, run all 3 .exe end-to-end. Likely surfaces 1–2 missing hiddenimports.
3. **Cohort creation UI + trainer notes UI** — small frontend pieces, backend is ready. Needed for a 10-participant classroom.
4. **Capture demo screenshots** during the next walkthrough — README and PITCH still reference placeholders.
5. **WCAG AA scan** — run axe-core against both tools, fix any AA failures the CSS layer missed.

---

## Contacts

| Person | Role | Notes |
|--------|------|-------|
| Mina Mikail | Builder | mmatheking99@gmail.com |
| Marko | AMS Vienna trainer | Key feedback partner; pilot classroom gatekeeper |
