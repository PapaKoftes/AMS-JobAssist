"""
Tests for PolishEngine multilingual version (Day 9 Phase 9.2).

Tests the new polish_answer_multilingual() method that:
- Generates 3 language versions (German, English, native)
- Returns CVSection objects (not dicts)
- Preserves all quality scoring and skill extraction
- Handles multiple languages and native language preferences
"""

import pytest
from src.backend.polish.engine import PolishEngine
from src.backend.cv.models import CVSection, QuestionCategory
from src.backend.db import DatabaseManager


class TestPolishAnswerMultilingual:
    """Test multilingual polishing with CVSection output."""

    @pytest.fixture
    def db_manager(self):
        """Provide in-memory database for testing."""
        db = DatabaseManager(":memory:")
        db.initialize()
        return db

    @pytest.fixture
    def polish_engine(self, db_manager):
        """Provide polish engine instance."""
        return PolishEngine(db_manager)

    def test_returns_cv_section(self, polish_engine):
        """Test that polish_answer_multilingual returns CVSection object."""
        result = polish_engine.polish_answer_multilingual(
            answer_text="I worked with Python and Excel.",
            category="experience",
            question_id="exp_001",
            user_native_language="en"
        )

        assert hasattr(result, "german") and hasattr(result, "english") and hasattr(result, "native")
        assert hasattr(result, 'german')
        assert hasattr(result, 'english')
        assert hasattr(result, 'native')

    def test_returns_three_language_versions(self, polish_engine):
        """Test that all three language versions are populated."""
        result = polish_engine.polish_answer_multilingual(
            answer_text="I led a team of five engineers.",
            category="experience",
            question_id="exp_001",
            user_native_language="de"
        )

        assert len(result.german) > 0, "German version should be populated"
        assert len(result.english) > 0, "English version should be populated"
        assert len(result.native) > 0, "Native version should be populated"

    def test_question_metadata_stored(self, polish_engine):
        """Test that question metadata is properly stored in CVSection."""
        result = polish_engine.polish_answer_multilingual(
            answer_text="I improved system performance.",
            category="experience",
            question_id="exp_002",
            user_native_language="en"
        )

        assert result.question_id == "exp_002"
        assert result.category == QuestionCategory.EXPERIENCE

    def test_language_detection_stored(self, polish_engine):
        """Test that detected language is stored in CVSection."""
        # English input
        result_en = polish_engine.polish_answer_multilingual(
            answer_text="I worked with software development tools.",
            category="skills",
            question_id="sk_001",
            user_native_language="en"
        )
        assert result_en.detected_input_language == "en"

    def test_native_language_preference_in_native_field(self, polish_engine):
        """Test that native version matches user's native language preference."""
        # German native
        result_de = polish_engine.polish_answer_multilingual(
            answer_text="I managed the project.",
            category="experience",
            question_id="exp_003",
            user_native_language="de"
        )
        # For German native language, native should equal German
        assert result_de.native == result_de.german

        # English native
        result_en = polish_engine.polish_answer_multilingual(
            answer_text="I managed the project.",
            category="experience",
            question_id="exp_003",
            user_native_language="en"
        )
        # For English native language, native should equal English
        assert result_en.native == result_en.english

    def test_skill_extraction_preserved(self, polish_engine):
        """Test that skill extraction works in multilingual mode."""
        result = polish_engine.polish_answer_multilingual(
            answer_text="I worked with Python, Java, and SQL databases.",
            category="skills",
            question_id="sk_001",
            user_native_language="en"
        )

        assert len(result.detected_skills) > 0, "Skills should be extracted"
        assert any("Python" in skill for skill in result.detected_skills)

    def test_quality_score_calculated(self, polish_engine):
        """Test that quality score is properly calculated."""
        result = polish_engine.polish_answer_multilingual(
            answer_text="I led a large team, improved efficiency, and trained new staff.",
            category="experience",
            question_id="exp_001",
            user_native_language="en"
        )

        assert 0.0 <= result.quality_score <= 1.0, "Quality score should be in range [0, 1]"
        assert result.confidence_level in ["low", "medium", "high"]

    def test_verb_enforcement_in_all_languages(self, polish_engine):
        """Test that strong verbs are enforced in multiple languages."""
        result = polish_engine.polish_answer_multilingual(
            answer_text="I worked with a team and helped improve efficiency.",
            category="experience",
            question_id="exp_001",
            user_native_language="de"
        )

        # English should have strong verbs
        english_lower = result.english.lower()
        # "helped" should become "supported" or similar action verb
        assert "helped" not in english_lower or "support" in english_lower

    def test_empty_answer_handling(self, polish_engine):
        """Test handling of empty answers."""
        result = polish_engine.polish_answer_multilingual(
            answer_text="",
            category="experience",
            question_id="exp_001",
            user_native_language="en"
        )

        assert hasattr(result, "german") and hasattr(result, "english") and hasattr(result, "native")
        assert result.german == ""
        assert result.english == ""
        assert result.quality_score == 0.0

    def test_timestamps_set(self, polish_engine):
        """Test that creation and polish timestamps are set."""
        result = polish_engine.polish_answer_multilingual(
            answer_text="I developed software solutions.",
            category="experience",
            question_id="exp_001",
            user_native_language="en"
        )

        assert result.created_at is not None
        assert result.polished_at is not None
        # Both should be ISO format strings
        assert "T" in result.created_at  # ISO format includes T
        assert "T" in result.polished_at

    def test_category_conversion(self, polish_engine):
        """Test that category string is converted to QuestionCategory enum."""
        for category_str in ["background", "experience", "skills", "motivation", "training", "projects"]:
            result = polish_engine.polish_answer_multilingual(
                answer_text="Test answer",
                category=category_str,
                question_id=f"q_{category_str}",
                user_native_language="en"
            )

            assert hasattr(result.category, "value")
            assert result.category.value == category_str

    def test_realistic_work_experience(self, polish_engine):
        """Test with realistic work experience text."""
        cv_text = (
            "I worked as a senior software engineer. "
            "I managed a team of five developers. "
            "I helped improve system performance by thirty percent. "
            "I used Python, Java, and SQL technologies."
        )
        result = polish_engine.polish_answer_multilingual(
            answer_text=cv_text,
            category="experience",
            question_id="exp_001",
            user_native_language="de"
        )

        assert len(result.english) > 0
        assert len(result.german) > 0
        assert len(result.detected_skills) > 0
        assert result.quality_score > 0.3  # Should have decent quality

    def test_multiple_native_languages(self, polish_engine):
        """Test that different native languages are handled correctly."""
        native_languages = ["de", "en", "sr", "uk", "tr", "it", "fr"]
        answer_text = "I led the development team."

        for lang in native_languages:
            result = polish_engine.polish_answer_multilingual(
                answer_text=answer_text,
                category="experience",
                question_id="exp_001",
                user_native_language=lang
            )

            assert hasattr(result, "german") and hasattr(result, "english") and hasattr(result, "native")
            assert result.user_native_language == lang
            # All should have content
            assert result.english.strip()
            assert result.german.strip()

    def test_error_gracefully_returns_section(self, polish_engine):
        """Test that errors return a valid CVSection (not raising exceptions)."""
        # Even with problematic input, should return CVSection
        result = polish_engine.polish_answer_multilingual(
            answer_text="!!!@@@###",  # Problematic but should still work
            category="experience",
            question_id="exp_001",
            user_native_language="en"
        )

        assert hasattr(result, "german") and hasattr(result, "english") and hasattr(result, "native")
        # Should have fallback values
        assert result.german is not None
        assert result.english is not None

    def test_none_native_language_handled(self, polish_engine):
        """Test that None native language is handled gracefully."""
        result = polish_engine.polish_answer_multilingual(
            answer_text="I worked with Python.",
            category="skills",
            question_id="sk_001",
            user_native_language=None
        )

        assert hasattr(result, "german") and hasattr(result, "english") and hasattr(result, "native")
        assert result.user_native_language in [None, result.detected_input_language, "unknown"]

    def test_all_question_categories(self, polish_engine):
        """Test that all question categories are properly handled."""
        categories = ["background", "experience", "skills", "motivation", "training", "projects"]

        for cat in categories:
            result = polish_engine.polish_answer_multilingual(
                answer_text=f"Sample {cat} answer",
                category=cat,
                question_id=f"q_{cat}",
                user_native_language="en"
            )

            assert result.category.value == cat
            assert hasattr(result, "german") and hasattr(result, "english") and hasattr(result, "native")


