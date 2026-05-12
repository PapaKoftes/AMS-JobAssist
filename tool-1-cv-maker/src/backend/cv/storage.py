"""
CV Storage - Persistence layer for CVData objects.

Handles:
1. Saving complete CVData to database
2. Retrieving CVData from database
3. Updating CVData with new sections
4. Transaction-based persistence with crash recovery
"""

import logging
import json
from typing import Optional, Dict, Any
from datetime import datetime

from cv.models import CVData, CVSection

logger = logging.getLogger(__name__)


class CVStorage:
    """Manages persistence of complete multilingual CVData objects."""

    def __init__(self, db_manager):
        """
        Initialize CVStorage.

        Args:
            db_manager: DatabaseManager instance for database operations
        """
        self.db = db_manager

    def save_cv_data(self, cv_data: CVData, session_id: int) -> bool:
        """
        Save complete CVData object to database.

        Serializes CVData to JSON and stores in cv_data table along with raw answers.
        Uses ACID transaction for consistency.

        Args:
            cv_data: Complete CVData object with all sections
            session_id: Associated session ID

        Returns:
            True if save successful, False otherwise

        Raises:
            sqlite3.Error: If database operation fails
        """
        try:
            logger.info(f"Saving CVData for session {session_id}")

            # Serialize CVData to JSON
            cv_dict = cv_data.to_dict()
            polished_output = json.dumps(cv_dict, indent=2)

            # Serialize raw answers if available (stored separately for transparency)
            raw_answers = None
            if hasattr(cv_data, 'raw_answers') and cv_data.raw_answers:
                raw_answers = json.dumps(cv_data.raw_answers, indent=2)

            # Check if cv_data already exists for this session
            existing = self.db.execute_query(
                "SELECT id FROM cv_data WHERE session_id = ?",
                (session_id,)
            )

            if existing:
                # Update existing cv_data
                self.db.execute_update(
                    """
                    UPDATE cv_data
                    SET raw_answers = ?, polished_output = ?, updated_at = datetime('now')
                    WHERE session_id = ?
                    """,
                    (raw_answers, polished_output, session_id)
                )
                logger.info(f"Updated existing CVData for session {session_id}")
            else:
                # Insert new cv_data
                self.db.execute_update(
                    """
                    INSERT INTO cv_data (session_id, raw_answers, polished_output, created_at, updated_at)
                    VALUES (?, ?, ?, datetime('now'), datetime('now'))
                    """,
                    (session_id, raw_answers, polished_output)
                )
                logger.info(f"Created new CVData for session {session_id}")

            return True

        except Exception as e:
            logger.error(f"Error saving CVData: {e}")
            return False

    def get_cv_data(self, session_id: int) -> Optional[CVData]:
        """
        Retrieve complete CVData object from database.

        Reconstructs CVData from JSON stored in cv_data table.

        Args:
            session_id: Session ID to retrieve CVData for

        Returns:
            CVData object if found, None otherwise

        Raises:
            sqlite3.Error: If database query fails
        """
        try:
            results = self.db.execute_query(
                """
                SELECT polished_output FROM cv_data WHERE session_id = ?
                """,
                (session_id,)
            )

            if not results:
                logger.warning(f"No CVData found for session {session_id}")
                return None

            polished_output = results[0]["polished_output"]
            cv_dict = json.loads(polished_output)

            # Reconstruct CVData from dict
            cv_data = CVData.from_dict(cv_dict)
            logger.info(f"Retrieved CVData for session {session_id}")
            return cv_data

        except Exception as e:
            logger.error(f"Error retrieving CVData: {e}")
            return None

    def get_cv_data_with_answers(self, session_id: int) -> Optional[Dict[str, Any]]:
        """
        Retrieve CVData along with raw answers from database.

        Returns both the polished CVData and the raw interview answers.

        Args:
            session_id: Session ID to retrieve data for

        Returns:
            Dict with 'cv_data' (CVData object) and 'raw_answers' (dict of answers)
            None if not found

        Raises:
            sqlite3.Error: If database query fails
        """
        try:
            results = self.db.execute_query(
                """
                SELECT polished_output, raw_answers FROM cv_data WHERE session_id = ?
                """,
                (session_id,)
            )

            if not results:
                logger.warning(f"No CVData found for session {session_id}")
                return None

            result = results[0]
            polished_output = result["polished_output"]
            raw_answers_json = result.get("raw_answers")

            # Reconstruct CVData
            cv_dict = json.loads(polished_output)
            cv_data = CVData.from_dict(cv_dict)

            # Reconstruct raw answers
            raw_answers = {}
            if raw_answers_json:
                raw_answers = json.loads(raw_answers_json)

            logger.info(f"Retrieved CVData with answers for session {session_id}")
            return {
                "cv_data": cv_data,
                "raw_answers": raw_answers
            }

        except Exception as e:
            logger.error(f"Error retrieving CVData with answers: {e}")
            return None

    def update_cv_data(self, cv_data: CVData, session_id: int) -> bool:
        """
        Update existing CVData with modified sections.

        Useful when CV quality is improved or sections are edited by trainers.

        Args:
            cv_data: Updated CVData object
            session_id: Session ID to update

        Returns:
            True if update successful, False otherwise

        Raises:
            sqlite3.Error: If database operation fails
        """
        return self.save_cv_data(cv_data, session_id)

    def delete_cv_data(self, session_id: int) -> bool:
        """
        Delete CVData for a session.

        Args:
            session_id: Session ID to delete

        Returns:
            True if deletion successful, False otherwise

        Raises:
            sqlite3.Error: If database operation fails
        """
        try:
            self.db.execute_update(
                "DELETE FROM cv_data WHERE session_id = ?",
                (session_id,)
            )
            logger.info(f"Deleted CVData for session {session_id}")
            return True

        except Exception as e:
            logger.error(f"Error deleting CVData: {e}")
            return False

    def export_cv_as_json(self, session_id: int) -> Optional[Dict[str, Any]]:
        """
        Export CVData as JSON structure suitable for external use.

        Includes complete multilingual content and metadata.

        Args:
            session_id: Session ID to export

        Returns:
            Dict with CVData structure, None if not found

        Raises:
            sqlite3.Error: If database query fails
        """
        try:
            cv_data = self.get_cv_data(session_id)
            if not cv_data:
                return None

            # Convert to exportable format
            export_dict = cv_data.to_dict()
            export_dict["export_timestamp"] = datetime.now().isoformat()
            export_dict["session_id"] = session_id

            logger.info(f"Exported CVData as JSON for session {session_id}")
            return export_dict

        except Exception as e:
            logger.error(f"Error exporting CVData: {e}")
            return None

    def get_all_cv_data_for_user(self, user_id: str) -> Dict[int, CVData]:
        """
        Retrieve all CVData objects for a user.

        Returns all completed interviews and their associated CV data.

        Args:
            user_id: User ID to retrieve CVData for

        Returns:
            Dict mapping session_id -> CVData object

        Raises:
            sqlite3.Error: If database query fails
        """
        try:
            results = self.db.execute_query(
                """
                SELECT cv_data.session_id, cv_data.polished_output
                FROM cv_data
                JOIN sessions ON cv_data.session_id = sessions.id
                WHERE sessions.user_id = ?
                """,
                (user_id,)
            )

            cv_data_dict = {}
            for result in results:
                session_id = result["session_id"]
                polished_output = result["polished_output"]

                try:
                    cv_dict = json.loads(polished_output)
                    cv_data = CVData.from_dict(cv_dict)
                    cv_data_dict[session_id] = cv_data
                except json.JSONDecodeError as e:
                    logger.warning(f"Failed to deserialize CVData for session {session_id}: {e}")
                    continue

            logger.info(f"Retrieved {len(cv_data_dict)} CVData objects for user {user_id}")
            return cv_data_dict

        except Exception as e:
            logger.error(f"Error retrieving CVData for user: {e}")
            return {}
