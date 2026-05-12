"""
Interview module - Core interview engine with question paths and flow management.

Components:
- paths.py: 5 hardcoded interview paths with questions and examples
- engine.py: Interview engine with flow control, validation, and re-ask logic
"""

from interview.paths import (
    get_interview_path,
    get_question,
    get_all_question_ids,
    get_question_by_order,
    INTERVIEW_PATHS,
)
from interview.engine import InterviewEngine

__all__ = [
    "InterviewEngine",
    "get_interview_path",
    "get_question",
    "get_all_question_ids",
    "get_question_by_order",
    "INTERVIEW_PATHS",
]
