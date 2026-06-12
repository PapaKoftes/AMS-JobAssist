"""
Comprehensive test suite for Autosave & Recovery functionality.

Test Coverage:
- Basic autosave operations (4 tests)
- Transaction atomicity (5 tests)
- Session state verification (6 tests)
- Crash recovery scenarios (6 tests)
- Autosave status queries (3 tests)
- Integration with interview engine (4 tests)

Total: 28 tests
"""

import pytest
import sys
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src" / "backend"))

from interview.autosave import AutosaveManager
from interview.engine import InterviewEngine


class TestAutoSaveBasic:
    """Tests for basic autosave operations."""

    def test_autosave_single_answer(self, db_manager, test_session, test_questions):
        """✅ Single answer saves successfully."""
        autosave = AutosaveManager(db_manager)

        result = autosave.autosave_answer(
            session_id=test_session["id"],
            question_id="u_01",
            answer_text="I have a high school diploma and completed a sales course."
        )

        assert result["status"] == "success"
        assert result["session_id"] == test_session["id"]
        assert result["question_id"] == "u_01"
        assert result["saved_at"]
        assert result["save_number"] == 1

    def test_autosave_increments_count(self, db_manager, test_session, test_questions):
        """✅ Multiple saves increment save counter."""
        autosave = AutosaveManager(db_manager)

        # First save
        result1 = autosave.autosave_answer(test_session["id"], "u_01", "Education text")
        assert result1["save_number"] == 1

        # Second save
        result2 = autosave.autosave_answer(test_session["id"], "u_02", "Experience text")
        assert result2["save_number"] == 2

        # Third save
        result3 = autosave.autosave_answer(test_session["id"], "u_03", "Skills text")
        assert result3["save_number"] == 3

    def test_autosave_records_timestamp(self, db_manager, test_session, test_questions):
        """✅ Autosave records timestamp in ISO format."""
        autosave = AutosaveManager(db_manager)
        before_save = datetime.now()

        result = autosave.autosave_answer(test_session["id"], "u_01", "Test answer")

        after_save = datetime.now()
        assert result["status"] == "success"
        assert result["saved_at"]

        # Parse ISO timestamp and verify it's between before and after
        saved_time = datetime.fromisoformat(result["saved_at"])
        assert before_save <= saved_time <= after_save

    def test_autosave_failed_saves_return_error(self, db_manager, test_session):
        """✅ Failed autosave returns error status."""
        autosave = AutosaveManager(db_manager)

        # Try to save with invalid session_id
        result = autosave.autosave_answer(
            session_id=99999,
            question_id="u_01",
            answer_text="Test"
        )

        assert result["status"] == "failed"
        assert result["error"]


class TestTransactionAtomicity:
    """Tests for transaction-based atomic saves."""

    def test_answer_and_progress_saved_together(self, db_manager, test_session, test_questions):
        """✅ Answer and progress_percent saved atomically."""
        autosave = AutosaveManager(db_manager)

        # Save first answer
        result = autosave.autosave_answer(test_session["id"], "u_01", "Education text")
        assert result["status"] == "success"

        # Verify answer was saved
        answers = db_manager.get_session_answers(test_session["id"])
        assert "u_01" in answers

        # Verify progress was updated
        session = db_manager.get_session(test_session["id"])
        expected_progress = int((1 / 5) * 100)  # 20%
        assert session["progress_percent"] == expected_progress

    def test_autosave_updates_progress_correctly(self, db_manager, test_session, test_questions):
        """✅ Progress updates correctly with each save (20%, 40%, 60%, 80%, 100%)."""
        autosave = AutosaveManager(db_manager)
        expected_progress = [20, 40, 60, 80, 100]

        for i in range(5):
            question_id = f"u_{i+1:02d}"
            autosave.autosave_answer(test_session["id"], question_id, f"Answer {i+1}")

            session = db_manager.get_session(test_session["id"])
            assert session["progress_percent"] == expected_progress[i], \
                f"After {i+1} saves, expected {expected_progress[i]}% but got {session['progress_percent']}%"

    def test_autosave_answer_text_stripped(self, db_manager, test_session, test_questions):
        """✅ Answer text is stripped of whitespace before saving."""
        autosave = AutosaveManager(db_manager)

        answer_with_whitespace = "  \n  Test answer with extra spaces  \n  "
        autosave.autosave_answer(test_session["id"], "u_01", answer_with_whitespace)

        answers = db_manager.get_session_answers(test_session["id"])
        assert answers["u_01"] == "Test answer with extra spaces"

    def test_concurrent_saves_not_corrupted(self, db_manager, test_session, test_questions):
        """✅ Rapid consecutive saves maintain consistency."""
        autosave = AutosaveManager(db_manager)

        # Simulate rapid saves
        for i in range(5):
            question_id = f"u_{i+1:02d}"
            answer_text = f"Answer number {i+1}"
            result = autosave.autosave_answer(test_session["id"], question_id, answer_text)
            assert result["status"] == "success"

        # Verify all answers present and progress correct
        answers = db_manager.get_session_answers(test_session["id"])
        session = db_manager.get_session(test_session["id"])

        assert len(answers) == 5
        assert session["progress_percent"] == 100


