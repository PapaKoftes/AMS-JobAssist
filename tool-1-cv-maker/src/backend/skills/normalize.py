"""
Offline skill normalization (Layer A).

Maps a free-text / multilingual skill phrase to a canonical AMS-aligned label from
data/knowledge/skills_taxonomy.json, so the trainer dashboard can aggregate cohorts
by skill even when participants phrase the same thing differently or in different
languages ("Stapler" / "forklift" / "vilicar" -> "Staplerschein/Gabelstapler").

Fully offline, pure stdlib (difflib for fuzzy fallback). Loaded once, cached. The
taxonomy is bundled into the frozen .exe via build_tool1.spec (data/knowledge/).
"""
from __future__ import annotations

import json
import logging
import re
import sys
import unicodedata
from difflib import SequenceMatcher
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# Frozen-aware path: in a PyInstaller build the taxonomy is unpacked under the
# bundle root at data/knowledge/ (same pattern as ai/knowledge.py).
if getattr(sys, "frozen", False):
    _TAXO_PATH = Path(sys.executable).resolve().parent / "data" / "knowledge" / "skills_taxonomy.json"
    _ALT_TAXO_PATH = Path(getattr(sys, "_MEIPASS", ".")) / "data" / "knowledge" / "skills_taxonomy.json"
else:
    _TAXO_PATH = Path(__file__).resolve().parents[3] / "data" / "knowledge" / "skills_taxonomy.json"
    _ALT_TAXO_PATH = _TAXO_PATH

_FUZZY_THRESHOLD = 0.86  # difflib ratio above which a near-match counts

_loaded = False
_canonical: list[str] = []                  # canonical labels, in taxonomy order
_label_of_category: dict[str, str] = {}     # canonical label -> category
_syn_index: dict[str, str] = {}             # exact synonym/label (norm) -> canonical
_syn_pairs: list[tuple[str, str]] = []      # (synonym_norm, canonical) for fuzzy

_ZERO_WIDTH = "".join(chr(c) for c in (0x200b, 0x200c, 0x200d, 0xfeff))
_PUNCT = re.compile(r"[.,;:!?()/\\\[\]\"'•·\-–—]")


def _fold_diacritics(s: str) -> str:
    """Fold accents so users who type without diacritics still match:
    viličar->vilicar, müşteri->musteri, Schweißen->schweissen."""
    s = s.replace("ß", "ss")
    # German umlauts read more naturally expanded than stripped.
    s = (s.replace("ä", "ae").replace("ö", "oe").replace("ü", "ue"))
    nfkd = unicodedata.normalize("NFKD", s)
    return "".join(c for c in nfkd if not unicodedata.combining(c))


def _norm(s: str) -> str:
    s = (s or "").strip().lower()
    s = s.translate({ord(c): None for c in _ZERO_WIDTH})  # drop zero-width/BOM
    s = _fold_diacritics(s)
    s = _PUNCT.sub(" ", s)                                 # punctuation -> space
    s = re.sub(r"\s+", " ", s).strip()
    return s


def _load() -> None:
    global _loaded
    if _loaded:
        return
    _loaded = True
    path = _TAXO_PATH if _TAXO_PATH.exists() else _ALT_TAXO_PATH
    if not path.exists():
        logger.warning("skills taxonomy not found: %s", path)
        return
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:  # pragma: no cover
        logger.error("failed to load skills taxonomy: %s", e)
        return
    for entry in data.get("skills", []):
        label = entry.get("label", "").strip()
        if not label:
            continue
        _canonical.append(label)
        _label_of_category[label] = entry.get("category", "")
        # The canonical label itself + all synonyms are match keys.
        for k in [label] + list(entry.get("syn", [])):
            nk = _norm(k)
            if not nk:
                continue
            _syn_index.setdefault(nk, label)
            _syn_pairs.append((nk, label))
    logger.info("skills taxonomy loaded: %d canonical skills", len(_canonical))


def normalize_skill(raw: str) -> Optional[str]:
    """Return the canonical AMS label for a raw skill phrase, or None if unknown.

    Strategy: exact synonym -> synonym contained as a whole word in the phrase ->
    fuzzy (difflib) above threshold. Conservative: returns None rather than a wrong
    guess, so the raw phrase is kept as-is by the caller.
    """
    _load()
    n = _norm(raw)
    if not n or not _syn_pairs:
        return None

    # 1) exact synonym/label match
    hit = _syn_index.get(n)
    if hit:
        return hit

    # 2) a known synonym appears as a whole word inside the phrase
    #    ("ich habe einen staplerschein" contains "staplerschein").
    for syn, label in _syn_pairs:
        if len(syn) >= 4 and re.search(r"\b" + re.escape(syn) + r"\b", n):
            return label

    # 3) fuzzy near-match on the whole phrase (handles typos / minor variants)
    best_label, best_ratio = None, 0.0
    for syn, label in _syn_pairs:
        if abs(len(syn) - len(n)) > 6:
            continue
        r = SequenceMatcher(None, n, syn).ratio()
        if r > best_ratio:
            best_ratio, best_label = r, label
    return best_label if best_ratio >= _FUZZY_THRESHOLD else None


def normalize_skills(raw_skills: list[str]) -> list[str]:
    """Map a list of raw skills to a de-duplicated list of canonical labels.

    Unrecognised skills are dropped from the canonical list (the caller keeps the
    raw list separately). Order follows first appearance.
    """
    out: list[str] = []
    seen: set[str] = set()
    for s in raw_skills or []:
        label = normalize_skill(s)
        if label and label not in seen:
            seen.add(label)
            out.append(label)
    return out


def find_skill_mentions(text: str, limit: int = 10) -> list[str]:
    """Scan free text for skills mentioned ANYWHERE (even buried in a sentence) and
    return the matched literal synonym terms — e.g. "...habe an der Kassa gearbeitet
    und Stapler gefahren" -> ["kassa", "stapler"].

    This boosts skills recall (the weakest extracted field): the model/regex often
    miss a skill embedded in an experience description, but the taxonomy knows the
    vocabulary. Returns at most one term per canonical skill, longest synonyms first
    (so "kundenberatung" wins over a generic token), capped at `limit`. Whole-word,
    len>=4 only, to avoid short-token false fires.
    """
    _load()
    n = _norm(text)
    if not n or not _syn_pairs:
        return []
    out: list[str] = []
    seen_labels: set[str] = set()
    # longest synonyms first → prefer the most specific match per skill
    for syn, label in sorted(_syn_pairs, key=lambda p: -len(p[0])):
        if len(syn) < 4 or label in seen_labels:
            continue
        if re.search(r"\b" + re.escape(syn) + r"\b", n):
            out.append(syn)
            seen_labels.add(label)
            if len(out) >= limit:
                break
    return out


def category_of(label: str) -> str:
    _load()
    return _label_of_category.get(label, "")


def all_canonical_skills() -> list[str]:
    _load()
    return list(_canonical)
