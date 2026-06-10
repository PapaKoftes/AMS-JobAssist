# Extraction eval — baseline of record

Measured with `run_extraction_eval.py` against `gold_dataset.json` (field-level
precision/recall/F1, relaxed matching). All runs fully offline. Re-run on every
model/prompt/pipeline change and update this table — **measure, don't eyeball.**

| Run | Model | Pipeline | n | macro-F1 | P | R | notable |
|---|---|---|---|---|---|---|---|
| baseline | local 1.5B (llama-cpp) | single-pass | 5 | 0.805 | 0.799 | 0.813 | skills 0.43, edu 0.67 |
| | local 1.5B | two-pass | 5 | 0.817 | 0.835 | 0.809 | exp precision 0.80→1.0; +3.7× latency |
| **current default** | **qwen2.5:3b (Ollama)** | **single-pass** | **8** | **0.837** | 0.832 | 0.858 | edu 0.75, skills 0.40 |
| | qwen2.5:3b | two-pass | 8 | 0.825 | 0.840 | 0.821 | edu **0.92** but skills **0.14** (net wash) |

## Conclusions (evidence-based)

1. **Model size is the real lever.** qwen2.5:3b (0.837) > local 1.5B (0.805), mainly
   on education and target/city consistency. Moving toward a 7B (Qwen2.5-7B,
   German-MMLU ~68) is the validated direction — re-run with `--tag qwen7b`.

2. **Two-pass is NOT a default win at these sizes.** It helped on the 1.5B (+0.012)
   but was a net loss on the 3B (−0.012): it lifted education (+0.17) yet hurt
   skills (−0.26), and it's slower. The "Format Tax" paper's +7pp does not
   reproduce on this task/scale. → **two-pass OFF by default** (code + the
   `AMS_EXTRACT_TWOPASS=1` flag kept for future larger-model / larger-gold-set
   experiments).

3. **Strong everywhere:** name/phone/email = 1.0 across all configs (regex atoms +
   model). **Weakest field = skills** — the next real target (polish over-expansion
   + small-model noise). A larger gold set (target ~100 cases) would tighten the
   noisy fields (skills/education currently n=2–4).

## How to reproduce / extend
```
python eval/run_extraction_eval.py --tag <label> --json eval/<label>.json
AMS_EXTRACT_TWOPASS=1 python eval/run_extraction_eval.py --tag <label>-twopass   # A/B
```
