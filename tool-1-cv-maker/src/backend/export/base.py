"""
CV Export Base Classes - Abstract interface for all export formats.

Handles:
1. Base CVExporter abstract class
2. Language selection and version extraction
3. Common formatting utilities
4. Export error handling
"""

import logging
import re
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from datetime import datetime
from pathlib import Path

from cv.models import CVData

logger = logging.getLogger(__name__)


def _sanitize_filename_component(name: str) -> str:
    """
    Reduce an arbitrary (possibly user-supplied) string to a SAFE single filename
    component: no directory separators, no traversal, no NUL/control chars.

    Prevents path traversal when joined with an output directory and zip-entry
    collision/escape in Tool 2's bulk export. Always returns a non-empty token.
    """
    name = str(name or "")
    # Drop any path components an attacker tried to inject.
    name = name.replace("\\", "/").split("/")[-1]
    # Keep only a conservative allow-list; collapse everything else to '_'.
    name = re.sub(r"[^A-Za-z0-9._-]", "_", name)
    # Disallow leading dots / pure-dot names ("..", ".") and over-long names.
    name = name.lstrip(".") or "cv"
    return name[:120]


class CVExporter(ABC):
    """
    Abstract base class for CV export engines.

    Defines interface for exporting CVData to various formats (PDF, DOCX, etc.).
    Subclasses implement format-specific logic.
    """

    SUPPORTED_FORMATS = ["pdf", "docx", "json"]
    LANGUAGE_CODES = ["de", "en", "sr", "fr", "it", "es", "pl", "ro", "bg", "hr", "sk", "hu", "cs", "lt"]

    def __init__(self, output_dir: str = "data/exports"):
        """
        Initialize CVExporter.

        Args:
            output_dir: Directory to save exported files
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"CVExporter initialized with output directory: {self.output_dir}")

    @abstractmethod
    def export(
        self,
        cv_data: CVData,
        language: str = "de",
        filename: Optional[str] = None
    ) -> Optional[str]:
        """
        Export CVData to format-specific file.

        Args:
            cv_data: Complete CVData object to export
            language: Target language for export ("de", "en", or user's native language code)
            filename: Optional custom filename (without extension)

        Returns:
            Path to exported file, or None if export failed
        """
        pass

    def get_cv_content_for_language(
        self,
        cv_data: CVData,
        language: str
    ) -> Optional[Dict[str, Any]]:
        """
        Extract CV content in specified language.

        Maps language to correct field (german, english, native) and extracts
        sections in that language.

        Args:
            cv_data: Complete CVData object
            language: Target language code ("de", "en", or native language code)

        Returns:
            Dict with sections organized by category in target language, or None
        """
        try:
            # Determine which language field to use
            if language == "de" or language == cv_data.language_output_primary:
                # Use German (primary output)
                return self._extract_sections_german(cv_data)
            elif language == "en" or language == cv_data.language_output_secondary:
                # Use English (secondary output)
                return self._extract_sections_english(cv_data)
            else:
                # Use native language
                return self._extract_sections_native(cv_data, language)

        except Exception as e:
            logger.error(f"Error extracting CV content for language {language}: {e}")
            return None

    def _extract_sections_german(self, cv_data: CVData) -> Dict[str, Any]:
        """Extract all sections in German."""
        return {
            "background": [{"text": s.german} for s in cv_data.background if s.german],
            "experience": [{"text": s.german} for s in cv_data.experience if s.german],
            "skills": [{"text": s.german} for s in cv_data.skills if s.german],
            "motivation": [{"text": s.german} for s in cv_data.motivation if s.german],
            "training": [{"text": s.german} for s in cv_data.training if s.german],
            "projects": [{"text": s.german} for s in cv_data.projects if s.german],
            "all_skills": cv_data.all_skills or [],
        }

    def _extract_sections_english(self, cv_data: CVData) -> Dict[str, Any]:
        """Extract all sections in English."""
        return {
            "background": [{"text": s.english} for s in cv_data.background if s.english],
            "experience": [{"text": s.english} for s in cv_data.experience if s.english],
            "skills": [{"text": s.english} for s in cv_data.skills if s.english],
            "motivation": [{"text": s.english} for s in cv_data.motivation if s.english],
            "training": [{"text": s.english} for s in cv_data.training if s.english],
            "projects": [{"text": s.english} for s in cv_data.projects if s.english],
            "all_skills": cv_data.all_skills or [],
        }

    def _extract_sections_native(self, cv_data: CVData, native_language: str) -> Dict[str, Any]:
        """Extract all sections in user's native language."""
        return {
            "background": [{"text": s.native} for s in cv_data.background if s.native],
            "experience": [{"text": s.native} for s in cv_data.experience if s.native],
            "skills": [{"text": s.native} for s in cv_data.skills if s.native],
            "motivation": [{"text": s.native} for s in cv_data.motivation if s.native],
            "training": [{"text": s.native} for s in cv_data.training if s.native],
            "projects": [{"text": s.native} for s in cv_data.projects if s.native],
            "all_skills": cv_data.all_skills or [],
        }

    def generate_filename(
        self,
        cv_data: CVData,
        language: str,
        extension: str,
        custom_name: Optional[str] = None
    ) -> str:
        """
        Generate standardized export filename.

        Format: {user_id}_{interview_path}_{language}_{timestamp}.{extension}

        Args:
            cv_data: CV being exported
            language: Target language
            extension: File extension (pdf, docx, json, etc.)
            custom_name: Optional custom filename

        Returns:
            Filename with extension
        """
        if custom_name:
            return f"{_sanitize_filename_component(custom_name)}.{extension}"

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        language_code = language if len(language) <= 2 else language[:2]
        base = f"{cv_data.user_id}_{cv_data.interview_path}_{language_code}_{timestamp}"
        return f"{_sanitize_filename_component(base)}.{extension}"

    def validate_cv_data(self, cv_data: CVData) -> bool:
        """
        Validate CVData is ready for export.

        Checks:
        - Has sections in at least one category
        - Has language fields set
        - All sections have required multilingual versions

        Args:
            cv_data: CVData to validate

        Returns:
            True if valid, False otherwise
        """
        if cv_data is None:
            logger.warning("CVData is None")
            return False

        # Check has sections
        section_count = (
            len(cv_data.background) + len(cv_data.experience) +
            len(cv_data.skills) + len(cv_data.motivation) +
            len(cv_data.training) + len(cv_data.projects)
        )
        if section_count == 0:
            logger.warning("CVData has no sections")
            return False

        # Check language fields
        if not cv_data.language_output_primary or not cv_data.language_output_secondary:
            logger.warning("CVData missing language_output fields")
            return False

        # Required sections must have multilingual versions; optional sections are skipped if empty
        required_sections = cv_data.background + cv_data.experience + cv_data.skills
        for section in required_sections:
            if not section.german and not section.english:
                logger.warning(f"Section {section.question_id} missing multilingual versions")
                return False

        return True

    def format_skill_list(self, skills: list, style: str = "comma") -> str:
        """
        Format skill list for export.

        Args:
            skills: List of skill strings
            style: Format style ("comma", "bullet", "inline")

        Returns:
            Formatted skill string
        """
        if not skills:
            return ""

        if style == "comma":
            return ", ".join(skills)
        elif style == "bullet":
            return "\n".join([f"• {skill}" for skill in skills])
        elif style == "inline":
            return " • ".join(skills)
        else:
            return ", ".join(skills)

    def format_section_title(self, category: str, language: str = "de") -> str:
        """
        Get localized section title.

        Args:
            category: Section category (background, experience, etc.)
            language: Language code

        Returns:
            Localized section title
        """
        titles_de = {
            "background": "Hintergrund",
            "experience": "Berufserfahrung",
            "skills": "Fähigkeiten",
            "motivation": "Motivation",
            "training": "Schulungen & Zertifikate",
            "projects": "Projekte",
        }

        titles_en = {
            "background": "Background",
            "experience": "Professional Experience",
            "skills": "Skills",
            "motivation": "Motivation",
            "training": "Training & Certifications",
            "projects": "Projects",
        }

        if language == "de":
            return titles_de.get(category, category.capitalize())
        else:
            return titles_en.get(category, category.capitalize())

    class ExportError(Exception):
        """Custom exception for export errors."""
        pass
