"""
Integration Tests for AMS JobAssist Tool 2 - Trainer Dashboard

Tests the complete workflow:
Tool 1 Export → Tool 2 Import → Review → Approval → Export

Covers:
- Import (single, batch, invalid, duplicate)
- Participant listing with pagination
- Approval workflow (approve, reject, needs_changes)
- Metrics calculation
- Data integrity (special chars, large fields, missing fields)
- Input validation
- Audit logging via TrainerFeedback records
- End-to-end workflows
"""

import pytest
import json
import sys
import os
import tempfile
from pathlib import Path
from datetime import datetime

# Add src to path
backend_path = Path(__file__).parent.parent / "src" / "backend"
sys.path.insert(0, str(backend_path))
os.chdir(str(backend_path))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app import app
from db import get_db
from models import Base, Participant, CVSubmission, TrainerFeedback


# ========================================
# Fixtures
# ========================================

@pytest.fixture(scope="session")
def test_engine():
    """Create a temporary database engine for the test session."""
    temp_dir = tempfile.gettempdir()
    db_path = os.path.join(temp_dir, f"test_ams_trainer_{os.getpid()}.db")

    if os.path.exists(db_path):
        os.remove(db_path)

    engine = create_engine(
        f"sqlite:///{db_path}",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(engine)

    yield engine

    engine.dispose()
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
        except PermissionError:
            pass


@pytest.fixture(autouse=True)
def db_session(test_engine):
    """
    Create a fresh session for each test with automatic rollback.

    Uses a nested transaction so each test is fully isolated:
    changes are rolled back after each test.
    """
    connection = test_engine.connect()
    transaction = connection.begin()
    Session = sessionmaker(bind=connection)
    session = Session()

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db_session):
    """Create a test client with the test database session."""

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


# ========================================
# Sample Data
# ========================================

@pytest.fixture
def sample_cv():
    """Sample CVData from Tool 1 export."""
    return {
        "user_id": "test_user_001",
        "name": "Max Mustermann",
        "email": "max@example.com",
        "interview_path": "unemployed",
        "background": "I worked in manufacturing for 5 years managing teams",
        "experience": "Led team of 3, improved efficiency by 20%",
        "skills": "Microsoft Excel, German, English, Leadership",
        "education": "Gymnasium, Abitur",
        "languages": "German, English, Basic Spanish",
        "overall_quality": 0.82,
        "ready_for_export": True,
        "language_output_primary": "de",
        "language_output_secondary": "en",
    }


@pytest.fixture
def sample_cv_batch():
    """Multiple CVs for batch testing."""
    return [
        {
            "user_id": "batch_001",
            "name": "Anna Schmidt",
            "email": "anna@example.com",
            "interview_path": "career-switch",
            "overall_quality": 0.75,
            "ready_for_export": True,
        },
        {
            "user_id": "batch_002",
            "name": "Thomas Mueller",
            "email": "thomas@example.com",
            "interview_path": "unemployed",
            "overall_quality": 0.88,
            "ready_for_export": True,
        },
        {
            "user_id": "batch_003",
            "name": "Elena Rossi",
            "email": "elena@example.com",
            "interview_path": "student",
            "overall_quality": 0.79,
            "ready_for_export": True,
        },
    ]


# ========================================
# Import Tests
# ========================================

