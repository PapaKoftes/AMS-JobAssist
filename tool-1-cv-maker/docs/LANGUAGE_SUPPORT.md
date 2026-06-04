# Language Support — Verified Capability vs. Intended Design

> ⚠️ **ACCURACY NOTICE (2026-06-04)** — This document was originally
> written as a design/aspiration spec. The sections below that describe
> "language packs", on-disk `~/.ams_jobassist/language_packs/*.json`
> files (~331 MB), and per-language size tables are **NOT IMPLEMENTED**.
> Those files do not exist. Detection uses Lingua + inline keyword dicts
> in `polish/language.py` — no language-pack files are downloaded or cached.
>
> **What is actually implemented:**
>
> | Capability | Reality |
> |---|---|
> | **Input detection** | ~14 languages via Lingua + hardcoded keyword dicts (exact set varies by detector config — see `CORE_LANGUAGES` in `polish/language.py`) |
> | **UI translations** | **12** locales in `TRANSLATIONS` (frontend/app.js); missing: `cs`, `hu`, `it`, `fr`, `fa` |
> | **CV output** | **German (de) + English (en) only** with polished prose; other inputs get a "native" passthrough (raw user text) with German/English section headings — NOT a translated output |
> | **Dump/gap conversation** | Full i18n only for **de** and **en**; all other languages fall back to German |
> | **Language packs on disk** | **Do not exist** |
>
> The design below remains as a record of intended future direction.
> Treat everything in §§ "On-Disk Storage", "Cache Structure", and the
> size tables as **future work**, not current capability.

---

# Language Support - 14 Core Languages (Design Document)

## Overview

The AMS JobAssist CV Maker targets **14 core languages** covering Austria's DACH region plus major immigrant populations. Detection is fully offline using Lingua; polished CV output is currently German (primary) and English (secondary).

**Implementation Date**: Week 2, Days 8-10  
**Status**: Input detection ✅ complete; Full per-language polished output 🔜 future work

---

## 14 Core Languages

### Language Families and Regions

#### Germanic Languages (2)
- **German** (de) - Primary language, AMS headquarters language
- **English** (en) - Secondary language, international standard

#### Romance Languages (2)
- **Italian** (it) - Neighbor country (South Tyrol, northern border)
- **French** (fr) - Western neighbor, European integration

#### Central European Slavic (4)
- **Polish** (pl) - Neighbor country, large immigrant population
- **Czech** (cs) - Neighbor country
- **Slovak** (sk) - Neighbor country
- **Hungarian** (hu) - Neighbor country, Finno-Ugric language group

#### Eastern European Slavic (4) - NEW FOR AUSTRIAN IMMIGRANT SUPPORT
- **Ukrainian** (uk) - NEW: Growing refugee population, humanitarian priority
- **Russian** (ru) - NEW: Significant immigrant population (~40-50k)
- **Serbian** (sr) - NEW: Former Yugoslav diaspora (~100k)
- **Bosnian** (bs) - NEW: Former Yugoslav diaspora (~50k)

#### Other Language Families (2)
- **Turkish** (tr) - NEW: Significant immigrant population (~50k)
- **Arabic** (ar) - NEW: Syrian diaspora, Middle Eastern populations (~40k)

---

## Technical Implementation

### Language Detection Engine

**Technology**: Lingua (Rust-based, 75+ languages supported)

```python
from lingua import LanguageDetectorBuilder, Language
from src.backend.polish.language import LanguageNormalizer

normalizer = LanguageNormalizer()

# Detect language
detected = normalizer.detect_language("Ich habe in Software entwickelt")
# Returns: "de"

# Get confidence scores for all 14 languages
confidence = normalizer.get_language_confidence("Mixed text mit English")
# Returns: {"de": 0.65, "en": 0.35, "it": 0.0, "pl": 0.0, ..., "ar": 0.0}
```

### Fallback Detection

When Lingua is unavailable:
1. Checks for language-specific character signals (e.g., umlauts for German)
2. Uses keyword-based detection with word boundary matching
3. Falls back to "unknown" when uncertain

### Language Normalization Pipeline

1. **Input**: User text in ANY language
2. **Detect**: Identify language automatically
3. **Normalize**: Convert to English for processing
4. **Polish**: Apply grammar, verb, skill improvements
5. **Translate**: Generate German + English + native language versions
6. **Output**: Multilingual CV data

### File Structure

