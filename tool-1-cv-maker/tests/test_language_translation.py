"""
Tests for language translation capability (Days 9-10 Phase 9.1).

Tests the new translation methods:
- LanguageNormalizer.translate_to_german()
- LanguageNormalizer.generate_all_versions()

These enable generating German and native language versions from normalized English.
"""

import pytest
from src.backend.polish.language import LanguageNormalizer


class TestTranslateToGerman:
    """Test English to German translation."""

    @pytest.fixture
    def normalizer(self):
        """Provide language normalizer instance."""
        return LanguageNormalizer()

    def test_translate_simple_verbs_to_german(self, normalizer):
        """Test translation of simple English action verbs to German."""
        # Test single verb translation
        english = "I led a team of five people."
        result = normalizer.translate_to_german(english)
        assert "leitete" in result.lower()

    def test_translate_multiple_verbs(self, normalizer):
        """Test translation of multiple verbs."""
        english = "I developed and managed software projects."
        result = normalizer.translate_to_german(english)
        assert "entwickelte" in result.lower()
        assert "verwaltete" in result.lower()

    def test_translate_preserves_non_verb_terms(self, normalizer):
        """Test that non-verb terms are preserved."""
        english = "I worked with Python and SQL databases."
        result = normalizer.translate_to_german(english)
        assert "Python" in result
        assert "SQL" in result

    def test_translate_empty_string(self, normalizer):
        """Test translation of empty string."""
        result = normalizer.translate_to_german("")
        assert result == ""

    def test_translate_whitespace_only(self, normalizer):
        """Test translation of whitespace-only string."""
        result = normalizer.translate_to_german("   ")
        assert result.strip() == ""

    def test_translate_capitalizes_first_letter(self, normalizer):
        """Test that translated German is properly capitalized."""
        english = "managed a large department"
        result = normalizer.translate_to_german(english)
        assert result[0].isupper(), "First letter should be capitalized"

    def test_translate_complex_experience(self, normalizer):
        """Test translation of realistic work experience."""
        english = "I led a team of five engineers, developed new features, and improved system performance."
        result = normalizer.translate_to_german(english)
        assert "leitete" in result.lower()
        assert "entwickelte" in result.lower()
        assert "verbesserte" in result.lower()

    def test_translate_case_insensitive(self, normalizer):
        """Test that translation works with different cases."""
        # All caps verb
        english = "I LED a team."
        result = normalizer.translate_to_german(english)
        assert "leitete" in result.lower() or "LEITETE" in result

        # Mixed case
        english = "I LeD a team."
        result = normalizer.translate_to_german(english)
        assert any(term.lower() == "leitete" for term in result.split())


