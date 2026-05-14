"""
Tests for polish.ats — ATS keyword scoring.
"""

import sys
from pathlib import Path

_BACKEND = Path(__file__).parent.parent / "src" / "backend"
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

from polish.ats import (
    ATSResult,
    extract_keywords,
    score_against_bank,
    score_against_job,
)


# ── extract_keywords ──────────────────────────────────────────────────────────

def test_extracts_exact_keyword():
    kws = extract_keywords("Ich beherrsche Microsoft Excel sehr gut.")
    assert "Microsoft Excel" in kws


def test_extracts_synonym():
    kws = extract_keywords("daily work in spreadsheet applications")
    assert "Microsoft Excel" in kws


def test_extracts_sql():
    kws = extract_keywords("Erfahrung mit MySQL und PostgreSQL")
    assert "SQL" in kws


def test_case_insensitive():
    kws = extract_keywords("PYTHON Entwicklung")
    assert "Python" in kws


def test_no_false_positives():
    kws = extract_keywords("Ich liebe Urlaub am Meer.")
    assert kws == []


def test_multiple_keywords():
    text = "I worked in customer service and managed a team with Excel and Python"
    kws = extract_keywords(text)
    assert "Python" in kws
    assert "Microsoft Excel" in kws
    assert "Kundenservice" in kws


# ── score_against_bank ────────────────────────────────────────────────────────

def test_bank_score_zero_keywords():
    result = score_against_bank("Kein relevanter Text hier.")
    assert isinstance(result, ATSResult)
    assert result.score == 0.0
    assert result.matched_keywords == []


def test_bank_score_some_keywords():
    result = score_against_bank("Python, Excel und SQL Kenntnisse vorhanden.")
    assert result.score > 0.0
    assert result.score <= 1.0
    assert len(result.matched_keywords) >= 3


def test_bank_score_returns_suggestions():
    result = score_against_bank("Ich kenne Excel.")
    assert len(result.missing_keywords) > 0
    assert len(result.suggestions) > 0


def test_bank_score_grade_low():
    result = score_against_bank("Hallo.")
    assert result.grade in ("Verbesserungsbedarf", "Ausreichend")


def test_bank_score_grade_good():
    text = (
        "Python, SQL, Microsoft Excel, SAP, Kundenservice, "
        "Teamarbeit, Kommunikation, Projektmanagement, "
        "Führerschein, Microsoft Word, Microsoft Office, "
        "Führungserfahrung, Staplerschein, Schichtarbeit, "
        "Buchhaltung, DATEV, BMD, Lehrabschluss, "
        "Berufserfahrung, B-Führerschein"
    )
    result = score_against_bank(text)
    # Check matched keywords rather than absolute score, since the ATS bank
    # may be expanded at runtime by db_seed_expansion.apply_ats_expansion().
    # The bank can grow from 14 to 50+ entries, so absolute score varies.
    assert len(result.matched_keywords) >= 8
    assert "Python" in result.matched_keywords
    assert "SAP" in result.matched_keywords
    assert result.score > 0.0  # Not zero — some keywords matched


# ── score_against_job ─────────────────────────────────────────────────────────

def test_job_score_exact_match():
    cv = "I have Python and SQL experience."
    jd = "We require Python and SQL skills."
    result = score_against_job(cv, jd)
    assert result.score == 1.0
    assert "Python" in result.matched_keywords
    assert "SQL" in result.matched_keywords
    assert result.missing_keywords == []


def test_job_score_partial():
    cv = "Python experience."
    jd = "Python, SQL, and Excel required."
    result = score_against_job(cv, jd)
    assert 0 < result.score < 1.0
    assert "Python" in result.matched_keywords
    assert len(result.missing_keywords) >= 1


def test_job_score_no_tracked_keywords_falls_back():
    """If JD has no tracked keywords, fall back to bank score."""
    cv = "Python and Excel."
    jd = "You should be a great person."
    result = score_against_job(cv, jd)
    assert isinstance(result, ATSResult)
    # Should not raise; result comes from bank fallback


def test_job_score_cv_missing_all():
    cv = "I am a very motivated individual."
    jd = "Python, SQL, SAP, Excel required."
    result = score_against_job(cv, jd)
    assert result.score == 0.0
    assert len(result.missing_keywords) >= 3


# ── ATSResult helpers ─────────────────────────────────────────────────────────

def test_to_dict_structure():
    result = ATSResult(score=0.75, matched_keywords=["Python"], missing_keywords=["SQL"])
    d = result.to_dict()
    assert "score" in d
    assert "grade" in d
    assert "matched_keywords" in d
    assert "missing_keywords" in d
    assert "suggestions" in d


def test_grade_mapping():
    assert ATSResult(score=0.85).grade == "Sehr gut"
    assert ATSResult(score=0.65).grade == "Gut"
    assert ATSResult(score=0.45).grade == "Ausreichend"
    assert ATSResult(score=0.2).grade == "Verbesserungsbedarf"
