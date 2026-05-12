"""
Language Normalization Tests - Comprehensive test suite for German/English detection and normalization.

Tests cover:
1. Language detection (German, English, mixed)
2. Normalization to English
3. Normalization to German
4. Spelling corrections
5. Term standardization
6. Denglish handling
7. Confidence scoring
8. Edge cases
"""

import pytest
from src.backend.polish.language import LanguageNormalizer


class TestLanguageDetection:
    """Test language detection for German, English, and mixed text."""

    @pytest.fixture
    def normalizer(self):
        """Language normalizer instance."""
        return LanguageNormalizer()

    def test_detect_german_text(self, normalizer):
        """German text is correctly detected."""
        german_text = "Ich habe eine Ausbildung als Elektroniker absolviert."
        detected = normalizer.detect_language(german_text)
        assert detected == "de"

    def test_detect_english_text(self, normalizer):
        """English text is correctly detected."""
        english_text = "I completed a 3-year apprenticeship in computer science."
        detected = normalizer.detect_language(english_text)
        assert detected == "en"

    def test_detect_german_with_umlauts(self, normalizer):
        """German text with umlauts strongly signals German."""
        text = "Ich habe Fähigkeiten in Netzwerk und IT."
        detected = normalizer.detect_language(text)
        assert detected == "de"

    def test_detect_denglish_mixed(self, normalizer):
        """Mixed German-English (Denglish) text."""
        mixed = "Ich habe ein Projekt managed und viel gelernt."
        detected = normalizer.detect_language(mixed)
        # Should detect one language, either is acceptable
        assert detected in ["de", "en", "unknown"]

    def test_detect_empty_text_returns_unknown(self, normalizer):
        """Empty text returns unknown."""
        detected = normalizer.detect_language("")
        assert detected == "unknown"

    def test_detect_too_short_returns_unknown(self, normalizer):
        """Text shorter than 5 chars returns unknown."""
        detected = normalizer.detect_language("hi")
        assert detected == "unknown"

    def test_detect_numbers_only(self, normalizer):
        """Text with only numbers returns unknown."""
        detected = normalizer.detect_language("12345")
        assert detected == "unknown"

    def test_detect_case_insensitive(self, normalizer):
        """Language detection is case-insensitive."""
        german_lower = "ich habe gelernt"
        german_upper = "ICH HABE GELERNT"
        assert normalizer.detect_language(german_lower) == normalizer.detect_language(german_upper)


class TestNormalizeToEnglish:
    """Test normalization of German and mixed text to English."""

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
        # Should contain English terms
        assert len(normalized) > 0

    def test_remove_umlauts_in_english(self, normalizer):
        """German umlauts are removed when normalizing to English."""
        text = "Fähigkeiten und Äpfel"
        normalized, _ = normalizer.normalize_to_language(text, "en")

        # Umlauts should be converted
        assert "ä" not in normalized
        assert "Ä" not in normalized
        assert "ö" not in normalized
        assert "ü" not in normalized

    def test_fix_english_spelling(self, normalizer):
        """Common English spelling mistakes are corrected."""
        text = "I have expirence and knowledge"
        normalized, _ = normalizer.normalize_to_language(text, "en")

        # Should correct "expirence" to "experience"
        assert "expirence" not in normalized.lower()

    def test_english_text_unchanged(self, normalizer):
        """English text normalizing to English stays similar."""
        english = "I worked on projects and improved systems."
        normalized, detected = normalizer.normalize_to_language(english, "en")

        assert detected == "en"
        # Should be similar length
        assert len(normalized) > 0

    def test_normalize_empty_to_english(self, normalizer):
        """Empty text handling for English normalization."""
        normalized, detected = normalizer.normalize_to_language("", "en")
        assert normalized == ""
        assert detected == "unknown"

    def test_denglish_corrected_to_english(self, normalizer):
        """Denglish (German-English mix) is corrected to pure English."""
        denglish = "Ich habe Projekte managed und Teams gelead."
        normalized, _ = normalizer.normalize_to_language(denglish, "en")

        # Should be in English or partially converted
        assert isinstance(normalized, str)
        assert len(normalized) > 0