class TestSessionStateVerification:
    """Tests for session state consistency checks."""

    def test_consistent_state_passes_verification(self, db_manager, test_session, test_questions):
        """✅ Consistent session state passes verification."""
        autosave = AutosaveManager(db_manager)

        # Save 3 answers
        for i in range(3):
            autosave.autosave_answer(test_session["id"], f"u_{i+1:02d}", f"Answer {i+1}")

        state = autosave.verify_session_state(test_session["id"])

        assert state["session_valid"] == True
        assert state["recovery_possible"] == True
        assert state["answers_saved"] == 3
        assert len(state["issues"]) == 0

    def test_nonexistent_session_fails_verification(self, db_manager):
        """✅ Nonexistent session fails verification."""
        autosave = AutosaveManager(db_manager)

        state = autosave.verify_session_state(99999)

        assert state["session_valid"] == False
        assert state["recovery_possible"] == False
        assert "Session not found" in state["issues"]

    def test_answer_count_exceeding_max_detected(self, db_manager, test_session, test_questions):
        """✅ Answer count > 60 detected as issue (ceiling allows dump-mode synthetics)."""
        autosave = AutosaveManager(db_manager)

        # Save 5 answers normally
        for i in range(5):
            autosave.autosave_answer(test_session["id"], f"cs_{i+1:02d}", f"Answer {i+1}")

        # Manually insert 60 extra answers to exceed the max of 60 (simulating corruption)
        for extra_idx in range(1, 61):
            db_manager.execute_update(
                """
                INSERT OR IGNORE INTO interview_questions
                (question_id, question_text, category, interview_path, question_order, hint, good_example, bad_example, min_length, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, 20, datetime('now'))
                """,
                (f"cs_extra_{extra_idx}", f"Extra question {extra_idx}", "background", "career-switch", 6 + extra_idx, "Extra hint", "Good example", "Bad example")
            )
            db_manager.save_answer(test_session["id"], f"cs_extra_{extra_idx}", f"Extra answer {extra_idx}")

        state = autosave.verify_session_state(test_session["id"])

        assert state["session_valid"] == False
        assert "Unexpected answer count" in str(state["issues"])

    def test_dump_mode_session_is_recoverable(self, db_manager, test_session, test_questions):
        """✅ REGRESSION (resume bug): a dump-mode-shaped session — many synthetic
        answer rows with progress capped at 100 — must be recoverable.

        The old 'progress mismatch' heuristic compared progress_percent against
        answers_count/5*100 (the ancient 5-question formula). Every default-mode
        dump session (8+ rows, progress <= 100) failed it, so /api/interview/resume
        refused with 'Session state is inconsistent' and the frontend silently
        restarted instead of resuming. progress_percent is cosmetic and must never
        block recovery."""
        autosave = AutosaveManager(db_manager)

        # Simulate a dump session: 8 captured-field rows, stored progress 50 %.
        # (Old formula would 'expect' 160 % → >25pp off → refused recovery.)
        # Register dump-style synthetic questions first (the dump endpoint does
        # the same), since the fixture only seeds 5 path questions.
        for i in range(8):
            db_manager.execute_update(
                """INSERT OR IGNORE INTO interview_questions
                   (question_id, question_text, category, interview_path, question_order,
                    hint, good_example, bad_example, min_length, created_at)
                   VALUES (?, '(dump)', 'background', 'dump', 100, '', '', '', 0, datetime('now'))""",
                (f"dump_f_{i+1:02d}",)
            )
            autosave.autosave_answer(test_session["id"], f"dump_f_{i+1:02d}", f"Feld {i+1}")
        db_manager.execute_update(
            "UPDATE sessions SET progress_percent = ? WHERE id = ?",
            (50, test_session["id"]),
        )

        state = autosave.verify_session_state(test_session["id"])
        assert state["session_valid"] is True, state["issues"]
        assert state["recovery_possible"] is True

        recovery = autosave.recover_session(test_session["id"])
        assert recovery["recovered"] is True
        assert recovery["answers_recovered"] == 8

    def test_timestamp_consistency_checked(self, db_manager, test_session, test_questions):
        """✅ Timestamp ordering verified (created <= updated)."""
        autosave = AutosaveManager(db_manager)

        # Save answer (updates updated_at)
        autosave.autosave_answer(test_session["id"], "u_01", "Answer text")

        state = autosave.verify_session_state(test_session["id"])

        # With valid timestamps, should pass
        assert state["session_valid"] == True
        assert "Timestamp inconsistency" not in str(state["issues"])