```
src/backend/
├── language_packs/
│   ├── __init__.py           # Package initialization
│   └── manager.py            # LanguagePackManager (300+ lines)
│
├── polish/
│   └── language.py           # LanguageNormalizer with Lingua (600+ lines)
│
└── api/
    └── language_packs.py     # FastAPI endpoints for language management

tests/
└── test_language_14core.py   # 47+ tests covering all 14 languages
```

---

## Core Language Data

### Size and Dependencies

| Language | Code | Region | Size (MB) | Native Name |
|----------|------|--------|-----------|------------|
| German | de | Germanic | 25 | Deutsch |
| English | en | Germanic | 28 | English |
| Italian | it | Romance | 22 | Italiano |
| French | fr | Romance | 24 | Français |
| Polish | pl | Slavic | 26 | Polski |
| Czech | cs | Slavic | 23 | Čeština |
| Slovak | sk | Slavic | 21 | Slovenčina |
| Hungarian | hu | Finno-Ugric | 20 | Magyar |
| Ukrainian | uk | Slavic | 24 | Українська |
| Russian | ru | Slavic | 27 | Русский |
| Serbian | sr | Slavic | 22 | Српски |
| Bosnian | bs | Slavic | 21 | Bosanski |
| Turkish | tr | Turkic | 23 | Türkçe |
| Arabic | ar | Semitic | 26 | العربية |

**Total Core Size**: ~331 MB (pre-bundled, fully offline)

---

## API Endpoints

### GET `/api/language-packs/available`
List all available languages (core + optional)

**Response**:
```json
{
  "core": [
    {
      "code": "de",
      "name": "German",
      "native_name": "Deutsch",
      "region": "Germanic",
      "is_core": true,
      "size_mb": 25.0,
      "description": "German - primary output language"
    },
    ...
  ],
  "optional": [...],
  "total": 26
}
```

### GET `/api/language-packs/core`
List core languages only

**Response**:
```json
{
  "core_languages": ["de", "en", "it", "pl", "cs", "sk", "hu", "fr", "uk", "tr", "sr", "ru", "ar", "bs"],
  "count": 14
}
```

### GET `/api/language-packs/info/{code}`
Get detailed info about a language

**Example**: `/api/language-packs/info/uk`

**Response**:
```json
{
  "code": "uk",
  "name": "Ukrainian",
  "native_name": "Українська",
  "region": "Slavic",
  "is_core": true,
  "size_mb": 24.0,
  "description": "Ukrainian - growing immigrant population (refugee support)"
}
```

### GET `/api/language-packs/stats`
Get language pack statistics

**Response**:
```json
{
  "total_languages": 26,
  "core_languages": 14,
  "core_size_mb": 331.0,
  "available_languages": 14,
  "core_list": ["de", "en", ...],
  "available_list": ["de", "en", ...]
}
```

### GET `/api/language-packs/check/{code}`
Check if a language is available

**Response**:
```json
{
  "language_code": "uk",
  "available": true
}
```

---

## Usage Examples

### Basic Language Detection

```python
from src.backend.polish.language import LanguageNormalizer

normalizer = LanguageNormalizer()

# German text
result = normalizer.detect_language("Ich arbeite seit fünf Jahren in der Softwareentwicklung.")
# Returns: "de"

# Ukrainian text
result = normalizer.detect_language("Я працював у ІТ-компанії протягом 5 років.")
# Returns: "uk"

# Turkish text
result = normalizer.detect_language("Beş yıldır yazılım geliştirme alanında çalışıyorum.")
# Returns: "tr"
```

### Confidence Scoring

```python
# Mixed language input
text = "Ich have managed some Projekte und gelernt viel Russian und Ukrainian."
confidence = normalizer.get_language_confidence(text)

# Returns confidence scores for all 14 languages
print(confidence)
# {
#   "de": 0.45,
#   "en": 0.35,
#   "uk": 0.1,
#   "ru": 0.1,
#   "it": 0.0, ... (all others 0.0)
# }
```

### Normalization

```python
# German to English
text = "Ich habe Fähigkeiten in Python und Java."
normalized, detected = normalizer.normalize_to_language(text, target_language="en")

# Returns:
# ("I have skills in Python and Java.", "de")
# Note: Umlauts removed, German terms translated
```

---

## Testing

### Test Coverage

**File**: `tests/test_language_14core.py`

