# Friday Demo — sit-down with Marko

A tight ~8-minute walkthrough. Everything runs **100% offline on this machine**.

---

## Before Marko arrives (do this ~3 min early)

1. Double-click **`START_DEMO.bat`** (or run `python start_demo.py`).
2. Wait for the console to print:
   ```
   ✅  READY FOR THE DEMO
   Participant (CV-Ersteller):  http://localhost:8000
   Trainer (Dashboard):         http://localhost:8001
   ```
   > It pre-loads the AI model (the slow part, ~60–90s) **now**, so during the
   > demo every AI step is fast. The browser opens automatically.
3. Leave the console window open (closing it stops the demo).

> Want a totally fresh slate? Run `python start_demo.py --reset`.

---

## Part 1 — Participant builds a CV (the "wow") · ~4 min

**Tab: http://localhost:8000**

1. **Start screen** — type a name (e.g. `Marko Test`), tick the consent box
   ("meine Daten bleiben auf diesem Gerät"), pick any path, click **Start**.
   - *Talking point:* "No account, no internet, no cloud. The consent is recorded."

2. **The dump** — paste this (or let Marko type his own, in any language):
   ```
   Ich bin Stefan Wagner, stefan.wagner@gmx.at, 0664 1234567.
   Ich suche Arbeit als Lagerleiter. Ich habe 8 Jahre als Lagerarbeiter
   bei Hofer gearbeitet, von 2015 bis 2023. Ich kann Stapler fahren,
   Lagerverwaltung und SAP. Ich habe einen Pflichtschulabschluss und
   einen Staplerschein.
   ```
   Click **Senden**.
   - Watch the AI **structure it onto the CV sheet** in real time (name,
     contact, job target, experience, skills, education).
   - *Talking point:* "It read free-form text — any language — and built a
     structured Austrian Lebenslauf. The local AI did the extraction."

3. **Answer 1–2 follow-up questions** the advisor asks (languages, strengths).
   - *Talking point:* "It fills the gaps like a supportive AMS advisor would."

4. Click **Lebenslauf erstellen** → then **export PDF** (and DOCX if you like).
   - The PDF opens — a clean Austrian tabellarischer Lebenslauf.
   - *Optional:* show the **anonymised** export (name → initials, no photo/DOB) —
     "for anti-discrimination applications."
   - *Optional:* generate the **cover letter** — note it takes ~30s because the
     AI is polishing it locally; good moment to say "this is all on-device."

---

## Part 2 — Trainer reviews & approves · ~3 min

**Tab: http://localhost:8001**

1. Back in Tool 1, click **export JSON** (or use the file just exported). In Tool 2,
   go to **Importieren**, pick that JSON, set a cohort name (e.g. `Demo-Kurs`).
2. Open the participant in **Teilnehmer** — show the **side-by-side**
   (raw answers vs. polished CV).
3. **Edit a section inline** (fix a word), save — show it persists.
4. Click **Freigeben** (approve). Show the status flip to approved.
5. *Optional:* **Bulk-Export** a ZIP of PDFs for the whole cohort.
   - *Talking point:* "The trainer reviews, corrects, approves, and exports the
     whole class — all offline, all auditable."

---

## Part 3 — The privacy story (the closer) · ~1 min

- "Everything you saw never touched the internet — the AI is a 1 GB model running
  on this laptop."
- Show the participant's **🔒 Meine Daten** button → downloads everything stored
  about them (DSGVO Art. 20), and **Daten löschen** → erases it all (Art. 17).
- *Talking point:* "Built for AMS: privacy-by-design, German output, Austrian CV
  format, works on a training-room PC with no internet."

---

## If something hiccups (be honest, it's a prototype)

| Symptom | What to say / do |
|---|---|
| First AI step is slow | The model is still warming — wait, it speeds up. (Pre-warming should prevent this.) |
| A page looks off | Refresh (Ctrl+R). State is saved after every step. |
| Cover letter slow (~30s) | Expected — the AI is writing it locally. Turn it into a talking point. |
| Want to restart clean | Ctrl+C the console, run `python start_demo.py --reset`. |

## Honest framing for Marko
This is a **working prototype**, not a shipped product. What's real and solid:
the offline AI extraction, the CV/cover-letter/exports, the trainer review flow,
and the privacy controls (consent, export, erasure — all tested). What's still
to come: a signed one-click installer, real translation of the *output* into all
12 UI languages (today the CV comes out in German/English), and a validated
Europass file. Ask him what matters most — that decides what we build next.
