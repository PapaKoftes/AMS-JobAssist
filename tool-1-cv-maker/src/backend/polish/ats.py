"""
ATS Optimization Layer — rule-based keyword extraction and scoring.

Analyses polished CV text against a target job description (or a default
keyword bank) and returns an ATS compatibility score with actionable gaps.

Design goals
------------
- No external API calls — works fully offline
- Fast: < 20 ms per analysis on a standard laptop
- Transparent: every recommendation cites the exact keyword that's missing
"""

from __future__ import annotations

import re
import logging
from dataclasses import dataclass, field
from typing import Optional

logger = logging.getLogger(__name__)


# ── Keyword bank ──────────────────────────────────────────────────────────────
# A SEED of ~14 common terms, expanded at startup to ~51 groups via
# db_seed_expansion.apply_ats_expansion(). This is a curated, hand-built list —
# NOT the full ESCO taxonomy (~13k skills). The no-job-description score divides
# by the whole bank, so it is a rough heuristic; prefer scoring against a pasted
# job description (score_against_job) for a meaningful result.
# Keys are canonical terms; values are common synonyms/variants to also match.

ATS_KEYWORD_BANK: dict[str, list[str]] = {
    # Technical tools
    "Microsoft Excel": ["excel", "ms excel", "spreadsheet"],
    "Microsoft Word": ["word", "ms word"],
    "Microsoft Office": ["ms office", "office suite", "office paket"],
    "SAP": ["sap erp", "sap r/3"],
    "Python": ["python3"],
    "SQL": ["mysql", "postgresql", "sqlite", "t-sql"],
    # Soft skills
    "Teamarbeit": ["teamwork", "team player", "teamfähigkeit"],
    "Kommunikation": ["communication", "kommunikationsstärke"],
    "Führungserfahrung": ["leadership", "leitungserfahrung", "führungskompetenz"],
    "Projektmanagement": ["project management", "projektleitung"],
    "Kundenservice": ["customer service", "kundendienst", "kundenbetreuung"],
    # Work environment
    "Schichtarbeit": ["shift work", "wechselschicht"],
    "Führerschein": ["driver's licence", "driving licence", "fahrerlaubnis"],
    "Staplerschein": ["forklift", "gabelstapler"],
}


# ── Data structures ───────────────────────────────────────────────────────────

@dataclass
class ATSResult:
    """Result of an ATS compatibility analysis.

    ``score`` is a 0.0–1.0 fraction when a meaningful comparison was possible
    (i.e. a real job description was provided). It may be ``None`` for the
    no-job-description case, where a percentage against the generic IT-skewed
    keyword bank would be misleading rather than informative (see
    ``score_no_job_description``). Consumers should treat ``score is None`` as
    "qualitative feedback only — no numeric match available".
    """
    score: Optional[float]              # 0.0–1.0, or None when not applicable
    matched_keywords: list[str] = field(default_factory=list)
    missing_keywords: list[str] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)

    @property
    def grade(self) -> str:
        if self.score is None:
            # No numeric score (no job description) — qualitative-only result.
            return "Keine Bewertung"
        if self.score >= 0.80:
            return "Sehr gut"
        if self.score >= 0.60:
            return "Gut"
        if self.score >= 0.40:
            return "Ausreichend"
        return "Verbesserungsbedarf"

    def to_dict(self) -> dict:
        return {
            "score": round(self.score, 3) if self.score is not None else None,
            "grade": self.grade,
            "matched_keywords": self.matched_keywords,
            "missing_keywords": self.missing_keywords,
            "suggestions": self.suggestions,
        }


# ── Core analyser ─────────────────────────────────────────────────────────────

def _normalise(text: str) -> str:
    """Lower-case and collapse whitespace."""
    return re.sub(r"\s+", " ", text.lower().strip())


