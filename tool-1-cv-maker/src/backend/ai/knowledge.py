"""
Austrian Job Knowledge Base — local RAG for CV polish and coaching.

Loads structured job data from data/knowledge/berufe.json and provides
retrieval functions for the polish engine and LLM prompts.

No external dependencies. Fully offline. ~25 common Austrian AMS jobs.
"""

import json
import logging
import re
from pathlib import Path
from typing import Optional, List, Dict

logger = logging.getLogger(__name__)

# Path to knowledge base (data/knowledge/). Frozen-aware: in a PyInstaller build
# Path(__file__) is unreliable for bundled assets, so use the bundle root where the
# spec ships data/knowledge/ (same pattern as skills/normalize.py).
import sys as _sys
if getattr(_sys, "frozen", False):
    _KNOWLEDGE_DIR = Path(getattr(_sys, "_MEIPASS", Path(_sys.executable).resolve().parent)) / "data" / "knowledge"
    if not (_KNOWLEDGE_DIR / "berufe.json").exists():
        _KNOWLEDGE_DIR = Path(_sys.executable).resolve().parent / "data" / "knowledge"
else:
    _KNOWLEDGE_DIR = Path(__file__).resolve().parents[3] / "data" / "knowledge"
_BERUFE_PATH = _KNOWLEDGE_DIR / "berufe.json"

_berufe: List[dict] = []   # loaded job entries
_loaded: bool = False


def _word_match(needle: str, haystack: str) -> bool:
    """Word-boundary aware substring check.

    Prevents short keywords like "it" from matching inside words like "with".
    Uses regex word boundaries for terms 3+ chars; exact word match for shorter.
    """
    if len(needle) <= 2:
        # Very short terms: require exact word match (space/start/end delimited)
        return bool(re.search(r'(?:^|\s)' + re.escape(needle) + r'(?:\s|$)', haystack))
    # Longer terms: standard word boundary
    return bool(re.search(r'\b' + re.escape(needle) + r'\b', haystack))


def _load():
    """Load the knowledge base from disk (once)."""
    global _berufe, _loaded
    if _loaded:
        return
    _loaded = True
    if not _BERUFE_PATH.exists():
        logger.warning(f"Knowledge base not found: {_BERUFE_PATH}")
        return
    try:
        with open(_BERUFE_PATH, "r", encoding="utf-8") as f:
            _berufe = json.load(f)
        logger.info(f"Loaded {len(_berufe)} job entries from knowledge base")
    except Exception as e:
        logger.error(f"Failed to load knowledge base: {e}")
        _berufe = []


def find_job(text: str) -> Optional[dict]:
    """
    Find the most relevant job entry for the given text.

    Uses keyword matching against job titles, keywords, and skills.
    Returns the best-matching job entry or None.

    Args:
        text: User's answer text, target job title, or any relevant text

    Returns:
        Best matching job entry dict, or None if no match found
    """
    _load()
    if not _berufe or not text:
        return None

    text_lower = text.lower()
    best_match = None
    best_score = 0

    for job in _berufe:
        score = 0
        # Check title match (highest weight)
        if job["title_de"].lower() in text_lower or text_lower in job["title_de"].lower():
            score += 10
        if job.get("title_en", "").lower() in text_lower:
            score += 8

        # Check keyword matches (word-boundary aware to avoid "it" matching "with")
        for kw in job.get("keywords", []):
            if _word_match(kw.lower(), text_lower):
                score += 3

        # Check skill mentions (word-boundary aware)
        for skill in job.get("skills", []):
            if _word_match(skill.lower(), text_lower):
                score += 2

        # Check verb matches (lower weight, word-boundary aware)
        for verb in job.get("verbs_de", []):
            if _word_match(verb.lower(), text_lower):
                score += 1

        if score > best_score:
            best_score = score
            best_match = job

    # Minimum threshold to avoid false matches
    return best_match if best_score >= 3 else None


