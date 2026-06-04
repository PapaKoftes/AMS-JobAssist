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


# ── W2-A: per-session access token is the strong ownership proof ──────────────
def test_session_access_token_minted_and_enforced(db_manager):
    from interview.engine import InterviewEngine
    eng = InterviewEngine(db_manager)
    res = eng.start_interview(user_id="tok-user", interview_path="other", language="de")
    token = res.get("access_token")
    sid = res["session_id"]
    assert token and len(token) >= 32, "a high-entropy token must be minted at start"

    # Stored on the session.
    row = db_manager.execute_query("SELECT access_token FROM sessions WHERE id=?", (sid,))
    assert row and row[0]["access_token"] == token

    # The authorize helper accepts the right token, rejects a wrong one.
    from app import _authorize_session_owner
    from fastapi import HTTPException
    assert _authorize_session_owner(db_manager, sid, supplied_token=token) == "tok-user"
    with pytest.raises(HTTPException):
        _authorize_session_owner(db_manager, sid, supplied_token="wrong-token")
    with pytest.raises(HTTPException):
        _authorize_session_owner(db_manager, sid)  # no proof at all


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
def test_retention_purges_completed_records_and_children(db_manager):
    """
    Retention must purge completed/approved/locked sessions past the ceiling AND
    their child rows — with NO orphaned PII. Run with foreign_keys OFF to mirror
    the worker-thread connection where ON DELETE CASCADE does NOT fire (the exact
    condition that previously orphaned child PII).
    """
    from interview.engine import InterviewEngine
    db_manager.execute_update("PRAGMA foreign_keys=OFF")  # mirror worker thread
    db_manager.create_user(user_id="old-user")
    db_manager.execute_update(
        "INSERT INTO sessions (user_id, interview_path, language, created_at, completed, approved, locked) "
        "VALUES ('old-user','other','de','2000-01-01 00:00:00', 1, 1, 1)")
    sid = db_manager.execute_query(
        "SELECT id FROM sessions WHERE created_at < '2001-01-01'")[0]["id"]
    # Seed child PII rows (FK is OFF, so the answer needs no registered question).
    db_manager.execute_update(
        "INSERT INTO answers (session_id, question_id, answer_text) VALUES (?, 'rq', 'Max Mustermann')", (sid,))
    db_manager.execute_update(
        "INSERT INTO consent_records (session_id, user_id, consent_given) VALUES (?, 'old-user', 1)", (sid,))
    assert db_manager.execute_query("SELECT 1 FROM answers WHERE session_id=?", (sid,))

    engine = InterviewEngine(db_manager)
    deleted = engine.cleanup_old_sessions(days_old=365, draft_days_old=30)
    assert deleted >= 1

    assert not db_manager.execute_query("SELECT id FROM sessions WHERE id=?", (sid,)), \
        "session past the ceiling must be purged"
    # The bug this locks: NO orphaned child PII may remain.
    assert not db_manager.execute_query("SELECT 1 FROM answers WHERE session_id=?", (sid,)), \
        "answers must NOT be orphaned (retention left child PII behind)"
    assert not db_manager.execute_query("SELECT 1 FROM consent_records WHERE session_id=?", (sid,)), \
        "consent_records must NOT be orphaned"


def test_admin_cleanup_endpoint_is_gated():
    """The destructive cleanup endpoint must refuse a non-loopback client without a key."""
    from api.interview import _require_local_or_key
    from fastapi import HTTPException

    class _FakeClient:
        host = "10.0.0.5"   # non-loopback

    class _FakeReq:
        client = _FakeClient()
        headers = {}

    with pytest.raises(HTTPException) as exc:
        _require_local_or_key(_FakeReq())
    assert exc.value.status_code == 403

    # Loopback is allowed.
    class _LoopClient:
        host = "127.0.0.1"

    class _LoopReq:
        client = _LoopClient()
        headers = {}

    _require_local_or_key(_LoopReq())  # must not raise


def test_foreign_keys_enabled_by_default(db_manager):
    """FK enforcement must be ON for every connection (prevents orphaned PII)."""
    row = db_manager.execute_query("PRAGMA foreign_keys")
    # PRAGMA foreign_keys returns [{'foreign_keys': 1}]
    val = list(row[0].values())[0] if row else 0
    assert val == 1, "foreign_keys must be ON so session cascade never orphans children"


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


# ── W2-B: encryption-at-rest startup gate (Art. 32) ───────────────────────────
def test_require_encryption_gate(tmp_path):
    import subprocess
    backend = str(Path(__file__).parent.parent / "src" / "backend")
    env = dict(os.environ)
    env["AMS_REQUIRE_ENCRYPTION"] = "1"
    env.pop("AMS_DATADIR_ENCRYPTED", None)
    env.pop("AMS_DB_KEY", None)
    env["AMS_DATA_DIR"] = str(tmp_path)
    # Must refuse to import (start) when encryption is required but not asserted.
    r = subprocess.run(["python", "-c", "import config"], cwd=backend, env=env,
                       capture_output=True, text=True)
    assert r.returncode != 0
    assert "REQUIRE_ENCRYPTION" in (r.stderr + r.stdout)
    # Asserting an encrypted volume lets it start.
    env["AMS_DATADIR_ENCRYPTED"] = "1"
    r2 = subprocess.run(["python", "-c", "import config; print('ok')"], cwd=backend, env=env,
                        capture_output=True, text=True)
    assert r2.returncode == 0 and "ok" in r2.stdout


# ── W2-C: cover letter is language- AND tone-aware (was German-only/flat) ──────
def test_cover_letter_language_and_tone():
    from cv.cover_letter import generate, CoverLetterRequest
    en_formal = generate(CoverLetterRequest(full_name="A B", job_title="Cook",
                                            language="en", tone="formal")).text
    en_friendly = generate(CoverLetterRequest(full_name="A B", job_title="Cook",
                                              language="en", tone="friendly")).text
    # English letter must use an English salutation/closing, not the German one.
    assert "Sehr geehrte" not in en_formal and "Mit freundlichen" not in en_formal
    assert "Dear Sir or Madam" in en_formal and "Yours faithfully" in en_formal
    # Tones must actually differ now (friendly uses different salutation + closing).
    assert "Hello" in en_friendly and "Best regards" in en_friendly
    assert "Dear Sir or Madam" not in en_friendly


# ── W2-C: anonymised CV export (anti-discrimination) ──────────────────────────
def test_anonymise_cv_redacts_identity():
    from app import _anonymise_cv
    from cv.models import CVData, CVIdentity
    cv = CVData(session_id="s", user_id="u", interview_path="other", language_input="de")
    cv.identity = CVIdentity(full_name="Maria Huber", location="Wien",
                             date_of_birth="1990-01-01", nationality="AT", photo="data:...")
    anon = _anonymise_cv(cv)
    assert anon.identity.full_name == "M. H."
    assert anon.identity.photo is None
    assert anon.identity.date_of_birth is None
    assert anon.identity.nationality is None
    # Original is untouched.
    assert cv.identity.full_name == "Maria Huber" and cv.identity.photo == "data:..."


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
