# Contributing to AMS JobAssist

AMS JobAssist is MIT licensed and built for employment training centers worldwide. Contributions that serve that mission are welcome.

---

## Before You Start

Read in order:
1. **[PHILOSOPHY.md](PHILOSOPHY.md)** — The north star. Every change should be traceable to this.
2. **[README.md](README.md)** — What this tool does and where it is now
3. **[ARCHITECTURE.md](ARCHITECTURE.md)** — Module structure and data flow
4. **[PROGRESS.md](PROGRESS.md)** — What's done, what's next, what's broken

---

## The One Rule

**This is a confidence scaffolding tool, not a smart system.**

```
If users feel: guided, safe, not judged → it works
If they feel: confused, exposed, overwhelmed → they quit
```

Every PR should be answerable: "How does this serve Maria?" If you can't answer that, reconsider the change.

---

## What the Codebase Looks Like

The code is intentionally modular so isolated changes don't cascade:

| What you want to change | Where to look |
|------------------------|---------------|
| Add a new interview path | `tool-1-cv-maker/src/backend/interview/paths.py` |
| Add translations for a language | `tool-1-cv-maker/src/backend/interview/translations.py` |
| Change how CVs are polished | `tool-1-cv-maker/src/backend/polish/engine.py` |
| Change AI polishing / chat coach | `tool-1-cv-maker/src/backend/ai/local_llm.py` |
| Change PDF/DOCX layout | `tool-1-cv-maker/src/backend/export/` |
| Change the interview UI | `tool-1-cv-maker/src/frontend/app.js` |
| Change the AI chat UI | `tool-1-cv-maker/src/frontend/app.js` → `AIChatManager` class |
| Add a trainer dashboard feature | `tool-2-trainer-dashboard/src/backend/api/routes.py` |
| Change the database schema | `tool-1-cv-maker/src/backend/schema.sql` + `db.py` |

---

## High-Value Contributions

### Adding a Language

1. Add language code to the `TRANSLATIONS` dict in `app.js` — all UI strings
2. Add question translations to `translations.py` — interview questions
3. Add language detection support in `polish/language.py` if needed
4. Test: run through a full interview in that language, export, verify output

### Adding an Interview Path

1. Define the path in `paths.py` — questions list with `id`, `text`, `type`, `examples`, `flags`
2. Add the path key to the pre-gate selector in the frontend
3. Add translations for the new questions in `translations.py`
4. Test: complete a full session on the new path, check export

### Improving Examples

Every question must have one good example and one bad example. If you have real CVs from your region, extract genuine examples and contribute them. Real beats invented, always.

### Accessibility

AMS participants often use basic Windows computers with default fonts and screen settings. Contributions that improve readability, keyboard navigation, or screen reader support are high priority.

---

## AI Engine

The local AI runs entirely on-device via `llama-cpp-python` (CPU-only, no GPU required). The model is **Qwen2.5-3B-Instruct (Q4_K_M, ~1.9 GB), downloaded once by the installer (SHA-256-verified) and then run fully offline**, chosen because it was natively trained on German, Turkish, Arabic, and Bosnian — languages real AMS participants write in.

Key module: `tool-1-cv-maker/src/backend/ai/local_llm.py`

Functions worth knowing:
- `polish_answer(raw_text, category, language)` — any-language input → professional German CV sentence
- `coach_chat(user_message, cv_context, language)` — context-aware coach that knows the user's actual CV
- `generate_interview_prep(cv_summary, target_job)` — 5 tailored interview questions
- `match_job_description(cv_summary, job_text)` — ✅ matches / ⚠️ gaps / 💡 one concrete fix

The `match_job_description()` function is also the **integration point for a planned AMS eAMS-Konto API connection** — instead of users pasting a job ad manually, the system should eventually pull live job postings directly from the AMS Open Data or eAMS API. See [PHILOSOPHY.md](PHILOSOPHY.md) for the full rationale.

AI always degrades gracefully: local model → Ollama (if running) → rule-based fallback. The interview, CV output, and exports must work without AI present.

---

## What Not to Build

- Cloud features — the system is offline-first by design. Network is blocked at runtime for privacy.
- Mobile apps — AMS participants use Windows desktops and laptops.
- Features that require internet — no participant should lose access because of connectivity.
- AI that gatekeeps — if the model is not loaded, every core feature must still work.
- "Smart" suggestions that weren't requested — don't invent skills Maria doesn't have.

---

## Code Style

- **Python**: Black formatter, ruff linter. Run both before committing.
- **Frontend**: Vanilla JavaScript. No frameworks. The people maintaining this long-term may not know React.
- **Comments**: Only write a comment when the *why* is non-obvious — a hidden constraint, a workaround, a subtle invariant. Not what the code does.
- **Variable names**: Clear enough to read without explanation. `session_language` not `sl`.
- **Tests**: If you add a new API endpoint or path, add a test. The test suite runs in CI.

---

## For AMS Centers Customizing This

1. Fork the repo
2. Fill out [docs/TRAINER_DECISIONS_CHECKLIST.md](docs/TRAINER_DECISIONS_CHECKLIST.md) with your center's specifics
3. Edit example answers in `paths.py` to match your region's real CVs
4. Adjust the skill normalization dictionary in `polish/engine.py` for local job market terms
5. Test a full cohort before rolling out
6. Open issues for anything broken or missing

You don't need to ask permission. That's what MIT means.

---

## Pull Request Checklist

- [ ] Tested full interview → export flow with the change applied
- [ ] Tested with AI model absent (core loop must still work — rule-based fallback)
- [ ] No new external dependencies added without discussion
- [ ] UI text follows the tone in [PHILOSOPHY.md](PHILOSOPHY.md) — encouraging, not condescending
- [ ] If changing interview questions: examples updated too
- [ ] If changing export format: verified PDF and DOCX output both render correctly
- [ ] If changing AI features: verified graceful degradation when model not loaded

---

## Questions

- **For users**: [docs/AMS_INSTRUCTOR_GUIDE.md](docs/AMS_INSTRUCTOR_GUIDE.md)
- **For developers**: [ARCHITECTURE.md](ARCHITECTURE.md)
- **For customization**: [docs/TRAINER_DECISIONS_CHECKLIST.md](docs/TRAINER_DECISIONS_CHECKLIST.md)
- **Issues and discussion**: GitHub Issues on this repo

---

Thank you for building tools that help people feel confident about their careers.
