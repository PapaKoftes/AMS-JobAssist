"""
Pytest configuration and fixtures for AMS JobAssist testing.

Provides:
- Temporary database fixture (in-memory SQLite for fast tests)
- Database manager fixture with schema initialized
- Session/user/answer fixtures for interview testing
- Cleanup and isolation between tests
"""

# demo_test.py is a manual integration script that connects to localhost:8000
# at import time — pytest can't collect it without a running server.
collect_ignore = ["demo_test.py"]

import pytest
import sqlite3
import tempfile
from pathlib import Path
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'backend'))

from db import DatabaseManager


@pytest.fixture
def temp_db_path(tmp_path):
    """Create temporary database file for testing (using pytest's tmp_path for better Windows support)."""
    db_path = str(tmp_path / "test.db")
    yield db_path


@pytest.fixture
def db_manager(temp_db_path):
    """Create and initialize database manager with test schema."""
    manager = DatabaseManager(database_path=temp_db_path)
    try:
        manager.initialize()

        # Populate verb replacements for polish engine testing
        verbs = [
            ("was", "became"),
            ("did", "accomplished"),
            ("worked", "led"),
            ("helped", "facilitated"),
            ("handled", "managed"),
            ("used", "leveraged"),
            ("completed", "accomplished"),
            ("learned", "mastered"),
        ]
        for weak, strong in verbs:
            manager.execute_update(
                "INSERT OR IGNORE INTO verb_replacements (weak_verb, strong_verb) VALUES (?, ?)",
                [weak, strong]
            )

        # Populate skills dictionary for polish engine testing
        skills = [
            ("python", "Python"),
            ("java", "Java"),
            ("javascript", "JavaScript"),
            ("sql", "SQL"),
            ("office", "Microsoft Office"),
            ("excel", "Microsoft Excel"),
            ("word", "Microsoft Word"),
            ("apprenticeship", "Apprenticeship"),
            ("technician", "Technician"),
            ("hardware", "Hardware"),
            ("customer service", "Customer Service"),
            ("retail", "Retail Management"),
        ]
        for key_term, normalized in skills:
            manager.execute_update(
                "INSERT OR IGNORE INTO skills_dictionary (key_term, normalized_skill) VALUES (?, ?)",
                [key_term, normalized]
            )

        yield manager
    finally:
        # Ensure proper cleanup
        manager.close()

        # On Windows, close any remaining handles
        import gc
        gc.collect()

        # Clean up WAL files if they exist
        import os
        for suffix in ['', '-wal', '-shm']:
            try:
                os.remove(temp_db_path + suffix)
            except (OSError, FileNotFoundError):
                pass


@pytest.fixture
def test_user(db_manager):
    """Create a test user in the database."""
    user_id = "test-user-001"
    db_manager.create_user(user_id=user_id, email="test@example.com")
    return {"user_id": user_id, "email": "test@example.com"}


@pytest.fixture
def test_session(db_manager, test_user):
    """Create a test session for the test user."""
    session_id = db_manager.create_session(
        user_id=test_user["user_id"],
        interview_path="career-switch",
        language="en"
    )
    return {"id": session_id, "user_id": test_user["user_id"], "path": "career-switch"}