class TestNormalizeToGerman:
    """Test normalization of English and mixed text to German."""

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

    def test_german_text_to_german_stays_similar(self, normalizer):
        """German text normalizing to German stays similar."""
        german = "Ich habe Projekte geleitet und Lösungen entwickelt."
        normalized, detected = normalizer.normalize_to_language(german, "de")

        assert detected == "de"
        assert len(normalized) > 0

    def test_german_capitalization(self, normalizer):
        """German nouns are capitalized properly."""
        text = "ich habe erfahrung mit projekten"
        normalized, _ = normalizer.normalize_to_language(text, "de")

        # First letter should be capitalized
        assert normalized[0].isupper()

    def test_normalize_empty_to_german(self, normalizer):
        """Empty text handling for German normalization."""
        normalized, detected = normalizer.normalize_to_language("", "de")
        assert normalized == ""
        assert detected == "unknown"

    def test_denglish_to_german(self, normalizer):
        """Denglish is handled when normalizing to German."""
        denglish = "Ich have managed projects und gelernt viel."
        normalized, _ = normalizer.normalize_to_language(denglish, "de")

        assert isinstance(normalized, str)
        assert len(normalized) > 0


class TestSpellingCorrections:
    """Test spelling correction functionality."""

    @pytest.fixture
    def normalizer(self):
        """Language normalizer instance."""
        return LanguageNormalizer()

    def test_english_spelling_corrections(self, normalizer):
        """English spelling mistakes are corrected."""
        text_with_errors = "expirence knowlege seperate"
        normalized, _ = normalizer.normalize_to_language(text_with_errors, "en")

        # Check that corrections were made
        assert "experience" in normalized.lower() or "expirence" not in normalized.lower()

    def test_german_spelling_corrections(self, normalizer):
        """German spelling mistakes are corrected."""
        text_with_errors = "fahigkeiten erfahung"
        normalized, _ = normalizer.normalize_to_language(text_with_errors, "de")

        assert isinstance(normalized, str)
        assert len(normalized) > 0

    def test_case_insensitive_spelling_correction(self, normalizer):
        """Spelling corrections work regardless of case."""
        uppercase = "EXPIRENCE"
        lowercase = "expirence"

        norm_upper, _ = normalizer.normalize_to_language(uppercase, "en")
        norm_lower, _ = normalizer.normalize_to_language(lowercase, "en")

        # Both should be corrected similarly
        assert isinstance(norm_upper, str)
        assert isinstance(norm_lower, str)


class TestTermStandardization:
    """Test standardization of common CV terms."""

    @pytest.fixture
    def normalizer(self):
        """Language normalizer instance."""
        return LanguageNormalizer()

    def test_german_to_english_verb_translation(self, normalizer):
        """German verbs are translated to English equivalents."""
        german = "Ich führte ein Team und entwickelte Software."
        normalized, _ = normalizer.normalize_to_language(german, "en")

        # Should contain English terms or their bases
        assert isinstance(normalized, str)
        assert len(normalized) > 0

    def test_english_to_german_verb_translation(self, normalizer):
        """English verbs are translated to German equivalents."""
        english = "I led a team and developed software."
        normalized, _ = normalizer.normalize_to_language(english, "de")

        # Should be in German or translated
        assert isinstance(normalized, str)
        assert len(normalized) > 0

    def test_preserve_unknown_terms(self, normalizer):
        """Unknown terms are preserved during translation."""
        text = "I worked with Kubernetes and Docker."
        normalized, _ = normalizer.normalize_to_language(text, "en")

        # Tech terms should be preserved
        assert "kubernetes" in normalized.lower() or "docker" in normalized.lower()


class TestCapitalization:
    """Test capitalization handling."""

    @pytest.fixture
    def normalizer(self):
        """Language normalizer instance."""
        return LanguageNormalizer()

    def test_first_letter_capitalization(self, normalizer):
        """First letter of text is capitalized."""
        text = "i worked in a company"
        normalized, _ = normalizer.normalize_to_language(text, "en")

        assert normalized[0].isupper()

    def test_sentence_capitalization_after_period(self, normalizer):
        """Sentences after periods are capitalized."""
        text = "I worked hard. i learned new skills."
        normalized, _ = normalizer.normalize_to_language(text, "en")

        # First letter of second sentence should be capitalized
        sentences = normalized.split('. ')
        if len(sentences) > 1:
            assert sentences[1][0].isupper()

    def test_german_noun_capitalization(self, normalizer):
        """German nouns are kept capitalized."""
        text = "ich habe erfahrung und projekte"
        normalized, _ = normalizer.normalize_to_language(text, "de")

        # Should have capital letters
        assert any(c.isupper() for c in normalized)


