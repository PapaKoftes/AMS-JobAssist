"""
Bewerbungs-Check — hire-readiness analysis of a finished CV.

Goes beyond the keyword-only ATS score: it checks the things Austrian recruiters
and application systems actually filter on for the AMS clientele (trades, care,
retail, gastro, office) and returns CONCRETE, actionable fixes — so the produced
CV is optimised for getting an interview, not just a number.

Pure / offline / stdlib — `analyze_cv(cv_dict, job_description="")` takes a flat
dict (the endpoint maps CVData onto it) so the logic is unit-testable in isolation.
"""
from __future__ import annotations

import re
from typing import Optional


def _grade(percent: int) -> str:
    if percent >= 85:
        return "Sehr gut"
    if percent >= 70:
        return "Gut"
    if percent >= 50:
        return "Ausreichend"
    return "Verbesserungsbedarf"


def analyze_cv(cv: dict, job_description: str = "") -> dict:
    """Return a hire-readiness report for a CV.

    cv keys (all optional): name, phone, email, city, target_job, photo (bool),
    languages [{language, code, level}], experiences [str], education [str],
    skills [str], all_text (str, everything concatenated for free-text scans).
    """
    checks: list[dict] = []

    def add(cid: str, label: str, ok: bool, weight: int, tip: str) -> None:
        checks.append({
            "id": cid, "label": label, "ok": bool(ok),
            "weight": weight, "tip": "" if ok else tip,
        })

    name = (cv.get("name") or "").strip()
    add("name", "Vollständiger Name", len(name.split()) >= 2, 2,
        "Geben Sie Vor- und Nachnamen an.")

    phone = (cv.get("phone") or "").strip()
    email = (cv.get("email") or "").strip()
    add("contact", "Telefon und E-Mail", bool(phone) and bool(email), 3,
        "Ergänzen Sie Telefonnummer UND E-Mail — Arbeitgeber müssen Sie schnell erreichen können.")

    target = (cv.get("target_job") or "").strip()
    add("target_job", "Zielberuf angegeben", bool(target), 2,
        "Nennen Sie den gewünschten Beruf — das richtet den ganzen Lebenslauf darauf aus.")

    add("photo", "Bewerbungsfoto vorhanden", bool(cv.get("photo")), 1,
        "Ein freundliches, professionelles Foto erhöht in Österreich die Einladungschance "
        "(besonders Verkauf, Pflege, Gastronomie).")

    langs = cv.get("languages") or []
    has_de_level = any(
        (str(l.get("code", "")).lower() == "de" or "deutsch" in str(l.get("language", "")).lower())
        and str(l.get("level", "")).strip()
        for l in langs
    )
    add("german_level", "Deutsch-Niveau angegeben", has_de_level, 3,
        "Geben Sie Ihr Deutsch-Niveau an (z.B. B1, B2 oder Muttersprache) — "
        "viele Arbeitgeber filtern Bewerbungen genau danach.")

    all_text = cv.get("all_text") or ""
    has_license = bool(re.search(
        r"führerschein|fuehrerschein|driving licen|fahrerlaubnis|"
        r"klasse\s*[a-e]\b|\b[a-e]-?führerschein\b|staplerschein|gabelstapler",
        all_text, re.IGNORECASE))
    add("license", "Führerschein / Schein genannt (falls vorhanden)", has_license, 2,
        "Falls vorhanden: Führerschein (B, C) oder Staplerschein angeben — bei Lager, "
        "Transport und Handwerk ist das oft ein Pflichtkriterium.")

    exps = cv.get("experiences") or []
    add("experience", "Berufserfahrung beschrieben", len(exps) >= 1, 3,
        "Beschreiben Sie mindestens eine Tätigkeit mit Ihren Aufgaben.")

    add("education", "Ausbildung / Schule vorhanden", len(cv.get("education") or []) >= 1, 1,
        "Ergänzen Sie Schulabschluss, Lehre, Ausbildung oder Kurse.")

    add("skills", "Mindestens 3 Kenntnisse", len(cv.get("skills") or []) >= 3, 2,
        "Listen Sie mehrere konkrete Kenntnisse und Stärken auf.")

    exp_text = " ".join(exps) if isinstance(exps, list) else str(exps)
    has_numbers = bool(re.search(r"\b\d{1,4}\b", exp_text))
    add("quantified", "Zahlen / Erfolge genannt", has_numbers, 1,
        "Nennen Sie konkrete Zahlen (z.B. ca. 150 Kunden pro Tag, Team von 5 Personen, "
        "5 Jahre Erfahrung) — das überzeugt Personalverantwortliche.")

    matched: list[str] = []
    missing: list[str] = []
    if job_description.strip():
        try:
            from .ats import extract_keywords
            job_kw = extract_keywords(job_description)
            cv_kw = {k.lower() for k in extract_keywords(all_text)}
            for k in job_kw:
                (matched if k.lower() in cv_kw else missing).append(k)
            kw_ok = (len(matched) >= max(1, len(job_kw) // 2)) if job_kw else True
            tip = "Übernehmen Sie wichtige Begriffe aus der Stellenanzeige in Ihren Lebenslauf"
            if missing:
                tip += ": " + ", ".join(missing[:6])
            add("keywords", "Passende Schlüsselwörter zur Stelle", kw_ok, 3, tip)
        except Exception:
            pass

    total_w = sum(c["weight"] for c in checks) or 1
    got_w = sum(c["weight"] for c in checks if c["ok"])
    percent = round(got_w / total_w * 100)

    # Top concrete next actions: the highest-weight failed checks first.
    todo = [c["tip"] for c in sorted(
        (c for c in checks if not c["ok"]), key=lambda c: -c["weight"]) if c["tip"]]

    return {
        "percent": percent,
        "grade": _grade(percent),
        "passed": sum(1 for c in checks if c["ok"]),
        "total": len(checks),
        "checks": checks,
        "todo": todo,
        "matched_keywords": matched,
        "missing_keywords": missing,
    }
