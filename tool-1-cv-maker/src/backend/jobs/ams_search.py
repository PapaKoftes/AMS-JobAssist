"""
AMS job-search bridge — Tier 0 "deep-link".

Builds a pre-filled search URL for the public AMS job board (jobs.ams.at, "alle
jobs") from the user's target job + location. The participant's OWN browser opens
that URL and does the search — **this app transmits nothing**. No network call
happens here, so the offline guarantee is untouched and there is no Datenschutz
data transmission to consent to (only a transparency notice in the UI).

Everything in this module is pure and offline: it just normalises text and
assembles a URL string. Unit-tested in tests/test_ams_search.py.

NOTE (build-time): jobs.ams.at is a single-page app, so the exact query parameter
could not be confirmed by static inspection. AMS_JOBS_BASE / AMS_JOBS_QUERY_PARAM
are the single source of truth — if a live search shows a different parameter,
change them here only. Either way the link degrades gracefully: an unrecognised
parameter is ignored and the user still lands on the AMS job portal.
"""
from __future__ import annotations

import re
from urllib.parse import urlencode

# Single source of truth for the AMS job board deep-link.
AMS_JOBS_BASE = "https://jobs.ams.at/public/emps/"
AMS_JOBS_QUERY_PARAM = "query"        # search term (profession/keyword)
AMS_JOBS_LOCATION_PARAM = "location"  # optional location filter

# Filler the user often wraps a target job in ("ich suche eine Stelle als …",
# "Arbeit als …", "I want to work as a …"). Stripped so the search term is clean.
_FILLER = re.compile(
    r"^\s*(?:"
    r"ich\s+(?:suche|m[öo]chte|will|w[üu]rde\s+gerne)\b[^A-Za-zÀ-ÿ]*|"
    r"suche\b[^A-Za-zÀ-ÿ]*|"
    r"(?:eine\s+|einen\s+)?(?:stelle|arbeit|job|t[äa]tigkeit|anstellung|position)\s+als\s+|"
    r"arbeit(?:en)?\s+als\s+|"
    r"als\s+|"
    r"i\s+(?:want|would\s+like)\s+to\s+work\s+as\s+(?:an?\s+)?|"
    r"looking\s+for\s+(?:a\s+job\s+as\s+)?(?:an?\s+)?|"
    r"work\s+as\s+(?:an?\s+)?"
    r")",
    re.IGNORECASE,
)

# Trailing noise after the actual job term ("Verkäuferin oder Kassiererin in Wien").
_TRAILER = re.compile(r"\s+(?:in|bei|im|um|nahe|raum)\s+.*$", re.IGNORECASE)


def normalize_occupation(target_job: str) -> str:
    """Turn a free-text target job into a clean search term.

    Strips lead-in filler ("ich suche als …") and trailing location clauses, then
    collapses whitespace. Deliberately returns the participant's OWN term rather
    than canonicalising it: for a job-board search the user's word (e.g.
    "Verkäuferin") is usually a better, broader query than a formal apprenticeship
    title (e.g. "Einzelhandelskaufmann/frau") — that's how openings are actually
    posted. Canonicalising to AMS-Berufssystematik/ESCO belongs in the *matching*
    layer, not the search URL.
    """
    if not target_job:
        return ""
    s = target_job.strip()
    # Strip filler lead-ins repeatedly (handles "ich suche arbeit als …").
    for _ in range(3):
        new = _FILLER.sub("", s).strip()
        if new == s:
            break
        s = new
    s = _TRAILER.sub("", s).strip()
    s = re.sub(r"\s+", " ", s).strip(" .,;:-")
    return s


def build_ams_search_url(target_job: str, location: str = "") -> dict:
    """Build a pre-filled AMS job-board search link.

    Returns {"url", "occupation", "location"}. Pure/offline — no network. If
    target_job is empty, returns the bare portal URL (user can search there).
    """
    occupation = normalize_occupation(target_job)
    loc = (location or "").strip()
    # Keep only the city/place token from a "1150 Wien" / "Wien, Österreich" style.
    if loc:
        loc = re.split(r"[,/]", loc)[0].strip()
        loc = re.sub(r"\b\d{4}\b", "", loc).strip()  # drop a leading PLZ

    params = {}
    if occupation:
        params[AMS_JOBS_QUERY_PARAM] = occupation
    if loc:
        params[AMS_JOBS_LOCATION_PARAM] = loc

    url = AMS_JOBS_BASE + (("?" + urlencode(params)) if params else "")
    return {"url": url, "occupation": occupation, "location": loc}