def get_verbs_for_job(job_id_or_text: str, language: str = "de") -> List[str]:
    """
    Get strong CV verbs relevant to a specific job.

    Args:
        job_id_or_text: Job ID (e.g., "einzelhandel") or text to search
        language: "de" for German verbs, "en" for English

    Returns:
        List of strong verbs for the matched job, empty list if no match
    """
    _load()

    # Try direct ID match first
    for job in _berufe:
        if job["id"] == job_id_or_text:
            return job.get(f"verbs_{language}", job.get("verbs_de", []))

    # Fall back to text search
    job = find_job(job_id_or_text)
    if job:
        return job.get(f"verbs_{language}", job.get("verbs_de", []))
    return []


def get_skills_for_job(job_id_or_text: str) -> List[str]:
    """Get skills relevant to a specific job."""
    _load()

    for job in _berufe:
        if job["id"] == job_id_or_text:
            return job.get("skills", [])

    job = find_job(job_id_or_text)
    return job.get("skills", []) if job else []


def get_example_phrases(job_id_or_text: str) -> List[str]:
    """Get example CV phrases for a job."""
    _load()

    for job in _berufe:
        if job["id"] == job_id_or_text:
            return job.get("example_phrases_de", [])

    job = find_job(job_id_or_text)
    return job.get("example_phrases_de", []) if job else []


def get_context_for_prompt(text: str, category: str = "experience") -> str:
    """
    Build a knowledge context string for LLM prompts.

    Finds the most relevant job and returns a formatted string
    with verbs, skills, and examples that the LLM can use as reference.

    Args:
        text: The user's answer or job-related text
        category: CV category (experience, skills, background, etc.)

    Returns:
        Formatted context string, or empty string if no relevant knowledge found
    """
    _load()
    job = find_job(text)
    if not job:
        return ""

    parts = [f"Beruf: {job['title_de']}"]

    if category in ("experience", "motivation"):
        verbs = job.get("verbs_de", [])[:6]
        if verbs:
            parts.append(f"Starke Verben: {', '.join(verbs)}")
        examples = job.get("example_phrases_de", [])[:2]
        if examples:
            parts.append("Beispiele: " + " | ".join(examples))

    if category in ("skills", "experience"):
        skills = job.get("skills", [])[:5]
        if skills:
            parts.append(f"Relevante Fähigkeiten: {', '.join(skills)}")

    if category == "background":
        tasks = job.get("tasks_de", [])[:3]
        if tasks:
            parts.append(f"Typische Aufgaben: {', '.join(tasks)}")

    return "\n".join(parts)


def get_all_jobs() -> List[dict]:
    """Return all job entries (for admin/debug endpoints)."""
    _load()
    return [{"id": j["id"], "title_de": j["title_de"], "title_en": j.get("title_en", ""), "category": j.get("category", "")} for j in _berufe]


def get_job_categories() -> Dict[str, List[str]]:
    """Return jobs grouped by category."""
    _load()
    categories: Dict[str, List[str]] = {}
    for job in _berufe:
        cat = job.get("category", "other")
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(job["title_de"])
    return categories


def is_loaded() -> bool:
    """Check if the knowledge base is loaded."""
    _load()
    return len(_berufe) > 0


def get_stats() -> dict:
    """Return knowledge base statistics."""
    _load()
    total_verbs = sum(len(j.get("verbs_de", [])) for j in _berufe)
    total_skills = sum(len(j.get("skills", [])) for j in _berufe)
    total_examples = sum(len(j.get("example_phrases_de", [])) for j in _berufe)
    categories = set(j.get("category", "other") for j in _berufe)
    return {
        "jobs": len(_berufe),
        "categories": len(categories),
        "total_verbs": total_verbs,
        "total_skills": total_skills,
        "total_examples": total_examples,
        "loaded": _loaded and len(_berufe) > 0,
    }
