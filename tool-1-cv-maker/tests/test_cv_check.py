"""Unit tests for the Bewerbungs-Check hire-readiness analyzer (pure)."""
import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parent.parent / "src" / "backend"
sys.path.insert(0, str(BACKEND))
from polish import cv_check as C  # noqa: E402


def _full_cv():
    return {
        "name": "Leyla Demir", "phone": "0660 123", "email": "l@example.at",
        "target_job": "Bürokauffrau", "photo": True,
        "languages": [{"language": "Deutsch", "code": "de", "level": "B2"}],
        "experiences": ["Verkäuferin bei Hofer, ca. 150 Kunden pro Tag, 5 Jahre"],
        "education": ["Lehre Einzelhandel"],
        "skills": ["Kassa", "Kundenberatung", "Excel"],
        "all_text": "Leyla Demir Verkäuferin Hofer Führerschein B Deutsch B2 Excel Kassa",
    }


def test_full_cv_scores_high():
    r = C.analyze_cv(_full_cv())
    assert r["percent"] >= 85
    assert r["grade"] == "Sehr gut"
    assert r["todo"] == []


def test_missing_german_level_flagged():
    cv = _full_cv()
    cv["languages"] = [{"language": "Deutsch", "code": "de", "level": ""}]
    r = C.analyze_cv(cv)
    gl = next(c for c in r["checks"] if c["id"] == "german_level")
    assert gl["ok"] is False
    assert "Deutsch-Niveau" in gl["tip"]
    assert any("Deutsch-Niveau" in t for t in r["todo"])


def test_missing_contact_is_high_weight_todo():
    cv = _full_cv(); cv["email"] = ""
    r = C.analyze_cv(cv)
    contact = next(c for c in r["checks"] if c["id"] == "contact")
    assert contact["ok"] is False
    # contact (weight 3) should appear before low-weight tips
    assert "erreichen" in r["todo"][0]


def test_license_detected_from_text():
    cv = _full_cv()
    assert next(c for c in C.analyze_cv(cv)["checks"] if c["id"] == "license")["ok"] is True
    cv["all_text"] = "Leyla Demir Verkäuferin Excel"  # no licence mention
    assert next(c for c in C.analyze_cv(cv)["checks"] if c["id"] == "license")["ok"] is False


def test_quantified_detects_numbers():
    cv = _full_cv()
    assert next(c for c in C.analyze_cv(cv)["checks"] if c["id"] == "quantified")["ok"] is True
    cv["experiences"] = ["Verkäuferin, Kundenberatung"]  # no numbers
    assert next(c for c in C.analyze_cv(cv)["checks"] if c["id"] == "quantified")["ok"] is False


def _quant_ok(exp_text):
    cv = _full_cv(); cv["experiences"] = [exp_text]
    return next(c for c in C.analyze_cv(cv)["checks"] if c["id"] == "quantified")["ok"]


def test_quantified_requires_a_real_metric_not_a_bare_year():
    # M2: a plain employment year must NOT count as a quantified achievement.
    assert _quant_ok("Seit 2019 bei Hofer") is False
    assert _quant_ok("2018 bis 2022 als Kellner") is False
    # but real metrics do count
    assert _quant_ok("ca. 150 Kunden pro Tag betreut") is True
    assert _quant_ok("Team von 5 Personen geleitet") is True
    assert _quant_ok("5 Jahre Erfahrung im Verkauf") is True
    assert _quant_ok("20 Kinder betreut") is True


def _license_ok(all_text):
    cv = _full_cv(); cv["all_text"] = all_text
    return next(c for c in C.analyze_cv(cv)["checks"] if c["id"] == "license")["ok"]


def test_license_not_falsely_detected_from_class_words():
    # M1: school / language "Klasse"/"Deutschklasse" must NOT read as a driving licence.
    assert _license_ok("Hassan Ali Deutschklasse B abgeschlossen") is False
    assert _license_ok("Sprachklasse B2 besucht") is False
    # but genuine licences still detected (incl. Austrian 'Lenkberechtigung')
    assert _license_ok("Führerschein der Klasse B vorhanden") is True
    assert _license_ok("B-Führerschein") is True
    assert _license_ok("Lenkberechtigung B und Staplerschein") is True


def test_keywords_check_added_only_with_job():
    r0 = C.analyze_cv(_full_cv())
    assert all(c["id"] != "keywords" for c in r0["checks"])
    r1 = C.analyze_cv(_full_cv(), job_description="Wir suchen Bürokauffrau mit Excel und SAP Kenntnissen.")
    kw = next(c for c in r1["checks"] if c["id"] == "keywords")
    assert "SAP" in r1["missing_keywords"] or "sap" in [m.lower() for m in r1["missing_keywords"]]


def test_empty_cv_low_score():
    r = C.analyze_cv({})
    assert r["percent"] < 50
    assert r["grade"] == "Verbesserungsbedarf"
    assert len(r["todo"]) >= 5


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v"]))
