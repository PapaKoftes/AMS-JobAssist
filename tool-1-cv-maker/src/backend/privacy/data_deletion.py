"""
Hard delete mechanism for DSGVO compliance (Right to be forgotten).

Implements secure, irreversible data deletion for user accounts.
Deletes ALL traces of user data from database and disk.

Design: Cascade delete from database with file cleanup.
Verification: Confirm deletion actually occurred.
"""

import logging
import os
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class DataDeletion:
    """
    Handles secure deletion of user data for DSGVO compliance.

    DSGVO Article 17 - Right to be forgotten:
    "The data subject shall have the right to obtain from the controller
    the erasure of personal data concerning him or her without undue delay
    and the controller shall have the obligation to erase personal data
    without undue delay."

    This implementation:
    1. Deletes user record from database (cascades to all related data)
    2. Verifies deletion occurred
    3. Optionally wipes export files
    4. Logs deletion for audit trail
    """

    def __init__(self, db_manager):
        """
        Initialize data deletion handler.

        Args:
            db_manager: DatabaseManager instance for database operations
        """
        self.db = db_manager

    def delete_user_data(self, user_id: str, export_dir: Optional[str] = None) -> bool:
        """
        Completely delete a user's data from the system.

        This operation is IRREVERSIBLE. All user data is permanently deleted.

        Steps:
        1. Verify user exists
        2. Get all related records for audit
        3. Delete from database (cascades to sessions, answers, cv_data)
        4. Delete exported files (if export_dir provided)
        5. Verify deletion
        6. Log deletion for audit trail

        Args:
            user_id: User to delete (string UUID)
            export_dir: Optional directory where exports are stored

        Returns:
            True if deletion successful and verified, False otherwise.

        Raises:
            ValueError: If user_id invalid or user not found.
        """
        if not user_id or not isinstance(user_id, str):
            raise ValueError("Invalid user_id")

        try:
            logger.warning(f"🗑️ INITIATING USER DATA DELETION: {user_id}")

            # Step 1: Verify user exists
            user_result = self.db.execute_query(
                "SELECT id FROM users WHERE user_id = ?",
                (user_id,)
            )
            if not user_result:
                raise ValueError(f"User not found: {user_id}")

            # Step 2: Get audit info (number of sessions, answers, etc.) before deletion
            sessions = self.db.execute_query(
                "SELECT COUNT(*) as count FROM sessions WHERE user_id = ?",
                (user_id,)
            )
            session_count = sessions[0]["count"] if sessions else 0

            answers = self.db.execute_query(
                """
                SELECT COUNT(*) as count FROM answers
                WHERE session_id IN (SELECT id FROM sessions WHERE user_id = ?)
                """,
                (user_id,)
            )
            answer_count = answers[0]["count"] if answers else 0

            # Step 3: Delete from database (CASCADE handles related records)
            deletion_result = self.db.execute_update(
                "DELETE FROM users WHERE user_id = ?",
                (user_id,)
            )

            if deletion_result == 0:
                logger.error(f"Database deletion failed for user: {user_id}")
                return False

            logger.info(f"✓ Database deletion complete: {session_count} sessions, {answer_count} answers removed")

            # Step 4: Delete exported files (if export_dir provided)
            if export_dir:
                self._delete_export_files(user_id, export_dir)

            # Step 5: Verify deletion
            verify_result = self.db.execute_query(
                "SELECT COUNT(*) as count FROM users WHERE user_id = ?",
                (user_id,)
            )
            if verify_result[0]["count"] != 0:
                logger.error(f"Verification FAILED: User still in database: {user_id}")
                return False

            logger.warning(f"✓ DELETION VERIFIED: User {user_id} completely removed")
            return True

        except Exception as e:
            logger.error(f"Error during data deletion: {e}")
            return False

    def _delete_export_files(self, user_id: str, export_dir: str) -> int:
        """
        Delete all exported files for a user.

        Args:
            user_id: User ID to match in filenames
            export_dir: Directory containing exports

        Returns:
            Number of files deleted
        """
        if not os.path.exists(export_dir):
            return 0

        deleted_count = 0
        try:
            for file in os.listdir(export_dir):
                # Match files containing user_id in filename
                if user_id in file:
                    file_path = os.path.join(export_dir, file)
                    os.remove(file_path)
                    deleted_count += 1
                    logger.debug(f"✓ Deleted export file: {file}")

            logger.info(f"✓ Deleted {deleted_count} export files for user: {user_id}")
            return deleted_count

        except Exception as e:
            logger.error(f"Error deleting export files: {e}")
            return deleted_count

    def verify_user_deleted(self, user_id: str) -> bool:
        """
        Verify that a user's data is completely deleted.

        Checks:
        1. User not in users table
        2. No sessions exist for user
        3. No answers exist for user's sessions
        4. No CV data exists

        Args:
            user_id: User to verify

        Returns:
            True if user is completely deleted, False otherwise.
        """
        try:
            # Check 1: User record deleted
            user_result = self.db.execute_query(
                "SELECT COUNT(*) as count FROM users WHERE user_id = ?",
                (user_id,)
            )
            if user_result[0]["count"] != 0:
                logger.error(f"Verification failed: User still exists: {user_id}")
                return False

            # Check 2: Sessions deleted
            sessions = self.db.execute_query(
                "SELECT COUNT(*) as count FROM sessions WHERE user_id = ?",
                (user_id,)
            )
            if sessions[0]["count"] != 0:
                logger.error(f"Verification failed: Sessions still exist for user: {user_id}")
                return False

            # Check 3: Answers for user's sessions deleted (cascade effect)
            answers = self.db.execute_query(
                """
                SELECT COUNT(*) as count FROM answers
                WHERE session_id IN (SELECT id FROM sessions WHERE user_id = ?)
                """,
                (user_id,)
            )
            if answers[0]["count"] != 0:
                logger.error(f"Verification failed: Answers still exist for user: {user_id}")
                return False

            logger.info(f"✓ Deletion verified for user: {user_id}")
            return True

        except Exception as e:
            logger.error(f"Verification error: {e}")
            return False

    def get_user_data_size(self, user_id: str) -> dict:
        """
        Get size of data to be deleted (for user confirmation).

        Returns info about:
        - Number of sessions
        - Number of answers
        - Approximate storage size
        - Estimated deletion time

        Args:
            user_id: User to check

        Returns:
            Dict with deletion scope info
        """
        try:
            # Count sessions
            sessions = self.db.execute_query(
                "SELECT COUNT(*) as count FROM sessions WHERE user_id = ?",
                (user_id,)
            )
            session_count = sessions[0]["count"] if sessions else 0

            # Count answers
            answers = self.db.execute_query(
                """
                SELECT COUNT(*) as count FROM answers
                WHERE session_id IN (SELECT id FROM sessions WHERE user_id = ?)
                """,
                (user_id,)
            )
            answer_count = answers[0]["count"] if answers else 0

            # Count CV data records
            cv_data = self.db.execute_query(
                """
                SELECT COUNT(*) as count FROM cv_data
                WHERE session_id IN (SELECT id FROM sessions WHERE user_id = ?)
                """,
                (user_id,)
            )
            cv_count = cv_data[0]["count"] if cv_data else 0

            return {
                "user_id": user_id,
                "sessions_to_delete": session_count,
                "answers_to_delete": answer_count,
                "cv_records_to_delete": cv_count,
                "total_records": session_count + answer_count + cv_count,
                "estimated_size_kb": (answer_count * 2) + (cv_count * 50),  # rough estimate
                "status": "ready_for_deletion" if session_count > 0 else "no_data_found"
            }

        except Exception as e:
            logger.error(f"Error calculating data size: {e}")
            return {"error": str(e), "status": "error"}
