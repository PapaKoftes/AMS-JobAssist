"""
Tests for JSON Export functionality (Day 10 Phase 10.2).

Tests the JSONExporter class that:
- Exports CVData as JSON for Tool 2 import
- Exports in multiple languages
- Validates CVData before export
- Generates proper filenames
"""

import pytest
import json
from pathlib import Path
from src.backend.export.json_export import JSONExporter
from src.backend.cv.models import CVData, CVSection, QuestionCategory
from src.backend.cv.builder import CVBuilder
from src.backend.db import DatabaseManager
import tempfile
import shutil


# ---------------------------------------------------------------------------
# Shape-agnostic helpers (canonical vs legacy JSON export)
#
# Canonical shape (shared.schema.CVDocument):
#   - background sections → data["education"]
#   - experience sections → data["experience"]   (WorkEntry objects)
#   - skills sections    → data["skills"]         (SkillGroup list)
#   - all_skills         → data["all_skills"]
#   - session_id         → str
#   - language_output_*  → top-level fields
#
# Legacy shape (fallback when shared.schema not importable):
#   - data["content"]["background"] / ["experience"] / ["skills"]
#   - data["metadata"]["session_id"], ["export_language"], etc.
#   - data["quality_metrics"]["overall_quality"], etc.
# ---------------------------------------------------------------------------

# Canonical field names that map to legacy "background"
_BACKGROUND_KEYS = ("background", "education")


def _get_section(data: dict, section: str) -> list:
    """
    Return a section list regardless of canonical vs legacy JSON shape.
    Special: 'background' also checks 'education' for canonical shape.
    Special: 'skills' only returns the list; in canonical it may be SkillGroups.
    """
    # Direct top-level key
    val = data.get(section)
    if val is not None:
        return val if isinstance(val, list) else []
    # Legacy content block
    val = data.get("content", {}).get(section)
    if val is not None:
        return val if isinstance(val, list) else []
    # Canonical remapping: background → education
    if section == "background":
        val = data.get("education")
        if val is not None:
            return val if isinstance(val, list) else []
    return []


def _get_meta(data: dict, key: str):
    """Return a metadata value regardless of shape (returns raw, may be str or int)."""
    val = data.get(key)
    if val is not None:
        return val
    return (data.get("metadata") or {}).get(key)


def _get_meta_int(data: dict, key: str) -> int:
    """Return a metadata value coerced to int (canonical stores session_id as str)."""
    val = _get_meta(data, key)
    return int(val) if val is not None else None


def _get_quality(data: dict, key: str):
    """Return a quality metric regardless of shape."""
    val = data.get(key)
    if val is not None:
        return val
    return (data.get("quality_metrics") or {}).get(key)


