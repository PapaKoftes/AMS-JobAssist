"""
Ollama local AI integration for AMS JobAssist.

Tries Ollama at localhost:11434. Falls back silently to rule-based polish.
Uses only stdlib — no new dependencies.

Priority order: llama3.2 → mistral → phi3 → gemma2 → any available
"""

import os
import json
import logging
import urllib.request
import urllib.error
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

OLLAMA_BASE = "http://localhost:11434"
# Prefer strong multilingual instruct models first (good German + JSON).
PREFERRED_MODELS = ["qwen2.5", "llama3.1", "llama3.2", "qwen2", "mistral", "gemma2", "phi3", "llama2"]

_ollama_available: Optional[bool] = None
_ollama_model: Optional[str] = None


def _http_get(url: str, timeout: int = 3) -> Optional[dict]:
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            return json.loads(resp.read().decode())
    except Exception:
        return None


def _http_post(url: str, payload: dict, timeout: int = 30) -> Optional[dict]:
    try:
        data = json.dumps(payload).encode()
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode())
    except Exception:
        return None


def detect_ollama() -> Tuple[bool, Optional[str]]:
    """Check if Ollama is running and pick the best available model.

    SINGLE-TRACK POLICY: the shipped product uses the in-process GGUF engine
    (local_llm) as its one default brain. Ollama is an OPT-IN upgrade, off unless
    AMS_USE_OLLAMA=1 is set (used by the eval harness and power users with a GPU
    box). This keeps one engine to test/certify and avoids a second, unbundled
    runtime dependency. See COMPLETION_PLAN.md §1.
    """
    global _ollama_available, _ollama_model

    if _ollama_available is not None:
        return _ollama_available, _ollama_model

    if os.environ.get("AMS_USE_OLLAMA", "").strip().lower() not in ("1", "true", "yes", "on"):
        _ollama_available = False
        _ollama_model = None
        return False, None

    result = _http_get(f"{OLLAMA_BASE}/api/tags", timeout=2)
    if not result:
        logger.info("Ollama not available — using rule-based polish")
        _ollama_available = False
        _ollama_model = None
        return False, None

    # Explicit override (ops / eval): pin an exact model tag, e.g.
    # AMS_OLLAMA_MODEL=qwen2.5:7b. Only honoured if that tag is actually installed.
    pinned = os.environ.get("AMS_OLLAMA_MODEL", "").strip()
    if pinned:
        installed = [m.get("name", "") for m in result.get("models", [])]
        if pinned in installed:
            logger.info(f"Ollama model pinned via AMS_OLLAMA_MODEL: {pinned}")
            _ollama_available = True
            _ollama_model = pinned
            return True, pinned
        logger.warning(f"AMS_OLLAMA_MODEL={pinned} not installed; falling back to auto-detect")

    models = [m.get("name", "").split(":")[0] for m in result.get("models", [])]
    if not models:
        logger.info("Ollama running but no models installed")
        _ollama_available = False
        _ollama_model = None
        return False, None

    chosen = None
    for preferred in PREFERRED_MODELS:
        if any(m == preferred or m.startswith(preferred) for m in models):
            chosen = next(m for m in result["models"] if m["name"].split(":")[0] == preferred or m["name"].startswith(preferred))
            chosen = chosen["name"]
            break

    if not chosen:
        chosen = result["models"][0]["name"]

    logger.info(f"Ollama available with model: {chosen}")
    _ollama_available = True
    _ollama_model = chosen
    return True, chosen


def reset_detection():
    """Force re-detection on next call (for testing or after model install)."""
    global _ollama_available, _ollama_model
    _ollama_available = None
    _ollama_model = None