class TestCrashRecovery:
    """Tests for crash recovery and session resumption."""

    def test_recover_after_zero_answers(self, db_manager, test_session, test_questions):
        """✅ Can recover session with no answers (resume at Q1)."""
        autosave = AutosaveManager(db_manager)

        result = autosave.recover_session(test_session["id"])

        assert result["recovered"] == True
        assert result["answers_recovered"] == 0
        assert result["current_question_index"] == 0  # 0-indexed, so first question

    def test_recover_after_partial_completion(self, db_manager, test_session, test_questions):
        """✅ Can recover session with 2 answers (resume at Q3)."""
        autosave = AutosaveManager(db_manager)

        # Save 2 answers
        autosave.autosave_answer(test_session["id"], "u_01", "Answer 1")
        autosave.autosave_answer(test_session["id"], "u_02", "Answer 2")

        result = autosave.recover_session(test_session["id"])

        assert result["recovered"] == True
        assert result["answers_recovered"] == 2
        assert result["current_question_index"] == 2  # Next question is at index 2

    def test_recover_after_completion(self, db_manager, test_session, test_questions):
        """✅ Can recover completed session (all 5 answers)."""
        autosave = AutosaveManager(db_manager)

        # Save all 5 answers
        for i in range(5):
            autosave.autosave_answer(test_session["id"], f"u_{i+1:02d}", f"Answer {i+1}")

        result = autosave.recover_session(test_session["id"])

        assert result["recovered"] == True
        assert result["answers_recovered"] == 5
        assert result["current_question_index"] == 5  # Past last question

    def test_recover_corrupted_session_fails(self, db_manager, test_session, test_questions):
        """✅ Cannot recover corrupted session state.

        Corruption = a violated invariant (timestamps out of order). NOTE: a
        'wrong-looking' progress_percent is NOT corruption — it's cosmetic and
        differs by flow (dump vs guided); see test_dump_mode_session_is_recoverable."""
        autosave = AutosaveManager(db_manager)

        # Save 3 answers
        for i in range(3):
            autosave.autosave_answer(test_session["id"], f"u_{i+1:02d}", f"Answer {i+1}")

        # Corrupt timestamps: created AFTER updated is impossible in a healthy DB.
        db_manager.execute_update(
            "UPDATE sessions SET created_at = datetime('now', '+1 day') WHERE id = ?",
            (test_session["id"],)
        )

        result = autosave.recover_session(test_session["id"])

        assert result["recovered"] == False
        assert "cannot be recovered" in result["message"]

    def test_recovery_message_includes_answer_count(self, db_manager, test_session, test_questions):
        """✅ Recovery message indicates how many answers were recovered."""
        autosave = AutosaveManager(db_manager)

        # Save 2 answers
        autosave.autosave_answer(test_session["id"], "u_01", "Answer 1")
        autosave.autosave_answer(test_session["id"], "u_02", "Answer 2")

        result = autosave.recover_session(test_session["id"])

        assert "2 answers" in result["message"]
        assert "resume" in result["message"].lower()


