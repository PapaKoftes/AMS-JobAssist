"""
Unit tests for two-pass Ollama extraction (mocked — no model/network needed).

Proves the orchestration: PASS 1 (freeform, unconstrained) → PASS 2 (constrained
JSON over the pass-1 notes), and that AMS_EXTRACT_TWOPASS=0 falls back to a single
constrained pass. The actual quality lift is measured by eval/run_extraction_eval.py
against a real model (--tag for A/B).
"""
import sys
import json
from pathlib import Path

BACKEND = Path(__file__).resolve().parent.parent / "src" / "backend"
sys.path.insert(0, str(BACKEND))
from ai import ollama as O  # noqa: E402


def test_two_pass_runs_freeform_then_json(monkeypatch):
    calls = []

    def fake_post(url, payload, timeout=30):
        calls.append(payload)
        if payload.get("format") == "json":
            return {"response": json.dumps({
                "name": "Maria Huber", "city": "Wien", "phone": "", "email": "",
                "target_job": "Verkäuferin",
                "experiences": ["Kassa und Verkauf bei Spar (5 Jahre)"],
                "education": [], "skills": ["Kassa"],
                "languages": ["Deutsch (Muttersprache)", "Kroatisch"],
                "motivation": "",
            })}
        # pass 1 freeform notes
        return {"response": "- Name: Maria Huber\n- Wohnort: Wien\n- Kassa und Verkauf bei Spar"}

    monkeypatch.setattr(O, "detect_ollama", lambda: (True, "testmodel"))
    monkeypatch.setattr(O, "_http_post", fake_post)
    monkeypatch.setenv("AMS_EXTRACT_TWOPASS", "1")

    out = O.extract_cv_fields_ollama("ich heisse maria, kassa bei spar...", "de")

    assert len(calls) == 2, "two-pass must make exactly two model calls"
    assert calls[0].get("format") != "json", "pass 1 must be UNCONSTRAINED (no format tax)"
    assert calls[1].get("format") == "json", "pass 2 must be constrained JSON"
    # pass 2 must be fed the pass-1 notes
    assert "Kassa und Verkauf bei Spar" in calls[1]["prompt"]
    assert "Originaltext" in calls[1]["prompt"], "pass 2 also gets the original as backstop"
    # output parsed correctly; languages merged into skills for the downstream pipeline
    assert out["name"] == "Maria Huber" and out["target_job"] == "Verkäuferin"
    assert "Deutsch (Muttersprache)" in out["skills"] and "Kroatisch" in out["skills"]


def test_single_pass_when_disabled(monkeypatch):
    calls = []

    def fake_post(url, payload, timeout=30):
        calls.append(payload)
        return {"response": json.dumps({"name": "X", "skills": [], "experiences": []})}

    monkeypatch.setattr(O, "detect_ollama", lambda: (True, "testmodel"))
    monkeypatch.setattr(O, "_http_post", fake_post)
    monkeypatch.setenv("AMS_EXTRACT_TWOPASS", "0")

    out = O.extract_cv_fields_ollama("text", "de")
    assert len(calls) == 1, "single-pass must make exactly one model call"
    assert calls[0].get("format") == "json"
    assert out["name"] == "X"


def test_returns_none_when_ollama_absent(monkeypatch):
    monkeypatch.setattr(O, "detect_ollama", lambda: (False, None))
    assert O.extract_cv_fields_ollama("text", "de") is None
