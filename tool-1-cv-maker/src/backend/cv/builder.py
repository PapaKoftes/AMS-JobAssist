"""
CV Builder - Assembles complete multilingual CVData from interview sessions.

Handles:
1. Collecting all CVSection objects from an interview session
2. Organizing sections by category
3. Deduplicating skills
4. Calculating overall quality score
5. Preparing CVData for export
"""

import logging
import re
from typing import Dict, Optional, List, Set
from datetime import datetime

from cv.models import CVData, CVSection, QuestionCategory
from db import DatabaseManager
from polish.engine import PolishEngine

# Sentinel value used to mark skipped questions — must match engine.py
ANSWER_SKIPPED = "[SKIPPED]"

# Suffixes appended to a base experience question id for its structured
# follow-ups (see interview/paths.py _make_employer/_title/_dates_question).
_EXP_SUBQ_SUFFIXES = ("_employer", "_title", "_dates")

# German month names → 2-digit month, for parsing free-text date ranges.
_MONTHS_DE = {
    "jänner": "01", "januar": "01", "jan": "01", "februar": "02", "feb": "02",
    "märz": "03", "maerz": "03", "mär": "03", "april": "04", "apr": "04",
    "mai": "05", "juni": "06", "jun": "06", "juli": "07", "jul": "07",
    "august": "08", "aug": "08", "september": "09", "sep": "09", "sept": "09",
    "oktober": "10", "okt": "10", "november": "11", "nov": "11",
    "dezember": "12", "dez": "12",
}
_PRESENT_WORDS = ("heute", "jetzt", "aktuell", "laufend", "derzeit",
                  "noch", "present", "now", "current", "ongoing")

logger = logging.getLogger(__name__)


def _parse_token_to_iso(token: str) -> Optional[str]:
    """Parse a single date token like 'Jänner 2020' / '03/2020' / '2020' → ISO partial."""
    token = token.strip().lower()
    if not token:
        return None
    # Month name + year
    m = re.search(r"([a-zä-ÿ]+)\.?\s+(\d{4})", token)
    if m and m.group(1) in _MONTHS_DE:
        return f"{m.group(2)}-{_MONTHS_DE[m.group(1)]}"
    # MM/YYYY or MM.YYYY
    m = re.search(r"(\d{1,2})[./](\d{4})", token)
    if m:
        return f"{m.group(2)}-{int(m.group(1)):02d}"
    # Bare year
    m = re.search(r"\b(19|20)\d{2}\b", token)
    if m:
        return m.group(0)
    return None


# Language name (any of several spellings) → (canonical English name, ISO 639-1).
_LANGUAGE_MAP = {
    "deutsch": ("German", "de"), "german": ("German", "de"),
    "englisch": ("English", "en"), "english": ("English", "en"),
    "bosnisch": ("Bosnian", "bs"), "bosnian": ("Bosnian", "bs"),
    "kroatisch": ("Croatian", "hr"), "croatian": ("Croatian", "hr"),
    "serbisch": ("Serbian", "sr"), "serbian": ("Serbian", "sr"),
    "türkisch": ("Turkish", "tr"), "tuerkisch": ("Turkish", "tr"), "turkish": ("Turkish", "tr"),
    "arabisch": ("Arabic", "ar"), "arabic": ("Arabic", "ar"),
    "polnisch": ("Polish", "pl"), "polish": ("Polish", "pl"),
    "rumänisch": ("Romanian", "ro"), "rumaenisch": ("Romanian", "ro"), "romanian": ("Romanian", "ro"),
    "ukrainisch": ("Ukrainian", "uk"), "ukrainian": ("Ukrainian", "uk"),
    "russisch": ("Russian", "ru"), "russian": ("Russian", "ru"),
    "französisch": ("French", "fr"), "franzoesisch": ("French", "fr"), "french": ("French", "fr"),
    "italienisch": ("Italian", "it"), "italian": ("Italian", "it"),
    "spanisch": ("Spanish", "es"), "spanish": ("Spanish", "es"),
    "slowakisch": ("Slovak", "sk"), "slovak": ("Slovak", "sk"),
    "ungarisch": ("Hungarian", "hu"), "hungarian": ("Hungarian", "hu"),
    "albanisch": ("Albanian", "sq"), "albanian": ("Albanian", "sq"),
    "persisch": ("Persian", "fa"), "farsi": ("Persian", "fa"), "persian": ("Persian", "fa"),
    "kurdisch": ("Kurdish", "ku"), "kurdish": ("Kurdish", "ku"),
}


