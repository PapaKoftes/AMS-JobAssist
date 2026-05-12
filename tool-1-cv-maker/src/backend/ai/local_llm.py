"""
Local LLM engine — wraps llama-cpp-python to run Qwen2.5-1.5B offline.

Priority chain called by polish engine and chat API:
  1. Local GGUF model (llama-cpp-python)  ← best quality, always offline
  2. Ollama                               ← if trainer already has it
  3. Rule-based                           ← always works, weakest output

Model: Qwen2.5-1.5B-Instruct-Q4_K_M.gguf  (~1.1 GB)
  - Native German + Turkish + Arabic + Bosnian support
  - Runs on CPU, no GPU needed (~3-5 tok/s on a basic laptop)
  - Downloads once via install chain to data/models/
"""

import logging
import os
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# Where the model lives — relative to the data dir
_MODEL_DIR  = Path(__file__).resolve().parents[3] / "data" / "models"
_MODEL_NAME = "qwen2.5-1.5b-instruct-q4_k_m.gguf"
_MODEL_PATH = _MODEL_DIR / _MODEL_NAME

# HuggingFace download URL
MODEL_URL = (
    "https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF"
    "/resolve/main/qwen2.5-1.5b-instruct-q4_k_m.gguf"
)

_llm = None          # cached Llama instance
_llm_ready = None    # True / False / None (not yet checked)


def model_exists() -> bool:
    return _MODEL_PATH.exists() and _MODEL_PATH.stat().st_size > 100_000_000


def _load():
    global _llm, _llm_ready
    if _llm_ready is not None:
        return _llm_ready

    if not model_exists():
        logger.info("Local model not found — falling back to Ollama/rules")
        _llm_ready = False
        return False

    try:
        from llama_cpp import Llama
        logger.info(f"Loading local model: {_MODEL_PATH}")
        _llm = Llama(
            model_path=str(_MODEL_PATH),
            n_ctx=2048,
            n_threads=max(1, (os.cpu_count() or 2) - 1),
            n_gpu_layers=0,       # CPU-only
            verbose=False,
        )
        _llm_ready = True
        logger.info("Local model loaded OK")
        return True
    except ImportError:
        logger.warning("llama-cpp-python not installed — run: pip install llama-cpp-python "
                       "--extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu")
        _llm_ready = False
        return False
    except Exception as e:
        logger.error(f"Failed to load local model: {e}")
        _llm_ready = False
        return False


def is_ready() -> bool:
    return _load()


def _run(prompt: str, max_tokens: int = 400, temperature: float = 0.3) -> Optional[str]:
    if not _load() or _llm is None:
        return None
    try:
        out = _llm(
            prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=0.9,
            stop=["<|im_end|>", "\n\n\n"],
            echo=False,
        )
        text = out["choices"][0]["text"].strip()
        return text if len(text) > 10 else None
    except Exception as e:
        logger.error(f"LLM inference error: {e}")
        return None


# ── Chat-style wrapper (system + user turns) ────────────────────────────────

def chat(system: str, user: str, max_tokens: int = 500) -> Optional[str]:
    """Send a chat-formatted prompt using Qwen's ChatML template."""
    prompt = (
        f"<|im_start|>system\n{system}<|im_end|>\n"
        f"<|im_start|>user\n{user}<|im_end|>\n"
        f"<|im_start|>assistant\n"
    )
    return _run(prompt, max_tokens=max_tokens, temperature=0.4)


# ── Task-specific helpers ────────────────────────────────────────────────────

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


def polish_answer(raw_text: str, category: str = "experience",
                  language: str = "de") -> Optional[str]:
    """
    Rewrite a raw CV answer as a professional German sentence.
    Input can be any language — output is always German.
    Returns None if model not available (caller falls back to rules).
    """
    lang_name  = _LANG_NAMES.get(language, language.upper())
    cat_label  = _CATEGORY_CONTEXT.get(category, "Lebenslaufinformation")

    if language == "de":
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
    user = f"Kategorie: {cat_label}\n{task}\n\nAntwort des Teilnehmers:\n{raw_text}\n\nVerbesserte Version:"
    return chat(system, user, max_tokens=350)


