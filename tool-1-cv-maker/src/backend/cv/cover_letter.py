"""
Cover Letter Generator — template-based, fully offline.

Produces a short, professional German cover letter from CVData and an
optional job posting snippet. No AI / external API calls required.

Design goals
------------
- Three tone presets: formal (Sehr geehrte/r), friendly (Guten Tag), neutral
- Plugs in the candidate's strongest skills and experience automatically
- Injects matched job-description keywords for better ATS match
- Stays under one page (~300 words) by default
- Returns plain text; callers can wrap in PDF/DOCX as needed
"""

from __future__ import annotations

import logging
import re
import textwrap
from dataclasses import dataclass, field
from datetime import date
from typing import Optional

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# JD keyword extraction (reuses ATS bank)
# ---------------------------------------------------------------------------

def extract_jd_keywords(job_description: str) -> list[str]:
    """
    Extract ATS-relevant keywords from a job description string.

    Reuses the ATS keyword bank so the cover letter targets exactly
    the same terms that the ATS scoring layer tracks.

    Args:
        job_description: Raw text from the job ad.

    Returns:
        Deduplicated list of canonical keyword names found in the JD.
    """
    if not job_description:
        return []
    try:
        from polish.ats import extract_keywords
        return extract_keywords(job_description)
    except ImportError:
        # Fallback: simple word extraction if ats module unavailable
        words = re.findall(r'\b[A-Za-z][A-Za-z0-9+#.]{2,}\b', job_description)
        seen: set[str] = set()
        result: list[str] = []
        for w in words:
            if w.lower() not in seen:
                seen.add(w.lower())
                result.append(w)
        return result[:10]


# ── Templates ─────────────────────────────────────────────────────────────────

_SALUTATIONS = {
    "formal":   "Sehr geehrte Damen und Herren",
    "friendly": "Guten Tag",
    "neutral":  "Sehr geehrte Damen und Herren",
}

_CLOSING = {
    "formal":   "Mit freundlichen Grüßen",
    "friendly": "Mit freundlichen Grüßen",
    "neutral":  "Mit freundlichen Grüßen",
}

_OPENING_SENTENCES = [
    "Hiermit bewerbe ich mich um die ausgeschriebene Stelle.",
    "Mit großem Interesse habe ich Ihre Stellenausschreibung gelesen.",
    "Ich möchte mich mit dieser Bewerbung vorstellen.",
]

_SKILL_INTRO = {
    "de": "Zu meinen Stärken zählen",
    "en": "My key strengths include",
}

_EXPERIENCE_INTRO = {
    "de": "In meiner bisherigen Tätigkeit konnte ich Erfahrungen sammeln in den Bereichen",
    "en": "Through my previous work I gained experience in",
}

_MOTIVATION_PHRASE = {
    "de": (
        "Ich freue mich darauf, meine Fähigkeiten in Ihrem Unternehmen einzubringen "
        "und gemeinsam mit Ihrem Team erfolgreich zu arbeiten."
    ),
    "en": (
        "I look forward to bringing my skills to your organisation and working "
        "successfully with your team."
    ),
}


# ── Data structures ───────────────────────────────────────────────────────────

@dataclass
class CoverLetterRequest:
    """Input data for cover letter generation."""
    full_name: str
    location: str = ""
    job_title: str = ""           # Target position (from job ad or free text)
    employer_name: str = ""       # Target company
    skills: list[str] = field(default_factory=list)
    experience_snippets: list[str] = field(default_factory=list)  # 1–3 sentence summaries
    motivation_text: str = ""     # Optional extra motivation paragraph (German)
    tone: str = "formal"          # formal | friendly | neutral
    language: str = "de"          # de | en (output language)
    date_str: str = field(default_factory=lambda: date.today().strftime("%d.%m.%Y"))
    # Optional raw job description text — keywords are extracted and injected
    # into the letter body to improve ATS match rate.
    job_description: str = ""


@dataclass
class CoverLetter:
    """Generated cover letter."""
    text: str
    word_count: int
    language: str

    def to_dict(self) -> dict:
        return {
            "text": self.text,
            "word_count": self.word_count,
            "language": self.language,
        }


# ── Generator ─────────────────────────────────────────────────────────────────

