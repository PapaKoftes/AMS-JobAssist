# AMS JobAssist — quick start (for Marko)

A small offline tool that interviews a participant in plain language and turns
their answers into a finished Austrian CV (+ cover letter and a ready-to-send
application e-mail). It runs entirely on the laptop — **nothing is sent to the
internet, and no ChatGPT account is needed.**

---

## Install (5 minutes, no Python, no setup)

1. **Download** the file I sent you (`AMS-JobAssist.zip`, ~2.2 GB) and **unzip it**
   to anywhere — e.g. your Desktop. You'll get a folder with a few files in it.
2. Open the folder and **double-click `AMS-JobAssist-Launcher.exe`**.
3. Windows may show a blue **"Windows protected your PC"** box (because the app
   isn't code-signed yet). Click **"More info" → "Run anyway"**. This is normal
   for a tool that isn't from the Microsoft Store.
4. A black window opens and then your **web browser opens automatically** with the
   app. (If the browser doesn't open, go to **http://127.0.0.1:8000** yourself.)

> Keep the black window open while you use the app — closing it stops the app.
> To stop, just close the black window.

### First launch: wait for the AI
On the **first** start, the AI model takes **about 30–60 seconds** to load. Top-right
you'll see a small status:
- **"KI aktiv (Qwen2.5-3B)"** ✅ — the AI is on, you're good.
- **"Modell lädt…"** — still loading, give it up to a minute.
- **"KI nicht aktiv"** ❌ — something's wrong with the model. **Please tell me** —
  don't judge the tool on this, the output would be the weak rule-based version.

---

## What I'd love you to try

Run through it **as if you were a participant** — ideally a tricky one, because
that's where it should help most:

1. Pick a situation (e.g. *Arbeitslos*) and just **talk/type freely** about a
   work history — short notes are fine, it's meant to handle messy input.
2. Try it with a **participant who has weak German / writes in another language**
   (Bosnian, Turkish, Arabic, Russian…). It translates to German for the CV.
3. Answer the follow-up questions, then **download the PDF** at the end and look at
   the CV, the **Bewerbungs-Check** (the hire-readiness checklist), and try the
   **cover letter** and **"Bewerbungs-E-Mail"** buttons.
4. There's also a **🔊 read-aloud** button on each question (for low-literacy users)
   and a **"Passende Jobs beim AMS finden"** button.

Use anything you like for test data — **none of it leaves the laptop.**

---

## The questions I actually need your feedback on

You mentioned PPC uses a **12-question prompt** to pull CV details out of
participants. That's the heart of this — so:

1. **The interview structure**: does the tool ask the *right things*, in the right
   order, to get good CV content out of a participant? What's missing? What's
   redundant?
2. **Compared to your 12-question GPT prompt** — where is the tool better, and
   where does your prompt still win? (If you can share the 12 questions, I'll make
   the tool ask exactly those.)
3. **Output quality**: is the German CV good enough to actually send? Where does it
   need work?
4. **Would you use this in a real session?** What would have to be true for that?

No rush — have a play with it first, then we can talk.

---

## Optional: quick notes template

If it helps, jot a line per test case (copy the block as many times as you like).
Rating per field: ✅ ok · ⚠️ half-right · ❌ wrong/missing.

```
Case __
- Input language:        (de / tr / bks / ar / ru / …)
- What you typed (gist):
- Name / contact:        ✅ ⚠️ ❌
- Target job:            ✅ ⚠️ ❌
- Experience:            ✅ ⚠️ ❌
- Skills:                ✅ ⚠️ ❌
- German quality of CV:  ✅ ⚠️ ❌
- Would you send it?     yes / no — why:
- Anything confusing / broken:
```

