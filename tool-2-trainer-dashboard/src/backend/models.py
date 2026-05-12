"""
SQLAlchemy models for Tool 2 - Trainer Dashboard

Stores:
- Participant information (imported from Tool 1)
- Submitted CVData objects (as JSON)
- Trainer feedback and approvals (audit trail)
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON, Float, Index
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()


class Participant(Base):
    """Trainer's participant / student"""
    __tablename__ = "participants"

    id = Column(Integer, primary_key=True)
    user_id = Column(String(255), unique=True, index=True)  # From Tool 1
    cohort_id = Column(String(255), index=True)  # Trainer's cohort/group
    name = Column(String(255))
    email = Column(String(255))

    # Status (indexed for fast filtering)
    status = Column(String(50), default="pending", index=True)  # pending, in_review, approved, rejected
    interview_path = Column(String(50))  # unemployed, career-switch, etc.

    # Tracking (use callable default= to avoid shared mutable datetime)
    first_imported_at = Column(DateTime, default=datetime.now)
    last_updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    completed_at = Column(DateTime, nullable=True)

    # Feedback
    trainer_notes = Column(Text, nullable=True)
    feedback = Column(Text, nullable=True)

    # Composite index for common query: filter by cohort + status
    __table_args__ = (
        Index("ix_participants_cohort_status", "cohort_id", "status"),
    )


class CVSubmission(Base):
    """A submitted CV (can be multiple per participant for revisions)"""
    __tablename__ = "cv_submissions"

    id = Column(Integer, primary_key=True)
    participant_id = Column(Integer, index=True)  # Links to Participant
    user_id = Column(String(255), index=True)  # Denormalized from Tool 1

    # CV Data (stored as JSON for compatibility with Tool 1)
    cv_data_json = Column(JSON)  # Complete CVData object from Tool 1

    # Quality & Status
    overall_quality = Column(Float)  # From CVData.overall_quality
    ready_for_export = Column(Boolean, default=False)

    # Trainer Review
    approval_status = Column(String(50), default="pending", index=True)
    approval_timestamp = Column(DateTime, nullable=True)
    approved_by = Column(String(255), nullable=True)  # Trainer username

    # Lock status (trainer can lock CV to prevent further participant edits)
    cv_locked = Column(Boolean, default=False)

    # Versioning
    version = Column(Integer, default=1)  # Revision number
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Language & Export
    language_primary = Column(String(5), default="de")  # German by default
    language_secondary = Column(String(5), default="en")

    # Composite index for looking up latest submission per participant
    __table_args__ = (
        Index("ix_cv_submissions_participant_version", "participant_id", "version"),
    )


class TrainerFeedback(Base):
    """Detailed feedback on specific CV sections — also used as audit trail"""
    __tablename__ = "trainer_feedback"

    id = Column(Integer, primary_key=True)
    submission_id = Column(Integer, index=True)
    participant_id = Column(Integer, index=True)

    # Feedback details
    category = Column(String(50))  # background, experience, skills, approval, bulk_approval
    feedback_text = Column(Text)
    suggestion = Column(Text, nullable=True)

    # Status
    addressed = Column(Boolean, default=False)

    # Metadata
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class ExportLog(Base):
    """Track exports for auditing and reuse"""
    __tablename__ = "export_logs"

    id = Column(Integer, primary_key=True)
    participant_id = Column(Integer, index=True)
    submission_id = Column(Integer, index=True)

    # Export details
    export_format = Column(String(50))  # pdf, docx, json
    export_language = Column(String(5))
    file_path = Column(String(255))
    file_size = Column(Integer)  # bytes

    # Metadata
    exported_at = Column(DateTime, default=datetime.now)
    exported_by = Column(String(255))  # Trainer


class CohortMetrics(Base):
    """Aggregate metrics for a cohort (calculated periodically)"""
    __tablename__ = "cohort_metrics"

    id = Column(Integer, primary_key=True)
    cohort_id = Column(String(255), unique=True, index=True)

    # Counts
    total_participants = Column(Integer, default=0)
    completed_count = Column(Integer, default=0)
    approved_count = Column(Integer, default=0)
    pending_count = Column(Integer, default=0)

    # Quality
    avg_quality_score = Column(Float, default=0.0)
    min_quality_score = Column(Float, default=0.0)
    max_quality_score = Column(Float, default=0.0)

    # Dates
    cohort_created = Column(DateTime)
    cohort_completed_by = Column(DateTime, nullable=True)
    metrics_updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
