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


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
