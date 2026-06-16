"""
FastAPI endpoints for interview flow.

Handles:
- Starting interviews
- Getting next questions
- Submitting answers
- Skipping questions
- Resuming interviews
- Getting interview status
"""

import logging
import contextvars
from fastapi import APIRouter, HTTPException, Request, Depends
from pydantic import BaseModel, field_validator
from typing import Optional, Dict

from db import DatabaseManager
from interview.engine import InterviewEngine
from interview.autosave import AutosaveManager
from cv.builder import CVBuilder
from cv.storage import CVStorage

# ContextVar that holds the active session_id for the current request thread/task.
# Set at the start of each endpoint, read by the log filter below.
_current_session_id: contextvars.ContextVar[Optional[int]] = contextvars.ContextVar(
    "_current_session_id", default=None
)


class _SessionIdFilter(logging.Filter):
    """Inject session_id into every log record emitted during a request."""

    def filter(self, record: logging.LogRecord) -> bool:
        sid = _current_session_id.get(None)
        record.session_id = sid if sid is not None else "-"
        return True


# Attach the filter to the root logger once so ALL loggers in this process
# automatically get session_id in their records.  Formatters that include
# %(session_id)s will show it; others silently ignore the extra attribute.
_sid_filter = _SessionIdFilter()
logging.getLogger().addFilter(_sid_filter)

try:
    from ai.ollama import get_status as ai_get_status, reset_detection as ai_reset
    _AI_MODULE = True
except ImportError:
    _AI_MODULE = False
    def ai_get_status(): return {"ollama_available": False, "mode": "Regelbasiert", "model": None}
    def ai_reset(): pass

logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter(prefix="/api/interview", tags=["interview"])

# Module-level instances (set once at startup via init_interview_routes)
_engine: Optional[InterviewEngine] = None
_autosave: Optional[AutosaveManager] = None
_builder: Optional[CVBuilder] = None
_storage: Optional[CVStorage] = None


def init_interview_routes(db: DatabaseManager):
    """Initialize interview routes with database manager.

    Called once at application startup from app.py lifespan.
    """
    global _engine, _autosave, _builder, _storage
    _engine = InterviewEngine(db)
    _autosave = AutosaveManager(db)
    _builder = CVBuilder(db)
    _storage = CVStorage(db)
    logger.info("Interview routes initialized")


def _get_engine() -> InterviewEngine:
    """Dependency: return the interview engine or raise 503."""
    if _engine is None:
        raise HTTPException(status_code=503, detail="Interview engine not initialized")
    return _engine


def _get_autosave() -> AutosaveManager:
    """Dependency: return the autosave manager or raise 503."""
    if _autosave is None:
        raise HTTPException(status_code=503, detail="Autosave not initialized")
    return _autosave


def _get_builder() -> CVBuilder:
    """Dependency: return the CV builder or raise 503."""
    if _builder is None:
        raise HTTPException(status_code=503, detail="CV builder not initialized")
    return _builder


def _get_storage() -> CVStorage:
    """Dependency: return the CV storage or raise 503."""
    if _storage is None:
        raise HTTPException(status_code=503, detail="CV storage not initialized")
    return _storage


# ============================================================================
# Request/Response Models (with validation)
# ============================================================================

VALID_INTERVIEW_PATHS = {"unemployed", "career-switch", "student", "pause", "other"}


class StartInterviewRequest(BaseModel):
    """Request to start a new interview."""
    user_id: str
    interview_path: str  # unemployed, career-switch, student, pause, other
    language: str = "de"
    user_native_language: Optional[str] = None
    # DSGVO Art. 7 — explicit, demonstrable consent captured at start.
    consent_given: bool = False
    consent_text_version: str = ""

    @field_validator("user_id")
    @classmethod
    def user_id_not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v or len(v) > 255:
            raise ValueError("user_id must be 1-255 characters")
        return v

    @field_validator("interview_path")
    @classmethod
    def valid_path(cls, v: str) -> str:
        if v not in VALID_INTERVIEW_PATHS:
            raise ValueError(f"interview_path must be one of: {', '.join(sorted(VALID_INTERVIEW_PATHS))}")
        return v


class SubmitAnswerRequest(BaseModel):
    """Request to submit an answer to a question."""
    session_id: int
    question_id: str
    answer_text: str

    @field_validator("answer_text")
    @classmethod
    def answer_not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("answer_text cannot be empty")
        if len(v) > 10000:
            raise ValueError("answer_text exceeds 10000 character limit")
        return v


class SkipQuestionRequest(BaseModel):
    """Request to skip a question."""
    session_id: int
    question_id: str


