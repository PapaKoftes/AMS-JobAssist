"""
Polish Engine - Transforms raw interview answers into polished CV content.

Handles:
1. Verb enforcement (weak → strong verbs)
2. Skill normalization (user terms → standardized skills)
3. Structure validation
4. Confidence scoring
5. Language normalization
"""

import logging
import re
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

from .language import LanguageNormalizer
from cv.models import CVSection, QuestionCategory

try:
    from ai.local_llm import (
        polish_answer as _local_polish,
        enhance_polished as _local_enhance,
        is_ready as _local_ready,
        get_status as _local_status,
    )
    _LOCAL_AI = True
except ImportError:
    _LOCAL_AI = False
    def _local_polish(*a, **kw): return None
    def _local_enhance(*a, **kw): return None
    def _local_ready(): return False
    def _local_status(): return {"local_model_available": False}

try:
    from ai.ollama import polish_with_ollama as _ollama_polish, get_status as _ollama_status
    _OLLAMA_AI = True
except ImportError:
    _OLLAMA_AI = False
    def _ollama_polish(*a, **kw): return None
    def _ollama_status(): return {"ollama_available": False}

try:
    from ai.knowledge import find_job, get_context_for_prompt, get_verbs_for_job, get_skills_for_job
    _HAS_KNOWLEDGE = True
except ImportError:
    _HAS_KNOWLEDGE = False
    def find_job(t): return None
    def get_context_for_prompt(t, c=""): return ""
    def get_verbs_for_job(t, l="de"): return []
    def get_skills_for_job(t): return []


def ai_enhance(rule_polished_text, category="experience", lang="de", knowledge_ctx=""):
    """Enhance ALREADY rule-polished text with LLM. Lighter task = faster + better.

    Pipeline: Rules handle verbs/skills/structure FIRST → LLM only rephrases for
    natural flow, injecting domain knowledge from the Austrian job knowledge base.

    Priority chain: Local GGUF → Ollama → None (rule output used as-is).
    """
    # Tier 1: local GGUF model — purpose-built enhance prompt
    if _LOCAL_AI and _local_ready():
        result = _local_enhance(rule_polished_text, category, lang, knowledge_ctx)
        if result:
            return result

    # Tier 2: Ollama — fall back to full polish (no enhance endpoint)
    result = _ollama_polish(rule_polished_text, category, lang)
    if result:
        return result

    # Tier 3: rule output is already good — return None so caller keeps it
    return None


def ai_polish(text, category="experience", lang="de"):
    """Full LLM polish — used for non-rule-processed paths (translation, chat).

    For the main polish pipeline, prefer ai_enhance() which takes rule-polished
    text and does a lighter enhancement task.
    """
    if _LOCAL_AI and _local_ready():
        result = _local_polish(text, category, lang)
        if result:
            return result
    result = _ollama_polish(text, category, lang)
    if result:
        return result
    return None


def ai_get_status():
    """Return which AI engine is active. Priority: Local LLM > Ollama > Rules."""
    local = _local_status()
    if local.get("local_model_available"):
        return {**local, "mode": "Lokales KI-Modell", "active_engine": "local"}
    ollama = _ollama_status()
    if ollama.get("ollama_available"):
        return {**ollama, "mode": "Ollama", "active_engine": "ollama"}
    return {"mode": "Regelbasiert", "active_engine": "rules", "ollama_available": False, "local_model_available": False}

logger = logging.getLogger(__name__)


@dataclass
class QualityScore:
    """Quality assessment for polished content."""
    overall_score: float  # 0.0 - 1.0
    verb_strength: float  # How strong the verbs are
    skill_clarity: float  # How clear the skills are
    structure_score: float  # How well-structured the text is
    confidence_level: str  # low, medium, high
    suggestions: List[str]  # Improvement suggestions


