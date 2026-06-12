"""
Autosave mechanism for interview sessions.

Provides transaction-based autosaving with crash recovery.

Design:
- After each answer submission, automatically save to database
- Use database transactions for atomicity
- Track save timestamps for debugging
- Provide recovery mechanism for incomplete sessions
- Log all saves for audit trail
"""

import logging
from typing import Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class AutosaveManager:
    """
    Manages automatic saving of interview state during sessions.

    Features:
    - Transaction-based saves (atomic operations)
    - Save status tracking (success/failure)
    - Recovery from incomplete saves
    - Audit logging of all saves
    """

    def __init__(self, db_manager):
        """
        Initialize autosave manager.

        Args:
            db_manager: DatabaseManager instance
        """
        self.db = db_manager
        self._save_count = 0
        self._last_save_time = None

    def autosave_answer(self, session_id: int, question_id: str, answer_text: str) -> Dict:
        """
        Autosave an answer using a transaction.

        This method wraps answer saving in a database transaction to ensure
        atomicity - either the answer is fully saved or not at all.

        Args:
            session_id: Session ID
            question_id: Question ID being answered
            answer_text: The answer text to save

        Returns:
            Dict with save status:
            {
                "status": "success" or "failed",
                "session_id": session_id,
                "question_id": question_id,
                "saved_at": timestamp,
                "save_number": count of saves in this session
            }

        Raises:
            ValueError: If session or question not found
        """
        try:
            logger.debug(f"Autosaving answer: session={session_id}, question={question_id}")

            # Verify session exists
            session = self.db.get_session(session_id)
            if not session:
                raise ValueError(f"Session not found: {session_id}")

            # Use transaction context for atomic save
            with self.db.get_transaction() as txn:
                # Save answer
                self.db.save_answer(
                    session_id=session_id,
                    question_id=question_id,
                    answer_text=answer_text.strip()
                )

                # Update session progress
                # Progress is calculated as: (questions_answered / total_questions) * 100
                answers = self.db.get_session_answers(session_id)
                progress_percent = int((len(answers) / 5) * 100)  # Assuming 5 questions per path

                self.db.execute_update(
                    """
                    UPDATE sessions
                    SET progress_percent = ?, updated_at = datetime('now')
                    WHERE id = ?
                    """,
                    (progress_percent, session_id)
                )

                # Transaction will auto-commit on successful exit
                self._save_count += 1
                self._last_save_time = datetime.now()

            result = {
                "status": "success",
                "session_id": session_id,
                "question_id": question_id,
                "saved_at": self._last_save_time.isoformat(),
                "save_number": self._save_count
            }

            logger.info(f"✓ Autosaved: session={session_id}, save_number={self._save_count}")
            return result

        except Exception as e:
            logger.error(f"Autosave failed: {e}")
            return {
                "status": "failed",
                "session_id": session_id,
                "question_id": question_id,
                "error": str(e)
            }

    def verify_session_state(self, session_id: int) -> Dict:
        """
        Verify that a session's state is consistent and recoverable.

        Checks:
        1. Session record exists
        2. Session has expected number of answers (0-5)
        3. All answers reference valid questions
        4. Session timestamps are reasonable

        Args:
            session_id: Session to verify

        Returns:
            Dict with verification results:
            {
                "session_valid": True/False,
                "answers_saved": count,
                "progress_percent": value,
                "recovery_possible": True/False,
                "issues": [list of any issues found]
            }
        """
        issues = []

        try:
            session = self.db.get_session(session_id)
            if not session:
                return {
                    "session_valid": False,
                    "recovery_possible": False,
                    "issues": ["Session not found"]
                }

            # Get answers for this session
            answers = self.db.get_session_answers(session_id)
            answers_count = len(answers)

            # Verify answer count is reasonable. The free-form "dump" mode (the
            # DEFAULT flow) registers a synthetic answer row per extracted field
            # per conversation turn (name/location/phone/email/target + several
            # experience/education/skills entries), so legitimate sessions can far
            # exceed the 13 guided questions. Ceiling only catches truly corrupt
            # data (e.g. 999 rows from a write loop).
            _MAX_ANSWERS = 60
            if answers_count > _MAX_ANSWERS:
                issues.append(f"Unexpected answer count: {answers_count} (expected max {_MAX_ANSWERS})")

            # NOTE: an earlier "progress mismatch" heuristic compared the stored
            # progress_percent against answers_count/5 — a formula from the old
            # 5-question flow. Dump sessions (8+ answer rows, progress capped at
            # 100) ALWAYS failed it, so resume was refused for every default-mode
            # session ("Session state is inconsistent"). progress_percent is
            # cosmetic; it can never make a session unsafe to resume. Removed.

            # Verify timestamps are reasonable
            if session["created_at"] and session["updated_at"]:
                # Both should be present and created should be before updated
                if session["created_at"] > session["updated_at"]:
                    issues.append("Timestamp inconsistency: created > updated")

            # Determine if recovery is possible
            recovery_possible = len(issues) == 0 and answers_count >= 0

            result = {
                "session_valid": len(issues) == 0,
                "answers_saved": answers_count,
                "progress_percent": session["progress_percent"],
                "recovery_possible": recovery_possible,
                "issues": issues
            }

            if recovery_possible:
                logger.info(f"✓ Session state verified: {answers_count} answers saved")
            else:
                logger.warning(f"⚠️ Session issues detected: {issues}")

            return result

        except Exception as e:
            logger.error(f"Verification error: {e}")
            return {
                "session_valid": False,
                "recovery_possible": False,
                "issues": [str(e)]
            }

    def recover_session(self, session_id: int) -> Dict:
        """
        Recover a session after a crash or interruption.

        Steps:
        1. Verify session exists
        2. Check for incomplete answers (saved but not fully processed)
        3. Restore session to consistent state
        4. Return current question to resume from

        Args:
            session_id: Session to recover

        Returns:
            Dict with recovery status:
            {
                "recovered": True/False,
                "session_id": session_id,
                "answers_recovered": count,
                "current_question_index": index,
                "message": recovery status message
            }
        """
        try:
            logger.warning(f"Attempting session recovery: session={session_id}")

            # Verify session state
            state = self.verify_session_state(session_id)

            if not state["recovery_possible"]:
                return {
                    "recovered": False,
                    "session_id": session_id,
                    "answers_recovered": 0,
                    "message": "Session state is inconsistent and cannot be recovered",
                    "issues": state["issues"]
                }

            # Session is recoverable
            answers_count = state["answers_saved"]
            current_index = answers_count  # 0-indexed, so next question is at this index

            result = {
                "recovered": True,
                "session_id": session_id,
                "answers_recovered": answers_count,
                "current_question_index": current_index,
                "message": f"Session recovered: {answers_count} answers found, ready to resume"
            }

            logger.info(f"✓ Session recovered: {answers_count} answers, resuming at question {current_index + 1}")
            return result

        except Exception as e:
            logger.error(f"Recovery failed: {e}")
            return {
                "recovered": False,
                "session_id": session_id,
                "answers_recovered": 0,
                "message": f"Recovery failed: {str(e)}"
            }

    def get_autosave_status(self, session_id: int) -> Dict:
        """
        Get autosave status for a session.

        Args:
            session_id: Session to check

        Returns:
            Dict with status information
        """
        try:
            session = self.db.get_session(session_id)
            if not session:
                return {"status": "session_not_found"}

            answers = self.db.get_session_answers(session_id)

            return {
                "status": "ok",
                "session_id": session_id,
                "answers_saved": len(answers),
                "progress_percent": session["progress_percent"],
                "last_updated": session["updated_at"],
                "created_at": session["created_at"]
            }

        except Exception as e:
            logger.error(f"Error getting autosave status: {e}")
            return {"status": "error", "error": str(e)}
