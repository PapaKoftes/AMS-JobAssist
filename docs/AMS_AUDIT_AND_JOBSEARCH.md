# AMS-POV audit + AMS job-search feature design

Re-audit of the whole project from the AMS institution's and the users' (participants +
trainers) point of view, plus a concrete, Datenschutz-first design for an optional
"find matching AMS jobs" feature. Grounded in how AMS job search actually works.

---

## Part 1 — Is this useful to AMS? (honest verdict)

**Yes, but it's a starting point, not a finished value chain.**

### What AMS genuinely gets today (real, working)
- A **dignity-respecting, multilingual CV builder** for exactly AMS's clientele (migrants,
  career-changers, trades/care/retail/gastro), producing a correct **Austrian** CV
  (tabellarischer Lebenslauf + photo + signature) and an ÖNORM cover letter, in PDF/DOCX/
  Europass. Input in any of 12 languages → polished German output.
- A **trainer dashboard** that mirrors a real classroom workflow: import a cohort,
  review raw-vs-polished side by side, edit inline, add notes (now persistent), approve,
  and **bulk-export** everyone's CVs. With audit logging and per-cohort metrics.
- **Datenschutz by construction:** fully offline (loopback-only network block), local
  SQLite, DSGVO data-export + erasure endpoints, retention policy. This is genuinely
  easier to get past an AMS legal/works-council review than any cloud tool.

### The strategic gap (what an AMS trainer/institution will notice)
1. **No bridge from "CV done" to "jobs to apply for."** Today job matching is *manual*
   (the participant pastes a job ad into `ats.py` / `/api/ats/score`). For a public
   employment service whose mandate is **placement**, that's the missing half. This is
   the upgrade this doc designs.
2. **Skills are free text, not standardized.** "Staplerschein" vs "Gabelstapler" vs
   "forklift" never aggregate. This blocks trainer analytics ("12 of 20 can do food
   prep") and weakens matching. (Skills is also our weakest extracted field, ~0.20–0.31
   F1 — see `tool-1-cv-maker/eval/RESULTS.md`.) ESCO fixes this — see
   `docs/ROADMAP_ESCO_MEINAMS.md`.
3. **No outcome loop.** AMS can't yet answer "did this course improve placement?" That's
   a real deployment concern, but it's a *separate system* with its own DPA — out of scope
   here, and deliberately so (see Datenschutz risks below).

### Data we already hold (the raw material for matching) — `shared/schema/cv_schema.py`
`target_job`, `basics` (incl. location), `experience[]` (title/employer/period + detected
skills), `education[]`, `skills[]` + `all_skills[]`, `languages[]` (CEFR). Everything a
keyword-or-profile match needs is already on the machine.

---

## Part 2 — How AMS job search actually works (verified)

- The job board for seekers is **`jobs.ams.at` ("alle jobs")**, the public successor view
  of the **eJob-Room** (`jobroom.ams.or.at`). **Searchable without login** (free search).
- **There is no public read API for job listings.** AMS publishes an **HR-API**, but it is
  for *employers to push job postings into* AMS from recruiting software, and needs an
  activated eAMS account. It does **not** let a job-seeker app pull listings.
- Therefore any *in-app* listing retrieval = scraping the `jobs.ams.at` SPA's internal
  XHR endpoints. Unofficial, may break without notice, and may touch ToS. Treat as a
  maintenance liability, not a stable integration.

**Consequence:** the cleanest, most durable, most privacy-preserving way to connect a
participant to real AMS jobs is to **hand the search to the participant's own browser**,
not to fetch inside our app.

---

## Part 3 — Feature design: three tiers (pick per appetite/risk)

### ★ Tier 0 — "One click to AMS jobs" (deep-link). RECOMMENDED FIRST.
On the completion screen, a button **"Passende Jobs beim AMS suchen"** opens the
participant's **own browser** at `jobs.ams.at` pre-filled with their `target_job`
(+ location/skill). 

- **The app transmits NOTHING.** The participant's browser does the search, exactly as if
  they typed it on ams.at themselves. No app network call → **offline guarantee intact**.
- **Datenschutz:** the only thing that reaches AMS is the search term the participant chose
  — no name, no CV, no profile. A short notice is still shown for transparency (below), but
  there is no data *transmission by us* to consent to.
- **Effort:** ~1 day. **Risk:** ~none. **This is the "make it super easy" win.**
- *Build note:* confirm the exact `jobs.ams.at` query parameter by inspecting one live
  search in a browser (the SPA hides it from static fetches).

### Tier 1 — In-app matches with local ranking (consented, optional, default OFF)
Button **"Jobs finden und auf meinen Lebenslauf abstimmen"**. With explicit DSGVO consent:
the app uses `temporarily_allow_network()` (already proven for model download,
`network_block.py`) **scoped to `*.ams.at` only**, fetches a handful of current listings
for the target job + location, and **ranks them locally** against the full profile using
the existing `match_job_description()` (`local_llm.py`) / `ats.py`.

