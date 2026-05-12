"""
JSON Exporter - Export CVData as JSON for Tool 2 import and data interchange.

Produces clean, structured JSON suitable for:
- Tool 2 Dashboard import
- External systems integration
- API responses
- Data backup
"""

import json
import logging
from typing import Optional, Dict
from pathlib import Path
from datetime import datetime

from cv.models import CVData
from export.base import CVExporter

logger = logging.getLogger(__name__)


class JSONExporter(CVExporter):
    """Export CVData as JSON format."""

    def export(
        self,
        cv_data: CVData,
        language: str = "de",
        filename: Optional[str] = None
    ) -> Optional[str]:
        """
        Export CVData as JSON file.

        Args:
            cv_data: Complete CVData object to export
            language: Target language ("de", "en", or native code)
            filename: Optional custom filename (without extension)

        Returns:
            Path to exported JSON file, or None if export failed
        """
        try:
            logger.info(f"Exporting CVData as JSON (language: {language})")

            # Validate CVData
            if not self.validate_cv_data(cv_data):
                logger.error("CVData validation failed")
                return None

            # ── Canonical schema export ────────────────────────────────────
            # Always export using the shared canonical CVDocument so Tool 2
            # can import without shape-normalisation.  The language parameter
            # is stored in the document for the consumer to use when rendering.
            try:
                doc = cv_data.to_canonical()
                json_output = doc.model_dump()
                # Stamp the requested export language so downstream knows
                # which language version to render.
                json_output["_export_language"] = language
            except ImportError:
                # Fallback: shared package not installed — emit legacy shape
                logger.warning("shared.schema not available; falling back to legacy export shape")
                content = self.get_cv_content_for_language(cv_data, language)
                json_output = {
                    "metadata": {
                        "exported_at": datetime.now().isoformat(),
                        "export_format": "JSON",
                        "export_version": "1.0",
                        "export_language": language,
                        "session_id": cv_data.session_id,
                        "user_id": cv_data.user_id,
                        "interview_path": cv_data.interview_path,
                    },
                    "quality_metrics": {
                        "overall_quality": cv_data.overall_quality,
                        "ready_for_export": cv_data.ready_for_export,
                        "language_input": cv_data.language_input,
                        "language_output_primary": cv_data.language_output_primary,
                        "language_output_secondary": cv_data.language_output_secondary,
                    },
                    "content": content or {},
                }

            # Generate filename
            json_filename = self.generate_filename(cv_data, language, "json", filename)
            json_path = self.output_dir / json_filename

            # Write JSON file
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(json_output, f, ensure_ascii=False, indent=2)

            logger.info(f"JSON export successful: {json_path}")
            return str(json_path)

        except Exception as e:
            logger.error(f"Error exporting CVData as JSON: {e}")
            return None

    def export_raw_cvdata(
        self,
        cv_data: CVData,
        filename: Optional[str] = None
    ) -> Optional[str]:
        """
        Export raw CVData object as JSON (complete multilingual data).

        Useful for data backup or Tool 2 import of full multilingual versions.

        Args:
            cv_data: CVData object
            filename: Optional custom filename

        Returns:
            Path to exported JSON file, or None if failed
        """
        try:
            logger.info("Exporting raw CVData as JSON")

            # Validate CVData
            if not self.validate_cv_data(cv_data):
                logger.error("CVData validation failed")
                return None

            # Convert CVData to dict using its to_dict() method
            cv_dict = cv_data.to_dict()

            # Add export metadata
            export_data = {
                "metadata": {
                    "exported_at": datetime.now().isoformat(),
                    "export_format": "Raw CVData JSON",
                    "export_version": "1.0",
                },
                "cvdata": cv_dict,
            }

            # Generate filename
            json_filename = self.generate_filename(cv_data, "all", "json", filename or "raw")
            json_path = self.output_dir / json_filename

            # Write JSON file
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)

            logger.info(f"Raw CVData JSON export successful: {json_path}")
            return str(json_path)

        except Exception as e:
            logger.error(f"Error exporting raw CVData: {e}")
            return None

    def export_for_api(
        self,
        cv_data: CVData,
        language: str = "de"
    ) -> Optional[Dict]:
        """
        Export CVData as dict for API response (no file writing).

        Useful for REST API endpoints that return JSON directly.

        Args:
            cv_data: CVData to export
            language: Target language

        Returns:
            Dict ready for JSON serialization, or None if failed
        """
        try:
            logger.info(f"Exporting CVData for API (language: {language})")

            # Validate CVData
            if not self.validate_cv_data(cv_data):
                logger.error("CVData validation failed")
                return None

            # Extract content in target language
            content = self.get_cv_content_for_language(cv_data, language)
            if content is None:
                logger.error("Failed to extract CV content")
                return None

            # Build response structure
            response = {
                "status": "success",
                "data": {
                    "metadata": {
                        "session_id": cv_data.session_id,
                        "user_id": cv_data.user_id,
                        "interview_path": cv_data.interview_path,
                        "export_timestamp": datetime.now().isoformat(),
                    },
                    "quality": {
                        "overall_quality": cv_data.overall_quality,
                        "ready_for_export": cv_data.ready_for_export,
                    },
                    "sections": {
                        "background": content.get("background", []),
                        "experience": content.get("experience", []),
                        "skills": content.get("skills", []),
                        "all_skills": content.get("all_skills", []),
                        "motivation": content.get("motivation", []),
                        "training": content.get("training", []),
                        "projects": content.get("projects", []),
                    },
                },
            }

            logger.info("API export successful")
            return response

        except Exception as e:
            logger.error(f"Error exporting for API: {e}")
            return {
                "status": "error",
                "error": str(e),
            }


if __name__ == "__main__":
    # Example usage
    from cv.models import CVData, CVSection, QuestionCategory

    # Create sample CVData
    cv = CVData(
        session_id=1,
        user_id="test_user",
        interview_path="unemployed",
        language_input="en"
    )

    # Add a sample section
    section = CVSection(
        german="Ich habe mit Python gearbeitet.",
        english="I worked with Python.",
        native="I worked with Python.",
        category=QuestionCategory.EXPERIENCE,
        question_id="exp_001",
        detected_input_language="en",
        user_native_language="en",
        quality_score=0.85,
        confidence_level="high",
        detected_skills=["Python"]
    )

    cv.experience.append(section)

    # Export
    exporter = JSONExporter()
    path = exporter.export(cv, language="en", filename="test_cv")
    print(f"Exported to: {path}")
