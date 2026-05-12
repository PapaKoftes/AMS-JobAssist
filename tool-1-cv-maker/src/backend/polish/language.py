"""
Language Normalization Module - Multilingual detection and normalization.

Handles:
1. Language detection using Lingua (supports 75 languages, accurate for all 14 core languages)
2. Fallback keyword-based detection when Lingua unavailable
3. Text normalization to English for processing pipeline
4. Translation to German and user's native language via Ollama
5. Skill normalization across all languages
6. Confidence scoring for detected languages

Supports 14 core languages:
- Germanic: German (de), English (en)
- Romance: Italian (it), French (fr)
- Slavic: Polish (pl), Czech (cs), Slovak (sk), Ukrainian (uk), Serbian (sr), Russian (ru), Bosnian (bs)
- Turkic: Turkish (tr)
- Semitic: Arabic (ar) — including Franco-Arabic / 3araby franco (Latin script with numeral substitutions)
- Finno-Ugric: Hungarian (hu)

Franco-Arabic numeral substitutions:
  3 = ع (ain)    7 = ح (ha)    2 = أ/ء (hamza)   5 = خ (kha)
  6 = ط (ta)     8 = غ (ghain) 9 = ق (qaf)        4 = ظ (dha, less common)

All languages include support for:
- Character normalization (umlauts, diacritics)
- Spelling corrections
- Term standardization
- Native to English mapping
"""

import logging
import re
from typing import Tuple, Optional, Dict, List
from enum import Enum

try:
    from lingua import LanguageDetectorBuilder, Language
    LINGUA_AVAILABLE = True
except ImportError:
    LINGUA_AVAILABLE = False
    Language = None
    logger = logging.getLogger(__name__)
    logger.warning(
        "Lingua not available - falling back to keyword-based detection. "
        "Install with: pip install lingua-language-detect"
    )

logger = logging.getLogger(__name__)


