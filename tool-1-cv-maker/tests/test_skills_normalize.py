"""Unit tests for offline skill normalization against the AMS taxonomy."""
import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parent.parent / "src" / "backend"
sys.path.insert(0, str(BACKEND))
from skills import normalize as N  # noqa: E402


def test_exact_synonym_maps_to_canonical():
    assert N.normalize_skill("kassa") == "Kassenführung"
    assert N.normalize_skill("Kassensystem") == "Kassenführung"


def test_english_synonym():
    assert N.normalize_skill("forklift") == "Staplerschein/Gabelstapler"
    assert N.normalize_skill("cashier") == "Kassenführung"


def test_multilingual_synonym():
    # Turkish / BKS / transliterated variants must collapse to one canonical skill
    assert N.normalize_skill("temizlik") == "Reinigung"          # TR cleaning
    assert N.normalize_skill("vilicar") == "Staplerschein/Gabelstapler"  # BKS forklift
    assert N.normalize_skill("bakım") == "Pflegeassistenz"       # TR care


def test_synonym_inside_phrase():
    assert N.normalize_skill("ich habe einen Staplerschein gemacht") == "Staplerschein/Gabelstapler"
    assert N.normalize_skill("Erfahrung mit Kundenberatung im Geschäft") == "Kundenberatung"


def test_fuzzy_typo():
    # minor typo still resolves
    assert N.normalize_skill("kommisionieren") == "Kommissionierung"


def test_unknown_returns_none():
    assert N.normalize_skill("Quantenphysik") is None
    assert N.normalize_skill("") is None
    assert N.normalize_skill("   ") is None


def test_normalize_skills_dedups_across_languages():
    raw = ["Stapler", "forklift", "Gabelstapler", "Kassa", "cashier", "Teamarbeit"]
    out = N.normalize_skills(raw)
    # forklift variants collapse to ONE canonical; cashier variants to ONE
    assert out.count("Staplerführung/Gabelstapler") == 0  # exact label below
    assert "Staplerschein/Gabelstapler" in out
    assert out.count("Staplerschein/Gabelstapler") == 1
    assert out.count("Kassenführung") == 1
    assert "Teamfähigkeit" in out


def test_category_lookup():
    assert N.category_of("Kassenführung") == "Handel/Verkauf"
    assert N.category_of("Schweißen") == "Bau/Handwerk"


def test_taxonomy_loaded_nontrivial():
    skills = N.all_canonical_skills()
    assert len(skills) >= 40
    # labels are unique
    assert len(skills) == len(set(skills))


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v"]))
