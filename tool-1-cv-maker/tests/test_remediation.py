"""
Remediation regression suite — proves the audit fixes work and STAY fixed.

Each test maps to an audit finding it locks down. Model-independent (no GGUF
required) so it runs in CI on every push.
"""

import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src", "backend"))


# ── RC-6: busy_timeout set on connections (avoids spurious 'database is locked') ──
def test_busy_timeout_is_set(db_manager):
    rows = db_manager.execute_query("PRAGMA busy_timeout")
    assert rows and rows[0]["timeout"] >= 5000


# ── RC-2 / M1: right-to-erasure actually cascades and removes ALL PII ──────────
def test_erasure_cascades_and_removes_all_pii(db_manager):
    from privacy.data_deletion import DataDeletion

    # Production runs with foreign_keys OFF (see db.py); neutralise any FK-on
    # state leaked by an earlier compliance test on the shared connection.
    db_manager.execute_update("PRAGMA foreign_keys=OFF")
    user_id = "erase-probe-user"
    db_manager.create_user(user_id=user_id, email="probe@example.com")
    sid = db_manager.create_session(user_id=user_id, interview_path="other", language="de")
    db_manager.save_answer(session_id=sid, question_id="q1", answer_text="Max Mustermann, Wien")

    # Pre-condition: data exists.
    assert db_manager.execute_query("SELECT 1 FROM users WHERE user_id=?", (user_id,))
    assert db_manager.execute_query("SELECT 1 FROM answers WHERE session_id=?", (sid,))

    ok = DataDeletion(db_manager).delete_user_data(user_id)
    assert ok is True

    # Post-condition: user, session AND answers all gone (cascade).
    assert not db_manager.execute_query("SELECT 1 FROM users WHERE user_id=?", (user_id,))
    assert not db_manager.execute_query("SELECT 1 FROM sessions WHERE id=?", (sid,))
    assert not db_manager.execute_query("SELECT 1 FROM answers WHERE session_id=?", (sid,)), \
        "answers must be cascade-deleted — orphaned PII would breach Art. 17"


def test_erasure_of_unknown_user_is_safe(db_manager):
    # Unknown-but-valid user: the deleter returns False (no-op), does not crash.
    from privacy.data_deletion import DataDeletion
    assert DataDeletion(db_manager).delete_user_data("does-not-exist") is False
    # Invalid input still raises (defensive).
    with pytest.raises(ValueError):
        DataDeletion(db_manager).delete_user_data("")


