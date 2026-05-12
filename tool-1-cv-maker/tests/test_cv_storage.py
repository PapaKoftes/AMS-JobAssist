"""
Tests for CVStorage persistence layer (Day 9 Phase 9.5).

Tests the CVStorage class that:
- Saves complete CVData to database as JSON
- Retrieves CVData from database
- Handles updates and deletions
- Exports CVData for external use
"""

import pytest
import json
from src.backend.cv.storage import CVStorage
from src.backend.cv.models import CVData, CVSection, QuestionCategory
from src.backend.db import DatabaseManager


class TestCVStoragePersistence:
    """Test CVStorage persistence operations."""

    @pytest.fixture
    def db_manager(self):
        """Provide in-memory database for testing."""
        db = DatabaseManager(":memory:")
        db.initialize()
        return db

    @pytest.fixture
    def storage(self, db_manager):
        """Provide CVStorage instance."""
        return CVStorage(db_manager)

    @pytest.fixture
    def sample_cv_data(self):
        """Provide sample CVData for testing."""
        cv_data = CVData(session_id=1, user_id="test_user", interview_path="unemployed", language_input="en")
        cv_data.language_output_primary = "de"
        cv_data.language_output_secondary = "en"

        # Add sample sections
        section1 = CVSection(
            german="Ich habe als Software-Ingenieur gearbeitet.",
            english="I worked as a software engineer.",
            native="I worked as a software engineer.",
            category=QuestionCategory.BACKGROUND,
            question_id="bg_001",
            detected_input_language="en",
            user_native_language="en",
            quality_score=0.85,
            confidence_level="high",
            detected_skills=["Software Development"]
        )

        section2 = CVSection(
            german="Ich verwaltete ein Team von fünf Entwicklern.",
            english="I managed a team of five developers.",
            native="I managed a team of five developers.",
            category=QuestionCategory.EXPERIENCE,
            question_id="exp_001",
            detected_input_language="en",
            user_native_language="en",
            quality_score=0.80,
            confidence_level="high",
            detected_skills=["Leadership", "Team Management"]
        )

        cv_data.background.append(section1)
        cv_data.experience.append(section2)

        return cv_data

    def _create_session(self, db_manager, user_id: str) -> int:
        """Helper to create a session."""
        # Check if user exists before creating
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

    def test_save_cv_data_creates_new_record(self, storage, db_manager, sample_cv_data):
        """Test that save_cv_data creates new cv_data record."""
        session_id = self._create_session(db_manager, "user_001")

        result = storage.save_cv_data(sample_cv_data, session_id)
        assert result is True

        # Verify it was saved
        cv_result = db_manager.execute_query(
            "SELECT id FROM cv_data WHERE session_id = ?",
            (session_id,)
        )
        assert len(cv_result) == 1

    def test_save_cv_data_stores_json(self, storage, db_manager, sample_cv_data):
        """Test that CVData is properly serialized to JSON."""
        session_id = self._create_session(db_manager, "user_002")

        storage.save_cv_data(sample_cv_data, session_id)

        # Retrieve raw JSON
        cv_result = db_manager.execute_query(
            "SELECT polished_output FROM cv_data WHERE session_id = ?",
            (session_id,)
        )
        assert len(cv_result) == 1

        polished_output = cv_result[0]["polished_output"]
        cv_dict = json.loads(polished_output)

        # Verify structure
        assert "language_output_primary" in cv_dict
        assert cv_dict["language_output_primary"] == "de"
        assert "background" in cv_dict and "experience" in cv_dict

    def test_get_cv_data_retrieves_object(self, storage, db_manager, sample_cv_data):
        """Test that get_cv_data reconstructs CVData object."""
        session_id = self._create_session(db_manager, "user_003")
        storage.save_cv_data(sample_cv_data, session_id)

        retrieved = storage.get_cv_data(session_id)

        assert retrieved is not None
        assert retrieved.language_output_primary == "de"
        assert len(retrieved.background) >= 1 and len(retrieved.experience) >= 1

    def test_get_cv_data_returns_none_for_missing(self, storage):
        """Test that get_cv_data returns None for non-existent session."""
        retrieved = storage.get_cv_data(999)
        assert retrieved is None

    def test_get_cv_data_preserves_sections(self, storage, db_manager, sample_cv_data):
        """Test that sections are preserved through save/retrieve cycle."""
        session_id = self._create_session(db_manager, "user_004")
        storage.save_cv_data(sample_cv_data, session_id)

        retrieved = storage.get_cv_data(session_id)

        # Verify section content
        assert len(retrieved.background) >= 1 and len(retrieved.experience) >= 1
        section = retrieved.background[0]
        assert section.german is not None
        assert section.english is not None
        assert section.quality_score == 0.85

    def test_get_cv_data_with_answers(self, storage, db_manager, sample_cv_data):
        """Test retrieving CVData along with raw answers."""
        session_id = self._create_session(db_manager, "user_005")

        # Add raw answers to cv_data
        sample_cv_data.raw_answers = {
            "bg_001": "I worked as an engineer",
            "exp_001": "I managed a team"
        }

        storage.save_cv_data(sample_cv_data, session_id)

        # Retrieve with answers
        result = storage.get_cv_data_with_answers(session_id)

        assert result is not None
        assert "cv_data" in result
        assert "raw_answers" in result
        assert result["raw_answers"]["bg_001"] == "I worked as an engineer"

    def test_update_cv_data(self, storage, db_manager, sample_cv_data):
        """Test updating existing CVData."""
        session_id = self._create_session(db_manager, "user_006")
        storage.save_cv_data(sample_cv_data, session_id)

        # Modify and update
        sample_cv_data.language_output_primary = "en"
        update_result = storage.update_cv_data(sample_cv_data, session_id)
        assert update_result is True

        # Verify update
        retrieved = storage.get_cv_data(session_id)
        assert retrieved.language_output_primary == "en"

    def test_delete_cv_data(self, storage, db_manager, sample_cv_data):
        """Test deleting CVData."""
        session_id = self._create_session(db_manager, "user_007")
        storage.save_cv_data(sample_cv_data, session_id)

        # Verify it exists
        assert storage.get_cv_data(session_id) is not None

        # Delete
        result = storage.delete_cv_data(session_id)
        assert result is True

        # Verify it's gone
        assert storage.get_cv_data(session_id) is None

    def test_export_cv_as_json(self, storage, db_manager, sample_cv_data):
        """Test exporting CVData as JSON."""
        session_id = self._create_session(db_manager, "user_008")
        storage.save_cv_data(sample_cv_data, session_id)

        export_dict = storage.export_cv_as_json(session_id)

        assert export_dict is not None
        assert export_dict["language_output_primary"] == "de"
        assert "export_timestamp" in export_dict
        assert export_dict["session_id"] == session_id
        # CVData uses category-specific fields, not a generic "sections" key
        assert "background" in export_dict or "experience" in export_dict or "skills" in export_dict

    def test_export_cv_returns_none_for_missing(self, storage):
        """Test export returns None for non-existent CV."""
        export_dict = storage.export_cv_as_json(999)
        assert export_dict is None

    def test_get_all_cv_data_for_user(self, storage, db_manager, sample_cv_data):
        """Test retrieving all CVData for a user."""
        user_id = "user_009"

        # Create multiple sessions for same user
        session1 = self._create_session(db_manager, user_id)
        session2 = self._create_session(db_manager, user_id)

        # Save CV data to both
        storage.save_cv_data(sample_cv_data, session1)
        storage.save_cv_data(sample_cv_data, session2)

        # Retrieve all
        all_cv_data = storage.get_all_cv_data_for_user(user_id)

        assert len(all_cv_data) == 2
        assert session1 in all_cv_data
        assert session2 in all_cv_data

    def test_get_all_cv_data_returns_empty_for_no_user(self, storage):
        """Test that get_all_cv_data returns empty dict for user with no CV."""
        all_cv_data = storage.get_all_cv_data_for_user("nonexistent_user")
        assert isinstance(all_cv_data, dict)
        assert len(all_cv_data) == 0

    def test_cv_data_roundtrip_preserves_all_fields(self, storage, db_manager, sample_cv_data):
        """Test that all CVData fields survive save/retrieve cycle."""
        session_id = self._create_session(db_manager, "user_010")

        # Set all fields
        sample_cv_data.language_output_primary = "de"
        sample_cv_data.language_output_secondary = "en"
        sample_cv_data.ready_for_export = True
        sample_cv_data.overall_quality = 0.82

        storage.save_cv_data(sample_cv_data, session_id)
        retrieved = storage.get_cv_data(session_id)

        # Verify all fields
        assert retrieved.language_output_primary == "de"
        assert retrieved.language_output_secondary == "en"
        assert retrieved.ready_for_export is True
        assert retrieved.overall_quality == 0.82

    def test_multiple_saves_update_not_duplicate(self, storage, db_manager, sample_cv_data):
        """Test that multiple saves update the same record, not duplicate."""
        session_id = self._create_session(db_manager, "user_011")

        # Save twice
        storage.save_cv_data(sample_cv_data, session_id)
        sample_cv_data.overall_quality = 0.90
        storage.save_cv_data(sample_cv_data, session_id)

        # Should only have one record
        cv_result = db_manager.execute_query(
            "SELECT COUNT(*) as count FROM cv_data WHERE session_id = ?",
            (session_id,)
        )
        assert cv_result[0]["count"] == 1

        # Should have updated quality score
        retrieved = storage.get_cv_data(session_id)
        assert retrieved.overall_quality == 0.90

    def test_handle_empty_cv_data(self, storage, db_manager):
        """Test saving and retrieving empty CVData."""
        session_id = self._create_session(db_manager, "user_012")
        empty_cv = CVData(session_id=1, user_id="test_user", interview_path="unemployed", language_input="en")

        result = storage.save_cv_data(empty_cv, session_id)
        assert result is True

        retrieved = storage.get_cv_data(session_id)
        assert retrieved is not None
        assert (len(retrieved.background) + len(retrieved.experience) + len(retrieved.skills) + len(retrieved.motivation) + len(retrieved.training) + len(retrieved.projects)) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
