"""Translate-first: non-German dumps are translated to German before the
German-prompted field extraction runs (fixes the AR/RU extraction collapse)."""
import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parent.parent / "src" / "backend"
sys.path.insert(0, str(BACKEND))

from ai import local_llm as L  # noqa: E402


def test_german_input_not_translated(monkeypatch):
    calls = {"n": 0}
    monkeypatch.setattr(L, "translate_to_german", lambda t: calls.__setitem__("n", calls["n"] + 1) or "X")
    # de/en must NOT be translated
    L.extract_cv_fields("Ich heiße Anna Berger. Ich suche als Köchin.", "de")
    L.extract_cv_fields("My name is Anna Berger.", "en")
    assert calls["n"] == 0


def test_non_german_input_is_translated_then_extracted(monkeypatch):
    # Force the in-process path (no Ollama) and a deterministic translation.
    monkeypatch.setattr(L, "translate_to_german",
                        lambda t: "Mein Name ist Ahmed Ali. Ich suche als Küchenhilfe.")
    # Ensure the Ollama early-return is skipped.
    import ai.ollama as O
    monkeypatch.setattr(O, "detect_ollama", lambda: (False, ""))

    out = L.extract_cv_fields("اسمي أحمد علي. أبحث عن عمل كمساعد مطبخ.", "ar")
    # Extraction now sees German → it can pull a name/target the Arabic original
    # would have collapsed on.
    assert "Ahmed" in (out.get("name") or "") or "Küchenhilfe" in (out.get("target_job") or "")


def test_translate_to_german_none_when_model_not_ready(monkeypatch):
    monkeypatch.setattr(L, "is_ready", lambda: False)
    assert L.translate_to_german("свободно немецкий") is None


def test_translation_failure_falls_back_to_original(monkeypatch):
    # translate returns None → original text is used, extraction still runs (no crash)
    monkeypatch.setattr(L, "translate_to_german", lambda t: None)
    import ai.ollama as O
    monkeypatch.setattr(O, "detect_ollama", lambda: (False, ""))
    out = L.extract_cv_fields("Some text in another language", "tr")
    assert isinstance(out, dict) and "name" in out


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v"]))
