"""
Database layer for Tool 2 - SQLite (separate from Tool 1)
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import DATABASE_URL, DB_ECHO

engine = create_engine(
    DATABASE_URL,
    echo=DB_ECHO,
    connect_args={"check_same_thread": False}
)

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
            except sqlite3.OperationalError:
                pass  # Column already exists — normal on upgrade
        raw.close()
    except Exception as exc:
        _log.warning(f"Tool 2 migration skipped (non-fatal): {exc}")
