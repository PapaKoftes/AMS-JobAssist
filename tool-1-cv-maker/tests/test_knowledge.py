"""
Tests for ai.knowledge — Austrian Job Knowledge Base (local RAG).

Tests cover:
1.  Knowledge base loads correctly (25 jobs)
2.  find_job("Kellner") finds the waiter job
3.  find_job("Sales") finds a retail job
4.  find_job("IT") finds IT-Techniker
5.  find_job("asdfghjkl") returns None (no false positives)
6.  get_verbs_for_job("kellner", "de") returns German verbs
7.  get_verbs_for_job("kellner", "en") returns English verbs
8.  get_skills_for_job("koch") returns cooking skills
9.  get_context_for_prompt("Ich war Kellner", "experience") contains verbs and examples
10. get_context_for_prompt("random text", "experience") returns empty string
11. get_all_jobs() returns 25 entries
12. get_job_categories() returns dict with 8 categories
13. get_stats() returns correct totals
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src" / "backend"))

from ai.knowledge import (
    find_job,
    get_all_jobs,
    get_context_for_prompt,
    get_job_categories,
    get_skills_for_job,
    get_stats,
    get_verbs_for_job,
    is_loaded,
)


# ── 1. Loading ───────────────────────────────────────────────────────────────

def test_knowledge_base_loads():
    """Knowledge base loads 25 Austrian job entries from berufe.json."""
    assert is_loaded()
    stats = get_stats()
    assert stats["jobs"] == 25
    assert stats["loaded"] is True


# ── 2-5. find_job — positive and negative matches ───────────────────────────

def test_find_job_kellner():
    """find_job('Kellner') returns the waiter job entry."""
    job = find_job("Kellner")
    assert job is not None
    assert job["id"] == "kellner"
    assert job["title_en"] == "Waiter/Waitress"


def test_find_job_sales():
    """find_job('Sales') finds a retail-related job."""
    job = find_job("Sales")
    assert job is not None
    # 'sales' is a keyword on einzelhandel (Retail Salesperson)
    assert job["id"] == "einzelhandel"


def test_find_job_it():
    """find_job('IT') finds IT-Techniker."""
    job = find_job("IT")
    assert job is not None
    assert job["id"] == "it_techniker"
    assert "IT" in job["title_de"]


def test_find_job_gibberish_returns_none():
    """find_job('asdfghjkl') returns None — no false positives."""
    job = find_job("asdfghjkl")
    assert job is None


# ── 6-7. get_verbs_for_job — German and English verbs ───────────────────────

def test_get_verbs_for_job_german():
    """get_verbs_for_job('kellner', 'de') returns German verbs."""
    verbs = get_verbs_for_job("kellner", "de")
    assert isinstance(verbs, list)
    assert len(verbs) > 0
    # Kellner German verbs include 'serviert'
    assert "serviert" in verbs


def test_get_verbs_for_job_english():
    """get_verbs_for_job('kellner', 'en') returns English verbs."""
    verbs = get_verbs_for_job("kellner", "en")
    assert isinstance(verbs, list)
    assert len(verbs) > 0
    assert "served" in verbs


# ── 8. get_skills_for_job ───────────────────────────────────────────────────

def test_get_skills_for_job_koch():
    """get_skills_for_job('koch') returns cooking-related skills."""
    skills = get_skills_for_job("koch")
    assert isinstance(skills, list)
    assert len(skills) > 0
    # Koch skills include HACCP and Speisenzubereitung
    skills_lower = [s.lower() for s in skills]
    assert any("haccp" in s for s in skills_lower)
    assert any("speisenzubereitung" in s for s in skills_lower)


# ── 9-10. get_context_for_prompt ─────────────────────────────────────────────

def test_get_context_for_prompt_kellner():
    """get_context_for_prompt('Ich war Kellner', 'experience') contains verbs and examples."""
    context = get_context_for_prompt("Ich war Kellner", "experience")
    assert isinstance(context, str)
    assert len(context) > 0
    # Should contain the job title
    assert "Kellner" in context
    # Should contain strong verbs section
    assert "Starke Verben" in context or "Verben" in context
    # Should contain example phrases section
    assert "Beispiele" in context


def test_get_context_for_prompt_no_match():
    """get_context_for_prompt with gibberish returns empty string."""
    context = get_context_for_prompt("xyzzy plugh qwfp", "experience")
    assert context == ""


# ── 11. get_all_jobs ─────────────────────────────────────────────────────────

def test_get_all_jobs_returns_25():
    """get_all_jobs() returns 25 entries with required fields."""
    jobs = get_all_jobs()
    assert isinstance(jobs, list)
    assert len(jobs) == 25
    # Each entry has the expected summary fields
    for job in jobs:
        assert "id" in job
        assert "title_de" in job
        assert "title_en" in job
        assert "category" in job


# ── 12. get_job_categories ───────────────────────────────────────────────────

def test_get_job_categories_returns_8():
    """get_job_categories() returns dict with 8 categories."""
    categories = get_job_categories()
    assert isinstance(categories, dict)
    assert len(categories) == 8
    # Known categories from berufe.json
    expected = {"handel", "buero", "gastro", "sozial", "transport", "handwerk", "technik", "produktion"}
    assert set(categories.keys()) == expected
    # Each category has at least one job
    for cat, jobs in categories.items():
        assert isinstance(jobs, list)
        assert len(jobs) >= 1


# ── 13. get_stats ────────────────────────────────────────────────────────────

def test_get_stats_totals():
    """get_stats() returns correct totals for the knowledge base."""
    stats = get_stats()
    assert stats["jobs"] == 25
    assert stats["categories"] == 8
    assert stats["total_verbs"] > 0
    assert stats["total_skills"] > 0
    assert stats["total_examples"] > 0
    assert stats["loaded"] is True
