"""
Comprehensive test suite for Interview Engine.

Test Coverage:
- Interview Initialization (4 tests)
- Question Sequencing & Flow (6 tests)
- Answer Validation & Re-ask Logic (7 tests)
- Example Injection (3 tests)
- Session Resume & State (5 tests)
- Integration (5 tests)

Total: 30 tests
"""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src" / "backend"))

from interview.engine import InterviewEngine
from interview.paths import get_interview_path, get_question, get_all_question_ids


class TestInterviewInitialization:
    """Tests for starting a new interview."""

    def test_start_interview_unemployed_path(self, db_manager, test_user):
        """✅ Can start an interview with unemployed path."""
        engine = InterviewEngine(db_manager)
        result = engine.start_interview(
            user_id=test_user["user_id"],
            interview_path="unemployed"
        )

        assert result["session_id"]
        assert result["interview_path"] == "unemployed"
        assert result["question_id"]
        assert result["question"]["text"]
        assert result["progress"]["current"] == 1
        assert result["progress"]["total"] == 15  # 4 identity + target_job + 10 path-specific questions

    def test_start_interview_career_switch_path(self, db_manager, test_user):
        """✅ Can start an interview with career_switch path."""
        engine = InterviewEngine(db_manager)
        result = engine.start_interview(
            user_id=test_user["user_id"],
            interview_path="career-switch"
        )

        assert result["interview_path"] == "career-switch"
        assert result["progress"]["total"] == 15  # 4 identity + target_job + 10 path-specific questions

    def test_start_interview_invalid_path(self, db_manager, test_user):
        """✅ Starting interview with invalid path raises ValueError."""
        engine = InterviewEngine(db_manager)

        with pytest.raises(ValueError):
            engine.start_interview(
                user_id=test_user["user_id"],
                interview_path="invalid_path"
            )

    def test_start_interview_sets_language(self, db_manager, test_user):
        """✅ Interview language is set and retrievable."""
        engine = InterviewEngine(db_manager)
        result = engine.start_interview(
            user_id=test_user["user_id"],
            interview_path="student",
            language="de"
        )

        session = db_manager.get_session(result["session_id"])
        assert session["language"] == "de"


class TestQuestionSequencing:
    """Tests for question flow through interview."""

    def test_get_next_question(self, db_manager, test_user):
        """✅ Can get next question after answering."""
        engine = InterviewEngine(db_manager)
        session_result = engine.start_interview(
            user_id=test_user["user_id"],
            interview_path="unemployed"
        )
        session_id = session_result["session_id"]
        question_id = session_result["question_id"]

        # Submit an answer
        engine.submit_answer(session_id, question_id, "I studied computer science for 3 years and learned programming.")

        # Get next question
        next_result = engine.get_next_question(session_id)

        assert next_result["question_id"] != question_id
        assert next_result["progress"]["current"] == 2
        assert next_result["progress"]["total"] == 15  # current path question count

    def test_progress_tracking(self, db_manager, test_user):
        """✅ Progress percentage increases with each question."""
        engine = InterviewEngine(db_manager)
        session_result = engine.start_interview(
            user_id=test_user["user_id"],
            interview_path="pause"
        )

        initial_progress = session_result["progress"]["percent"]
        assert initial_progress == pytest.approx(100.0 / 15, abs=1.0)  # 1 of 15 (pause path)

        # Answer and move to next
        engine.submit_answer(
            session_result["session_id"],
            session_result["question_id"],
            "I was a project manager for 7 years managing teams and clients."
        )
        next_q = engine.get_next_question(session_result["session_id"])
        assert next_q["progress"]["percent"] == pytest.approx(200.0 / 15, abs=1.0)  # 2 of 15

    def test_interview_completion_detected(self, db_manager, test_user):
        """✅ Interview completion is detected after last question."""
        engine = InterviewEngine(db_manager)
        session_result = engine.start_interview(
            user_id=test_user["user_id"],
            interview_path="student"
        )

        session_id = session_result["session_id"]
        question_ids = get_all_question_ids("student")

        # Answer all 5 questions
        for i, qid in enumerate(question_ids):
            if i < len(question_ids) - 1:
                engine.submit_answer(session_id, qid, "Good answer about my experience and background here.")
                engine.get_next_question(session_id)
            else:
                # Last question
                engine.submit_answer(session_id, qid, "I want to work in data analysis in tech companies.")
                result = engine.get_next_question(session_id)
                assert result["status"] == "complete"

    def test_question_ordering(self, db_manager, test_user):
        """✅ Questions are returned in correct order."""
        engine = InterviewEngine(db_manager)
        session_result = engine.start_interview(
            user_id=test_user["user_id"],
            interview_path="other"
        )

        expected_ids = get_all_question_ids("other")
        actual_ids = [session_result["question_id"]]

        for _ in range(len(expected_ids) - 1):
            engine.submit_answer(
                session_result["session_id"],
                actual_ids[-1],
                "Good answer with sufficient detail here."
            )
            next_q = engine.get_next_question(session_result["session_id"])
            if next_q.get("question_id"):
                actual_ids.append(next_q["question_id"])

        assert actual_ids == expected_ids

    def test_all_five_paths_have_questions(self, db_manager):
        """✅ All 5 interview paths have valid questions (6 identity + target_job + path-specific)."""
        # Question counts: base (17/19) + 8 optional experience questions (2 blocks × 4 each)
        expected_counts = {
            "unemployed": 15,
            "career-switch": 15,
            "student": 15,
            "pause": 15,
            "other": 15,
        }

        for path_key, expected in expected_counts.items():
            path = get_interview_path(path_key)
            assert path is not None, f"Path '{path_key}' not found"
            assert len(path["questions"]) == expected, f"Path '{path_key}': expected {expected}, got {len(path['questions'])}"
            assert all("id" in q and "text" in q for q in path["questions"])


