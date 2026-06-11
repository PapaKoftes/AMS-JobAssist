# Extraction eval — baseline of record

Measured with `run_extraction_eval.py` against `gold_dataset.json` (field-level
precision/recall/F1, relaxed matching). All runs fully offline. Re-run on every
model/prompt/pipeline change and update this table — **measure, don't eyeball.**

| Run | Model | Pipeline | n | macro-F1 | P | R | notable |
|---|---|---|---|---|---|---|---|
| baseline | local 1.5B (llama-cpp) | single-pass | 5 | 0.805 | 0.799 | 0.813 | skills 0.43, edu 0.67 |
| | local 1.5B | two-pass | 5 | 0.817 | 0.835 | 0.809 | exp precision 0.80→1.0; +3.7× latency |
| optimistic subset | qwen2.5:3b (Ollama) | single-pass | 8 | 0.837 | 0.832 | 0.858 | edu 0.75, skills 0.40 — **rosy: easy subset** |
| | qwen2.5:3b | two-pass | 8 | 0.825 | 0.840 | 0.821 | edu **0.92** but skills **0.14** (net wash) |
| **honest baseline A** | **qwen2.5:3b** | **single, temp 0.1** | **20** | **0.730** | 0.724 | 0.754 | skills 0.27, exp 0.54, lang 0.51 |
| honest baseline B (re-run) | qwen2.5:3b | single, temp 0.1 | 20 | 0.731 | 0.722 | 0.767 | skills 0.34, lang 0.47 — **±0.07 swing** |
| **baseline of record** | **qwen2.5:3b** | **single, temp 0 (greedy)** | **20** | **0.738** | 0.727 | 0.775 | skills 0.31, exp 0.55, lang 0.53 |
| temp-0 re-run (verify) | qwen2.5:3b | single, temp 0 (greedy) | 20 | 0.730 | 0.720 | 0.764 | skills/lang **identical**; exp/edu still wobble |
| **size lever** | **qwen2.5:7b** | **single, temp 0 (greedy)** | **20** | **0.806** | 0.790 | 0.855 | skills **0.60**, exp **0.83** — fixes the 2 weak fields |
| **★ SHIPPED default** | **qwen2.5-3b GGUF, in-process (llama-cpp)** | **labelled-line, temp 0** | **20** | **0.742** | 0.745 | 0.744 | exp **0.78**, target 0.80; skills 0.20 weakest. ~12 s/case warm. |
| **★ + taxonomy skill-boost** | **qwen2.5-3b GGUF, in-process** | **labelled-line + skills-taxonomy scan** | **20** | **0.765** | 0.768 | 0.783 | **skills 0.20→0.40 (doubled)**, lang 0.44→0.52; the weakest field fixed by surfacing skills buried in sentences. |

> **★ This is what Marko actually gets.** The shipped product runs the 3B GGUF
> in-process via llama-cpp-python (no Ollama, no service, one double-click, fully
> offline). It scores **0.742** — slightly *above* the Ollama-3B path (0.738) and
> well above the 1.5B, because its labelled-line extractor structures work
> experience far better (exp 0.78 vs 0.55). It trades some skills/languages recall
> (skills 0.20 — still the weakest field, the known open problem). Engine is
> single-track: Ollama is opt-in only (`AMS_USE_OLLAMA=1`), used by this eval's
> Ollama rows and power users; the 7B GGUF can be dropped in as an optional
> quality upgrade.

> **The 8-case 0.837 was not representative.** On the full 20-case set (CP-B added
> 12 harder, sparser, more multilingual AMS personas — Arabic/Russian names,
> one-line inputs, missing fields) the true offline-3B quality is **macro-F1 ≈ 0.73**.
> Two identical runs (A, B above) agree on the aggregate (0.730 vs 0.731) but the
> small-n fields **skills and languages swing ±0.07 purely from LLM sampling** —
> e.g. `de-it-10` skills scored 0.0 in run A and 0.67 in run B. That nondeterminism
> made the eval untrustworthy as an instrument, so extraction temperature was set
> to **0.0 (greedy)** — see `qwen3b-temp0` row once measured.

