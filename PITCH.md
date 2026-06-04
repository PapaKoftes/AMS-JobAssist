# AMS JobAssist — One-Page Brief

*A tool built for AMS Wien classroom use, ready for pilot.*

---

## The problem you have

Every AMS course participant needs a CV. Most cannot write one alone. Trainers spend hours per participant on a task that is largely mechanical — fix verb tense, fill in dates, translate broken German, format consistently. The participants who would benefit most (lower literacy, non-native German, mid-career gaps) are also the most likely to feel ashamed of their drafts and quit.

## What AMS JobAssist is

A laptop application. Two interfaces:

- **Participant interface:** A guided 10–15 minute interview in the participant's chosen language. They answer in any language they speak. The tool produces a German PDF, DOCX, and Europass JSON. No typing of a CV from scratch.
- **Trainer interface:** A dashboard where you see every participant's progress, edit any section inline with one click, approve or request changes, and bulk-export the whole cohort.

It runs entirely on the trainer's laptop. There is no cloud, no account, no server to administer.

## Why this matters for AMS specifically

| AMS requirement | How JobAssist meets it |
|---|---|
| DSGVO compliant by default | Data never leaves the laptop. Network access blocked at the OS socket layer. Consent screen before any input. Article 20 download endpoint built in. Article 17 deletion built in. |
| Configurable retention | `AMS_DATA_RETENTION_DAYS=90` deletes incomplete sessions automatically. |
| Trainer audit | Every export and every edit is recorded with timestamp and trainer identity. |
| Multilingual cohort | 12 UI languages, 14 polish languages. Right-to-left for Arabic. |
| Accessibility | WCAG-targeted: visible focus rings, 44 px touch targets, font scaler, RTL, reduced-motion preference, high-contrast preference. |
| Offline classroom | One `.exe`. No Python on the target machine. No internet. Tested on Windows 10. |
| No vendor lock-in | MIT licensed open source. Source code in the repo. AMS can fork, modify, deploy in any centre. |

## What it costs

- Software: **€0** (MIT open-source)
- Cloud: **€0** (there is no cloud)
- Training: **~30 minutes** for a trainer to learn the dashboard
- Hardware: one laptop with Windows 10 and 4 GB RAM. Optional 2 GB extra disk for the local AI model.

## What we are asking for

**Two things.**

1. **30 minutes of one AMS instructor's time** for a guided walkthrough. We will demo a full participant flow, a full trainer flow, and the privacy/audit layer.
2. **A signed-off `TRAINER_DECISIONS_CHECKLIST`.** The code is ready; what we need from AMS is confirmation that the five interview paths match real cohort segmentation, that the example wording is appropriate, that the skill list aligns with AMS terminology, and that the consent text passes legal review.

After both items, we propose a **single-classroom pilot of 8 participants** to measure: completion rate, trainer time saved per CV, and participant satisfaction.

## What we have already delivered

- **778 automated tests** across both tools — all passing
- **3 standalone Windows .exe artifacts** in the build pipeline, reproducible from `build_all.bat`
- **12-language UI**, 14-language CV polish
- **5 interview paths** with example answers, quick-fill chips, helper tips per question
- **All export formats** working: PDF (ReportLab), DOCX (python-docx), Europass XML, JSON
- **Trainer dashboard** with side-by-side compare, inline edit with audit, bulk approve, bulk export, lock/unlock, cohort filters, API-key auth, CSRF middleware
- **DSGVO endpoints** for data portability and deletion
- **Network-layer offline enforcement** (loopback allowlist; external sockets refused)
- **Optional local AI** (Qwen2.5-1.5B GGUF) for chat coach, interview prep, and job-match — works fully offline; rule-based fallback when no model present

## What we have not yet delivered

- AMS-signed sample examples (we need real anonymised CVs from AMS to replace placeholder text)
- Pilot data from a live classroom
- A signed-off WCAG AA audit (the technical work is done; we need an external auditor to verify)

## Contacts

- **GitHub repository:** [PapaKoftes/AMS-JobAssist](https://github.com/PapaKoftes/AMS-JobAssist)
- **Demo guide:** [DEMO_GUIDE.md](DEMO_GUIDE.md)
- **For the technical IT contact at AMS:** [docs/ADMINISTRATOR_GUIDE.md](docs/ADMINISTRATOR_GUIDE.md)
- **For the trainer subject expert at AMS:** [docs/AMS_INSTRUCTOR_GUIDE.md](docs/AMS_INSTRUCTOR_GUIDE.md)