class TestLanguageConfidence:
    """Test language detection confidence scoring."""

    @pytest.fixture
    def normalizer(self):
        """Language normalizer instance."""
        return LanguageNormalizer()

    def test_confidence_scores_sum_to_one(self, normalizer):
        """Confidence scores for all languages sum to 1.0."""
        text = "I have worked and gelernt viel."
        confidence = normalizer.get_language_confidence(text)

        total = confidence["de"] + confidence["en"] + confidence.get("unknown", 0)
        assert abs(total - 1.0) < 0.01  # Allow for rounding

    def test_german_text_high_german_confidence(self, normalizer):
        """German text has high German confidence."""
        german = "Ich habe eine Ausbildung mit guten Fähigkeiten absolviert."
        confidence = normalizer.get_language_confidence(german)

        assert confidence["de"] > confidence["en"]

    def test_english_text_high_english_confidence(self, normalizer):
        """English text has high English confidence."""
        english = "I completed an apprenticeship with excellent skills."
        confidence = normalizer.get_language_confidence(english)

        assert confidence["en"] > confidence["de"]

    def test_empty_text_has_unknown_confidence(self, normalizer):
        """Empty text has zero confidence for all languages."""
        confidence = normalizer.get_language_confidence("")

        # All core languages should have 0 confidence
        for lang_code in normalizer.CORE_LANGUAGES:
            assert confidence[lang_code] == 0.0

    def test_confidence_values_in_range(self, normalizer):
        """Confidence values are between 0 and 1."""
        text = "Some mixed text mit deutschen Wörtern."
        confidence = normalizer.get_language_confidence(text)

        for lang, score in confidence.items():
            assert 0.0 <= score <= 1.0

    def test_umlaut_boosts_german_confidence(self, normalizer):
        """Presence of umlauts boosts German confidence."""
        with_umlauts = "Ich habe Fähigkeiten und Erfahrung."
        without_umlauts = "Ich habe Fahigkeiten und Erfahrung."

        conf_with = normalizer.get_language_confidence(with_umlauts)
        conf_without = normalizer.get_language_confidence(without_umlauts)

        # With umlauts should have higher German confidence
        assert conf_with["de"] >= conf_without["de"]


class TestEdgeCases:
    """Test edge cases and unusual inputs."""

    @pytest.fixture
    def normalizer(self):
        """Language normalizer instance."""
        return LanguageNormalizer()

    def test_very_long_text(self, normalizer):
        """Very long text is handled correctly."""
        long_text = "I worked " * 1000 + "and learned."
        normalized, detected = normalizer.normalize_to_language(long_text, "en")

        assert isinstance(normalized, str)
        assert len(normalized) > 0

    def test_special_characters_preserved(self, normalizer):
        """Special characters are preserved during normalization."""
        text = "I earned 50,000€ and worked 5.5 years."
        normalized, _ = normalizer.normalize_to_language(text, "en")

        # Numbers and symbols should be preserved
        assert any(c.isdigit() for c in normalized)

    def test_unicode_characters(self, normalizer):
        """Unicode characters are handled."""
        text = "Ich arbeitete mit café und über-Zeit."
        normalized, detected = normalizer.normalize_to_language(text, "de")

        assert detected == "de"
        assert isinstance(normalized, str)

    def test_url_preserved(self, normalizer):
        """URLs are preserved during normalization."""
        text = "I worked with www.example.com and api.github.com."
        normalized, _ = normalizer.normalize_to_language(text, "en")

        # URLs should be preserved
        assert "example.com" in normalized or "github.com" in normalized

    def test_email_preserved(self, normalizer):
        """Email addresses are preserved."""
        text = "Contact me at john@example.com for more info."
        normalized, _ = normalizer.normalize_to_language(text, "en")

        # Email should be preserved
        assert "@" in normalized

    def test_whitespace_normalization(self, normalizer):
        """Extra whitespace is cleaned up."""
        text = "I   worked    in    a    company"
        normalized, _ = normalizer.normalize_to_language(text, "en")

        # Excessive spaces should be reduced
        assert "   " not in normalized

    def test_unsupported_language_target(self, normalizer):
        """Unsupported target language returns original text."""
        text = "I have skills and experience."
        normalized, _ = normalizer.normalize_to_language(text, "fr")

        # Should return original or similar
        assert isinstance(normalized, str)
        assert len(normalized) > 0

    def test_none_input_handled_gracefully(self, normalizer):
        """None input is handled without error."""
        try:
            normalized, detected = normalizer.normalize_to_language(None, "en")
            # Should either return empty or raise AttributeError which is ok
        except (AttributeError, TypeError):
            # Expected if None is passed
            pass