def _detect_language_level(text: str) -> str:
    """Map free-text proficiency wording to a CEFR level (or 'native')."""
    low = text.lower()
    m = re.search(r"\b([abc][12])\b", low)
    if m:
        return m.group(1).upper()
    if re.search(r"muttersprache|muttersprachlich|native|mother\s*tongue|maternel", low):
        return "native"
    if re.search(r"fließend|fliessend|fluent|verhandlungssicher|sehr\s+gut|excellent", low):
        return "C1"
    if re.search(r"\bgut\b|good|advanced|fortgeschritten", low):
        return "B2"
    if re.search(r"grundkenntnisse|basic|basis|anfänger|anfaenger|beginner|wenig", low):
        return "A2"
    return ""


def _extract_languages_from_skills(skills: List[str]):
    """
    Pull language proficiencies ("Deutsch B2", "Bosnisch Muttersprache") out of a
    flat skills list. Returns (languages, remaining_skills) where languages is a
    list of {language, code, level} dicts (deduped by code, best level kept).
    """
    _LEVEL_RANK = {"": 0, "A1": 1, "A2": 2, "B1": 3, "B2": 4, "C1": 5, "C2": 6, "native": 7}
    languages: Dict[str, Dict[str, str]] = {}
    remaining: List[str] = []
    for skill in skills:
        low = skill.lower()
        matched = None
        for name, (canon, code) in _LANGUAGE_MAP.items():
            # Prefix match (no trailing \b) so the polish engine's compound forms
            # also map: "Deutschkenntnisse" / "Deutsch (Muttersprache)" → German.
            if re.search(r"\b" + re.escape(name), low):
                matched = (canon, code)
                break
        if not matched:
            remaining.append(skill)
            continue
        canon, code = matched
        level = _detect_language_level(skill)
        prev = languages.get(code)
        if prev is None or _LEVEL_RANK.get(level, 0) > _LEVEL_RANK.get(prev["level"], 0):
            languages[code] = {"language": canon, "code": code, "level": level}
    return list(languages.values()), remaining


def _parse_experience_period(text: str) -> Optional[Dict[str, Optional[str]]]:
    """
    Parse a free-text German/English date answer into {"start", "end"}.

    Handles: "Jänner 2020 bis März 2022", "2018–2021", "seit 2019",
    "von 2020 bis heute", "ca. 2 Jahre" (→ None, not a fixed range).
    Returns None if nothing date-like is found.
    """
    if not text:
        return None
    low = text.strip().lower()
    # Ongoing if a present-word appears with a start.
    ongoing = any(w in low for w in _PRESENT_WORDS)
    # Split on range separators.
    parts = re.split(r"\s*(?:bis|to|–|—|-|until|until now)\s*", low)
    parts = [p for p in parts if p.strip()]
    start = _parse_token_to_iso(parts[0]) if parts else None
    end = None
    if len(parts) >= 2 and not ongoing:
        end = _parse_token_to_iso(parts[-1])
    if start is None and end is None:
        return None
    return {"start": start, "end": (None if ongoing else end)}


