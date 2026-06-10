"""Unit tests for smoke_test.py polling/parse logic (no network, no exe)."""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import smoke_test as st  # noqa: E402


# ---- wait_health -----------------------------------------------------------

def test_wait_health_succeeds_immediately():
    calls = []
    got = st.wait_health(
        8000, timeout=10,
        _get=lambda url: {"status": "ok"},
        _sleep=lambda s: calls.append(s),
    )
    assert got is True
    assert calls == []  # returned before sleeping


def test_wait_health_succeeds_after_retries():
    seq = [None, None, {"status": "ok"}]
    state = {"i": 0}

    def fake_get(url):
        v = seq[state["i"]]
        state["i"] += 1
        return v

    got = st.wait_health(8000, timeout=10, _get=fake_get, _sleep=lambda s: None)
    assert got is True
    assert state["i"] == 3


def test_wait_health_times_out():
    # timeout=0 → loop body never runs → False
    got = st.wait_health(8000, timeout=0, _get=lambda url: {"status": "ok"},
                         _sleep=lambda s: None)
    assert got is False


def test_wait_health_ignores_non_ok_status():
    got = st.wait_health(8000, timeout=0, _get=lambda url: {"status": "starting"},
                         _sleep=lambda s: None)
    assert got is False


# ---- offline_ai_ready ------------------------------------------------------

def test_offline_ready_local_model_on_disk():
    assert st.offline_ai_ready(
        {"status": "success", "data": {"active_engine": "local",
                                       "local": {"model_exists_on_disk": True},
                                       "ollama": {"ollama_available": False}}}
    ) is True


def test_offline_ready_ollama_only():
    assert st.offline_ai_ready(
        {"data": {"active_engine": "ollama",
                  "local": {"model_exists_on_disk": False},
                  "ollama": {"ollama_available": True}}}
    ) is True


def test_offline_not_ready_rules_only():
    assert st.offline_ai_ready(
        {"data": {"active_engine": "rules",
                  "local": {"model_exists_on_disk": False},
                  "ollama": {"ollama_available": False}}}
    ) is False


def test_offline_not_ready_on_none():
    assert st.offline_ai_ready(None) is False


def test_offline_ready_handles_flat_payload():
    # tolerate a payload without the data wrapper
    assert st.offline_ai_ready({"local": {"local_model_available": True}}) is True


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v"]))
