# AMS JobAssist — Product Philosophy

**This document is the north star. Every feature, every word of UI text, every design decision should be traceable back to something written here.**

---

## The Golden Rule

> You are building a confidence scaffolding tool, not a smart system.

```
If users feel: guided, safe, not judged → the tool works
If they feel: confused, exposed, overwhelmed → they quit immediately
```

Maria, sitting in an AMS course, already feels like she did not do enough, is not good enough, does not know enough. She is looking at a blank page and thinking: *"What do I even write? I haven't done anything special."*

She is wrong. This tool exists to show her she is wrong — gently, specifically, with proof.

---

## What We Are Actually Building

**Not** a CV generator. Not a form. Not an AI demo.

We are building the moment where Maria looks at her screen and thinks: *"Oh — I actually DID do stuff."*

That moment is the product. Everything else is infrastructure.

---

## On Dignity

People using this tool have not failed. They are between jobs, changing careers, returning after a gap, starting fresh. These are normal human situations.

The tool must treat them accordingly:

- **Never expose weakness.** Only show the improved output, not the raw input alongside a judgment.
- **Never use the word "insufficient."** Say "Can you add a detail?" instead.
- **Never say "weak."** Say "Let's strengthen this together."
- **Don't be cute.** Encouraging does not mean condescending. Adults can handle clear language.
- **Don't over-explain.** One clear sentence is more respectful than three cautious ones.

Maria is not broken. She just needs a scaffold.

---

## On Personality

The AI structures. It does not replace.

Maria writes: *"i was doing the filing and helping customers and sometimes i did the till too"*

The tool should surface: organized document management, customer service, cash handling.

The tool should NOT invent: "Led cross-functional customer engagement initiatives and optimized filing workflows."

We use buzzwords only when they match real skills. We never invent skills Maria does not have. We never strip her voice and replace it with corporate template language.

Her original words are preserved for the trainer — they are the real thing. The structured version is the bridge to the format the world uses. Both are true. Both matter.

---

## On Language

Maria might write in Turkish, Arabic, Bosnian, or broken German mixed with something else. She should not have to apologize for that.

The tool:
- Accepts answers in any language without judgment
- Processes silently into professional German
- Never exposes the raw input to Maria as a contrast against "correct" language
- Never asks her to rewrite in German

Language is a tool, not a measure of worth.

---

## On AI's Role

The AI is an enhancer, not a gatekeeper. It runs entirely offline — bundled with the app, no internet, no account, no subscription.

- If the model isn't loaded → the interview still works
- If the model isn't loaded → the CV still exports
- If the model isn't loaded → Maria still leaves with something real

AI is used to: surface buried skills, rewrite broken multi-language text into professional German, gently probe for more detail, and help Maria understand how she compares to a real job posting.

AI is never used to: invent experience, exaggerate skills, or replace what the user actually said.

### The Model

We use **Qwen2.5-1.5B-Instruct** (Q4 quantized, ~1.1 GB), chosen because it was trained natively on German, Turkish, Arabic, and Bosnian — not translated from English. A participant who writes in Turkish gets a coherent German sentence back, not a literal translation of Turkish structure.

It runs on a basic Windows laptop CPU. No GPU. No cloud.

### The Coach

Beyond polishing CV text, the AI acts as a chat coach that knows Maria's CV:

- **During the interview**: she can ask "is this good enough?" and get a specific answer about what she actually wrote, not generic advice
- **At the end**: she can ask for likely interview questions based on her finished CV
- **Job matching**: paste a job ad → the model tells her what matches, what's missing, and one concrete thing to fix

### Future: AMS Job Service Integration

The job matching feature is designed with a clear future step in mind: instead of pasting a job ad manually, the system should connect to the AMS job listings — note the **eAMS-Konto was replaced by *MeinAMS* (2025/26)**, so the integration target is MeinAMS / the eJob-Room (via AMS Open Data where available). The coach would then be able to pull live job postings that match the participant's target job, run the same analysis automatically, and show Maria real opportunities she's already close to qualifying for. (This is a documented *future* step — today job-match is manual paste only.)

This turns the tool from "here's your CV" into "here's your CV and here are three jobs you should apply for today."

See `ai/local_llm.py` — the `match_job_description()` function is the interface point for this integration.

---

## On the Interview

The interview should feel like a good conversation with a helpful person, not a form to fill out or a test to pass.

Principles:
- One question at a time. Not two.
- Every question shows a concrete example. Not an abstract one.
- Quick-fill buttons start the sentence. Maria finishes it.
- If an answer is vague, the system asks a follow-up — once, gently. Not three times.
- The system moves on. Maria's pace is respected.
- Progress is always visible. "Step 4 of 9" keeps her moving.

The first two questions must be easy wins: name, location. Build momentum before asking anything hard.

---

## On the Trainer's Role

The trainer is not a corrector. They are a teacher.

The before/after view exists so the trainer can sit next to a participant and say: *"Look — here's what you wrote, and here's how the tool presented it. Can you see why this word is stronger?"*

That is a teaching moment. That is worth more than any generated text.

The tool saves the trainer from the basics — structure, format, verb choice — so the trainer can focus on coaching. Not replacing coaching. Enabling it.

---

## On Scope

We build what serves Maria and her trainer. If a feature does not serve one of them directly, it does not ship.

Phase 1 is: complete interview → polished CV → trainer review → export. That loop must work perfectly, offline, every time, before anything else is added.

Scope creep is the enemy of a tool that actually gets used.

---

## Open Source

This tool is MIT licensed because AMS centers across Austria and beyond should be able to take it, adapt it, translate it, and use it without asking anyone's permission.

The code is modular so that:
- A translator can add a new language in one file
- A developer can add a new interview path without touching unrelated code
- An AMS center can fork and customize without breaking anything

We write clear code, not clever code. Someone who did not write this should be able to read it.

---

## What Success Looks Like

A nervous person completes the interview in 30-60 minutes.

They see their rough answers transformed into a professional CV.

They think: *"Oh — I actually DID do stuff."*

The trainer reviews it in 5 minutes.

The PDF prints cleanly.

The trainer shows the class the before/after and says: *"See how we improved this?"*

That is the whole product. That is what we are building.