def polish_with_ollama(raw_text: str, category: str = "experience",
                       language: str = "de") -> Optional[str]:
    """
    Polish a raw CV answer using Ollama.

    Understands input in any language (German, Bosnian, Turkish, Arabic, …)
    and outputs a professional German CV formulation.  Falls back to rule-based
    processing by returning None if Ollama is unavailable or produces bad output.

    Args:
        raw_text:  Raw user answer in any language
        category:  Question category (experience / skills / background / …)
        language:  ISO-639-1 code of the detected/selected input language
    """
    available, model = detect_ollama()
    if not available or not model:
        return None

    prompt = _build_prompt(raw_text, category, language)
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.3,
            "top_p": 0.9,
            "num_predict": 350,
        }
    }

    result = _http_post(f"{OLLAMA_BASE}/api/generate", payload, timeout=30)
    if not result:
        logger.warning("Ollama request failed — falling back to rules")
        return None

    response_text = result.get("response", "").strip()
    if not response_text or len(response_text) < 10:
        return None

    cleaned = _clean_response(response_text, raw_text)
    return cleaned if cleaned else None


# Language names + category context live in ai.lang_labels (single source of truth).
from ai.lang_labels import LANG_NAMES as _LANG_NAMES, CATEGORY_CONTEXT as _CATEGORY_CONTEXT


def _build_prompt(raw_text: str, category: str, language: str = "de") -> str:
    """
    Build a language-aware Ollama prompt.

    For German input: keep original and improve phrasing.
    For all other languages: understand the content and rewrite in German.
    """
    category_context = _CATEGORY_CONTEXT.get(category, "Lebenslaufinformation")

    lang_name = _LANG_NAMES.get(language, language.upper())

    if language == "de":
        lang_instruction = (
            "Die Antwort ist auf Deutsch. Verbessere die Formulierung und "
            "benutze stärkere Tätigkeitsverben."
        )
    else:
        lang_instruction = (
            f"Die Antwort wurde auf {lang_name} geschrieben. "
            f"Verstehe den Inhalt vollständig und schreibe ihn auf professionellem Deutsch um. "
            f"Behalte alle genannten Fakten, Zahlen und Fähigkeiten bei."
        )

    return f"""Du bist ein professioneller Lebenslauf-Assistent für AMS Österreich. \
Deine Aufgabe: Rohe Antworten von Jobsuchenden in professionelle deutsche Lebenslauf-Formulierungen umschreiben.

{lang_instruction}

Regeln:
- Ausgabe IMMER auf Deutsch
- Starke Tätigkeitsverben: koordinierte, betreute, leitete, entwickelte, organisierte, verwaltete, optimierte
- Inhalt und Fakten beibehalten — nichts erfinden
- Professionell und klar, aber ehrlich
- Maximal 3–4 Sätze, kein Aufzählungszeichen, nur Fließtext
- Nur der verbesserte Text — keine Einleitung wie "Hier ist die verbesserte Version:"

Kategorie: {category_context}

Originale Antwort:
{raw_text}

Verbesserte deutsche Version:"""


def _clean_response(response: str, original: str) -> str:
    """Strip common LLM prefixes and validate the response makes sense."""
    prefixes_to_remove = [
        "Verbesserte Version:",
        "Verbesserter Text:",
        "Hier ist die verbesserte Version:",
        "Lebenslauf-Version:",
        "Professionelle Version:",
        "**",
        "##",
    ]
    cleaned = response
    for prefix in prefixes_to_remove:
        if cleaned.startswith(prefix):
            cleaned = cleaned[len(prefix):].strip()

    # If the model returned something very short or just repeated the original, skip it
    if len(cleaned) < 15:
        return ""
    if cleaned.lower() == original.lower():
        return ""

    return cleaned


def generate_ollama(system: str, user: str, num_predict: int = 500,
                    temperature: float = 0.3) -> Optional[str]:
    """
    Generic chat/generation via Ollama (used for coach chat, interview prep,
    job match, etc. when a real model is available). Returns None on failure so
    callers fall back to the local 1.5B / rules path.
    """
    available, model = detect_ollama()
    if not available or not model:
        return None
    payload = {
        "model": model,
        "prompt": user,
        "system": system,
        "stream": False,
        "options": {"temperature": temperature, "top_p": 0.9, "num_predict": num_predict},
    }
    result = _http_post(f"{OLLAMA_BASE}/api/generate", payload, timeout=90)
    if not result:
        return None
    resp = (result.get("response") or "").strip()
    return resp or None


