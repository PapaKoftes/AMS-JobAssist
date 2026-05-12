"""
Interview Engine - Core logic for guided interview flow.

Handles:
1. Question sequencing
2. Example injection (showing good/bad examples to guide users)
3. Re-ask logic (when answers are too short or weak)
4. Answer validation
5. State tracking
6. Transaction-based autosaving with crash recovery
"""

import logging
from typing import Optional, Dict, List, Tuple
from datetime import datetime

from interview.paths import (
    get_interview_path,
    get_question,
    get_all_question_ids,
    get_question_by_order,
    get_localized_question,
)
from interview.autosave import AutosaveManager
from polish.engine import PolishEngine
from cv.models import CVSection, QuestionCategory

logger = logging.getLogger(__name__)

# Sentinel value written to the DB when a question is skipped
ANSWER_SKIPPED = "[SKIPPED]"


class InterviewEngine:
    """
    Manages interview flow through questions with example guidance and validation.
    """

    def __init__(self, db_manager):
        """
        Initialize interview engine.

        Args:
            db_manager: DatabaseManager instance
        """
        self.db = db_manager
        self.autosave = AutosaveManager(db_manager)
        self.polish = PolishEngine(db_manager)
        self._ensure_questions_loaded()

    def start_interview(self, user_id: str, interview_path: str, language: str = "de", user_native_language: Optional[str] = None) -> Dict:
        """
        Start a new interview session for a user.

        Args:
            user_id: User ID starting the interview
            interview_path: Path key (unemployed, career_switch, student, pause, other)
            language: Interview language (default: de)
            user_native_language: User's native language (ISO 639-1 code, e.g., 'de', 'en', 'sr')

        Returns:
            Dict with session_id, first_question, and progress info

        Raises:
            ValueError: If path is invalid
        """
        # Validate path
        if interview_path not in ["unemployed", "career-switch", "student", "pause", "other"]:
            raise ValueError(f"Invalid interview path: {interview_path}")

        path = get_interview_path(interview_path)
        if not path:
            raise ValueError(f"Interview path not found: {interview_path}")

        try:
            logger.info(f"Starting interview: user={user_id}, path={interview_path}, language={language}, native_language={user_native_language}")

            # Ensure user exists (INSERT OR IGNORE so returning users are handled)
            self.db.execute_update(
                "INSERT OR IGNORE INTO users (user_id, created_at) VALUES (?, datetime('now'))",
                (user_id,)
            )

            # Create new session in database (with native language in single INSERT)
            session_id = self.db.create_session(
                user_id=user_id,
                interview_path=interview_path,
                language=language,
                user_native_language=user_native_language
            )

            # CVSections will be rebuilt from DB on demand (get_cv_sections)
            # No instance-level cache to avoid race conditions between concurrent users

            # Get first question
            first_question_id = get_all_question_ids(interview_path)[0]
            first_question = get_question(interview_path, first_question_id)

            result = {
                "session_id": session_id,
                "interview_path": interview_path,
                "question_id": first_question_id,
                "question": self._prepare_question(
                    get_localized_question(first_question, language)
                ),
                "progress": {
                    "current": 1,
                    "total": len(path["questions"]),
                    "percent": 1 / len(path["questions"]) * 100
                }
            }

            logger.info(f"Interview started: session_id={session_id}")
            return result

        except Exception as e:
            logger.error(f"Error starting interview: {e}")
            raise

    def get_next_question(self, session_id: str) -> Dict:
        """
        Get the next question in the interview.

        Args:
            session_id: Current session ID

        Returns:
            Dict with next question and progress info
        """
        try:
            # Get session info
            session = self.db.get_session(session_id)
            if not session:
                raise ValueError(f"Session not found: {session_id}")

            interview_path = session["interview_path"]
            path = get_interview_path(interview_path)

            # Get all questions for this path
            question_ids = get_all_question_ids(interview_path)

            # current_question is stored as 1-based index
            # Convert to 0-based for list access
            current_index = (session["current_question"] or 1) - 1

            # Move to next
            next_index = current_index + 1

            if next_index >= len(question_ids):
                # Interview complete
                return {
                    "status": "complete",
                    "message": "Interview abgeschlossen! Überprüfen Sie Ihre Antworten.",
                    "progress": {
                        "current": len(question_ids),
                        "total": len(question_ids),
                        "percent": 100
                    }
                }

            # Get next question
            next_question_id = question_ids[next_index]
            next_question = get_question(interview_path, next_question_id)

            # Update session with 1-based index
            self.db.execute_update(
                "UPDATE sessions SET current_question = ? WHERE id = ?",
                (next_index + 1, session_id)
            )

            session_language = session.get("language", "de")
            result = {
                "session_id": session_id,
                "question_id": next_question_id,
                "question": self._prepare_question(
                    get_localized_question(next_question, session_language)
                ),
                "progress": {
                    "current": next_index + 1,
                    "total": len(question_ids),
                    "percent": ((next_index + 1) / len(question_ids)) * 100
                }
            }

            return result

        except Exception as e:
            logger.error(f"Error getting next question: {e}")
            raise

    def submit_answer(self, session_id: str, question_id: str, answer_text: str) -> Dict:
        """
        Submit an answer to a question.

        Polishes the answer in multiple languages and may trigger re-ask if quality is low.
        Uses transaction-based autosave to ensure answer + progress are saved atomically.
        Creates CVSection objects with multilingual versions for later use in CV building.

        Args:
            session_id: Session ID
            question_id: Question ID being answered
            answer_text: The answer text

        Returns:
            Dict with validation result and next action:
            - status: "accepted" or "re_ask"
            - message: Feedback message
            - question: Re-ask question (if status = "re_ask")
            - polished_text: Improved version of the answer (English)
            - extracted_skills: List of extracted skills
            - quality: Quality score and feedback
        """
        try:
            logger.info(f"Submitting answer: session={session_id}, question={question_id}")

            # Reject writes to locked sessions (trainer lock)
            lock_check = self.db.execute_query(
                "SELECT locked FROM sessions WHERE id = ?", (int(session_id),)
            )
            if lock_check and lock_check[0].get("locked"):
                return {
                    "status": "error",
                    "message": "Diese Session ist gesperrt. Bitte kontaktieren Sie Ihren Trainer."
                }

            # Get session and question info
            session = self.db.get_session(session_id)
            interview_path = session["interview_path"]
            user_native_language = session.get("user_native_language")
            # Follow-up supplements are stored under base question ID
            base_question_id = question_id.removesuffix("_followup") if question_id.endswith("_followup") else question_id
            question = get_question(interview_path, base_question_id)

            if not question:
                raise ValueError(f"Question not found: {question_id}")

            question_id = base_question_id  # store under base ID (appends to existing answer)

            # ── Structured question handling (employer, title, date_range) ───────
            question_flags = question.get("flags", [])
            is_structured = any(
                f in question_flags for f in ["employer_name", "job_title", "date_range"]
            )

            if is_structured and "date_range" in question_flags:
                # Lightly normalise: flag obviously vague date inputs for trainer review
                vague_date_patterns = ["schon lange", "weiß nicht", "keine ahnung", "long time"]
                answer_lower = answer_text.strip().lower()
                if any(p in answer_lower for p in vague_date_patterns):
                    try:
                        self.db.execute_update(
                            "UPDATE sessions SET needs_review = 1, updated_at = datetime('now') "
                            "WHERE id = ?",
                            (int(session_id),)
                        )
                    except Exception:
                        pass  # Column may not exist on older DBs — non-fatal

            # Get question category for polishing
            question_category = question.get("category", "general")

            # Polish the answer in multiple languages and get CVSection
            # If user_native_language is not set, it will be detected from the answer
            cv_section = self.polish.polish_answer_multilingual(
                answer_text=answer_text,
                category=question_category,
                question_id=question_id,
                user_native_language=user_native_language
            )

            # If this is the first answer and user_native_language wasn't set,
            # store the detected language in the session
            if not user_native_language and cv_section.detected_input_language:
                detected_lang = cv_section.detected_input_language
                self.db.execute_update(
                    "UPDATE sessions SET user_native_language = ? WHERE id = ?",
                    (detected_lang, session_id)
                )
                logger.info(f"Detected user native language: {detected_lang}")

            # CV sections are stored in the database via autosave
            # No need for instance-level cache (avoids race conditions)

            # Save answer using transaction-based autosave
            save_result = self.autosave.autosave_answer(
                session_id=session_id,
                question_id=question_id,
                answer_text=answer_text
            )

            if save_result["status"] == "failed":
                raise Exception(f"Autosave failed: {save_result.get('error')}")

            # Update session progress
            try:
                total_q = len(get_all_question_ids(session["interview_path"]))
                answered = self.db.execute_query(
                    "SELECT COUNT(*) as cnt FROM answers WHERE session_id = ?",
                    (int(session_id),)
                )
                answered_count = answered[0]["cnt"] if answered else 0
                pct = min(100, int((answered_count / total_q) * 100)) if total_q > 0 else 0
                self.db.execute_update(
                    "UPDATE sessions SET progress_percent = ?, updated_at = datetime('now') WHERE id = ?",
                    (pct, int(session_id))
                )
            except Exception as prog_err:
                logger.warning(f"Progress update failed (non-fatal): {prog_err}")

            quality_score = cv_section.quality_score
            confidence_level = cv_section.confidence_level

            # Re-ask only when the answer is BOTH low quality AND genuinely short.
            # The quality scorer is biased toward English verbs/skills — a well-written
            # German answer legitimately scores "low" due to language mismatch, so we
            # guard with a word-count floor.  We also skip re-ask for simple identity
            # questions (name, location) where any answer is valid.
            # Structured questions (employer name, job title, date range) frequently
            # have short but perfectly valid answers like "BILLA" or "Lagermitarbeiter".
            min_length = question.get("min_length") or 0
            word_count = len(answer_text.strip().split())
            identity_question = question.get("category") == "identity"
            short_enough_to_reask = word_count < max(8, (min_length // 5) + 1)
            # Hard floor: any answer under 3 words is always too short for a
            # content question, regardless of what the quality scorer says.
            # (A 1-2 word answer can accidentally score "medium" because the
            # verb fallback = 0.5 and structure penalty is capped at 0.3.)
            definitely_too_short = word_count < 3

            if not identity_question and not is_structured and (
                definitely_too_short or
                (confidence_level == "low" and short_enough_to_reask)
            ):
                # Re-ask messages in user's language
                _ui_lang = session.get("language", "de")
                _reask_msgs = {
                    "de": ("Nennen Sie verwendete Werkzeuge oder Fähigkeiten", "Fügen Sie konkrete Beispiele oder Details hinzu", "Diese Antwort kann noch verbessert werden.", "Bitte fügen Sie mehr Details zu Ihrer Antwort hinzu"),
                    "en": ("Name the tools or skills you used", "Add concrete examples or details", "This answer could be improved.", "Please add more details to your answer"),
                    "tr": ("Kullandığınız araçları veya becerileri belirtin", "Somut örnekler veya ayrıntılar ekleyin", "Bu cevap geliştirilebilir.", "Lütfen cevabınıza daha fazla ayrıntı ekleyin"),
                    "pl": ("Wymień używane narzędzia lub umiejętności", "Dodaj konkretne przykłady lub szczegóły", "Ta odpowiedź może być ulepszona.", "Dodaj więcej szczegółów do swojej odpowiedzi"),
                    "ro": ("Enumerați instrumentele sau abilitățile utilizate", "Adăugați exemple concrete sau detalii", "Acest răspuns poate fi îmbunătățit.", "Adăugați mai multe detalii la răspunsul dvs."),
                    "uk": ("Назвіть використані інструменти або навички", "Додайте конкретні приклади або деталі", "Цю відповідь можна покращити.", "Будь ласка, додайте більше деталей"),
                    "ru": ("Назовите используемые инструменты или навыки", "Добавьте конкретные примеры или детали", "Этот ответ можно улучшить.", "Пожалуйста, добавьте больше деталей"),
                    "ar": ("اذكر الأدوات أو المهارات المستخدمة", "أضف أمثلة أو تفاصيل ملموسة", "يمكن تحسين هذه الإجابة.", "الرجاء إضافة المزيد من التفاصيل"),
                    "bs": ("Navedite korištene alate ili vještine", "Dodajte konkretne primjere ili detalje", "Ovaj odgovor može biti poboljšan.", "Dodajte više detalja svom odgovoru"),
                    "hr": ("Navedite korištene alate ili vještine", "Dodajte konkretne primjere ili detalje", "Ovaj odgovor može biti poboljšan.", "Dodajte više detalja svom odgovoru"),
                    "sr": ("Navedite korišćene alate ili veštine", "Dodajte konkretne primere ili detalje", "Ovaj odgovor može biti poboljšan.", "Dodajte više detalja svom odgovoru"),
                    "sk": ("Uveďte použité nástroje alebo zručnosti", "Pridajte konkrétne príklady alebo detaily", "Túto odpoveď možno vylepšiť.", "Prosím pridajte viac detailov"),
                }
                _rm = _reask_msgs.get(_ui_lang, _reask_msgs["de"])
                suggestions = []
                if cv_section.detected_skills:
                    suggestions.append(_rm[0])
                suggestions.append(_rm[1])

                suggestion_text = "; ".join(suggestions[:2]) if suggestions else _rm[3]

                return {
                    "status": "re_ask",
                    "message": f"{_rm[2]} {suggestion_text}",
                    "question": self._prepare_question(
                        get_localized_question(question, _ui_lang)
                    ),
                    "quality": {
                        "overall": quality_score,
                        "confidence": confidence_level,
                        "suggestions": suggestions[:2]
                    },
                    "suggestion": suggestion_text
                }

            # Answer accepted — pick an encouraging message based on quality
            _ui_lang = session.get("language", "de")
            _enc = {
                "de": {
                    "high":   ["Sehr gut! Weiter so.", "Perfekt — das klingt professionell.", "Ausgezeichnet!"],
                    "medium": ["Gut! Das hilft uns.", "Danke — das ist hilfreich.", "Gut gemacht!"],
                    "low":    ["Danke — gespeichert.", "Notiert, danke!", "Gespeichert."],
                },
                "en": {
                    "high":   ["Great answer!", "Excellent — sounds very professional.", "Perfect!"],
                    "medium": ["Good, that helps.", "Thank you — that's useful.", "Well done!"],
                    "low":    ["Noted, thank you.", "Saved.", "Thank you."],
                },
                "tr": {
                    "high":   ["Harika!", "Çok iyi!", "Mükemmel!"],
                    "medium": ["Teşekkürler, bu yardımcı oldu.", "İyi!", "Güzel!"],
                    "low":    ["Kaydedildi.", "Teşekkürler.", "Tamam."],
                },
                "ar": {
                    "high":   ["ممتاز!", "إجابة رائعة!", "أحسنت!"],
                    "medium": ["شكراً، هذا مفيد.", "جيد!", "حسناً!"],
                    "low":    ["تم الحفظ.", "شكراً.", "حسناً."],
                },
                "bs": {
                    "high":   ["Odlično!", "Savršeno — zvuči profesionalno.", "Izvrsno!"],
                    "medium": ["Dobro, to pomaže.", "Hvala — korisno je.", "Bravo!"],
                    "low":    ["Sačuvano.", "Hvala.", "U redu."],
                },
                "hr": {
                    "high":   ["Odlično!", "Savršeno — zvuči profesionalno.", "Izvrsno!"],
                    "medium": ["Dobro, to pomaže.", "Hvala — korisno je.", "Bravo!"],
                    "low":    ["Spremljeno.", "Hvala.", "U redu."],
                },
                "sr": {
                    "high":   ["Odlično!", "Savršeno — zvuči profesionalno.", "Izvrsno!"],
                    "medium": ["Dobro, to pomaže.", "Hvala — korisno je.", "Bravo!"],
                    "low":    ["Sačuvano.", "Hvala.", "U redu."],
                },
                "pl": {
                    "high":   ["Świetnie!", "Doskonale — brzmi profesjonalnie.", "Znakomicie!"],
                    "medium": ["Dobrze, to pomaga.", "Dziękuję — to przydatne.", "Brawo!"],
                    "low":    ["Zapisano.", "Dziękuję.", "Dobrze."],
                },
                "ro": {
                    "high":   ["Excelent!", "Perfect — sună profesional.", "Minunat!"],
                    "medium": ["Bine, asta ajută.", "Mulțumesc — e util.", "Bravo!"],
                    "low":    ["Salvat.", "Mulțumesc.", "Bine."],
                },
                "uk": {
                    "high":   ["Чудово!", "Відмінно — звучить професійно.", "Прекрасно!"],
                    "medium": ["Добре, це допомагає.", "Дякую — це корисно.", "Молодець!"],
                    "low":    ["Збережено.", "Дякую.", "Добре."],
                },
                "ru": {
                    "high":   ["Отлично!", "Превосходно — звучит профессионально.", "Замечательно!"],
                    "medium": ["Хорошо, это помогает.", "Спасибо — это полезно.", "Молодец!"],
                    "low":    ["Сохранено.", "Спасибо.", "Хорошо."],
                },
                "sk": {
                    "high":   ["Výborne!", "Perfektne — znie to profesionálne.", "Skvelé!"],
                    "medium": ["Dobre, to pomáha.", "Ďakujem — to je užitočné.", "Dobre urobené!"],
                    "low":    ["Uložené.", "Ďakujem.", "Dobre."],
                },
            }
            _lang_enc = _enc.get(_ui_lang, _enc["de"])
            import random as _rand
            if confidence_level == "high" or quality_score >= 0.7:
                _msg = _rand.choice(_lang_enc["high"])
            elif quality_score >= 0.45:
                _msg = _rand.choice(_lang_enc["medium"])
            else:
                _msg = _rand.choice(_lang_enc["low"])

            # Choose display text in the user's language.
            # German users see German.  Others see native/English so the text makes
            # sense to them.  The German CV field is populated correctly and the
            # trainer can review non-German inputs when AI was not available.
            _display_lang = session.get("language", "de")
            if _display_lang == "de" or cv_section.detected_input_language == "de":
                _display_text = cv_section.german
            else:
                _display_text = (
                    cv_section.native
                    or cv_section.english
                    or cv_section.german
                )

            return {
                "status": "accepted",
                "message": _msg,
                "polished_text": _display_text,
                "extracted_skills": cv_section.detected_skills,
                "quality": {
                    "overall": quality_score,
                    "confidence": confidence_level,
                    "detected_language": cv_section.detected_input_language,
                    "native_language": cv_section.user_native_language
                }
            }

        except Exception as e:
            logger.error(f"Error submitting answer: {e}")
            raise

    def skip_question(self, session_id: str, question_id: str) -> Dict:
        """
        Allow user to skip a question and come back to it later.

        Args:
            session_id: Session ID
            question_id: Question being skipped

        Returns:
            Dict with next question or completion status
        """
        try:
            logger.info(f"Skipping question: session={session_id}, question={question_id}")

            # Mark question as skipped (save empty answer with flag)
            self.db.save_answer(
                session_id=session_id,
                question_id=question_id,
                answer_text=ANSWER_SKIPPED
            )

            # Update session progress
            try:
                session = self.db.get_session(session_id)
                total_q = len(get_all_question_ids(session["interview_path"]))
                answered = self.db.execute_query(
                    "SELECT COUNT(*) as cnt FROM answers WHERE session_id = ?",
                    (int(session_id),)
                )
                answered_count = answered[0]["cnt"] if answered else 0
                pct = min(100, int((answered_count / total_q) * 100)) if total_q > 0 else 0
                self.db.execute_update(
                    "UPDATE sessions SET progress_percent = ?, updated_at = datetime('now') WHERE id = ?",
                    (pct, int(session_id))
                )
            except Exception as prog_err:
                logger.warning(f"Progress update failed (non-fatal): {prog_err}")

            # Get next question
            return self.get_next_question(session_id)

        except Exception as e:
            logger.error(f"Error skipping question: {e}")
            raise

    def resume_interview(self, session_id: str) -> Dict:
        """
        Resume an interview that was paused.

        Uses crash recovery to restore session to consistent state and return the current question.

        Args:
            session_id: Session ID to resume

        Returns:
            Dict with current question and progress
        """
        try:
            logger.info(f"Resuming interview: session={session_id}")

            session = self.db.get_session(session_id)
            if not session:
                raise ValueError(f"Session not found: {session_id}")

            interview_path = session["interview_path"]
            question_ids = get_all_question_ids(interview_path)
            path = get_interview_path(interview_path)

            # Use autosave recovery to verify session state and get resume point
            recovery = self.autosave.recover_session(session_id)

            if not recovery["recovered"]:
                # Session state is corrupted, cannot safely resume
                logger.error(f"Cannot recover session {session_id}: {recovery['message']}")
                raise ValueError(f"Session recovery failed: {recovery['message']}")

            # current_question_index is 0-based (0, 1, 2, 3, 4, or 5 for completion)
            current_index = recovery["current_question_index"]

            # Clamp to valid range (if somehow past completion)
            if current_index >= len(question_ids):
                current_index = len(question_ids) - 1

            current_question_id = question_ids[current_index]
            question = get_question(interview_path, current_question_id)

            if not question:
                raise ValueError(f"Question not found: {current_question_id}")

            session_language = session.get("language", "de")
            result = {
                "session_id": session_id,
                "question_id": current_question_id,
                "question": self._prepare_question(
                    get_localized_question(question, session_language)
                ),
                "progress": {
                    "current": current_index + 1,
                    "total": len(path["questions"]),
                    "percent": ((current_index + 1) / len(path["questions"])) * 100
                }
            }

            logger.info(f"Interview resumed at question {current_index + 1} (recovered {recovery['answers_recovered']} answers)")
            return result

        except Exception as e:
            logger.error(f"Error resuming interview: {e}")
            raise

    def get_interview_status(self, session_id: str) -> Dict:
        """
        Get current status of an interview session.

        Args:
            session_id: Session ID

        Returns:
            Dict with interview status and answers
        """
        try:
            session = self.db.get_session(session_id)
            if not session:
                raise ValueError(f"Session not found: {session_id}")

            interview_path = session["interview_path"]
            question_ids = get_all_question_ids(interview_path)
            answers = self.db.get_session_answers(session_id)  # Returns dict: {question_id: answer_text}

            # Count completed answers (not skipped)
            # answers is a dict mapping question_id -> answer_text
            completed = len([ans_text for ans_text in answers.values() if ans_text != ANSWER_SKIPPED])
            skipped = len([ans_text for ans_text in answers.values() if ans_text == ANSWER_SKIPPED])

            result = {
                "session_id": session_id,
                "interview_path": interview_path,
                "current_question": session["current_question"],
                "total_questions": len(question_ids),
                "answers_completed": completed,
                "answers_skipped": skipped,
                "progress_percent": session["progress_percent"],
                "created_at": session["created_at"],
                "last_updated": session["updated_at"]
            }

            return result

        except Exception as e:
            logger.error(f"Error getting interview status: {e}")
            raise

    def get_cv_sections(self, session_id: str) -> Dict[str, CVSection]:
        """
        Retrieve all accumulated CVSection objects from an interview session.

        These are populated during submit_answer() for each question answered.
        Used by CVBuilder to assemble complete multilingual CVData.

        Args:
            session_id: Session ID

        Returns:
            Dict mapping question_id -> CVSection object
            Empty dict if no sections have been accumulated yet
        """
        try:
            # Always rebuild CVSections from raw answers (stateless)
            # This ensures consistency across concurrent requests and is thread-safe
            session = self.db.get_session(session_id)
            if not session:
                raise ValueError(f"Session not found: {session_id}")

            interview_path = session["interview_path"]
            user_native_language = session.get("user_native_language")
            answers = self.db.get_session_answers(session_id)

            cv_sections = {}
            for question_id, answer_text in answers.items():
                if answer_text and answer_text != ANSWER_SKIPPED:
                    question = get_question(interview_path, question_id)
                    if question:
                        category = question.get("category", "general")
                        cv_section = self.polish.polish_answer_multilingual(
                            answer_text=answer_text,
                            category=category,
                            question_id=question_id,
                            user_native_language=user_native_language
                        )
                        cv_sections[question_id] = cv_section

            return cv_sections

        except Exception as e:
            logger.error(f"Error retrieving CV sections: {e}")
            raise

    # ============================================================================
    # Private helper methods
    # ============================================================================

    def _prepare_question(self, question: Dict) -> Dict:
        """
        Prepare question for presentation to user.

        Includes question text, hint, and both good/bad examples.

        Args:
            question: Raw question dict from paths.py

        Returns:
            Formatted question dict for frontend
        """
        return {
            "id": question["id"],
            "text": question["text"],
            "hint": question["hint"],
            "category": question["category"],
            "examples": {
                "good": question["examples"]["good"],
                "bad": question["examples"]["bad"]
            },
            "quick_fill": question.get("quick_fill", []),
            "helper_tip": question.get("helper_tip", ""),
        }

    def _ensure_questions_loaded(self) -> None:
        """
        Ensure all interview questions are loaded into the database.

        Called on engine initialization. Uses INSERT OR IGNORE so it is safe to
        call multiple times and will add any new questions (e.g., identity questions)
        even if older questions already exist in the DB.
        """
        try:
            logger.debug("Ensuring interview questions are up-to-date in database...")

            # Load all questions from all paths
            from interview.paths import INTERVIEW_PATHS

            questions_to_insert = []

            for path_key, path_config in INTERVIEW_PATHS.items():
                for question in path_config["questions"]:
                    questions_to_insert.append((
                        question["id"],  # question_id (TEXT)
                        question["text"],  # question_text
                        question["category"],  # category
                        path_key,  # interview_path
                        question["order"],  # question_order
                        question["hint"],  # hint
                        question["examples"]["good"],  # good_example
                        question["examples"]["bad"],  # bad_example
                        question.get("min_length", 20)  # min_length
                    ))

            # Batch insert all questions (INSERT OR IGNORE so adding new questions to existing DB works)
            sql = """
            INSERT OR IGNORE INTO interview_questions
            (question_id, question_text, category, interview_path, question_order, hint, good_example, bad_example, min_length)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """

            self.db.execute_batch(sql, questions_to_insert)
            logger.info(f"✓ Loaded {len(questions_to_insert)} interview questions")

        except Exception as e:
            logger.error(f"Error loading interview questions: {e}")
            # Don't raise - this shouldn't block engine initialization

    def cleanup_old_sessions(self, days_old: int = 90) -> int:
        """
        Delete incomplete sessions older than *days_old* days.

        Only sessions that were never finished (completed = 0 or the column
        does not exist yet) are removed. Approved/locked sessions are always
        kept to preserve the trainer audit trail.

        Args:
            days_old: Age threshold in whole days (default 90).

        Returns:
            Number of sessions deleted.
        """
        try:
            result = self.db.execute_update(
                """DELETE FROM sessions
                   WHERE created_at < datetime('now', '-' || ? || ' days')
                     AND (completed IS NULL OR completed = 0)
                     AND (locked IS NULL OR locked = 0)
                     AND (approved IS NULL OR approved = 0)""",
                (days_old,)
            )
            logger.info(f"Cleaned up {result} stale sessions older than {days_old} days")
            return result if result is not None else 0
        except Exception as e:
            logger.error(f"Session cleanup failed: {e}")
            return 0

    @staticmethod
    def validate_interview_path(path_key: str) -> bool:
        """
        Check if an interview path is valid.

        Args:
            path_key: Path key to validate

        Returns:
            True if valid, False otherwise
        """
        valid_paths = ["unemployed", "career-switch", "student", "pause", "other"]
        return path_key in valid_paths