class TestCVSectionMultilingualIntegration:
    """Test integration of CVSection with multilingual data."""

    @pytest.fixture
    def db_manager(self):
        """Provide in-memory database for testing."""
        db = DatabaseManager(":memory:")
        db.initialize()
        return db

    @pytest.fixture
    def polish_engine(self, db_manager):
        """Provide polish engine instance."""
        return PolishEngine(db_manager)

    def test_cv_section_serializable(self, polish_engine):
        """Test that CVSection with multilingual data can be serialized."""
        result = polish_engine.polish_answer_multilingual(
            answer_text="I developed web applications.",
            category="experience",
            question_id="exp_001",
            user_native_language="de"
        )

        # Should be serializable to dict
        section_dict = result.to_dict()
        assert isinstance(section_dict, dict)
        assert section_dict["german"] == result.german
        assert section_dict["english"] == result.english
        assert section_dict["native"] == result.native

    def test_cv_section_deserializable(self, polish_engine):
        """Test that CVSection can be created from dict."""
        result = polish_engine.polish_answer_multilingual(
            answer_text="I managed projects.",
            category="experience",
            question_id="exp_001",
            user_native_language="en"
        )

        # Convert to dict and back
        section_dict = result.to_dict()
        restored = CVSection.from_dict(section_dict)

        assert restored.german == result.german
        assert restored.english == result.english
        assert restored.native == result.native
        assert restored.question_id == result.question_id


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
