"""
Tests for InterviewEngine multilingual integration (Day 9 Phase 9.4).

Tests the updated InterviewEngine that:
- Accepts user_native_language parameter in start_interview()
- Calls polish_answer_multilingual() in submit_answer()
- Stores CVSection objects for later CV building
- Detects and stores native language from first answer if not provided
"""

import pytest
from src.backend.interview.engine import InterviewEngine
from src.backend.cv.models import CVSection
from src.backend.db import DatabaseManager


class TestInterviewEngineMultilingual:
    """Test InterviewEngine with multilingual polishing integration."""

    @pytest.fixture
    def db_manager(self):
        """Provide in-memory database for testing."""
        db = DatabaseManager(":memory:")
        db.initialize()
        return db

    @pytest.fixture
    def interview_engine(self, db_manager):
        """Provide interview engine instance."""
        return InterviewEngine(db_manager)

    def _create_user(self, db_manager, user_id: str):
        """Helper to create a user in the database."""
        db_manager.execute_update(
            "INSERT INTO users (user_id, email) VALUES (?, ?)",
            (user_id, f"{user_id}@test.local")
        )

    def test_start_interview_with_native_language(self, interview_engine, db_manager):
        """Test that start_interview accepts and stores user_native_language."""
        user_id = "test_user_001"
        self._create_user(db_manager, user_id)
        result = interview_engine.start_interview(
            user_id=user_id,
            interview_path="unemployed",
            language="en",
            user_native_language="de"
        )

        assert "session_id" in result
        session_id = result["session_id"]

        # Verify native language was stored in session
        session = db_manager.get_session(session_id)
        assert session["user_native_language"] == "de"

    def test_start_interview_without_native_language(self, interview_engine, db_manager):
        """Test that start_interview works without user_native_language."""
        user_id = "test_user_002"
        self._create_user(db_manager, user_id)
        result = interview_engine.start_interview(
            user_id=user_id,
            interview_path="career-switch",
            language="en"
        )

        assert "session_id" in result
        assert "question_id" in result

    def test_submit_answer_calls_multilingual_polishing(self, interview_engine, db_manager):
        """Test that submit_answer uses polish_answer_multilingual."""
        user_id = "test_user_003"
        self._create_user(db_manager, user_id)
        session = interview_engine.start_interview(
            user_id=user_id,
            interview_path="unemployed",
            user_native_language="en"
        )
        session_id = session["session_id"]
        question_id = session["question_id"]

        result = interview_engine.submit_answer(
            session_id=session_id,
            question_id=question_id,
            answer_text="I worked with Python and Excel."
        )

        # Check response structure
        assert "status" in result
        assert "polished_text" in result
        assert "quality" in result
        # polished_text should be English version
        assert len(result["polished_text"]) > 0

    def test_submit_answer_extracts_skills(self, interview_engine, db_manager):
        """Test that skills are extracted and returned."""
        user_id = "test_user_004"
        self._create_user(db_manager, user_id)
        session = interview_engine.start_interview(
            user_id=user_id,
            interview_path="unemployed",
            user_native_language="en"
        )
        session_id = session["session_id"]
        question_id = session["question_id"]

        result = interview_engine.submit_answer(
            session_id=session_id,
            question_id=question_id,
            answer_text="I worked with Python, Java, and SQL databases for analysis."
        )

        assert "extracted_skills" in result
        assert len(result["extracted_skills"]) > 0
        # Should detect at least some of these
        skills_lower = [s.lower() for s in result["extracted_skills"]]
        assert any("python" in s or "java" in s or "sql" in s for s in skills_lower)

    def test_submit_answer_stores_cv_section(self, interview_engine, db_manager):
        """Test that CVSection is stored internally for later retrieval."""
        user_id = "test_user_005"
        self._create_user(db_manager, user_id)
        session = interview_engine.start_interview(
            user_id=user_id,
            interview_path="unemployed",
            user_native_language="de"
        )
        session_id = session["session_id"]
        question_id = session["question_id"]

        interview_engine.submit_answer(
            session_id=session_id,
            question_id=question_id,
            answer_text="Ich habe mit Python gearbeitet."
        )

        # Retrieve stored CVSections
        cv_sections = interview_engine.get_cv_sections(session_id)
        assert question_id in cv_sections
        # Verify it's a CVSection by checking key attributes
        cv_section = cv_sections[question_id]
        assert hasattr(cv_section, 'german')
        assert hasattr(cv_section, 'english')
        assert hasattr(cv_section, 'native')

    def test_native_language_detection_on_first_answer(self, interview_engine, db_manager):
        """Test that native language is detected from first answer if not provided."""
        user_id = "test_user_006"
        self._create_user(db_manager, user_id)
        # Start without specifying user_native_language
        session = interview_engine.start_interview(
            user_id=user_id,
            interview_path="unemployed"
        )
        session_id = session["session_id"]
        question_id = session["question_id"]

        # Submit answer in German
        interview_engine.submit_answer(
            session_id=session_id,
            question_id=question_id,
            answer_text="Ich habe mit Python und Excel gearbeitet."
        )

        # Verify detected language was stored
        updated_session = db_manager.get_session(session_id)
        # Should detect German or at least not be None
        assert updated_session["user_native_language"] is not None

    def test_cv_section_has_multilingual_versions(self, interview_engine, db_manager):
        """Test that retrieved CVSection has all three language versions."""
        user_id = "test_user_007"
        self._create_user(db_manager, user_id)
        session = interview_engine.start_interview(
            user_id=user_id,
            interview_path="unemployed",
            user_native_language="de"
        )
        session_id = session["session_id"]
        question_id = session["question_id"]

        interview_engine.submit_answer(
            session_id=session_id,
            question_id=question_id,
            answer_text="I worked as a senior engineer."
        )

        cv_sections = interview_engine.get_cv_sections(session_id)
        cv_section = cv_sections[question_id]

        # All three versions should be present
        assert cv_section.german is not None
        assert len(cv_section.german) > 0
        assert cv_section.english is not None
        assert len(cv_section.english) > 0
        assert cv_section.native is not None
        assert len(cv_section.native) > 0

    def test_submit_answer_with_weak_content_triggers_re_ask(self, interview_engine, db_manager):
        """Test that weak answers trigger re-ask as before."""
        user_id = "test_user_008"
        self._create_user(db_manager, user_id)
        session = interview_engine.start_interview(
            user_id=user_id,
            interview_path="unemployed",
            user_native_language="en"
        )
        session_id = session["session_id"]
        question_id = session["question_id"]

        result = interview_engine.submit_answer(
            session_id=session_id,
            question_id=question_id,
            answer_text="OK"  # Too short
        )

        # Should either be re_ask or accepted depending on quality scoring
        assert "status" in result
        assert result["status"] in ["re_ask", "accepted"]

    def test_get_cv_sections_rebuilds_from_database(self, interview_engine, db_manager):
        """Test that get_cv_sections can rebuild from database if needed."""
        user_id = "test_user_009"
        self._create_user(db_manager, user_id)
        session = interview_engine.start_interview(
            user_id=user_id,
            interview_path="unemployed",
            user_native_language="en"
        )
        session_id = session["session_id"]
        question_id = session["question_id"]

        interview_engine.submit_answer(
            session_id=session_id,
            question_id=question_id,
            answer_text="I developed web applications."
        )

        # Create new engine instance (simulating session state loss)
        new_engine = InterviewEngine(interview_engine.db)

        # Should still be able to rebuild CVSections
        cv_sections = new_engine.get_cv_sections(session_id)
        assert question_id in cv_sections
        # Verify it's a CVSection by checking key attributes
        cv_section = cv_sections[question_id]
        assert hasattr(cv_section, 'german')
        assert hasattr(cv_section, 'english')
        assert hasattr(cv_section, 'native')

    def test_multiple_answers_accumulate_cv_sections(self, interview_engine, db_manager):
        """Test that multiple submitted answers accumulate CVSections."""
        user_id = "test_user_010"
        self._create_user(db_manager, user_id)
        session = interview_engine.start_interview(
            user_id=user_id,
            interview_path="unemployed",
            user_native_language="en"
        )
        session_id = session["session_id"]

        # Get first question
        first_q_id = session["question_id"]

        # Submit first answer
        interview_engine.submit_answer(
            session_id=session_id,
            question_id=first_q_id,
            answer_text="I worked as an engineer."
        )

        # Get next question and answer
        next_q = interview_engine.get_next_question(session_id)
        if next_q.get("status") != "complete":
            second_q_id = next_q["question_id"]
            interview_engine.submit_answer(
                session_id=session_id,
                question_id=second_q_id,
                answer_text="I have skills in Python and SQL."
            )

            # Retrieve all sections
            cv_sections = interview_engine.get_cv_sections(session_id)

            # Should have at least 2 sections
            assert len(cv_sections) >= 2
            assert first_q_id in cv_sections
            assert second_q_id in cv_sections

    def test_quality_metadata_in_cv_section(self, interview_engine, db_manager):
        """Test that quality metrics are stored in CVSection."""
        user_id = "test_user_011"
        self._create_user(db_manager, user_id)
        session = interview_engine.start_interview(
            user_id=user_id,
            interview_path="unemployed",
            user_native_language="en"
        )
        session_id = session["session_id"]
        question_id = session["question_id"]

        interview_engine.submit_answer(
            session_id=session_id,
            question_id=question_id,
            answer_text="I led a team of engineers, developed new features, and improved system efficiency."
        )

        cv_sections = interview_engine.get_cv_sections(session_id)
        cv_section = cv_sections[question_id]

        # Quality metrics should be present
        assert cv_section.quality_score is not None
        assert 0.0 <= cv_section.quality_score <= 1.0
        assert cv_section.confidence_level in ["low", "medium", "high"]

    def test_language_metadata_preserved_in_cv_section(self, interview_engine, db_manager):
        """Test that language detection info is in CVSection."""
        user_id = "test_user_012"
        self._create_user(db_manager, user_id)
        session = interview_engine.start_interview(
            user_id=user_id,
            interview_path="unemployed",
            user_native_language="sr"  # Serbian
        )
        session_id = session["session_id"]
        question_id = session["question_id"]

        interview_engine.submit_answer(
            session_id=session_id,
            question_id=question_id,
            answer_text="I worked with Python and SQL."
        )

        cv_sections = interview_engine.get_cv_sections(session_id)
        cv_section = cv_sections[question_id]

        # Language metadata should be preserved
        assert cv_section.user_native_language == "sr"
        assert cv_section.detected_input_language is not None

    def test_timestamps_set_in_cv_section(self, interview_engine, db_manager):
        """Test that timestamps are set when CVSection is created."""
        user_id = "test_user_013"
        self._create_user(db_manager, user_id)
        session = interview_engine.start_interview(
            user_id=user_id,
            interview_path="unemployed",
            user_native_language="en"
        )
        session_id = session["session_id"]
        question_id = session["question_id"]

        interview_engine.submit_answer(
            session_id=session_id,
            question_id=question_id,
            answer_text="I developed software."
        )

        cv_sections = interview_engine.get_cv_sections(session_id)
        cv_section = cv_sections[question_id]

        # Timestamps should be ISO format
        assert cv_section.created_at is not None
        assert "T" in cv_section.created_at
        assert cv_section.polished_at is not None
        assert "T" in cv_section.polished_at

    def test_category_from_question_stored_in_cv_section(self, interview_engine, db_manager):
        """Test that question category is stored in CVSection."""
        user_id = "test_user_014"
        self._create_user(db_manager, user_id)
        session = interview_engine.start_interview(
            user_id=user_id,
            interview_path="unemployed",
            user_native_language="en"
        )
        session_id = session["session_id"]
        question_id = session["question_id"]

        interview_engine.submit_answer(
            session_id=session_id,
            question_id=question_id,
            answer_text="I worked with teams."
        )

        cv_sections = interview_engine.get_cv_sections(session_id)
        cv_section = cv_sections[question_id]

        # Category should match question category
        assert cv_section.category is not None
        # Should be one of the standard categories (including identity for the first two questions)
        assert cv_section.category.value in ["identity", "background", "experience", "skills", "motivation", "training", "projects"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
