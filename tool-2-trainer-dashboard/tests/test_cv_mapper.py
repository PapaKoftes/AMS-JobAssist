"""
Tests for services.cv_mapper — normalises Tool 1 export shapes to flat dict.
"""

import pytest
import sys
from pathlib import Path

# Ensure backend is importable when run without pip install
_BACKEND = Path(__file__).parent.parent / "src" / "backend"
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

from services.cv_mapper import normalise


# ── Shape A (default export: nested metadata + quality_metrics + content) ─────

SHAPE_A = {
    "metadata": {
        "exported_at": "2026-01-01T00:00:00",
        "export_format": "JSON",
        "export_version": "1.0",
        "session_id": 42,
        "user_id": "user_abc",
        "interview_path": "unemployed",
    },
    "quality_metrics": {
        "overall_quality": 0.75,
        "ready_for_export": True,
        "language_output_primary": "de",
        "language_output_secondary": "en",
    },
    "content": {
        "background": [{"text": "some background"}],
        "experience": [],
        "skills": [],
        "all_skills": ["Python", "SQL"],
        "motivation": [],
        "training": [],
        "projects": [],
    },
}


def test_shape_a_user_id():
    flat = normalise(SHAPE_A)
    assert flat["user_id"] == "user_abc"


def test_shape_a_interview_path():
    flat = normalise(SHAPE_A)
    assert flat["interview_path"] == "unemployed"


def test_shape_a_overall_quality():
    flat = normalise(SHAPE_A)
    assert flat["overall_quality"] == 0.75


def test_shape_a_ready_for_export():
    flat = normalise(SHAPE_A)
    assert flat["ready_for_export"] is True


def test_shape_a_language_primary():
    flat = normalise(SHAPE_A)
    assert flat["language_output_primary"] == "de"


def test_shape_a_content_preserved():
    flat = normalise(SHAPE_A)
    assert flat["all_skills"] == ["Python", "SQL"]
    assert len(flat["background"]) == 1


# ── Shape B (export_raw_cvdata: cvdata wrapper) ───────────────────────────────

SHAPE_B = {
    "metadata": {
        "exported_at": "2026-01-01T00:00:00",
        "export_format": "Raw CVData JSON",
    },
    "cvdata": {
        "session_id": "99",
        "user_id": "user_xyz",
        "interview_path": "career-switch",
        "overall_quality": 0.82,
        "ready_for_export": True,
        "language_output_primary": "de",
        "language_output_secondary": "en",
        "all_skills": ["Führerschein"],
    },
}


def test_shape_b_user_id():
    flat = normalise(SHAPE_B)
    assert flat["user_id"] == "user_xyz"


def test_shape_b_overall_quality():
    flat = normalise(SHAPE_B)
    assert flat["overall_quality"] == 0.82


def test_shape_b_metadata_not_overwritten():
    """export_format from top-level metadata should not clobber cvdata fields."""
    flat = normalise(SHAPE_B)
    assert flat["user_id"] == "user_xyz"  # cvdata value wins


# ── Shape C (flat / legacy) ───────────────────────────────────────────────────

SHAPE_C = {
    "user_id": "user_flat",
    "interview_path": "student",
    "overall_quality": 0.6,
    "ready_for_export": False,
    "language_output_primary": "de",
}


def test_shape_c_user_id():
    flat = normalise(SHAPE_C)
    assert flat["user_id"] == "user_flat"


def test_shape_c_passthrough():
    flat = normalise(SHAPE_C)
    assert flat["overall_quality"] == 0.6


# ── Error cases ───────────────────────────────────────────────────────────────

def test_rejects_non_dict():
    with pytest.raises(ValueError, match="JSON object"):
        normalise(["not", "a", "dict"])


def test_rejects_unrecognised_shape():
    with pytest.raises(ValueError, match="Unrecognised"):
        normalise({"something_random": 123})


def test_rejects_empty_dict():
    with pytest.raises(ValueError):
        normalise({})