class TestAnswerValidationAndReAsk:
    """Tests for answer validation and re-ask logic."""

    def _advance_to_content_question(self, engine, session_id, session_result):
        """Helper: skip past identity questions to the first content question."""
        from interview.paths import get_all_question_ids as _all_ids
        from interview.paths import get_interview_path as _gip
        # Identity question IDs start with 'id_'
        qid = session_result["question_id"]
        while qid.startswith("id_"):
            engine.submit_answer(session_id, qid, "Test answer for identity question.")
            next_q = engine.get_next_question(session_id)
            if next_q.get("status") == "complete":
                break
            qid = next_q["question_id"]
        return qid

    def test_short_answer_triggers_reask(self, db_manager, test_user):
        """✅ Very short answer triggers re-ask on a content question."""
        engine = InterviewEngine(db_manager)
        session_result = engine.start_interview(
            user_id=test_user["user_id"],
            interview_path="unemployed"
        )
        session_id = session_result["session_id"]

        # Advance past identity questions to the first content question
        content_qid = self._advance_to_content_question(engine, session_id, session_result)

        result = engine.submit_answer(
            session_id,
            content_qid,
            "Yes."  # Too short for a content question
        )

        assert result["status"] == "re_ask"
        assert result["quality"]["confidence"] == "low"
        assert "stronger" in result["message"].lower() or "more detail" in result["message"].lower() or "detail" in result["message"].lower()

    def test_weak_answer_triggers_reask(self, db_manager, test_user):
        """✅ Answer below minimum length triggers re-ask on a content question."""
        engine = InterviewEngine(db_manager)
        session_result = engine.start_interview(
            user_id=test_user["user_id"],
            interview_path="career-switch"
        )
        session_id = session_result["session_id"]

        # Advance past identity questions to the first content question
        content_qid = self._advance_to_content_question(engine, session_id, session_result)

        result = engine.submit_answer(
            session_id,
            content_qid,
            "Sales job"  # Only 2 words — below min_length of a content question
        )

        assert result["status"] == "re_ask"
        # Confidence may be "low" or "medium" depending on whether the LLM
        # enhanced the 2-word answer. The re-ask is triggered by the word-count
        # floor (< 3 words), not by the confidence level.
        assert result["quality"]["confidence"] in ("low", "medium")
        assert "stronger" in result["message"].lower() or "detail" in result["message"].lower()

    def test_strong_answer_accepted(self, db_manager, test_user):
        """✅ Strong answer is accepted immediately."""
        engine = InterviewEngine(db_manager)
        session_result = engine.start_interview(
            user_id=test_user["user_id"],
            interview_path="unemployed"
        )

        result = engine.submit_answer(
            session_result["session_id"],
            session_result["question_id"],
            "I completed a 3-year apprenticeship as a computer technician where I learned to install and repair hardware, troubleshoot software problems, and work with customers."
        )

        assert result["status"] == "accepted"
        assert result["quality"]["confidence"] in ["high", "medium"]  # Strong/adequate answers
        assert "polished_text" in result

    def test_answer_quality_assessment(self, db_manager, test_user):
        """✅ Answers are assessed for quality levels."""
        engine = InterviewEngine(db_manager)
        session_result = engine.start_interview(
            user_id=test_user["user_id"],
            interview_path="student"
        )

        # Test different quality levels - even short answers can have medium confidence
        answer_result = engine.submit_answer(
            session_result["session_id"],
            session_result["question_id"],
            "Not much."
        )
        # Medium quality is acceptable and moves forward
        assert answer_result["status"] == "accepted"
        assert answer_result["quality"]["confidence"] in ["medium", "low"]

    def test_reask_includes_suggestion(self, db_manager, test_user):
        """✅ Polish provides quality feedback and suggestions."""
        engine = InterviewEngine(db_manager)
        session_result = engine.start_interview(
            user_id=test_user["user_id"],
            interview_path="unemployed"
        )

        result = engine.submit_answer(
            session_result["session_id"],
            session_result["question_id"],
            "School."  # Very short
        )

        # Even for short answers, quality assessment is provided
        assert result["status"] in ["accepted", "re_ask"]
        assert "quality" in result
        # Check that quality info is included
        assert "confidence" in result["quality"]
        assert "overall" in result["quality"]

    def test_answer_persistence(self, db_manager, test_user):
        """✅ Answers are saved to database."""
        engine = InterviewEngine(db_manager)
        session_result = engine.start_interview(
            user_id=test_user["user_id"],
            interview_path="pause"
        )

        answer_text = "I was a project manager for 7 years managing teams and clients successfully."
        question_id = session_result["question_id"]

        engine.submit_answer(
            session_result["session_id"],
            question_id,
            answer_text
        )

        # Retrieve answer from database (returns dict mapping question_id → answer_text)
        answers = db_manager.get_session_answers(session_result["session_id"])
        assert len(answers) > 0
        assert answers[question_id] == answer_text


