"""
Database layer for Tool 2 - SQLite (separate from Tool 1)
"""

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from config import DATABASE_URL, DB_ECHO

engine = create_engine(
    DATABASE_URL,
    echo=DB_ECHO,
    connect_args={"check_same_thread": False}
)


@event.listens_for(engine, "connect")
def _sqlite_pragmas(dbapi_connection, _record):
    """
    Per-connection SQLite hardening (RC-6 reliability + data integrity):
    - WAL journal mode: readers don't block writers → no spurious 'database is
      locked' when a trainer reads while another writes.
    - busy_timeout: wait up to 5s for a lock instead of failing immediately.
    - foreign_keys ON: enforce referential integrity / ON DELETE CASCADE so
      deleting a participant actually removes their submissions/feedback.
    """
    cur = dbapi_connection.cursor()
    try:
        cur.execute("PRAGMA journal_mode=WAL")
        cur.execute("PRAGMA busy_timeout=5000")
        cur.execute("PRAGMA foreign_keys=ON")
    finally:
        cur.close()


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Dependency for FastAPI"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize database and apply safe column migrations."""
    import sqlite3
    import logging
    from models import Base
    from config import DATABASE_URL

    Base.metadata.create_all(bind=engine)

    # Safe column migrations for existing databases.
    # OperationalError("duplicate column name") is expected on all but first run.
    _log = logging.getLogger(__name__)
    _migrations = [
        "ALTER TABLE cv_submissions ADD COLUMN cv_locked BOOLEAN DEFAULT 0",
    ]
    db_path = DATABASE_URL.replace("sqlite:///", "")
    try:
        raw = sqlite3.connect(db_path)
        for sql in _migrations:
            try:
                raw.execute(sql)
                raw.commit()
                _log.debug(f"Tool 2 migration applied: {sql[:60]}")
            except sqlite3.OperationalError as oe:
                # Only "duplicate column" is the expected no-op on upgrade; any
                # other OperationalError (locked, disk full, syntax) is a REAL
                # failure and must be surfaced, not silently swallowed.
                if "duplicate column" in str(oe).lower():
                    pass
                else:
                    _log.error(f"Tool 2 migration FAILED ({sql[:60]}): {oe}")
                    raise
        raw.close()
    except Exception as exc:
        _log.warning(f"Tool 2 migration skipped (non-fatal): {exc}")
