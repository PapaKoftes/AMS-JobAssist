"""Tests for honest language-level detection (H1) + the merge export gate (H3)."""
import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parent.parent / "src" / "backend"
sys.path.insert(0, str(BACKEND))

from cv.language_levels import detect_level, is_cefr, display_label, level_rank  # noqa: E402


class TestDetectLevel:
    def test_explicit_cefr_band_kept(self):
        assert detect_level("Deutsch B2") == "B2"
        assert detect_level("englisch c1") == "C1"
        assert detect_level("A2 Niveau") == "A2"

    def test_native_detected(self):
        assert detect_level("Bosnisch Muttersprache") == "native"
        assert detect_level("mother tongue") == "native"

    def test_vague_positive_never_becomes_cefr_band(self):
        # H1: "gut"/"fließend" must NOT fabricate B2/C1 — they map to a
        # descriptive level instead, which is not a CEFR band.
        assert detect_level("Deutsch gut") == "Gut"
        assert not is_cefr(detect_level("Deutsch gut"))
        assert detect_level("Englisch fließend") == "Fließend"
        assert not is_cefr(detect_level("Englisch fließend"))
        assert detect_level("Deutsch sehr gut") == "Sehr gut"

    def test_negation_never_upgrades(self):
        # H1 core: negated proficiency must never become a positive level.
        assert detect_level("Deutsch nicht so gut") == "Grundkenntnisse"
        assert not is_cefr(detect_level("Deutsch nicht so gut"))
        assert detect_level("kaum Englisch") == "Grundkenntnisse"
        assert detect_level("kein gutes Deutsch") == "Grundkenntnisse"

    def test_basic_wording(self):
        assert detect_level("Grundkenntnisse Englisch") == "Grundkenntnisse"
        assert detect_level("nur wenig Deutsch") == "Grundkenntnisse"

    def test_nothing_stated(self):
        assert detect_level("Deutsch") == ""
        assert detect_level("") == ""


class TestIsCefr:
    def test_bands(self):
        for b in ("A1", "a2", "B1", "b2", "C1", "C2"):
            assert is_cefr(b)

    def test_non_bands(self):
        for v in ("", "native", "Gut", "Fließend", "Grundkenntnisse", "GUT"):
            assert not is_cefr(v)


class TestDisplayLabel:
    def test_cefr_glossed(self):
        assert display_label("b2") == "B2 – Arbeitsniveau"
        assert display_label("native") == "Muttersprache"

    def test_descriptive_verbatim(self):
        assert display_label("Gut") == "Gut"
        assert display_label("Fließend") == "Fließend"
        assert display_label("Grundkenntnisse") == "Grundkenntnisse"

    def test_empty(self):
        assert display_label("") == ""


class TestLevelRank:
    def test_cefr_outranks_empty_and_basic(self):
        assert level_rank("B2") > level_rank("")
        assert level_rank("C2") > level_rank("Grundkenntnisse")
        assert level_rank("Gut") > level_rank("")


class TestExtractLanguagesFromSkills:
    def test_no_fabricated_band_through_pipeline(self):
        from cv.builder import _extract_languages_from_skills
        langs, _ = _extract_languages_from_skills(["Deutsch nicht so gut", "Englisch B2"])
        by_code = {l["code"]: l for l in langs}
        assert by_code["de"]["level"] == "Grundkenntnisse"  # not B2
        assert by_code["en"]["level"] == "B2"


class TestEuropassOnlyEmitsCefr:
    def test_descriptive_level_not_emitted_as_cefr(self):
        import xml.etree.ElementTree as ET
        from cv.models import CVData
        from export.europass_export import EuropassExporter
        cv = CVData(session_id="1", user_id="u", interview_path="unemployed", language_input="de")
        cv.languages = [
            {"language": "Deutsch", "code": "de", "level": "Gut"},        # descriptive
            {"language": "Englisch", "code": "en", "level": "B2"},        # CEFR
            {"language": "Bosnisch", "code": "bs", "level": "native"},
        ]
        root = EuropassExporter()._build_xml(cv, language="de")
        text = ET.tostring(root, encoding="unicode")
        assert "<ProficiencyLevel>B2</ProficiencyLevel>" in text  # real CEFR emitted
        assert "GUT" not in text  # descriptive level must NOT appear as a CEFR code
        assert "Deutsch" in text  # but the language itself is still listed


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v"]))