**Test Classes**:
1. `TestLanguageDetectionCore14` - Core language detection (14 tests)
2. `TestUmlautDetection` - Character-based detection
3. `TestEdgeCases` - Edge cases and unusual inputs
4. `TestLanguageConfidence` - Confidence scoring
5. `TestNormalizationToEnglish` - English normalization
6. `TestNormalizationToGerman` - German normalization
7. `TestCoreLanguageConstants` - Verify all 14 languages defined

**Total Tests**: 47+

**Run Tests**:
```bash
pytest tests/test_language_14core.py -v
```

---

## Offline Architecture

### Why Fully Offline?

1. **Privacy (Datenschutz)**: No data leaves the user's machine
2. **Speed**: No network latency for language detection
3. **Reliability**: Works without internet connection
4. **Compliance**: GDPR/DSGVO compliant, user text never transmitted

### On-Disk Storage

```
~/.ams_jobassist/
├── language_packs/
│   ├── index.json                    # Language pack metadata
│   ├── de.json                       # German language data
│   ├── en.json                       # English language data
│   ├── uk.json                       # Ukrainian language data
│   └── ... (12 more core languages)
└── cache/
    └── ... (optional downloaded languages)
```

### Cache Structure

**Index File** (`~/.ams_jobassist/language_packs/index.json`):
```json
{
  "de": {
    "code": "de",
    "name": "German",
    "downloaded": true,
    "size_mb": 25.0,
    "is_core": true,
    "cached_at": "2026-05-02T10:30:00Z"
  },
  ... (13 more languages)
}
```

---

## Integration Checklist

- [x] Language pack manager created
- [x] 14 core languages defined with metadata
- [x] Lingua-based detector implemented
- [x] Fallback keyword detection (9 language families)
- [x] Language normalization pipeline
- [x] FastAPI endpoints for language management
- [x] Comprehensive test suite (47+ tests)
- [x] Requirements updated with lingua-py
- [x] Documentation completed
- [ ] Full integration with interview engine (Days 8-10)
- [ ] Database schema updates for multilingual CV storage (Day 9)
- [ ] CV builder with multilingual output (Day 10)

---

## Next Steps

### Day 8-10 Plan (Continuation)

**Day 8**: Language Detection & Pack Manager ✅
- [x] LanguageNormalizer with Lingua
- [x] LanguagePackManager
- [x] FastAPI endpoints
- [x] Tests for all 14 languages

**Day 9**: Multilingual Processing Pipeline
- [ ] Update PolishEngine for translate pipeline
- [ ] Multilingual answer storage
- [ ] Database schema updates
- [ ] Integration with interview engine

**Day 10**: CV Building & Export
- [ ] CVBuilder with multilingual output
- [ ] MultilingualCV data model
- [ ] Export to German/English/native
- [ ] Integration testing

---

## Dependencies

**Core Dependencies**:
- `lingua-py==1.3.1` - Language detection (Rust-based, ~5-10MB binary)
- `fastapi==0.104.1` - API framework
- `pydantic==2.5.0` - Data validation

**Optional**:
- Ollama (local) - Translation when needed
- reportlab - PDF export
- python-docx - DOCX export

---

## Performance Notes

**Language Detection**:
- Lingua: ~10-50ms per text detection
- Keyword fallback: ~1-5ms per detection
- Confidence scoring: ~20-100ms per text

**Memory Usage**:
- Core languages: ~150MB total (all 14 loaded in memory)
- Per-request: ~5-10MB overhead

**Storage**:
- Cache directory: ~331MB (core languages only)
- Index file: ~2KB

---

## Support Matrix

### Input Languages (Supported)
✅ All 14 core languages + 60+ optional languages (Lingua supports 75 total)

### Output Languages
- Primary: German (de)
- Secondary: English (en)
- Tertiary: User's detected language

### Missing Coverage
- Sign languages
- Constructed languages (Esperanto, Klingon, etc.)
- Ancient/historical languages
- Right-to-left languages (partial Arabic support via Lingua)

---

## Future Enhancements

### Phase 2 (Potential)
- [ ] RTL language support improvements
- [ ] Character encoding detection
- [ ] Script detection (Cyrillic, Arabic, Greek, etc.)
- [ ] Regional variant support (de-CH, de-AT differentiation)
- [ ] Custom language packs for specific domains

### Phase 3 (Post-MVP)
- [ ] Machine translation via Ollama for real-time translation
- [ ] Language pack auto-update mechanism
- [ ] Crowdsourced language pack improvements
- [ ] Language-specific CV templates

---

**Documentation Version**: 1.0  
**Last Updated**: 2026-05-02  
**Status**: Implementation Complete (Days 8-10, Phase 1)