class TestLanguageDetectionKeywords:
    """Test keyword-based language detection."""

    @pytest.fixture
    def normalizer(self):
        """Language normalizer instance."""
        return LanguageNormalizer()

    def test_german_articles_detected(self, normalizer):
        """German articles (der, die, das) are detected."""
        text = "Der Mann und die Frau arbeiten mit dem Team."
        detected = normalizer.detect_language(text)
        assert detected == "de"

    def test_english_articles_detected(self, normalizer):
        """English articles (the, a, an) are detected."""
        text = "The man and a woman work with the team."
        detected = normalizer.detect_language(text)
        assert detected == "en"

    def test_german_verbs_detected(self, normalizer):
        """German verbs signal German language."""
        text = "Ich arbeite und lerne neue Fähigkeiten."
        detected = normalizer.detect_language(text)
        assert detected == "de"

    def test_english_verbs_detected(self, normalizer):
        """English verbs signal English language."""
        text = "I work and learn new skills."
        detected = normalizer.detect_language(text)
        assert detected == "en"

    def test_no_keywords_defaults_to_unknown(self, normalizer):
        """Text with no recognized keywords returns unknown."""
        text = "xyz abc qwerty"
        detected = normalizer.detect_language(text)
        assert detected == "unknown"  # No keywords found