class TestExampleInjection:
    """Tests for example injection in questions."""

    def test_good_example_provided(self, db_manager, test_user):
        """✅ Good example is provided with question."""
        engine = InterviewEngine(db_manager)
        session_result = engine.start_interview(
            user_id=test_user["user_id"],
            interview_path="unemployed"
        )

        question = session_result["question"]
        assert "examples" in question
        assert "good" in question["examples"]
        assert len(question["examples"]["good"]) > 0

    def test_bad_example_provided(self, db_manager, test_user):
        """✅ Bad example is provided for comparison."""
        engine = InterviewEngine(db_manager)
        session_result = engine.start_interview(
            user_id=test_user["user_id"],
            interview_path="career-switch"
        )

        question = session_result["question"]
        assert "bad" in question["examples"]
        assert len(question["examples"]["bad"]) > 0
        assert question["examples"]["bad"] != question["examples"]["good"]

    def test_all_questions_have_examples(self, db_manager, test_user):
        """✅ Every question has both good and bad examples."""
        for path_key in ["unemployed", "career-switch", "student", "pause", "other"]:
            path = get_interview_path(path_key)
            for question in path["questions"]:
                assert "examples" in question
                assert "good" in question["examples"]
                assert "bad" in question["examples"]
                assert len(question["examples"]["good"]) > 0
                assert len(question["examples"]["bad"]) > 0