_EXTRACT_SCHEMA_KEYS = ("name", "city", "phone", "email", "target_job",
                        "experiences", "education", "skills", "languages", "motivation")


def _ollama_freeform(text: str, language: str, model: str) -> Optional[str]:
    """
    PASS 1 of two-pass extraction: free reasoning with NO format constraint.

    Research ("the Format Tax", arXiv) shows that forcing a model to emit JSON
    via the prompt degrades its reasoning by ~6-8pp, and most of that damage
    comes from the format-requesting prompt, not the decoder. So we first let the
    model just UNDERSTAND the text and write German bullet notes — no JSON — then
    a cheap second pass reformats those notes. This recovers the lost accuracy.
    """
    lang_name = _LANG_NAMES.get(language, language.upper())
    system = (
        "Du bist ein sorgfältiger Lebenslauf-Assistent für AMS Österreich. Du liest "
        "die freie Erzählung einer arbeitssuchenden Person (in irgendeiner Sprache) "
        "und fasst die Fakten auf Deutsch in Stichworten zusammen. Erfinde nichts."
    )
    prompt = f"""Sprache der Eingabe: {lang_name}.
Lies den Text und schreibe in kurzen deutschen Stichworten auf, was du über die
Person weißt. Gehe diese Punkte durch (lass weg, was fehlt):
- Name
- Wohnort
- Telefon
- E-Mail
- Gewünschter Beruf
- Berufserfahrung: für JEDE Stelle eine Zeile mit Tätigkeit, Arbeitgeber und Zeitraum
- Ausbildung / Abschlüsse
- Fähigkeiten / Kenntnisse / Werkzeuge / Programme / Tätigkeiten, die im Text vorkommen — auch aus der Berufserfahrung; nur was genannt wird, nichts erfinden; keine Sprachen
- Sprachen mit Niveau

Schreibe NUR die Stichworte, KEIN JSON, keine Einleitung.

Text:
{text}
"""
    payload = {
        "model": model, "prompt": prompt, "system": system, "stream": False,
        # Extraction is fact-pulling, not creative writing: greedy (temp 0) so the
        # output is deterministic/reproducible and the model cannot drift/invent.
        "options": {"temperature": 0.0, "top_p": 1.0, "num_predict": 600},
    }
    result = _http_post(f"{OLLAMA_BASE}/api/generate", payload, timeout=120)
    notes = (result.get("response") or "").strip() if result else ""
    return notes or None


