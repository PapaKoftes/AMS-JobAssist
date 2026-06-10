# Roadmap: ESCO skill taxonomy & MeinAMS export compatibility (P3.2)

Status: **planning only — not implemented.** This is an evidence-based plan for two
distinct, often-confused ideas. Both must respect the project's hard constraints:
offline-first, privacy-first, canonical `CVDocument`, AMS-focused, multilingual input.

---

## Why this is on the roadmap

The eval (see `tool-1-cv-maker/eval/RESULTS.md`) shows **skills is our weakest field
(F1 ≈ 0.31)** and **languages/multilingual cases are noisy** — Arabic/Russian persona
names and skill terms are where the small local model degrades. Free-text skills also
mean two participants who both "drive a forklift" produce two different strings, so the
trainer dashboard (Tool 2) can't aggregate or filter cohorts by skill.

A controlled vocabulary fixes the *representation* problem that no amount of prompt
tuning on free text will. ESCO is the obvious candidate: it is the EU-standard taxonomy,
it is free, and — critically for us — it ships in **28 languages including Arabic and
Ukrainian**, the exact languages our extraction struggles with.

---

## Part A — ESCO skill/occupation taxonomy

### What ESCO is (verified facts)
- **Current version: ESCO v1.2.0** (released May 2024; v1.2.1 refines the skills
  hierarchy into four sub-classifications).
- **3,039 occupations** and **13,939 skills/competences**, each with a stable URI,
  preferred + alternative labels, and a description.
- Mapped to **ISCO-08** occupation codes (the international standard AMS already aligns to).
- Translated into **28 languages** — all official EU languages plus Icelandic, Norwegian,
  **Ukrainian, and Arabic**.
- Distributed **free** as a static download (RDF/Turtle and CSV) *and* via a live REST API.

### The offline-first decision
**Use the static CSV download, bundled as a curated local dataset. Do NOT call the ESCO
API at runtime.** The live API would violate offline-first and leak the participant's
skills to an EU server — a privacy regression. The full dataset is large (~14k skills ×
28 languages), so we ship a **curated AMS-relevant subset**, the same pattern as today's
`data/knowledge/berufe.json` (~25 jobs). ESCO is the standardized replacement/extension
for that hand-built file.

### Phased plan

**Phase 0 — Spike & subset (1–2 days, low risk)**
- Download ESCO v1.2.0 CSV. Filter to occupations/skills relevant to AMS clientele
  (entry-level trades, care, retail, gastronomy, cleaning, warehouse, driving — the
  categories already in `berufe.json` and the gold dataset).
- Produce `data/knowledge/esco_subset.json`: `{skill_uri, isco, labels{de,en,tr,ar,uk,ru…},
  alt_labels[], broader[]}`. Target a few hundred skills, not 14k — keep the bundle small.
- Deliverable: a static file + a loader, no behaviour change yet. Reversible.

**Phase 1 — Skill normalization at extraction (the actual quality lever)**
- After the LLM/regex produces a free-text skill, **map it to the nearest ESCO label**
  via the multilingual alt-labels (offline fuzzy match — reuse `metrics.keyword_in`'s
  difflib approach, extended with the ESCO alt-label index).
- Store BOTH on the canonical schema: the raw user phrase **and** the matched
  `esco_uri` + canonical label. Never discard the participant's own words.
- **Measure on the gold set before/after.** Hypothesis: multilingual alt-labels lift
  skills recall on tr/ar/ru cases (the current weak spots). If the eval doesn't show a
  gain, we ship the data but not the auto-mapping — same discipline as the two-pass
  decision. *This is the one phase with a quality claim, so it is gated on the eval.*

**Phase 2 — Cohort analytics in Tool 2 (trainer value)**
- With skills carrying stable URIs, the trainer dashboard can aggregate: "12 of 20
  participants have ESCO 'food preparation' skills" → targeted course planning.
- Pure read-side; no change to Tool 1's participant flow.

### Canonical schema impact
`Skill` (or the skills list entry) gains optional `esco_uri: str = ""` and
`esco_label: str = ""`. **Both optional, defaulted empty** — existing CVs and the
cross-tool contract stay valid (same additive pattern as `target_job`).