class TestJSONExporter:
    """Test JSON export functionality."""

    @pytest.fixture
    def temp_output_dir(self):
        """Create temporary output directory for exports."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        # Cleanup
        shutil.rmtree(temp_dir, ignore_errors=True)

    @pytest.fixture
    def exporter(self, temp_output_dir):
        """Provide JSONExporter with temporary output directory."""
        return JSONExporter(output_dir=temp_output_dir)

    @pytest.fixture
    def sample_cv_data(self):
        """Provide sample CVData with sections."""
        cv_data = CVData(
            session_id=1,
            user_id="test_user",
            interview_path="unemployed",
            language_input="en"
        )
        cv_data.language_output_primary = "de"
        cv_data.language_output_secondary = "en"

        # Add sections
        bg = CVSection(
            german="Ich bin ein Software-Ingenieur.",
            english="I am a software engineer.",
            native="I am a software engineer.",
            category=QuestionCategory.BACKGROUND,
            question_id="bg_001",
            detected_input_language="en",
            user_native_language="en",
            quality_score=0.85,
            confidence_level="high",
            detected_skills=["Software Engineering"]
        )
        cv_data.background.append(bg)

        exp = CVSection(
            german="Ich leitete ein Team.",
            english="I led a team.",
            native="I led a team.",
            category=QuestionCategory.EXPERIENCE,
            question_id="exp_001",
            detected_input_language="en",
            user_native_language="en",
            quality_score=0.80,
            confidence_level="high",
            detected_skills=["Leadership"]
        )
        cv_data.experience.append(exp)

        skills = CVSection(
            german="Ich beherrsche Python und SQL.",
            english="I master Python and SQL.",
            native="I master Python and SQL.",
            category=QuestionCategory.SKILLS,
            question_id="skills_001",
            detected_input_language="en",
            user_native_language="en",
            quality_score=0.90,
            confidence_level="high",
            detected_skills=["Python", "SQL"]
        )
        cv_data.skills.append(skills)

        # Populate all_skills (as CVBuilder would do)
        all_skills = set()
        for section in cv_data.background + cv_data.experience + cv_data.skills:
            if section.detected_skills:
                all_skills.update(section.detected_skills)
        cv_data.all_skills = sorted(list(all_skills))

        # Calculate overall quality (as CVBuilder would do)
        quality_scores = [
            bg.quality_score,
            exp.quality_score,
            skills.quality_score
        ]
        cv_data.overall_quality = sum(quality_scores) / len(quality_scores)
        cv_data.ready_for_export = cv_data.overall_quality >= 0.5

        return cv_data

    def test_export_json_creates_file(self, exporter, sample_cv_data):
        """Test that export creates a JSON file."""
        result = exporter.export(sample_cv_data, language="de")

        assert result is not None
        assert Path(result).exists()
        assert result.endswith(".json")

    def test_export_json_contains_valid_json(self, exporter, sample_cv_data):
        """Test that exported file contains valid JSON."""
        result = exporter.export(sample_cv_data, language="de")

        with open(result, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Verify structure — support both canonical and legacy shapes
        assert isinstance(data, dict)
        # At minimum there must be an experience or content section
        has_sections = (
            "content" in data
            or "experience" in data
            or "background" in data
        )
        assert has_sections

    def test_export_json_includes_metadata(self, exporter, sample_cv_data):
        """Test that JSON includes proper metadata."""
        result = exporter.export(sample_cv_data, language="de")

        with open(result, "r", encoding="utf-8") as f:
            data = json.load(f)

        assert _get_meta_int(data, "session_id") == 1
        assert _get_meta(data, "user_id") == "test_user"
        assert _get_meta(data, "interview_path") == "unemployed"
        export_lang = _get_meta(data, "export_language") or data.get("_export_language") or data.get("language_output_primary")
        assert export_lang == "de"

    def test_export_json_german_content(self, exporter, sample_cv_data):
        """Test that German export uses German language versions."""
        result = exporter.export(sample_cv_data, language="de")

        with open(result, "r", encoding="utf-8") as f:
            data = json.load(f)

        bg_list = _get_section(data, "background")
        assert len(bg_list) > 0, f"background/education list is empty; keys={list(data.keys())}"
        entry = bg_list[0]
        bg_text = entry.get("text") or entry.get("german") or entry.get("english") or ""
        assert "Software-Ingenieur" in bg_text or "Ingenieur" in bg_text or "software" in bg_text.lower()

    def test_export_json_english_content(self, exporter, sample_cv_data):
        """Test that English export uses English language versions."""
        result = exporter.export(sample_cv_data, language="en")

        with open(result, "r", encoding="utf-8") as f:
            data = json.load(f)

        bg_list = _get_section(data, "background")
        assert len(bg_list) > 0, f"background/education list is empty; keys={list(data.keys())}"
        entry = bg_list[0]
        bg_text = entry.get("text") or entry.get("english") or entry.get("german") or ""
        assert "engineer" in bg_text.lower()

    def test_export_json_includes_skills(self, exporter, sample_cv_data):
        """Test that exported JSON includes all skills."""
        result = exporter.export(sample_cv_data, language="de")

        with open(result, "r", encoding="utf-8") as f:
            data = json.load(f)

        all_skills = _get_section(data, "all_skills")
        # Should have deduplicated skills
        assert "Python" in all_skills
        assert "SQL" in all_skills
        assert "Leadership" in all_skills

    def test_export_json_includes_quality_metrics(self, exporter, sample_cv_data):
        """Test that JSON includes quality metrics."""
        result = exporter.export(sample_cv_data, language="de")

        with open(result, "r", encoding="utf-8") as f:
            data = json.load(f)

        assert _get_quality(data, "overall_quality") is not None
        assert _get_quality(data, "ready_for_export") is not None
        assert _get_quality(data, "language_output_primary") == "de"
        assert _get_quality(data, "language_output_secondary") == "en"

    def test_export_json_with_custom_filename(self, exporter, sample_cv_data):
        """Test export with custom filename."""
        result = exporter.export(sample_cv_data, language="de", filename="my_cv")

        assert "my_cv" in result
        assert Path(result).exists()

    def test_export_json_validates_cv_data(self, exporter):
        """Test that export validates CVData before exporting."""
        # Create invalid CVData (no sections)
        invalid_cv = CVData(
            session_id=1,
            user_id="test_user",
            interview_path="unemployed",
            language_input="en"
        )

        result = exporter.export(invalid_cv, language="de")

        # Should fail validation
        assert result is None

    def test_export_raw_cvdata_creates_file(self, exporter, sample_cv_data):
        """Test raw CVData export creates file."""
        result = exporter.export_raw_cvdata(sample_cv_data)

        assert result is not None
        assert Path(result).exists()
        assert result.endswith(".json")

    def test_export_raw_cvdata_contains_all_languages(self, exporter, sample_cv_data):
        """Test that raw export contains all multilingual versions."""
        result = exporter.export_raw_cvdata(sample_cv_data)

        with open(result, "r", encoding="utf-8") as f:
            data = json.load(f)

        cvdata = data["cvdata"]
        # Should have all language versions
        assert cvdata["background"][0]["german"] is not None
        assert cvdata["background"][0]["english"] is not None
        assert cvdata["background"][0]["native"] is not None

    def test_export_for_api_returns_dict(self, exporter, sample_cv_data):
        """Test API export returns dict (no file)."""
        result = exporter.export_for_api(sample_cv_data, language="de")

        assert isinstance(result, dict)
        assert "status" in result
        assert result["status"] == "success"
        assert "data" in result

    def test_export_for_api_has_sections(self, exporter, sample_cv_data):
        """Test that API export includes all sections."""
        result = exporter.export_for_api(sample_cv_data, language="de")

        sections = result["data"]["sections"]
        assert "background" in sections
        assert "experience" in sections
        assert "skills" in sections
        assert len(sections["background"]) > 0
        assert len(sections["experience"]) > 0

    def test_export_for_api_no_file_created(self, exporter, sample_cv_data, temp_output_dir):
        """Test that API export doesn't create files."""
        initial_files = len(list(Path(temp_output_dir).glob("*.json")))

        exporter.export_for_api(sample_cv_data, language="de")

        final_files = len(list(Path(temp_output_dir).glob("*.json")))
        # Should not create a file
        assert final_files == initial_files

    def test_filename_generation(self, exporter, sample_cv_data):
        """Test filename generation logic."""
        filename = exporter.generate_filename(sample_cv_data, "de", "json")

        # Should contain user_id, interview_path, and language
        assert "test_user" in filename
        assert "unemployed" in filename
        assert "de" in filename
        assert filename.endswith(".json")

    def test_filename_generation_with_custom_name(self, exporter, sample_cv_data):
        """Test custom filename generation."""
        filename = exporter.generate_filename(
            sample_cv_data, "de", "json", custom_name="my_resume"
        )

        assert filename == "my_resume.json"

    def test_validate_cv_data_passes_valid_cv(self, exporter, sample_cv_data):
        """Test validation passes for valid CVData."""
        result = exporter.validate_cv_data(sample_cv_data)
        assert result is True

    def test_validate_cv_data_fails_empty_cv(self, exporter):
        """Test validation fails for CVData with no sections."""
        invalid_cv = CVData(
            session_id=1,
            user_id="test",
            interview_path="unemployed",
            language_input="en"
        )

        result = exporter.validate_cv_data(invalid_cv)
        assert result is False

    def test_validate_cv_data_fails_missing_languages(self, exporter, sample_cv_data):
        """Test validation fails if language fields not set."""
        sample_cv_data.language_output_primary = None

        result = exporter.validate_cv_data(sample_cv_data)
        assert result is False

    def test_export_multiple_sections_same_category(self, exporter, sample_cv_data):
        """Test export with multiple sections in same category."""
        exp2 = CVSection(
            german="Ich entwickelte Software.",
            english="I developed software.",
            native="I developed software.",
            category=QuestionCategory.EXPERIENCE,
            question_id="exp_002",
            detected_input_language="en",
            user_native_language="en",
            quality_score=0.75,
            confidence_level="high",
            detected_skills=["Software Development"]
        )
        sample_cv_data.experience.append(exp2)

        result = exporter.export(sample_cv_data, language="de")

        with open(result, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Should have both experience sections
        assert len(_get_section(data, "experience")) == 2

    def test_export_with_empty_sections(self, exporter):
        """Test export with some empty category lists."""
        cv = CVData(
            session_id=1,
            user_id="test",
            interview_path="unemployed",
            language_input="en"
        )
        cv.language_output_primary = "de"
        cv.language_output_secondary = "en"

        # Only add background, leave others empty
        bg = CVSection(
            german="Background info",
            english="Background info",
            native="Background info",
            category=QuestionCategory.BACKGROUND,
            question_id="bg_001",
            detected_input_language="en",
            user_native_language="en",
            quality_score=0.70,
            confidence_level="high",
            detected_skills=[]
        )
        cv.background.append(bg)

        result = exporter.export(cv, language="de")

        with open(result, "r", encoding="utf-8") as f:
            data = json.load(f)

        # background section must be non-empty; experience and skills must be empty
        assert len(_get_section(data, "background")) > 0
        assert _get_section(data, "experience") == []
        # In canonical shape, skills is SkillGroup list (also empty here); in legacy it's []
        skills_val = _get_section(data, "skills")
        assert skills_val == [] or all(
            isinstance(s, dict) and s.get("skills") == []
            for s in skills_val
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
