# Building an offline, multilingual CV builder for AMS course participants — what a solo developer learned in 6 weeks

*Draft case study — for Medium, dev.to, or a personal blog. ~1500 words.*

---

## The person I built this for

Maria is 47. She was a baker for 22 years until her bakery closed. Her German is functional but not professional — she mixes in Bosnian when she's tired. She's never written a CV in her life and the last time she applied for a job was 1998 with a typed résumé and a passport photo. She's now in an AMS retraining course in Vienna and her trainer has six weeks to get her job-ready.

When Maria opens karriere.at's CV builder, she sees a blank "Berufserfahrung" form with no instructions and freezes. When she opens Europass online, she hits the same wall in a different shade of blue. When her trainer suggests ChatGPT, she doesn't know what to type and is afraid of getting it wrong.

Maria is who I built AMS JobAssist for.

## The brief I gave myself

Three constraints. Non-negotiable.

1. **Offline.** Maria's classroom Wi-Fi is unreliable, the AMS DPO is conservative about data leaving Austria, and the participants are sometimes asylum-context people whose work history is sensitive. Nothing leaves the laptop.
2. **Multilingual.** AMS courses include native speakers of at least eight languages. The participant types in any language; the output is professional German.
3. **Trainer-supervisable.** Trainers don't want an AI black box. They want to see what the participant wrote, see what the polish layer produced, and edit anything they want before signing off.

Everything else is downstream of these three.

## What got built

Two FastAPI servers and a vanilla-JavaScript frontend each. No build step, no React, no SaaS dependencies.

