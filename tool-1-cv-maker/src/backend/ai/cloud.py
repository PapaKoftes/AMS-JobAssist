"""
Cloud AI provider — optional upgrade for when internet is available.

Supports OpenAI and Anthropic APIs with the same interface as local_llm.py.
Only active when AMS_AI_PROVIDER is set to 'openai' or 'anthropic'.

DSGVO NOTE: Enabling cloud AI means CV data leaves the local machine.
The calling code must ensure user consent before activating this module.
"""

import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# ── Configuration from environment ─────────────────────────────────────────

PROVIDER = os.environ.get("AMS_AI_PROVIDER", "local")  # local | ollama | openai | anthropic
OPENAI_API_KEY = os.environ.get("AMS_OPENAI_API_KEY", "")
OPENAI_MODEL = os.environ.get("AMS_OPENAI_MODEL", "gpt-4o-mini")
ANTHROPIC_API_KEY = os.environ.get("AMS_ANTHROPIC_API_KEY", "")
ANTHROPIC_MODEL = os.environ.get("AMS_ANTHROPIC_MODEL", "claude-sonnet-4-20250514")

# Lazy-initialized SDK client
_client = None

# ── Optional SDK imports ───────────────────────────────────────────────────

try:
    import openai as _openai_mod
    _HAS_OPENAI = True
except ImportError:
    _openai_mod = None
    _HAS_OPENAI = False

try:
    import anthropic as _anthropic_mod
    _HAS_ANTHROPIC = True
except ImportError:
    _anthropic_mod = None
    _HAS_ANTHROPIC = False

# ── Shared prompts (same as local_llm.py) ──────────────────────────────────

_LANG_NAMES = {
    "de": "Deutsch", "en": "Englisch", "tr": "Türkisch", "ar": "Arabisch",
    "bs": "Bosnisch", "hr": "Kroatisch", "sr": "Serbisch", "pl": "Polnisch",
    "uk": "Ukrainisch", "ru": "Russisch", "ro": "Rumänisch", "sk": "Slowakisch",
}

_CATEGORY_CONTEXT = {
    "experience": "Berufserfahrung",
    "skills":     "Fähigkeiten und Kenntnisse",
    "background": "Ausbildung / Hintergrund",
    "motivation": "Motivation und Berufsziel",
    "training":   "Weiterbildung",
    "projects":   "Projekte",
    "identity":   "Persönliche Angaben",
}


# ── Public helpers ─────────────────────────────────────────────────────────

def is_cloud_enabled() -> bool:
    """Check if a cloud provider is configured and has an API key."""
    if PROVIDER == "openai" and OPENAI_API_KEY and _HAS_OPENAI:
        return True
    if PROVIDER == "anthropic" and ANTHROPIC_API_KEY and _HAS_ANTHROPIC:
        return True
    return False


def is_ready() -> bool:
    """Check if the cloud client is initialized and ready."""
    if not is_cloud_enabled():
        return False
    _init_client()
    return _client is not None


def _init_client():
    """Lazy-initialize the appropriate SDK client."""
    global _client
    if _client is not None:
        return

    try:
        if PROVIDER == "openai" and OPENAI_API_KEY and _HAS_OPENAI:
            _client = _openai_mod.OpenAI(api_key=OPENAI_API_KEY)
            logger.info(f"Cloud AI: OpenAI client initialized (model: {OPENAI_MODEL})")

        elif PROVIDER == "anthropic" and ANTHROPIC_API_KEY and _HAS_ANTHROPIC:
            _client = _anthropic_mod.Anthropic(api_key=ANTHROPIC_API_KEY)
            logger.info(f"Cloud AI: Anthropic client initialized (model: {ANTHROPIC_MODEL})")

        else:
            logger.debug("Cloud AI: no valid provider/key combination configured")

    except Exception as exc:
        logger.error(f"Cloud AI: failed to initialize client: {exc}")
        _client = None


# ── Core chat function ─────────────────────────────────────────────────────

def chat(system: str, user: str, max_tokens: int = 500) -> Optional[str]:
    """
    Send a chat message to the cloud provider.

    Returns None on any failure so the caller can fall back.
    """
    if not is_ready():
        return None

    try:
        if PROVIDER == "openai":
            return _openai_chat(system, user, max_tokens)
        elif PROVIDER == "anthropic":
            return _anthropic_chat(system, user, max_tokens)
        else:
            return None
    except Exception as exc:
        logger.warning(f"Cloud AI chat error: {exc}")
        return None


