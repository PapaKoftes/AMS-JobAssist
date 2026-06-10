# Completion Plan — "Working product for Marko"

Single source of truth for finishing AMS-JobAssist into a product Marko can install
and use. Every step has a **verification gate**. Nothing is "done" until its gate passes.

Status legend: [x] done · [~] doing · [ ] todo · [-] removed (decided against)

---

## ✅ STATUS: COMPLETE — all phases A–E passed their gates

| Phase | Gate result |
|---|---|
| A — single in-process 3B engine | **macro-F1 0.742** ≥ 0.73 floor (beats Ollama-3B 0.738); single-track, Ollama opt-in. |
| B — Tool 2 trainer fixes | trainer notes reload + real name on canonical import; **53 Tool 2 tests** pass. |
| C — packaging completeness | `build_all.bat` produced `dist/`: 3 exes + installer + **3B GGUF (1.84 GB, 3B only)**; knowledge bundled; install.bat copies model beside exe. |
| D — clean-machine smoke | **smoke_test.py PASS** on the built launcher: both `/health`, bundled 3B loads in the frozen exe, offline. |
| E — end-to-end + docs | cross-tool E2E (real Tool1 export → Tool2 import → edit → notes → approve → PDF) passes; FOR_MARKO refreshed. **Full suite green: Tool1 761, Tool2 53, packaging 9.** |

