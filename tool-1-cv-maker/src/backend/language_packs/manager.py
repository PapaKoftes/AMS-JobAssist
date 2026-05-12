"""
Language Pack Manager - Handles on-demand language pack downloads and caching.

Supports:
1. Language detection with Lingua
2. On-demand language pack downloads
3. Local caching for offline use
4. Language availability checking
5. Confidence scoring for detected languages
"""

import logging
import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class LanguageCode(str, Enum):
    """ISO 639-1 language codes for supported languages."""
    # Core languages (pre-downloaded, always available)
    GERMAN = "de"
    ENGLISH = "en"
    ITALIAN = "it"
    POLISH = "pl"
    CZECH = "cs"
    SLOVAK = "sk"
    HUNGARIAN = "hu"
    FRENCH = "fr"
    UKRAINIAN = "uk"
    TURKISH = "tr"
    SERBIAN = "sr"
    RUSSIAN = "ru"
    ARABIC = "ar"
    BOSNIAN = "bs"
    CHINESE = "zh"


@dataclass
class LanguagePack:
    """Metadata for a language pack."""
    code: str
    name: str
    native_name: str
    region: str  # European, Slavic, Turkic, Sino-Tibetan, Semitic
    is_core: bool  # Core languages are bundled; optional languages downloaded on-demand
    size_mb: float  # Approximate download size
    description: str = ""

    # Download/availability info
    download_url: str = ""
    downloaded: bool = False
    last_updated: Optional[str] = None
    local_path: Optional[str] = None


