"""
Local LLM engine — wraps llama-cpp-python to run GGUF models offline.

Architecture (rules-first):
  1. Rule-based engine (PRIMARY) — verb enforcement, skill normalization, structure
  2. Knowledge base (RAG)        — Austrian job data for domain-aware prompts
  3. Local GGUF model            — enhances rule-polished text (lighter task = faster)
  4. Ollama                      — fallback if trainer has a larger model running

The LLM does NOT rewrite from scratch. The rule engine handles 80%+ of the
polish work (verbs, skills, structure). The LLM's job is to:
  - Make rule-polished text flow naturally
  - Add professional framing using knowledge base context
  - Power coach chat and job-match analysis

Tiered models — users choose the best model for their hardware:

  Tier   | Model                         | Size   | RAM    | Speed
  -------|-------------------------------|--------|--------|------------------
  light  | Qwen2.5-0.5B-Instruct Q4_K_M | ~400MB | 4 GB   | ~8-12 tok/s
  medium | Qwen2.5-1.5B-Instruct Q4_K_M | ~1.1GB | 8 GB   | ~3-5 tok/s
  full   | Qwen2.5-3B-Instruct Q4_K_M   | ~2.0GB | 16 GB  | ~1-3 tok/s

All models:
  - Native German + Turkish + Arabic + Bosnian + multilingual support
  - Run on CPU, no GPU needed
  - Download once via in-app button or install chain
  - Verified by SHA-256 hash on download
"""

import logging
import os
from pathlib import Path
from typing import Optional, Dict, List

logger = logging.getLogger(__name__)

# Where models live. Order of resolution:
#   1. AMS_MODEL_DIR env (explicit override),
#   2. FROZEN .exe: <exe-dir>/data/models  — the installer ships the GGUF here.
#      (Do NOT use __file__: in a PyInstaller build it points into the temp
#      extraction dir, which is wiped on exit, so a shipped model is never found.)
#   3. dev/source: tool-1-cv-maker/data/models
import sys as _sys
if os.environ.get("AMS_MODEL_DIR"):
    _MODEL_DIR = Path(os.environ["AMS_MODEL_DIR"])
elif getattr(_sys, "frozen", False):
    _MODEL_DIR = Path(_sys.executable).resolve().parent / "data" / "models"
else:
    _MODEL_DIR = Path(__file__).resolve().parents[3] / "data" / "models"

# ── Tiered model registry ─────────────────────────────────────────────────────
# Each tier has: filename, HuggingFace URL, expected SHA-256, context window,
# approximate size description, and minimum recommended RAM.

MODEL_TIERS: Dict[str, dict] = {
    "light": {
        "name": "Qwen2.5-0.5B-Instruct Q4_K_M",
        "filename": "qwen2.5-0.5b-instruct-q4_k_m.gguf",
        "url": (
            "https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct-GGUF"
            "/resolve/main/qwen2.5-0.5b-instruct-q4_k_m.gguf"
        ),
        "sha256": "",  # TODO: pin after first verified download
        "n_ctx": 2048,
        "size_mb": 400,
        "min_ram_gb": 4,
        "description": "Schnell — gut für ältere Laptops (4 GB RAM)",
    },
    "medium": {
        "name": "Qwen2.5-1.5B-Instruct Q4_K_M",
        "filename": "qwen2.5-1.5b-instruct-q4_k_m.gguf",
        "url": (
            "https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF"
            "/resolve/main/qwen2.5-1.5b-instruct-q4_k_m.gguf"
        ),
        "sha256": "6a1a2eb6d15622bf3c96857206351ba97e1af16c30d7a74ee38970e434e9407e",
        "n_ctx": 2048,
        "size_mb": 1100,
        "min_ram_gb": 8,
        "description": "Empfohlen — beste Balance aus Qualität und Geschwindigkeit (8 GB RAM)",
    },
    "full": {
        "name": "Qwen2.5-3B-Instruct Q4_K_M",
        "filename": "qwen2.5-3b-instruct-q4_k_m.gguf",
        "url": (
            "https://huggingface.co/Qwen/Qwen2.5-3B-Instruct-GGUF"
            "/resolve/main/qwen2.5-3b-instruct-q4_k_m.gguf"
        ),
        # Pinned: this is the SHIPPED default model (bundled in the installer).
        "sha256": "5ee4f07cdb9beadbbb293e85803c569b01bd37ed059d2715faa7bb405f31caa6",
        "n_ctx": 4096,
        "size_mb": 2000,
        "min_ram_gb": 8,
        "description": "Beste Qualität — empfohlen, läuft auf normalen Büro-PCs (8 GB RAM)",
    },
}

# Default tier when NO model file is present yet. The shipped product bundles the
# "full" (3B) model, and _get_active_tier() auto-selects it (full > medium > light)
# whenever its file is on disk — so 3B is the de-facto default in the installer.
DEFAULT_TIER = "full"


def _get_active_tier() -> str:
    """Return the configured model tier. Falls back to whichever tier has a model on disk."""
    preferred = os.environ.get("AMS_MODEL_TIER", "").lower()
    if preferred in MODEL_TIERS:
        return preferred
    # Auto-detect: use the best available model on disk (full > medium > light)
    for tier in ("full", "medium", "light"):
        path = _MODEL_DIR / MODEL_TIERS[tier]["filename"]
        if path.exists() and path.stat().st_size > 10_000_000:
            return tier
    return DEFAULT_TIER


def _get_model_path() -> Path:
    tier = _get_active_tier()
    return _MODEL_DIR / MODEL_TIERS[tier]["filename"]


def _get_model_config() -> dict:
    return MODEL_TIERS[_get_active_tier()]