- **Privacy-preserving split:** only **non-identifying search keywords** (target job,
  location) leave the machine. The **full CV/profile never leaves** — ranking happens
  locally. Results shown as "you're a strong match for 3 of these."
- **Datenschutz: requires explicit consent + audit log + default-off** (see Part 4).
- **Effort:** 3–5 days + ongoing maintenance (SPA scraping is fragile). **Risk:** medium
  (fragility, scope-creep, ToS). **Value:** high — the real "here are jobs you match today."

### Tier 2 — Institutional integration (case-file linkage, outcome tracking). OUT OF SCOPE.
Linking CVs to AMS case files / tracking applications & hires. High value to AMS leadership
but needs an AMS institutional agreement, a separate DPA, and likely credential handling —
which this tool must **never** do. Park it; note it; don't build it here.

---

## Part 4 — Datenschutz model (for Tier 1; Tier 0 needs only a notice)

Any feature that transmits profile-derived data gets a **clear, specific, opt-in consent**,
per DSGVO Art. 6(1)(a) + Art. 7 (freely given, specific, informed, revocable):

- **Default OFF.** The feature does nothing until the participant actively clicks it.
- **Consent dialog states exactly what leaves the machine:** "Für die Jobsuche wird Ihr
  **Zielberuf** und (optional) Ihr **Wohnort** an das AMS-Jobportal gesendet. **Ihr Name,
  Ihre Kontaktdaten und Ihr Lebenslauf werden NICHT übertragen.** Die Bewertung der Jobs
  passiert lokal auf diesem Gerät. Einverstanden?" — with **Ja / Nein**, no pre-tick.
- **Minimization:** transmit only the keyword(s); never the CV, name, contact, or
  identifiers. Ranking is local.
- **Scope lock:** the network exception is hardcoded to `*.ams.at`, read-only, and closes
  immediately after the fetch (`temporarily_allow_network()` re-installs the block).
- **Auditability:** every network call logged (URL, timestamp, response size, trainer/
  session) so a DSGVO audit can verify scope. Offline-by-default remains the provable
  baseline (`verify_network_blocked()` test stays green for the normal path).
- **Revocable & transparent:** a settings toggle; the trainer guide documents the exception.

---

## Part 5 — Recommended AMS upgrades, ranked (beyond job search)

| # | Upgrade | Why AMS cares | Effort | Datenschutz |
|---|---|---|---|---|
| 1 | **Tier 0 deep-link to `jobs.ams.at`** | Bridges CV→jobs with zero privacy cost | ~1 d | Notice only |
| 2 | **ESCO skill normalization** (`ROADMAP_ESCO_MEINAMS.md` Ph.1) | Fixes weak skills field; enables matching + analytics; multilingual | 2–4 d | Local only |
| 3 | **Expand berufe knowledge base 25→~100** | Sharper job-match coaching for AMS trades/care/gastro | 2–3 d | Local only |
| 4 | **Cohort skill analytics in Tool 2** | "12 of 20 can do X" → course planning | 2–3 d | Local only |
| 5 | **Cohort bulk-delete endpoint** | Course ends → erase the whole cohort (DSGVO duty) | 1 d | Strengthens |
| 6 | **MeinAMS upload guide** (compatibility, not integration) | "Where does my CV go next?" | 0.5 d | None |
| 7 | **Tier 1 consented in-app job match** | "Here are 3 jobs you match today" | 3–5 d | Consent + audit |

---

## Recommendation

1. **Ship Tier 0 (deep-link) now** — it delivers the "super easy CV→jobs" upgrade with
   **no Datenschutz transmission and no offline breach**. Biggest value-per-risk by far.
2. **Then do ESCO skill normalization (#2)** — it's the keystone: it fixes our weakest
   field AND is the prerequisite for good matching and trainer analytics.
3. **Treat Tier 1 (in-app fetch) as an explicit, consented, default-off option** to add
   only if AMS wants it and accepts the SPA-scraping maintenance + the consent model above.
4. **Do not** build case-file linkage or credential handling (Tier 2) without an AMS
   institutional agreement and a dedicated DPA.

## Sources
- [AMS Jobsuche (alle jobs / eJob-Room)](https://www.ams.at/arbeitsuchende/arbeitslos-was-tun/jobsuche-online-und-mobil)
- [AMS eJob-Room free search (no login)](https://jobroom.ams.or.at/jobsuche/FreieSuche.jsp)
- [AMS HR-API (employer-side only)](https://www.ams.at/unternehmen/service-zur-personalsuche/ams-hr-api)
- [DSGVO Art. 7 — conditions for consent](https://datenschutz-grundverordnung.eu/dsgvo/art-7-dsgvo-bedingungen-fuer-die-einwilligung/)
