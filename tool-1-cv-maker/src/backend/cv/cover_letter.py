"""
Cover Letter Generator — based on the AMS Bewerbungsschreiben Vorlage.

Structure (from Marko's template):
  Eigener Name / Adresse / Telefon / E-Mail       ← header block (right-aligned in Word)
  Firmenbezeichnung / Straße / PLZ Ort             ← recipient block
  Ort, Datum                                       ← date line
  Betreffzeile                                     ← subject line
  Sehr geehrte(r) …,                               ← salutation
  Bezugnahme auf Inserat / Einleitung              ← opening paragraph
  Qualifikationen, Berufspraxis, persönliche Fähigkeiten  ← body
  Gesprächsanfrage / Erreichbarkeit                ← closing paragraph
  Mit freundlichen Grüßen / Unterschrift           ← sign-off
  Anlagen: Lebenslauf, Zeugniskopien               ← attachments line

Design goals
------------
- Follows official Austrian Bewerbungsschreiben DIN 5008 layout
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
    """Extract ATS-relevant keywords from a job description string."""
    if not job_description:
        return []
    try:
        from polish.ats import extract_keywords
        return extract_keywords(job_description)
    except ImportError:
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

# Opening sentence that references the job ad (Bezugnahme auf Inserat)
_OPENING_DE = [
    "Mit großem Interesse habe ich Ihre Stellenausschreibung gelesen und bewerbe mich hiermit um die ausgeschriebene Stelle als {job_title}.",
    "Hiermit bewerbe ich mich auf Ihre Stellenanzeige für die Position {job_title} in Ihrem Unternehmen.",
    "Ihre Stellenausschreibung hat mein Interesse geweckt, und ich möchte mich als {job_title} bei Ihnen bewerben.",
]
_OPENING_BLIND_DE = "Ich bewerbe mich hiermit initiativ in Ihrem Unternehmen und biete meine Kenntnisse und Erfahrungen an."

_OPENING_EN = [
    "I am writing to apply for the position of {job_title} as advertised.",
    "I am very interested in the {job_title} role at your organisation and wish to apply.",
]
_OPENING_BLIND_EN = "I am writing to express my interest in joining your organisation."

# Gesprächsanfrage — invitation for an interview
_INTERVIEW_REQUEST_DE = (
    "Ich würde mich sehr freuen, meine Eignung in einem persönlichen Gespräch näherzubringen. "
    "Sie erreichen mich am besten telefonisch oder per E-Mail, um einen Termin zu vereinbaren."
)
_INTERVIEW_REQUEST_EN = (
    "I would welcome the opportunity to discuss my suitability in a personal interview. "
    "Please feel free to contact me by phone or e-mail to arrange a convenient time."
)

_ATTACHMENTS_DE = "Anlagen: Lebenslauf, Zeugniskopien"
_ATTACHMENTS_EN = "Enclosures: CV, copies of certificates"

_SKILL_INTRO = {
    "de": "Meine Stärken liegen insbesondere in",
    "en": "My key strengths lie particularly in",
}

_EXPERIENCE_INTRO = {
    "de": "In meiner bisherigen Berufspraxis konnte ich fundierte Erfahrungen sammeln in",
    "en": "Through my professional experience I have gained solid expertise in",
}

_MOTIVATION_PHRASE = {
    "de": (
        "Ich bin motiviert, meine Kenntnisse und Fähigkeiten in Ihrem Unternehmen einzubringen "
        "und aktiv zum Teamerfolg beizutragen."
    ),
    "en": (
        "I am motivated to contribute my skills and experience to your organisation "
        "and to actively support your team's success."
    ),
}


# ── Data structures ───────────────────────────────────────────────────────────

@dataclass
class CoverLetterRequest:
    """Input data for cover letter generation."""
    full_name: str
    address: str = ""           # Street address line
    city: str = ""              # City (Wohnort)
    phone: str = ""
    email: str = ""
    job_title: str = ""         # Target position (from job ad or free text)
    employer_name: str = ""     # Target company
    employer_address: str = ""  # Recipient address (optional)
    skills: list[str] = field(default_factory=list)
    experience_snippets: list[str] = field(default_factory=list)
    motivation_text: str = ""
    tone: str = "formal"        # formal | friendly | neutral
    language: str = "de"        # de | en (output language)
    date_str: str = field(default_factory=lambda: date.today().strftime("%d.%m.%Y"))
    job_description: str = ""   # Optional: JD text for keyword injection


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
    Generate a cover letter following the Austrian Bewerbungsschreiben Vorlage.

    Layout:
        [Absender-Block]         Eigener Name, Adresse, Telefon, E-Mail
        [Empfänger-Block]        Firmenbezeichnung, Adresse
        [Ort, Datum]
        [Betreff]                Bewerbung als …
        [Anrede]                 Sehr geehrte Damen und Herren,
        [Einleitung]             Bezugnahme auf Inserat
        [Hauptteil]              Qualifikationen / Berufspraxis / persönliche Fähigkeiten
        [Gesprächsanfrage]       Bitte um Vorstellungsgespräch
        [Abschluss]              Mit freundlichen Grüßen
        [Anlagen]                Lebenslauf, Zeugniskopien
    """
    lang = req.language if req.language in ("de", "en") else "de"
    tone = req.tone if req.tone in _SALUTATIONS else "formal"

    parts: list[str] = []

    # ── Absender-Block (sender header) ────────────────────────────────────────
    sender_lines = [req.full_name]
    if req.address:
        sender_lines.append(req.address)
    if req.city:
        sender_lines.append(req.city)
    if req.phone:
        sender_lines.append(req.phone)
    if req.email:
        sender_lines.append(req.email)
    parts.append("\n".join(sender_lines))
    parts.append("")

    # ── Empfänger-Block (recipient) ───────────────────────────────────────────
    if req.employer_name:
        recipient_lines = [req.employer_name]
        if req.employer_address:
            recipient_lines.append(req.employer_address)
        parts.append("\n".join(recipient_lines))
        parts.append("")

    # ── Ort, Datum ────────────────────────────────────────────────────────────
    if req.city:
        parts.append(f"{req.city}, {req.date_str}")
    else:
        parts.append(req.date_str)
    parts.append("")

    # ── Betreff (subject line) ────────────────────────────────────────────────
    if req.job_title and req.employer_name:
        if lang == "de":
            subject = f"Bewerbung als {req.job_title} bei {req.employer_name}"
        else:
            subject = f"Application for the position of {req.job_title} at {req.employer_name}"
    elif req.job_title:
        subject = f"Bewerbung als {req.job_title}" if lang == "de" else f"Application for {req.job_title}"
    else:
        subject = "Bewerbung" if lang == "de" else "Job Application"

    parts.append(subject)
    parts.append("")

    # ── Anrede (salutation) ───────────────────────────────────────────────────
    parts.append(f"{_SALUTATIONS[tone]},")
    parts.append("")

    # ── Einleitung / Bezugnahme auf Inserat ───────────────────────────────────
    if req.job_title:
        if lang == "de":
            opening = _OPENING_DE[0].format(job_title=req.job_title)
        else:
            opening = _OPENING_EN[0].format(job_title=req.job_title)
    else:
        opening = _OPENING_BLIND_DE if lang == "de" else _OPENING_BLIND_EN
    parts.append(opening)
    parts.append("")

    # ── Hauptteil: Qualifikationen, Berufspraxis, persönliche Fähigkeiten ─────
    # Extract JD keywords and merge with candidate skills
    jd_keywords: list[str] = []
    if req.job_description:
        jd_keywords = extract_jd_keywords(req.job_description)

    merged_skills = list(jd_keywords)
    for s in req.skills:
        if s not in merged_skills:
            merged_skills.append(s)

    if merged_skills:
        top_skills = merged_skills[:6]
        skill_list = ", ".join(top_skills)
        intro = _SKILL_INTRO.get(lang, _SKILL_INTRO["de"])
        parts.append(f"{intro}: {skill_list}.")
        parts.append("")

    if req.experience_snippets:
        snippet = req.experience_snippets[0]
        intro = _EXPERIENCE_INTRO.get(lang, _EXPERIENCE_INTRO["de"])
        parts.append(f"{intro}: {snippet}")
        parts.append("")

    # Motivation / persönliche Fähigkeiten
    motivation = req.motivation_text or _MOTIVATION_PHRASE.get(lang, _MOTIVATION_PHRASE["de"])
    parts.append(motivation)
    parts.append("")

    # ── Gesprächsanfrage ──────────────────────────────────────────────────────
    parts.append(_INTERVIEW_REQUEST_DE if lang == "de" else _INTERVIEW_REQUEST_EN)
    parts.append("")

    # ── Abschluss ─────────────────────────────────────────────────────────────
    parts.append(f"{_CLOSING[tone]},")
    parts.append("")
    parts.append(req.full_name)
    parts.append("")

    # ── Anlagen ───────────────────────────────────────────────────────────────
    parts.append(_ATTACHMENTS_DE if lang == "de" else _ATTACHMENTS_EN)

    text = "\n".join(parts)
    word_count = len(text.split())

    logger.debug(f"Cover letter generated: {word_count} words, language={lang}, tone={tone}")
    return CoverLetter(text=text, word_count=word_count, language=lang)