# Legacy aliases for backward compatibility
_MODEL_NAME = MODEL_TIERS[DEFAULT_TIER]["filename"]
_MODEL_PATH = _MODEL_DIR / _MODEL_NAME
MODEL_URL = MODEL_TIERS[DEFAULT_TIER]["url"]
MODEL_SHA256 = MODEL_TIERS[DEFAULT_TIER]["sha256"]

_llm = None          # cached Llama instance
_llm_ready = None    # True / False / None (not yet checked)
_active_tier = None  # which tier is currently loaded

# ── Background download manager state ─────────────────────────────────────────
# Shared so /api/ai/download-status can report progress and /api/ai/download-cancel
# can stop an in-flight download. Guarded by _download_lock.
import threading as _threading

_download_lock = _threading.Lock()
# Serialize inference: llama_cpp.Llama is NOT re-entrant on one instance, and
# FastAPI runs sync endpoints in a threadpool — the background warm-up, two tabs,
# or overlapping live-preview calls could otherwise call the single _llm
# concurrently and crash/garble. On CPU you want serialized inference anyway.
_inference_lock = _threading.Lock()
_cancel_event = _threading.Event()
_download_state: Dict = {
    "status": "idle",   # idle | downloading | verifying | done | error | cancelled
    "tier": None,
    "downloaded": 0,
    "total": 0,
    "error": None,
}


def _set_download_state(**kw) -> None:
    with _download_lock:
        _download_state.update(kw)


def get_download_status() -> Dict:
    """Snapshot of the current/last download for the frontend to poll."""
    with _download_lock:
        s = dict(_download_state)
    s["percent"] = round(s["downloaded"] / s["total"] * 100, 1) if s["total"] else 0.0
    s["downloaded_mb"] = round(s["downloaded"] / 1_000_000, 1)
    s["total_mb"] = round(s["total"] / 1_000_000, 1)
    return s


def cancel_download() -> bool:
    """Signal any in-flight download to stop. The .part file is kept so a later
    download resumes from where it left off."""
    _cancel_event.set()
    _set_download_state(status="cancelled")
    return True


def model_exists() -> bool:
    """Check if any model file exists on disk (any tier)."""
    path = _get_model_path()
    return path.exists() and path.stat().st_size > 10_000_000


def get_available_tiers() -> List[dict]:
    """Return info about all tiers, including which ones have models on disk."""
    result = []
    for tier_id, config in MODEL_TIERS.items():
        path = _MODEL_DIR / config["filename"]
        on_disk = path.exists() and path.stat().st_size > 10_000_000
        result.append({
            "tier": tier_id,
            "name": config["name"],
            "description": config["description"],
            "size_mb": config["size_mb"],
            "min_ram_gb": config["min_ram_gb"],
            "on_disk": on_disk,
            "active": tier_id == _get_active_tier() and _llm_ready is True,
        })
    return result


def _load():
    global _llm, _llm_ready, _active_tier
    if _llm_ready is not None:
        return _llm_ready

    if not model_exists():
        logger.info("No local model found — falling back to Ollama/rules")
        _llm_ready = False
        return False

    tier = _get_active_tier()
    config = MODEL_TIERS[tier]
    model_path = _MODEL_DIR / config["filename"]

    try:
        from llama_cpp import Llama
        logger.info(f"Loading local model [{tier}]: {model_path}")
        _llm = Llama(
            model_path=str(model_path),
            n_ctx=config["n_ctx"],
            n_threads=max(1, (os.cpu_count() or 2) - 1),
            n_gpu_layers=0,       # CPU-only
            verbose=False,
        )
        _llm_ready = True
        _active_tier = tier
        logger.info(f"Local model loaded OK [{tier}]: {config['name']}")
        return True
    except ImportError:
        logger.warning("llama-cpp-python not installed — run: pip install llama-cpp-python "
                       "--extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu")
        _llm_ready = False
        return False
    except Exception as e:
        logger.error(f"Failed to load local model [{tier}]: {e}")
        _llm_ready = False
        return False


def is_ready() -> bool:
    """
    True when AI is available for the request endpoints.

    Prefers Ollama (a real model): if it's up we report ready WITHOUT loading the
    local 1.5B GGUF - saving ~1GB RAM and routing all generation to the better
    model. Only when Ollama is absent do we load/use the local GGUF.
    """
    try:
        from ai import ollama as _ollama
        av, _ = _ollama.detect_ollama()
        if av:
            return True
    except Exception:
        pass
    return _load()


def _run(prompt: str, max_tokens: int = 400, temperature: float = 0.3) -> Optional[str]:
    if not _load() or _llm is None:
        return None
    try:
        with _inference_lock:  # one inference at a time — Llama isn't re-entrant
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

