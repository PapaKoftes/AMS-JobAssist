# AMS JobAssist — Review Guide for Marko

Thanks for taking the time to look at this! This guide gets you up and running in ~5 minutes and tells you exactly what to look at and what kind of feedback is most useful.

---

## What this is (2 sentences)

A participant in an AMS retraining course sits down, answers questions in their own language (Turkish, Arabic, German — 12 supported), and walks away with a polished German CV in PDF/DOCX/Europass format. A trainer watches progress in a separate dashboard, can edit inline, bulk-approve, and export everyone's CVs with one click — all offline, no data leaves the machine.

---

## Install (5 minutes, needs Python 3.10+)

**Option A — just double-click:**

```
START.bat
```

It detects Python, installs dependencies, tries to download the AI model (~1.1 GB, optional), and opens the browser. If the AI model download fails or you skip it, everything still works — the rule-based engine handles CV polishing without it.

**Option B — manual (if you prefer to see what's happening):**

```bash
git clone https://github.com/PapaKoftes/AMS-JobAssist
cd AMS-JobAssist
pip install -e shared/ -e tool-1-cv-maker -e tool-2-trainer-dashboard
python launcher.py
```

Then open:
- **http://localhost:8000** — participant CV maker (Tool 1)
- **http://localhost:8001** — trainer dashboard (Tool 2)

---

## What to try (in order)

### 1 · The participant flow (~10 min)

Open **http://localhost:8000**.

1. Change the language — click any flag on the welcome screen. Every label should update immediately, including RTL layout for Arabic.
2. Tick the consent checkbox, pick **"Berufswechsel"** (career switch), click Start.
3. Answer at least 3 questions. Try a deliberately rough answer like:
   > *"i worked in bakery, made bread and cake, helped customers sometimes"*
4. Watch the live CV preview on the right update as you type.
5. Finish all questions and look at the completion screen: quality score, PDF/DOCX/Europass download, ATS job-match panel, cover letter generator.
6. Download the PDF and open it.

### 2 · The trainer flow (~5 min)

Open **http://localhost:8001** in a second tab.

1. Your participant from step 1 should appear in the list.
2. Click the row — side-by-side compare shows raw answers vs. polished CV.
3. Click any section on the right side to edit it inline. Save. The green "✓ Saved" badge should appear.
4. Click "Genehmigen" (Approve) in the header.
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

- **Cohort creation UI** is missing — you can filter by cohort but can't create one through the UI yet (backend is ready).
- **Trainer notes UI** is missing — the column exists in the database but there's no text field in the UI yet.
- **AI model is optional** — if you skipped the 1.1 GB download, AI-powered features (chat coach, interview prep generator) show "Regelbasiert" (rule-based) in the UI. This is intended — the core CV polishing always works.
- **Screenshots in README are placeholders** — the actual app screenshots haven't been captured yet.
- **No code signing** — Windows SmartScreen will warn on the `.exe` files if you run those. Safe to click through.

---

## Sending feedback back

Whatever works for you — a reply email, a shared doc, a voice note, comments directly in this file. If you find something specific that broke, the most useful info is: what you did, what you expected, what actually happened.

Thank you!
