"""
Shared canonical CV schema — Pydantic v2 models used by both Tool 1 and Tool 2.

This module is the single source of truth for the data contract between the
two tools. Tool 1 exports to this shape; Tool 2 reads it.

Schema version: 1.0
"""

from __future__ import annotations

from datetime import date
from typing import Any, Optional

from pydantic import BaseModel, Field, field_validator


SCHEMA_VERSION = "1.0"


# ── Small building blocks ─────────────────────────────────────────────────────

class DateRange(BaseModel):
    """Inclusive date range for a work / education entry."""
    start: Optional[str] = None   # ISO 8601 partial date, e.g. "2020-03"
    end: Optional[str] = None     # None = present / ongoing


class LanguageProficiency(BaseModel):
    """A language the candidate speaks, with an optional CEFR level."""
    language: str                 # Human-readable name, e.g. "English"
    code: str = ""                # ISO 639-1 code, e.g. "en"
    level: str = ""               # CEFR: A1, A2, B1, B2, C1, C2, or "native"


# ── CV sections ───────────────────────────────────────────────────────────────

class Basics(BaseModel):
    """Top-level personal information."""
    full_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    date_of_birth: Optional[str] = None
    nationality: Optional[str] = None
    photo: Optional[str] = None   # Base-64 data URI or filesystem path; None = omit


class WorkEntry(BaseModel):
    """A single work-experience entry."""
    title: str = ""               # Job title / role
    employer: str = ""
    period: Optional[DateRange] = None
    # Polished prose in each language
    german: str = ""
    english: str = ""
    native: str = ""
    # ATS-friendly achievement bullets (language-agnostic or German)
    bullets: list[str] = Field(default_factory=list)
    detected_skills: list[str] = Field(default_factory=list)
    quality_score: float = 0.0
    hidden: bool = False          # Trainer can suppress a section without deleting it


class EducationEntry(BaseModel):
    """A single education / training entry."""
    degree: str = ""
    institution: str = ""
    period: Optional[DateRange] = None
    german: str = ""
    english: str = ""
    native: str = ""
    bullets: list[str] = Field(default_factory=list)
    quality_score: float = 0.0
    hidden: bool = False


class SkillGroup(BaseModel):
    """A group of skills (e.g. 'Software', 'Communication')."""
    label: str = ""
    skills: list[str] = Field(default_factory=list)


class CustomSection(BaseModel):
    """
    Flexible catch-all for sections that don't fit standard categories
    (e.g. volunteering, projects, publications).
    """
    heading: str = ""   # optional; a missing heading is recoverable (routes to motivation)
    german: str = ""
    english: str = ""
    native: str = ""
    bullets: list[str] = Field(default_factory=list)
    period: Optional[DateRange] = None
    quality_score: float = 0.0
    hidden: bool = False


# ── Root document ─────────────────────────────────────────────────────────────

class CVDocument(BaseModel):
    """
    Canonical CV document exchanged between Tool 1 and Tool 2.

    All fields are optional except ``schema_version`` and ``user_id`` so that
    partially-completed CVs can be serialised and imported at any stage.
    """

    schema_version: str = SCHEMA_VERSION
    user_id: str
    session_id: str = ""
    interview_path: str = ""      # unemployed | career-switch | student | pause | other

    # Language settings
    language_input: str = "de"           # Language user wrote in
    language_output_primary: str = "de"  # Primary export language (German)
    language_output_secondary: str = "en"
    language_output_native: Optional[str] = None

    # The job/role the participant is applying for (drives cover letter + ATS).
    target_job: str = ""

    # Personal info
    basics: Optional[Basics] = None

    # CV content
    experience: list[WorkEntry] = Field(default_factory=list)
    education: list[EducationEntry] = Field(default_factory=list)
    skills: list[SkillGroup] = Field(default_factory=list)
    languages: list[LanguageProficiency] = Field(default_factory=list)
    custom_sections: list[CustomSection] = Field(default_factory=list)

    # Aggregated skill list for quick lookup (raw, as the participant phrased them)
    all_skills: list[str] = Field(default_factory=list)

    # Canonical AMS-aligned skill labels, mapped from all_skills via the offline
    # skills taxonomy (data/knowledge/skills_taxonomy.json). Lets the trainer
    # dashboard aggregate cohorts by skill even when participants phrase the same
    # skill differently or in different languages ("Stapler"/"forklift"/"forklift
    # driving" → "Staplerschein/Gabelstapler"). Optional + additive: empty when
    # no normalization ran, so older CVs and the cross-tool contract stay valid.
    normalized_skills: list[str] = Field(default_factory=list)

    # Quality
    overall_quality: float = 0.0
    ready_for_export: bool = False

    # Timestamps (ISO 8601)
    created_at: str = ""
    completed_at: Optional[str] = None
    exported_at: Optional[str] = None

    @field_validator("schema_version")
    @classmethod
    def _check_version(cls, v: str) -> str:
        if v != SCHEMA_VERSION:
            import warnings
            warnings.warn(
                f"CV schema version mismatch: file is '{v}', reader expects '{SCHEMA_VERSION}'",
                stacklevel=4,
            )
        return v

    # ── Helpers ──────────────────────────────────────────────────────────────

    def visible_experience(self) -> list[WorkEntry]:
        return [e for e in self.experience if not e.hidden]

    def visible_education(self) -> list[EducationEntry]:
        return [e for e in self.education if not e.hidden]

    def visible_custom(self) -> list[CustomSection]:
        return [s for s in self.custom_sections if not s.hidden]
