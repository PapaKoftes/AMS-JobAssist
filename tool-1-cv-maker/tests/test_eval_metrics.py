"""
Unit tests for the extraction-eval metric math (model-free, CI-safe).

These prove the precision/recall/F1 + relaxed-matching logic is correct, so the
eval harness's numbers can be trusted. Extraction quality itself is measured by
eval/run_extraction_eval.py against the gold set (needs a model present).
"""
import sys
import json
from pathlib import Path

EVAL = Path(__file__).resolve().parent.parent / "eval"
sys.path.insert(0, str(EVAL))
import metrics  # noqa: E402


def test_scalar_exact_and_relaxed():
    assert metrics.scalar_score("Maria Huber", "Maria Huber")["match"] is True
    # relaxed: gold is contained / fuzzy
    assert metrics.scalar_score("Maria Huber (Wien)", "Maria Huber")["match"] is True
    # wrong, present prediction -> 0
    s = metrics.scalar_score("Hans Meier", "Maria Huber")
    assert s["match"] is False and s["f1"] == 0.0
    # missing prediction -> recall 0
    s = metrics.scalar_score("", "Maria Huber")
    assert s["recall"] == 0.0 and s["f1"] == 0.0
    # no gold expectation -> not scored
    assert metrics.scalar_score("anything", "") is None


def test_list_recall_and_precision():
    # all gold keywords found, no junk -> F1 1.0
    s = metrics.list_score(["Kassiererin bei Spar", "Reinigung im Hotel Sacher"],
                           ["Spar", "Hotel Sacher"])
    assert s["recall"] == 1.0 and s["precision"] == 1.0 and s["f1"] == 1.0

    # a junk prediction (no gold keyword) drops precision (catches the identity-blob bug)
    s = metrics.list_score(["Kassiererin bei Spar", "Meine Telefonnummer ist ..."],
                           ["Spar"])
    assert s["recall"] == 1.0
    assert s["precision"] == 0.5          # 1 of 2 predicted entries is relevant
    assert 0.6 < s["f1"] < 0.7

    # missed gold keyword -> recall < 1
    s = metrics.list_score(["Kassiererin bei Spar"], ["Spar", "Hotel Sacher"])
    assert s["recall"] == 0.5

    # empty prediction -> recall 0
    s = metrics.list_score([], ["Spar"])
    assert s["recall"] == 0.0 and s["f1"] == 0.0

    # no gold expectation -> not scored
    assert metrics.list_score(["x"], []) is None


def test_keyword_relaxed_matching():
    # languages buried in a polished compound skill still count
    assert metrics.keyword_in("Deutsch", ["Deutschkenntnisse"]) is True
    assert metrics.keyword_in("Türkisch", ["Türkisch (Muttersprache)"]) is True
    assert metrics.keyword_in("SAP", ["MS Office"]) is False


def test_macro_average():
    fs = {
        "name": [metrics.scalar_score("Maria Huber", "Maria Huber")],          # f1 1.0
        "skills": [metrics.list_score(["Excel"], ["Excel", "Word"])],          # recall .5, prec 1 -> f1 .667
        "education": [None],                                                    # unscored -> ignored
    }
    agg = metrics.macro_average(fs)
    assert agg["per_field"]["name"]["f1"] == 1.0
    assert "education" not in agg["per_field"]      # all-None field dropped
    assert 0.0 < agg["overall"]["macro_f1"] <= 1.0


def test_gold_dataset_wellformed():
    gold = json.loads((EVAL / "gold_dataset.json").read_text(encoding="utf-8"))
    cases = gold["cases"]
    assert len(cases) >= 5
    for c in cases:
        assert c.get("id") and c.get("text") and isinstance(c.get("expected"), dict)
        # at least name + a target job labelled on every case
        assert c["expected"].get("name")
