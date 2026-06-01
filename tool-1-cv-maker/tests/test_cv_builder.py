"""
Tests for CVBuilder (Day 10 Phase 10.1).

Tests the CVBuilder class that:
- Assembles complete CVData from session answers
- Organizes sections by category
- Deduplicates skills
- Calculates overall quality score
- Marks ready_for_export
"""

import pytest
from src.backend.cv.builder import CVBuilder
from src.backend.cv.models import CVData, CVSection, QuestionCategory
from src.backend.db import DatabaseManager


class TestCVBuilder:
    """Test CVBuilder assembly of complete CVData."""

    @pytest.fixture
    def db_manager(self):
        """Provide in-memory database for testing."""
        db = DatabaseManager(":memory:")
        db.initialize()
        return db

    @pytest.fixture
    def builder(self, db_manager):
        """Provide CVBuilder instance."""
        return CVBuilder(db_manager)

    @pytest.fixture
    def sample_cv_sections(self):
        """Provide sample CVSection objects for building."""
        sections = []

        # Background section
        bg = CVSection(
            german="Ich bin ein erfahrener Softwareentwickler.",
            english="I am an experienced software developer.",
            native="I am an experienced software developer.",
            category=QuestionCategory.BACKGROUND,
            question_id="bg_001",
            detected_input_language="en",
            user_native_language="en",
            quality_score=0.85,
            confidence_level="high",
            detected_skills=["Software Development"]
        )
        sections.append(bg)

        # Experience section 1
        exp1 = CVSection(
            german="Ich leitete ein Team von fünf Entwicklern.",
            english="I led a team of five developers.",
            native="I led a team of five developers.",
            category=QuestionCategory.EXPERIENCE,
            question_id="exp_001",
            detected_input_language="en",
            user_native_language="en",
            quality_score=0.80,
            confidence_level="high",
            detected_skills=["Leadership", "Team Management"]
        )
        sections.append(exp1)

        # Experience section 2
        exp2 = CVSection(
            german="Ich entwickelte Web-Anwendungen mit Python.",
            english="I developed web applications with Python.",
            native="I developed web applications with Python.",
            category=QuestionCategory.EXPERIENCE,
            question_id="exp_002",
            detected_input_language="en",
            user_native_language="en",
            quality_score=0.75,
            confidence_level="high",
            detected_skills=["Python", "Web Development"]
        )
        sections.append(exp2)

        # Skills section
        skills = CVSection(
            german="Ich beherrsche Python, SQL und Excel.",
            english="I master Python, SQL, and Excel.",
            native="I master Python, SQL, and Excel.",
            category=QuestionCategory.SKILLS,
            question_id="skills_001",
            detected_input_language="en",
            user_native_language="en",
            quality_score=0.90,
            confidence_level="high",
            detected_skills=["Python", "SQL", "Microsoft Excel"]
        )
        sections.append(skills)

        # Motivation section
        mot = CVSection(
            german="Ich interessiere mich für neue Projekte.",
            english="I am interested in new projects.",
            native="I am interested in new projects.",
            category=QuestionCategory.MOTIVATION,
            question_id="mot_001",
            detected_input_language="en",
            user_native_language="en",
            quality_score=0.70,
            confidence_level="medium",
            detected_skills=[]
        )
        sections.append(mot)

        return sections

    def _create_session(self, db_manager, user_id: str) -> int:
        """Helper to create a session."""
        existing_user = db_manager.execute_query(
            "SELECT user_id FROM users WHERE user_id = ?",
            (user_id,)
        )

        if not existing_user:
            db_manager.execute_update(
                "INSERT INTO users (user_id, email) VALUES (?, ?)",
                (user_id, f"{user_id}@test.local")
            )

        return db_manager.create_session(
            user_id=user_id,
            interview_path="unemployed",
            language="de"
        )

    def test_build_cv_from_answers_dict_creates_valid_cv(self, builder, sample_cv_sections):
        """Test building CVData from answers dictionary."""
        answers_dict = {s.question_id: s for s in sample_cv_sections}

        cv_data = builder.build_cv_from_answers_dict(
            session_id=1,
            user_id="test_user",
            interview_path="unemployed",
            language_input="en",
            answers_dict=answers_dict
        )

        assert cv_data is not None
        assert cv_data.session_id == 1
        assert cv_data.user_id == "test_user"

    def test_build_cv_organizes_sections_by_category(self, builder, sample_cv_sections):
        """Test that sections are organized into correct categories."""
        answers_dict = {s.question_id: s for s in sample_cv_sections}

        cv_data = builder.build_cv_from_answers_dict(
            session_id=1,
            user_id="test_user",
            interview_path="unemployed",
            language_input="en",
            answers_dict=answers_dict
        )

        # Verify each category has correct sections
        assert len(cv_data.background) == 1
        assert len(cv_data.experience) == 2
        assert len(cv_data.skills) == 1
        assert len(cv_data.motivation) == 1
        assert len(cv_data.training) == 0
        assert len(cv_data.projects) == 0

    def test_build_cv_deduplicates_skills(self, builder, sample_cv_sections):
        """Test that skills are deduplicated across sections."""
        answers_dict = {s.question_id: s for s in sample_cv_sections}

        cv_data = builder.build_cv_from_answers_dict(
            session_id=1,
            user_id="test_user",
            interview_path="unemployed",
            language_input="en",
            answers_dict=answers_dict
        )

        # Python appears in 2 sections, should be deduplicated
        assert "Python" in cv_data.all_skills
        assert cv_data.all_skills.count("Python") == 1

        # Check total unique skills
        # Should have: Software Development, Leadership, Team Management, Python,
        # Web Development, SQL, Microsoft Excel (7 total)
        assert len(cv_data.all_skills) >= 6

    def test_build_cv_calculates_overall_quality(self, builder, sample_cv_sections):
        """Test that overall quality score is calculated correctly."""
        answers_dict = {s.question_id: s for s in sample_cv_sections}

        cv_data = builder.build_cv_from_answers_dict(
            session_id=1,
            user_id="test_user",
            interview_path="unemployed",
            language_input="en",
            answers_dict=answers_dict
        )

        # Average of [0.85, 0.80, 0.75, 0.90, 0.70] = 0.80
        assert cv_data.overall_quality == pytest.approx(0.80, abs=0.01)

    def test_build_cv_marks_ready_for_export_when_quality_high(self, builder, sample_cv_sections):
        """Test that ready_for_export is True when quality >= 0.5."""
        answers_dict = {s.question_id: s for s in sample_cv_sections}

        cv_data = builder.build_cv_from_answers_dict(
            session_id=1,
            user_id="test_user",
            interview_path="unemployed",
            language_input="en",
            answers_dict=answers_dict
        )

        # Quality is 0.80, threshold is 0.50
        assert cv_data.ready_for_export is True

    def test_build_cv_empty_is_not_exportable(self, builder):
        """ready_for_export is based on COMPLETENESS, not a quality score.

        The quality scorer is biased toward English verbs/skills, so a valid
        German CV legitimately scores low — gating export on that score wrongly
        blocked real participants. Export readiness now requires a name plus at
        least one content section. An empty interview yields no CV at all
        (None), which is the real "nothing to export" state.
        """
        cv_data = builder.build_cv_from_answers_dict(
            session_id=1,
            user_id="test_user",
            interview_path="unemployed",
            language_input="en",
            answers_dict={}  # no answers at all
        )

        # No content → no CV to export (or, if built, not export-ready)
        assert cv_data is None or cv_data.ready_for_export is False

    def test_build_cv_ready_for_low_quality_but_complete(self, builder):
        """A complete-but-low-quality CV (e.g. terse German) is still exportable."""
        low_quality = CVSection(
            german="OK",
            english="OK",
            native="OK",
            category=QuestionCategory.BACKGROUND,
            question_id="bg_001",
            detected_input_language="en",
            user_native_language="en",
            quality_score=0.30,
            confidence_level="low",
            detected_skills=[]
        )

        cv_data = builder.build_cv_from_answers_dict(
            session_id=1,
            user_id="test_user",
            interview_path="unemployed",
            language_input="en",
            answers_dict={"bg_001": low_quality}
        )

        # Has a name (from user) + a content section → exportable despite low score
        assert cv_data.ready_for_export is True

    def test_build_cv_handles_empty_answers(self, builder):
        """Test building CV from empty answers dictionary."""
        cv_data = builder.build_cv_from_answers_dict(
            session_id=1,
            user_id="test_user",
            interview_path="unemployed",
            language_input="en",
            answers_dict={}
        )

        assert cv_data is None

    def test_build_cv_sets_language_output_fields(self, builder, sample_cv_sections):
        """Test that language output fields are set correctly."""
        answers_dict = {s.question_id: s for s in sample_cv_sections}

        cv_data = builder.build_cv_from_answers_dict(
            session_id=1,
            user_id="test_user",
            interview_path="unemployed",
            language_input="en",
            answers_dict=answers_dict,
            language_output_primary="de",
            language_output_secondary="en"
        )

        assert cv_data.language_output_primary == "de"
        assert cv_data.language_output_secondary == "en"

    def test_build_cv_preserves_section_metadata(self, builder, sample_cv_sections):
        """Test that section metadata is preserved in built CV."""
        answers_dict = {s.question_id: s for s in sample_cv_sections}

        cv_data = builder.build_cv_from_answers_dict(
            session_id=1,
            user_id="test_user",
            interview_path="unemployed",
            language_input="en",
            answers_dict=answers_dict
        )

        # Check first section from background
        bg_section = cv_data.background[0]
        assert bg_section.quality_score == 0.85
        assert bg_section.confidence_level == "high"
        assert len(bg_section.detected_skills) > 0

    def test_calculate_category_quality(self, builder, sample_cv_sections):
        """Test quality calculation for a category."""
        exp_sections = [s for s in sample_cv_sections if s.category == QuestionCategory.EXPERIENCE]

        quality = builder.calculate_category_quality(exp_sections)

        # Average of [0.80, 0.75] = 0.775
        assert quality == pytest.approx(0.775, abs=0.01)

    def test_calculate_category_quality_empty_list(self, builder):
        """Test quality calculation for empty list."""
        quality = builder.calculate_category_quality([])
        assert quality == 0.0

    def test_calculate_category_quality_with_none_scores(self, builder):
        """Test quality calculation when some sections have None quality_score."""
        section1 = CVSection(
            german="Test",
            english="Test",
            native="Test",
            category=QuestionCategory.BACKGROUND,
            question_id="bg_001",
            detected_input_language="en",
            user_native_language="en",
            quality_score=0.80,
            confidence_level="high",
            detected_skills=[]
        )

        section2 = CVSection(
            german="Test",
            english="Test",
            native="Test",
            category=QuestionCategory.BACKGROUND,
            question_id="bg_002",
            detected_input_language="en",
            user_native_language="en",
            quality_score=None,  # No score
            confidence_level="high",
            detected_skills=[]
        )

        quality = builder.calculate_category_quality([section1, section2])
        # Only section1 is counted
        assert quality == 0.80

    def test_get_sections_by_quality_filters_correctly(self, builder, sample_cv_sections):
        """Test filtering sections by quality threshold."""
        answers_dict = {s.question_id: s for s in sample_cv_sections}

        cv_data = builder.build_cv_from_answers_dict(
            session_id=1,
            user_id="test_user",
            interview_path="unemployed",
            language_input="en",
            answers_dict=answers_dict
        )

        # Get sections with quality >= 0.80
        filtered = builder.get_sections_by_quality(cv_data, min_quality=0.80)

        # Background: 1 section at 0.85 (included)
        # Experience: 2 sections at 0.80, 0.75 (1 included, 1 excluded)
        # Skills: 1 section at 0.90 (included)
        # Motivation: 1 section at 0.70 (excluded)
        assert len(filtered["background"]) == 1
        assert len(filtered["experience"]) == 1
        assert len(filtered["skills"]) == 1
        assert len(filtered["motivation"]) == 0

    def test_get_sections_by_quality_with_zero_threshold(self, builder, sample_cv_sections):
        """Test that min_quality=0.0 returns all sections."""
        answers_dict = {s.question_id: s for s in sample_cv_sections}

        cv_data = builder.build_cv_from_answers_dict(
            session_id=1,
            user_id="test_user",
            interview_path="unemployed",
            language_input="en",
            answers_dict=answers_dict
        )

        filtered = builder.get_sections_by_quality(cv_data, min_quality=0.0)

        assert len(filtered["background"]) == 1
        assert len(filtered["experience"]) == 2
        assert len(filtered["skills"]) == 1
        assert len(filtered["motivation"]) == 1

    def test_merge_cv_data_combines_sections(self, builder, sample_cv_sections):
        """Test merging two CVData objects."""
        # Create two CVData objects
        sections1 = sample_cv_sections[:3]
        sections2 = sample_cv_sections[3:]

        answers_dict1 = {s.question_id: s for s in sections1}
        answers_dict2 = {s.question_id: s for s in sections2}

        cv1 = builder.build_cv_from_answers_dict(
            session_id=1,
            user_id="test_user",
            interview_path="unemployed",
            language_input="en",
            answers_dict=answers_dict1
        )

        cv2 = builder.build_cv_from_answers_dict(
            session_id=2,
            user_id="test_user",
            interview_path="unemployed",
            language_input="en",
            answers_dict=answers_dict2
        )

        # Merge them
        merged = builder.merge_cv_data(cv1, cv2)

        # Verify combined sections
        assert len(merged.background) == 1
        assert len(merged.experience) == 2
        assert len(merged.skills) == 1
        assert len(merged.motivation) == 1

    def test_merge_cv_data_deduplicates_merged_skills(self, builder, sample_cv_sections):
        """Test that merged CV has deduplicated skills."""
        sections1 = sample_cv_sections[:2]
        sections2 = [sample_cv_sections[2]]  # Skills section with Python

        answers_dict1 = {s.question_id: s for s in sections1}
        answers_dict2 = {s.question_id: s for s in sections2}

        cv1 = builder.build_cv_from_answers_dict(
            session_id=1,
            user_id="test_user",
            interview_path="unemployed",
            language_input="en",
            answers_dict=answers_dict1
        )

        cv2 = builder.build_cv_from_answers_dict(
            session_id=2,
            user_id="test_user",
            interview_path="unemployed",
            language_input="en",
            answers_dict=answers_dict2
        )

        merged = builder.merge_cv_data(cv1, cv2)

        # Python should appear in both cv1 and cv2, should be deduplicated
        assert merged.all_skills.count("Python") == 1

    def test_merge_cv_data_recalculates_quality(self, builder, sample_cv_sections):
        """Test that merged CV recalculates overall quality."""
        sections1 = [sample_cv_sections[0]]  # Quality 0.85
        sections2 = [sample_cv_sections[3]]  # Quality 0.90

        answers_dict1 = {s.question_id: s for s in sections1}
        answers_dict2 = {s.question_id: s for s in sections2}

        cv1 = builder.build_cv_from_answers_dict(
            session_id=1,
            user_id="test_user",
            interview_path="unemployed",
            language_input="en",
            answers_dict=answers_dict1
        )

        cv2 = builder.build_cv_from_answers_dict(
            session_id=2,
            user_id="test_user",
            interview_path="unemployed",
            language_input="en",
            answers_dict=answers_dict2
        )

        merged = builder.merge_cv_data(cv1, cv2)

        # Average of [0.85, 0.90] = 0.875
        assert merged.overall_quality == pytest.approx(0.875, abs=0.01)

    def test_build_cv_with_all_languages(self, builder, sample_cv_sections):
        """Test building CV with different language configurations."""
        answers_dict = {s.question_id: s for s in sample_cv_sections}

        cv_data = builder.build_cv_from_answers_dict(
            session_id=1,
            user_id="test_user",
            interview_path="unemployed",
            language_input="sr",  # Serbian input
            answers_dict=answers_dict,
            language_output_primary="en",  # English output
            language_output_secondary="de"  # German secondary
        )

        assert cv_data.language_input == "sr"
        assert cv_data.language_output_primary == "en"
        assert cv_data.language_output_secondary == "de"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
