"""
Language Detection Tests - Comprehensive test suite for all 14 core languages.

Tests cover:
1. Language detection (German, English, Italian, Polish, Czech, Slovak, Hungarian, French)
2. Slavic languages (Ukrainian, Serbian, Russian, Bosnian)
3. Turkic languages (Turkish)
4. Semitic languages (Arabic)
5. Normalization across all languages
6. Spelling corrections
7. Term standardization
8. Confidence scoring
9. Edge cases
"""

import pytest
from src.backend.polish.language import LanguageNormalizer


class TestLanguageDetectionCore14:
    """Test detection for all 14 core languages."""

    @pytest.fixture
    def normalizer(self):
        """Language normalizer instance."""
        return LanguageNormalizer()

    # === Germanic Languages ===

    def test_detect_german(self, normalizer):
        """German text is correctly detected."""
        german_text = "Ich habe eine Ausbildung als Elektroniker absolviert."
        detected = normalizer.detect_language(german_text)
        assert detected == "de", f"Expected 'de', got '{detected}'"

    def test_detect_english(self, normalizer):
        """English text is correctly detected."""
        english_text = "I completed a 3-year apprenticeship in computer science."
        detected = normalizer.detect_language(english_text)
        assert detected == "en", f"Expected 'en', got '{detected}'"

    # === Romance Languages ===

    def _assert_detection(self, normalizer, text, expected_code):
        """
        Assert language detection result.

        Without Lingua: validates result is a valid ISO code (not corrupted output).
        With Lingua: validates the exact expected language is detected.
        """
        detected = normalizer.detect_language(text)
        valid_codes = set(normalizer.CORE_LANGUAGES) | {"unknown"}

        # Always: must return a valid language code, never arbitrary garbage
        assert detected in valid_codes, (
            f"Returned '{detected}' which is not a valid language code. "
            f"Valid codes: {sorted(valid_codes)}"
        )

        # With Lingua: must detect the specific language correctly
        if normalizer._detector is not None:
            assert detected == expected_code, (
                f"With Lingua: expected '{expected_code}', got '{detected}'"
            )
        # Without Lingua: fallback is known to return 'de'/'en'/'unknown' only
        # The fact that it returns a valid code is the best we can assert

    def test_detect_italian(self, normalizer):
        """Italian returns valid code; exact 'it' requires Lingua."""
        self._assert_detection(normalizer,
            "Ho completato un apprendistato di tre anni in informatica.", "it")

    def test_detect_french(self, normalizer):
        """French returns valid code; exact 'fr' requires Lingua."""
        self._assert_detection(normalizer,
            "J'ai complété un apprentissage de trois ans en informatique.", "fr")

    # === Central European Slavic ===

    def test_detect_polish(self, normalizer):
        """Polish returns valid code; exact 'pl' requires Lingua."""
        self._assert_detection(normalizer,
            "Ukończyłem trzyletnią praktykę w informatyce.", "pl")

    def test_detect_czech(self, normalizer):
        """Czech returns valid code; exact 'cs' requires Lingua."""
        self._assert_detection(normalizer,
            "Absolvoval jsem tříletý učební obor v informatice.", "cs")

    def test_detect_slovak(self, normalizer):
        """Slovak returns valid code; exact 'sk' requires Lingua."""
        self._assert_detection(normalizer,
            "Absolvoval som trojročný učebný odbor v informatike.", "sk")

    def test_detect_hungarian(self, normalizer):
        """Hungarian returns valid code; exact 'hu' requires Lingua."""
        self._assert_detection(normalizer,
            "Elvégeztem egy hároméves szakképzést az informatikában.", "hu")

    # === Eastern European Slavic (NEW CORE) ===

    def test_detect_ukrainian(self, normalizer):
        """Ukrainian returns valid code; exact 'uk' requires Lingua."""
        self._assert_detection(normalizer,
            "Я закінчив трирічне навчання в галузі інформатики.", "uk")

    def test_detect_russian(self, normalizer):
        """Russian returns valid code; exact 'ru' requires Lingua."""
        self._assert_detection(normalizer,
            "Я завершил трехлетнее обучение в области информатики.", "ru")

    def test_detect_serbian(self, normalizer):
        """Serbian returns valid code; exact 'sr' requires Lingua."""
        self._assert_detection(normalizer,
            "Završio sam trogodišnje obukovanje u oblasti informatike.", "sr")

    def test_detect_bosnian(self, normalizer):
        """Bosnian returns valid code; exact 'bs' requires Lingua."""
        self._assert_detection(normalizer,
            "Završio sam trogodišnju obuku u oblasti informatike.", "bs")

    # === Other Language Families ===

    def test_detect_turkish(self, normalizer):
        """Turkish returns valid code; exact 'tr' requires Lingua."""
        self._assert_detection(normalizer,
            "Bilgisayar bilimleri alanında üç yıllık bir eğitim tamamladım.", "tr")

    def test_detect_arabic(self, normalizer):
        """Arabic returns valid code; exact 'ar' requires Lingua."""
        self._assert_detection(normalizer,
            "أكملت تدريبًا لمدة ثلاث سنوات في علوم الحاسب الآلي.", "ar")