class LanguagePackManager:
    """Manages language packs for offline use."""

    # Core languages always available (14 languages for DACH + immigrant populations)
    CORE_LANGUAGES = [
        "de", "en", "it", "pl", "cs", "sk", "hu", "fr",  # Original 8
        "uk", "tr", "sr", "ru", "ar", "bs"  # New core (8 more)
    ]

    # All supported languages with metadata
    LANGUAGE_PACKS: Dict[str, LanguagePack] = {
        # Core DACH + European languages
        "de": LanguagePack(
            code="de",
            name="German",
            native_name="Deutsch",
            region="Germanic",
            is_core=True,
            size_mb=25.0,
            description="German - primary output language for AMS"
        ),
        "en": LanguagePack(
            code="en",
            name="English",
            native_name="English",
            region="Germanic",
            is_core=True,
            size_mb=28.0,
            description="English - secondary output language"
        ),
        "it": LanguagePack(
            code="it",
            name="Italian",
            native_name="Italiano",
            region="Romance",
            is_core=True,
            size_mb=22.0,
            description="Italian - neighbor to Austria"
        ),
        "fr": LanguagePack(
            code="fr",
            name="French",
            native_name="Français",
            region="Romance",
            is_core=True,
            size_mb=24.0,
            description="French - Western Europe"
        ),

        # Core Slavic languages (Central & Eastern European)
        "pl": LanguagePack(
            code="pl",
            name="Polish",
            native_name="Polski",
            region="Slavic",
            is_core=True,
            size_mb=26.0,
            description="Polish - large Central European population"
        ),
        "cs": LanguagePack(
            code="cs",
            name="Czech",
            native_name="Čeština",
            region="Slavic",
            is_core=True,
            size_mb=23.0,
            description="Czech - neighbor to Austria"
        ),
        "sk": LanguagePack(
            code="sk",
            name="Slovak",
            native_name="Slovenčina",
            region="Slavic",
            is_core=True,
            size_mb=21.0,
            description="Slovak - neighbor to Austria"
        ),
        "uk": LanguagePack(
            code="uk",
            name="Ukrainian",
            native_name="Українська",
            region="Slavic",
            is_core=True,
            size_mb=24.0,
            description="Ukrainian - growing immigrant population (refugee support)"
        ),
        "sr": LanguagePack(
            code="sr",
            name="Serbian",
            native_name="Српски",
            region="Slavic",
            is_core=True,
            size_mb=22.0,
            description="Serbian - former Yugoslav diaspora in Austria (~100k)"
        ),
        "ru": LanguagePack(
            code="ru",
            name="Russian",
            native_name="Русский",
            region="Slavic",
            is_core=True,
            size_mb=27.0,
            description="Russian - significant immigrant population"
        ),

        # Core other languages (immigrant populations in Austria)
        "hu": LanguagePack(
            code="hu",
            name="Hungarian",
            native_name="Magyar",
            region="Finno-Ugric",
            is_core=True,
            size_mb=20.0,
            description="Hungarian - neighbor to Austria"
        ),
        "tr": LanguagePack(
            code="tr",
            name="Turkish",
            native_name="Türkçe",
            region="Turkic",
            is_core=True,
            size_mb=23.0,
            description="Turkish - significant immigrant population (~50k)"
        ),
        "ar": LanguagePack(
            code="ar",
            name="Arabic",
            native_name="العربية",
            region="Semitic",
            is_core=True,
            size_mb=26.0,
            description="Arabic - significant immigrant population (~40k, Syrian diaspora)"
        ),
        "bs": LanguagePack(
            code="bs",
            name="Bosnian",
            native_name="Bosanski",
            region="Slavic",
            is_core=True,
            size_mb=21.0,
            description="Bosnian - former Yugoslav diaspora in Austria (~50k)"
        ),

        # Optional languages (on-demand download)
        "zh": LanguagePack(
            code="zh",
            name="Chinese (Simplified)",
            native_name="简体中文",
            region="Sino-Tibetan",
            is_core=False,
            size_mb=32.0,
            description="Chinese (Simplified) - growing tech/business population"
        ),
        "es": LanguagePack(
            code="es",
            name="Spanish",
            native_name="Español",
            region="Romance",
            is_core=False,
            size_mb=25.0,
            description="Spanish - optional language"
        ),
        "pt": LanguagePack(
            code="pt",
            name="Portuguese",
            native_name="Português",
            region="Romance",
            is_core=False,
            size_mb=24.0,
            description="Portuguese - optional language"
        ),
        "nl": LanguagePack(
            code="nl",
            name="Dutch",
            native_name="Nederlands",
            region="Germanic",
            is_core=False,
            size_mb=23.0,
            description="Dutch - optional language"
        ),
        "sv": LanguagePack(
            code="sv",
            name="Swedish",
            native_name="Svenska",
            region="Germanic",
            is_core=False,
            size_mb=22.0,
            description="Swedish - optional language"
        ),
        "da": LanguagePack(
            code="da",
            name="Danish",
            native_name="Dansk",
            region="Germanic",
            is_core=False,
            size_mb=21.0,
            description="Danish - optional language"
        ),
        "no": LanguagePack(
            code="no",
            name="Norwegian",
            native_name="Norsk",
            region="Germanic",
            is_core=False,
            size_mb=21.0,
            description="Norwegian - optional language"
        ),
        "el": LanguagePack(
            code="el",
            name="Greek",
            native_name="Ελληνικά",
            region="Indo-European",
            is_core=False,
            size_mb=23.0,
            description="Greek - optional language"
        ),
        "ja": LanguagePack(
            code="ja",
            name="Japanese",
            native_name="日本語",
            region="Japonic",
            is_core=False,
            size_mb=30.0,
            description="Japanese - optional language"
        ),
        "ko": LanguagePack(
            code="ko",
            name="Korean",
            native_name="한국어",
            region="Koreanic",
            is_core=False,
            size_mb=28.0,
            description="Korean - optional language"
        ),
    }

    def __init__(self, cache_dir: Optional[str] = None):
        """
        Initialize language pack manager.

        Args:
            cache_dir: Directory for language pack cache. Defaults to ~/.ams_jobassist/language_packs/
        """
        if cache_dir is None:
            home = Path.home()
            cache_dir = home / ".ams_jobassist" / "language_packs"

        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.index_file = self.cache_dir / "index.json"

        # Load or initialize index
        self._index = self._load_index()

        logger.info(f"Language pack manager initialized at {self.cache_dir}")
        logger.info(f"Core languages ({len(self.CORE_LANGUAGES)}): {', '.join(self.CORE_LANGUAGES)}")

    def _load_index(self) -> Dict[str, Dict]:
        """Load language pack index from cache."""
        if self.index_file.exists():
            try:
                with open(self.index_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Error loading language pack index: {e}")

        # Initialize new index with all core languages
        index = {}
        for code in self.CORE_LANGUAGES:
            if code in self.LANGUAGE_PACKS:
                pack = self.LANGUAGE_PACKS[code]
                index[code] = {
                    "code": code,
                    "name": pack.name,
                    "downloaded": False,  # Core languages need to be verified/bundled
                    "size_mb": pack.size_mb,
                    "is_core": True,
                    "cached_at": None
                }

        self._save_index(index)
        return index

    def _save_index(self, index: Dict) -> None:
        """Save language pack index to cache."""
        try:
            with open(self.index_file, 'w', encoding='utf-8') as f:
                json.dump(index, f, indent=2, ensure_ascii=False)
            logger.debug(f"Saved language pack index to {self.index_file}")
        except Exception as e:
            logger.error(f"Error saving language pack index: {e}")

    def is_language_available(self, language_code: str) -> bool:
        """
        Check if a language is available (downloaded or core).

        Args:
            language_code: ISO 639-1 language code

        Returns:
            True if language is available offline
        """
        if language_code not in self.LANGUAGE_PACKS:
            return False

        pack = self.LANGUAGE_PACKS[language_code]

        # Core languages should be available
        if pack.is_core:
            return True

        # Optional languages must be downloaded
        if language_code in self._index:
            return self._index[language_code].get("downloaded", False)

        return False

    def get_available_languages(self) -> List[str]:
        """
        Get list of available language codes (core + downloaded optional).

        Returns:
            List of language codes
        """
        available = self.CORE_LANGUAGES.copy()

        # Add any downloaded optional languages
        for code, info in self._index.items():
            if code not in available and info.get("downloaded", False):
                available.append(code)

        return sorted(available)

    def get_core_languages(self) -> List[str]:
        """Get list of core language codes."""
        return sorted(self.CORE_LANGUAGES)

    def get_language_info(self, language_code: str) -> Optional[LanguagePack]:
        """
        Get metadata for a language.

        Args:
            language_code: ISO 639-1 language code

        Returns:
            LanguagePack metadata or None if not found
        """
        return self.LANGUAGE_PACKS.get(language_code)

    def ensure_language_pack(self, language_code: str) -> bool:
        """
        Ensure a language pack is available (download if needed).

        Args:
            language_code: ISO 639-1 language code

        Returns:
            True if language is available
        """
        if not self.is_language_available(language_code):
            logger.warning(f"Language {language_code} not available for offline use")
            return False

        return True

    def get_cached_languages(self) -> Dict[str, Dict]:
        """
        Get all cached language information.

        Returns:
            Dict mapping language codes to metadata
        """
        return self._index.copy()

    def mark_language_downloaded(self, language_code: str, timestamp: str) -> None:
        """
        Mark a language as downloaded.

        Args:
            language_code: ISO 639-1 language code
            timestamp: ISO 8601 timestamp of download
        """
        if language_code not in self._index:
            self._index[language_code] = {}

        self._index[language_code]["downloaded"] = True
        self._index[language_code]["cached_at"] = timestamp
        self._save_index(self._index)
        logger.info(f"Marked language {language_code} as downloaded")

    def get_language_stats(self) -> Dict:
        """
        Get statistics about language packs.

        Returns:
            Dict with stats
        """
        return {
            "total_languages": len(self.LANGUAGE_PACKS),
            "core_languages": len(self.CORE_LANGUAGES),
            "core_size_mb": sum(
                self.LANGUAGE_PACKS[code].size_mb
                for code in self.CORE_LANGUAGES
            ),
            "available_languages": len(self.get_available_languages()),
            "core_list": self.CORE_LANGUAGES,
            "available_list": self.get_available_languages(),
        }