class ResumeInterviewRequest(BaseModel):
    """Request to resume an interview."""
    session_id: int


class PreviewAnswerRequest(BaseModel):
    """Polish a raw answer for live preview — no save, no session required."""
    answer_text: str
    category: str = "experience"
    language: str = ""   # Optional ISO-639-1 hint from the UI language picker

    @field_validator("answer_text")
    @classmethod
    def answer_not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("answer_text cannot be empty")
        if len(v) > 10000:
            raise ValueError("answer_text too long")
        return v


# ============================================================================
# Endpoints
# ============================================================================

@router.post("/start")
async def start_interview(
    request: StartInterviewRequest,
    engine: InterviewEngine = Depends(_get_engine),
) -> Dict:
    """
    Start a new interview session.

    Args:
        user_id: Unique identifier for the user
        interview_path: One of: unemployed, career-switch, student, pause, other
        language: Interview language (default: de)
        user_native_language: Optional native language code (ISO 639-1)

    Returns:
        Dict with session_id, first_question, and progress info
    """
    try:
        logger.info(f"Starting interview: user={request.user_id}, path={request.interview_path}")

        # DSGVO Art. 7: processing requires demonstrable consent. Refuse to start
        # (and to store any answers) without it — fail closed, not open.
        if not request.consent_given:
            raise HTTPException(
                status_code=403,
                detail="Einwilligung erforderlich, um den Lebenslauf zu erstellen (DSGVO Art. 7).",
            )

        result = engine.start_interview(
            user_id=request.user_id,
            interview_path=request.interview_path,
            language=request.language,
            user_native_language=request.user_native_language,
        )

        # Persist a demonstrable consent record (who/when/which text/language).
        try:
            sid = result.get("session_id") if isinstance(result, dict) else None
            if sid is not None:
                engine.db.execute_update(
                    """INSERT INTO consent_records
                       (session_id, user_id, consent_given, consent_text_version, language)
                       VALUES (?, ?, 1, ?, ?)""",
                    (sid, request.user_id, request.consent_text_version or "v1", request.language),
                )
        except Exception as _ce:
            logger.warning(f"consent record not persisted (non-fatal): {_ce}")

        return {
            "status": "success",
            "data": result
        }

    except HTTPException:
        raise
    except ValueError as e:
        logger.warning(f"Invalid interview request: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error starting interview: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to start interview")


@router.get("/next-question/{session_id}")
async def get_next_question(
    session_id: int,
    engine: InterviewEngine = Depends(_get_engine),
) -> Dict:
    """
    Get the next question in the interview.

    Args:
        session_id: Current session ID

    Returns:
        Dict with next question and progress info, or completion status
    """
    _current_session_id.set(session_id)
    try:
        result = engine.get_next_question(str(session_id))

        if result.get("status") == "complete":
            return {
                "status": "complete",
                "data": result
            }

        return {
            "status": "success",
            "data": result
        }

    except ValueError as e:
        logger.warning(f"Session not found: {e}")
        raise HTTPException(status_code=404, detail="Session not found")
    except Exception as e:
        logger.error(f"Error getting next question: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to get next question")