def generate_from_cv_data(cv_data, job_title: str = "", employer_name: str = "",
                          tone: str = "formal", language: str = "de") -> CoverLetter:
    """
    Convenience wrapper: build a CoverLetterRequest from a CVData object.
    """
    full_name = ""
    location = ""
    phone = ""
    email = ""

    if cv_data.identity:
        full_name = cv_data.identity.full_name or ""
        location = cv_data.identity.location or ""
        # CVIdentity stores these as contact_phone / contact_email (with
        # legacy phone/email as fallbacks for older serialised objects).
        phone = (getattr(cv_data.identity, "contact_phone", "")
                 or getattr(cv_data.identity, "phone", "") or "")
        email = (getattr(cv_data.identity, "contact_email", "")
                 or getattr(cv_data.identity, "email", "") or "")

    skills = cv_data.all_skills[:8] if cv_data.all_skills else []

    snippets: list[str] = []
    for section in (cv_data.experience or [])[:3]:
        text = section.german if language == "de" else section.english
        if text:
            snippets.append(text)

    motivation = ""
    for m in (cv_data.motivation or [])[:1]:
        motivation = m.german if language == "de" else m.english

    req = CoverLetterRequest(
        full_name=full_name,
        city=location,
        phone=phone,
        email=email,
        job_title=job_title,
        employer_name=employer_name,
        skills=skills,
        experience_snippets=snippets,
        motivation_text=motivation,
        tone=tone,
        language=language,
    )
    return generate(req)
