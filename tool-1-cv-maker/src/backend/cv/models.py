"""
CV Data Models - Multilingual CV data structures.

Handles:
1. Multilingual CV section storage (German, English, native)
2. Complete CV data assembly
3. Skill extraction and normalization
4. Language metadata tracking
5. JSON serialization for export
"""

import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, fields, asdict
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class QuestionCategory(str, Enum):
    """Interview question categories."""
    IDENTITY = "identity"
    BACKGROUND = "background"
    EXPERIENCE = "experience"
    SKILLS = "skills"
    MOTIVATION = "motivation"
    TRAINING = "training"
    PROJECTS = "projects"
    OTHER = "general"


@dataclass
class MultilingualText:
    """Text in multiple languages."""
    german: str  # Primary output language
    english: str  # Secondary output language
    native: str  # User's detected native language (optional)

    def to_dict(self) -> Dict[str, str]:
        """Convert to dictionary."""
        return asdict(self)

    def get_language(self, lang_code: str) -> Optional[str]:
        """Get text for specific language code."""
        if lang_code == "de":
            return self.german
        elif lang_code == "en":
            return self.english
        else:
            return self.native if self.native else self.english


@dataclass
class CVSection:
    """
    A section of the CV with multilingual content.

    Represents a single user answer/experience/skill with polished versions
    in German, English, and user's native language.
    """
    # Content
    german: str  # Polished German version
    english: str  # Polished English version
    native: str  # Polished version in user's native language

    # Structured content (ATS-friendly bullet points)
    bullets: List[str] = field(default_factory=list)  # Achievement bullets (lang-agnostic)

    # Date range for experience/education entries
    period: Optional[Dict[str, Optional[str]]] = None  # {"start": "2020-01", "end": "2023-03"} or None

    # Metadata
    category: QuestionCategory = QuestionCategory.OTHER  # Section category
    question_id: str = ""  # Original question ID
    detected_input_language: str = "de"  # Language user actually wrote in (ISO 639-1)
    user_native_language: str = "de"  # User's detected native language

    # Quality metrics
    quality_score: float = 0.0  # 0.0-1.0
    confidence_level: str = "low"  # low, medium, high
    detected_skills: List[str] = field(default_factory=list)  # Extracted/normalized skills

    # Visibility flag — allows trainer to hide a section without deleting it
    hidden: bool = False

    # Explainability — list of transformations applied during polishing.
    # e.g. ["Replaced weak verb 'did' → 'executed'", "Identified skill: 'Python'"]
    # Empty list means no changes were tracked (legacy data).
    changes: List[str] = field(default_factory=list)

    # Timestamps
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    polished_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "german": self.german,
            "english": self.english,
            "native": self.native,
            "bullets": self.bullets,
            "period": self.period,
            "category": self.category.value,
            "question_id": self.question_id,
            "detected_input_language": self.detected_input_language,
            "user_native_language": self.user_native_language,
            "quality_score": self.quality_score,
            "confidence_level": self.confidence_level,
            "detected_skills": self.detected_skills,
            "hidden": self.hidden,
            "changes": self.changes,
            "created_at": self.created_at,
            "polished_at": self.polished_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CVSection":
        """Create from dictionary. Tolerates missing optional fields for backward compat."""
        data = data.copy()
        if isinstance(data.get("category"), str):
            try:
                data["category"] = QuestionCategory(data["category"])
            except ValueError:
                data["category"] = QuestionCategory.OTHER
        # Strip unknown keys so old serialised data doesn't crash the constructor
        known = {f.name for f in cls.__dataclass_fields__.values()}
        data = {k: v for k, v in data.items() if k in known}
        return cls(**data)


