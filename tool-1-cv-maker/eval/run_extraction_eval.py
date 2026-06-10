#!/usr/bin/env python3
"""
Extraction evaluation harness — objective, re-runnable quality measurement.

Runs the REAL extraction pipeline (extract_cv_fields → Ollama 7B if available,
else local 1.5B / rules) over a labelled gold dataset and reports field-level
precision / recall / F1 with relaxed matching, plus an overall macro-F1.

This is the measurement backbone: every model swap, prompt change, or pipeline
change (e.g. two-pass constrained extraction) can now be compared on the SAME
gold set instead of eyeballing. Fully offline.

Usage:
    python eval/run_extraction_eval.py                 # full gold set
    python eval/run_extraction_eval.py --limit 3       # quick subset
    python eval/run_extraction_eval.py --json out.json # also write machine-readable report
    python eval/run_extraction_eval.py --tag qwen7b    # label the run (for A/B comparison)

Exit code is non-zero if macro-F1 < --min-f1 (default 0.0 → never fails), so it
can gate CI once a baseline is established.
"""
import sys
import os
import json
import time
import argparse
from pathlib import Path

HERE = Path(__file__).resolve().parent
BACKEND = HERE.parent / "src" / "backend"
sys.path.insert(0, str(BACKEND))
sys.path.insert(0, str(HERE))

import metrics  # noqa: E402

# Scalar fields are single-value; list fields use set P/R/F1. Languages live in
# the extractor's `skills` list (the builder separates them later), so we score
# gold languages against the predicted skills pool.
_SCALAR = ["name", "city", "phone", "email", "target_job"]
_LIST = {"experiences": "experiences", "education": "education", "skills": "skills"}


def _load_gold(path: Path):
    data = json.loads(path.read_text(encoding="utf-8"))
    return data.get("cases", [])


def evaluate(cases, tag=""):
    from ai.local_llm import extract_cv_fields  # imported here so --help is instant
    field_scores = {f: [] for f in _SCALAR}
    field_scores.update({"experiences": [], "education": [], "skills": [], "languages": []})
    per_case = []
    t0 = time.time()

    for i, case in enumerate(cases, 1):
        cid = case.get("id", f"case{i}")
        exp = case.get("expected", {})
        ts = time.time()
        try:
            pred = extract_cv_fields(case["text"], case.get("language", "de")) or {}
        except Exception as e:
            print(f"  [{i}/{len(cases)}] {cid}: EXTRACTION ERROR: {e}")
            pred = {}
        dt = time.time() - ts

        case_scores = {}
        for f in _SCALAR:
            s = metrics.scalar_score(pred.get(f, ""), exp.get(f, ""))
            field_scores[f].append(s)
            if s is not None:
                case_scores[f] = round(s["f1"], 2)
        for gold_key, pred_key in _LIST.items():
            s = metrics.list_score(pred.get(pred_key, []), exp.get(gold_key, []))
            field_scores[gold_key].append(s)
            if s is not None:
                case_scores[gold_key] = round(s["f1"], 2)
        # languages are merged into the predicted skills pool by the extractor
        s = metrics.list_score(pred.get("skills", []), exp.get("languages", []))
        field_scores["languages"].append(s)
        if s is not None:
            case_scores["languages"] = round(s["f1"], 2)

        per_case.append({"id": cid, "seconds": round(dt, 1), "f1": case_scores})
        line = " ".join(f"{k}={v}" for k, v in case_scores.items())
        print(f"  [{i}/{len(cases)}] {cid} ({dt:.1f}s)  {line}")

    agg = metrics.macro_average(field_scores)
    return {
        "tag": tag,
        "n_cases": len(cases),
        "elapsed_s": round(time.time() - t0, 1),
        "overall": agg["overall"],
        "per_field": agg["per_field"],
        "per_case": per_case,
    }


def _print_report(rep):
    print("\n" + "=" * 60)
    print(f"  EXTRACTION EVAL  {('['+rep['tag']+']') if rep['tag'] else ''}")
    print("=" * 60)
    print(f"  cases: {rep['n_cases']}   time: {rep['elapsed_s']}s")
    o = rep["overall"]
    print(f"  OVERALL  macro-F1={o['macro_f1']}  P={o['precision']}  R={o['recall']}")
    print("  per field:")
    for f, m in rep["per_field"].items():
        print(f"    {f:<13} F1={m['f1']:<5} P={m['precision']:<5} R={m['recall']:<5} (n={m['n']})")
    print("=" * 60)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0, help="run only the first N cases")
    ap.add_argument("--json", type=str, default="", help="write machine-readable report here")
    ap.add_argument("--tag", type=str, default="", help="label this run (model/config)")
    ap.add_argument("--min-f1", type=float, default=0.0, help="exit non-zero if macro-F1 below this")
    ap.add_argument("--gold", type=str, default=str(HERE / "gold_dataset.json"))
    args = ap.parse_args()

    cases = _load_gold(Path(args.gold))
    if args.limit:
        cases = cases[:args.limit]
    print(f"Evaluating {len(cases)} case(s) against the live extraction pipeline...")
    rep = evaluate(cases, tag=args.tag)
    _print_report(rep)
    if args.json:
        Path(args.json).write_text(json.dumps(rep, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"  report written: {args.json}")
    return 0 if rep["overall"]["macro_f1"] >= args.min_f1 else 1


if __name__ == "__main__":
    sys.exit(main())
