# Demo Guide

A step-by-step script for running AMS JobAssist end-to-end so you can test it yourself, capture screenshots, or present to AMS staff.

Estimated demo time: **15 minutes** (or 25 minutes with full trainer flow).

---

## 0 · Setup (one-time, ~3 minutes)

You need Python 3.10+ on PATH.

```bash
git clone https://github.com/PapaKoftes/AMS-JobAssist
cd AMS-JobAssist
pip install -r requirements.txt
```

That installs Tool 1, Tool 2, the shared schema package, dev dependencies, and PyInstaller in one shot.

> **AI model:** the Qwen2.5-3B-Instruct GGUF model (Q4_K_M, ~1.9 GB) is downloaded once by the installer (SHA-256-verified) and then runs fully offline — nothing is downloaded at runtime after that one-time install fetch. For a from-source dev run it lives at `tool-1-cv-maker/data/models/qwen2.5-3b-instruct-q4_k_m.gguf`. If the model is missing, every AI feature falls back to rule-based logic — the tool keeps working, just without LLM-quality output.

---

## 1 · Start the system (~10 seconds)

```bash
python launcher.py
```

Expected console output:

```
[>>] Starting Tool 1...
[>>] Starting Tool 2...
[OK] Tool 1 bereit: http://localhost:8000
[OK] Trainer-Dashboard bereit: http://localhost:8001
[>>] Öffne Browser...
```

The browser opens on Tool 1 automatically. Tool 2 you open manually when needed.

📸 **Screenshot 1** — `01_launcher.png`: the console window with both green "[OK]" lines.

---

## 2 · Participant flow (~10 minutes — the heart of the demo)

### 2.1 — Welcome screen

What to point out:
- **Trust block**: "Wir verwandeln Ihre Antworten automatisch in einen professionellen Lebenslauf" — sets expectations.
- **Language selector first**: a participant who doesn't read German can still use the tool. Click any flag and watch every label on the page change live.
- **5 paths with icons**: not corporate categories — relatable phrasing ("Berufliche Pause" not "Career interruption").
- **Consent checkbox**: the "Create my CV" button stays disabled until ticked — DSGVO is enforced in UX, not just policy.

📸 **Screenshot 2** — `02_welcome.png`: full welcome screen with language selector and path cards visible.

### 2.2 — Interview

Pick **"Berufswechsel"** for the demo (shows the most varied questions). Type a deliberately rough first answer, e.g.:

> *"i worked in bakery, made bread and cake, helped customers sometimes"*

Things to point out:
- **One question per screen** — no overwhelm.
- **Good and bad example** chips below the question — concrete, not abstract.
- **Quick-fill chips** — single tap inserts a sentence starter.
- **Word counter + quality indicator** — non-judgmental: "Etwas kurz — fügen Sie noch ein Detail hinzu".
- **Live preview pane** on the right shows the CV building as you answer.
- **Save status** in the top bar: "Wird gespeichert…" → "Gespeichert ✓".
- **Skip is allowed** — explicit, no shame.

📸 **Screenshot 3** — `03_interview.png`: an interview question with the live preview visible on the right.

📸 **Screenshot 4** — `04_polish_before_after.png`: the live preview showing the raw answer on the left and the polished version on the right.

### 2.3 — Completion

After the last question:
- **Quality summary** with encouraging tip text (never "your CV is bad" — always "let's add a detail").
- **Three download buttons**: PDF, DOCX, Europass JSON.
- **🎯 ATS / job-match panel**: paste a real job listing from karriere.at or AMS — see which keywords match and which are missing.
- **✉️ Cover letter generator**: enter company + position, get a personalised first-draft cover letter.
- **🔒 Meine Daten herunterladen**: DSGVO Art. 20 portability — full JSON dump of everything stored.

📸 **Screenshot 5** — `05_completion.png`: the completion screen with download buttons.

📸 **Screenshot 6** — `06_pdf.png`: open the downloaded PDF in your viewer and screenshot the first page.

📸 **Screenshot 7** — `07_ats.png`: paste a real job ad, click analyse, screenshot the keyword matrix.

---

## 3 · Trainer flow (~5 minutes)

Open **http://localhost:8001** in a second browser tab.

### 3.1 — Participant list

What to point out:
- **One row per participant**, status badge, last-updated, quality score.
- **Cohort filter, status filter, name search** in the toolbar.
- **Completion badge** (✓ Fertig / ⏳) — instant scan of who needs attention.
- **📤 Alle als PDF exportieren** — bulk export everyone with one click.

📸 **Screenshot 8** — `08_trainer_list.png`: the participant table.

### 3.2 — Detail view

Click a participant row.

