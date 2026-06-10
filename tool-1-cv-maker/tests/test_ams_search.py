"""Unit tests for the AMS job-search deep-link builder (pure, offline)."""
import sys
from pathlib import Path
from urllib.parse import urlparse, parse_qs

BACKEND = Path(__file__).resolve().parent.parent / "src" / "backend"
sys.path.insert(0, str(BACKEND))
from jobs import ams_search as J  # noqa: E402


def _qs(url):
    return {k: v[0] for k, v in parse_qs(urlparse(url).query).items()}


# ---- normalize_occupation --------------------------------------------------

def test_strips_german_filler():
    # Keeps the user's own term (no over-canonicalisation), filler removed.
    assert J.normalize_occupation("ich suche eine Stelle als Verkäuferin") == "Verkäuferin"


def test_strips_arbeit_als():
    out = J.normalize_occupation("arbeit als Lagermitarbeiter")
    assert "lager" in out.lower() and "arbeit als" not in out.lower()


def test_strips_english_filler():
    assert J.normalize_occupation("I want to work as a cook") == "cook"


def test_strips_trailing_location():
    out = J.normalize_occupation("Kassiererin in Wien")
    assert "wien" not in out.lower()


def test_empty_is_empty():
    assert J.normalize_occupation("") == ""
    assert J.normalize_occupation("   ") == ""


def test_plain_job_passes_through():
    # A clean job title with no filler and no KB match stays usable.
    out = J.normalize_occupation("Mechatroniker")
    assert out == "Mechatroniker"


# ---- build_ams_search_url --------------------------------------------------

def test_url_has_base_and_query():
    r = J.build_ams_search_url("Verkäuferin", "Wien")
    assert r["url"].startswith(J.AMS_JOBS_BASE)
    qs = _qs(r["url"])
    assert J.AMS_JOBS_QUERY_PARAM in qs
    assert qs[J.AMS_JOBS_QUERY_PARAM]  # non-empty occupation


def test_url_includes_location_city_only():
    r = J.build_ams_search_url("Koch", "1150 Wien")
    qs = _qs(r["url"])
    assert qs.get(J.AMS_JOBS_LOCATION_PARAM) == "Wien"  # PLZ stripped


def test_empty_target_returns_bare_portal():
    r = J.build_ams_search_url("", "")
    assert r["url"] == J.AMS_JOBS_BASE
    assert r["occupation"] == "" and r["location"] == ""


def test_url_is_properly_encoded():
    # spaces / umlauts must be percent-encoded, never raw in the URL
    r = J.build_ams_search_url("Bürokauffrau Teilzeit", "Wien")
    assert " " not in r["url"]
    assert "ü" not in r["url"].split("?")[1]  # query part is encoded


def test_returns_occupation_and_location_fields():
    r = J.build_ams_search_url("ich suche als Reinigungskraft", "Graz")
    assert r["occupation"] and r["location"] == "Graz"


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v"]))