# ── RC-2 / M2: consent record store exists (Art. 7 demonstrable consent) ───────
def test_consent_records_table_exists(db_manager):
    rows = db_manager.execute_query(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='consent_records'")
    assert rows, "consent_records table must exist for demonstrable consent"


# ── RC-5 / M12: export filename sanitizer blocks path traversal / collision ────
@pytest.mark.parametrize("evil,must_not_contain", [
    ("../../etc/passwd", "/"),
    ("..\\..\\windows\\system32", "\\"),
    ("....//....//x", "/"),
    ("a/b/c", "/"),
])
def test_filename_sanitizer_blocks_traversal(evil, must_not_contain):
    from export.base import _sanitize_filename_component
    out = _sanitize_filename_component(evil)
    assert must_not_contain not in out
    assert not out.startswith("."), "must not produce a dotfile / traversal token"
    assert out, "must always return a non-empty token"


def test_filename_sanitizer_keeps_safe_names():
    from export.base import _sanitize_filename_component
    assert _sanitize_filename_component("Lebenslauf_Maria-2024") == "Lebenslauf_Maria-2024"


# ── RC-5 / M9-M10: unpinned model tiers are REFUSED (no silent skip) ───────────
def test_unpinned_model_tier_is_refused(monkeypatch):
    monkeypatch.delenv("AMS_ALLOW_UNPINNED_MODEL", raising=False)
    from ai import local_llm
    # 'light' and 'full' ship with empty sha256 → must refuse, not silently skip.
    assert local_llm.MODEL_TIERS["light"]["sha256"] == ""
    assert local_llm.download_model(tier="light") is False
    # The pinned default tier keeps a real hash.
    assert len(local_llm.MODEL_TIERS["medium"]["sha256"]) == 64


# ── RC-3 / M4: retention purges COMPLETED records past the ceiling ─────────────
def test_retention_purges_completed_records(db_manager):
    from interview.engine import InterviewEngine
    # Seed an old COMPLETED session (the kind that used to be kept forever).
    db_manager.create_user(user_id="old-user")
    db_manager.execute_update(
        "INSERT INTO sessions (user_id, interview_path, language, created_at, completed, approved, locked) "
        "VALUES ('old-user','other','de','2000-01-01 00:00:00', 1, 1, 1)")
    old = db_manager.execute_query(
        "SELECT id FROM sessions WHERE created_at < '2001-01-01'")
    assert old, "seed session should exist"

    engine = InterviewEngine(db_manager)
    deleted = engine.cleanup_old_sessions(days_old=365, draft_days_old=30)
    assert deleted >= 1

    remaining = db_manager.execute_query(
        "SELECT id FROM sessions WHERE created_at < '2001-01-01'")
    assert not remaining, "completed/approved/locked records past the ceiling must be purged"


def test_retention_disabled_when_zero(db_manager):
    from interview.engine import InterviewEngine
    db_manager.execute_update("PRAGMA foreign_keys=OFF")
    db_manager.execute_update(
        "INSERT INTO sessions (user_id, interview_path, language, created_at, completed) "
        "VALUES ('z','other','de','2000-01-01 00:00:00', 1)")
    engine = InterviewEngine(db_manager)
    assert engine.cleanup_old_sessions(days_old=0) == 0
    assert db_manager.execute_query("SELECT 1 FROM sessions WHERE created_at < '2001-01-01'")


# ── RC-2 / M5: compliance checker is honest (no false "COMPLIANT") ─────────────
def test_compliance_check_does_not_claim_legal_compliance(db_manager):
    from privacy import NetworkBlocker, PrivacyFilter, ComplianceChecker
    checker = ComplianceChecker(db_manager, NetworkBlocker(), PrivacyFilter())
    results = checker.verify_all_requirements()
    # The misleading "overall_compliant / COMPLIANT" key is gone.
    assert "overall_compliant" not in results
    assert "all_controls_present" in results
    # The deletion check now EXERCISES erasure rather than returning True blindly:
    # it must leave no probe user behind.
    assert not db_manager.execute_query(
        "SELECT 1 FROM users WHERE user_id LIKE '%selfcheck%'")


def test_compliance_logging_check_fails_when_filter_not_installed(db_manager):
    """_verify_logging_filtered must FAIL when no PrivacyFilter is on a handler."""
    import logging
    from privacy import NetworkBlocker, PrivacyFilter, ComplianceChecker
    from privacy.logging_rules import PrivacyFilter as PF
    # Ensure no PrivacyFilter is attached to any handler.
    for lg in (logging.getLogger(), logging.getLogger("uvicorn")):
        for h in lg.handlers:
            h.filters = [f for f in h.filters if not isinstance(f, PF)]
    checker = ComplianceChecker(db_manager, NetworkBlocker(), PrivacyFilter())
    assert checker._verify_logging_filtered() is False


# ── RC-2 / M3: the handler-level PII filter installer actually attaches ────────
def test_privacy_filter_installs_on_handlers():
    import logging
    from privacy.logging_rules import install_privacy_filter_on_handlers, PrivacyFilter
    root = logging.getLogger()
    if not root.handlers:
        logging.basicConfig()
    n = install_privacy_filter_on_handlers()
    assert n >= 1
    assert any(isinstance(f, PrivacyFilter) for h in root.handlers for f in h.filters)
