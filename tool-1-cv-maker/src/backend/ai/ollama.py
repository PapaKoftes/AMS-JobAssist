"""
Ollama local AI integration for AMS JobAssist.

Tries Ollama at localhost:11434. Falls back silently to rule-based polish.
Uses only stdlib — no new dependencies.

Priority order: llama3.2 → mistral → phi3 → gemma2 → any available
"""

import json
import logging
import urllib.request
import urllib.error
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

OLLAMA_BASE = "http://localhost:11434"
PREFERRED_MODELS = ["llama3.2", "mistral", "phi3", "gemma2", "llama2", "qwen2"]

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
    """Check if Ollama is running and pick the best available model."""
    global _ollama_available, _ollama_model

    if _ollama_available is not None:
        return _ollama_available, _ollama_model

    result = _http_get(f"{OLLAMA_BASE}/api/tags", timeout=2)
    if not result:
        logger.info("Ollama not available — using rule-based polish")
        _ollama_available = False
        _ollama_model = None
        return False, None

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


# Human-readable language names for the AI prompt
_LANG_NAMES = {
    "de": "Deutsch", "en": "Englisch", "tr": "Türkisch", "ar": "Arabisch",
    "bs": "Bosnisch", "hr": "Kroatisch", "sr": "Serbisch", "pl": "Polnisch",
    "uk": "Ukrainisch", "ru": "Russisch", "ro": "Rumänisch", "sk": "Slowakisch",
    "cs": "Tschechisch", "hu": "Ungarisch", "it": "Italienisch", "fr": "Französisch",
}


def _build_prompt(raw_text: str, category: str, language: str = "de") -> str:
    """
    Build a language-aware Ollama prompt.

    For German input: keep original and improve phrasing.
    For all other languages: understand the content and rewrite in German.
    """
    category_context = {
        "experience": "Berufserfahrung oder Arbeitstätigkeit",
        "skills":     "Fähigkeiten und Kenntnisse",
        "background": "Ausbildung und Hintergrund",
        "motivation": "Motivation und Karriereziele",
        "training":   "Weiterbildung und Kurse",
        "projects":   "Projekte und Leistungen",
        "identity":   "Persönliche Angaben",
    }.get(category, "Lebenslaufinformation")

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
