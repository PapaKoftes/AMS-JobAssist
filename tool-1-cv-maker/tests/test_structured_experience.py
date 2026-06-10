"""
P2.2 — structured work experience: the dump path produces prose experience lines
(no employer/title/dates). _parse_experience_line() splits a clean line into
title/employer/period so the CV renders a proper structured entry. Model-free.
"""
import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parent.parent / "src" / "backend"
sys.path.insert(0, str(BACKEND))
from cv.builder import _parse_experience_line as P  # noqa: E402


def test_parses_role_employer_period():
    t, e, p = P("Kassa und Verkauf bei Spar (2018-2023)")
    assert t == "Kassa und Verkauf" and e == "Spar"
    assert p == {"start": "2018", "end": "2023"}


def test_parses_im_employer():
    t, e, p = P("Reinigungskraft im Hotel Sacher (2 Jahre)")
    assert t == "Reinigungskraft" and e == "Hotel Sacher"


def test_employer_stops_at_dates():
    t, e, p = P("als Kellnerin in einem Restaurant von 2019 bis 2022")
    assert t == "Kellnerin" and e == "Restaurant"
    assert p == {"start": "2019", "end": "2022"}


def test_comma_period():
    t, e, p = P("Lagerarbeiter bei Hofer, 8 Jahre")
    assert t == "Lagerarbeiter" and e == "Hofer"


def test_no_pattern_returns_empty():
    # prose with no clear role-bei-employer structure -> nothing forced
    t, e, p = P("Ich habe einfach viel verschiedene Sachen gemacht")
    assert t == "" and e == ""


def test_empty_input():
    assert P("") == ("", "", None)