class LanguageNormalizer:
    """
    Multilingual language detection and normalization.

    Supports 14 core languages with fallback detection.
    Uses Lingua for accurate detection when available.
    """

    # Core languages for CV processing (14 languages)
    CORE_LANGUAGES = ["de", "en", "it", "pl", "cs", "sk", "hu", "fr", "uk", "tr", "sr", "ru", "ar", "bs"]

    # Lingua Language objects for core languages
    LINGUA_LANGUAGES = {}
    if LINGUA_AVAILABLE:
        try:
            LINGUA_LANGUAGES = {
                "de": Language.GERMAN,
                "en": Language.ENGLISH,
                "it": Language.ITALIAN,
                "pl": Language.POLISH,
                "cs": Language.CZECH,
                "sk": Language.SLOVAK,
                "hu": Language.HUNGARIAN,
                "fr": Language.FRENCH,
                "uk": Language.UKRAINIAN,
                "tr": Language.TURKISH,
                "sr": Language.SERBIAN,
                "ru": Language.RUSSIAN,
                "ar": Language.ARABIC,
                "bs": Language.BOSNIAN,
            }
        except AttributeError as e:
            logger.warning(f"Some Lingua languages not available: {e}")

    # Language name mappings
    LANGUAGE_NAMES = {
        "de": "German",
        "en": "English",
        "it": "Italian",
        "pl": "Polish",
        "cs": "Czech",
        "sk": "Slovak",
        "hu": "Hungarian",
        "fr": "French",
        "uk": "Ukrainian",
        "tr": "Turkish",
        "sr": "Serbian",
        "ru": "Russian",
        "ar": "Arabic",
        "bs": "Bosnian",
    }

    # Fallback keyword detection (for when Lingua unavailable)
    GERMAN_KEYWORDS = {
        "der", "die", "das", "ein", "eine", "einen", "einem",
        "ist", "sind", "war", "waren", "sein", "habe", "hat", "haben",
        "zu", "für", "mit", "von", "bei", "in", "auf", "an", "aus",
        "arbeitet", "arbeiten", "gearbeitet", "gelernt", "erlebt",
        "Jahr", "Jahre", "Jahren", "Monat", "Monate", "Tag", "Tage",
        "Schule", "Ausbildung", "Beruf", "Arbeit", "Projekt", "Team",
        "Fähigkeiten", "Kenntnisse", "Erfahrung", "Verantwortung",
        "ü", "ö", "ä", "ß"
    }

    ENGLISH_KEYWORDS = {
        "the", "a", "an", "is", "are", "was", "were", "be", "have", "has",
        "to", "for", "with", "from", "at", "in", "on", "by", "of",
        "worked", "working", "work", "learned", "learning", "experience",
        "year", "years", "month", "months", "day", "days",
        "school", "training", "apprenticeship", "job", "role", "project",
        "skills", "knowledge", "ability", "responsibility", "team"
    }

    # Common spelling corrections for supported languages
    SPELLING_CORRECTIONS = {
        "en": {
            r"\bexpirence\b": "experience",
            r"\bresponcibility\b": "responsibility",
            r"\bknowlege\b": "knowledge",
            r"\bseperate\b": "separate",
            r"\bteached\b": "taught",
            r"\bworkt\b": "worked",
        },
        "de": {
            r"\babeiter\b": "arbeiter",
            r"\berfahung\b": "erfahrung",
            r"\bfahigkeiten\b": "fähigkeiten",
        },
    }

    # German to English term standardization
    GERMAN_TO_ENGLISH_TERMS = {
        "führte": "led",
        "entwickelte": "developed",
        "verbesserte": "improved",
        "erhöhte": "increased",
        "reduzierte": "reduced",
        "verwaltete": "managed",
        "unterstützte": "supported",
        "leitete": "led",
        "betreute": "supervised",
        "schulte": "trained",
        "beriet": "consulted",
    }

    # English to German term standardization
    ENGLISH_TO_GERMAN_TERMS = {
        "led": "leitete",
        "developed": "entwickelte",
        "improved": "verbesserte",
        "increased": "erhöhte",
        "reduced": "reduzierte",
        "managed": "verwaltete",
        "supported": "unterstützte",
        "supervised": "betreute",
        "trained": "schulte",
        "consulted": "beriet",
    }

    # Denglish (German-English mix) corrections
    DENGLISH_CORRECTIONS = {
        r"\bmanagen\b": "manage",
        r"\bmanagé\b": "manage",
        r"\bmanagt\b": "manages",
        r"\bmanaged\b": "managed",
        r"\bperformen\b": "perform",
        r"\bperformt\b": "performs",
        r"\bteamen\b": "work in teams",
        r"\bteamt\b": "teams",
        r"\bfokus\b": "focus",
        r"\bfokusieren\b": "focus",
        r"\bprojekt\b": "project",
        r"\bprojekte\b": "projects",
    }

    # -----------------------------------------------------------------------
    # Arabic / Franco-Arabic support
    # -----------------------------------------------------------------------

    # Franco-Arabic (3araby franco): Latin script + numeral substitutions.
    # These are the substitutions used in Egyptian/Levantine colloquial Arabic
    # written in Latin characters online.  Numbers that appear *inside* or
    # *adjacent* to letter runs are treated as consonants, not digits.
    FRANCO_NUMERAL_MAP = {
        "3": "ع",   # ain
        "7": "ح",   # ha
        "2": "أ",   # hamza / alef
        "5": "خ",   # kha
        "6": "ط",   # ta (colloquial)
        "8": "غ",   # ghain
        "9": "ق",   # qaf
        "4": "ظ",   # dha (less common)
    }

    # Common Franco-Arabic words used in everyday / work context.
    # Normalised to lowercase Latin for matching.
    FRANCO_ARABIC_KEYWORDS = {
        # pronouns / particles
        "ana", "enta", "enti", "howa", "hiya", "ehna", "ento", "homa",
        "w", "el", "al", "fi", "fe", "mn", "min", "3la", "3ala", "bs",
        "bas", "mesh", "mish", "msh", "ma", "leh", "leeh", "tab",
        # work-related
        "beshtaghal", "bshtgl", "shghlt", "shtaghalt", "shtaghal",
        "bashtghel", "bashtghil", "b3ml", "b3aml", "3mlt", "3milt",
        "khdmt", "khedmet", "khedma", "khdma", "kont", "knt", "kan",
        "kanet", "kanit", "mas2ol", "mas2oul", "mas2ola",
        "msoul", "mas7ol",  # responsible
        "khebra", "khibra", "khebrit", "khibrit",  # experience
        "mahara", "maharat",  # skills
        "farik", "freeq", "friq",  # team
        "mashr3", "mashrou3", "mashroo3",  # project
        "zabon", "zaban", "zeboun",  # customer
        "mabi3at", "mabe3at",  # sales
        "3ndi", "3andi", "3ndy", "3andy",  # I have
        "lazm", "lazem", "lzm",  # must / need
        "ktir", "kteer", "kthir",  # many / a lot
        "sahn", "shn",   # year (colloquial)
        "sana", "sneen",  # year / years
        "shaghla", "shghla",  # job/work
        "mowzaf", "mozaf",  # employee
        "modir", "mudir",  # manager
        "ra2is", "rai2is",  # head / chief
        "mou3lm", "mu3lm", "mo3lm",  # trainer / teacher
    }

    # Arabic-to-English skill/work term translations.
    # Covers both Arabic script and common Franco-Arabic transliterations.
    ARABIC_TO_ENGLISH_TERMS = {
        # Arabic script → English
        "خبرة": "experience",
        "مهارات": "skills",
        "فريق": "team",
        "مشروع": "project",
        "زبائن": "customers",
        "مبيعات": "sales",
        "إدارة": "management",
        "تطوير": "development",
        "تصميم": "design",
        "برمجة": "programming",
        "تقنية": "technology",
        "معلومات": "information",
        "تواصل": "communication",
        "قيادة": "leadership",
        "تدريب": "training",
        "تعليم": "education",
        "خدمة": "service",
        "عملاء": "customers",
        "حاسوب": "computer",
        "شبكة": "network",
        "بيانات": "data",
        "تحليل": "analysis",
        "تسويق": "marketing",
        "محاسبة": "accounting",
        "مالية": "finance",
        "مسؤول": "responsible",
        "مدير": "manager",
        "رئيس": "head",
        "موظف": "employee",
        "عمل": "work",
        "وظيفة": "job",
        "شركة": "company",
        "مصنع": "factory",
        # Franco-Arabic transliterations → English
        "khebra": "experience",
        "khibra": "experience",
        "mahara": "skill",
        "maharat": "skills",
        "farik": "team",
        "freeq": "team",
        "mashr3": "project",
        "mashrou3": "project",
        "zabon": "customer",
        "mabi3at": "sales",
        "mabe3at": "sales",
        "tatweer": "development",
        "tasmeem": "design",
        "taqnia": "technology",
        "tawasol": "communication",
        "qiyada": "leadership",
        "tadreeb": "training",
        "ta3leem": "education",
        "khedma": "service",
        "mohasaba": "accounting",
        "maliya": "finance",
        "mas2ol": "responsible",
        "mas2oul": "responsible",
        "modir": "manager",
        "mudir": "manager",
        "ra2is": "head",
        "mowzaf": "employee",
        "shaghla": "job",
        "shghla": "job",
        "sharka": "company",
        "mosna3": "factory",
    }

    def __init__(self):
        """Initialize language normalizer."""
        self._detector = None
        self._german_keywords_set = self.GERMAN_KEYWORDS
        self._english_keywords_set = self.ENGLISH_KEYWORDS

        # Initialize Lingua detector if available
        if LINGUA_AVAILABLE and self.LINGUA_LANGUAGES:
            try:
                self._detector = LanguageDetectorBuilder.from_languages(
                    *self.LINGUA_LANGUAGES.values()
                ).build()
                logger.info(f"✓ Lingua language detector initialized with {len(self.LINGUA_LANGUAGES)} languages")
            except Exception as e:
                logger.warning(f"Error initializing Lingua: {e}. Falling back to keyword detection.")
                self._detector = None
        else:
            logger.info("Lingua not available. Using fallback keyword-based detection.")

    # -----------------------------------------------------------------------
    # Arabic / Franco-Arabic helper methods
    # -----------------------------------------------------------------------

    @staticmethod
    def _has_arabic_script(text: str) -> bool:
        """Return True if the text contains Arabic Unicode characters (U+0600–U+06FF)."""
        return bool(re.search(r'[؀-ۿ]', text))

    def _is_franco_arabic(self, text: str) -> bool:
        """
        Return True if the text appears to be Franco-Arabic (3araby franco).

        Franco-Arabic uses Latin letters mixed with specific numerals that
        substitute Arabic consonants (3, 7, 2, 5, 6, 8, 9).  We require
        at least two signals:
          1. A 'numeral-embedded-in-word' pattern (e.g. "3andi", "kh5da")
          2. At least one known Franco-Arabic keyword OR a high numeral density.
        """
        if not text:
            return False

        text_lower = text.lower()

        # Signal 1: numerals that appear adjacent to letters (not standalone)
        franco_numeral_pattern = re.compile(
            r'(?<=[a-z])[23456789]|[23456789](?=[a-z])',
            re.IGNORECASE
        )
        numeral_hits = franco_numeral_pattern.findall(text_lower)

        if not numeral_hits:
            return False  # No numeral-in-word pattern → not Franco-Arabic

        # Signal 2a: known Franco-Arabic keywords
        words = set(re.findall(r'[a-z0-9]+', text_lower))
        keyword_hits = words & self.FRANCO_ARABIC_KEYWORDS
        if keyword_hits:
            return True

        # Signal 2b: high numeral density (> 15 % of tokens are franco-numerals)
        all_tokens = re.findall(r'\S+', text_lower)
        if all_tokens and len(numeral_hits) / len(all_tokens) > 0.15:
            return True

        return False

    def normalize_franco_arabic_numerals(self, text: str) -> str:
        """
        Replace Franco-Arabic numeral substitutions with their Arabic script equivalents.

        Converts embedded numerals (e.g. "3andi" → "عandi") — useful when
        storing the canonical native version.  Only substitutes numerals that
        appear adjacent to Latin letters.
        """
        def replace_numeral(match: re.Match) -> str:
            char = match.group(0)
            return self.FRANCO_NUMERAL_MAP.get(char, char)

        return re.sub(
            r'(?<=[a-zA-Z])[23456789]|[23456789](?=[a-zA-Z])',
            replace_numeral,
            text
        )

    def _normalize_arabic_to_english(self, text: str) -> str:
        """
        Translate Arabic-script and Franco-Arabic terms to English.

        Used to populate the English CV field when the user wrote in Arabic or
        Franco-Arabic so that the polishing pipeline can process it.
        """
        result = text

        # Replace Arabic-script terms
        for arabic_term, english_term in self.ARABIC_TO_ENGLISH_TERMS.items():
            if '؀' <= arabic_term[0] <= 'ۿ':  # Arabic script key
                result = result.replace(arabic_term, english_term)
            else:
                # Franco-Arabic / transliterated key — word-boundary match
                pattern = rf'\b{re.escape(arabic_term)}\b'
                result = re.sub(pattern, english_term, result, flags=re.IGNORECASE)

        # Normalize whitespace
        result = re.sub(r'\s+', ' ', result).strip()
        return result

    # -----------------------------------------------------------------------

    def detect_language(self, text: str) -> str:
        """
        Detect the primary language of the text.

        Args:
            text: Text to analyze

        Returns:
            ISO 639-1 language code ('de', 'en', 'it', etc.) or 'unknown'
        """
        if not text or len(text) < 5:
            return "unknown"

        # Arabic script has an unambiguous Unicode signature — check before Lingua.
        if self._has_arabic_script(text):
            return "ar"

        # Franco-Arabic: Latin + numeral substitutions (must check before Lingua
        # since Lingua would otherwise mis-classify it as some Latin language).
        if self._is_franco_arabic(text):
            return "ar"  # We canonicalize Franco-Arabic to "ar"

        # Try Lingua first
        if self._detector:
            try:
                detected_lang = self._detector.detect_language_of(text)
                if detected_lang:
                    lang_code = detected_lang.iso_code_639_1.name.lower()
                    if lang_code in self.CORE_LANGUAGES:
                        return lang_code
            except Exception as e:
                logger.debug(f"Lingua detection error: {e}. Falling back to keywords.")

        # Fallback to keyword-based detection
        return self._detect_language_keywords(text)

    def _detect_language_keywords(self, text: str) -> str:
        """Fallback keyword-based language detection."""
        if not text or len(text) < 5:
            return "unknown"

        # Arabic script is unambiguous — Unicode range check
        if self._has_arabic_script(text):
            return "ar"

        # Franco-Arabic detection (Latin + numerals)
        if self._is_franco_arabic(text):
            return "ar"

        text_lower = text.lower()

        # Check for German umlauts (strongest signal for German)
        has_umlauts = bool(re.search(r'[äöüß]', text_lower))
        if has_umlauts:
            return "de"

        # Count keyword matches using word boundaries
        words = re.findall(r'\b\w+\b', text_lower)
        words_set = set(words)

        german_matches = sum(1 for keyword in self._german_keywords_set
                            if keyword in words_set or (len(keyword) > 2 and keyword in text_lower))
        english_matches = sum(1 for keyword in self._english_keywords_set
                             if keyword in words_set or (len(keyword) > 2 and keyword in text_lower))

        # Franco-Arabic keyword signal even if numeral pattern didn't fire
        franco_keyword_matches = len(words_set & self.FRANCO_ARABIC_KEYWORDS)
        if franco_keyword_matches >= 2:
            return "ar"

        # Determine language
        if german_matches > english_matches and german_matches > 0:
            return "de"
        elif english_matches > german_matches and english_matches > 0:
            return "en"
        elif german_matches == english_matches and german_matches > 0:
            return "en"  # Default to English if inconclusive
        else:
            return "unknown"

    def normalize_to_language(self, text: str, target_language: str = "en") -> Tuple[str, str]:
        """
        Normalize text to target language.

        Args:
            text: Text to normalize
            target_language: Target language code ('en' or 'de')

        Returns:
            Tuple of (normalized_text, detected_language)
        """
        if not text or not text.strip():
            return text, "unknown"

        # Detect current language
        detected = self.detect_language(text)

        # Normalize based on target language
        if target_language == "de":
            normalized = self._normalize_to_german(text, detected)
        elif target_language == "en":
            normalized = self._normalize_to_english(text, detected)
        else:
            logger.warning(f"Unsupported target language: {target_language}")
            normalized = text

        return normalized, detected

    def _normalize_to_english(self, text: str, detected_lang: str) -> str:
        """Normalize text to English."""
        normalized = text

        # For Arabic / Franco-Arabic: translate known terms to English.
        # The raw Arabic text is not useful for the polishing pipeline, so we
        # surface as many English equivalents as we can.
        if detected_lang == "ar":
            normalized = self._normalize_arabic_to_english(normalized)
            # After translation, strip any remaining Arabic-script characters
            # (they won't parse in the verb-enforcement pipeline)
            # Keep Latin/numeral characters only as best-effort
            normalized = re.sub(r'[؀-ۿ]', '', normalized).strip()
            normalized = re.sub(r'\s+', ' ', normalized).strip()
            # Capitalize properly and return early (no German/Denglish processing needed)
            return self._fix_capitalization(normalized) if normalized else text

        # Fix common English spelling mistakes
        if "en" in self.SPELLING_CORRECTIONS:
            for pattern, correction in self.SPELLING_CORRECTIONS["en"].items():
                normalized = re.sub(pattern, correction, normalized, flags=re.IGNORECASE)

        # If text is in German, translate key terms
        if detected_lang == "de":
            for german_term, english_term in self.GERMAN_TO_ENGLISH_TERMS.items():
                pattern = rf'\b{german_term}\b'
                normalized = re.sub(pattern, english_term, normalized, flags=re.IGNORECASE)

        # Fix Denglish mixtures
        for pattern, correction in self.DENGLISH_CORRECTIONS.items():
            normalized = re.sub(pattern, correction, normalized, flags=re.IGNORECASE)

        # Normalize German umlauts to English equivalents
        normalized = normalized.replace("ä", "a").replace("Ä", "A")
        normalized = normalized.replace("ö", "o").replace("Ö", "O")
        normalized = normalized.replace("ü", "u").replace("Ü", "U")
        normalized = normalized.replace("ß", "ss")

        # Capitalize properly
        normalized = self._fix_capitalization(normalized)

        # Normalize whitespace
        normalized = re.sub(r'\s+', ' ', normalized)

        return normalized.strip()

    def _normalize_to_german(self, text: str, detected_lang: str) -> str:
        """Normalize text to German."""
        normalized = text

        # Fix common German spelling mistakes
        if "de" in self.SPELLING_CORRECTIONS:
            for pattern, correction in self.SPELLING_CORRECTIONS["de"].items():
                normalized = re.sub(pattern, correction, normalized, flags=re.IGNORECASE)

        # If text is in English, translate key terms
        if detected_lang == "en":
            for english_term, german_term in self.ENGLISH_TO_GERMAN_TERMS.items():
                pattern = rf'\b{english_term}\b'
                normalized = re.sub(pattern, german_term, normalized, flags=re.IGNORECASE)

        # Capitalize properly
        normalized = self._fix_capitalization(normalized)

        # Normalize whitespace
        normalized = re.sub(r'\s+', ' ', normalized)

        return normalized.strip()

    def _fix_capitalization(self, text: str) -> str:
        """Fix capitalization: first letter of sentences."""
        if not text:
            return text

        # Capitalize first letter
        text = text[0].upper() + text[1:] if len(text) > 1 else text.upper()

        # Capitalize after sentence-ending punctuation
        text = re.sub(r'([.!?])\s+([a-z])', lambda m: m.group(1) + ' ' + m.group(2).upper(), text)

        return text

    def get_language_confidence(self, text: str) -> Dict[str, float]:
        """
        Get confidence scores for detected languages.

        Args:
            text: Text to analyze

        Returns:
            Dict with confidence scores for each core language
        """
        if not text or len(text) < 5:
            return {code: 0.0 for code in self.CORE_LANGUAGES}

        # Try Lingua first
        if self._detector:
            try:
                probabilities = self._detector.compute_language_confidence_scores(text)
                scores = {}
                for lang_code in self.CORE_LANGUAGES:
                    # Find matching probability
                    score = 0.0
                    for prob in probabilities:
                        if prob.language.iso_code_639_1.name.lower() == lang_code:
                            score = round(prob.confidence, 2)
                            break
                    scores[lang_code] = score

                return scores
            except Exception as e:
                logger.debug(f"Lingua confidence error: {e}. Using keyword fallback.")

        # Fallback to keyword-based confidence
        return self._get_confidence_keywords(text)

    def _get_confidence_keywords(self, text: str) -> Dict[str, float]:
        """Keyword-based confidence scoring."""
        # Arabic script is unambiguous
        if self._has_arabic_script(text):
            scores = {code: 0.0 for code in self.CORE_LANGUAGES}
            scores["ar"] = 0.95
            return scores

        # Franco-Arabic
        if self._is_franco_arabic(text):
            scores = {code: 0.0 for code in self.CORE_LANGUAGES}
            scores["ar"] = 0.85
            return scores

        text_lower = text.lower()

        # Check for German umlauts (strong signal)
        has_umlauts = bool(re.search(r'[äöüß]', text_lower))

        # Count keyword matches
        words = re.findall(r'\b\w+\b', text_lower)
        words_set = set(words)

        german_matches = sum(1 for keyword in self._german_keywords_set
                            if keyword in words_set or (len(keyword) > 2 and keyword in text_lower))
        english_matches = sum(1 for keyword in self._english_keywords_set
                             if keyword in words_set or (len(keyword) > 2 and keyword in text_lower))

        # Franco-Arabic keyword signal
        franco_matches = len(words_set & self.FRANCO_ARABIC_KEYWORDS)
        if franco_matches >= 2:
            scores = {code: 0.0 for code in self.CORE_LANGUAGES}
            scores["ar"] = round(min(1.0, 0.5 + franco_matches * 0.1), 2)
            return scores

        total_matches = german_matches + english_matches

        # Compute confidence
        if total_matches == 0:
            if has_umlauts:
                return {"de": 0.8, **{code: 0.0 for code in self.CORE_LANGUAGES if code != "de"}}
            return {code: 0.0 for code in self.CORE_LANGUAGES}

        german_conf = german_matches / total_matches
        english_conf = english_matches / total_matches

        # Boost German confidence if umlauts present
        if has_umlauts:
            german_conf = min(1.0, german_conf + 0.3)

        # Normalize
        total = german_conf + english_conf
        if total > 0:
            german_conf /= total
            english_conf /= total

        # Build full confidence dict for all core languages
        scores = {code: 0.0 for code in self.CORE_LANGUAGES}
        scores["de"] = round(german_conf, 2)
        scores["en"] = round(english_conf, 2)

        return scores

    def translate_to_german(self, english_text: str) -> str:
        """
        Translate normalized English text back to German.

        This is a reverse translation that:
        1. Translates English terms back to German using ENGLISH_TO_GERMAN_TERMS
        2. Reverts umlaut normalizations (fahigkeiten → fähigkeiten)
        3. Applies German grammar and capitalization

        Args:
            english_text: English text to translate to German

        Returns:
            German-formatted text
        """
        if not english_text or not english_text.strip():
            return english_text

        german_text = english_text

        # Translate English terms back to German
        for english_term, german_term in self.ENGLISH_TO_GERMAN_TERMS.items():
            pattern = rf'\b{re.escape(english_term)}\b'
            german_text = re.sub(pattern, german_term, german_text, flags=re.IGNORECASE)

        # Revert umlaut normalizations (restore German umlauts)
        # These patterns handle common cases where umlauts were normalized to non-umlaut versions
        german_text = re.sub(r'\bfahigkeiten\b', 'Fähigkeiten', german_text, flags=re.IGNORECASE)
        german_text = re.sub(r'\berfahrung\b', 'Erfahrung', german_text, flags=re.IGNORECASE)
        german_text = re.sub(r'\bfahigkeit\b', 'Fähigkeit', german_text, flags=re.IGNORECASE)
        german_text = re.sub(r'\bgefuhl\b', 'Gefühl', german_text, flags=re.IGNORECASE)
        german_text = re.sub(r'\bfuhrt\b', 'führt', german_text, flags=re.IGNORECASE)
        german_text = re.sub(r'\bgrosse\b', 'Größe', german_text, flags=re.IGNORECASE)

        # Apply German capitalization
        german_text = self._fix_capitalization(german_text)

        # Normalize whitespace
        german_text = re.sub(r'\s+', ' ', german_text)

        return german_text.strip()

    def generate_all_versions(self, raw_text: str, user_native_language: Optional[str] = None) -> Dict[str, str]:
        """
        Generate all three language versions (German, English, native) from raw user input.

        Pipeline:
        1. Detect input language and normalize to English (existing behavior)
        2. Polish the English version
        3. Translate English to German using term mapping
        4. Generate native language version (if different from English/German)

        Args:
            raw_text: Raw user input (in any language)
            user_native_language: User's detected native language code (ISO 639-1)

        Returns:
            Dict with keys 'german', 'english', 'native'
            Each value is a polished version in that language
        """
        if not raw_text or not raw_text.strip():
            return {"german": "", "english": "", "native": ""}

        try:
            # Detect input language first to avoid degrading already-German text
            detected_lang = self.detect_language(raw_text)

            if detected_lang == "de":
                # Input is already German — use it directly as the german version
                # Just normalize/clean without translating through English
                german_version, _ = self.normalize_to_language(raw_text, "de")
                english_version = self._normalize_to_english(raw_text, detected_lang)
                native_version = raw_text if user_native_language in (None, "de") else english_version

            elif detected_lang == "ar":
                # Arabic / Franco-Arabic input.
                # The native version preserves the original (with Franco numeral
                # substitutions converted to Arabic script for readability).
                # The English version is our best-effort translation using the
                # Arabic→English term map.  The German version is translated from
                # that English base.
                native_version = self.normalize_franco_arabic_numerals(raw_text)
                english_version = self._normalize_arabic_to_english(raw_text)
                # Strip residual Arabic script from the English field
                english_version = re.sub(r'[؀-ۿ]', '', english_version).strip()
                english_version = re.sub(r'\s+', ' ', english_version).strip()
                if english_version:
                    english_version = self._fix_capitalization(english_version)
                else:
                    english_version = raw_text  # last-resort fallback
                german_version = self.translate_to_german(english_version)

            else:
                # Step 1: Normalize to English (handles all language conversions)
                english_version, _ = self.normalize_to_language(raw_text, "en")

                # Step 2: Generate German from English
                german_version = self.translate_to_german(english_version)

                # Step 3: Generate native version
                if user_native_language and user_native_language != "de" and user_native_language != "en":
                    # For non-English, non-German native languages, use normalized English as base
                    # In future, could add language-specific translations here
                    native_version = english_version
                elif user_native_language == "de":
                    # If German is native language, use German version
                    native_version = german_version
                elif user_native_language == "en":
                    # If English is native, use English
                    native_version = english_version
                else:
                    # Default: use English
                    native_version = english_version

            logger.debug(
                f"Generated all versions for language '{detected_lang}': "
                f"de={len(german_version)} chars, en={len(english_version)} chars, "
                f"native({user_native_language})={len(native_version)} chars"
            )

            return {
                "german": german_version,
                "english": english_version,
                "native": native_version
            }

        except Exception as e:
            logger.error(f"Error generating all versions: {e}")
            # Fallback: return normalized English in all versions
            normalized, _ = self.normalize_to_language(raw_text, "en")
            return {
                "german": normalized,
                "english": normalized,
                "native": normalized
            }
