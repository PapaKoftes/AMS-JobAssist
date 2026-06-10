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

> **The 8-case 0.837 was not representative.** On the full 20-case set (CP-B added
> 12 harder, sparser, more multilingual AMS personas — Arabic/Russian names,
> one-line inputs, missing fields) the true offline-3B quality is **macro-F1 ≈ 0.73**.
> Two identical runs (A, B above) agree on the aggregate (0.730 vs 0.731) but the
> small-n fields **skills and languages swing ±0.07 purely from LLM sampling** —
> e.g. `de-it-10` skills scored 0.0 in run A and 0.67 in run B. That nondeterminism
> made the eval untrustworthy as an instrument, so extraction temperature was set
> to **0.0 (greedy)** — see `qwen3b-temp0` row once measured.

## Conclusions (evidence-based)

1. **Honest baseline is ~0.73, not 0.84.** The headline number dropped when the gold
   set grew 8→20 because the new cases are harder (sparse one-liners, Arabic/Russian
   names, missing education/skills). This is the point of a bigger eval: it stops us
   shipping a flattering subset number. **Don't quote 0.837 — quote 0.73.**

2. **Extraction must be deterministic.** Run-to-run skills/languages variance of ±0.07
   at temperature 0.1 meant the eval couldn't certify a code change as good or bad.
   Extraction is fact-pulling, not creative writing, so temperature is now **0.0
   (greedy, top_p 1.0)** in both `_ollama_to_json` and `_ollama_freeform`. Re-running
   the same input now yields the same output — the eval is a real instrument again.

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