class CVBuilder:
    """Assembles complete multilingual CVData from interview session."""

    def __init__(self, db_manager: DatabaseManager):
        """
        Initialize CVBuilder.

        Args:
            db_manager: DatabaseManager instance for database operations
        """
        self.db = db_manager
        self.polish = PolishEngine(db_manager)

    def build_cv_from_session(
        self,
        session_id: int,
        user_id: str,
        interview_path: str,
        language_input: str,
        language_output_primary: str = "de",
        language_output_secondary: str = "en"
    ) -> Optional[CVData]:
        """
        Build complete CVData from interview session.

        Retrieves all CVSection objects from session and assembles CVData.

        Args:
            session_id: Interview session ID
            user_id: User ID who completed interview
            interview_path: Interview path selected (unemployed, career-switch, etc.)
            language_input: Input language used in interview
            language_output_primary: Primary output language (default German)
            language_output_secondary: Secondary output language (default English)

        Returns:
            Complete CVData object, or None if no sections found

        Raises:
            Exception: If database query fails
        """
        try:
            logger.info(f"Building CVData for session {session_id}")

            # Get all CVSection objects from session (stored in database)
            cv_sections = self._get_cv_sections_from_session(session_id)

            if not cv_sections:
                logger.warning(f"No CVSection objects found for session {session_id}")
                return None

            # Delegate to common build method
            return self._build_cv_from_sections(
                session_id=session_id,
                user_id=user_id,
                interview_path=interview_path,
                language_input=language_input,
                cv_sections=cv_sections,
                language_output_primary=language_output_primary,
                language_output_secondary=language_output_secondary
            )

        except Exception as e:
            logger.error(f"Error building CVData: {e}")
            return None

    def build_cv_from_answers_dict(
        self,
        session_id: int,
        user_id: str,
        interview_path: str,
        language_input: str,
        answers_dict: Dict[str, CVSection],
        language_output_primary: str = "de",
        language_output_secondary: str = "en"
    ) -> Optional[CVData]:
        """
        Build CVData from pre-collected answers dictionary.

        Takes CVSections already loaded in memory (question_id -> CVSection mapping)
        and assembles them into a complete CVData object.

        Args:
            session_id: Interview session ID
            user_id: User ID who completed interview
            interview_path: Interview path selected
            language_input: Input language used
            answers_dict: Dict mapping question_id -> CVSection
            language_output_primary: Primary output language
            language_output_secondary: Secondary output language

        Returns:
            Complete CVData object, or None if no answers found
        """
        if not answers_dict:
            logger.warning(f"No answers provided for session {session_id}")
            return None

        # Convert dict values to list
        cv_sections = list(answers_dict.values())

        # Delegate to common build method
        return self._build_cv_from_sections(
            session_id=session_id,
            user_id=user_id,
            interview_path=interview_path,
            language_input=language_input,
            cv_sections=cv_sections,
            language_output_primary=language_output_primary,
            language_output_secondary=language_output_secondary
        )

    def _build_cv_from_sections(
        self,
        session_id: int,
        user_id: str,
        interview_path: str,
        language_input: str,
        cv_sections: List[CVSection],
        language_output_primary: str = "de",
        language_output_secondary: str = "en"
    ) -> Optional[CVData]:
        """
        Internal method: Build CVData from a list of CVSection objects.

        Common logic for organizing sections, deduplicating skills, and
        calculating quality. Used by both build_cv_from_session() and
        build_cv_from_answers_dict().

        Args:
            session_id: Interview session ID
            user_id: User ID
            interview_path: Interview path
            language_input: Input language
            cv_sections: List of CVSection objects (already loaded)
            language_output_primary: Primary output language
            language_output_secondary: Secondary output language

        Returns:
            Complete CVData object
        """
        # Create CVData container
        cv_data = CVData(
            session_id=session_id,
            user_id=user_id,
            interview_path=interview_path,
            language_input=language_input
        )
        cv_data.language_output_primary = language_output_primary
        cv_data.language_output_secondary = language_output_secondary

        # Populate identity from dedicated identity question answers
        cv_data.identity = self._extract_identity(session_id, user_id)

        # Extract target_job from the id_target_job answer (stored as raw text in answers table)
        try:
            raw_answers = self.db.execute_query(
                "SELECT question_id, answer_text FROM answers WHERE session_id = ? AND question_id = 'id_target_job'",
                (session_id,)
            )
            if raw_answers:
                cv_data.target_job = (raw_answers[0].get("answer_text") or "").strip()
        except Exception:
            pass  # Non-fatal: target_job defaults to ""

        # Organize sections by category
        skill_set = set()  # For deduplication
        quality_scores = []

        for section in cv_sections:
            if section.category == QuestionCategory.BACKGROUND:
                cv_data.background.append(section)
            elif section.category == QuestionCategory.EXPERIENCE:
                cv_data.experience.append(section)
            elif section.category == QuestionCategory.SKILLS:
                cv_data.skills.append(section)
            elif section.category == QuestionCategory.MOTIVATION:
                cv_data.motivation.append(section)
            elif section.category == QuestionCategory.TRAINING:
                cv_data.training.append(section)
            elif section.category == QuestionCategory.PROJECTS:
                cv_data.projects.append(section)

            # Collect skills for deduplication
            if section.detected_skills:
                skill_set.update(section.detected_skills)

            # Collect quality scores
            if section.quality_score is not None:
                quality_scores.append(section.quality_score)

        # Deduplicate skills
        cv_data.all_skills = sorted(list(skill_set))
        logger.info(f"Deduped {len(skill_set)} unique skills from {len(cv_sections)} sections")

        # Promote language proficiencies to a first-class CV section. Language
        # answers otherwise sit inside the generic skills blob; pulling them out
        # gives the export a proper "Sprachen" section with CEFR levels and stops
        # them being listed twice (once as a skill, once as a language).
        try:
            langs, remaining = _extract_languages_from_skills(cv_data.all_skills)
            if langs:
                cv_data.languages = langs
                cv_data.all_skills = sorted(remaining)
                logger.info(f"Extracted {len(langs)} language(s) from skills")
        except Exception as _lex:
            logger.warning(f"Language extraction failed (non-fatal): {_lex}")

        # Calculate overall quality score
        if quality_scores:
            cv_data.overall_quality = sum(quality_scores) / len(quality_scores)
            logger.info(f"Overall quality score: {cv_data.overall_quality:.2f}")
        else:
            cv_data.overall_quality = 0.0

        # Ready for export when the CV is actually COMPLETE, not when it hits a
        # quality number. The quality scorer is biased toward English verbs/skills,
        # so a perfectly valid German CV legitimately scores below 0.5 — gating
        # export on that score wrongly blocked real participants. Instead require
        # an identity name plus at least one content section. The quality score is
        # still reported for encouraging feedback, just not as an export gate.
        has_name = bool(getattr(cv_data, "identity", None) and getattr(cv_data.identity, "full_name", ""))
        has_content = len(cv_sections) >= 1
        cv_data.ready_for_export = has_name and has_content
        logger.info(f"Ready for export: {cv_data.ready_for_export} (name={has_name}, sections={len(cv_sections)})")

        logger.info(f"Built CVData with {len(cv_sections)} sections, overall quality {cv_data.overall_quality:.2f}")
        return cv_data

    def _get_cv_sections_from_session(self, session_id: int) -> List[CVSection]:
        """
        Retrieve all CVSection objects from session.

        Attempts to retrieve from database answer records. Each answer
        contains a serialized CVSection (created during polish_answer_multilingual).

        Args:
            session_id: Session to retrieve sections for

        Returns:
            List of CVSection objects, empty list if none found
        """
        try:
            # Query answers joined with question categories
            results = self.db.execute_query(
                """
                SELECT a.question_id, a.answer_text,
                       COALESCE(q.category, 'experience') AS category
                FROM answers a
                LEFT JOIN interview_questions q ON a.question_id = q.question_id
                WHERE a.session_id = ?
                ORDER BY COALESCE(q.question_order, 9999), a.id
                """,
                (session_id,)
            )

            if not results:
                logger.warning(f"No answers found for session {session_id}")
                return []

            # Get user's native language from session
            session_rows = self.db.execute_query(
                "SELECT user_native_language FROM sessions WHERE id = ?",
                (session_id,)
            )
            native_lang = session_rows[0].get("user_native_language") if session_rows else None

            # Index all answers so structured experience follow-ups
            # (<base>_employer / _title / _dates) can be folded into the base
            # entry instead of becoming 3 disconnected prose sections.
            answers_by_id: Dict[str, str] = {}
            for row in results:
                qid = row["question_id"]
                txt = (row["answer_text"] or "").strip()
                if txt and txt != ANSWER_SKIPPED:
                    answers_by_id[qid] = txt

            def _subq(base: str, suffix: str) -> str:
                return answers_by_id.get(f"{base}{suffix}", "").strip()

            cv_sections = []
            for row in results:
                question_id = row["question_id"]
                answer_text = row["answer_text"]
                category = row["category"]

                # Skip identity questions — handled separately by _extract_identity().
                # id_target_job is skipped here too: it is captured separately as
                # cv_data.target_job, so including it as a motivation section would
                # make the target job appear twice in the exported CV.
                if question_id in ("id_name", "id_contact", "id_location", "id_phone", "id_email", "id_target_job"):
                    continue

                # Structured experience follow-ups are folded into their base
                # entry below — don't emit them as standalone sections.
                if question_id.endswith(_EXP_SUBQ_SUFFIXES):
                    continue

                # Skip skipped/empty answers
                if not answer_text or answer_text.strip() in ("", ANSWER_SKIPPED):
                    continue

                try:
                    # Re-polish the raw answer to rebuild the CVSection
                    cv_section = self.polish.polish_answer_multilingual(
                        answer_text=answer_text,
                        category=category,
                        question_id=question_id,
                        user_native_language=native_lang
                    )

                    # Attach structured metadata from the follow-up questions.
                    title = _subq(question_id, "_title")
                    employer = _subq(question_id, "_employer")
                    dates = _subq(question_id, "_dates")
                    if title:
                        cv_section.title = title
                    if employer:
                        cv_section.employer = employer
                    if dates and not cv_section.period:
                        parsed = _parse_experience_period(dates)
                        if parsed:
                            cv_section.period = parsed

                    cv_sections.append(cv_section)
                except Exception as section_err:
                    logger.warning(f"Could not polish answer {question_id}: {section_err}")
                    continue

            logger.info(f"Rebuilt {len(cv_sections)} CVSections for session {session_id}")
            return cv_sections

        except Exception as e:
            logger.error(f"Error retrieving CVSections: {e}")
            return []

    def _extract_identity(self, session_id: int, user_id: str) -> 'CVIdentity':
        """Extract CVIdentity from identity question answers."""
        from cv.models import CVIdentity
        import re as _re
        try:
            rows = self.db.execute_query(
                "SELECT question_id, answer_text FROM answers WHERE session_id = ? AND question_id IN ('id_name', 'id_contact', 'id_location', 'id_phone', 'id_email')",
                (session_id,)
            )
        except Exception as e:
            logger.warning(f"Could not fetch identity answers: {e}")
            rows = []
        full_name = user_id  # fallback
        location = ""
        phone = ""
        email = ""

        def _parse_contact(blob: str):
            """Pull e-mail / phone / city out of one combined contact line."""
            loc, ph, em = "", "", ""
            m = _re.search(r"[\w.+-]+@[\w-]+\.[\w.-]+", blob)
            if m:
                em = m.group(0)
                blob = blob.replace(em, " ")
            m = _re.search(r"(?<!\w)(\+?\d[\d\s/().\-]{6,}\d)", blob)
            if m:
                ph = m.group(1).strip()
                blob = blob.replace(m.group(1), " ")
            # Remaining text → city (first non-empty comma/whitespace chunk).
            rest = [p.strip(" ,;·") for p in _re.split(r"[,\n;]", blob)]
            rest = [p for p in rest if p]
            if rest:
                loc = rest[0]
            return loc, ph, em

        for row in (rows or []):
            qid = row.get("question_id", "")
            text = (row.get("answer_text") or "").strip()
            if not text or text == ANSWER_SKIPPED:
                continue
            if qid == "id_name":
                full_name = text
            elif qid == "id_contact":
                location, phone, email = _parse_contact(text)
            elif qid == "id_location":   # legacy sessions
                location = text
            elif qid == "id_phone":
                phone = text
            elif qid == "id_email":
                email = text
        return CVIdentity(
            full_name=full_name,
            location=location,
            contact_phone=phone or None,
            contact_email=email or None,
        )

    def calculate_category_quality(self, sections: List[CVSection]) -> float:
        """
        Calculate average quality score for a list of sections.

        Args:
            sections: List of CVSection objects to score

        Returns:
            Average quality score (0.0-1.0), or 0.0 if no sections
        """
        if not sections:
            return 0.0

        quality_scores = [s.quality_score for s in sections if s.quality_score is not None]
        if not quality_scores:
            return 0.0

        return sum(quality_scores) / len(quality_scores)

    def get_sections_by_quality(
        self,
        cv_data: CVData,
        min_quality: float = 0.0
    ) -> Dict[str, List[CVSection]]:
        """
        Filter and organize CVData sections by quality threshold.

        Useful for identifying which sections need trainer review.

        Args:
            cv_data: Complete CVData object
            min_quality: Minimum quality score to include (0.0-1.0)

        Returns:
            Dict mapping category name -> filtered sections list
        """
        categories = {
            "background": cv_data.background,
            "experience": cv_data.experience,
            "skills": cv_data.skills,
            "motivation": cv_data.motivation,
            "training": cv_data.training,
            "projects": cv_data.projects,
        }

        filtered = {}
        for category_name, sections in categories.items():
            filtered[category_name] = [
                s for s in sections
                if s.quality_score is None or s.quality_score >= min_quality
            ]

        return filtered

    def merge_cv_data(self, cv_data1: CVData, cv_data2: CVData) -> Optional[CVData]:
        """
        Merge two CVData objects (e.g., from multiple interviews).

        Combines sections, deduplicates skills, recalculates overall quality.

        Args:
            cv_data1: First CVData object
            cv_data2: Second CVData object to merge into first

        Returns:
            Merged CVData with combined sections, or None if either input is None
        """
        if cv_data1 is None or cv_data2 is None:
            logger.warning("Cannot merge: one or both CVData objects are None")
            return None

        try:
            # Merge sections
            merged = CVData(
                session_id=cv_data1.session_id,
                user_id=cv_data1.user_id,
                interview_path=cv_data1.interview_path,
                language_input=cv_data1.language_input
            )

            merged.background = cv_data1.background + cv_data2.background
            merged.experience = cv_data1.experience + cv_data2.experience
            merged.skills = cv_data1.skills + cv_data2.skills
            merged.motivation = cv_data1.motivation + cv_data2.motivation
            merged.training = cv_data1.training + cv_data2.training
            merged.projects = cv_data1.projects + cv_data2.projects

            # Deduplicate skills
            all_skills = set(cv_data1.all_skills or []) | set(cv_data2.all_skills or [])
            merged.all_skills = sorted(list(all_skills))

            # Recalculate overall quality
            all_sections = (
                merged.background + merged.experience + merged.skills +
                merged.motivation + merged.training + merged.projects
            )
            quality_scores = [s.quality_score for s in all_sections if s.quality_score is not None]
            if quality_scores:
                merged.overall_quality = sum(quality_scores) / len(quality_scores)

            merged.ready_for_export = merged.overall_quality >= 0.5
            logger.info(f"Merged CVData: {len(all_sections)} sections, quality {merged.overall_quality:.2f}")
            return merged

        except Exception as e:
            logger.error(f"Error merging CVData: {e}")
            return None
