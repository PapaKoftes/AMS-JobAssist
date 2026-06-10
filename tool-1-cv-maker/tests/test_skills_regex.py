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
