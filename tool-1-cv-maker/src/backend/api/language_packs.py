"""
Language Packs API - Endpoints for managing language packs.

Provides:
1. /api/language-packs/available - List available languages
2. /api/language-packs/core - List core languages
3. /api/language-packs/info/{code} - Get info about a specific language
4. /api/language-packs/stats - Get language pack statistics
"""

import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional
from language_packs.manager import LanguagePackManager

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/language-packs", tags=["language-packs"])

# Module-level singleton (initialized once, immutable after)
_manager: Optional[LanguagePackManager] = None


def get_language_pack_manager() -> LanguagePackManager:
    """Get or lazily initialize language pack manager singleton."""
    global _manager
    if _manager is None:
        _manager = LanguagePackManager()
    return _manager


# === Response Models ===

class LanguageInfo(BaseModel):
    """Language metadata."""
    code: str
    name: str
    native_name: str
    region: str
    is_core: bool
    size_mb: float
    description: str


class LanguagePackStats(BaseModel):
    """Language pack statistics."""
    total_languages: int
    core_languages: int
    core_size_mb: float
    available_languages: int
    core_list: List[str]
    available_list: List[str]


class AvailableLanguages(BaseModel):
    """List of available languages."""
    core: List[LanguageInfo]
    optional: List[LanguageInfo]
    total: int


# === Endpoints ===

@router.get("/available", response_model=AvailableLanguages)
async def get_available_languages():
    """
    Get all available languages (core and optional).

    Returns:
        Dict with core and optional languages
    """
    try:
        manager = get_language_pack_manager()
        available = manager.get_available_languages()

        core_langs = []
        optional_langs = []

        for code, pack in manager.LANGUAGE_PACKS.items():
            lang_info = LanguageInfo(
                code=pack.code,
                name=pack.name,
                native_name=pack.native_name,
                region=pack.region,
                is_core=pack.is_core,
                size_mb=pack.size_mb,
                description=pack.description
            )

            if pack.is_core:
                core_langs.append(lang_info)
            else:
                optional_langs.append(lang_info)

        return AvailableLanguages(
            core=core_langs,
            optional=optional_langs,
            total=len(manager.LANGUAGE_PACKS)
        )

    except Exception as e:
        logger.error(f"Error getting available languages: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/core", response_model=Dict[str, List[str]])
async def get_core_languages():
    """
    Get list of core languages (14 languages, always available offline).

    Returns:
        List of ISO 639-1 language codes
    """
    try:
        manager = get_language_pack_manager()
        return {
            "core_languages": manager.get_core_languages(),
            "count": len(manager.CORE_LANGUAGES)
        }
    except Exception as e:
        logger.error(f"Error getting core languages: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/info/{language_code}", response_model=LanguageInfo)
async def get_language_info(language_code: str):
    """
    Get detailed information about a specific language.

    Args:
        language_code: ISO 639-1 language code (e.g., 'de', 'en', 'uk')

    Returns:
        Language metadata
    """
    try:
        manager = get_language_pack_manager()
        pack = manager.get_language_info(language_code)

        if not pack:
            raise HTTPException(
                status_code=404,
                detail=f"Language '{language_code}' not found"
            )

        return LanguageInfo(
            code=pack.code,
            name=pack.name,
            native_name=pack.native_name,
            region=pack.region,
            is_core=pack.is_core,
            size_mb=pack.size_mb,
            description=pack.description
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting language info for {language_code}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats", response_model=LanguagePackStats)
async def get_language_stats():
    """
    Get statistics about language packs.

    Returns:
        Language pack statistics including total, core, available counts
    """
    try:
        manager = get_language_pack_manager()
        stats = manager.get_language_stats()

        return LanguagePackStats(
            total_languages=stats["total_languages"],
            core_languages=stats["core_languages"],
            core_size_mb=stats["core_size_mb"],
            available_languages=stats["available_languages"],
            core_list=stats["core_list"],
            available_list=stats["available_list"]
        )

    except Exception as e:
        logger.error(f"Error getting language stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/check/{language_code}", response_model=Dict[str, bool])
async def check_language_available(language_code: str):
    """
    Check if a language is available for offline use.

    Args:
        language_code: ISO 639-1 language code

    Returns:
        Dict with 'available' boolean flag
    """
    try:
        manager = get_language_pack_manager()
        available = manager.is_language_available(language_code)

        return {
            "language_code": language_code,
            "available": available
        }

    except Exception as e:
        logger.error(f"Error checking language availability: {e}")
        raise HTTPException(status_code=500, detail=str(e))