## Conclusions (evidence-based)

1. **Honest baseline is ~0.73 (3B), not 0.84.** The headline number dropped when the gold
   set grew 8→20 because the new cases are harder (sparse one-liners, Arabic/Russian
   names, missing education/skills). This is the point of a bigger eval: it stops us
   shipping a flattering subset number. **Don't quote 0.837 — quote 0.738 for 3B.**

1b. **Model size IS the lever — measured (+0.068), and it fixes exactly the weak fields.**
   qwen2.5:7b scores **0.806** on the same 20 hard cases vs 3B's 0.738. The gain is
   concentrated where 3B is worst: **skills 0.31→0.60** (recall 0.43→0.86 — the 7B
   actually finds embedded skills) and **experiences 0.55→0.83**. Atoms and the
   already-good fields are unchanged. The audit's "size is the real lever" claim is
   now evidence, not assertion. **BUT latency:** 7B ran 825s/20 cases ≈ **40s per
   answer on CPU** — too slow for the live interview UX. So the recommendation is
   tiered, not "always 7B": ship the bundled 1.5B as the fast offline default; use 3B
   when Ollama is present and responsiveness matters; reserve **7B for batch/quality
   mode or a machine with a GPU**. 7B-on-hard-cases (0.806) ≈ 3B-on-easy-cases (0.837),
   which is the fair apples-to-apples read.

2. **Extraction temperature → 0 cut the worst variance, but does NOT give bit-perfect
   determinism.** At temp 0.1 the skills/languages fields swung ±0.07 between identical
   runs — enough to drown any real signal. At temp 0 (greedy, top_p 1.0, in both
   `_ollama_to_json` and `_ollama_freeform`) two back-to-back 20-case runs produced
   **identical skills/languages/name/city/phone/email/target_job** scores — the swingers
   are locked. The aggregate tightened to ±0.008 (0.738 vs 0.730). BUT experiences and
   education still wobbled (~0.025 and 0.10): llama.cpp greedy decode is still subject to
   floating-point nondeterminism in threaded matmul, so it is not bit-reproducible. Net:
   the eval is now a usable instrument for skills/languages/atoms (the fields we tune),
   but treat ±0.01 on the aggregate and ±0.1 on small-n exp/edu as noise, not signal.

3. **Skills is the weakest field (~0.27–0.34) and CP-C's regex backstop did NOT
   demonstrably lift the aggregate.** No same-set before/after exists, and the swing
   is larger than any claimed gain, so **skills remains an open problem, not "fixed."**
   The backstop ships (it never hurts and helps the embedded-skill cases) but is not
   credited with a win. Real levers still on the table: bigger model (7B), gold-set
   growth to ~100 to de-noise small-n fields, and a skills-specific prompt/labelling pass.

4. **Two-pass is NOT a default win at these sizes.** It helped the 1.5B (+0.012) but was
   a net loss on the 3B (−0.012): lifted education (+0.17), hurt skills (−0.26), slower.
   The "Format Tax" +7pp does not reproduce here. → **two-pass OFF by default**
   (`AMS_EXTRACT_TWOPASS=1` kept for re-testing on larger models / larger gold sets).

5. **Rock-solid fields:** phone/email = 1.0, name = 0.90 (the two 0.0s are Arabic/Russian
   names the model transliterates oddly — a known, bounded gap). These come from regex
   atoms + model agreement and are the trustworthy core of every CV.

## How to reproduce / extend
```
python eval/run_extraction_eval.py --tag <label> --json eval/<label>.json
AMS_EXTRACT_TWOPASS=1 python eval/run_extraction_eval.py --tag <label>-twopass   # A/B
```