class TestAutosaveStatus:
    """Tests for autosave status queries."""

    def test_status_includes_answer_count(self, db_manager, test_session, test_questions):
        """✅ Autosave status includes answer count."""
        autosave = AutosaveManager(db_manager)

        # Save 3 answers
        for i in range(3):
            autosave.autosave_answer(test_session["id"], f"u_{i+1:02d}", f"Answer {i+1}")

        status = autosave.get_autosave_status(test_session["id"])

        assert status["status"] == "ok"
        assert status["answers_saved"] == 3

    def test_status_includes_progress_percent(self, db_manager, test_session, test_questions):
        """✅ Autosave status includes progress percentage."""
        autosave = AutosaveManager(db_manager)

        # Save 2 answers (40%)
        autosave.autosave_answer(test_session["id"], "u_01", "Answer 1")
        autosave.autosave_answer(test_session["id"], "u_02", "Answer 2")

        status = autosave.get_autosave_status(test_session["id"])

        assert status["progress_percent"] == 40

    def test_status_includes_timestamps(self, db_manager, test_session, test_questions):
        """✅ Autosave status includes creation and update timestamps."""
        autosave = AutosaveManager(db_manager)

        autosave.autosave_answer(test_session["id"], "u_01", "Answer 1")

        status = autosave.get_autosave_status(test_session["id"])

        assert status["created_at"]
        assert status["last_updated"]

    def test_status_nonexistent_session_error(self, db_manager):
        """✅ Status query on nonexistent session returns error."""
        autosave = AutosaveManager(db_manager)

        status = autosave.get_autosave_status(99999)

        assert status["status"] == "session_not_found"


class TestAutosaveIntegration:
    """Integration tests with InterviewEngine."""

    def test_autosave_preserves_answer_persistence(self, db_manager, test_user, test_questions):
        """✅ Answers saved via autosave are retrievable."""
        engine = InterviewEngine(db_manager)
        autosave = AutosaveManager(db_manager)

        # Start interview
        result = engine.start_interview(test_user["user_id"], "unemployed")
        session_id = result["session_id"]

        # Submit answer
        answer_text = "I have a high school diploma and completed a sales training course."
        autosave.autosave_answer(session_id, "u_01", answer_text)

        # Verify answer persists
        answers = db_manager.get_session_answers(session_id)
        assert answers["u_01"] == answer_text.strip()

    def test_autosave_enables_session_resume(self, db_manager, test_user, test_questions):
        """✅ After autosave, session can be resumed at correct point."""
        engine = InterviewEngine(db_manager)
        autosave = AutosaveManager(db_manager)

        # Start interview and save answers
        result = engine.start_interview(test_user["user_id"], "unemployed")
        session_id = result["session_id"]

        # Save 3 answers
        for i in range(3):
            autosave.autosave_answer(session_id, f"u_{i+1:02d}", f"Answer {i+1}")

        # Recover session
        recovery = autosave.recover_session(session_id)

        # Should resume at question 4 (index 3)
        assert recovery["current_question_index"] == 3
        assert recovery["recovered"] == True

    def test_autosave_maintains_progress_accuracy(self, db_manager, test_user, test_questions):
        """✅ Progress percent remains accurate after autosave sequence."""
        engine = InterviewEngine(db_manager)
        autosave = AutosaveManager(db_manager)

        result = engine.start_interview(test_user["user_id"], "unemployed")
        session_id = result["session_id"]

        expected_progress = [20, 40, 60, 80, 100]

        for i in range(5):
            autosave.autosave_answer(session_id, f"u_{i+1:02d}", f"Answer {i+1}")

            status = autosave.get_autosave_status(session_id)
            assert status["progress_percent"] == expected_progress[i], \
                f"After {i+1} saves: expected {expected_progress[i]}%, got {status['progress_percent']}%"

    def test_autosave_handles_multiple_sessions(self, db_manager, test_questions):
        """✅ Autosave correctly handles multiple concurrent sessions."""
        autosave = AutosaveManager(db_manager)
        engine = InterviewEngine(db_manager)

        # Create users first (they don't exist yet)
        db_manager.create_user(user_id="user1", email="user1@example.com")
        db_manager.create_user(user_id="user2", email="user2@example.com")

        # Start two separate sessions
        session1 = engine.start_interview("user1", "unemployed")
        session2 = engine.start_interview("user2", "career-switch")

        sid1 = session1["session_id"]
        sid2 = session2["session_id"]

        # Save different answers in each
        autosave.autosave_answer(sid1, "u_01", "User 1 answer")
        autosave.autosave_answer(sid2, "cs_01", "User 2 answer")

        # Verify each session has correct answer
        answers1 = db_manager.get_session_answers(sid1)
        answers2 = db_manager.get_session_answers(sid2)

        assert answers1["u_01"] == "User 1 answer"
        assert answers2["cs_01"] == "User 2 answer"
        assert "cs_01" not in answers1  # Session 1 doesn't have session 2's answer
        assert "u_01" not in answers2   # Session 2 doesn't have session 1's answer