class TestImport:
    """Test CV import functionality."""

    def test_import_single_cv(self, client, sample_cv):
        response = client.post(
            "/api/import-cvs?cohort_id=Test-Cohort",
            files={"file": ("test.json", json.dumps(sample_cv), "application/json")},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["imported"] == 1
        assert "participant_id" in data

    def test_import_invalid_file_type(self, client):
        response = client.post(
            "/api/import-cvs?cohort_id=Test-Cohort",
            files={"file": ("test.txt", b"invalid content", "text/plain")},
        )
        assert response.status_code == 400

    def test_import_invalid_json(self, client):
        response = client.post(
            "/api/import-cvs?cohort_id=Test-Cohort",
            files={"file": ("test.json", b"not json{{{", "application/json")},
        )
        assert response.status_code == 400

    def test_import_missing_cohort(self, client, sample_cv):
        response = client.post(
            "/api/import-cvs",
            files={"file": ("test.json", json.dumps(sample_cv), "application/json")},
        )
        assert response.status_code in [400, 422]

    def test_import_duplicate_creates_new_version(self, client, sample_cv, db_session):
        # First import
        client.post(
            "/api/import-cvs?cohort_id=Test-Cohort",
            files={"file": ("cv.json", json.dumps(sample_cv), "application/json")},
        )
        # Second import
        resp = client.post(
            "/api/import-cvs?cohort_id=Test-Cohort",
            files={"file": ("cv.json", json.dumps(sample_cv), "application/json")},
        )
        assert resp.status_code == 200

        participant = db_session.query(Participant).filter_by(user_id="test_user_001").first()
        assert participant is not None
        submissions = db_session.query(CVSubmission).filter_by(participant_id=participant.id).all()
        assert len(submissions) == 2
        assert submissions[1].version == 2

    def test_import_missing_user_id(self, client):
        bad_cv = {"name": "No User ID", "overall_quality": 0.5}
        response = client.post(
            "/api/import-cvs?cohort_id=Test",
            files={"file": ("bad.json", json.dumps(bad_cv), "application/json")},
        )
        assert response.status_code == 500  # ValueError from _import_single_cv


# ========================================
# Participant Tests
# ========================================

class TestParticipants:
    """Test participant listing and retrieval."""

    def test_list_empty(self, client):
        response = client.get("/api/participants")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["items"] == []

    def test_list_after_import(self, client, sample_cv):
        client.post(
            "/api/import-cvs?cohort_id=Test",
            files={"file": ("cv.json", json.dumps(sample_cv), "application/json")},
        )
        response = client.get("/api/participants")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["name"] == "Max Mustermann"

    def test_get_detail(self, client, sample_cv):
        resp = client.post(
            "/api/import-cvs?cohort_id=Test",
            files={"file": ("cv.json", json.dumps(sample_cv), "application/json")},
        )
        pid = resp.json()["participant_id"]

        detail = client.get(f"/api/participants/{pid}")
        assert detail.status_code == 200
        assert detail.json()["user_id"] == "test_user_001"

    def test_get_nonexistent(self, client):
        response = client.get("/api/participants/99999")
        assert response.status_code == 404

    def test_filter_by_cohort(self, client):
        cv1 = {"user_id": "u1", "overall_quality": 0.8, "ready_for_export": True}
        cv2 = {"user_id": "u2", "overall_quality": 0.9, "ready_for_export": True}

        client.post("/api/import-cvs?cohort_id=A", files={"file": ("cv.json", json.dumps(cv1))})
        client.post("/api/import-cvs?cohort_id=B", files={"file": ("cv.json", json.dumps(cv2))})

        response = client.get("/api/participants?cohort_id=A")
        data = response.json()
        assert data["total"] == 1

    def test_filter_by_status(self, client, sample_cv):
        resp = client.post(
            "/api/import-cvs?cohort_id=Test",
            files={"file": ("cv.json", json.dumps(sample_cv))},
        )
        pid = resp.json()["participant_id"]
        client.post(
            f"/api/participants/{pid}/approve",
            json={"approval_status": "approved", "feedback": "OK", "approved_by": "tester"},
        )

        pending = client.get("/api/participants?status=pending")
        approved = client.get("/api/participants?status=approved")

        assert pending.json()["total"] == 0
        assert approved.json()["total"] == 1

    def test_pagination(self, client):
        for i in range(5):
            cv = {"user_id": f"page_user_{i}", "overall_quality": 0.5}
            client.post("/api/import-cvs?cohort_id=PageTest", files={"file": ("cv.json", json.dumps(cv))})

        page1 = client.get("/api/participants?page=1&page_size=2")
        data1 = page1.json()
        assert data1["total"] == 5
        assert len(data1["items"]) == 2
        assert data1["page"] == 1
        assert data1["total_pages"] == 3

        page3 = client.get("/api/participants?page=3&page_size=2")
        data3 = page3.json()
        assert len(data3["items"]) == 1


# ========================================
# Approval Tests
# ========================================

class TestApproval:
    """Test approval workflow with audit logging."""

    def _import_and_get_id(self, client, cv=None):
        cv = cv or {"user_id": "approve_test", "overall_quality": 0.8}
        resp = client.post(
            "/api/import-cvs?cohort_id=ApprovalTest",
            files={"file": ("cv.json", json.dumps(cv))},
        )
        return resp.json()["participant_id"]

    def test_approve(self, client):
        pid = self._import_and_get_id(client)
        response = client.post(
            f"/api/participants/{pid}/approve",
            json={"approval_status": "approved", "feedback": "Good CV", "approved_by": "trainer1"},
        )
        assert response.status_code == 200
        assert response.json()["approval_status"] == "approved"

    def test_reject(self, client):
        pid = self._import_and_get_id(client, {"user_id": "reject_test", "overall_quality": 0.3})
        response = client.post(
            f"/api/participants/{pid}/approve",
            json={"approval_status": "rejected", "feedback": "Needs work", "approved_by": "trainer1"},
        )
        assert response.status_code == 200
        assert response.json()["approval_status"] == "rejected"

    def test_needs_changes(self, client):
        pid = self._import_and_get_id(client, {"user_id": "changes_test", "overall_quality": 0.6})
        response = client.post(
            f"/api/participants/{pid}/approve",
            json={"approval_status": "needs_changes", "feedback": "Add detail", "approved_by": "trainer1"},
        )
        assert response.status_code == 200
        assert response.json()["approval_status"] == "needs_changes"

    def test_invalid_status(self, client):
        pid = self._import_and_get_id(client, {"user_id": "invalid_status", "overall_quality": 0.5})
        response = client.post(
            f"/api/participants/{pid}/approve",
            json={"approval_status": "INVALID", "feedback": "test", "approved_by": "trainer1"},
        )
        assert response.status_code == 422  # Pydantic validation error

    def test_approval_creates_audit_record(self, client, db_session):
        pid = self._import_and_get_id(client, {"user_id": "audit_test", "overall_quality": 0.7})
        client.post(
            f"/api/participants/{pid}/approve",
            json={"approval_status": "approved", "feedback": "Audit check", "approved_by": "auditor"},
        )

        feedbacks = db_session.query(TrainerFeedback).filter_by(participant_id=pid).all()
        assert len(feedbacks) >= 1
        assert "approved" in feedbacks[-1].feedback_text

    def test_approve_nonexistent(self, client):
        response = client.post(
            "/api/participants/99999/approve",
            json={"approval_status": "approved", "feedback": "test", "approved_by": "trainer"},
        )
        assert response.status_code == 404

    def test_missing_approved_by(self, client):
        pid = self._import_and_get_id(client, {"user_id": "no_approver", "overall_quality": 0.5})
        response = client.post(
            f"/api/participants/{pid}/approve",
            json={"approval_status": "approved"},
        )
        assert response.status_code == 422  # Missing required field


# ========================================
# Metrics Tests
# ========================================

class TestMetrics:
    """Test cohort metrics calculations."""

    def test_empty_cohort(self, client):
        response = client.get("/api/cohorts/Empty/metrics")
        assert response.status_code == 200
        data = response.json()
        assert data["total_participants"] == 0
        assert data["completion_rate"] == "0%"

    def test_metrics_with_data(self, client):
        for i, status in enumerate(["approved", "pending", "rejected"]):
            cv = {"user_id": f"metric_{i}", "overall_quality": 0.5 + i * 0.15}
            resp = client.post(
                "/api/import-cvs?cohort_id=MetricTest",
                files={"file": ("cv.json", json.dumps(cv))},
            )
            if status != "pending":
                pid = resp.json()["participant_id"]
                client.post(
                    f"/api/participants/{pid}/approve",
                    json={"approval_status": status, "approved_by": "tester"},
                )

        response = client.get("/api/cohorts/MetricTest/metrics")
        data = response.json()
        assert data["total_participants"] == 3
        assert data["completed"] == 1  # Only "approved" counts


# ========================================
# Data Integrity Tests
# ========================================

class TestDataIntegrity:
    """Test data integrity and edge cases."""

    def test_special_characters(self, client, db_session):
        cv = {
            "user_id": "special_user",
            "name": "Müller-König äöü",
            "email": "test@example.de",
            "overall_quality": 0.75,
        }
        response = client.post(
            "/api/import-cvs?cohort_id=Test",
            files={"file": ("cv.json", json.dumps(cv))},
        )
        assert response.status_code == 200

    def test_minimal_cv(self, client):
        cv = {"user_id": "minimal", "overall_quality": 0.5, "ready_for_export": False}
        response = client.post(
            "/api/import-cvs?cohort_id=Test",
            files={"file": ("cv.json", json.dumps(cv))},
        )
        assert response.status_code == 200

    def test_large_text(self, client):
        cv = {"user_id": "large_text", "background": "x" * 5000, "overall_quality": 0.7}
        response = client.post(
            "/api/import-cvs?cohort_id=Test",
            files={"file": ("cv.json", json.dumps(cv))},
        )
        assert response.status_code == 200

    def test_quality_clamped(self, client, db_session):
        cv = {"user_id": "high_quality", "overall_quality": 99.9}
        client.post(
            "/api/import-cvs?cohort_id=Test",
            files={"file": ("cv.json", json.dumps(cv))},
        )
        sub = db_session.query(CVSubmission).filter_by(user_id="high_quality").first()
        assert sub is not None
        assert sub.overall_quality <= 1.0


# ========================================
# End-to-End Tests
# ========================================

class TestE2E:
    """End-to-end workflow tests."""

    def test_complete_workflow(self, client, sample_cv):
        # 1. Import
        resp = client.post(
            "/api/import-cvs?cohort_id=E2E",
            files={"file": ("cv.json", json.dumps(sample_cv))},
        )
        assert resp.status_code == 200
        pid = resp.json()["participant_id"]

        # 2. List
        list_resp = client.get("/api/participants?cohort_id=E2E")
        assert list_resp.json()["total"] == 1

        # 3. Detail
        detail = client.get(f"/api/participants/{pid}")
        assert detail.json()["status"] == "pending"

        # 4. Approve
        approve_resp = client.post(
            f"/api/participants/{pid}/approve",
            json={"approval_status": "approved", "feedback": "Excellent", "approved_by": "trainer"},
        )
        assert approve_resp.status_code == 200

        # 5. Verify
        final = client.get(f"/api/participants/{pid}")
        assert final.json()["status"] == "approved"

    def test_multi_participant_workflow(self, client, sample_cv_batch):
        pids = []
        for cv in sample_cv_batch:
            resp = client.post(
                "/api/import-cvs?cohort_id=BatchE2E",
                files={"file": ("cv.json", json.dumps(cv))},
            )
            pids.append(resp.json()["participant_id"])

        assert len(pids) == 3

        # Approve first, reject second, needs_changes third
        for pid, status in zip(pids, ["approved", "rejected", "needs_changes"]):
            client.post(
                f"/api/participants/{pid}/approve",
                json={"approval_status": status, "feedback": "test", "approved_by": "trainer"},
            )

        metrics = client.get("/api/cohorts/BatchE2E/metrics")
        data = metrics.json()
        assert data["total_participants"] == 3
        assert data["completed"] == 1


def _canonical_cv(user_id="canon_user"):
    """A canonical CVDocument as Tool 1 exports it (basics + typed section lists)."""
    return {
        "schema_version": "1.0",
        "user_id": user_id,
        "interview_path": "career-switch",
        "basics": {
            "full_name": "Canonical Tester",
            "location": "Wien",
            "email": "c@example.com",
            "phone": "+43 1 234",
        },
        "experience": [
            {"german": "Verkäufer bei BILLA, 2018-2023", "english": "Salesperson at BILLA", "native": ""},
        ],
        "education": [
            {"german": "Lehre Einzelhandel", "english": "Retail apprenticeship", "native": ""},
        ],
        "custom_sections": [
            {"german": "Motiviert für einen Neuanfang", "english": "Motivated for a fresh start", "native": ""},
        ],
        "all_skills": ["Kassenführung", "Kundenberatung"],
        "overall_quality": 0.6,
        "ready_for_export": True,
        "language_output_primary": "de",
    }


class TestCanonicalEdit:
    """Trainer inline edits must persist for canonical CVDocument imports."""

    def _import(self, client, cv):
        resp = client.post(
            "/api/import-cvs?cohort_id=CanonEdit",
            files={"file": ("cv.json", json.dumps(cv))},
        )
        assert resp.status_code == 200
        return resp.json()["participant_id"]

    def test_canonical_inline_edit_persists(self, client, db_session):
        pid = self._import(client, _canonical_cv())

        # Edit experience.0 (canonical list.index key) in German
        resp = client.patch(
            f"/api/participants/{pid}/cv-section",
            json={"question_id": "experience.0", "edited_text": "GEÄNDERT durch Trainer", "language": "de"},
        )
        assert resp.status_code == 200, resp.text

        # Verify it persisted into the canonical experience[0].german field
        sub = (
            db_session.query(CVSubmission)
            .filter(CVSubmission.participant_id == pid)
            .order_by(CVSubmission.version.desc())
            .first()
        )
        assert sub.cv_data_json["experience"][0]["german"] == "GEÄNDERT durch Trainer"
        assert sub.cv_data_json["experience"][0]["trainer_edited"] is True

    def test_canonical_edit_custom_section_english(self, client, db_session):
        pid = self._import(client, _canonical_cv("canon_user2"))
        resp = client.patch(
            f"/api/participants/{pid}/cv-section",
            json={"question_id": "custom_sections.0", "edited_text": "Edited motivation", "language": "en"},
        )
        assert resp.status_code == 200, resp.text
        sub = (
            db_session.query(CVSubmission)
            .filter(CVSubmission.participant_id == pid)
            .order_by(CVSubmission.version.desc())
            .first()
        )
        assert sub.cv_data_json["custom_sections"][0]["english"] == "Edited motivation"

    def test_canonical_edit_bad_index_404(self, client):
        pid = self._import(client, _canonical_cv("canon_user3"))
        resp = client.patch(
            f"/api/participants/{pid}/cv-section",
            json={"question_id": "experience.99", "edited_text": "x", "language": "de"},
        )
        assert resp.status_code == 404


class TestTrainerNotesAndName:
    """Phase B fixes: trainer notes must reload; canonical imports must show the
    participant's real name (basics.full_name), not the user_id placeholder."""

    def _import(self, client, cv):
        resp = client.post(
            "/api/import-cvs?cohort_id=PhaseB",
            files={"file": ("cv.json", json.dumps(cv))},
        )
        assert resp.status_code == 200, resp.text
        return resp.json()["participant_id"]

    def test_canonical_import_shows_real_name_and_email(self, client):
        """G2: name/email come from canonical basics, not the user_id fallback."""
        pid = self._import(client, _canonical_cv("u_realname"))
        detail = client.get(f"/api/participants/{pid}")
        assert detail.status_code == 200
        body = detail.json()
        assert body["name"] == "Canonical Tester", "must read basics.full_name, not user_id"
        assert body["email"] == "c@example.com"

    def test_trainer_notes_persist_and_reload(self, client):
        """G1: notes saved via approval must come back on the detail view."""
        pid = self._import(client, _canonical_cv("u_notes"))
        # Save trainer notes via the approval feedback field
        resp = client.post(
            f"/api/participants/{pid}/approve",
            json={"approval_status": "needs_changes",
                  "feedback": "Bitte Foto hinzufügen und Datum prüfen.",
                  "approved_by": "Marko"},
        )
        assert resp.status_code == 200, resp.text
        # Reload detail — notes must be present (was previously write-only)
        detail = client.get(f"/api/participants/{pid}")
        assert detail.status_code == 200
        assert detail.json()["trainer_notes"] == "Bitte Foto hinzufügen und Datum prüfen."


def _build_tool1_canonical_export():
    """Produce a REAL canonical CVDocument the way Tool 1 does: build a CVData
    with Tool 1's own dataclasses, then call to_canonical().model_dump(). This is
    the actual artifact that crosses the tool boundary — no hand-faked JSON."""
    import sys as _sys
    from pathlib import Path as _Path
    t1_backend = _Path(__file__).resolve().parents[3] / "tool-1-cv-maker" / "src" / "backend"
    if str(t1_backend) not in _sys.path:
        _sys.path.insert(0, str(t1_backend))
    from cv.models import CVData, CVSection, CVIdentity, QuestionCategory  # type: ignore

    cv = CVData(
        session_id="sess-e2e",
        user_id="fatima_y",
        interview_path="career-switch",
        language_input="de",
        target_job="Bürokauffrau",
        identity=CVIdentity(
            full_name="Fatima Yilmaz", location="Wien",
            contact_email="fatima@example.at", contact_phone="+43 660 1234567",
            nationality="Österreich",
        ),
        experience=[CVSection(
            german="Verkauf und Kassa bei BILLA", english="Sales and checkout at BILLA",
            native="", title="Verkäuferin", employer="BILLA",
            period={"start": "2019-03", "end": "2024-01"},
            category=QuestionCategory.EXPERIENCE, question_id="exp_1",
            quality_score=0.8, confidence_level="high",
        )],
        background=[CVSection(
            german="Lehre Einzelhandel abgeschlossen", english="Completed retail apprenticeship",
            native="", category=QuestionCategory.OTHER, question_id="edu_1",
            quality_score=0.7,
        )],
        skills=[CVSection(
            german="Kassenführung, Kundenberatung", english="Cash handling, customer advice",
            native="", category=QuestionCategory.SKILLS, question_id="skills_1",
            detected_skills=["Kassenführung", "Kundenberatung"], quality_score=0.7,
        )],
        all_skills=["Kassenführung", "Kundenberatung"],
        languages=[{"language": "Deutsch", "code": "de", "level": "C1"},
                   {"language": "Türkisch", "code": "tr", "level": "native"}],
        overall_quality=0.75,
        ready_for_export=True,
    )
    return cv.to_canonical().model_dump()


class TestCrossToolE2E:
    """The whole point: a CV built by Tool 1 must flow into Tool 2 and be fully
    usable. This drives Tool 1's REAL to_canonical() export → Tool 2 import →
    trainer review (real name, edit, notes, approve) → bulk PDF export."""

    def test_tool1_export_flows_through_tool2(self, client, db_session):
        canonical = _build_tool1_canonical_export()

        # 0. The export must satisfy the cross-tool contract (canonical schema).
        import sys as _sys
        from pathlib import Path as _Path
        repo = _Path(__file__).resolve().parents[3]
        if str(repo) not in _sys.path:
            _sys.path.insert(0, str(repo))
        from shared.schema.cv_schema import CVDocument  # type: ignore
        CVDocument.model_validate(canonical)  # raises if Tool 1 broke the contract
        assert canonical["basics"]["full_name"] == "Fatima Yilmaz"

        # 1. Trainer imports the participant's CV.
        r = client.post("/api/import-cvs?cohort_id=E2E-Real",
                        files={"file": ("fatima.json", json.dumps(canonical))})
        assert r.status_code == 200, r.text
        pid = r.json()["participant_id"]

        # 2. The dashboard shows the REAL name (not the user_id) — Phase B fix.
        detail = client.get(f"/api/participants/{pid}").json()
        assert detail["name"] == "Fatima Yilmaz"
        cv_json = detail["latest_submission"]["cv_data"]
        assert cv_json["experience"][0]["title"] == "Verkäuferin"
        assert cv_json["experience"][0]["employer"] == "BILLA"

        # 3. Trainer edits a section (canonical experience.0) — must persist.
        r = client.patch(f"/api/participants/{pid}/cv-section",
                         json={"question_id": "experience.0",
                               "edited_text": "Verkauf, Kassa und Lagerverwaltung bei BILLA",
                               "language": "de"})
        assert r.status_code == 200, r.text

        # 4. Trainer adds notes + approves — notes must reload (Phase B fix).
        r = client.post(f"/api/participants/{pid}/approve",
                        json={"approval_status": "approved",
                              "feedback": "Sehr gut. Foto noch ergänzen.",
                              "approved_by": "Marko"})
        assert r.status_code == 200, r.text
        detail2 = client.get(f"/api/participants/{pid}").json()
        assert detail2["status"] == "approved"
        assert detail2["trainer_notes"] == "Sehr gut. Foto noch ergänzen."
        assert "Lagerverwaltung" in detail2["latest_submission"]["cv_data"]["experience"][0]["german"]

        # 5. Trainer bulk-exports the approved CV as PDF — must produce a non-trivial file.
        r = client.post("/api/bulk-export",
                        json={"participant_ids": [pid], "format": "pdf", "language": "de"})
        assert r.status_code == 200, r.text
        assert len(r.content) > 1000  # a real zip with a real PDF inside


# ========================================
# Run
# ========================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
