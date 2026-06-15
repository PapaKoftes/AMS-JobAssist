"""
Single source of truth for language-proficiency levels.

Why this exists: a CV's stated language level is something Austrian employers
filter on, so it must be honest. We only emit a CEFR band (A1-C2) when the user
*actually states one*. Vague wording ("gut", "fließend") becomes a DESCRIPTIVE
level that is rendered verbatim — never a fabricated band like B2 — and a negated
phrase ("nicht so gut") is never upgraded to a positive level.

Returned level tokens (the `level` field on a {language, code, level} dict):
  - a CEFR band: "A1" "A2" "B1" "B2" "C1" "C2"
  - "native"
  - a descriptive German level: "Fließend" | "Sehr gut" | "Gut" | "Grundkenntnisse"
  - "" when nothing about proficiency was stated

Consumers:
  - PDF / DOCX exporters render via `display_label`.
  - The Europass exporter emits <ProficiencyLevel> only when `is_cefr` is true
    (descriptive levels are not valid CEFR codes).
  - builder._extract_languages_from_skills picks the best level via `level_rank`.
"""
from __future__ import annotations

import re

CEFR_BANDS = ("A1", "A2", "B1", "B2", "C1", "C2")

# Display labels (German — the CV language for Austrian employers). CEFR bands get
# a plain-language gloss; descriptive levels render verbatim.
_DISPLAY_LABELS = {
    "native":          "Muttersprache",
    "c2":              "C2 – Verhandlungssicher",
    "c1":              "C1 – Fließend",
    "b2":              "B2 – Arbeitsniveau",
    "b1":              "B1 – Gute Kenntnisse",
    "a2":              "A2 – Grundkenntnisse",
    "a1":              "A1 – Anfänger",
    "fließend":        "Fließend",
    "sehr gut":        "Sehr gut",
    "gut":             "Gut",
    "grundkenntnisse": "Grundkenntnisse",
}

# Ordering for "keep the best level" dedup. CEFR/native are the precise scale;
# descriptive levels rank above "" and roughly where they sit, but a precise CEFR
# band is preferred on a tie.
_LEVEL_RANK = {
    "": 0,
    "grundkenntnisse": 2, "gut": 4, "sehr gut": 5, "fließend": 6,
    "a1": 1, "a2": 2, "b1": 3, "b2": 4, "c1": 5, "c2": 6, "native": 7,
}


def is_cefr(level: str) -> bool:
    """True only for a real CEFR band (A1-C2)."""
    return bool(level) and level.strip().upper() in CEFR_BANDS


def level_rank(level: str) -> int:
    """Comparable rank for choosing the strongest stated level (higher = better)."""
    return _LEVEL_RANK.get((level or "").lower(), 0)


def display_label(level: str) -> str:
    """Human label for a level token; unknown tokens upper-cased as a safe fallback."""
    if not level:
        return ""
    return _DISPLAY_LABELS.get(level.lower(), level.upper())


def detect_level(text: str) -> str:
    """Map free-text proficiency wording to a level token (see module docstring).

    Never fabricates a CEFR band from a bare adjective, and never upgrades a negated
    phrase to a positive level.
    """
    low = text.lower()

    # 1) Explicit CEFR band — the only high-confidence numeric level.
    m = re.search(r"\b([abc][12])\b", low)
    if m:
        return m.group(1).upper()

    # 2) Native speaker (DE/EN/FR + AR/RU/TR/PL/UK native wording).
    if re.search(r"muttersprache|muttersprachlich|native|mother\s*tongue|maternelle?|"
                 r"اللغة الأم|لغة أم|родной|рідна|ana dil|język ojczysty|jezyk ojczysty|"
                 r"materní", low):
        return "native"

    # 3) Negated proficiency ("nicht so gut", "kaum", "kein…") — do NOT claim a
    #    positive level; record basic knowledge at most.
    if re.search(r"\b(nicht|kein|keine|kaum|schlecht)\b|لا أتحدث|плохо|kötü|słabo", low):
        return "Grundkenntnisse"

    # 4) Positive wording → DESCRIPTIVE level (verbatim intent), never a CEFR band.
    #    Includes AR/RU/TR/PL/UK equivalents so a migrant stating level in their own
    #    language still gets a level on the CV (which AT employers filter on).
    if re.search(r"fließend|fliessend|fluent|verhandlungssicher|بطلاقة|свободно|вільно|"
                 r"akıcı|akici|biegle|płynnie|plynnie", low):
        return "Fließend"
    if re.search(r"sehr\s+gut|excellent|ausgezeichnet|hervorragend|ممتاز|отлично|çok iyi|"
                 r"bardzo dobrze", low):
        return "Sehr gut"
    if re.search(r"\bgut\b|good|advanced|fortgeschritten|جيد|хорошо|добре|\biyi\b|dobrze", low):
        return "Gut"
    if re.search(r"grundkenntnisse|basic|basis|anfänger|anfaenger|beginner|\bwenig\b|"
                 r"أساسي|مبتدئ|базов|початков|temel|podstaw", low):
        return "Grundkenntnisse"

    return ""