class PolishEngine:
    """
    Transforms raw answers into polished CV content.

    Pipeline:
    1. Normalize whitespace and fix basic errors
    2. Enforce strong verbs
    3. Normalize and extract skills
    4. Validate structure
    5. Score quality
    6. Generate suggestions
    """

    def __init__(self, db_manager):
        """
        Initialize polish engine.

        Args:
            db_manager: DatabaseManager instance
        """
        self.db = db_manager
        self.language_normalizer = LanguageNormalizer()
        self._verb_map = None       # English weak→strong verbs
        self._de_verb_map = None    # German weak→strong verbs
        self._skill_map = None      # All-language skill terms
        self._verb_regex = None     # Compiled EN verb pattern (cached)
        self._de_verb_regex = None  # Compiled DE verb pattern (cached)
        self._load_mappings()

    def _load_mappings(self):
        """Load verb and skill mappings from database (all languages)."""
        try:
            # English verb replacements
            verb_results = self.db.execute_query(
                "SELECT weak_verb, strong_verb FROM verb_replacements "
                "WHERE language = 'en' OR language IS NULL"
            )
            self._verb_map = {row['weak_verb'].lower(): row['strong_verb']
                            for row in verb_results}

            # German verb replacements (separate map, applied to German field)
            de_verb_results = self.db.execute_query(
                "SELECT weak_verb, strong_verb FROM verb_replacements WHERE language = 'de'"
            )
            self._de_verb_map = {row['weak_verb'].lower(): row['strong_verb']
                               for row in de_verb_results}

            # Skill dictionary — ALL languages (key terms in any language)
            skill_results = self.db.execute_query(
                "SELECT key_term, normalized_skill FROM skills_dictionary"
            )
            self._skill_map = {row['key_term'].lower(): row['normalized_skill']
                             for row in skill_results}

            logger.info(
                f"Loaded mappings: {len(self._verb_map)} EN verbs, "
                f"{len(self._de_verb_map)} DE verbs, "
                f"{len(self._skill_map)} skills (all languages)"
            )

            # Pre-compile verb regex patterns (avoids recompilation on every call)
            self._verb_regex = self._compile_verb_regex(self._verb_map)
            self._de_verb_regex = self._compile_verb_regex(self._de_verb_map)

        except Exception as e:
            logger.error(f"Error loading mappings: {e}")
            self._verb_map = {}
            self._de_verb_map = {}
            self._skill_map = {}
            self._verb_regex = None
            self._de_verb_regex = None

    def polish_answer(self, answer_text: str, category: str,
                      hint_language: str = "") -> Dict[str, Any]:
        """
        Polish a single answer for CV inclusion (used by preview endpoint).

        Language-aware: German input gets German verb enforcement; English gets
        English verb enforcement; other languages get skill extraction + minimal
        normalization. The returned `polished_text` is always in the input language
        so the live-preview split stays readable for the user.

        Args:
            answer_text: Raw user answer (any language)
            category: Question category
            hint_language: Optional ISO-639-1 code from the UI language picker

        Returns:
            Dict with polished_text, extracted_skills, quality_score, changes, etc.
        """
        if not answer_text or not answer_text.strip():
            return {
                "polished_text": "",
                "extracted_skills": [],
                "quality_score": QualityScore(0.0, 0.0, 0.0, 0.0, "low", ["Antwort ist leer"]),
                "suggestions": ["Bitte geben Sie eine Antwort ein"],
                "detected_language": "unknown",
                "language_confidence": {},
            }

        try:
            # Detect language; prefer explicit hint from UI over auto-detection
            detected_language = (
                hint_language
                or self.language_normalizer.detect_language(answer_text)
            )
            language_confidence = self.language_normalizer.get_language_confidence(answer_text)

            # ── STEP 1: RULES FIRST (always run, fast, deterministic) ────────
            normalized = self._normalize_text(answer_text)
            if detected_language == "de":
                with_strong_verbs, verb_changes = self._enforce_german_verbs_tracked(normalized)
            elif detected_language == "en":
                with_strong_verbs, verb_changes = self._enforce_strong_verbs_tracked(normalized)
            else:
                # Other languages: minimal normalisation, no verb rewriting
                with_strong_verbs = normalized
                verb_changes = []

            # ── STEP 2: KNOWLEDGE RETRIEVAL (augment with Austrian job data) ──
            knowledge_ctx = ""
            if _HAS_KNOWLEDGE:
                knowledge_ctx = get_context_for_prompt(answer_text, category)

            # ── STEP 3: LLM ENHANCEMENT (optional, on rule-polished text) ────
            # LLM receives already-structured text + domain knowledge.
            # Its task is simpler: natural rephrasing, not rewriting from scratch.
            ai_enhanced = ai_enhance(with_strong_verbs, category, detected_language, knowledge_ctx)
            if ai_enhanced:
                with_strong_verbs = ai_enhanced
                verb_changes.append("KI-Verbesserung angewendet")
                ai_mode = True
            else:
                ai_mode = False

            # Skill extraction from ORIGINAL text (catches German/Turkish/Arabic terms)
            extracted_skills = self._extract_skills_multilang(answer_text)

            # Also extract knowledge-based skills if available
            if _HAS_KNOWLEDGE:
                job = find_job(answer_text)
                if job:
                    for skill in get_skills_for_job(job.get("id", "")):
                        if skill not in extracted_skills:
                            # Only add if the skill term appears in the text
                            if skill.lower() in answer_text.lower():
                                extracted_skills.append(skill)
            skill_changes = [f"Fähigkeit erkannt: '{s}'" for s in extracted_skills]

            # Structure validation and quality scoring
            _, structural_issues = self._validate_structure(with_strong_verbs)
            quality_score = self._score_quality(
                with_strong_verbs,
                extracted_skills,
                structural_issues,
                category,
                original_text=answer_text,
                detected_language=detected_language,
            )

            suggestions = self._generate_suggestions(
                with_strong_verbs, extracted_skills, quality_score, category
            )

            return {
                "polished_text": with_strong_verbs,
                "extracted_skills": extracted_skills,
                "quality_score": quality_score,
                "suggestions": suggestions,
                "detected_language": detected_language,
                "language_confidence": language_confidence,
                "changes": verb_changes + skill_changes,
                "ai_mode": ai_mode,
            }

        except Exception as e:
            logger.error(f"Error polishing answer: {e}")
            detected_language = hint_language or self.language_normalizer.detect_language(answer_text)
            return {
                "polished_text": answer_text,
                "extracted_skills": [],
                "quality_score": QualityScore(0.5, 0.5, 0.5, 0.5, "medium", [str(e)]),
                "suggestions": [],
                "detected_language": detected_language,
                "language_confidence": {},
            }

    def polish_answer_multilingual(
        self,
        answer_text: str,
        category: str,
        question_id: str,
        user_native_language: Optional[str] = None
    ) -> CVSection:
        """
        Polish a single answer and return as CVSection with 3 language versions.

        This is the Day 9-10 multilingual version that:
        1. Detects the input language
        2. Generates 3 polished versions (German, English, native)
        3. Extracts skills and scores quality
        4. Returns CVSection with all multilingual data

        Args:
            answer_text: Raw user answer (in any language)
            category: Question category (background, experience, skills, etc.)
            question_id: Question ID this answer is for
            user_native_language: User's detected native language (ISO 639-1 code)

        Returns:
            CVSection dataclass with:
            - german, english, native: Polished versions in 3 languages
            - category: QuestionCategory enum
            - question_id: Reference to question
            - detected_input_language: Language user wrote in
            - user_native_language: User's native language
            - quality_score, confidence_level: Quality metrics
            - detected_skills: Extracted and normalized skills
            - created_at, polished_at: Timestamps
        """
        if not answer_text or not answer_text.strip():
            empty_section = CVSection(
                german="",
                english="",
                native="",
                category=QuestionCategory(category) if isinstance(category, str) else category,
                question_id=question_id,
                detected_input_language="unknown",
                user_native_language=user_native_language or "unknown",
                quality_score=0.0,
                confidence_level="low",
                detected_skills=[],
                created_at=datetime.now().isoformat(),
                polished_at=datetime.now().isoformat()
            )
            return empty_section

        try:
            # Step 1: Detect language from raw input
            detected_language = self.language_normalizer.detect_language(answer_text)

            # Step 2: Normalise input for English CV pipeline.
            # We keep the ORIGINAL text for German processing to avoid losing umlauts.
            english_text, _ = self.language_normalizer.normalize_to_language(answer_text, "en")
            normalized_en = self._normalize_text(english_text)

            # ── STEP 3: RULES FIRST — verb enforcement on English field ──────
            with_strong_verbs, verb_changes = self._enforce_strong_verbs_tracked(normalized_en)

            # ── STEP 3b: Knowledge retrieval ─────────────────────────────────
            knowledge_ctx = ""
            if _HAS_KNOWLEDGE:
                knowledge_ctx = get_context_for_prompt(answer_text, category)

            # ── STEP 3c: LLM ENHANCEMENT — on rule-polished English text ─────
            ai_enhanced = ai_enhance(with_strong_verbs, category, detected_language, knowledge_ctx)
            if ai_enhanced:
                with_strong_verbs = ai_enhanced
                verb_changes.append("KI-Verbesserung angewendet")

            # Step 4: Extract skills from ORIGINAL text (catches German/Turkish/Arabic terms)
            # and also from English normalised text (catches English skill terms)
            extracted_skills = self._extract_skills_multilang(answer_text)
            skill_changes = [f"Fähigkeit erkannt: '{s}'" for s in extracted_skills]
            all_changes = verb_changes + skill_changes

            # Step 5: Build German CV field FIRST so we can score it.
            # German input → apply German verbs to original (preserves umlauts).
            # Other input → translate English-polished to German.
            if detected_language == "de":
                german_polished = self._normalize_text(answer_text)
                german_polished, de_verb_changes = self._enforce_german_verbs_tracked(german_polished)
                all_changes.extend(de_verb_changes)

                # Optionally enhance German text too
                de_enhanced = ai_enhance(german_polished, category, "de", knowledge_ctx)
                if de_enhanced:
                    german_polished = de_enhanced

                score_text = german_polished      # score the actual German output
            else:
                german_polished = self.language_normalizer.translate_to_german(with_strong_verbs)
                score_text = with_strong_verbs    # score English for non-German

            # Step 6: Validate structure (on the text we'll score)
            _, structural_issues = self._validate_structure(score_text)

            # Step 7: Score quality using language-aware scorer.
            quality_score = self._score_quality(
                score_text,
                extracted_skills,
                structural_issues,
                category,
                original_text=answer_text,
                detected_language=detected_language,
            )

            # Step 8: Native version
            if user_native_language and user_native_language not in ("de", "en"):
                # Keep original text (their native language) as native field
                native_polished = self._normalize_text(answer_text)
            elif user_native_language == "de":
                native_polished = german_polished
            else:
                native_polished = with_strong_verbs

            # Step 9: Create CVSection
            cv_section = CVSection(
                german=german_polished,
                english=with_strong_verbs,
                native=native_polished,
                category=QuestionCategory(category) if isinstance(category, str) else category,
                question_id=question_id,
                detected_input_language=detected_language,
                user_native_language=user_native_language or detected_language,
                quality_score=quality_score.overall_score,
                confidence_level=quality_score.confidence_level,
                detected_skills=extracted_skills,
                changes=all_changes,
                created_at=datetime.now().isoformat(),
                polished_at=datetime.now().isoformat()
            )

            logger.info(
                f"Polished multilingual answer: "
                f"lang={detected_language}, category={category}, "
                f"quality={quality_score.overall_score:.2f}, skills={len(extracted_skills)}"
            )

            return cv_section

        except Exception as e:
            logger.error(f"Error polishing multilingual answer: {e}")
            detected_language = self.language_normalizer.detect_language(answer_text)
            # Return empty section on error
            error_section = CVSection(
                german=answer_text,
                english=answer_text,
                native=answer_text,
                category=QuestionCategory(category) if isinstance(category, str) else category,
                question_id=question_id,
                detected_input_language=detected_language,
                user_native_language=user_native_language or detected_language,
                quality_score=0.5,
                confidence_level="medium",
                detected_skills=[],
                created_at=datetime.now().isoformat(),
                polished_at=datetime.now().isoformat()
            )
            return error_section

    def _normalize_text(self, text: str) -> str:
        """Normalize whitespace and basic errors."""
        # Strip leading/trailing whitespace
        text = text.strip()

        # Normalize multiple spaces
        text = re.sub(r'\s+', ' ', text)

        # Fix common capitalization issues
        # Capitalize first letter if it's lowercase
        if text and text[0].islower():
            text = text[0].upper() + text[1:]

        return text

    @staticmethod
    def _compile_verb_regex(verb_map: dict):
        """Compile a single regex matching all keys in verb_map (longest first).

        Returns None if the map is empty.  Called once at init time so the
        pattern is reused on every polish call instead of recompiling.
        """
        if not verb_map:
            return None
        return re.compile(
            r'\b(' + '|'.join(re.escape(k) for k in sorted(verb_map, key=len, reverse=True)) + r')\b',
            flags=re.IGNORECASE,
        )

    def _enforce_strong_verbs(self, text: str) -> str:
        """Replace weak verbs with strong verbs, preserving case."""
        polished, _ = self._enforce_strong_verbs_tracked(text)
        return polished

    def _enforce_strong_verbs_tracked(self, text: str) -> tuple:
        """
        Replace weak verbs with strong verbs in a SINGLE PASS and track changes.

        Single-pass replacement prevents cascading (e.g., A→B then B→C becoming A→C
        by accident).  A combined regex matches all weak verbs simultaneously so each
        position in the text is visited exactly once.

        Returns:
            (polished_text, changes) where changes is a list of human-readable
            transformation descriptions like "Replaced 'did' → 'executed'".
        """
        if not self._verb_map or not self._verb_regex:
            return text, []

        changes: list[str] = []
        replaced: set = set()

        def _sub(m):
            original = m.group(0)
            key = original.lower()
            strong = self._verb_map.get(key, original)
            if strong.lower() != key and key not in replaced:
                replaced.add(key)
                changes.append(f"Replaced '{key}' → '{strong}'")
            if original.isupper():
                return strong.upper()
            elif original[0].isupper():
                return strong[0].upper() + strong[1:]
            return strong

        result = self._verb_regex.sub(_sub, text)
        return result, changes

    def _enforce_german_verbs_tracked(self, text: str) -> tuple:
        """
        Replace weak German verb forms with stronger ones in a SINGLE PASS.

        Uses the same single-pass approach as _enforce_strong_verbs_tracked to
        prevent cascading replacements (e.g., A→B then B→C in the same run).
        """
        if not self._de_verb_map or not self._de_verb_regex:
            return text, []

        changes: list[str] = []
        replaced: set = set()

        def _sub(m):
            original = m.group(0)
            key = original.lower()
            strong = self._de_verb_map.get(key, original)
            if strong.lower() != key and key not in replaced:
                replaced.add(key)
                changes.append(f"Verb verbessert: '{key}' → '{strong}'")
            if original.isupper():
                return strong.upper()
            elif original[0].isupper():
                return strong[0].upper() + strong[1:]
            return strong

        result = self._de_verb_regex.sub(_sub, text)
        return result, changes

    def _score_german_verbs(self, text: str) -> float:
        """
        Score verb strength for German text.

        Detects:
        1. Strong verbs from our German verb map (values)
        2. German -ierte/-isierte participle/preterite forms (always professional)
        3. German ge-...-t/en perfect participles

        Returns a 0.0–1.0 score (0.5 fallback for empty / unparseable text).
        """
        text_lower = text.lower()
        words = text_lower.split()
        word_count = len(words)
        if word_count == 0:
            return 0.5

        # Build set of strong German CV verbs from our map values
        strong_de = {v.lower() for v in (self._de_verb_map or {}).values()}
        # Add common strong verbs not necessarily in the map
        strong_de.update({
            'koordiniert', 'koordinierte', 'leitete', 'geführt', 'entwickelt',
            'entwickelte', 'organisiert', 'organisierte', 'betreut', 'betreute',
            'verantwortet', 'verantwortete', 'erstellt', 'erstellte', 'verwaltet',
            'verwaltete', 'unterstützt', 'unterstützte', 'optimiert', 'optimierte',
            'realisiert', 'realisierte', 'konzipiert', 'konzipierte', 'überwacht',
            'überwachte', 'analysiert', 'analysierte', 'eingesetzt', 'angewendet',
            'umgesetzt', 'durchgeführt', 'abgerechnet', 'verfasst', 'aufgebaut',
            'bewältigt', 'angeeignet', 'vermittelt', 'erfasst', 'dokumentiert',
            'präsentiert', 'kommuniziert', 'koordinierend', 'leitend',
        })

        # Count direct matches in text
        direct_hits = sum(
            1 for w in words
            if w.rstrip('.,;:!?') in strong_de
        )

        # Count German professional verb patterns:
        # -ierte/-isierte (koordinierte, organisierte, informierte, optimierte)
        ierte_hits = len(re.findall(
            r'\b\w{4,}(?:isier|ier)te[ns]?\b', text_lower
        ))
        # ge-...-t/en perfect participles (koordiniert, entwickelt, eingesetzt)
        partizip_hits = len(re.findall(
            r'\bge[a-zäöüß]{3,}(?:t|en)\b', text_lower
        ))
        # -iert/-isiert participiples without ge- prefix (koordiniert, optimiert)
        partizip2_hits = len(re.findall(
            r'\b[a-zäöüß]{4,}(?:isier|ier)t\b', text_lower
        ))

        total_action = direct_hits + ierte_hits + partizip_hits + partizip2_hits
        ratio = total_action / max(word_count, 1)

        if ratio >= 0.15:
            return 0.9
        elif ratio >= 0.08:
            return 0.75
        elif ratio >= 0.04:
            return 0.6
        elif ratio >= 0.02:
            return 0.5
        else:
            return 0.4

    def _extract_skills_multilang(self, text: str) -> List[str]:
        """
        Extract skills from text in ANY language.

        Searches the original (un-normalised) text so that German terms like
        'kassensystem', Turkish 'mutfak', and Arabic 'مطبخ' are all matched
        against the multilingual skills_dictionary loaded from the DB.
        """
        if not self._skill_map:
            return []
        found_skills = []
        text_lower = text.lower()
        for key_term, normalized_skill in self._skill_map.items():
            if key_term in text_lower and normalized_skill not in found_skills:
                found_skills.append(normalized_skill)
        return found_skills

    def _validate_structure(self, text: str) -> Tuple[bool, List[str]]:
        """Validate the structure of the text."""
        issues = []

        # Check sentence structure
        sentences = text.split('.')
        if len(sentences) < 2:
            issues.append("Nur ein Satz — fügen Sie mehr Details hinzu")

        # Check for run-on sentences (very long without punctuation)
        long_sentences = [s for s in sentences if len(s.split()) > 30]
        if long_sentences:
            issues.append(f"Einige Sätze sind sehr lang ({len(long_sentences[0].split())} Wörter)")

        # Check for concrete details
        has_numbers = bool(re.search(r'\d+', text))
        if not has_numbers:
            issues.append("Fügen Sie spezifische Zahlen, Daten oder Ergebnisse hinzu")

        # Check for vague terms — both English and German
        _vague = ['thing', 'stuff', 'many', 'lots',
                  'dinge', 'sachen', 'einiges', 'vieles', 'irgendwas', 'verschiedenes']
        if any(word in text.lower() for word in _vague):
            issues.append("Verwenden Sie spezifischere Begriffe statt vager Ausdrücke")

        is_valid = len(issues) == 0
        return is_valid, issues

    def _score_quality(self, text: str, skills: List[str],
                      issues: List[str], category: str,
                      original_text: str = "",
                      detected_language: str = "") -> QualityScore:
        """Score the overall quality of the polished text.

        Args:
            text: The polished/processed text to score
            skills: Extracted skill list
            issues: Structural issues list
            category: Question category
            original_text: Raw answer before normalisation (used for word-count bonus)
            detected_language: ISO-639-1 code — selects language-appropriate verb scoring
        """

        # Language-aware verb strength scoring
        _NON_LATIN_LANGS = {"ar", "uk", "ru"}  # scripts where Latin regex is useless
        _OTHER_LANGS = {"tr", "bs", "hr", "sr", "pl", "ro", "sk"}  # Latin but non-English
        if detected_language == "de":
            # Use German verb patterns on the original or current text
            ref_for_verbs = original_text if original_text else text
            verb_strength = self._score_german_verbs(ref_for_verbs)
        elif detected_language in _NON_LATIN_LANGS:
            # Non-Latin script: English verb regex never fires — avoid penalising.
            # Give a neutral-positive score; word-count bonus below rewards detail.
            verb_strength = 0.55
        elif detected_language in _OTHER_LANGS:
            # Latin-script but not English: some regex matches may fire coincidentally.
            # Try English scoring but floor at 0.55 so thorough answers pass.
            verbs_found = 0
            strong_verbs_found = 0
            strong_en_values = {v.lower() for v in (self._verb_map or {}).values()}
            for verb in re.findall(r'\b[a-z]+ed\b|\b[a-z]+ing\b|\b[a-z]+s\b', text.lower()):
                verbs_found += 1
                if verb in strong_en_values:
                    strong_verbs_found += 1
            raw = (strong_verbs_found / verbs_found) if verbs_found > 0 else 0.0
            verb_strength = max(0.55, raw)  # floor prevents unfair penalisation
        else:
            # English or unknown: use English verb pattern matching as-is
            verbs_found = 0
            strong_verbs_found = 0
            strong_en_values = {v.lower() for v in (self._verb_map or {}).values()}
            for verb in re.findall(r'\b[a-z]+ed\b|\b[a-z]+ing\b|\b[a-z]+s\b', text.lower()):
                verbs_found += 1
                if verb in strong_en_values:
                    strong_verbs_found += 1
            verb_strength = (strong_verbs_found / verbs_found) if verbs_found > 0 else 0.5

        # Calculate skill clarity
        # For non-English/German text the skill DB may not match foreign-language terms.
        # Avoid double-penalising: if the answer is long but no skills detected, use
        # neutral (0.5) instead of the penalty (0.3).
        ref_word_count = len((original_text or text).split())
        if not skills and detected_language not in ("de", "en") and ref_word_count >= 12:
            skill_clarity = 0.5   # long answer but skills undetectable in this language
        elif skills:
            skill_clarity = 1.0 if len(skills) <= 3 else 0.9
        else:
            skill_clarity = 0.3

        # Calculate structure score
        structure_score = 1.0 - (len(issues) * 0.15)  # Each issue reduces score by 15%
        structure_score = max(0.3, structure_score)

        # Word-count bonus: reward answers that clearly contain real detail.
        # This compensates for the English-biased verb/skill scoring when the
        # user writes a thorough answer in German or another non-English language.
        ref_text = original_text if original_text else text
        word_count = len(ref_text.split())
        if word_count >= 30:
            word_bonus = 0.12
        elif word_count >= 20:
            word_bonus = 0.08
        elif word_count >= 12:
            word_bonus = 0.04
        else:
            word_bonus = 0.0

        # Overall score
        overall_score = min(1.0, (verb_strength + skill_clarity + structure_score) / 3 + word_bonus)

        # Determine confidence level
        if overall_score >= 0.75:
            confidence = "high"
        elif overall_score >= 0.5:
            confidence = "medium"
        else:
            confidence = "low"

        suggestions = []
        if verb_strength < 0.5:
            suggestions.append("Verwenden Sie mehr Tätigkeitsverben, um Ihre Erfahrung zu beschreiben")
        if not skills:
            suggestions.append("Nennen Sie spezifische Werkzeuge, Technologien oder Fähigkeiten")
        if len(issues) > 0:
            suggestions.extend(issues[:2])  # Top 2 structural issues

        return QualityScore(
            overall_score=overall_score,
            verb_strength=verb_strength,
            skill_clarity=skill_clarity,
            structure_score=structure_score,
            confidence_level=confidence,
            suggestions=suggestions
        )

    def _generate_suggestions(self, text: str, skills: List[str],
                            quality_score: QualityScore, category: str) -> List[str]:
        """Generate improvement suggestions based on category and content."""
        suggestions = list(quality_score.suggestions)

        # Category-specific suggestions
        if category == "experience":
            if not re.search(r'\d+', text):
                suggestions.append("Fügen Sie Zahlen hinzu: Mitarbeiter, Projekte, Ergebnisse")
            if 'impact' not in text.lower() and 'result' not in text.lower() and 'ergebnis' not in text.lower():
                suggestions.append("Beschreiben Sie den Nutzen Ihrer Arbeit, nicht nur die Aufgaben")

        elif category == "skills":
            if len(skills) < 3:
                suggestions.append("Nennen Sie mehr spezifische technische oder soziale Fähigkeiten")

        elif category == "background":
            if 'certificate' not in text.lower() and 'degree' not in text.lower() and 'zertifikat' not in text.lower():
                suggestions.append("Klären Sie die Art des Abschlusses (Diplom, Zertifikat, Ausbildung)")

        elif category == "motivation":
            if not any(word in text.lower() for word in ['interested', 'want', 'passion', 'goal', 'interesse', 'möchte', 'ziel']):
                suggestions.append("Drücken Sie Ihre Motivation klar aus (Was interessiert Sie?)")

        return suggestions[:3]  # Limit to 3 suggestions

    def polish_session(self, session_id: int, answers: Dict[str, str],
                     question_categories: Dict[str, str]) -> Dict[str, Any]:
        """
        Polish all answers for a completed session.

        Args:
            session_id: Interview session ID
            answers: Dict of question_id → answer_text
            question_categories: Dict of question_id → category

        Returns:
            Dict with polished CV data
        """
        polished_answers = {}
        all_skills = []
        overall_quality = []

        for question_id, answer_text in answers.items():
            category = question_categories.get(question_id, "general")
            polished = self.polish_answer(answer_text, category)

            polished_answers[question_id] = {
                "raw": answer_text,
                "polished": polished["polished_text"],
                "skills": polished["extracted_skills"],
                "quality": {
                    "overall": polished["quality_score"].overall_score,
                    "verb_strength": polished["quality_score"].verb_strength,
                    "skill_clarity": polished["quality_score"].skill_clarity,
                    "structure": polished["quality_score"].structure_score,
                    "confidence": polished["quality_score"].confidence_level,
                }
            }

            all_skills.extend(polished["extracted_skills"])
            overall_quality.append(polished["quality_score"].overall_score)

        # Deduplicate skills
        unique_skills = list(set(all_skills))

        # Calculate session-wide quality
        session_quality = (sum(overall_quality) / len(overall_quality)) if overall_quality else 0.0

        return {
            "session_id": session_id,
            "polished_answers": polished_answers,
            "extracted_skills": unique_skills,
            "overall_quality_score": session_quality,
            "ready_for_export": session_quality >= 0.5
        }