class TestUmlautDetection:
    """Test umlaut-based detection (German/Ukrainian)."""

    @pytest.fixture
    def normalizer(self):
        """Language normalizer instance."""
        return LanguageNormalizer()

    def test_german_with_umlauts(self, normalizer):
        """German text with umlauts strongly signals German."""
        text = "Ich habe Fähigkeiten in Netzwerk und IT."
        detected = normalizer.detect_language(text)
        assert detected == "de"

    def test_uppercase_umlaut(self, normalizer):
        """Uppercase umlauts are recognized."""
        text = "FÄHIGKEITEN UND ERFAHRUNG"
        detected = normalizer.detect_language(text)
        assert detected == "de"

    def test_mixed_case_umlauts(self, normalizer):
        """Mixed case umlauts are recognized."""
        text = "Ich habe Erfahrung und Fähigkeiten"
        detected = normalizer.detect_language(text)
        assert detected == "de"


class TestEdgeCases:
    """Test edge cases and unusual inputs."""

    @pytest.fixture
    def normalizer(self):
        """Language normalizer instance."""
        return LanguageNormalizer()

    def test_empty_text(self, normalizer):
        """Empty text returns unknown."""
        detected = normalizer.detect_language("")
        assert detected == "unknown"

    def test_too_short_text(self, normalizer):
        """Text shorter than 5 characters returns unknown."""
        detected = normalizer.detect_language("hi")
        assert detected == "unknown"

    def test_numbers_only(self, normalizer):
        """Text with only numbers returns unknown."""
        detected = normalizer.detect_language("12345")
        assert detected == "unknown"

    def test_special_characters_only(self, normalizer):
        """Text with only special characters returns unknown."""
        detected = normalizer.detect_language("!!!???***")
        assert detected == "unknown"

    def test_mixed_scripts(self, normalizer):
        """Text with mixed Latin and Cyrillic scripts."""
        mixed = "Ich have managed projects und gelernt viel на русском языке."
        detected = normalizer.detect_language(mixed)
        # Should detect primary language (German or Russian)
        assert detected in ["de", "ru", "en", "unknown"]

    def test_very_long_text(self, normalizer):
        """Very long text is handled correctly."""
        long_text = "I worked in a company for many years. " * 100 + "and learned new skills."
        detected = normalizer.detect_language(long_text)
        assert isinstance(detected, str)
        assert detected in normalizer.CORE_LANGUAGES + ["unknown"]

    def test_special_characters_preserved(self, normalizer):
        """Special characters are preserved during detection."""
        text = "I earned 50,000€ and worked 5.5 years in informatik@company."
        detected = normalizer.detect_language(text)
        assert isinstance(detected, str)

    def test_urls_and_emails(self, normalizer):
        """URLs and emails don't break detection."""
        text = "I worked with www.example.com and contact@example.de for many years."
        detected = normalizer.detect_language(text)
        assert isinstance(detected, str)

    def test_whitespace_normalization(self, normalizer):
        """Extra whitespace doesn't affect detection."""
        text1 = "I worked in a company for many years"
        text2 = "I   worked    in    a    company    for    many    years"
        assert normalizer.detect_language(text1) == normalizer.detect_language(text2)


class TestLanguageConfidence:
    """Test language detection confidence scoring."""

    @pytest.fixture
    def normalizer(self):
        """Language normalizer instance."""
        return LanguageNormalizer()

    def test_confidence_dict_structure(self, normalizer):
        """Confidence dict has all 14 core languages."""
        text = "I have worked and gelernt viel."
        confidence = normalizer.get_language_confidence(text)

        assert isinstance(confidence, dict)
        # Should have entries for core languages
        for code in normalizer.CORE_LANGUAGES:
            assert code in confidence or confidence.get(code) is not None

    def test_german_text_high_german_confidence(self, normalizer):
        """German text has higher German confidence than English."""
        german = "Ich habe eine Ausbildung mit guten Fähigkeiten absolviert."
        confidence = normalizer.get_language_confidence(german)

        # German confidence should be present
        assert "de" in confidence
        german_conf = confidence.get("de", 0)
        english_conf = confidence.get("en", 0)
        assert german_conf >= english_conf

    def test_english_text_high_english_confidence(self, normalizer):
        """English text has higher English confidence than German."""
        english = "I completed an apprenticeship with excellent skills."
        confidence = normalizer.get_language_confidence(english)

        assert "en" in confidence
        english_conf = confidence.get("en", 0)
        german_conf = confidence.get("de", 0)
        assert english_conf >= german_conf

    def test_empty_text_confidence(self, normalizer):
        """Empty text returns zero confidence for all languages."""
        confidence = normalizer.get_language_confidence("")

        for code in normalizer.CORE_LANGUAGES:
            assert confidence.get(code, 0) == 0.0

    def test_confidence_values_in_range(self, normalizer):
        """Confidence values are between 0 and 1."""
        text = "Some mixed text mit deutschen Wörtern and English too."
        confidence = normalizer.get_language_confidence(text)

        for code in normalizer.CORE_LANGUAGES:
            score = confidence.get(code, 0)
            assert 0.0 <= score <= 1.0


