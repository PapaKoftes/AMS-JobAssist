import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src" / "backend"))
from ai.local_llm import _extract_skills_regex as S


def test_bare_kenne():
    out = S("Ich habe gearbeitet und kenne Windows, Active Directory, Netzwerke und Ticketsysteme.")
    assert "Windows" in out and "Active Directory" in out and "Netzwerke" in out


def test_ich_kann():
    out = S("Ich kann Verkabelung, Schaltpläne lesen und Wartung")
    assert "Verkabelung" in out and "Wartung" in out


def test_no_trigger_empty():
    assert S("Ich habe im Verkauf gearbeitet und war fleißig") == []


def test_english_triggers():
    out = S("I know Python, Django and PostgreSQL")
    assert "Python" in out and "PostgreSQL" in out


def test_prose_clauses_are_not_skills():
    # The main failure mode: verb/soft-skill clauses must NOT become skills.
    assert S("ich kann gut mit menschen umgehen und bin sehr motiviert") == []
    assert S("ich kann nicht so gut deutsch") == []
    assert "bin sehr motiviert" not in S("ich kann pünktlich sein und bin sehr motiviert")


def test_leading_filler_stripped():
    # "gut Excel" should yield "Excel", not "gut Excel".
    out = S("ich kann gut Excel und sehr gut Word")
    assert "Excel" in out and "Word" in out
    assert "gut Excel" not in out


def test_real_skills_still_extracted():
    out = S("Ich kann Excel, Word und PowerPoint")
    assert out == ["Excel", "Word", "PowerPoint"]
    assert "Stapler fahren" in S("ich kann Stapler fahren")
    assert "Kassa" in S("Erfahrung mit Kassa und Lagerverwaltung")