def chat(system: str, user: str, max_tokens: int = 500,
         temperature: float = 0.4) -> Optional[str]:
    """
    Send a chat prompt. Uses the in-process GGUF engine (the shipped default);
    Ollama only if opted in (AMS_USE_OLLAMA=1). Pass temperature=0.0 for
    extraction/structuring (deterministic, no drift); leave the 0.4 default for
    coach/prep/polish where a little variety reads better.
    """
    try:
        from ai import ollama as _ollama
        _av, _ = _ollama.detect_ollama()
        if _av:
            out = _ollama.generate_ollama(system, user, num_predict=max_tokens, temperature=temperature)
            if out:
                return out
    except Exception:
        pass
    prompt = (
        f"<|im_start|>system\n{system}<|im_end|>\n"
        f"<|im_start|>user\n{user}<|im_end|>\n"
        f"<|im_start|>assistant\n"
    )
    return _run(prompt, max_tokens=max_tokens, temperature=temperature)


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

    NOTE: For the main polish pipeline, prefer enhance_polished() which takes
    rule-processed text and does a lighter task = faster + better results.
    This function is used for translation paths and standalone LLM calls.
    """
    lang_name  = _LANG_NAMES.get(language, language.upper())
    cat_label  = _CATEGORY_CONTEXT.get(category, "Lebenslaufinformation")

    # Inject knowledge context if available
    knowledge_block = ""
    try:
        from ai.knowledge import get_context_for_prompt
        ctx = get_context_for_prompt(raw_text, category)
        if ctx:
            knowledge_block = f"\nFachkontext:\n{ctx}\n"
    except ImportError:
        pass

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
    user = f"Kategorie: {cat_label}\n{task}{knowledge_block}\n\nAntwort des Teilnehmers:\n{raw_text}\n\nVerbesserte Version:"
    return chat(system, user, max_tokens=350)


def enhance_polished(rule_polished_text: str, category: str = "experience",
                     language: str = "de", knowledge_ctx: str = "") -> Optional[str]:
    """
    Enhance ALREADY rule-polished CV text — lighter task than full rewrite.

    The rule engine has already:
    - Enforced strong verbs (gemacht → umgesetzt)
    - Normalized skills
    - Fixed capitalization and whitespace

    This function asks the LLM to:
    - Make the text flow naturally (remove robotic feel from rule substitutions)
    - Add professional framing using domain knowledge
    - Keep ALL facts, verbs, and skills intact

    Because the input is already structured, this requires fewer tokens and
    produces better results than asking the LLM to rewrite from scratch.

    Args:
        rule_polished_text: Text already processed by rule engine
        category: CV category (experience, skills, background, etc.)
        language: ISO-639-1 code of the text language
        knowledge_ctx: Pre-built knowledge context string from knowledge.py

    Returns:
        Enhanced text, or None if model not available.
    """
    cat_label = _CATEGORY_CONTEXT.get(category, "Lebenslaufinformation")

    # Build a focused, short prompt — fewer tokens = faster inference
    system = (
        "Du bist ein Lebenslauf-Assistent bei AMS Österreich. "
        "Der folgende Text wurde bereits automatisch verbessert (Verben, Fähigkeiten). "
        "Mache die Formulierung natürlicher und flüssiger. "
        "Regeln: Behalte ALLE Fakten und starken Verben bei. Max 3 Sätze. "
        "Nichts erfinden. Keine Einleitung."
    )

    # Inject knowledge context if provided
    knowledge_block = ""
    if knowledge_ctx:
        knowledge_block = f"\n{knowledge_ctx}\n"

    user = (
        f"Kategorie: {cat_label}{knowledge_block}\n"
        f"Automatisch verbesserter Text:\n{rule_polished_text}\n\n"
        f"Natürlicher formuliert:"
    )

    # Use lower max_tokens — text is already structured, needs less generation
    return chat(system, user, max_tokens=250)


def coach_chat(user_message: str, cv_context: dict, language: str = "de") -> Optional[str]:
    """
    Respond to a chat message from the user, with awareness of their CV.
    cv_context: dict with keys target_job, name, path, sections_summary

    Injects knowledge base context when a target job is known, so the coach
    can give job-specific advice (e.g., "For a Kellner position, mention
    Kassensystem experience").
    """
    name       = cv_context.get("name", "")
    target_job = cv_context.get("target_job", "")
    summary    = cv_context.get("sections_summary", "")

    # Retrieve domain knowledge for the target job
    knowledge_block = ""
    if target_job:
        try:
            from ai.knowledge import get_context_for_prompt, find_job
            job = find_job(target_job)
            if job:
                ctx = get_context_for_prompt(target_job, "experience")
                if ctx:
                    knowledge_block = f"Berufsdaten: {ctx} "
        except ImportError:
            pass

    system = (
        "Du bist ein freundlicher, ermutigender Lebenslauf-Coach bei AMS Österreich. "
        "Du hilfst Jobsuchenden dabei, ihren Lebenslauf zu verbessern. "
        "Antworte kurz (max 3 Sätze), klar und ermutigend — nie kritisch oder überwältigend. "
        f"{'Der Teilnehmer heißt ' + name + '. ' if name else ''}"
        f"{'Zielberuf: ' + target_job + '. ' if target_job else ''}"
        f"{knowledge_block}"
        f"{'Bisheriger Lebenslauf-Inhalt: ' + summary if summary else ''}"
    )
    return chat(system, user_message, max_tokens=400)


import re as _re_mod

# Skill-mention triggers (broader than the inline name/target ones — includes bare
# "kenne", "beherrsche", "Erfahrung mit", English variants). Used as a deterministic
# backstop so explicitly-listed skills are never lost even when the model misses
# skills embedded in a work description (diagnosed gap on the 3B).
_SKILL_TRIGGERS = _re_mod.compile(
    r"\b(?:ich\s+kann|ich\s+kenne|kenne|kann\s+gut|beherrsche|ich\s+spreche|"
    r"erfahrung\s+(?:mit|in)|kenntnisse\s+(?:in|von)|i\s+can|i\s+know|skilled\s+in|"
    r"experience\s+(?:with|in)|knowledge\s+of)\b[\s:]*([A-Za-zÀ-ÿ][^.;\n]{2,160})",
    _re_mod.IGNORECASE)
_SKILL_STOP = {"alles", "lots", "gut", "viel", "vieles", "etwas", "ein", "bisschen",
               "ein bisschen", "gearbeitet", "deutsch", "englisch"}

# Reject fragments that are PROSE, not skills. A captured clause like
# "gut mit menschen umgehen" or "bin sehr motiviert" is a sentence fragment, not a
# discrete skill — emitting it as a CV "skill" is the regex's main failure mode.
_SKILL_NEG = _re_mod.compile(r"\b(nicht|kein|keine|kaum|schlecht|wenig)\b", _re_mod.IGNORECASE)
_SKILL_LEAD_FILLER = _re_mod.compile(r"^(?:sehr\s+gut|ganz\s+gut|gut|sehr|ganz)\s+", _re_mod.IGNORECASE)
# A skill doesn't start with a preposition or a finite verb/pronoun.
_SKILL_BAD_PREFIX = ("mit ", "in ", "im ", "an ", "auf ", "für ", "fuer ", "zu ", "zum ",
                     "bei ", "über ", "ueber ", "von ", "vom ", "aus ", "the ", "a ")
_SKILL_BAD_START = {"bin", "habe", "hatte", "arbeite", "mache", "kann", "möchte", "moechte",
                    "will", "mich", "mir", "mein", "meine", "meinen", "ich", "wir", "es",
                    "am", "is", "was", "have", "can", "very"}


def _looks_like_skill(p: str) -> bool:
    """True if a captured fragment reads like a discrete skill, not a prose clause."""
    p = _SKILL_LEAD_FILLER.sub("", p).strip()
    low = p.lower()
    if not p or len(p) > 40 or p.lower() in _SKILL_STOP:
        return False
    if _SKILL_NEG.search(low):
        return False
    words = low.split()
    if len(words) > 4:
        return False
    if words[0] in _SKILL_BAD_START:
        return False
    if any(low.startswith(pre) for pre in _SKILL_BAD_PREFIX):
        return False
    return True


def _extract_skills_regex(text: str) -> list:
    """Deterministic skill extraction from 'ich kann/kenne/beherrsche … X, Y und Z'.

    Captures discrete skills only — prose clauses ("gut mit menschen umgehen",
    "bin sehr motiviert", "nicht so gut deutsch") are filtered out, since emitting
    those as CV skills is worse than missing them.
    """
    out = []
    for m in _SKILL_TRIGGERS.finditer(text or ""):
        frag = m.group(1)
        # cut off any trailing clause ("… und habe …", "… gearbeitet", "… von 2020")
        frag = _re_mod.split(r"\b(?:und\s+habe|gearbeitet|von\s+\d|seit\s+\d)\b", frag)[0]
        for part in _re_mod.split(r"\s*(?:,|\bund\b|\band\b|/|\|)\s*", frag):
            p = _re_mod.sub(r"\s{2,}", " ", part).strip(" ,;.:-")
            p = _SKILL_LEAD_FILLER.sub("", p).strip()   # normalise "gut Excel" → "Excel"
            if _looks_like_skill(p) and p not in out:
                out.append(p)
    return out


def extract_cv_fields(text: str, language: str = "de") -> dict:
    """
    Free-form "dump" extraction: pull structured CV fields out of one big block
    of text the participant wrote in any language.

    Strategy (rules-first, AI-assisted, never blocks):
      - email / phone via regex (reliable, no model needed)
      - name / city / target job / experience / education / skills via the local
        LLM using a robust labelled-line format (easier for a small model than
        JSON). Falls back gracefully when the model is absent or the output
        can't be parsed.

    Returns a dict:
      {name, city, phone, email, target_job, experiences[], education[], skills[]}
    """
    import re as _re
    result = {
        "name": "", "city": "", "phone": "", "email": "",
        "target_job": "", "experiences": [], "education": [], "skills": [],
    }
    if not text or not text.strip():
        return result

    def _clean(s):
        return _re.sub(r"\s{2,}", " ", str(s or "")).strip(" ,;.:-")

    # ---- email / phone (regex) -------------------------------------------------
    # These two are extracted by regex regardless of engine — a model has no
    # advantage on them and regex is 100% reliable.
    m = _re.search(r"[\w.+-]+@[\w-]+\.[\w.-]+", text)
    if m:
        result["email"] = m.group(0).rstrip(".,;")

    # ---- LLM-FIRST path: a real model (Ollama) does the structuring -----------
    # If Ollama is available, let it parse the messy free text into structured,
    # professional German fields (the thing a 1.5B + regex does poorly). Regex
    # email/phone still win (reliable). This is what makes the "AI" actually do
    # the work instead of being overridden by regex.
    try:
        from ai import ollama as _ollama
        _av, _ = _ollama.detect_ollama()
        if _av:
            _o = _ollama.extract_cv_fields_ollama(text, language)
            if _o:
                # phone via regex below if the model missed it
                m2 = _re.search(r"(?<!\w)(\+?\d[\d\s/()\-]{6,}\d)", text)
                phone = (m2.group(1).strip() if m2 else "") or _o.get("phone", "")
                # Backstop: merge explicitly-listed skills (regex) that the model
                # may have left in the work description instead of the skills field.
                skills = list(_o.get("skills", []))
                _lower = {s.lower() for s in skills}
                for sk in _extract_skills_regex(text):
                    if sk.lower() not in _lower:
                        skills.append(sk); _lower.add(sk.lower())
                return {
                    "name": _o.get("name", ""),
                    "city": _o.get("city", ""),
                    "phone": phone,
                    "email": result["email"] or _o.get("email", ""),
                    "target_job": _o.get("target_job", ""),
                    "experiences": _o.get("experiences", []),
                    "education": _o.get("education", []),
                    "skills": skills,
                    "motivation": _o.get("motivation", ""),
                }
    except Exception as _oe:
        logger.warning(f"Ollama extraction unavailable, using rules/1.5B: {_oe}")

    # No '.' in the phone char class, so it can't spill into the next sentence
    # ("…7778899. 12 Jahre…" no longer captures the "12").
    m = _re.search(r"(?<!\w)(\+?\d[\d\s/()\-]{6,}\d)", text)
    if m:
        result["phone"] = m.group(1).strip()
    # No '.' in the phone char class, so it can't spill into the next sentence
    # ("…7778899. 12 Jahre…" no longer captures the "12").
    m = _re.search(r"(?<!\w)(\+?\d[\d\s/()\-]{6,}\d)", text)
    if m:
        result["phone"] = m.group(1).strip()

    # ---- name (regex, trimmed to first+last, stops at connector words) --------
    _STOP = {"aus", "ich", "und", "der", "die", "das", "ist", "bin", "habe", "hab",
             "kann", "brauche", "brauch", "wohne", "komme", "in", "von", "mit",
             "sehr", "arbeit", "arbeite", "jahre", "jahr", "seit", "als", "bei",
             "ein", "eine", "einen", "my", "i", "am", "name", "mein", "heisse",
             "heiße", "heisst", "wir", "sie", "es", "auch", "oder", "nicht", "gerne",
             "afghanistan", "wien", "graz", "linz", "wels"}
    # Name-intro triggers across the main AMS languages. The structure is
    # "<intro> <Name>" in German, English, Turkish (adım/ismim/benim adım),
    # Bosnian/Croatian/Serbian (zovem se / ja sam / moje ime je) and
    # Arabic-Latin transliteration (ismi). SOV-sensitive job/skill triggers are
    # intentionally NOT added here — those are left to the multilingual LLM step.
    _name_re = _re.search(
        r"\b(?:ich\s+(?:bin|heisse|heiße|heisst)|mein\s+name\s+ist|my\s+name\s+is|i\s*am|i'm|"
        r"benim\s+adım|adım|ismim|zovem\s+se|ja\s+sam|moje\s+ime\s+je|ismi)\s+"
        r"([A-Za-zÀ-ÿ'’\-]{2,}(?:\s+[A-Za-zÀ-ÿ'’\-]{2,}){0,3})",
        text, flags=_re.IGNORECASE)
    _regex_name = ""
    if _name_re:
        _nw = []
        for w in _name_re.group(1).split():
            if w.lower() in _STOP:
                break
            _nw.append(w)
            if len(_nw) >= 2:
                break
        _regex_name = " ".join(_nw)
    if not _regex_name:
        # Leading-name heuristic: "Maria Huber, Linz…" / "Petra Wagner, Wels…".
        _lead = _re.match(r"\s*([A-ZÄÖÜ][a-zà-ÿ]+(?:\s+[A-ZÄÖÜ][a-zà-ÿ]+)?)\s*[,\n]", text)
        if _lead and _lead.group(1).split()[0].lower() not in _STOP:
            _regex_name = _lead.group(1).strip()

    # ---- target job (regex from "suche/möchte/looking for") -------------------
    _tj = _re.search(
        r"\b(?:suche?|m[oö]chte|ich\s+suche|looking\s+for|i\s+want(?:\s+to)?|i\s+am\s+looking|seeking|such\s+wieda|such)\b[\s:]*"
        r"((?:stelle\s+als\s+|job\s+als\s+|arbeit\s+als\s+|a\s+|als\s+|im\s+|in\s+der\s+)?[A-Za-zÀ-ÿ][^.;\n]{2,55})",
        text, flags=_re.IGNORECASE)
    _regex_target = ""
    if _tj:
        _t = _re.sub(r"^\s*(?:stelle|job|arbeit|eine?|einen|wieda|wieder|gerne|again|"
                     r"in\s+ein\w*|im|in\s+der)\s+", "", _tj.group(1), flags=_re.IGNORECASE)
        _t = _re.sub(r"^\s*(?:als|im|in)\s+", "", _t, flags=_re.IGNORECASE)
        _regex_target = _clean(_t)[:60]

    # ---- skills (regex from "ich kann/kenne/spreche" enumerations) ------------
    _regex_skills = []
    for m2 in _re.finditer(
            r"\b(?:ich\s+kann|ich\s+kenne|kann\s+gut|spreche|ich\s+spreche|"
            r"ich\s+bin\s+sehr|bin\s+sehr|i\s+(?:can|know|speak))\b[\s:]*"
            r"([A-Za-zÀ-ÿ][^.;\n]{2,140})", text, flags=_re.IGNORECASE):
        for part in _re.split(r"\s*(?:,|\bund\b|\band\b|/|\|)\s*", m2.group(1)):
            p = _clean(part)
            if p and p.lower() not in {"alles", "lots", "gut", "viel", "vieles", "etwas",
                                       "ein", "bisschen", "ein bisschen"} and 1 < len(p) <= 40:
                if p not in _regex_skills:
                    _regex_skills.append(p)

    # ---- education (regex keywords) -------------------------------------------
    _EDU = (r"(lehre|matura|ausbildung|studium|bachelor|master|diplom|abschluss|"
            r"schule|gymnasium|htl|hlw|hak|\bfh\b|universit|hochschule|kurs|zertifikat|"
            r"gesellenbrief|abgeschlossen|semester|studiere|maturiert|diplomiert|"
            # Turkish: school / high-school / university / diploma / certificate
            r"okul|lise|[uü]niversite|diploma|sertifika|fakülte|mezun|"
            # Bosnian/Croatian/Serbian: school / faculty / university / diploma
            r"škola|fakultet|univerzitet|sveučilište|diplom[ao]|svjedodžba)")
    _regex_edu = []
    for clause in _re.split(r"[.,;\n]", text):
        c = _clean(clause)
        if c and _re.search(_EDU, c, flags=_re.IGNORECASE) and 3 < len(c) <= 90:
            if c not in _regex_edu:
                _regex_edu.append(c)

    def _split_items(val: str):
        parts = [p.strip(" -•·\t") for p in _re.split(r"\s*\|\s*|\n", val)]
        return [p for p in parts if len(p) > 1]

    parsed = False
    try:
        if is_ready():
            sys_prompt = (
                "Du bist ein präziser Lebenslauf-Datenextraktor. Lies den Text des "
                "Nutzers (egal welche Sprache) und gib GENAU diese Zeilen zurück, "
                "nichts anderes. Lass eine Zeile leer, wenn die Info fehlt. Trenne "
                "mehrere Einträge mit ' | '.\n"
                "NAME:\nORT:\nZIELBERUF:\nERFAHRUNG:\nAUSBILDUNG:\nFAEHIGKEITEN:"
            )
            # Two-pass: a freeform reasoning pass with NO format constraint, then
            # the labelled-line reformat — recovers accuracy lost to the "format
            # tax". MEASURED on this 1.5B (eval gold set): two-pass lifts the weak
            # fields (experience precision 0.80→1.0, skills 0.43→0.50) but is 3.7×
            # slower (23s→85s/5 cases). On a small CPU model that latency isn't
            # worth ~+0.01 overall, so two-pass is OFF by default HERE and ON for
            # the Ollama/7B path (see ollama.py). Set AMS_EXTRACT_TWOPASS=1 to force.
            _src = text[:1600]
            if os.environ.get("AMS_EXTRACT_TWOPASS", "0").lower() not in ("0", "false", "no"):
                _ff_sys = (
                    "Du bist ein sorgfältiger Lebenslauf-Assistent. Lies den Text "
                    "(irgendeine Sprache) und schreibe in kurzen deutschen Stichworten, "
                    "was du über die Person weißt: Name, Wohnort, Telefon, E-Mail, "
                    "gewünschter Beruf, jede Arbeitsstelle (Tätigkeit, Arbeitgeber, "
                    "Zeitraum), Ausbildung, Fähigkeiten, Sprachen. KEIN JSON, nur Stichworte."
                )
                _notes = chat(_ff_sys, text[:1600], max_tokens=400, temperature=0.0) or ""
                if _notes.strip():
                    _src = (_notes + "\n\n--- Originaltext ---\n" + text)[:1800]
            out = chat(sys_prompt, _src, max_tokens=420, temperature=0.0) or ""
            for line in out.splitlines():
                if ":" not in line:
                    continue
                key, _, val = line.partition(":")
                key = key.strip().upper()
                val = val.strip()
                if not val:
                    continue
                if key.startswith("NAME"):
                    result["name"] = val[:80]; parsed = True
                elif key.startswith("ORT"):
                    result["city"] = val[:80]; parsed = True
                elif key.startswith("ZIEL"):
                    result["target_job"] = val[:120]; parsed = True
                elif key.startswith("ERFAHRUNG"):
                    result["experiences"] = _split_items(val); parsed = True
                elif key.startswith("AUSBILDUNG"):
                    result["education"] = _split_items(val); parsed = True
                elif key.startswith("FAEHIG") or key.startswith("FÄHIG"):
                    result["skills"] = _split_items(val); parsed = True
    except Exception as _e:
        logger.warning(f"extract_cv_fields LLM step failed (using fallback): {_e}")

    # ---- MERGE: prefer the trustworthy regex values over the small model -------
    # name: regex wins (the model mis-spells / over-grabs); tidy lowercase.
    if _regex_name:
        result["name"] = _regex_name
    nm = result.get("name", "")
    if nm and nm == nm.lower():
        result["name"] = " ".join(w.capitalize() for w in nm.split())

    # target: prefer the participant's literal "suche X" over a model guess
    # (which hallucinated e.g. Maurer -> "Bauingenieur").
    if _regex_target:
        result["target_job"] = _regex_target

    # skills / education: combine regex + model, de-duplicated, regex first.
    def _merge(primary, secondary):
        out = []
        for x in list(primary) + list(secondary):
            x = _clean(x)
            if x and x.lower() not in {y.lower() for y in out}:
                out.append(x)
        return out
    # Taxonomy-driven recall: surface skills mentioned ANYWHERE in the text that the
    # model/regex missed (e.g. a skill buried in an experience sentence). Added last
    # so explicit model/regex skills keep priority. Best-effort, never fatal.
    _taxo_skills: list = []
    try:
        from skills.normalize import find_skill_mentions as _find_sk
        _taxo_skills = _find_sk(text)
    except Exception:
        _taxo_skills = []

    # Skills are atomic: split any comma-joined entry (the model sometimes returns
    # "A, B, C" as one string while the regex returns them split) and dedupe, so
    # the CV never shows a redundant combined skill alongside its parts.
    _merged_skills = _merge(_merge(_regex_skills, result.get("skills") or []), _taxo_skills)
    _skills: list = []
    for _sk in _merged_skills:
        for _part in _re.split(r"\s*,\s*", _sk):
            _part = _clean(_part)
            if _part and _part.lower() not in {y.lower() for y in _skills}:
                _skills.append(_part)
    result["skills"] = _skills[:14]
    result["education"] = _merge(_regex_edu, result.get("education") or [])[:5]

    # ---- EXPERIENCE: clean the fallback so it reads as a CV line, not the raw
    # dump. Strip everything we captured elsewhere (name, city, email, phone,
    # age, skills, education, the "suche …" target clause).
    if not result["experiences"]:
        leftover = text.strip()
        for piece in [result.get("email"), result.get("phone"), result.get("name"),
                      result.get("city")]:
            if piece:
                leftover = _re.sub(_re.escape(piece), " ", leftover, flags=_re.IGNORECASE)
        # "ich bin/heisse/wohne …," and "ich bin 27 jahre alt," intros
        leftover = _re.sub(r"\bich\s+(?:bin|heisse|heiße|heisst|wohne|komme)\s+[^.,;]*[.,;]",
                           " ", leftover, flags=_re.IGNORECASE)
        leftover = _re.sub(r"\b(?:ich\s+)?(?:bin|habe)?\s*\d{1,2}\s*jahre?\s*alt\b[^.,;]*[.,;]?",
                           " ", leftover, flags=_re.IGNORECASE)
        # the "ich kann/kenne/spreche … , lots" enumerations and the target clause
        leftover = _re.sub(r"\bich\s+(?:kann|kenne|spreche)\b[^.;\n]*", " ", leftover, flags=_re.IGNORECASE)
        leftover = _re.sub(r"\b(?:suche?|m[oö]chte|looking\s+for|i\s+want(?:\s+to)?|seeking|such)\b[^.;\n]*", " ", leftover, flags=_re.IGNORECASE)
        leftover = _re.sub(r"\s*,?\s*lots\b\.?", " ", leftover, flags=_re.IGNORECASE)
        # remove captured skill/education phrases to avoid duplication
        for ph in (result.get("skills") or []) + (result.get("education") or []):
            leftover = _re.sub(_re.escape(ph), " ", leftover, flags=_re.IGNORECASE)
        # collapse leftover punctuation noise ("Linz, , . 6 Jahre" -> "6 Jahre")
        leftover = _re.sub(r"[,;]\s*(?=[,;.])", " ", leftover)
        leftover = _re.sub(r"\s*[.,;]\s*", lambda mm: ", " if mm.group(0).strip() == "," else " ", leftover)
        leftover = _re.sub(r"(?:^|\s)[,;.]+", " ", leftover)
        leftover = _re.sub(r"\s{2,}", " ", leftover).strip(" ,;.:-")
        # Only treat the leftover as work experience if it actually mentions work.
        # Otherwise an identity-only dump ("Ich heiße…, Telefon…, E-Mail…") would
        # leave junk like "Meine Telefonnummer ist … Ich" as a fake job.
        _WORK = (r"(gearbeitet|arbeit|t[äa]tig|besch[äa]ftigt|jahre?|\bbei\b|\bals\b|"
                 r"firma|betrieb|praktik|lehre|\bjob\b|angestellt|mitarbeiter|kassa|"
                 r"verk[äa]uf|erfahrung|worked|company|years?)")
        if len(leftover) > 8 and _re.search(_WORK, leftover, flags=_re.IGNORECASE):
            result["experiences"] = [leftover[:600]]
        # else: no work experience in this dump — leave empty (a gap question asks later)
    return result


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

    Uses the knowledge base to understand what skills/verbs are expected for
    the detected job type, giving more targeted recommendations.

    Current mode: job_text is pasted manually by the user.

    Future integration point: instead of a manual paste, this function should
    receive live job postings pulled from the AMS eAMS-Konto system via the
    AMS Open Data API or eAMS API. The analysis logic stays identical — only
    the source of job_text changes. This turns the tool from "here's your CV"
    into "here's your CV and here are three jobs you should apply for today."

    See PHILOSOPHY.md → "Future: AMS Job Service Integration" for full context.
    """
    # Inject knowledge about the job type from RAG
    knowledge_block = ""
    try:
        from ai.knowledge import find_job
        job = find_job(job_text)
        if job:
            skills = ", ".join(job.get("skills", [])[:5])
            knowledge_block = (
                f"\nBeruf: {job['title_de']}\n"
                f"Typische Anforderungen: {skills}\n"
            )
    except ImportError:
        pass

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
        f"Stellenausschreibung:\n{job_text[:1500]}"
        f"{knowledge_block}"
    )
    return chat(system, user, max_tokens=450)