@router.post("/submit-answer")
def submit_answer(
    request: SubmitAnswerRequest,
    engine: InterviewEngine = Depends(_get_engine),
) -> Dict:
    """
    Submit an answer to a question.

    Validates answer length and may trigger re-ask if too weak.
    """
    _current_session_id.set(request.session_id)
    try:
        logger.info(f"Submitting answer: session={request.session_id}, question={request.question_id}")

        result = engine.submit_answer(
            session_id=str(request.session_id),
            question_id=request.question_id,
            answer_text=request.answer_text
        )

        return {
            "status": "success",
            "data": result
        }

    except ValueError as e:
        logger.warning(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error submitting answer: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to submit answer")


@router.post("/skip-question")
async def skip_question(
    request: SkipQuestionRequest,
    engine: InterviewEngine = Depends(_get_engine),
) -> Dict:
    """
    Skip a question and get the next one.
    """
    _current_session_id.set(request.session_id)
    try:
        logger.info(f"Skipping question: session={request.session_id}, question={request.question_id}")

        result = engine.skip_question(
            session_id=str(request.session_id),
            question_id=request.question_id
        )

        if result.get("status") == "complete":
            return {
                "status": "complete",
                "data": result
            }

        return {
            "status": "success",
            "data": result
        }

    except ValueError as e:
        logger.warning(f"Skip error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error skipping question: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to skip question")


@router.post("/resume")
async def resume_interview(
    request: ResumeInterviewRequest,
    engine: InterviewEngine = Depends(_get_engine),
) -> Dict:
    """
    Resume an interview that was paused.

    Uses crash recovery to restore session to consistent state.
    """
    _current_session_id.set(request.session_id)
    try:
        logger.info(f"Resuming interview: session={request.session_id}")

        result = engine.resume_interview(str(request.session_id))

        return {
            "status": "success",
            "data": result
        }

    except ValueError as e:
        logger.warning(f"Resume error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error resuming interview: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to resume interview")


@router.get("/status/{session_id}")
async def get_interview_status(
    session_id: int,
    engine: InterviewEngine = Depends(_get_engine),
) -> Dict:
    """
    Get current status of an interview session.
    """
    try:
        result = engine.get_interview_status(str(session_id))

        return {
            "status": "success",
            "data": result
        }

    except ValueError as e:
        logger.warning(f"Session not found: {e}")
        raise HTTPException(status_code=404, detail="Session not found")
    except Exception as e:
        logger.error(f"Error getting interview status: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to get interview status")


@router.get("/autosave-status/{session_id}")
async def get_autosave_status(
    session_id: int,
    autosave: AutosaveManager = Depends(_get_autosave),
) -> Dict:
    """
    Get autosave status for a session.
    """
    try:
        result = autosave.get_autosave_status(session_id)

        return {
            "status": "success",
            "data": result
        }

    except Exception as e:
        logger.error(f"Error getting autosave status: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to get autosave status")


@router.post("/preview")
def preview_answer(
    request: PreviewAnswerRequest,
    engine: InterviewEngine = Depends(_get_engine),
) -> Dict:
    """
    Polish a raw answer for live preview without saving it.

    Called on every keystroke (debounced) to show the user how their
    rough text will look on their CV before they submit.

    Args:
        answer_text: Raw text the user is currently typing
        category: Question category (default: experience)

    Returns:
        Dict with polished_text (English version for display)
    """
    try:
        # polish_answer now handles language detection and German verb enforcement
        result = engine.polish.polish_answer(
            request.answer_text,
            request.category,
            hint_language=request.language,
        )
        qs = result.get("quality_score")
        score = qs.overall_score if hasattr(qs, "overall_score") else 0.0
        detected_lang = result.get("detected_language", request.language or "de")
        changes = result.get("changes", [])[:5]
        suggestions = result.get("suggestions", [])[:2]

        # Quality labels — keyed by language, frontend can also override these
        _quality_labels = {
            "de": ("Sehr gut — bereit für Ihren Lebenslauf", "Gut — noch ein Detail macht es besser", "Guter Anfang — mehr Detail hilft", "Mehr Detail wäre hilfreich"),
            "en": ("Great — ready for your CV", "Good — one more detail makes it better", "Good start — more detail helps", "More detail would help"),
            "tr": ("Harika — CV'niz için hazır", "İyi — bir detay daha daha iyi yapar", "İyi başlangıç — daha fazla ayrıntı yardımcı olur", "Daha fazla ayrıntı yardımcı olur"),
            "pl": ("Świetnie — gotowe do CV", "Dobrze — jeden szczegół uczyni to lepszym", "Dobry start — więcej szczegółów pomoże", "Więcej szczegółów by pomogło"),
            "ro": ("Excelent — gata pentru CV", "Bine — un detaliu mai mult ar ajuta", "Start bun — mai multe detalii ajută", "Mai multe detalii ar ajuta"),
            "uk": ("Чудово — готово для резюме", "Добре — ще одна деталь покращить", "Гарний початок — більше деталей", "Більше деталей допоможе"),
            "ru": ("Отлично — готово для резюме", "Хорошо — ещё одна деталь улучшит", "Хорошее начало — больше деталей", "Больше деталей поможет"),
            "ar": ("ممتاز — جاهز للسيرة الذاتية", "جيد — تفصيل واحد يجعله أفضل", "بداية جيدة — مزيد من التفاصيل يساعد", "مزيد من التفاصيل سيساعد"),
            "bs": ("Odlično — spremo za CV", "Dobro — još jedan detalj poboljšava", "Dobar početak — više detalja pomaže", "Više detalja bi pomoglo"),
            "hr": ("Odlično — spremo za životopis", "Dobro — još jedan detalj poboljšava", "Dobar početak — više detalja pomaže", "Više detalja bi pomoglo"),
            "sr": ("Odlično — spremo za CV", "Dobro — još jedan detalj poboljšava", "Dobar početak — više detalja pomaže", "Više detalja bi pomoglo"),
            "sk": ("Výborne — pripravené pre životopis", "Dobre — jeden detail to zlepší", "Dobrý štart — viac detailov pomôže", "Viac detailov by pomohlo"),
        }
        _lang = request.language if request.language in _quality_labels else "de"
        _ql = _quality_labels[_lang]
        if score >= 0.75:
            quality_label = _ql[0]
        elif score >= 0.5:
            quality_label = _ql[1]
        elif score >= 0.25:
            quality_label = _ql[2]
        else:
            quality_label = _ql[3]

        # polish_answer already returns the language-appropriate polished text
        # (German verbs for DE input, English verbs for EN, etc.) — no round-trip needed
        display_text = result.get("polished_text", request.answer_text)

        return {
            "status": "success",
            "data": {
                "polished_text": display_text,
                "quality_score": score,
                "quality_label": quality_label,
                "detected_language": detected_lang,
                "changes": changes,
                "suggestions": suggestions,
            }
        }
    except Exception as e:
        logger.warning(f"Preview polish error (non-fatal): {e}")
        return {
            "status": "success",
            "data": {"polished_text": request.answer_text, "quality_score": 0.0}
        }


class FollowUpRequest(BaseModel):
    """Request a follow-up probe for a just-submitted answer."""
    session_id: int
    question_id: str
    answer_text: str
    language: str = "de"


@router.post("/follow-up")
async def get_follow_up(
    request: FollowUpRequest,
    engine: InterviewEngine = Depends(_get_engine),
) -> Dict:
    """
    Generate one targeted follow-up question for a just-submitted answer.

    Reads the session's target_job (if any) to align probes.
    Returns null follow_up when no probe is needed (answer is sufficient).
    """
    try:
        session = engine.db.get_session(str(request.session_id))
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        # Retrieve target job if already answered
        answers = engine.db.get_session_answers(str(request.session_id))
        target_job = answers.get("id_target_job", "")

        follow_up = _generate_follow_up(
            question_id=request.question_id,
            answer_text=request.answer_text,
            target_job=target_job,
            language=request.language,
        )
        return {"status": "success", "data": {"follow_up": follow_up}}
    except HTTPException:
        raise
    except Exception as e:
        logger.warning(f"Follow-up generation failed (non-fatal): {e}")
        return {"status": "success", "data": {"follow_up": None}}


def _generate_follow_up(
    question_id: str,
    answer_text: str,
    target_job: str = "",
    language: str = "de",
) -> Optional[str]:
    """
    Follow-up probe generator — AI-first with rule-based fallback.

    Tries local LLM for a personalised, context-aware probe.
    Falls back to rule-based probes when model is not available.
    Returns None when the answer is already detailed enough.
    """
    words = answer_text.strip().split()
    word_count = len(words)
    lower = answer_text.lower()

    # Answer is already detailed enough — don't press further
    if word_count >= 25:
        return None

    # Try AI follow-up first (non-blocking: catches all exceptions)
    try:
        from ai.local_llm import is_ready as _ready, chat as _chat
        if _ready():
            target_clause = f" Zielberuf: {target_job}." if target_job else ""
            prompt_sys = (
                "Du bist ein freundlicher Interviewleiter bei AMS Österreich. "
                "Stelle EINE kurze, ermutigende Nachfrage (max. 12 Wörter) auf "
                f"{'Deutsch' if language == 'de' else 'Englisch'}."
                " Nie wertend, immer konkret. Nur die Frage, keine Einleitung."
            )
            prompt_usr = f"Antwort des Teilnehmers:{target_clause} \"{answer_text[:300]}\""
            result = _chat(prompt_sys, prompt_usr, max_tokens=60)
            if result and 3 <= len(result.split()) <= 20:
                result = result.strip().strip('"\'').rstrip()
                # Only accept a genuine, on-topic QUESTION. The 1.5B model often
                # returns a statement ("Sei nicht zu ehrlich zu dir selbst") that
                # the old code force-turned into a fake question with a trailing
                # "?". Require it to naturally end with "?" AND contain a German/
                # English question word; otherwise fall through to the curated
                # rule-based probes, which are concrete and always on-topic.
                _qwords = ("wie", "was", "welche", "welcher", "welches", "wann",
                           "warum", "wo", "wer", "womit", "wofür", "what", "how",
                           "which", "when", "why", "where", "who")
                _lower = result.lower()
                is_question = result.endswith("?") and any(w in _lower for w in _qwords)
                if is_question:
                    return result
                # else: not a real question — use rule-based probe below
    except Exception:
        pass  # Fall through to rule-based

    # Probes keyed by question category/id prefix
    _probes: dict = {
        "de": {
            "background": [
                "Was haben Sie dabei konkret gelernt oder gemacht?",
                "Haben Sie besondere Fähigkeiten oder Zertifikate dabei erworben?",
            ],
            "experience": [
                f"Was haben Sie dort gemacht — was wäre nützlich für {target_job}?" if target_job else "Was waren Ihre wichtigsten Aufgaben dabei?",
                "Welche Werkzeuge oder Maschinen haben Sie dabei verwendet?",
                "Haben Sie dabei mit Kunden, Kollegen oder alleine gearbeitet?",
            ],
            "skills": [
                f"Welche dieser Fähigkeiten wäre besonders hilfreich für {target_job}?" if target_job else "In welchen Programmen oder Werkzeugen sind Sie besonders geübt?",
                "Haben Sie das in einem Job oder privat gelernt?",
            ],
            "motivation": [
                f"Was interessiert Sie an {target_job} am meisten?" if target_job else "Was interessiert Sie an dieser Stelle am meisten?",
                "Was können Sie in dieser Stelle besonders gut einbringen?",
            ],
            "training": [
                "Wann haben Sie das abgeschlossen und wo?",
                f"Hat Ihnen dieser Kurs für {target_job} geholfen?" if target_job else "Hat Ihnen dieser Kurs bei der Arbeit geholfen?",
            ],
        },
        "en": {
            "background": [
                "What specifically did you learn or do there?",
                "Did you gain any skills or certifications?",
            ],
            "experience": [
                f"What tasks there would help in {target_job}?" if target_job else "What were your main tasks?",
                "What tools or equipment did you use?",
                "Did you work with customers, colleagues, or on your own?",
            ],
            "skills": [
                f"Which of these skills would be most useful for {target_job}?" if target_job else "Which programs or tools are you most comfortable with?",
                "Did you learn that at work or on your own?",
            ],
            "motivation": [
                f"What interests you most about {target_job}?" if target_job else "What interests you most about this kind of work?",
                "What do you feel you'd bring to this role?",
            ],
            "training": [
                "When did you complete it and where?",
                f"Did that course help you towards {target_job}?" if target_job else "Did that course help you in your work?",
            ],
        },
    }

    lang = language if language in _probes else "de"
    probes_for_lang = _probes[lang]

    # Pick category from question_id patterns.
    # Convention: questions ending in _01 = background, _05 = skills,
    # _06 = training, _07 = motivation (consistent across all 5 paths).
    category = "experience"
    if question_id.endswith("_01") or question_id == "background":
        category = "background"
    elif "skill" in question_id or question_id.endswith("_05"):
        category = "skills"
    elif "motivation" in question_id or question_id.endswith("_07") or question_id == "id_target_job":
        category = "motivation"
    elif "training" in question_id or question_id.endswith("_06"):
        category = "training"

    probes = probes_for_lang.get(category, probes_for_lang["experience"])

    # Context-sensitive: pick probe based on what's missing from the answer
    if category == "experience":
        if not any(w in lower for w in ["kunde", "customer", "kollege", "colleague", "team", "allein", "alone"]):
            return probes[2] if len(probes) > 2 else probes[0]
        if not any(w in lower for w in ["maschine", "machine", "computer", "program", "software", "gerät", "werkzeug", "tool"]):
            return probes[1]

    # Default: first probe for the category
    return probes[0]


@router.get("/ai/status")
async def get_ai_status() -> Dict:
    """
    Return the current AI mode — checks local model, Ollama, and rule-based.

    Called by the frontend to show the AI indicator badge.
    Returns a unified status so the badge correctly reflects whichever engine
    is actually active (local model takes priority over Ollama over rules).
    """
    try:
        # Check local model first (highest priority)
        local_ready = False
        local_model = None
        try:
            from ai.local_llm import is_ready as _local_ready, get_status as _local_status
            local_ready = _local_ready()
            if local_ready:
                _ls = _local_status()
                local_model = _ls.get("model_name", "Lokales Modell")
        except ImportError:
            pass

        if local_ready:
            return {"status": "success", "data": {
                "ollama_available": True,  # kept for frontend compat
                "mode": "KI-Modell",
                "model": local_model,
                "engine": "local",
                "description": f"Lokales KI-Modell aktiv: {local_model}"
            }}

        # Check Ollama
        try:
            status = ai_get_status()
            if status.get("ollama_available"):
                status["engine"] = "ollama"
                return {"status": "success", "data": status}
        except Exception:
            pass

        return {
            "status": "success",
            "data": {
                "ollama_available": False,
                "mode": "Regelbasiert",
                "model": None,
                "engine": "rules",
                "description": "Regelbasierte Verbesserung aktiv."
            }
        }
    except Exception as e:
        logger.warning(f"AI status check failed: {e}")
        return {
            "status": "success",
            "data": {"ollama_available": False, "mode": "Regelbasiert", "model": None,
                     "engine": "rules", "description": "Regelbasierte Verbesserung aktiv."}
        }


@router.post("/ai/refresh")
async def refresh_ai_detection() -> Dict:
    """Force re-detection of all AI engines (local model + Ollama)."""
    ai_reset()

    # Check local model first (highest priority)
    local_ready = False
    local_model = None
    try:
        from ai.local_llm import is_ready as _local_ready, get_status as _local_status
        local_ready = _local_ready()
        if local_ready:
            _ls = _local_status()
            local_model = _ls.get("model_name", "Lokales Modell")
    except ImportError:
        pass

    if local_ready:
        return {"status": "success", "data": {
            "ollama_available": True,
            "mode": "KI-Modell",
            "model": local_model,
            "engine": "local",
            "description": f"Lokales KI-Modell aktiv: {local_model}"
        }}

    # Fall back to Ollama check
    try:
        status = ai_get_status()
        if status.get("ollama_available"):
            status["engine"] = "ollama"
            return {"status": "success", "data": status}
    except Exception:
        pass

    return {"status": "success", "data": {
        "ollama_available": False, "mode": "Regelbasiert",
        "model": None, "engine": "rules",
        "description": "Regelbasierte Verbesserung aktiv."
    }}


def _require_local_or_key(request: Request) -> None:
    """
    Gate destructive/admin endpoints. Allowed from loopback OR with a matching
    X-API-Key. A remote caller without the key is refused. Kept self-contained
    here to avoid a circular import from app.py.
    """
    from shared.utils.network_block import is_loopback_host  # canonical, single source
    if is_loopback_host(request.client.host if request.client else ""):
        return
    import secrets as _secrets
    try:
        from config import API_KEY
    except Exception:
        API_KEY = ""
    supplied = request.headers.get("X-API-Key", "")
    if not API_KEY or not _secrets.compare_digest(supplied, API_KEY):
        _client = request.client.host if request.client else "unknown"
        logger.warning(f"admin endpoint refused: non-loopback client={_client} without valid key")
        raise HTTPException(status_code=403,
                            detail="Restricted to the local machine or an authenticated request.")


@router.post("/admin/cleanup-sessions")
async def cleanup_sessions(
    request: Request,
    days_old: int = 365,
    draft_days_old: int = 30,
    engine: InterviewEngine = Depends(_get_engine),
) -> Dict:
    """
    Trigger a retention sweep (DESTRUCTIVE) older than the given thresholds.

    Two-tier purge: abandoned drafts after `draft_days_old`; ALL sessions
    (incl. completed/approved/locked) after `days_old`. Child rows are deleted
    explicitly (no orphaned PII). Gated to loopback-or-API-key — it can delete
    approved CVs, so it must not be callable by an unauthenticated remote client.

    WARNING: days_old=1 will delete approved CVs older than 1 day. Export first.

    Returns:
        Dict with number of deleted sessions and thresholds used.
    """
    _require_local_or_key(request)
    try:
        count = engine.cleanup_old_sessions(days_old, draft_days_old)
        return {"status": "success",
                "data": {"deleted": count, "days_old": days_old, "draft_days_old": draft_days_old}}
    except Exception as e:
        logger.error(f"Session cleanup error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Session cleanup failed")


def interpret_quality(score: float, language: str = "de") -> dict:
    """
    Convert a raw 0–1 quality score into a human-readable label and tip.

    The tip is shown directly in the UI so it must be encouraging, never
    critical (matching the project's confidence-scaffolding philosophy).

    Args:
        score:    CV quality score in the range [0.0, 1.0].
        language: ISO 639-1 UI language.  Defaults to "de".

    Returns:
        Dict with keys: label (emoji + short text), tip (longer explanation),
        score (rounded to 2 decimal places).
    """
    _quality_messages: dict = {
        "de": {
            "excellent": (
                "⭐⭐⭐ Ausgezeichnet",
                "Ihr Lebenslauf ist vollständig und professionell. Gut gemacht!",
            ),
            "good": (
                "⭐⭐ Gut",
                "Ihr Lebenslauf ist gut. Einige Details könnten noch helfen.",
            ),
            "fair": (
                "⭐ Ausreichend",
                "Ihr Lebenslauf ist verwendbar. Ihr Trainer kann Ihnen helfen, ihn zu verbessern.",
            ),
            "weak": (
                "⚠️ Unvollständig",
                "Ihr Lebenslauf braucht noch mehr Details. Bitte ergänzen Sie Ihre Antworten.",
            ),
        },
        "en": {
            "excellent": ("⭐⭐⭐ Excellent", "Your CV is complete and professional. Well done!"),
            "good": ("⭐⭐ Good", "Your CV is good. A few more details would help."),
            "fair": ("⭐ Fair", "Your CV is usable. Your trainer can help you improve it."),
            "weak": ("⚠️ Incomplete", "Your CV needs more detail. Please add more to your answers."),
        },
        "tr": {
            "excellent": ("⭐⭐⭐ Mükemmel", "CV'niz eksiksiz ve profesyonel. Tebrikler!"),
            "good": ("⭐⭐ İyi", "CV'niz iyi. Birkaç detay daha yardımcı olur."),
            "fair": ("⭐ Yeterli", "CV'niz kullanılabilir. Eğitmeniniz geliştirmenize yardımcı olabilir."),
            "weak": ("⚠️ Eksik", "CV'niz daha fazla ayrıntı gerektiriyor. Lütfen yanıtlarınızı tamamlayın."),
        },
        "ar": {
            "excellent": ("⭐⭐⭐ ممتاز", "سيرتك الذاتية كاملة ومحترفة. أحسنت!"),
            "good": ("⭐⭐ جيد", "سيرتك جيدة. بعض التفاصيل تساعد."),
            "fair": ("⭐ مقبول", "سيرتك صالحة للاستخدام. مدربك يساعدك."),
            "weak": ("⚠️ غير مكتمل", "تحتاج سيرتك إلى مزيد من التفاصيل."),
        },
        "bs": {
            "excellent": ("⭐⭐⭐ Odlično", "Vaš CV je potpun i profesionalan. Bravo!"),
            "good": ("⭐⭐ Dobro", "Vaš CV je dobar. Još malo detalja bi pomoglo."),
            "fair": ("⭐ Dovoljno", "Vaš CV je upotrebljiv. Vaš trener može pomoći."),
            "weak": ("⚠️ Nepotpuno", "Vaš CV treba više detalja. Dopunite odgovore."),
        },
        "pl": {
            "excellent": ("⭐⭐⭐ Doskonały", "Twoje CV jest kompletne i profesjonalne. Świetna robota!"),
            "good": ("⭐⭐ Dobry", "Twoje CV jest dobre. Kilka dodatkowych szczegółów pomoże."),
            "fair": ("⭐ Wystarczający", "Twoje CV nadaje się do użytku. Trener pomoże ci je poprawić."),
            "weak": ("⚠️ Niepełny", "CV wymaga więcej szczegółów. Uzupełnij swoje odpowiedzi."),
        },
        "ro": {
            "excellent": ("⭐⭐⭐ Excelent", "CV-ul tău este complet şi profesional. Felicitări!"),
            "good": ("⭐⭐ Bun", "CV-ul tău este bun. Câteva detalii în plus ar ajuta."),
            "fair": ("⭐ Satisfăcător", "CV-ul tău este utilizabil. Formatorul te poate ajuta."),
            "weak": ("⚠️ Incomplet", "CV-ul tău necesită mai multe detalii. Completează răspunsurile."),
        },
        "uk": {
            "excellent": ("⭐⭐⭐ Видатно", "Ваше резюме повне і професійне. Молодець!"),
            "good": ("⭐⭐ Добре", "Ваше резюме добре. Декілька деталей допоможуть."),
            "fair": ("⭐ Достатньо", "Ваше резюме придатне. Тренер допоможе його поліпшити."),
            "weak": ("⚠️ Неповне", "Резюме потребує більше деталей. Доповніть відповіді."),
        },
        "ru": {
            "excellent": ("⭐⭐⭐ Отлично", "Ваше резюме полное и профессиональное. Отличная работа!"),
            "good": ("⭐⭐ Хорошо", "Ваше резюме хорошее. Ещё несколько деталей помогут."),
            "fair": ("⭐ Удовлетворительно", "Ваше резюме пригодно. Тренер поможет улучшить."),
            "weak": ("⚠️ Неполное", "Резюме нуждается в большем количестве деталей."),
        },
        "sk": {
            "excellent": ("⭐⭐⭐ Vynikajúce", "Váš životopis je úplný a profesionálny. Skvelo!"),
            "good": ("⭐⭐ Dobré", "Váš životopis je dobrý. Niekolko detailov by pomohlo."),
            "fair": ("⭐ Dostatočné", "Váš životopis je použiteľný. Tréner vám môže pomôcť."),
            "weak": ("⚠️ Nekompletné", "Váš životopis potrebuje viac detailov. Doplňte odpovede."),
        },
    }

    lang = language if language in _quality_messages else "de"
    msgs = _quality_messages[lang]

    if score >= 0.8:
        label, tip = msgs["excellent"]
    elif score >= 0.6:
        label, tip = msgs["good"]
    elif score >= 0.4:
        label, tip = msgs["fair"]
    else:
        label, tip = msgs["weak"]

    return {"label": label, "tip": tip, "score": round(score, 2)}


@router.post("/complete/{session_id}")
def complete_interview(
    session_id: int,
    builder: CVBuilder = Depends(_get_builder),
    storage: CVStorage = Depends(_get_storage),
    engine: InterviewEngine = Depends(_get_engine),
) -> Dict:
    """
    Finalize interview: build CVData from all answers and persist it.

    Must be called when interview is complete so exports can work.
    Returns CV summary including quality score and ready_for_export flag.
    """
    _current_session_id.set(session_id)
    try:
        logger.info(f"Completing interview for session {session_id}")

        # Get session info directly (get_interview_status omits user_id/language)
        session = engine.db.get_session(str(session_id))
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        user_id = session.get("user_id", "unknown")
        interview_path = session.get("interview_path", "other")
        language = session.get("language", "de")

        # Build CVData by re-polishing all answers
        cv_data = builder.build_cv_from_session(
            session_id=session_id,
            user_id=user_id,
            interview_path=interview_path,
            language_input=language
        )

        if cv_data is None:
            raise HTTPException(status_code=400, detail="No answers found - cannot build CV")

        # Persist to cv_data table
        saved = storage.save_cv_data(cv_data, session_id=session_id)
        if not saved:
            raise HTTPException(status_code=500, detail="Failed to save CV data")

        sections_count = (len(cv_data.background) + len(cv_data.experience) +
                          len(cv_data.skills) + len(cv_data.motivation) +
                          len(cv_data.training) + len(cv_data.projects))

        # AI skill surfacing — scan all raw answers for skills the rule engine may have missed.
        # OFF by default: on a CPU-only local model this extra generation adds
        # 30-60s to "complete", and the rule engine already extracts skills during
        # the build. Enable with AMS_AI_SKILL_SURFACING=1 where latency is fine.
        surfaced_skills: list = []
        try:
            import os as _os
            _surf_on = _os.environ.get("AMS_AI_SKILL_SURFACING", "0").lower() in ("1", "true", "yes")
            from ai.local_llm import is_ready as _ai_ready, chat as _ai_chat
            if _surf_on and _ai_ready():
                raw_answers = engine.db.execute_query(
                    "SELECT answer_text FROM answers WHERE session_id = ? AND answer_text NOT LIKE '[SKIPPED]'",
                    (session_id,)
                )
                all_raw_text = " ".join(r.get("answer_text", "") for r in raw_answers)[:1200]
                if all_raw_text.strip():
                    skill_result = _ai_chat(
                        system=(
                            "Du bist ein Skill-Extraktor für Lebensläufe. "
                            "Extrahiere konkrete, berufsrelevante Fähigkeiten aus dem Text. "
                            "Format: eine Fähigkeit pro Zeile, max. 10 Fähigkeiten, nur Nomen oder kurze Phrasen. "
                            "Keine Einleitung, keine Nummerierung."
                        ),
                        user=f"Rohtexte aus dem Interview:\n{all_raw_text}",
                        max_tokens=200,
                    )
                    if skill_result:
                        new_skills = [s.strip(" -•·") for s in skill_result.splitlines() if s.strip()]
                        existing_lower = {s.lower() for s in cv_data.all_skills}
                        surfaced_skills = [s for s in new_skills if s and s.lower() not in existing_lower]
                        if surfaced_skills:
                            cv_data.all_skills = cv_data.all_skills + surfaced_skills
                            # Re-save with surfaced skills
                            storage.save_cv_data(cv_data, session_id=session_id)
        except Exception as _exc:
            logger.debug(f"AI skill surfacing skipped: {_exc}")

        # Mark the session completed so retention cleanup never purges a
        # finished CV (cleanup_old_sessions only spares completed = 1).
        try:
            engine.db.execute_update(
                "UPDATE sessions SET completed = 1, updated_at = datetime('now') WHERE id = ?",
                (int(session_id),),
            )
        except Exception as _exc:
            logger.warning(f"Could not mark session completed (non-fatal): {_exc}")

        quality_interpretation = interpret_quality(
            score=cv_data.overall_quality or 0.0,
            language=language,
        )

        return {
            "status": "success",
            "data": {
                "session_id": session_id,
                "overall_quality": cv_data.overall_quality,
                "quality_interpretation": quality_interpretation,
                "ready_for_export": cv_data.ready_for_export,
                "sections_count": sections_count,
                "all_skills": cv_data.all_skills,
                "surfaced_skills": surfaced_skills,
                "message": "Interview complete. CV is ready for export."
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error completing interview: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to complete interview")