def coach_chat(user_message: str, cv_context: dict, language: str = "de") -> Optional[str]:
    """
    Respond to a chat message from the user, with awareness of their CV.
    cv_context: dict with keys target_job, name, path, sections_summary
    """
    name       = cv_context.get("name", "")
    target_job = cv_context.get("target_job", "")
    summary    = cv_context.get("sections_summary", "")

    system = (
        "Du bist ein freundlicher, ermutigender Lebenslauf-Coach bei AMS Österreich. "
        "Du hilfst Jobsuchenden dabei, ihren Lebenslauf zu verbessern. "
        "Antworte kurz (max 3 Sätze), klar und ermutigend — nie kritisch oder überwältigend. "
        f"{'Der Teilnehmer heißt ' + name + '. ' if name else ''}"
        f"{'Zielberuf: ' + target_job + '. ' if target_job else ''}"
        f"{'Bisheriger Lebenslauf-Inhalt: ' + summary if summary else ''}"
    )
    return chat(system, user_message, max_tokens=400)


def generate_interview_prep(cv_summary: str, target_job: str) -> Optional[str]:
    """
    Generate likely interview questions based on the finished CV.
    """
    system = (
        "Du bist ein Karriereberater. Erstelle 5 wahrscheinliche Vorstellungsgespräch-Fragen "
        "basierend auf dem Lebenslauf und der Zielstelle. "
        "Nummeriere die Fragen. Jede Frage max. eine Zeile. Keine Einleitung."
    )
    user = f"Zielstelle: {target_job}\n\nLebenslauf-Zusammenfassung:\n{cv_summary}"
    return chat(system, user, max_tokens=400)


def match_job_description(cv_summary: str, job_text: str) -> Optional[str]:
    """
    Compare CV to a job description and give specific, actionable feedback.

    Current mode: job_text is pasted manually by the user.

    Future integration point: instead of a manual paste, this function should
    receive live job postings pulled from the AMS eAMS-Konto system via the
    AMS Open Data API or eAMS API. The analysis logic stays identical — only
    the source of job_text changes. This turns the tool from "here's your CV"
    into "here's your CV and here are three jobs you should apply for today."

    See PHILOSOPHY.md → "Future: AMS Job Service Integration" for full context.
    """
    system = (
        "Du analysierst Lebensläufe gegen Stellenausschreibungen für AMS Österreich. "
        "Antworte auf Deutsch in 3 kurzen Abschnitten:\n"
        "1. ✅ Was passt gut (max 2 Punkte)\n"
        "2. ⚠️ Was fehlt oder sollte ergänzt werden (max 2 Punkte)\n"
        "3. 💡 Ein konkreter Verbesserungsvorschlag\n"
        "Kein Fließtext — nur die 3 Abschnitte."
    )
    user = (
        f"Lebenslauf:\n{cv_summary}\n\n"
        f"Stellenausschreibung:\n{job_text[:1500]}"  # cap at 1500 chars
    )
    return chat(system, user, max_tokens=450)


def get_status() -> dict:
    ready = is_ready()
    return {
        "local_model_available": ready,
        "local_model_path": str(_MODEL_PATH) if ready else None,
        "model_name": _MODEL_NAME,
        "model_exists_on_disk": model_exists(),
        "mode": "Lokales KI-Modell" if ready else ("Modell vorhanden, lädt…" if model_exists() else "Kein Modell"),
    }


def download_model(progress_callback=None) -> bool:
    """
    Download the GGUF model from HuggingFace.
    progress_callback(bytes_downloaded, total_bytes) called periodically.
    Returns True on success.
    """
    import urllib.request
    _MODEL_DIR.mkdir(parents=True, exist_ok=True)
    tmp = _MODEL_PATH.with_suffix(".tmp")
    try:
        logger.info(f"Downloading model from {MODEL_URL}")
        def _reporthook(block, block_size, total):
            if progress_callback:
                progress_callback(block * block_size, total)
        urllib.request.urlretrieve(MODEL_URL, str(tmp), _reporthook)
        tmp.rename(_MODEL_PATH)
        logger.info(f"Model downloaded: {_MODEL_PATH}")
        return True
    except Exception as e:
        logger.error(f"Model download failed: {e}")
        if tmp.exists():
            tmp.unlink()
        return False