def generate(req: CoverLetterRequest) -> CoverLetter:
    """
    Generate a cover letter from ``req``.

    Args:
        req: CoverLetterRequest with candidate data.

    Returns:
        CoverLetter with the rendered text and metadata.
    """
    lang = req.language if req.language in ("de", "en") else "de"
    tone = req.tone if req.tone in _SALUTATIONS else "formal"

    salutation = _SALUTATIONS[tone]
    closing = _CLOSING[tone]

    # Header block
    header_lines = [req.full_name]
    if req.location:
        header_lines.append(req.location)
    header_lines.append(req.date_str)
    header = "\n".join(header_lines)

    # Subject line
    if req.job_title and req.employer_name:
        subject = f"Bewerbung als {req.job_title} bei {req.employer_name}" if lang == "de" \
                  else f"Application for the position of {req.job_title} at {req.employer_name}"
    elif req.job_title:
        subject = f"Bewerbung als {req.job_title}" if lang == "de" \
                  else f"Application for {req.job_title}"
    else:
        subject = "Bewerbung" if lang == "de" else "Job Application"

    # Opening paragraph
    opening = _OPENING_SENTENCES[0]

    # Extract JD keywords and merge with candidate skills for better ATS match
    jd_keywords: list[str] = []
    if req.job_description:
        jd_keywords = extract_jd_keywords(req.job_description)
        logger.debug(f"JD keywords extracted: {jd_keywords}")

    # Merge: JD-matched keywords first (most relevant), then candidate skills
    merged_skills: list[str] = list(jd_keywords)
    for s in req.skills:
        if s not in merged_skills:
            merged_skills.append(s)

    # Skills paragraph
    skills_block = ""
    if merged_skills:
        top_skills = merged_skills[:6]
        skill_list = ", ".join(top_skills)
        intro = _SKILL_INTRO.get(lang, _SKILL_INTRO["de"])
        skills_block = f"{intro}: {skill_list}."

    # Experience paragraph
    exp_block = ""
    if req.experience_snippets:
        snippet = req.experience_snippets[0]  # use the strongest / first snippet
        intro = _EXPERIENCE_INTRO.get(lang, _EXPERIENCE_INTRO["de"])
        exp_block = f"{intro}: {snippet}"

    # Motivation paragraph
    if req.motivation_text:
        motivation = req.motivation_text
    else:
        motivation = _MOTIVATION_PHRASE.get(lang, _MOTIVATION_PHRASE["de"])

    # Assemble letter
    parts = [
        header,
        "",
        f"{salutation},",
        "",
        f"Betreff: {subject}" if lang == "de" else f"Re: {subject}",
        "",
        opening,
    ]

    body_paragraphs = [p for p in [skills_block, exp_block, motivation] if p]
    for para in body_paragraphs:
        parts.append("")
        parts.append(para)

    parts += [
        "",
        f"{closing},",
        req.full_name,
    ]

    text = "\n".join(parts)
    word_count = len(text.split())

    logger.debug(f"Cover letter generated: {word_count} words, language={lang}, tone={tone}")
    return CoverLetter(text=text, word_count=word_count, language=lang)


def generate_from_cv_data(cv_data, job_title: str = "", employer_name: str = "",
                          tone: str = "formal", language: str = "de") -> CoverLetter:
    """
    Convenience wrapper: build a CoverLetterRequest from a CVData object.

    Args:
        cv_data: CVData instance (from cv.models).
        job_title: Target job title from the job ad.
        employer_name: Target company name.
        tone: Letter tone preset.
        language: Output language ("de" or "en").

    Returns:
        CoverLetter.
    """
    # Extract identity fields
    full_name = ""
    location = ""
    if cv_data.identity:
        full_name = cv_data.identity.full_name or ""
        location = cv_data.identity.location or ""

    # Top skills
    skills = cv_data.all_skills[:8] if cv_data.all_skills else []

    # Experience snippets (use German or English depending on output language)
    snippets: list[str] = []
    for section in (cv_data.experience or [])[:3]:
        text = section.german if language == "de" else section.english
        if text:
            snippets.append(text)

    # Motivation text
    motivation = ""
    for m in (cv_data.motivation or [])[:1]:
        motivation = m.german if language == "de" else m.english

    req = CoverLetterRequest(
        full_name=full_name,
        location=location,
        job_title=job_title,
        employer_name=employer_name,
        skills=skills,
        experience_snippets=snippets,
        motivation_text=motivation,
        tone=tone,
        language=language,
    )
    return generate(req)
