"""
DatabaseManager: SQLite connection pool and transaction layer for AMS JobAssist.

Handles:
- Connection pooling (single-threaded sqlite3 with connection reuse)
- ACID transactions with crash recovery
- Schema verification
- Domain-specific CRUD operations (users, sessions, answers, CV data)
- Automatic database initialization

Philosophy: Transparent crashes. If database corrupts, recover from last good state.
"""

import sqlite3
import json
import threading
from contextlib import contextmanager
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

# Thread-local storage so each thread gets its own SQLite connection.
# SQLite connections must not be shared across threads when using WAL + write workloads.
_tls = threading.local()


class DatabaseManager:
    """SQLite database connection manager with crash recovery and transaction support."""

    def __init__(self, database_path: str = "data/ams_jobassist.db"):
        """
        Initialize database manager with crash recovery.

        Args:
            database_path: Path to SQLite database file.
                          Creates parent directories if they don't exist.

        Raises:
            ValueError: If database_path is invalid.
        """
        self.database_path = Path(database_path)
        self._initialized = False

        # Ensure parent directory exists
        try:
            self.database_path.parent.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            raise ValueError(f"Cannot create database directory: {e}")

    def initialize(self) -> bool:
        """
        Initialize database: create connection, enable crash recovery, load schema.

        Steps:
        1. Open connection with WAL mode (Write-Ahead Logging) for crash safety
        2. Load schema.sql and execute all DDL statements
        3. Verify all 8 tables exist with correct constraints
        4. Initialize skill_dictionary and verb_replacements lookup tables
        5. Set connection parameters (timeout, row factory)

        Returns:
            True if initialization successful, False if schema verification failed.

        Raises:
            sqlite3.Error: If database is corrupted or schema load fails.
        """
        try:
            # Step 1: Open connection with WAL mode
            conn = self._get_connection()
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA synchronous=FULL")  # Crash-safe writes
            logger.info(f"Database opened: {self.database_path}")

            # Step 2: Load and execute schema
            schema_path = Path(__file__).parent / "schema.sql"
            if not schema_path.exists():
                logger.error(f"Schema file not found: {schema_path}")
                return False

            with open(schema_path, "r", encoding="utf-8") as f:
                schema_sql = f.read()

            # Execute schema (may include CREATE TABLE IF NOT EXISTS)
            conn.executescript(schema_sql)
            logger.info("Schema loaded successfully")

            # Step 2b: Safe migrations — add new columns to existing databases.
            # ALTER TABLE fails if the column already exists, so we swallow that error.
            _migrations = [
                "ALTER TABLE sessions ADD COLUMN completed INTEGER DEFAULT 0",
                "ALTER TABLE sessions ADD COLUMN approved INTEGER DEFAULT 0",
                "ALTER TABLE sessions ADD COLUMN approved_at TEXT",
                "ALTER TABLE sessions ADD COLUMN locked INTEGER DEFAULT 0",
                "ALTER TABLE sessions ADD COLUMN needs_review INTEGER DEFAULT 0",
            ]
            for _sql in _migrations:
                try:
                    conn.execute(_sql)
                    conn.commit()
                    logger.debug(f"Migration applied: {_sql[:60]}")
                except Exception as _me:
                    # Only "duplicate column" is the expected no-op on upgrade.
                    # Any other failure (locked DB, disk full) is real and must be
                    # surfaced rather than silently swallowed.
                    if "duplicate column" in str(_me).lower():
                        pass
                    else:
                        logger.error(f"Migration FAILED ({_sql[:60]}): {_me}")
                        raise

            # Step 3: Verify all tables exist
            # Temporarily mark initialized so verify_schema() can call execute_query()
            self._initialized = True
            if not self.verify_schema():
                self._initialized = False
                logger.error("Schema verification failed")
                return False

            # Step 4: Commit initialization
            conn.commit()
            logger.info("Database initialized successfully")
            return True

        except sqlite3.Error as e:
            logger.error(f"Database initialization error: {e}")
            conn = getattr(_tls, "connection", None)
            if conn:
                conn.close()
                _tls.connection = None
            raise

    def _get_connection(self) -> sqlite3.Connection:
        """
        Get or create a per-thread SQLite connection.

        Each thread gets its own connection stored in thread-local storage.
        This is the correct approach for FastAPI/uvicorn multi-threaded deployments.

        Configuration:
        - row_factory=sqlite3.Row (access columns by name)
        - timeout=10s (wait for WAL locks)
        - isolation_level=None (manual transaction control)
        - check_same_thread=True (enforced by TLS — each thread owns its connection)
        """
        conn = getattr(_tls, "connection", None)
        if conn is None:
            conn = sqlite3.connect(
                str(self.database_path),
                timeout=10.0,
                check_same_thread=True,
            )
            conn.row_factory = sqlite3.Row  # Allow dict-like access to rows
            conn.isolation_level = None  # Manual transaction control
            # NOTE: foreign_keys is intentionally left at SQLite's per-connection
            # default (OFF) here. The dump-mode flow writes answers for synthetic
            # identity question_ids that aren't all pre-registered, and enabling
            # FK globally would reject those inserts. Erasure does NOT depend on
            # cascade — DataDeletion deletes children explicitly in order. WAL is
            # set once at init; busy_timeout avoids spurious 'database is locked'.
            conn.execute("PRAGMA busy_timeout=5000")
            _tls.connection = conn
            logger.debug(f"New DB connection for thread {threading.current_thread().name}")
        return conn

    @contextmanager
    def get_transaction(self):
        """
        Context manager for ACID transactions with automatic rollback on error.

        Usage:
            with db.get_transaction() as cursor:
                cursor.execute("INSERT INTO users ...")
                cursor.execute("INSERT INTO sessions ...")
            # Auto-commit on successful exit
            # Auto-rollback if exception raised

        Yields:
            sqlite3.Cursor object for the transaction.

        Raises:
            sqlite3.Error: If transaction fails; propagates after rollback.
        """
        if not self._initialized:
            raise RuntimeError("Database not initialized. Call initialize() first.")

        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("BEGIN TRANSACTION")
            yield cursor
            conn.commit()
            logger.debug("Transaction committed")
        except Exception as e:
            conn.rollback()
            logger.error(f"Transaction rolled back due to error: {e}")
            raise

    def execute_query(self, sql: str, params: Tuple = ()) -> List[Dict[str, Any]]:
        """
        Execute SELECT query and return results as list of dicts.

        Args:
            sql: SELECT statement with ? placeholders for params.
            params: Tuple of parameter values (e.g., (user_id, session_id)).

        Returns:
            List of dicts where each dict is one row with column names as keys.
            Empty list if no results.

        Raises:
            sqlite3.Error: If query execution fails.
        """
        if not self._initialized:
            raise RuntimeError("Database not initialized.")

        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            # Convert sqlite3.Row objects to plain dicts
            return [dict(row) for row in rows]
        except sqlite3.Error as e:
            logger.error(f"Query execution error: {e}, SQL: {sql}")
            raise

    def execute_update(self, sql: str, params: Tuple = ()) -> int:
        """
        Execute INSERT/UPDATE/DELETE and return lastrowid or rows_affected.

        Args:
            sql: INSERT/UPDATE/DELETE statement with ? placeholders.
            params: Tuple of parameter values.

        Returns:
            lastrowid for INSERT (new row's auto-increment ID)
            rows_affected for UPDATE/DELETE (number of rows changed)

        Raises:
            sqlite3.Error: If execution fails (rolls back first).
        """
        if not self._initialized:
            raise RuntimeError("Database not initialized.")

        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(sql, params)
            conn.commit()
            # For INSERT, return lastrowid; for UPDATE/DELETE, return changes()
            result = cursor.lastrowid if "INSERT" in sql.upper() else cursor.rowcount
            logger.debug(f"Update executed: {sql[:50]}... Result: {result}")
            return result
        except sqlite3.Error as e:
            try:
                conn.rollback()
                logger.warning(f"Rolled back failed update: {sql[:50]}...")
            except sqlite3.Error:
                pass  # Rollback failure is secondary
            logger.error(f"Update execution error: {e}, SQL: {sql}")
            raise

    def execute_batch(self, sql: str, param_list: List[Tuple]) -> int:
        """
        Execute multiple INSERT/UPDATE/DELETE statements in a single transaction.

        Args:
            sql: INSERT/UPDATE/DELETE statement with ? placeholders.
            param_list: List of tuples, each tuple is one parameter set.
                       Example: [("user1", 123), ("user2", 456)]

        Returns:
            Total number of rows affected across all statements.

        Raises:
            sqlite3.Error: If any statement fails; all changes rolled back.

        Example:
            db.execute_batch(
                "INSERT INTO answers (session_id, question_id, answer_text) VALUES (?, ?, ?)",
                [
                    (1, 10, "answer 1"),
                    (1, 11, "answer 2"),
                    (1, 12, "answer 3"),
                ]
            )
        """
        if not self._initialized:
            raise RuntimeError("Database not initialized.")

        try:
            with self.get_transaction() as cursor:
                for params in param_list:
                    cursor.execute(sql, params)
                # Transaction auto-commits here on successful exit
            logger.info(f"Batch executed: {len(param_list)} statements")
            return len(param_list)
        except sqlite3.Error as e:
            logger.error(f"Batch execution error: {e}, SQL: {sql}")
            raise

    # ============================================================================
    # Domain-Specific CRUD Methods (Interview System)
    # ============================================================================

    def create_user(self, user_id: str, email: Optional[str] = None) -> int:
        """
        Create a new user (job seeker).

        Args:
            user_id: Unique identifier (UUID recommended).
            email: Optional email address (not used in basic flow).

        Returns:
            Inserted user ID (should match user_id input).

        Raises:
            sqlite3.IntegrityError: If user_id already exists.
        """
        return self.execute_update(
            "INSERT INTO users (user_id, email, created_at) VALUES (?, ?, datetime('now'))",
            (user_id, email)
        )

    def create_session(self, user_id: str, interview_path: str, language: str = "de",
                       user_native_language: Optional[str] = None) -> int:
        """
        Create a new interview session.

        Args:
            user_id: User identifier from users table.
            interview_path: One of: 'unemployed', 'career-switch', 'student', 'pause', 'other'.
            language: Input language (default 'de' for German).
            user_native_language: User's native language ISO 639-1 code (e.g. 'sr', 'pl', 'de').

        Returns:
            New session ID (auto-increment primary key).

        Raises:
            sqlite3.IntegrityError: If user_id doesn't exist.
        """
        return self.execute_update(
            """
            INSERT INTO sessions (user_id, interview_path, language, user_native_language,
                                 current_question, progress_percent, created_at, updated_at)
            VALUES (?, ?, ?, ?, 1, 0, datetime('now'), datetime('now'))
            """,
            (user_id, interview_path, language, user_native_language)
        )

    def save_answer(self, session_id: int, question_id: str, answer_text: str) -> int:
        """
        Save or update a user's answer to a question (autosave operation).

        Args:
            session_id: Current session ID.
            question_id: Question being answered.
            answer_text: User's raw input (may be in any language).

        Returns:
            Answer ID (or updated row count if already exists).

        Raises:
            sqlite3.IntegrityError: If session_id or question_id invalid.
        """
        # Check if answer already exists for this session/question
        existing = self.execute_query(
            "SELECT id FROM answers WHERE session_id = ? AND question_id = ?",
            (session_id, question_id)
        )

        if existing:
            # Update existing answer
            return self.execute_update(
                """
                UPDATE answers
                SET answer_text = ?, updated_at = datetime('now')
                WHERE session_id = ? AND question_id = ?
                """,
                (answer_text, session_id, question_id)
            )
        else:
            # Insert new answer
            return self.execute_update(
                """
                INSERT INTO answers (session_id, question_id, answer_text, created_at, updated_at)
                VALUES (?, ?, ?, datetime('now'), datetime('now'))
                """,
                (session_id, question_id, answer_text)
            )

    def get_session_answers(self, session_id: int) -> Dict[str, str]:
        """
        Retrieve all answers for a session (resume functionality).

        Args:
            session_id: Session to retrieve.

        Returns:
            Dict mapping question_id (str) → answer_text.
            Example: {"u_01": "John Doe", "u_02": "Munich", "u_03": "5 years in IT"}

        Raises:
            sqlite3.Error: If query fails.
        """
        results = self.execute_query(
            "SELECT question_id, answer_text FROM answers WHERE session_id = ? ORDER BY question_id",
            (session_id,)
        )
        return {row["question_id"]: row["answer_text"] for row in results}

    def get_session(self, session_id: int) -> Optional[Dict[str, Any]]:
        """
        Retrieve complete session state (for resume).

        Args:
            session_id: Session to retrieve.

        Returns:
            Dict with session metadata:
            {
                "id": 1,
                "user_id": "uuid-123",
                "interview_path": "career-switch",
                "language": "en",
                "user_native_language": "de",
                "current_question": 5,
                "progress_percent": 45,
                "created_at": "2026-04-22T10:30:00",
                "updated_at": "2026-04-22T11:45:00"
            }
            None if session not found.
        """
        results = self.execute_query(
            """
            SELECT id, user_id, interview_path, language, user_native_language, current_question,
                   progress_percent, completed, approved, approved_at, locked, needs_review,
                   created_at, updated_at
            FROM sessions WHERE id = ?
            """,
            (session_id,)
        )
        return results[0] if results else None

    def update_session_progress(self, session_id: int, current_question: int, progress_percent: int) -> int:
        """
        Update session progress (called after each answer saved).

        Args:
            session_id: Session to update.
            current_question: Next question to ask.
            progress_percent: Percentage of interview complete (0-100).

        Returns:
            Number of rows updated (1 if successful).
        """
        return self.execute_update(
            """
            UPDATE sessions
            SET current_question = ?, progress_percent = ?, updated_at = datetime('now')
            WHERE id = ?
            """,
            (current_question, progress_percent, session_id)
        )

    def save_cv_data(self, session_id: int, raw_answers: Dict[str, Any],
                    polished_output: Optional[Dict[str, Any]] = None) -> int:
        """
        Save polished CV data (called after interview complete).

        Args:
            session_id: Completed session.
            raw_answers: User's original answers (dict, stored as JSON).
            polished_output: Polished CV data (dict, stored as JSON). None initially.

        Returns:
            CV data record ID.
        """
        return self.execute_update(
            """
            INSERT INTO cv_data (session_id, raw_answers, polished_output, created_at, updated_at)
            VALUES (?, ?, ?, datetime('now'), datetime('now'))
            """,
            (session_id, json.dumps(raw_answers), json.dumps(polished_output) if polished_output else None)
        )

    def get_cv_data(self, session_id: int) -> Optional[Dict[str, Any]]:
        """
        Retrieve CV data for a session.

        Args:
            session_id: Session with CV data.

        Returns:
            Dict with raw_answers and polished_output (parsed from JSON).
            None if no CV data found.
        """
        results = self.execute_query(
            "SELECT raw_answers, polished_output FROM cv_data WHERE session_id = ?",
            (session_id,)
        )
        if not results:
            return None

        row = results[0]
        return {
            "raw_answers": json.loads(row["raw_answers"]) if row["raw_answers"] else {},
            "polished_output": json.loads(row["polished_output"]) if row["polished_output"] else None
        }

    def verify_schema(self) -> bool:
        """
        Verify all 8 required tables exist with correct structure.

        Checks:
        - users table exists with user_id PK
        - sessions table exists with id PK
        - interview_questions table exists
        - answers table exists with foreign keys
        - cv_data table exists
        - exports table exists
        - skills_dictionary table exists
        - verb_replacements table exists

        Returns:
            True if all tables present and valid, False otherwise.
        """
        required_tables = [
            "users",
            "sessions",
            "interview_questions",
            "answers",
            "cv_data",
            "exports",
            "skills_dictionary",
            "verb_replacements"
        ]

        try:
            for table_name in required_tables:
                results = self.execute_query(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
                    (table_name,)
                )
                if not results:
                    logger.error(f"Required table missing: {table_name}")
                    return False

            logger.info(f"Schema verification passed: {len(required_tables)} tables found")
            return True

        except sqlite3.Error as e:
            logger.error(f"Schema verification error: {e}")
            return False

    def close(self) -> None:
        """
        Close database connection and cleanup resources.

        Safe to call multiple times (idempotent).
        """
        conn = getattr(_tls, "connection", None)
        if conn:
            try:
                conn.close()
                _tls.connection = None
                self._initialized = False
                logger.info("Database connection closed")
            except sqlite3.Error as e:
                logger.error(f"Error closing database: {e}")

    def __del__(self):
        """Cleanup on garbage collection (safety net)."""
        self.close()

    def __enter__(self):
        """Context manager entry."""
        if not self._initialized:
            self.initialize()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