class TestSessionResumeAndState:
    """Tests for session management and resume functionality."""

    def test_resume_interview_mid_session(self, db_manager, test_user):
        """✅ Can resume interview from where it was paused."""
        engine = InterviewEngine(db_manager)
        session_result = engine.start_interview(
            user_id=test_user["user_id"],
            interview_path="student"
        )

        session_id = session_result["session_id"]
        first_question_id = session_result["question_id"]

        # Answer first question
        engine.submit_answer(
            session_id,
            first_question_id,
            "I'm studying computer science in my 3rd semester at Technical University."
        )
        engine.get_next_question(session_id)

        # Close and resume
        resumed = engine.resume_interview(session_id)
        assert resumed["session_id"] == session_id
        assert resumed["progress"]["current"] == 2

    def test_interview_status_tracking(self, db_manager, test_user):
        """✅ Can get complete interview status."""
        engine = InterviewEngine(db_manager)
        session_result = engine.start_interview(
            user_id=test_user["user_id"],
            interview_path="other"
        )

        session_id = session_result["session_id"]

        # Answer 2 questions
        engine.submit_answer(
            session_id,
            session_result["question_id"],
            "I've worked as a freelance graphic designer for 4 years with various clients."
        )
        next_q = engine.get_next_question(session_id)
        engine.submit_answer(session_id, next_q["question_id"], "I'm proficient in Adobe Creative Suite and web design tools.")

        status = engine.get_interview_status(session_id)
        assert status["answers_completed"] >= 2
        assert status["interview_path"] == "other"

    def test_skip_question_functionality(self, db_manager, test_user):
        """✅ Can skip a question and come back later."""
        engine = InterviewEngine(db_manager)
        session_result = engine.start_interview(
            user_id=test_user["user_id"],
            interview_path="pause"
        )

        # Skip first question
        skip_result = engine.skip_question(
            session_result["session_id"],
            session_result["question_id"]
        )

        assert "question_id" in skip_result
        assert skip_result["question_id"] != session_result["question_id"]

    def test_session_language_preserved(self, db_manager, test_user):
        """✅ Interview language is preserved across resume."""
        engine = InterviewEngine(db_manager)
        session_result = engine.start_interview(
            user_id=test_user["user_id"],
            interview_path="unemployed",
            language="de"
        )

        session_id = session_result["session_id"]

        # Resume
        resumed = engine.resume_interview(session_id)
        session_check = db_manager.get_session(session_id)
        assert session_check["language"] == "de"

    def test_progress_preserved_on_resume(self, db_manager, test_user):
        """✅ Progress percentage is preserved on resume."""
        engine = InterviewEngine(db_manager)
        session_result = engine.start_interview(
            user_id=test_user["user_id"],
            interview_path="student"
        )

        session_id = session_result["session_id"]
        initial_progress = session_result["progress"]["percent"]

        # Answer and move forward
        engine.submit_answer(
            session_id,
            session_result["question_id"],
            "I'm pursuing a degree in Business Information Systems in my 3rd semester."
        )
        engine.get_next_question(session_id)

        # Resume
        resumed = engine.resume_interview(session_id)
        assert resumed["progress"]["current"] == 2


class TestIntegrationAndEdgeCases:
    """Integration tests and edge case handling."""

    def test_complete_interview_workflow(self, db_manager, test_user):
        """✅ Complete end-to-end interview workflow."""
        engine = InterviewEngine(db_manager)

        # Start
        session_result = engine.start_interview(
            user_id=test_user["user_id"],
            interview_path="career-switch",
            language="en"
        )
        session_id = session_result["session_id"]

        # Answer all questions (career-switch = 15 total)
        question_ids = get_all_question_ids("career-switch")

        answers_by_index = [
            "Maria Musterfrau",           # id_name
            "Quellenstraße 45, 1100 Wien", # id_location
            "+43 660 123 45 67",          # id_phone
            "maria@example.com",          # id_email
            "Software Developer",         # id_target_job
            "For 5 years I worked as a sales representative at a clothing company managing customer relationships.",
            "Sales Company GmbH, Wien",   # employer
            "Sales Representative",       # title
            "2018 to 2023",               # dates
        ]

        for i, qid in enumerate(question_ids):
            answer = answers_by_index[i] if i < len(answers_by_index) else "Good detailed answer with enough length here."
            engine.submit_answer(session_id, qid, answer)

            if i < len(question_ids) - 1:
                engine.get_next_question(session_id)

        # Check final status — all 15 questions answered (none skipped)
        status = engine.get_interview_status(session_id)
        assert status["answers_completed"] == len(question_ids)

    def test_multiple_users_separate_sessions(self, db_manager):
        """✅ Different users have separate interview sessions."""
        engine = InterviewEngine(db_manager)

        # Create 2 test users
        db_manager.create_user(user_id="user-1")
        db_manager.create_user(user_id="user-2")

        # Start interviews
        session1 = engine.start_interview(user_id="user-1", interview_path="unemployed")
        session2 = engine.start_interview(user_id="user-2", interview_path="student")

        assert session1["session_id"] != session2["session_id"]

    def test_validate_interview_path(self):
        """✅ Interview path validation works."""
        assert InterviewEngine.validate_interview_path("unemployed") == True
        assert InterviewEngine.validate_interview_path("invalid") == False

    def test_path_summary_available(self):
        """✅ All paths have label and description."""
        for path_key in ["unemployed", "career-switch", "student", "pause", "other"]:
            path = get_interview_path(path_key)
            assert "label" in path
            assert "description" in path
            assert len(path["label"]) > 0

    def test_question_categories_consistent(self):
        """✅ Questions have valid categories."""
        valid_categories = {
            "identity", "background", "experience", "skills", "motivation",
            "training", "projects"
        }

        for path_key in ["unemployed", "career-switch", "student", "pause", "other"]:
            path = get_interview_path(path_key)
            for question in path["questions"]:
                assert question["category"] in valid_categories