### Risks / honest non-goals
- **Bundle size:** the full taxonomy is too big to ship; a subset is mandatory, and a
  subset means coverage gaps. Log what's dropped (no silent truncation).
- **Mapping errors:** auto-mapping a wrong ESCO code is worse than free text. Phase 1 is
  gated on eval evidence and always keeps the raw phrase.
- **Not** an ATS keyword engine. ESCO here is for *standardization and multilingual
  normalization*, not for gaming applicant-tracking systems (which are cargo-cult for
  AMS clientele — see the audit).

---

## Part B — MeinAMS export compatibility

### What MeinAMS is (and what it is not, for us)
- **MeinAMS** is the AMS Austria participant portal that is **replacing the eAMS-Konto**
  (transition through 2025/26). Participants log in to manage their job-seeking,
  appointments, and documents.
- There is **no public third-party/partner API** for an offline desktop tool to push CVs
  into a participant's MeinAMS account, and even if there were, calling it would violate
  offline-first and require handling the participant's AMS credentials — which this tool
  must **never** do.

### Therefore: this is export *compatibility*, not *integration*
The realistic, in-scope goal is: **produce files the participant can themselves upload to
MeinAMS**, in the formats it accepts. The participant stays in control; we never touch
their account or credentials.

### Phased plan

**Phase 0 — Verify accepted formats (research, blocking)**
- Confirm what MeinAMS document upload accepts (almost certainly **PDF**, possibly DOCX
  and a size cap). We already export both — so this may be **zero code**, just a
  documented confirmation in the trainer guide. *Verify before building anything.*

**Phase 1 — Export hygiene for upload**
- Ensure the exported PDF meets portal constraints (file size, PDF/A if required,
  filename conventions). Add a one-line "ready to upload to MeinAMS" hint in the UI after
  export. Low effort, high participant clarity.

**Phase 2 — (Speculative, only if a partner channel ever opens)**
- If AMS ever publishes a partner upload spec, revisit. Until then this stays a
  documentation/format concern, **not** a network integration. No credential handling,
  ever — that's a prohibited action for this tool.

### Risks / honest non-goals
- **Do not** build anything that logs into or scrapes MeinAMS.
- **Do not** store or transmit AMS credentials. The whole value proposition is that the
  data never leaves the machine.
- Treat the eAMS→MeinAMS transition naming carefully in user-facing copy so trainers
  aren't confused during the changeover.

---

## Priority & sequencing (Impact / Risk / Effort)

| Item | Impact | Risk | Effort | Verdict |
|---|---|---|---|---|
| ESCO Phase 0 (subset file) | Medium | Low | 1–2 d | **Do first** — unblocks everything, reversible |
| ESCO Phase 1 (skill normalization) | **High** (weakest field, multilingual) | Medium | 2–4 d | Do, **gated on eval evidence** |
| ESCO Phase 2 (cohort analytics) | Medium (trainer) | Low | 2–3 d | After Phase 1 |
| MeinAMS Phase 0 (format check) | Medium | Low | hours | **Do first** — may be zero code |
| MeinAMS Phase 1 (export hygiene) | Low–Med | Low | 1 d | Quick win |
| MeinAMS Phase 2 (API) | — | — | — | **Blocked**: no public partner API exists |

**Recommended next concrete step:** ESCO Phase 0 + MeinAMS Phase 0 — both are
low-risk, reversible, and de-risk the higher-impact phases. Neither makes a quality
claim, so neither needs the eval; ESCO Phase 1 is the first step that does, and it must
prove a gain on `gold_dataset.json` before it ships (same rule that kept two-pass off).

## Sources
- [The ESCO Classification](https://esco.ec.europa.eu/en/classification)
- [ESCO download (CSV/RDF, free)](https://esco.ec.europa.eu/en/use-esco/download)
- [ESCO v1.2 release notes](https://esco.ec.europa.eu/en/about-esco/escopedia/escopedia/esco-v12)
- [ESCO ↔ ISCO mapping](https://esco.ec.europa.eu/en/about-esco/escopedia/escopedia/international-standard-classification-occupations-isco)
