"""
Field-level extraction metrics (precision / recall / F1) with RELAXED matching.

Standard information-extraction methodology: score each field against a labelled
gold value. Scalar fields (name/city/phone/email/target_job) are single-value;
list fields (experiences/education/skills/languages) use set-style P/R/F1 where
gold entries are REQUIRED keywords/substrings that must appear in some predicted
entry, and predicted entries are "relevant" if they contain a gold keyword
(so junk/extra predictions — e.g. an identity blob mis-filed as experience —
lower precision).

Pure functions, stdlib only → unit-testable without loading any model.
"""
from __future__ import annotations
import re
import difflib

_KEEP = re.compile(r"[^\w\s@.+-]", re.UNICODE)
_WS = re.compile(r"\s+")


def normalize(s: str) -> str:
    s = (s or "").lower().strip()
    s = _KEEP.sub(" ", s)
    return _WS.sub(" ", s).strip()


def _fuzzy(a: str, b: str, thr: float = 0.86) -> bool:
    if not a or not b:
        return False
    return difflib.SequenceMatcher(None, a, b).ratio() >= thr


def keyword_in(keyword: str, candidates) -> bool:
    """True if `keyword` appears (normalised substring) in any candidate, or fuzzy-matches one."""
    k = normalize(keyword)
    if not k:
        return False
    for c in candidates:
        nc = normalize(c)
        if not nc:
            continue
        if k in nc or nc in k or _fuzzy(k, nc):
            return True
    return False


def _prf(precision: float, recall: float) -> float:
    return (2 * precision * recall / (precision + recall)) if (precision + recall) else 0.0


def scalar_score(pred: str, gold: str):
    """Score a single-value field. Returns None when there is no gold expectation."""
    gold = (gold or "").strip()
    if not gold:
        return None
    pred = (pred or "").strip()
    ok = bool(pred) and keyword_in(gold, [pred])
    precision = 1.0 if ok else 0.0   # a present-but-wrong prediction scores 0
    recall = 1.0 if ok else 0.0
    return {"match": ok, "precision": precision, "recall": recall, "f1": _prf(precision, recall)}


def list_score(pred, gold_keywords):
    """
    Set-style P/R/F1 with relaxed matching. Returns None when no gold expectation.
    - recall:    fraction of gold keywords found in some predicted entry
    - precision: fraction of predicted entries that contain a gold keyword
    """
    gold = [g for g in (gold_keywords or []) if normalize(g)]
    pred = [p for p in (pred or []) if normalize(p)]
    if not gold:
        return None
    found = sum(1 for g in gold if keyword_in(g, pred))
    recall = found / len(gold)
    if pred:
        relevant = sum(1 for p in pred if any(keyword_in(g, [p]) for g in gold))
        precision = relevant / len(pred)
    else:
        precision = 0.0
    return {"tp": found, "gold_n": len(gold), "pred_n": len(pred),
            "precision": precision, "recall": recall, "f1": _prf(precision, recall)}


def macro_average(field_scores: dict) -> dict:
    """field_scores: {field_name: [score_dict, ...]} → per-field + overall macro P/R/F1."""
    per_field = {}
    all_p, all_r, all_f = [], [], []
    for field, scores in field_scores.items():
        scores = [s for s in scores if s is not None]
        if not scores:
            continue
        p = sum(s["precision"] for s in scores) / len(scores)
        r = sum(s["recall"] for s in scores) / len(scores)
        f = sum(s["f1"] for s in scores) / len(scores)
        per_field[field] = {"precision": round(p, 3), "recall": round(r, 3),
                            "f1": round(f, 3), "n": len(scores)}
        all_p.append(p); all_r.append(r); all_f.append(f)
    overall = {
        "precision": round(sum(all_p) / len(all_p), 3) if all_p else 0.0,
        "recall": round(sum(all_r) / len(all_r), 3) if all_r else 0.0,
        "macro_f1": round(sum(all_f) / len(all_f), 3) if all_f else 0.0,
        "fields": len(per_field),
    }
    return {"per_field": per_field, "overall": overall}
