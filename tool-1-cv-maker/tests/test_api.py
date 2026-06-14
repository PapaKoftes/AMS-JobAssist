"""
Tests for FastAPI endpoints (Phase 10.3).

Tests the REST API endpoints for:
- CV export (JSON, PDF, DOCX)
- CV metadata retrieval
- Health checks
"""

import pytest
from fastapi.testclient import TestClient
from app import app, ExportRequest
from cv.models import CVData, CVSection, QuestionCategory


@pytest.fixture
def client():
    """Provide TestClient for FastAPI app with lifespan (DB initialised)."""
    with TestClient(app) as c:
        yield c


class TestHealthCheck:
    """Test health check endpoint."""

    def test_health_check(self, client):
        """Test /health endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


class TestExportRequest:
    """Test export request model validation."""

    def test_export_request_requires_session_id(self):
        """Test ExportRequest requires session_id."""
        with pytest.raises(Exception):  # Pydantic validation error
            ExportRequest(language="de")

    def test_export_request_defaults_language(self):
        """Test ExportRequest defaults language to 'de'."""
        request = ExportRequest(session_id=1)
        assert request.language == "de"

    def test_export_request_allows_custom_filename(self):
        """Test ExportRequest allows optional custom filename."""
        request = ExportRequest(session_id=1, filename="my_cv")
        assert request.filename == "my_cv"


class TestCVMetadata:
    """Test CV metadata retrieval."""

    def test_get_cv_nonexistent_returns_404(self, client):
        """Test GET /api/cv/{session_id} returns 404 when not found."""
        response = client.get("/api/cv/999")
        assert response.status_code == 404


class TestJSONExport:
    """Test JSON export endpoint."""

    def test_json_export_nonexistent_returns_404(self, client):
        """Test POST /api/export/json returns 404 when CV not found."""
        response = client.post(
            "/api/export/json",
            json={"session_id": 999, "language": "de"}
        )
        assert response.status_code == 404

    def test_json_export_request_validation(self, client):
        """Test POST /api/export/json requires session_id."""
        response = client.post(
            "/api/export/json",
            json={"language": "de"}  # Missing session_id
        )
        assert response.status_code == 422  # Validation error


class TestPDFExport:
    """Test PDF export endpoint."""

    def test_pdf_export_nonexistent_returns_404(self, client):
        """Test POST /api/export/pdf returns 404 when CV not found."""
        response = client.post(
            "/api/export/pdf",
            json={"session_id": 999, "language": "de"}
        )
        assert response.status_code == 404

    def test_pdf_export_request_validation(self, client):
        """Test POST /api/export/pdf requires session_id."""
        response = client.post(
            "/api/export/pdf",
            json={"language": "de"}  # Missing session_id
        )
        assert response.status_code == 422  # Validation error


class TestDOCXExport:
    """Test DOCX export endpoint."""

    def test_docx_export_nonexistent_returns_404(self, client):
        """Test POST /api/export/docx returns 404 when CV not found."""
        response = client.post(
            "/api/export/docx",
            json={"session_id": 999, "language": "de"}
        )
        assert response.status_code == 404

    def test_docx_export_request_validation(self, client):
        """Test POST /api/export/docx requires session_id."""
        response = client.post(
            "/api/export/docx",
            json={"language": "de"}  # Missing session_id
        )
        assert response.status_code == 422  # Validation error


class TestAmsJobSearch:
    """The AMS job-search deep-link endpoint (offline, no transmission)."""

    def test_builds_prefilled_link(self, client):
        r = client.get("/api/jobs/ams-search",
                       params={"target_job": "ich suche als Verkäuferin", "location": "1150 Wien"})
        assert r.status_code == 200
        data = r.json()["data"]
        assert data["url"].startswith("https://jobs.ams.at/")
        assert data["occupation"] == "Verkäuferin"  # filler stripped
        assert data["location"] == "Wien"            # PLZ stripped
        # the URL must be encoded (no raw spaces)
        assert " " not in data["url"]

    def test_empty_target_returns_bare_portal(self, client):
        r = client.get("/api/jobs/ams-search")
        assert r.status_code == 200
        data = r.json()["data"]
        assert data["url"].startswith("https://jobs.ams.at/")
        assert data["occupation"] == ""

    def test_no_network_is_made(self, client):
        # The endpoint must never need network — it works under the offline block.
        # (If it tried to fetch, the call would error; a 200 proves it's link-only.)
        r = client.get("/api/jobs/ams-search", params={"target_job": "Koch"})
        assert r.status_code == 200

    def test_suggested_occupation_is_non_destructive(self, client):
        # A colloquial/typo term gets a canonical "also search as" suggestion, but
        # the URL still uses the user's OWN term (suggestion is additive only).
        r = client.get("/api/jobs/ams-search", params={"target_job": "Programmierer"})
        data = r.json()["data"]
        assert data["occupation"] == "Programmierer"          # user's term preserved
        assert "Programmierer" in data["url"] or "programmierer" in data["url"].lower()
        assert data.get("suggested_occupation") == "Softwareentwickler/in (Programmierer/in)"


class TestBewerbungsCheck:
    """Test the /api/cv/check hire-readiness endpoint + its CVData mapper."""

    def test_check_nonexistent_returns_404(self, client):
        r = client.post("/api/cv/check", json={"session_id": 999999})
        assert r.status_code == 404

    def test_check_requires_session_id(self, client):
        r = client.post("/api/cv/check", json={"job_description": "x"})
        assert r.status_code == 422  # pydantic validation

    def test_mapper_flattens_cvdata(self):
        from app import _cv_data_to_check_dict
        from cv.models import CVData, CVSection, CVIdentity, QuestionCategory
        cv = CVData(
            session_id="1", user_id="u", interview_path="unemployed", language_input="de",
            identity=CVIdentity(full_name="Leyla Demir", contact_phone="0660 1",
                                contact_email="l@x.at", location="Wien", photo="data:image/png;base64,AAA"),
            experience=[CVSection(german="Verkäuferin, 150 Kunden/Tag", english="", native="",
                                  category=QuestionCategory.EXPERIENCE)],
            background=[CVSection(german="Lehre Einzelhandel", english="", native="",
                                  category=QuestionCategory.BACKGROUND)],
            all_skills=["Kassa", "Excel", "Kundenberatung"],
            languages=[{"language": "Deutsch", "code": "de", "level": "B2"}],
            target_job="Bürokauffrau",
        )
        d = _cv_data_to_check_dict(cv)
        assert d["name"] == "Leyla Demir"
        assert d["phone"] and d["email"] and d["city"] == "Wien"
        assert d["photo"] is True
        assert d["target_job"] == "Bürokauffrau"
        assert "Verkäuferin" in d["experiences"][0]
        assert d["education"] == ["Lehre Einzelhandel"]
        assert d["skills"] == ["Kassa", "Excel", "Kundenberatung"]
        assert "Verkäuferin" in d["all_text"] and "Deutsch B2" in d["all_text"]
        # and that mapped dict produces a high hire-readiness score
        from polish.cv_check import analyze_cv
        assert analyze_cv(d)["percent"] >= 70

    def test_mapper_skills_fallback_to_section_text(self):
        from app import _cv_data_to_check_dict
        from cv.models import CVData, CVSection, QuestionCategory
        cv = CVData(session_id="1", user_id="u", interview_path="unemployed", language_input="de",
                    skills=[CVSection(german="Teamfähig", english="", native="",
                                      category=QuestionCategory.SKILLS)])
        d = _cv_data_to_check_dict(cv)
        assert d["skills"] == ["Teamfähig"]  # used section text when all_skills empty


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