def _contains(haystack: str, needle: str) -> bool:
    """Word-boundary aware substring check (case-insensitive)."""
    pattern = r"\b" + re.escape(needle.lower()) + r"\b"
    return bool(re.search(pattern, haystack))


def extract_keywords(text: str) -> list[str]:
    """
    Extract ATS-relevant keywords from ``text`` using the built-in bank.

    Returns a deduplicated list of canonical keyword names found in the text.
    """
    normalised = _normalise(text)
    found: list[str] = []
    for canonical, synonyms in ATS_KEYWORD_BANK.items():
        all_forms = [canonical] + synonyms
        if any(_contains(normalised, form) for form in all_forms):
            found.append(canonical)
    return found


def score_against_job(cv_text: str, job_description: str) -> ATSResult:
    """
    Score ``cv_text`` against a specific ``job_description``.

    Extracts keywords from the job description first, then checks how many
    appear in the CV.

    Args:
        cv_text: Full CV text (any language).
        job_description: Job ad text pasted by the user.

    Returns:
        ATSResult with score and keyword gap analysis.
    """
    jd_lower = _normalise(job_description)
    cv_lower = _normalise(cv_text)

    # Find which bank keywords appear in the job description
    required: list[str] = []
    for canonical, synonyms in ATS_KEYWORD_BANK.items():
        all_forms = [canonical] + synonyms
        if any(_contains(jd_lower, form) for form in all_forms):
            required.append(canonical)

    if not required:
        # Job description doesn't mention any tracked keywords — generic bank score
        logger.debug("ATS: no tracked keywords in job description; falling back to bank score")
        return score_against_bank(cv_text)

    matched = [kw for kw in required if any(
        _contains(cv_lower, form)
        for form in [kw] + ATS_KEYWORD_BANK.get(kw, [])
    )]
    missing = [kw for kw in required if kw not in matched]

    score = len(matched) / len(required) if required else 1.0

    suggestions = [
        f"Füge '{kw}' oder ähnliche Formulierungen hinzu" for kw in missing[:5]
    ]

    return ATSResult(
        score=score,
        matched_keywords=matched,
        missing_keywords=missing,
        suggestions=suggestions,
    )


def validate_cv_structure(cv_data) -> list[str]:
    """
    Check structural ATS requirements on a CVData (or CVDocument) object.

    Returns a list of human-readable warnings. Empty list = structurally sound.

    Checks performed:
    - Experience entries have at least 2 bullets
    - No experience entry is too short (< 20 words)
    - Skills list is not empty
    - Important keywords appear somewhere in the document
    - Section presence: warns if key sections are missing

    Args:
        cv_data: Either a CVData (tool-1 internal model) or a dict with
                 ``experience``, ``all_skills`` etc. at the top level.

    Returns:
        List of warning strings. Empty = no structural issues.
    """
    warnings: list[str] = []

    # Normalise to dict for generic access
    if hasattr(cv_data, "to_dict"):
        data = cv_data.to_dict()
    elif hasattr(cv_data, "model_dump"):
        data = cv_data.model_dump()
    elif isinstance(cv_data, dict):
        data = cv_data
    else:
        return ["Cannot analyse structure: unknown cv_data type"]

    experience = data.get("experience", [])
    all_skills = data.get("all_skills", [])
    background = data.get("background", data.get("education", []))

    # ── Section presence ──────────────────────────────────────────────────────
    if not experience:
        warnings.append("Missing experience section — add at least one work entry")
    if not all_skills:
        warnings.append("No skills detected — mention specific tools, languages, or competencies")
    if not background:
        warnings.append("No background / education section — consider adding education history")

    # ── Experience entry depth ────────────────────────────────────────────────
    for i, entry in enumerate(experience, 1):
        # Handle both CVSection (dict with german/english) and WorkEntry (Pydantic)
        text = ""
        if isinstance(entry, dict):
            text = entry.get("german") or entry.get("english") or ""
            bullets = entry.get("bullets", [])
        else:
            text = getattr(entry, "german", "") or getattr(entry, "english", "")
            bullets = getattr(entry, "bullets", [])

        word_count = len(text.split()) if text else 0
        if word_count < 20:
            warnings.append(
                f"Experience entry {i} is too short ({word_count} words) — "
                "add daily tasks, tools used, or impact"
            )
        if len(bullets) < 2 and word_count < 40:
            warnings.append(
                f"Experience entry {i} lacks detail — "
                "add bullets or expand the description"
            )

    # ── Keyword placement ─────────────────────────────────────────────────────
    # Combine all experience text to check keyword density
    all_text = " ".join(
        (e.get("german", "") or e.get("english", "")) if isinstance(e, dict)
        else (getattr(e, "german", "") or getattr(e, "english", ""))
        for e in experience
    )
    found_keywords = extract_keywords(all_text)
    if experience and not found_keywords:
        warnings.append(
            "Experience section contains no recognised ATS keywords — "
            "mention specific tools, skills, or technologies"
        )

    # ── Length constraints ────────────────────────────────────────────────────
    total_words = len(all_text.split())
    if total_words > 800:
        warnings.append(
            f"CV content is very long ({total_words} words) — "
            "ATS systems prefer concise entries under 600 words"
        )

    return warnings