![Architecture](https://github.com/PapaKoftes/AMS-JobAssist/raw/main/docs/img/architecture.png)

**Tool 1 (the participant interface)** runs a guided interview: one question per screen, examples and quick-fill chips below each question, live preview of the CV building up on the right. The polish layer does verb-tense enforcement, skill normalisation ("office work" → "Microsoft Office (Word, Excel, Outlook)"), structure validation, and language normalisation. A local LLM (Qwen2.5-3B-Instruct Q4_K_M GGUF, ~1.9 GB — downloaded once by the installer, then run fully offline) handles the chat coach, interview prep, and job-match analysis — but every feature degrades gracefully to rule-based logic if the model isn't loaded. The CV exports to PDF (ReportLab), DOCX (python-docx), and Europass XML.

**Tool 2 (the trainer dashboard)** imports participant exports as JSON, shows a sortable list of the whole cohort, and opens a side-by-side comparison view per participant. The trainer clicks any polished section to edit it inline; each edit is recorded in a `TrainerFeedback` audit table. Bulk approve, bulk export to a ZIP of PDFs, lock CVs from further participant edits. API-key auth, CSRF middleware, request-size limits, and an `ExportLog` table that records who downloaded whose CV and when.

The network-blocking layer is genuinely strict. It monkey-patches `socket.socket`, `socket.getaddrinfo`, `urllib.request.urlopen`, and `http.client.HTTP[S]Connection` to refuse any connect target that isn't loopback (`127.0.0.1`, `::1`, `localhost`). Set `AMS_ENFORCE_OFFLINE=0` to disable for development. Verified by a test that confirms `example.com` lookup fails while `localhost` lookup succeeds.

922 tests, all passing. 3 standalone Windows `.exe` artifacts reproducibly built from `build_all.bat`.

## Three things that worked

**Rule-based polish with LLM fallback was the right call.** I started by assuming the LLM would do the heavy lifting. Then I imagined Maria's classroom: 12 participants, one laptop each, a 1.9 GB model download blocked by the school's firewall. I rewrote the polish layer to be 100% deterministic on its own — verb maps, skill dictionaries, structure rules — with the LLM as an optional "cleaner pass" on top. The deterministic core is now what's tested, what's auditable, and what works on every machine. The LLM is what makes the chat coach feel personal when it's available.

**Loopback-allowlist offline mode beat all-or-nothing.** My first attempt blocked all sockets at the layer of `socket.socket = lambda *a, **k: raise OSError`. It worked perfectly — and killed the FastAPI server, because the server itself uses sockets to accept connections on `127.0.0.1`. The fix was a `_LoopbackOnlySocket` subclass that lets loopback through and refuses everything else. The server is happy, external network is genuinely blocked, and you can pull the Ethernet cable and watch the demo keep running.

**Tests as a forcing function.** 852 in Tool 1 alone. I write them not because I aspire to "good engineering hygiene" but because the AMS audience will not let me push a regression to a classroom. The discipline of "every bug becomes a test" caught three real edge cases in the polish engine during the last two weeks — none of which I would have noticed in manual testing because they only triggered in Turkish or Arabic input.

## Three things that surprised me

**12 languages of UI is mostly i18n plumbing, not translation.** I expected translation quality to be the hard part. The real hard part is making every label, button, placeholder, error message, ARIA description, and date format flow through one `t('key')` function that falls back gracefully when a key is missing in a non-default language. The translations themselves are LLM-assisted (which means they're plausible but unverified by native speakers — flagged as a known limitation). The infrastructure that *uses* them is 2,000 lines of careful wiring.

**Packaging is its own multi-day project.** PyInstaller is conceptually simple — point at an entrypoint, get an `.exe`. In practice: missing hidden imports, transitive deps that bloat the binary by 200 MB, spec files that reference paths relative to the wrong directory, an invalid `--buildpath` flag in my build script that worked silently for weeks. The final `.exe` is 375 MB because `llama-cpp-python` pulls in PyTorch as a transitive optional dep that I had to explicitly exclude. None of this is in any tutorial. All of it cost evenings.

**Building without a real user is the riskiest thing about a "complete" product.** I haven't watched a real AMS participant use this. I haven't sent the pitch deck to a real AMS trainer. The product is technically sound and visually polished, and I have no idea if Maria — the actual Maria, not my mental model of her — would finish the interview or quit at question 4. Every hour I spent past "minimum viable" was an hour of guessing. The most useful thing I could do this week is stop coding and start observing.

## What's next

The remaining gap is not technical. It's institutional.

The code is ready. The build is reproducible. The privacy architecture survives a DSGVO audit on paper (a draft DPIA is in the repo). The documentation set is now pitch-quality. None of this matters if AMS doesn't sign off on the five interview paths, the example wording, the skill normalisation list, the consent text, and the retention defaults. There's a `TRAINER_DECISIONS_CHECKLIST.md` in the repo with eleven items. Every one is unchecked.

My honest plan for the next six weeks:

1. **Watch one real person use it.** No coaching, no help. Record the screen. Watch where they get stuck.
2. **Cold-email three AMS trainers** with the one-page brief. Not for a meeting — just for a 5-minute reaction.
3. **Run the .exe on a clean Windows 10 VM** with no Python installed. See how long Windows Defender takes to release it. Time the cold start.
4. **Stop adding features** until I've done the first three.

Everything I learn from those four will reshape the product more than the next 100 hours of coding.

## Closing

The repo is open source under MIT at <https://github.com/PapaKoftes/AMS-JobAssist>. There's a pitch document (`PITCH.md`), a demo guide (`DEMO_GUIDE.md`), a trainer guide written in plain language (`docs/AMS_INSTRUCTOR_GUIDE.md`), and the data-protection impact assessment (`docs/DPIA.md`).

If you work at an AMS centre — in Austria, or a sister employment service in Germany, Switzerland, or anywhere with a public job-placement programme — and any of this resonates, please open an issue or fork the repo. The differentiator here isn't the technology. It's the assumption that the person typing into the box is allowed to be insecure, allowed to be multilingual, and allowed to feel like they actually did something with their working life.

The technology only matters if it gets to her.

---

*Mina Mikail · 2026 · MIT licence · maintained as a portfolio piece while seeking AMS pilot validation.*