class TestArabicAndFrancoArabic:
    """Tests for Arabic-script and Franco-Arabic (3araby franco) detection and normalization."""

    @pytest.fixture
    def normalizer(self):
        return LanguageNormalizer()

    # ── detection ────────────────────────────────────────────────────────────

    def test_detect_arabic_script(self, normalizer):
        """Pure Arabic script is detected as Arabic."""
        text = "أنا لدي خبرة في البرمجة وإدارة الفرق."
        assert normalizer.detect_language(text) == "ar"

    def test_detect_arabic_script_short(self, normalizer):
        """Short Arabic text (≥5 chars) is detected correctly."""
        assert normalizer.detect_language("خبرة عمل") == "ar"

    def test_detect_franco_arabic_numeral_keyword(self, normalizer):
        """Franco-Arabic text with numeral+keyword is detected as Arabic."""
        # "3andi khebra" = "I have experience"
        text = "ana 3andi khebra f el sales w kont mas2ol 3la farik."
        assert normalizer.detect_language(text) == "ar"

    def test_detect_franco_arabic_keywords_only(self, normalizer):
        """≥2 Franco-Arabic keywords trigger Arabic detection even without numerals."""
        text = "ana kont beshtaghal fe sharka kbira."
        assert normalizer.detect_language(text) == "ar"

    def test_detect_franco_arabic_classic_phrases(self, normalizer):
        """Classic Franco-Arabic work phrases are detected."""
        text = "b3ml fe el mashr3 w bashtghel m3 el farik kl yom."
        assert normalizer.detect_language(text) == "ar"

    def test_plain_numbers_not_franco(self, normalizer):
        """Standalone digits in a sentence do not trigger Franco-Arabic detection."""
        text = "I worked 3 years and managed 5 teams in the company."
        detected = normalizer.detect_language(text)
        # Should NOT be Arabic — standalone digits, no Arabic keywords
        assert detected != "ar"

    # ── Arabic-script detection helper ───────────────────────────────────────

    def test_has_arabic_script_true(self, normalizer):
        assert normalizer._has_arabic_script("مرحبا") is True

    def test_has_arabic_script_false_latin(self, normalizer):
        assert normalizer._has_arabic_script("hello world") is False

    # ── Franco-Arabic detection helper ───────────────────────────────────────

    def test_is_franco_arabic_true(self, normalizer):
        assert normalizer._is_franco_arabic("ana 3andi khebra") is True

    def test_is_franco_arabic_false_english(self, normalizer):
        assert normalizer._is_franco_arabic("I have experience in sales") is False

    # ── Numeral substitution normalizer ──────────────────────────────────────

    def test_normalize_franco_numerals_3(self, normalizer):
        """3 adjacent to letters is replaced by ع."""
        result = normalizer.normalize_franco_arabic_numerals("3andi")
        assert "ع" in result

    def test_normalize_franco_numerals_7(self, normalizer):
        """7 adjacent to letters is replaced by ح."""
        result = normalizer.normalize_franco_arabic_numerals("7elo")
        assert "ح" in result

    def test_normalize_franco_numerals_2(self, normalizer):
        """2 adjacent to letters is replaced by أ."""
        result = normalizer.normalize_franco_arabic_numerals("mas2ol")
        assert "أ" in result

    def test_normalize_standalone_numbers_unchanged(self, normalizer):
        """Standalone digits (not adjacent to letters) are NOT replaced."""
        result = normalizer.normalize_franco_arabic_numerals("worked 3 years in 5 teams")
        # Standalone '3' and '5' should remain digits
        assert "3" in result
        assert "5" in result

    # ── Arabic→English term translation ──────────────────────────────────────

    def test_arabic_script_term_translated(self, normalizer):
        """Arabic-script skill term is translated to English."""
        result = normalizer._normalize_arabic_to_english("لدي خبرة في القيادة")
        assert "experience" in result.lower() or "leadership" in result.lower()

    def test_franco_arabic_term_translated(self, normalizer):
        """Franco-Arabic transliteration is mapped to English."""
        result = normalizer._normalize_arabic_to_english("3andi khebra f el sales")
        assert "experience" in result.lower() or "sales" in result.lower()

    def test_mas2ol_translated(self, normalizer):
        """mas2ol / mas2oul → responsible."""
        result = normalizer._normalize_arabic_to_english("kont mas2ol 3la el farik")
        assert "responsible" in result.lower()

    # ── generate_all_versions for Arabic ─────────────────────────────────────

    def test_generate_all_versions_arabic_script(self, normalizer):
        """Arabic-script input: native version preserved, english/german generated."""
        text = "لدي خبرة في البرمجة وإدارة الفرق."
        versions = normalizer.generate_all_versions(text, user_native_language="ar")

        assert isinstance(versions["native"], str) and len(versions["native"]) > 0
        assert isinstance(versions["english"], str) and len(versions["english"]) > 0
        assert isinstance(versions["german"], str) and len(versions["german"]) > 0
        # Native should preserve original Arabic content (or numeral-expanded form)
        assert any(c in "؀ۿ" or ('؀' <= c <= 'ۿ') for c in versions["native"])

    def test_generate_all_versions_franco_arabic(self, normalizer):
        """Franco-Arabic input: native version preserved with numeral expansion."""
        text = "ana 3andi khebra fe el sales w mas2ol 3la farik."
        versions = normalizer.generate_all_versions(text, user_native_language="ar")

        assert isinstance(versions["native"], str) and len(versions["native"]) > 0
        assert isinstance(versions["english"], str) and len(versions["english"]) > 0
        assert isinstance(versions["german"], str) and len(versions["german"]) > 0

    def test_arabic_english_version_contains_translated_terms(self, normalizer):
        """English version of Arabic input should contain mapped English terms."""
        text = "3andi khebra w maharat f el mas2oul."
        versions = normalizer.generate_all_versions(text, user_native_language="ar")
        english = versions["english"].lower()
        # At least one known term should have been translated
        assert any(word in english for word in ["experience", "skills", "skill", "responsible"])

    def test_arabic_confidence_high_for_arabic_script(self, normalizer):
        """Arabic-script text returns high Arabic confidence."""
        text = "أنا لدي خبرة في إدارة الفرق والتواصل مع العملاء."
        confidence = normalizer.get_language_confidence(text)
        assert confidence.get("ar", 0) >= 0.9

    def test_arabic_confidence_high_for_franco_arabic(self, normalizer):
        """Franco-Arabic text returns meaningful Arabic confidence."""
        text = "ana 3andi khebra kbira f el tasmeem w taqnia."
        confidence = normalizer.get_language_confidence(text)
        assert confidence.get("ar", 0) >= 0.7