def get_status() -> dict:
    ready = is_ready()
    tier = _active_tier or _get_active_tier()
    config = MODEL_TIERS.get(tier, MODEL_TIERS[DEFAULT_TIER])
    return {
        "local_model_available": ready,
        "local_model_path": str(_MODEL_DIR / config["filename"]) if ready else None,
        "model_name": config["name"],
        "model_tier": tier,
        "model_exists_on_disk": model_exists(),
        "available_tiers": get_available_tiers(),
        "mode": f"Lokales KI-Modell ({config['name']})" if ready else (
            "Modell vorhanden, lädt…" if model_exists() else "Kein Modell"
        ),
    }


def _sha256_of(path: Path, chunk_size: int = 1024 * 1024) -> str:
    """Stream-hash a file with SHA-256."""
    import hashlib
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            h.update(chunk)
    return h.hexdigest()


def verify_model_hash() -> bool:
    """
    Verify the on-disk model matches the pinned SHA-256. Returns True if OK
    or if the pin is the placeholder (allows first-run setup without bricking
    the install).
    """
    if not _MODEL_PATH.exists():
        return False
    if not MODEL_SHA256:
        logger.warning("MODEL_SHA256 is empty — skipping verification.")
        return True
    actual = _sha256_of(_MODEL_PATH)
    ok = actual.lower() == MODEL_SHA256.lower()
    if not ok:
        logger.error(
            "Model SHA-256 mismatch: expected %s, got %s. Refusing to load.",
            MODEL_SHA256, actual,
        )
    return ok


