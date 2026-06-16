"""
Shared human-readable labels for AI prompts — single source of truth.

Previously `_LANG_NAMES` and the category-context map were copy-pasted in both
local_llm.py and ollama.py and had already drifted (local_llm listed 12 languages,
ollama 16). Keeping one copy here prevents that.
"""

# Language code → German name, used to phrase the input language in prompts.
LANG_NAMES = {
    "de": "Deutsch", "en": "Englisch", "tr": "Türkisch", "ar": "Arabisch",
    "bs": "Bosnisch", "hr": "Kroatisch", "sr": "Serbisch", "pl": "Polnisch",
    "uk": "Ukrainisch", "ru": "Russisch", "ro": "Rumänisch", "sk": "Slowakisch",
    "cs": "Tschechisch", "hu": "Ungarisch", "it": "Italienisch", "fr": "Französisch",
}

# CV section/category → German context phrase, used to ground LLM prompts.
CATEGORY_CONTEXT = {
    "experience": "Berufserfahrung oder Arbeitstätigkeit",
    "skills":     "Fähigkeiten und Kenntnisse",
    "background": "Ausbildung und Hintergrund",
    "motivation": "Motivation und Karriereziele",
    "training":   "Weiterbildung und Kurse",
    "projects":   "Projekte und Leistungen",
    "identity":   "Persönliche Angaben",
}
