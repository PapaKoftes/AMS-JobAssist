"""
Language Packs - Support for 14+ languages including all major Austrian immigrant populations.

Core Languages (14):
- Germanic: German, English, Dutch
- Romance: Italian, French
- Slavic: Polish, Czech, Slovak, Ukrainian, Serbian, Russian, Bosnian
- Turkic: Turkish
- Semitic: Arabic
- Finno-Ugric: Hungarian

Optional Languages (on-demand):
- Chinese (Simplified & Traditional)
- Spanish, Portuguese
- Scandinavian: Swedish, Danish, Norwegian
- Greek, Japanese, Korean
"""

from .manager import LanguagePackManager, LanguagePack, LanguageCode

__all__ = [
    "LanguagePackManager",
    "LanguagePack",
    "LanguageCode",
]