What to point out:
- **Side-by-side compare**: what the participant wrote on the left, what the CV says on the right.
- **Inline edit** — click any polished section, edit in place, click Save. Green "✓ Saved" badge appears. This is what makes the trainer feel in control without modal-dialog friction.
- **Prev/next nav** — "1 von 12" with arrows — flip through the cohort like a slideshow.
- **Approve / Lock / Unlock** — controls in the header.

📸 **Screenshot 9** — `09_trainer_detail.png`: detail view with inline-edit active.

📸 **Screenshot 10** — `10_trainer_bulk.png`: select multiple participants, hit bulk approve.

---

## 4 · Privacy / DSGVO demo (~30 seconds)

Show two things to seal the trust story:

1. **Right-to-portability**: On the completion screen, click **🔒 Meine Daten herunterladen**. A JSON file downloads with every byte the tool stores about that user.

2. **Audit trail**: In the trainer dashboard, after a bulk export, run:

   ```bash
   sqlite3 tool-2-trainer-dashboard/data/ams_trainer.db "SELECT * FROM export_logs ORDER BY exported_at DESC LIMIT 5;"
   ```

   Every download is recorded with timestamp, format, and trainer identity.

3. **Offline proof** (optional but powerful): with the tool running, disable your Wi-Fi. Everything still works. (Yes, you can also `tcpdump` the loopback interface to show packets stay local.)

---

## 5 · Build the .exe (~5 minutes, one-time)

Show that the deployment story isn't speculative.

```bat
build_all.bat
```

After ~5 minutes:

```
dist/
├── AMS-JobAssist-Launcher.exe      (8 MB)
├── AMS-JobAssist-Tool1.exe         (375 MB)
└── AMS-JobAssist-Tool2.exe         (46 MB)
```

Double-click `AMS-JobAssist-Launcher.exe` and watch the same two-tool environment come up on a machine without Python or any dev tools installed.

📸 **Screenshot 11** — `11_dist.png`: file explorer view of the `dist/` folder.

---

## Talking points cheat sheet

| Question you may get | Answer |
|---|---|
| "Where does the data go?" | Stays on the trainer's laptop. SQLite file, no network. Loopback-only enforcement at the socket layer — set `AMS_ENFORCE_OFFLINE=0` to disable if you ever want to. |
| "Does it need internet?" | Only once, during install: the installer downloads the AI model (SHA-256-verified). After that it runs locally and fully offline — nothing is downloaded at runtime. |
| "How is the CV improved?" | Rule-based polish (verb enforcement, skill normalization, structure validation) plus a local Qwen LLM downloaded once during install, then run fully offline (rule-based fallback if the model is missing). Same input always produces the same output for the same engine — auditable. |
| "Can we edit the polished CV?" | Trainer edits inline, with audit trail. Lock the CV to freeze it from further participant edits. |
| "DSGVO?" | Consent screen, Article 20 download endpoint, Article 17 deletion endpoint, retention cleanup, audit log, no PII in logs (regex redaction filter). |
| "Languages?" | UI: 12 (de, en, bs, hr, sr, tr, pl, ro, uk, ru, ar, sk). Polish output: 14. Detection: automatic. |
| "Custom for our AMS centre?" | All five paths, examples, quick-fill chips, and skill list are configured in plain Python files. Adding a new path is ~30 lines. |
| "Cost?" | MIT-licensed. €0 software cost. €0 cloud cost (there is no cloud). |
| "Timeline to pilot?" | Pending a 30-minute trainer review (see `TRAINER_DECISIONS_CHECKLIST.md`). Code is ready. |

---

## Trouble-shooting

| Symptom | Cause | Fix |
|---|---|---|
| Browser shows "site can't be reached" | Tool 1 or Tool 2 didn't bind | Check `python launcher.py` console output; another process may be on port 8000/8001 (launcher auto-advances ports, check the console for the actual one) |
| AI chat says "Regelbasiert" | No GGUF model placed at expected path | Either copy the model file or accept rule-based fallback — every feature still works |
| Trainer dashboard returns 401 | `AMS_TRAINER_API_KEY` is set but request had no `X-API-Key` header | Unset the env var, or pass the key as `?api_key=…` for browser testing |
| `pip install` fails on `llama-cpp-python` | Build toolchain missing | Skip AI extras: `pip install -e tool-1-cv-maker` (without `[ai]`) |
| Build .exe fails with "module not found" | Hidden import missed | Add the module to `hiddenimports` in the relevant `packaging/*.spec` |

---

After the demo, send the AMS contact to **PITCH.md** and **docs/TRAINER_DECISIONS_CHECKLIST.md**.