Remaining hand-off item (needs a separate clean Windows VM, can't be automated here):
run the installer on a fresh machine with the network physically off and confirm the
double-click → working product flow. All logic it would exercise is already certified
above from source + on the built exes.

---

## 0. End-goal (Definition of Done)

Marko receives **one installer**, double-clicks it on a normal Windows PC (no admin,
no internet), and within ~5 minutes has:

1. A desktop/Start-menu shortcut that launches **both** tools.
2. **Tool 1 (CV maker):** a participant answers interview questions in any language →
   gets a **complete, correct Austrian CV** (identity, photo, structured work history,
   education, skills, languages, signature block) exported to **PDF and DOCX**, plus an
   ÖNORM cover letter. AI runs **locally** (3B, good quality), fully offline.
3. **Tool 2 (trainer dashboard):** Marko imports the participant's CV, sees the real
   name, reviews/edits sections, adds notes that **persist**, approves, and bulk-exports.
4. **Offline guarantee holds** — no outbound network at any point after install.
5. A **smoke test passes on a clean machine** certifying 1–4.

---

## 1. Architecture decision record (locked)

**ONE model engine: in-process GGUF via llama-cpp-python. The Ollama-bundling track is
removed.**

- *Why:* the app already loads GGUF in-process (the 1.5B proves the path). Shipping the
  **qwen2.5-3b** GGUF the same way gives the measured 0.738 quality with **no Ollama
  install, no background service, no admin, no extra 750 MB** — a true one-double-click
  offline product. Best quality-that-fits, fastest path, least regression surface.
- *Ollama:* demoted to a **dormant opt-in** (`AMS_USE_OLLAMA=1`) used only by the eval
  harness / power users. It is NOT bundled, NOT a default, NOT a product dependency.
- *7B:* remains an optional "quality mode" GGUF a user can drop in later; not shipped by
  default (40 s/answer on CPU is too slow for the live interview).

---

## 2. Contracts (must not break)

| # | Contract | Guarantee | Enforced by |
|---|---|---|---|
| C1 | **Offline-first** | No outbound network post-install; only loopback. | `network_block` enabled at startup in both tools; smoke test. |
| C2 | **Privacy-first** | Participant PII never leaves the machine; no telemetry. | C1 + no external endpoints in code. |
| C3 | **Canonical `CVDocument`** | The only cross-tool artifact. Tool 1 exports it; Tool 2 imports it. | `shared/schema/cv_schema.py`; round-trip test. |
| C4 | **Model engine = in-process GGUF** | Default AI is the bundled 3B GGUF, loaded in-process; deterministic (temp 0). | `local_llm.py`; engine-selection test. |
| C5 | **No-admin install** | Installer writes only to per-user locations; no elevation. | `install.bat` / Inno `{autopf}`+`{userappdata}`; clean-VM test. |
| C6 | **Quality floor** | Extraction macro-F1 ≥ 0.73 on the 20-case gold set (in-process 3B). | `eval/run_extraction_eval.py`; RESULTS.md. |

---

## 3. Verified ground truth (from end-to-end trace, checked against code)

**Works (do not touch):**
- Tool 1 full pipeline: interview → extraction (correctly prefers stronger engine →
  rules) → CV build (structured title/employer/period, languages) → PDF/DOCX export
  **incl. signature block** (`pdf_export.py`/`docx_export.py` — verified present) →
  ÖNORM cover letter.
- Tool 2: import (canonical+legacy), list/search/filter, detail view, inline edit
  (canonical `experience.0` keys), approve/reject, lock, bulk PDF/DOCX/JSON export.
- Offline enforcement: enabled at startup in **both** tools; loopback allowlisted.
- Cross-tool round-trip test exists (Tool1 export → Tool2 import → edit).

**Real, verified gaps (fix these):**
- **G1** Tool 2 `trainer_notes` is write-only — saved (routes.py:608/790) but never
  returned in `ParticipantResponse` → trainer can't reload notes.
- **G2** Canonical import reads top-level `cv_dict.get("name")`/`("email")`
  (routes.py:1420-1421) which don't exist in canonical (`basics.full_name`/`basics.email`)
  → trainer sees `user_id` instead of the real name.
- **G3** `local_llm.get_status()` reports `local_model_available=True` whenever *any*
  engine is ready → `/api/ai/model-status` mislabels the active engine. Cosmetic but
  confusing; simplify with the single-engine model.
- **G4** Knowledge base `berufe.json` not bundled into the frozen build (spec datas omit
  `data/knowledge`) → degraded prompts in the .exe.
- **G5** Only the 1.5B GGUF is on disk; **3B GGUF must be produced** and made the default.
- **G6** Installer messaging says "AI not bundled / rules-only"; must reflect bundled 3B.
- **G7** No automated smoke test runs against the *built exe* on a clean layout.

**Deferred (not needed for Marko's trial; logged, not done):**
- Cohort-creation UI, data-retention job in Tool 2, settings server-persistence,
  print stylesheet, ESCO/MeinAMS (see `docs/ROADMAP_ESCO_MEINAMS.md`).

---

## 4. Execution phases (each ends in a gate)

### Phase A — Single 3B engine, validated  (Contract C4, C6; gap G5, G3)
- A1 ⬜ Produce `qwen2.5-3b-instruct-q4_k_m.gguf` (extract from the already-pulled Ollama
  blob if it's standard GGUF; else download official HF GGUF). Place in
  `tool-1-cv-maker/data/models/`.
- A2 ⬜ Register a `large`/3B tier in `local_llm.MODEL_TIERS` (filename + pinned SHA-256)
  and make it the default when present. Keep 1.5B as fallback.
- A3 ⬜ Make engine selection single-track: in-process GGUF default; Ollama only if
  `AMS_USE_OLLAMA=1`. Simplify `get_status()` to report the true active engine (fix G3).
- A4 ⬜ **Gate:** load the 3B in-process and run `eval/run_extraction_eval.py` against the
  in-process path (Ollama off). Must hit **macro-F1 ≥ 0.73**. Record `qwen3b-inproc` row
  in RESULTS.md. *If it regresses vs Ollama-3B, diagnose before proceeding.*

### Phase B — Tool 2 trainer fixes  (Contract C3; gaps G1, G2)
- B1 ⬜ Add `trainer_notes` to `ParticipantResponse` and populate it on detail. (G1)
- B2 ⬜ Canonical-aware name/email on import: fall back to `basics.full_name`/`basics.email`
  when top-level absent. (G2)
- B3 ⬜ **Gate:** tests — `trainer_notes` round-trips (save → reload); canonical import of a
  Tool-1 export shows the real participant name. Full Tool 2 suite green.

### Phase C — Packaging completeness  (Contracts C1, C5; gaps G4, G6)
- C1p ⬜ Bundle `data/knowledge` (and confirm `data/models`) into `build_tool1.spec` datas
  and `build_all.bat` so the frozen exe finds berufe.json + the 3B GGUF. (G4)
- C2p ⬜ Update `install.bat` / Inno `.iss` messaging + always-on desktop shortcut; reflect
  "3B AI included, fully offline". (G6)
- C3p ⬜ Launcher: pre-warm the in-process 3B before opening the browser (avoid cold first
  answer), with graceful timeout.
- C4p ⬜ **Gate:** `build_all.bat` produces `dist/` with both exes + launcher + 3B GGUF +
  knowledge; layout asserted.

### Phase D — Clean-machine certification  (all contracts; gap G7)
- D1 ⬜ Extend `packaging/smoke_test.py` to drive the built launcher: both `/health`,
  offline-AI present (in-process model on disk), and a **real extraction round-trip**
  (POST an answer → get structured fields) + a **Tool1→Tool2 import** of that CV.
- D2 ⬜ **Gate:** smoke test PASS against `dist/`. (Manual clean-VM run is the final
  hand-off cert — documented, not automatable here.)

### Phase E — End-to-end product test & docs
- E1 ⬜ One scripted end-to-end test: interview answers → CV → PDF/DOCX exists & parses →
  Tool 2 import → edit → approve → bulk export. (the "put money where mouth is" test)
- E2 ⬜ `FOR_MARKO.md` refreshed: exactly what to click, what he'll see, offline promise.
- E3 ⬜ **Gate:** full repo test suite green; COMPLETION_PLAN statuses all ✅.

---

## 5. Out of scope for this push (explicit)
Ollama bundling (removed), GPU path, ESCO/MeinAMS, cohort-creation UI, retention job.
These are logged in their docs and do not block Marko's trial.