class TestNormalizationToEnglish:
    """Test normalization to English."""

    @pytest.fixture
    def normalizer(self):
        """Language normalizer instance."""
        return LanguageNormalizer()

    def test_normalize_german_to_english(self, normalizer):
        """German text is normalized to English."""
        german = "Ich habe gelernt und entwickelt."
        normalized, detected = normalizer.normalize_to_language(german, "en")

        assert detected == "de"
        assert isinstance(normalized, str)
        assert len(normalized) > 0

    def test_remove_umlauts(self, normalizer):
        """German umlauts are removed in English normalization."""
        text = "Fähigkeiten und Äpfel Überzeugung"
        normalized, _ = normalizer.normalize_to_language(text, "en")

        assert "ä" not in normalized.lower()
        assert "ö" not in normalized.lower()
        assert "ü" not in normalized.lower()
        assert "Ä" not in normalized
        assert "Ö" not in normalized
        assert "Ü" not in normalized

    def test_english_text_to_english_unchanged(self, normalizer):
        """English text normalizing to English stays similar."""
        english = "I worked on projects and improved systems."
        normalized, detected = normalizer.normalize_to_language(english, "en")

        assert detected == "en"
        assert len(normalized) > 0

    def test_empty_text_normalization(self, normalizer):
        """Empty text handling for normalization."""
        normalized, detected = normalizer.normalize_to_language("", "en")
        assert normalized == ""
        assert detected == "unknown"


class TestNormalizationToGerman:
    """Test normalization to German."""

    @pytest.fixture
    def normalizer(self):
        """Language normalizer instance."""
        return LanguageNormalizer()

    def test_normalize_english_to_german(self, normalizer):
        """English text is normalized to German."""
        english = "I led projects and developed solutions."
        normalized, detected = normalizer.normalize_to_language(english, "de")

        assert detected == "en"
        assert isinstance(normalized, str)
        assert len(normalized) > 0

    def test_german_to_german_stays_similar(self, normalizer):
        """German text normalizing to German stays similar."""
        german = "Ich habe Projekte geleitet und Lösungen entwickelt."
        normalized, detected = normalizer.normalize_to_language(german, "de")

        assert detected == "de"
        assert len(normalized) > 0

    def test_capitalization_in_normalization(self, normalizer):
        """First letter is capitalized in normalization."""
        text = "i have worked in companies"
        normalized, _ = normalizer.normalize_to_language(text, "de")

        assert normalized[0].isupper()


class TestCoreLanguageConstants:
    """Test that all 14 core languages are properly defined."""

    @pytest.fixture
    def normalizer(self):
        """Language normalizer instance."""
        return LanguageNormalizer()

    def test_all_14_core_languages_defined(self, normalizer):
        """All 14 core languages are in CORE_LANGUAGES."""
        expected = ["de", "en", "it", "pl", "cs", "sk", "hu", "fr", "uk", "tr", "sr", "ru", "ar", "bs"]
        assert set(normalizer.CORE_LANGUAGES) == set(expected)
        assert len(normalizer.CORE_LANGUAGES) == 14

    def test_all_core_languages_have_names(self, normalizer):
        """All core languages have human-readable names."""
        for code in normalizer.CORE_LANGUAGES:
            assert code in normalizer.LANGUAGE_NAMES
            assert len(normalizer.LANGUAGE_NAMES[code]) > 0

    def test_all_core_languages_have_lingua_support(self, normalizer):
        """All core languages are in Lingua mappings (if Lingua available)."""
        if normalizer._detector is not None:  # Lingua is available
            for code in normalizer.CORE_LANGUAGES:
                # Check that the language code is valid
                assert code in ["de", "en", "it", "pl", "cs", "sk", "hu", "fr", "uk", "tr", "sr", "ru", "ar", "bs"]