def download_model(progress_callback=None, tier: str = None) -> bool:
    """
    Download a GGUF model from HuggingFace — resumable, cancellable, and safe
    to run in a background thread.

    - Resumes from a partial `.part` file via an HTTP Range request, so an
      interrupted download (dropped connection, app restart, user cancel) is
      continued instead of restarted.
    - Honours cancel_download(): checks the cancel flag between chunks and stops
      cleanly, leaving the `.part` file in place for a later resume.
    - Updates the shared download state so get_download_status() can report
      live progress to the UI.
    - Retries transient network errors with resume (up to 40 attempts).
    - Verifies SHA-256 before installing.

    Args:
        progress_callback: optional function(bytes_downloaded, total_bytes).
        tier: which model tier ("light", "medium", "full"). Defaults to active.
    Returns True on success.
    """
    import urllib.request
    import time

    if tier is None:
        tier = _get_active_tier()
    if tier not in MODEL_TIERS:
        logger.error(f"Unknown model tier: {tier}")
        _set_download_state(status="error", tier=tier, error=f"Unknown tier: {tier}")
        return False

    config = MODEL_TIERS[tier]
    model_path = _MODEL_DIR / config["filename"]
    model_url = config["url"]
    expected_sha = config["sha256"]

    # Integrity: refuse to download a tier with no pinned SHA-256 — otherwise
    # verification is silently skipped and a corrupted/MITM'd GGUF loads unnoticed.
    # Only the pinned 'medium' tier ships verified; light/full must be pinned
    # before use, or explicitly overridden by an operator who accepts the risk.
    if not expected_sha and os.environ.get("AMS_ALLOW_UNPINNED_MODEL", "").lower() not in ("1", "true", "yes"):
        msg = (f"Model tier '{tier}' has no pinned SHA-256 — refusing to install it "
               f"unverified. Use the pinned 'medium' tier, or set "
               f"AMS_ALLOW_UNPINNED_MODEL=1 to override (not recommended).")
        logger.error(msg)
        _set_download_state(status="error", tier=tier, error=msg)
        return False

    # Already installed?
    if model_path.exists() and model_path.stat().st_size > 10_000_000:
        _set_download_state(status="done", tier=tier,
                            downloaded=model_path.stat().st_size,
                            total=model_path.stat().st_size, error=None)
        return True

    _MODEL_DIR.mkdir(parents=True, exist_ok=True)
    part = model_path.with_suffix(".part")

    _cancel_event.clear()
    _set_download_state(status="downloading", tier=tier, downloaded=0, total=0, error=None)
    logger.info(f"Downloading model [{tier}]: {config['name']} from {model_url}")

    def _attempt() -> bool:
        have = part.stat().st_size if part.exists() else 0
        req = urllib.request.Request(model_url, headers={"User-Agent": "ams-jobassist"})
        if have:
            req.add_header("Range", f"bytes={have}-")
        with urllib.request.urlopen(req, timeout=60) as resp:
            total = int(resp.headers.get("Content-Length", 0)) + have
            _set_download_state(downloaded=have, total=total)
            mode = "ab" if have else "wb"
            with open(part, mode) as f:
                while True:
                    if _cancel_event.is_set():
                        logger.info("Model download cancelled by user — .part kept for resume")
                        return False
                    chunk = resp.read(256 * 1024)
                    if not chunk:
                        break
                    f.write(chunk)
                    have += len(chunk)
                    _set_download_state(downloaded=have, total=total)
                    if progress_callback:
                        try:
                            progress_callback(have, total)
                        except Exception:
                            pass
        return True

    # Offline mode (default-on) monkey-patches sockets to refuse non-loopback
    # destinations, which would block the HuggingFace download. The model
    # download is the one legitimate, user-initiated outbound request, so lift
    # the block just for its duration. No-op if offline mode isn't active.
    try:
        from privacy.network_block import temporarily_allow_network as _allow_net
    except Exception:
        import contextlib as _ctx
        def _allow_net():
            return _ctx.nullcontext()

    # Download with resume-on-failure
    with _allow_net():
        for attempt_n in range(1, 41):
            if _cancel_event.is_set():
                _set_download_state(status="cancelled")
                return False
            try:
                if _attempt():
                    break  # completed
                else:
                    # cancelled inside _attempt
                    _set_download_state(status="cancelled")
                    return False
            except Exception as e:
                logger.warning(f"Download attempt {attempt_n} failed ({type(e).__name__}: {e}) — resuming")
                _set_download_state(status="downloading", error=f"retrying ({attempt_n})")
                time.sleep(3)
        else:
            logger.error("Model download failed after 40 retries")
            _set_download_state(status="error", error="Network error after 40 retries")
            return False

    # Verify hash BEFORE moving to final location.
    _set_download_state(status="verifying")
    try:
        if expected_sha:
            actual = _sha256_of(part)
            if actual.lower() != expected_sha.lower():
                part.unlink(missing_ok=True)
                logger.error("Downloaded model SHA-256 mismatch: expected %s, got %s.",
                             expected_sha, actual)
                _set_download_state(status="error", error="SHA-256 mismatch — download discarded")
                return False
            logger.info(f"Model SHA-256 verified: {actual}")
        else:
            logger.warning(f"No SHA-256 pin for tier '{tier}' — skipping hash verification.")

        part.replace(model_path)
        logger.info(f"Model downloaded [{tier}]: {model_path}")

        # Reset the loaded model so next call picks up the new/better tier
        global _llm, _llm_ready, _active_tier
        _llm = None
        _llm_ready = None
        _active_tier = None

        _set_download_state(status="done", tier=tier, error=None)
        return True
    except Exception as e:
        logger.error(f"Model install failed [{tier}]: {e}")
        _set_download_state(status="error", error=str(e))
        return False
