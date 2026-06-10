"""
Unit tests for Ollama model selection (mocked /api/tags — no network).

Covers AMS_OLLAMA_MODEL pinning (used by the eval and ops to force an exact
tag, e.g. qwen2.5:7b) and the auto-detect fallback via PREFERRED_MODELS.
"""
import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parent.parent / "src" / "backend"
sys.path.insert(0, str(BACKEND))
from ai import ollama as O  # noqa: E402


def _reset_cache(monkeypatch=None):
    O._ollama_available = None
    O._ollama_model = None
    # Ollama is opt-in now (single-track default = in-process GGUF). These tests
    # exercise the detection/selection logic, so they enable the opt-in flag.
    if monkeypatch is not None:
        monkeypatch.setenv("AMS_USE_OLLAMA", "1")


def _fake_tags(*names):
    return lambda url, timeout=2: {"models": [{"name": n} for n in names]}


def test_pin_selects_exact_installed_tag(monkeypatch):
    _reset_cache(monkeypatch)
    monkeypatch.setattr(O, "_http_get", _fake_tags("qwen2.5:3b", "qwen2.5:7b"))
    monkeypatch.setenv("AMS_OLLAMA_MODEL", "qwen2.5:7b")
    ok, model = O.detect_ollama()
    assert ok is True
    assert model == "qwen2.5:7b", "pin must win even though 3b is also installed"


def test_pin_ignored_when_not_installed(monkeypatch):
    _reset_cache(monkeypatch)
    monkeypatch.setattr(O, "_http_get", _fake_tags("qwen2.5:3b"))
    monkeypatch.setenv("AMS_OLLAMA_MODEL", "qwen2.5:7b")  # not installed
    ok, model = O.detect_ollama()
    assert ok is True
    assert model == "qwen2.5:3b", "missing pin must fall back to auto-detect, not fail"


def test_autodetect_prefers_qwen(monkeypatch):
    _reset_cache(monkeypatch)
    monkeypatch.delenv("AMS_OLLAMA_MODEL", raising=False)
    # mistral listed first, but qwen2.5 is higher in PREFERRED_MODELS
    monkeypatch.setattr(O, "_http_get", _fake_tags("mistral:latest", "qwen2.5:3b"))
    ok, model = O.detect_ollama()
    assert ok is True
    assert model.startswith("qwen2.5"), "PREFERRED_MODELS must rank qwen2.5 above mistral"


def test_no_models_means_unavailable(monkeypatch):
    _reset_cache(monkeypatch)
    monkeypatch.delenv("AMS_OLLAMA_MODEL", raising=False)
    monkeypatch.setattr(O, "_http_get", lambda url, timeout=2: {"models": []})
    ok, model = O.detect_ollama()
    assert ok is False and model is None


def test_ollama_off_by_default_single_track(monkeypatch):
    """Single-track policy: Ollama must be OFF unless AMS_USE_OLLAMA is opted in,
    even if Ollama is running with models — the shipped default is in-process GGUF."""
    O._ollama_available = None
    O._ollama_model = None
    monkeypatch.delenv("AMS_USE_OLLAMA", raising=False)
    # _http_get would return models, but the gate must short-circuit before calling it
    called = {"n": 0}

    def _should_not_be_called(url, timeout=2):
        called["n"] += 1
        return {"models": [{"name": "qwen2.5:7b"}]}

    monkeypatch.setattr(O, "_http_get", _should_not_be_called)
    ok, model = O.detect_ollama()
    assert ok is False and model is None
    assert called["n"] == 0, "must not even probe Ollama when not opted in"
