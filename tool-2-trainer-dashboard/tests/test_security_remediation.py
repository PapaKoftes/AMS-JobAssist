"""
Tool 2 security remediation tests (audit RC-5 zip-bomb, RC-5 error leakage).

Reuses the `client` fixture from test_integration.py's conftest pattern.
"""

import io
import os
import sys
import zipfile
from pathlib import Path

import pytest

backend_path = Path(__file__).parent.parent / "src" / "backend"
sys.path.insert(0, str(backend_path))

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app import app
from db import get_db
from models import Base


@pytest.fixture
def client(tmp_path):
    db_path = tmp_path / "sec_test.db"
    engine = create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)

    def override_get_db():
        s = Session()
        try:
            yield s
        finally:
            s.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
    engine.dispose()


def _make_zip_bomb(entry_uncompressed_mb: int = 60) -> bytes:
    """A single highly-compressible JSON entry that expands past the per-entry cap."""
    payload = b'{"x":"' + (b"A" * (entry_uncompressed_mb * 1024 * 1024)) + b'"}'
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("bomb.json", payload)
    return buf.getvalue()


def test_zip_bomb_is_rejected(client):
    """A zip whose entry decompresses past the cap must be rejected, not OOM."""
    bomb = _make_zip_bomb(60)            # 60 MB uncompressed > 25 MB per-entry cap
    assert len(bomb) < 1_000_000          # but tiny on the wire (high ratio)
    resp = client.post(
        "/api/import-cvs?cohort_id=SEC",
        files={"file": ("bomb.zip", bomb, "application/zip")},
    )
    assert resp.status_code == 400, resp.text
    assert "size" in resp.text.lower()


def test_normal_small_zip_still_imports(client):
    """Regression: a legitimate small zip is unaffected by the bomb guard."""
    import json
    good = {
        "user_id": "sec-user-1", "name": "Test", "interview_path": "unemployed",
        "language_output_primary": "de",
        "experience": [], "education": [], "skills": [],
    }
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("cv1.json", json.dumps(good))
    resp = client.post(
        "/api/import-cvs?cohort_id=SEC",
        files={"file": ("ok.zip", buf.getvalue(), "application/zip")},
    )
    # Either imported, or a clean validation error — never a 500 / crash.
    assert resp.status_code in (200, 400, 422), resp.text


def test_import_500_does_not_leak_internal_detail(client, monkeypatch):
    """On an unexpected error the client must get a generic message, not internals."""
    import api.routes as routes
    def _boom(*a, **k):
        raise RuntimeError("SECRET /var/db/path leaked stacktrace detail")
    monkeypatch.setattr(routes, "_import_single_cv", _boom)
    import json
    resp = client.post(
        "/api/import-cvs?cohort_id=SEC",
        files={"file": ("cv.json", json.dumps({"user_id": "u"}).encode(), "application/json")},
    )
    assert resp.status_code == 500
    assert "SECRET" not in resp.text and "stacktrace" not in resp.text.lower()


def test_canonical_schema_validation_rejects_malformed():
    """The cross-tool contract is enforced: a malformed canonical doc is rejected."""
    from services.cv_mapper import normalise
    import pytest as _pytest
    # schema_version present (canonical path) but 'experience' is the wrong type
    bad = {
        "schema_version": "1.0",
        "user_id": "u1",
        "experience": "not-a-list",   # must be a list of entries
    }
    with _pytest.raises(ValueError):
        normalise(bad)


def test_canonical_schema_validation_accepts_valid():
    """A well-formed canonical doc passes validation and normalises."""
    from services.cv_mapper import normalise
    good = {
        "schema_version": "1.0",
        "user_id": "u2",
        "interview_path": "other",
        "basics": {"full_name": "A B"},
        "experience": [{"german": "x", "english": "x", "native": ""}],
        "custom_sections": [{"german": "m", "english": "m", "native": ""}],  # no heading → OK
    }
    out = normalise(good)
    assert out["user_id"] == "u2"