def _openai_chat(system: str, user: str, max_tokens: int) -> Optional[str]:
    """Call OpenAI chat completions."""
    logger.info(f"Cloud AI: OpenAI request (model={OPENAI_MODEL}, max_tokens={max_tokens})")
    try:
        response = _client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            max_tokens=max_tokens,
            temperature=0.3,
            top_p=0.9,
        )
        text = response.choices[0].message.content.strip()
        if text and len(text) > 10:
            logger.info(f"Cloud AI: OpenAI response OK ({len(text)} chars)")
            return text
        return None
    except _openai_mod.RateLimitError as exc:
        logger.warning(f"Cloud AI: OpenAI rate limit: {exc}")
        return None
    except _openai_mod.AuthenticationError as exc:
        logger.error(f"Cloud AI: OpenAI auth error: {exc}")
        return None
    except _openai_mod.APITimeoutError as exc:
        logger.warning(f"Cloud AI: OpenAI timeout: {exc}")
        return None
    except Exception as exc:
        logger.warning(f"Cloud AI: OpenAI unexpected error: {exc}")
        return None


def _anthropic_chat(system: str, user: str, max_tokens: int) -> Optional[str]:
    """Call Anthropic messages API."""
    logger.info(f"Cloud AI: Anthropic request (model={ANTHROPIC_MODEL}, max_tokens={max_tokens})")
    try:
        response = _client.messages.create(
            model=ANTHROPIC_MODEL,
            max_tokens=max_tokens,
            system=system,
            messages=[
                {"role": "user", "content": user},
            ],
        )
        text = response.content[0].text.strip()
        if text and len(text) > 10:
            logger.info(f"Cloud AI: Anthropic response OK ({len(text)} chars)")
            return text
        return None
    except _anthropic_mod.RateLimitError as exc:
        logger.warning(f"Cloud AI: Anthropic rate limit: {exc}")
        return None
    except _anthropic_mod.AuthenticationError as exc:
        logger.error(f"Cloud AI: Anthropic auth error: {exc}")
        return None
    except _anthropic_mod.APITimeoutError as exc:
        logger.warning(f"Cloud AI: Anthropic timeout: {exc}")
        return None
    except Exception as exc:
        logger.warning(f"Cloud AI: Anthropic unexpected error: {exc}")
        return None


# ── Task-specific helpers (same interface as local_llm.py) ─────────────────

def polish_answer(text: str, category: str = "experience",
                  lang: str = "de") -> Optional[str]:
    """
    Polish a CV answer using cloud AI. Same interface as local_llm.polish_answer.

    Returns None on failure to trigger fallback.
    """
    lang_name = _LANG_NAMES.get(lang, lang.upper())
    cat_label = _CATEGORY_CONTEXT.get(category, "Lebenslaufinformation")

    if lang == "de":
        task = "Verbessere die Formulierung. Benutze stärkere Tätigkeitsverben."
    else:
        task = (f"Der Text ist auf {lang_name}. "
                f"Verstehe den Inhalt vollständig und schreibe ihn auf professionellem Deutsch um. "
                f"Behalte alle Fakten und Zahlen bei.")

    system = (
        "Du bist ein professioneller Lebenslauf-Assistent für AMS Österreich. "
        "Schreibe rohe Antworten von Jobsuchenden in professionelle deutsche CV-Sätze um. "
        "Regeln: nur Fließtext, max 3 Sätze, keine Einleitung, Inhalt nicht erfinden."
    )
    user = f"Kategorie: {cat_label}\n{task}\n\nAntwort des Teilnehmers:\n{text}\n\nVerbesserte Version:"
    return chat(system, user, max_tokens=350)


def coach_chat(user_message: str, context: dict = None,
               language: str = "de") -> Optional[str]:
    """
    Conversational coaching. Same interface as local_llm.coach_chat.

    Returns None on failure to trigger fallback.
    """
    context = context or {}
    name = context.get("name", "")
    target_job = context.get("target_job", "")
    summary = context.get("sections_summary", "")

    system = (
        "Du bist ein freundlicher, ermutigender Lebenslauf-Coach bei AMS Österreich. "
        "Du hilfst Jobsuchenden dabei, ihren Lebenslauf zu verbessern. "
        "Antworte kurz (max 3 Sätze), klar und ermutigend — nie kritisch oder überwältigend. "
        f"{'Der Teilnehmer heißt ' + name + '. ' if name else ''}"
        f"{'Zielberuf: ' + target_job + '. ' if target_job else ''}"
        f"{'Bisheriger Lebenslauf-Inhalt: ' + summary if summary else ''}"
    )
    return chat(system, user_message, max_tokens=400)


def get_status() -> dict:
    """Return status info for the AI status endpoint."""
    enabled = is_cloud_enabled()
    ready = is_ready() if enabled else False

    if PROVIDER == "openai" and enabled:
        provider_name = "OpenAI"
        model_name = OPENAI_MODEL
    elif PROVIDER == "anthropic" and enabled:
        provider_name = "Anthropic"
        model_name = ANTHROPIC_MODEL
    else:
        provider_name = None
        model_name = None

    return {
        "available": enabled and ready,
        "provider": provider_name,
        "model": model_name,
        "mode": f"Cloud AI ({provider_name})" if ready else "Nicht konfiguriert",
    }