class TestGenerateAllVersions:
    """Test generation of all three language versions."""

    @pytest.fixture
    def normalizer(self):
        """Provide language normalizer instance."""
        return LanguageNormalizer()

    def test_generate_versions_english_input(self, normalizer):
        """Test generating versions from English input."""
        english_input = "I worked with Python and Excel to analyze data."
        result = normalizer.generate_all_versions(english_input, user_native_language="en")

        assert "german" in result
        assert "english" in result
        assert "native" in result

        assert len(result["english"]) > 0
        assert len(result["german"]) > 0
        assert len(result["native"]) > 0

    def test_generate_versions_german_native(self, normalizer):
        """Test that German version is used when German is native language."""
        english_input = "I managed a large team and improved efficiency."
        result = normalizer.generate_all_versions(english_input, user_native_language="de")

        # German and native should be the same
        assert result["german"] == result["native"]
        # German should contain translated verbs
        assert "verwaltete" in result["german"].lower()

    def test_generate_versions_english_native(self, normalizer):
        """Test that English version is used when English is native language."""
        english_input = "I developed software systems."
        result = normalizer.generate_all_versions(english_input, user_native_language="en")

        # English and native should be the same
        assert result["english"] == result["native"]

    def test_generate_versions_other_native_language(self, normalizer):
        """Test that English is used for non-English, non-German native languages."""
        english_input = "I led the technical team for five years."
        result = normalizer.generate_all_versions(english_input, user_native_language="sr")  # Serbian

        # Native version should default to English for non-supported languages
        assert result["native"] == result["english"]

    def test_generate_versions_empty_input(self, normalizer):
        """Test that empty input returns empty versions."""
        result = normalizer.generate_all_versions("", user_native_language="en")

        assert result["german"] == ""
        assert result["english"] == ""
        assert result["native"] == ""

    def test_generate_versions_all_three_populated(self, normalizer):
        """Test that all three versions are generated and non-empty."""
        input_text = "I worked with Java, developed web applications, and trained new team members."
        result = normalizer.generate_all_versions(input_text, user_native_language="de")

        # All versions should be populated
        assert bool(result["german"].strip()), "German version should not be empty"
        assert bool(result["english"].strip()), "English version should not be empty"
        assert bool(result["native"].strip()), "Native version should not be empty"

    def test_generate_versions_german_contains_verbs(self, normalizer):
        """Test that German version contains appropriate German verbs."""
        input_text = "I managed several projects and improved team productivity."
        result = normalizer.generate_all_versions(input_text, user_native_language="de")

        german_lower = result["german"].lower()
        # Should contain German verbs (or English if fallback)
        assert "verwaltete" in german_lower or "managed" in german_lower
        assert "verbesserte" in german_lower or "improved" in german_lower

    def test_generate_versions_multiple_languages(self, normalizer):
        """Test with various native languages to ensure fallback works."""
        input_text = "I led the team."
        native_langs = ["de", "en", "sr", "uk", "tr", "it", "fr"]

        for lang in native_langs:
            result = normalizer.generate_all_versions(input_text, user_native_language=lang)
            assert all(key in result for key in ["german", "english", "native"])
            # All should be non-empty (or empty if input was empty, which it isn't here)
            if input_text.strip():
                assert result["english"].strip(), f"English version should be populated for {lang}"

    def test_generate_versions_preserves_capitalization(self, normalizer):
        """Test that proper nouns and names are preserved."""
        input_text = "I worked with Python and Microsoft Excel at Google."
        result = normalizer.generate_all_versions(input_text, user_native_language="en")

        # Proper nouns should be preserved
        assert "Python" in result["english"]
        assert "Excel" in result["english"]
        assert "Google" in result["english"]

    def test_generate_versions_realistic_cv_text(self, normalizer):
        """Test with realistic CV text covering multiple skills."""
        cv_text = (
            "I led the development of a machine learning platform. "
            "I managed a team of eight engineers and improved system performance by thirty percent. "
            "I trained junior developers on best practices."
        )
        result = normalizer.generate_all_versions(cv_text, user_native_language="de")

        # All versions should be reasonable length
        min_length = len(cv_text) * 0.7  # At least 70% of original
        assert len(result["english"]) >= min_length
        assert len(result["german"]) >= min_length

        # German should have some translated terms
        german_lower = result["german"].lower()
        has_german_terms = any(term in german_lower for term in ["leitete", "verwaltete", "schulte", "verbesserte"])
        assert has_german_terms, "German version should contain some translated German terms"


class TestVersionConsistency:
    """Test consistency across versions."""

    @pytest.fixture
    def normalizer(self):
        """Provide language normalizer instance."""
        return LanguageNormalizer()

    def test_versions_convey_same_meaning(self, normalizer):
        """Test that all versions convey the same core information."""
        input_text = "I developed software and managed a team."
        result = normalizer.generate_all_versions(input_text, user_native_language="de")

        # All versions should mention development/team management concepts
        for version in [result["english"], result["german"], result["native"]]:
            version_lower = version.lower()
            # Should have some action-related content
            assert any(word in version_lower for word in ["develop", "entwickel", "manag", "verwalt", "team"])

    def test_native_language_preference_respected(self, normalizer):
        """Test that native language preference is respected in output."""
        input_text = "I managed the project"

        # With German native language
        result_de = normalizer.generate_all_versions(input_text, user_native_language="de")
        assert result_de["native"] == result_de["german"]

        # With English native language
        result_en = normalizer.generate_all_versions(input_text, user_native_language="en")
        assert result_en["native"] == result_en["english"]

    def test_error_handling_returns_fallback(self, normalizer):
        """Test that errors gracefully return fallback (all English)."""
        # This is hard to test without mocking, but we can verify the structure
        input_text = "Normal input"
        result = normalizer.generate_all_versions(input_text, user_native_language="invalid_lang")

        # Should still return all three keys
        assert all(key in result for key in ["german", "english", "native"])
        assert len(result["english"]) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
