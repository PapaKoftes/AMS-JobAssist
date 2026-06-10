# AMS JobAssist — Review Guide for Marko

Thanks for taking the time to look at this! This guide gets you up and running in ~5 minutes and tells you exactly what to look at and what kind of feedback is most useful.

---

## What this is (2 sentences)

A participant in an AMS retraining course sits down, answers questions in their own language (Turkish, Arabic, German — 12 supported), and walks away with a polished German CV in PDF/DOCX/Europass format. A trainer watches progress in a separate dashboard, can edit inline, bulk-approve, and export everyone's CVs with one click — all offline, no data leaves the machine.

---

## Install (one double-click, no internet, no admin)

**Just run the installer:**

```
AMS-JobAssist-Setup.exe      (or: install.bat, if you got the folder version)
```

That's it. It installs both tools, the **bundled local AI model (3B, ~1.9 GB, already included)**, and a desktop + Start-menu shortcut — to a per-user folder, **no admin rights needed**. Nothing is downloaded; the whole thing runs **fully offline**. After install, launch **"AMS JobAssist"** from the desktop and your browser opens automatically.

- **http://localhost:8000** — participant CV maker (Tool 1)
- **http://localhost:8001** — trainer dashboard (Tool 2)

(If those ports are busy, the launcher picks the next free ones and prints them in its window.)

> **The AI is real and built in.** It runs the Qwen 3B model *locally, in-process* — no Ollama, no setup, no account, nothing leaves the machine. The launcher pre-loads it so your first answer isn't slow.

**Developer option (run from source, needs Python 3.10+):**

```bash
git clone https://github.com/PapaKoftes/AMS-JobAssist
cd AMS-JobAssist
pip install -e shared/ -e tool-1-cv-maker -e tool-2-trainer-dashboard
python launcher.py
```

---

## What to try (in order)

### 1 · The participant flow (~10 min)

Open **http://localhost:8000**.

1. Change the language — click any flag on the welcome screen. Every label updates immediately, including right-to-left layout for Arabic.
2. Tick the consent checkbox, pick **"Berufswechsel"** (career switch), enter a name, click Start.
3. You land in a **split screen**: top = your CV (empty at first), bottom = a chat with the AMS assistant. It says **"Erzählen Sie mir alles über sich."**
4. **Just dump everything** in one go — any language, rough is fine. Try:
   > *"Ich bin Maria Horvat aus Wien, +43 660 1234567, maria@example.com. Fünf Jahre Bäckerei: Brot gebacken, Kasse geführt, Kunden beraten. Pflichtschulabschluss, Staplerschein. Pünktlich, spreche Deutsch und Bosnisch. Suche Bürokauffrau oder Verkauf."*
5. Watch the **AI structure it onto the CV above** — name, contact, target job, experience, education, skills all sort themselves into the right sections. Then the assistant asks about whatever's missing. Add more, or click **"✓ Lebenslauf erstellen"**.
6. On the completion screen: quality score, PDF/DOCX/Europass download, ATS job-match, cover letter, and the **AI chat coach** (ask it "Ist mein Lebenslauf gut genug?").
7. Download the PDF and open it.

> The launcher pre-loads the AI model at startup, so the first answer comes back in a few seconds (~10–15 s on a normal office PC), not the half-minute it used to take cold.

### 2 · The trainer flow (~5 min)

Open **http://localhost:8001** in a second tab.

1. Your participant from step 1 should appear in the list — by their **real name** (not an ID).
2. Click the row — side-by-side compare shows raw answers vs. polished CV.
3. Click any section on the right side to edit it inline. Save. The green "✓ Saved" badge should appear.
4. Type a note in the trainer-notes field and click "Genehmigen" (Approve). Reopen the participant — **your note is still there** (it now persists).
5. Back on the list — try "Alle als PDF exportieren" (bulk export). A ZIP downloads.

### 3 · Quick extras worth seeing

- **ATS job match**: on the completion screen, paste a job listing from karriere.at and click Analyse.
- **Cover letter**: enter a company name + position, click generate.
- **DSGVO download**: click the 🔒 button on the completion screen — downloads a JSON of everything stored about that session.

---

## Feedback questions

Honest reactions are more useful than polished ones. Feel free to just note things as you go.

1. **First impression** — what did you think the tool did after 30 seconds on the welcome screen? Was it clear?
2. **Interview flow** — did the one-question-per-screen approach feel right, or too slow / too fast?
3. **The polished CV output** — compared to what you typed in, does the transformation feel useful? Surprising? Overcorrected?
4. **Trainer dashboard** — if you were a trainer running a class of 15 people, would this give you control? What's missing?
5. **Install experience** — did START.bat / the manual install work cleanly? Any friction?
6. **Anything that felt wrong or missing** — broken UI, confusing copy, feature you'd expect that isn't there.
7. **One thing you'd cut** — if you had to remove one feature to ship faster, what would it be?
8. **One thing you'd add before showing it to AMS** — what's the biggest gap between this and something a real trainer would trust in a classroom?

---

## Known gaps (so you don't have to discover them as bugs)

- **Cohort creation UI** is missing — you can filter by cohort and set one at import, but can't pre-create/rename cohorts through the UI yet (backend is ready).
- **Skills extraction is the weakest field** — the local AI reliably gets name, contact, target job, and work experience, but sometimes misses a skill buried in a sentence. Everything is editable in both tools, so it's a polish gap, not a blocker. (Measured: see `tool-1-cv-maker/eval/RESULTS.md`.)
- **Data-retention auto-cleanup** in the trainer dashboard isn't wired yet — old participants stay until manually removed (fine for a trial).
- **Screenshots in README are placeholders** — the actual app screenshots haven't been captured yet.
- **No code signing** — Windows SmartScreen may warn on the installer/`.exe`. Safe to click through ("More info" → "Run anyway").

---

## Sending feedback back

Whatever works for you — a reply email, a shared doc, a voice note, comments directly in this file. If you find something specific that broke, the most useful info is: what you did, what you expected, what actually happened.

Thank you!