@dataclass
class CVIdentity:
    """Personal identity section of CV."""
    full_name: str
    date_of_birth: Optional[str] = None
    nationality: Optional[str] = None
    languages_spoken: List[str] = field(default_factory=list)
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    location: Optional[str] = None
    # Optional path or URL to a profile photo (base64 data URI or filesystem path)
    photo: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class CVData:
    """
    Complete multilingual CV data.

    Represents a full CV in German, English, and user's native language,
    assembled from polished interview answers.
    """
    # Session info
    session_id: str
    user_id: str
    interview_path: str  # unemployed, career-switch, student, pause, other
    language_input: str  # Language user selected/detected for input
    language_output_primary: str = "de"  # German (primary)
    language_output_secondary: str = "en"  # English (secondary)
    language_output_native: Optional[str] = None  # User's native (tertiary)

    # Personal info
    identity: Optional[CVIdentity] = None

    # CV Sections (organized by category)
    background: List[CVSection] = field(default_factory=list)  # Background/education
    experience: List[CVSection] = field(default_factory=list)  # Work experience
    skills: List[CVSection] = field(default_factory=list)  # Skills
    motivation: List[CVSection] = field(default_factory=list)  # Motivation
    training: List[CVSection] = field(default_factory=list)  # Training/courses
    projects: List[CVSection] = field(default_factory=list)  # Projects

    # Extracted data
    all_skills: List[str] = field(default_factory=list)  # Normalized skills (deduplicated)
    detected_languages: List[str] = field(default_factory=list)  # Languages detected in input

    # Language proficiencies with CEFR levels (for CV language section)
    # Each entry: {"language": "English", "code": "en", "level": "C1"}
    # CEFR levels: A1, A2, B1, B2, C1, C2, "native"
    languages: List[Dict[str, str]] = field(default_factory=list)

    # Job target (used by AI chat coach and job-match feature)
    target_job: str = ""  # Job title or description user wants to match

    # Quality metrics
    overall_quality: float = 0.0  # Average quality score
    ready_for_export: bool = False  # Whether CV is complete enough to export

    # Timestamps
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    completed_at: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "interview_path": self.interview_path,
            "language_input": self.language_input,
            "language_output_primary": self.language_output_primary,
            "language_output_secondary": self.language_output_secondary,
            "language_output_native": self.language_output_native,
            "identity": self.identity.to_dict() if self.identity else None,
            "background": [s.to_dict() for s in self.background],
            "experience": [s.to_dict() for s in self.experience],
            "skills": [s.to_dict() for s in self.skills],
            "motivation": [s.to_dict() for s in self.motivation],
            "training": [s.to_dict() for s in self.training],
            "projects": [s.to_dict() for s in self.projects],
            "all_skills": self.all_skills,
            "detected_languages": self.detected_languages,
            "languages": self.languages,
            "target_job": self.target_job,
            "overall_quality": self.overall_quality,
            "ready_for_export": self.ready_for_export,
            "created_at": self.created_at,
            "completed_at": self.completed_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CVData":
        """Create from dictionary."""
        data = data.copy()

        # Convert identity
        if data.get("identity"):
            data["identity"] = CVIdentity(**data["identity"])

        # Convert sections
        for section_name in ["background", "experience", "skills", "motivation", "training", "projects"]:
            if section_name in data:
                data[section_name] = [CVSection.from_dict(s) for s in data[section_name]]

        # Drop unknown keys so old JSON exports with extra fields don't crash
        known = {f.name for f in fields(cls)}
        data = {k: v for k, v in data.items() if k in known}
        return cls(**data)

    def add_section(self, section: CVSection) -> None:
        """Add a polished CV section to the appropriate category."""
        if section.category == QuestionCategory.BACKGROUND:
            self.background.append(section)
        elif section.category == QuestionCategory.EXPERIENCE:
            self.experience.append(section)
        elif section.category == QuestionCategory.SKILLS:
            self.skills.append(section)
        elif section.category == QuestionCategory.MOTIVATION:
            self.motivation.append(section)
        elif section.category == QuestionCategory.TRAINING:
            self.training.append(section)
        elif section.category == QuestionCategory.PROJECTS:
            self.projects.append(section)
        else:
            logger.warning(f"Unknown section category: {section.category}")

        # Update skills dedup
        self.all_skills = list(set(self.all_skills + section.detected_skills))

        # Update languages
        if section.detected_input_language not in self.detected_languages:
            self.detected_languages.append(section.detected_input_language)

    def get_section_by_language(self, category: QuestionCategory, lang_code: str) -> List[str]:
        """
        Get all sections for a category in a specific language.

        Args:
            category: Section category
            lang_code: Language code (de, en, or native language code)

        Returns:
            List of polished text sections in requested language
        """
        sections = []

        if category == QuestionCategory.BACKGROUND:
            sections = self.background
        elif category == QuestionCategory.EXPERIENCE:
            sections = self.experience
        elif category == QuestionCategory.SKILLS:
            sections = self.skills
        elif category == QuestionCategory.MOTIVATION:
            sections = self.motivation
        elif category == QuestionCategory.TRAINING:
            sections = self.training
        elif category == QuestionCategory.PROJECTS:
            sections = self.projects

        # Extract text for requested language
        result = []
        for section in sections:
            text = section.get_language(lang_code)
            if text:
                result.append(text)

        return result

    def get_german_cv(self) -> Dict[str, List[str]]:
        """Get CV in German (primary output language)."""
        return {
            "background": self.get_section_by_language(QuestionCategory.BACKGROUND, "de"),
            "experience": self.get_section_by_language(QuestionCategory.EXPERIENCE, "de"),
            "skills": self.get_section_by_language(QuestionCategory.SKILLS, "de"),
            "motivation": self.get_section_by_language(QuestionCategory.MOTIVATION, "de"),
            "training": self.get_section_by_language(QuestionCategory.TRAINING, "de"),
            "projects": self.get_section_by_language(QuestionCategory.PROJECTS, "de"),
        }

    def get_english_cv(self) -> Dict[str, List[str]]:
        """Get CV in English (secondary output language)."""
        return {
            "background": self.get_section_by_language(QuestionCategory.BACKGROUND, "en"),
            "experience": self.get_section_by_language(QuestionCategory.EXPERIENCE, "en"),
            "skills": self.get_section_by_language(QuestionCategory.SKILLS, "en"),
            "motivation": self.get_section_by_language(QuestionCategory.MOTIVATION, "en"),
            "training": self.get_section_by_language(QuestionCategory.TRAINING, "en"),
            "projects": self.get_section_by_language(QuestionCategory.PROJECTS, "en"),
        }

    def get_native_cv(self) -> Optional[Dict[str, List[str]]]:
        """Get CV in user's native language (if applicable)."""
        if not self.language_output_native:
            return None

        return {
            "background": self.get_section_by_language(QuestionCategory.BACKGROUND, self.language_output_native),
            "experience": self.get_section_by_language(QuestionCategory.EXPERIENCE, self.language_output_native),
            "skills": self.get_section_by_language(QuestionCategory.SKILLS, self.language_output_native),
            "motivation": self.get_section_by_language(QuestionCategory.MOTIVATION, self.language_output_native),
            "training": self.get_section_by_language(QuestionCategory.TRAINING, self.language_output_native),
            "projects": self.get_section_by_language(QuestionCategory.PROJECTS, self.language_output_native),
        }

    def calculate_quality(self) -> None:
        """Calculate overall quality score based on all sections."""
        if not self._get_all_sections():
            self.overall_quality = 0.0
            self.ready_for_export = False
            return

        total_score = 0.0
        for section in self._get_all_sections():
            total_score += section.quality_score

        self.overall_quality = total_score / len(self._get_all_sections())
        self.ready_for_export = self.overall_quality >= 0.5

    def _get_all_sections(self) -> List[CVSection]:
        """Get all sections."""
        return (
            self.background
            + self.experience
            + self.skills
            + self.motivation
            + self.training
            + self.projects
        )

    def to_canonical(self):
        """
        Convert to the shared canonical CVDocument (Pydantic model).

        This is the authoritative export format used for Tool 2 import,
        JSON export, and any downstream consumer. The mapper in Tool 2
        becomes a thin validator once this format is used consistently.

        Returns:
            shared.schema.cv_schema.CVDocument
        """
        # Late import avoids circular dependency and keeps shared/ optional
        # for environments that don't have pydantic installed.
        try:
            from shared.schema.cv_schema import (
                CVDocument, Basics, WorkEntry, EducationEntry,
                SkillGroup, LanguageProficiency, CustomSection, DateRange,
            )
        except ImportError:
            raise ImportError(
                "shared.schema.cv_schema not found. "
                "Ensure the shared/ package is on sys.path or installed."
            )

        def _date_range(period_dict):
            if not period_dict:
                return None
            return DateRange(
                start=period_dict.get("start"),
                end=period_dict.get("end"),
            )

        def _section_to_work(s: "CVSection") -> WorkEntry:
            return WorkEntry(
                german=s.german,
                english=s.english,
                native=s.native,
                bullets=list(s.bullets),
                period=_date_range(s.period),
                detected_skills=list(s.detected_skills),
                quality_score=s.quality_score,
                hidden=s.hidden,
            )

        def _section_to_education(s: "CVSection") -> EducationEntry:
            return EducationEntry(
                german=s.german,
                english=s.english,
                native=s.native,
                bullets=list(s.bullets),
                period=_date_range(s.period),
                quality_score=s.quality_score,
                hidden=s.hidden,
            )

        def _section_to_custom(s: "CVSection", heading: str) -> CustomSection:
            return CustomSection(
                heading=heading,
                german=s.german,
                english=s.english,
                native=s.native,
                bullets=list(s.bullets),
                period=_date_range(s.period),
                quality_score=s.quality_score,
                hidden=s.hidden,
            )

        # Map identity → Basics
        basics = None
        if self.identity:
            basics = Basics(
                full_name=self.identity.full_name,
                email=self.identity.contact_email,
                phone=self.identity.contact_phone,
                location=self.identity.location,
                date_of_birth=self.identity.date_of_birth,
                nationality=self.identity.nationality,
                photo=self.identity.photo,
            )

        # Map sections
        experience = [_section_to_work(s) for s in self.experience]
        # background + training → education (both are non-work time periods)
        education = (
            [_section_to_education(s) for s in self.background]
            + [_section_to_education(s) for s in self.training]
        )
        # skills → a single SkillGroup
        skills_group: List[SkillGroup] = []
        if self.all_skills:
            skills_group = [SkillGroup(label="Fähigkeiten", skills=sorted(self.all_skills))]

        # motivation + projects → custom sections
        custom = (
            [_section_to_custom(s, "Motivation") for s in self.motivation]
            + [_section_to_custom(s, "Projekte") for s in self.projects]
        )

        # Language proficiencies
        lang_profs = [
            LanguageProficiency(
                language=l.get("language", ""),
                code=l.get("code", ""),
                level=l.get("level", ""),
            )
            for l in (self.languages or [])
        ]

        from datetime import datetime as _dt
        return CVDocument(
            user_id=str(self.user_id),
            session_id=str(self.session_id),
            interview_path=self.interview_path,
            language_input=self.language_input,
            language_output_primary=self.language_output_primary,
            language_output_secondary=self.language_output_secondary,
            language_output_native=self.language_output_native,
            basics=basics,
            experience=experience,
            education=education,
            skills=skills_group,
            languages=lang_profs,
            custom_sections=custom,
            all_skills=sorted(self.all_skills) if self.all_skills else [],
            overall_quality=self.overall_quality,
            ready_for_export=self.ready_for_export,
            created_at=self.created_at or "",
            completed_at=self.completed_at,
            exported_at=_dt.now().isoformat(),
        )