def _ollama_to_json(source: str, language: str, model: str) -> Optional[dict]:
    """
    PASS 2: reformat already-understood notes (or raw text) into strict JSON.
    Reformatting is mechanical → far less reasoning-sensitive, so format=json is
    safe here. Returns the structured CV dict or None.
    """
    lang_name = _LANG_NAMES.get(language, language.upper())
    system = (
        "Du bist ein präziser Datenformatierer. Du wandelst die gegebenen Notizen in "
        "GENAU das geforderte JSON um. Erfinde nichts; lass Felder leer, wenn die "
        "Info fehlt. Alle Inhalte auf professionellem Deutsch."
    )
    prompt = f"""Sprache: {lang_name}. Wandle die folgenden Notizen in NUR dieses JSON um
(keine Erklärung, keine Markdown-Zeichen):

{{
  "name": "Vor- und Nachname, falls genannt",
  "city": "Wohnort",
  "phone": "Telefonnummer",
  "email": "E-Mail",
  "target_job": "gewünschter Beruf / Zielposition",
  "experiences": ["je EIN kurzer, professioneller deutscher Satz pro Job, z.B. 'Kassa und Verkauf bei Spar (6 Jahre)'"],
  "education": ["Ausbildung/Abschluss, je ein Eintrag"],
  "skills": ["Fähigkeiten, Werkzeuge, Programme, Maschinen und Tätigkeiten, die IM TEXT vorkommen — auch solche, die in der Berufserfahrung stecken. NUR was wirklich genannt wird, NICHTS erfinden. KEINE Sprachen"],
  "languages": ["Sprache mit Niveau, z.B. 'Deutsch (Muttersprache)', 'Englisch (Grundkenntnisse)'"],
  "motivation": "ein Satz zur Motivation, falls erkennbar"
}}

Notizen:
{source}
"""
    payload = {
        "model": model, "prompt": prompt, "system": system, "stream": False,
        "format": "json", "options": {"temperature": 0.0, "top_p": 1.0, "num_predict": 700},
    }
    result = _http_post(f"{OLLAMA_BASE}/api/generate", payload, timeout=120)
    if not result:
        return None
    raw = (result.get("response") or "").strip()
    if not raw:
        return None
    try:
        data = json.loads(raw)
    except Exception:
        import re as _re
        m = _re.search(r"\{.*\}", raw, _re.DOTALL)
        if not m:
            logger.warning("Ollama extraction returned non-JSON")
            return None
        try:
            data = json.loads(m.group(0))
        except Exception:
            return None
    if not isinstance(data, dict):
        return None

    def _as_list(v):
        if isinstance(v, list):
            return [str(x).strip() for x in v if str(x).strip()]
        if isinstance(v, str) and v.strip():
            return [v.strip()]
        return []

    def _as_str(v):
        return str(v).strip() if isinstance(v, (str, int, float)) else ""

    out = {
        "name": _as_str(data.get("name"))[:80],
        "city": _as_str(data.get("city"))[:80],
        "phone": _as_str(data.get("phone"))[:40],
        "email": _as_str(data.get("email"))[:80],
        "target_job": _as_str(data.get("target_job"))[:120],
        "experiences": _as_list(data.get("experiences"))[:8],
        "education": _as_list(data.get("education"))[:6],
        "skills": _as_list(data.get("skills"))[:16],
        "motivation": " ".join(_as_list(data.get("motivation"))) or _as_str(data.get("motivation")),
    }
    langs = _as_list(data.get("languages"))
    for lg in langs:
        if lg and lg not in out["skills"]:
            out["skills"].append(lg)
    return out


def extract_cv_fields_ollama(text: str, language: str = "de") -> Optional[dict]:
    """
    LLM-FIRST structured extraction via Ollama. Default is TWO-PASS (freeform
    reasoning → constrained reformat), the SOTA recipe that beats single-pass
    JSON on small/mid models. Set AMS_EXTRACT_TWOPASS=0 for single-pass (used by
    the eval harness for A/B comparison). Returns the CV dict or None (→ caller
    falls back to the local 1.5B / rules path).
    """
    available, model = detect_ollama()
    if not available or not model:
        return None
    # MEASURED on the eval gold set (qwen2.5:3b, 8 cases): two-pass did NOT beat
    # single-pass (0.825 vs 0.837 macro-F1) — it helped education (+0.17) but hurt
    # skills (-0.26), net wash, and is slower. The Format-Tax paper's +7pp does
    # not reproduce at this task/scale, so two-pass is OFF by default. The code +
    # AMS_EXTRACT_TWOPASS=1 flag are kept for re-testing on larger models / a
    # larger gold set. (See tool-1-cv-maker/eval/qwen3b_*.json.)
    two_pass = os.environ.get("AMS_EXTRACT_TWOPASS", "0").lower() not in ("0", "false", "no")
    source = text
    if two_pass:
        notes = _ollama_freeform(text, language, model)
        if notes:
            # Give pass 2 the notes AND the original, so nothing the notes missed
            # is permanently lost.
            source = f"{notes}\n\n--- Originaltext ---\n{text}"
    return _ollama_to_json(source, language, model)


def get_status() -> dict:
    """Return AI status for the /api/ai/status endpoint."""
    available, model = detect_ollama()
    return {
        "ollama_available": available,
        "model": model,
        "mode": "KI-gestützt" if available else "Regelbasiert",
        "mode_en": "AI-assisted" if available else "Rule-based",
        "description": (
            f"Lokale KI aktiv ({model}) — Ihre Antworten werden mit KI verbessert."
            if available else
            "Regelbasierte Verbesserung aktiv — Ihre Antworten werden automatisch optimiert."
        ),
    }