def score_against_bank(cv_text: str) -> ATSResult:
    """
    Score ``cv_text`` against the full built-in keyword bank.

    Useful when no specific job description is available.

    Args:
        cv_text: Full CV text (any language).

    Returns:
        ATSResult with score and keyword gap analysis.
    """
    cv_lower = _normalise(cv_text)
    all_keywords = list(ATS_KEYWORD_BANK.keys())

    matched = [kw for kw in all_keywords if any(
        _contains(cv_lower, form)
        for form in [kw] + ATS_KEYWORD_BANK.get(kw, [])
    )]
    missing = [kw for kw in all_keywords if kw not in matched]

    score = len(matched) / len(all_keywords) if all_keywords else 1.0

    suggestions = [
        f"Erwäge '{kw}' hinzuzufügen, wenn es zutrifft" for kw in missing[:5]
    ]

    return ATSResult(
        score=score,
        matched_keywords=matched,
        missing_keywords=missing,
        suggestions=suggestions,
    )


def score_no_job_description(cv_text: str) -> ATSResult:
    """
    Honest, encouraging ATS feedback when NO job description is available.

    The generic keyword bank is small (~14 seed terms, expanded to ~51) and
    IT-skewed. Dividing matched keywords by the WHOLE bank gives a solid
    trades/care/retail CV a demoralising ~10–15 % — a meaningless number for
    the AMS clientele, who mostly apply by human-read SME email rather than
    through an automated ATS.

    So instead of a misleading percentage, this returns ``score=None`` plus the
    keywords we *did* recognise and qualitative, encouraging guidance. Use
    ``score_against_job`` whenever a real job ad is pasted — that path still
    produces a meaningful keyword-match percentage.
    """
    matched = extract_keywords(cv_text)

    suggestions: list[str] = []
    if matched:
        joined = ", ".join(matched)
        suggestions.append(
            f"Gut erkannte Schlüsselbegriffe in Ihrem Lebenslauf: {joined}."
        )
    else:
        suggestions.append(
            "Nennen Sie konkrete Tätigkeiten, Werkzeuge und Programme, mit "
            "denen Sie arbeiten — das macht Ihren Lebenslauf greifbarer."
        )
    suggestions.append(
        "Für eine gezielte Auswertung fügen Sie eine konkrete Stellenanzeige "
        "ein. Dann vergleichen wir Ihren Lebenslauf direkt mit den dort "
        "geforderten Begriffen."
    )

    # score=None → no misleading percentage; grade resolves to "Keine Bewertung".
    return ATSResult(
        score=None,
        matched_keywords=matched,
        missing_keywords=[],
        suggestions=suggestions,
    )