@pytest.fixture
def test_questions(db_manager):
    """Create comprehensive test interview questions for all paths."""
    questions = [
        # Unemployed path
        ("u_01", "What is your education?", "background", "unemployed", 1, "School, apprenticeship, courses", "High school diploma", "school"),
        ("u_02", "Where do you live?", "background", "unemployed", 2, "City and country", "Munich, Germany", "here"),
        ("u_03", "What work experience do you have?", "experience", "unemployed", 3, "Jobs, internships, volunteering", "Worked in retail for 2 years", "had a job"),
        ("u_04", "What skills do you have?", "skills", "unemployed", 4, "Technical and soft skills", "Python, teamwork, communication", "coding"),
        ("u_05", "Why do you want this job?", "motivation", "unemployed", 5, "Your interests and goals", "I'm interested in problem-solving", "just want a job"),

        # Career-switch path
        ("cs_01", "What was your previous career?", "background", "career-switch", 1, "Your old job or field", "I was in retail management", "something else"),
        ("cs_02", "How much experience do you have?", "experience", "career-switch", 2, "Years and main roles", "8 years as a team lead", "many years"),
        ("cs_03", "What skills transfer to this new role?", "skills", "career-switch", 3, "Leadership, organization, etc.", "Leadership, budget management, team coordination", "I'm a manager"),
        ("cs_04", "Why are you switching careers?", "motivation", "career-switch", 4, "What attracted you to new field", "I want to work in tech and help people", "I want a change"),
        ("cs_05", "What have you learned so far?", "training", "career-switch", 5, "Training, courses, self-study", "I completed 3 online courses in Python", "I'm learning"),

        # Student path
        ("st_01", "What is your current education?", "background", "student", 1, "School, university, apprenticeship", "Currently studying IT at TU Munich", "in school"),
        ("st_02", "What work experience do you have?", "experience", "student", 2, "Internships, part-time work, projects", "Completed internship at a tech startup", "had an internship"),
        ("st_03", "What technical skills do you have?", "skills", "student", 3, "Programming languages, tools, frameworks", "Python, JavaScript, SQL, Git", "some coding"),
        ("st_04", "Have you done any projects?", "projects", "student", 4, "Personal, academic, or team projects", "Built a web app with 3 classmates", "we made something"),
        ("st_05", "What are your career goals?", "motivation", "student", 5, "What you want after graduation", "I want to become a software engineer", "good job"),

        # Pause path
        ("p_01", "What was your previous job?", "experience", "pause", 1, "Your last role before the break", "I was a nurse for 5 years", "health worker"),
        ("p_02", "Why did you take a break?", "background", "pause", 2, "Reason for the career gap", "I took time for family and health", "personal reasons"),
        ("p_03", "What did you do during the break?", "background", "pause", 3, "Activities, learning, volunteering", "I volunteered at a community center and took online courses", "wasn't working"),
        ("p_04", "Do you want to return to your previous field?", "motivation", "pause", 4, "Career direction after break", "Yes, I want to return to nursing", "don't know yet"),
        ("p_05", "What have you maintained from your previous role?", "skills", "pause", 5, "Skills still relevant and current", "Patient care, empathy, communication skills", "I remember stuff"),

        # Other path
        ("o_01", "Tell us about yourself", "background", "other", 1, "Background and introduction", "I'm an experienced graphic designer", "I'm me"),
        ("o_02", "What is your work history?", "experience", "other", 2, "Jobs and roles over time", "Designer for 6 years, worked at 2 agencies", "I've worked"),
        ("o_03", "What tools and skills do you have?", "skills", "other", 3, "Specific tools and competencies", "Adobe Creative Suite, Figma, web design, branding", "design stuff"),
        ("o_04", "What kind of work interests you?", "motivation", "other", 4, "Types of roles and projects you want", "I'm interested in UX/UI and user-centered design", "something interesting"),
        ("o_05", "What can you offer an employer?", "skills", "other", 5, "Your unique value proposition", "Creative problem-solving, user research, design thinking", "I'm good at stuff"),
    ]

    for q_id, text, category, path, order, hint, good_ex, bad_ex in questions:
        db_manager.execute_update(
            """
            INSERT INTO interview_questions
            (question_id, question_text, category, interview_path, question_order, hint, good_example, bad_example, min_length, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 20, datetime('now'))
            """,
            (q_id, text, category, path, order, hint, good_ex, bad_ex)
        )

    return {q_id: text for q_id, text, _, _, _, _, _, _ in questions}


@pytest.fixture
def test_answers(db_manager, test_session, test_questions):
    """Save test answers to the session."""
    answers = [
        ("u_01", "John Doe"),
        ("u_02", "Munich, Germany"),
        ("cs_01", "5 years in IT as a developer"),
        ("cs_02", "Python, JavaScript, SQL"),
        ("st_01", "Problem-solving, teamwork, communication"),
    ]

    for question_id, answer_text in answers:
        db_manager.save_answer(
            session_id=test_session["id"],
            question_id=question_id,
            answer_text=answer_text
        )

    return {
        "session_id": test_session["id"],
        "answers": {q_id: text for q_id, text in answers}
    }
