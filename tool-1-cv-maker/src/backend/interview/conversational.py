"""
Conversational LLM Interview Engine — skeleton for future development.

Status: 🚧 In progress — architecture defined, implementation pending.

Design intent
─────────────
Replace (or optionally augment) the hardcoded-path interview with a
multi-turn LLM-driven conversation that adapts dynamically to each
participant's situation.

Key differences from the current StateMachine engine
─────────────────────────────────────────────────────
Current engine  → fixed list of questions per path, rule-based polish
This engine     → free-flowing chat, LLM decides next probe, extracts
                  structured CV fields from the conversation as a whole

Architecture
────────────
1. ConversationalSession  — holds turn history + extracted fields
2. ConversationalEngine   — drives the conversation via local LLM
3. FieldExtractor         — runs structured extraction at the end of
                            each turn to update the growing CVData

Integration with Tool 1
───────────────────────
- Falls back to the existing StateMachine engine if local LLM is not
  loaded (ensures offline-first guarantee is never broken).
- The same /api/interview/start → /api/interview/submit-answer →
  /api/interview/complete flow is reused; mode is selected by the
  `interview_mode` field in the start request.
- The existing CVBuilder and export pipeline work unchanged — this
  engine must produce the same CVData shape as output.

Usage (future)
──────────────
    from interview.conversational import ConversationalEngine

    engine = ConversationalEngine(db_manager)
    session = engine.start_session(user_id, language)
    response = engine.submit_turn(session_id, user_message)
    cv_data  = engine.finalize(session_id)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

# Maximum turns before the engine wraps up and finalizes the CV.
MAX_TURNS = 20

# System prompt template — guides the LLM to act as a warm AMS career coach.
_SYSTEM_PROMPT_TEMPLATE = """
Du bist ein einfühlsamer AMS-Karrierecoach. Deine Aufgabe ist es, dem Teilnehmer
beim Erstellen eines professionellen Lebenslaufs zu helfen — durch ein natürliches,
ermutigendes Gespräch.

Regeln:
- Stelle immer nur EINE Frage pro Antwort.
- Verwende einfache, klare Sprache — keine Fachbegriffe.
- Beginne mit einfachen Fragen (Name, Wohnort) und gehe dann zu Erfahrungen über.
- Ermutige den Teilnehmer ständig — auch kurze Antworten sind wertvoll.
- Falls der Teilnehmer {language} spricht, antworte auf {language}.
- Nach {max_turns} Gesprächsrunden beende das Gespräch freundlich.
"""


@dataclass
class ConversationalTurn:
    """A single exchange in the conversation."""
    role: str          # "user" | "assistant"
    content: str
    extracted_fields: Dict[str, str] = field(default_factory=dict)


@dataclass
class ConversationalSession:
    """Full state for one conversational interview session."""
    session_id: str
    user_id: str
    language: str
    turns: List[ConversationalTurn] = field(default_factory=list)
    extracted_cv_fields: Dict[str, str] = field(default_factory=dict)
    turn_count: int = 0
    is_complete: bool = False

    def history_for_llm(self) -> List[Dict[str, str]]:
        """Return turn history in the format llama-cpp-python expects."""
        return [{"role": t.role, "content": t.content} for t in self.turns]


class ConversationalEngine:
    """
    LLM-driven interview engine — adapts questions to each participant.

    🚧 NOT YET IMPLEMENTED — this is the architecture skeleton.
       All public methods raise NotImplementedError until the
       implementation sprint begins.
    """

    def __init__(self, db_manager=None):
        self.db = db_manager
        self._sessions: Dict[str, ConversationalSession] = {}
        logger.info("ConversationalEngine initialised (skeleton — not yet active)")

    # ── Public API (mirrors InterviewEngine interface) ────────────────────────

    def start_session(self, user_id: str, language: str = "de") -> Dict:
        """
        Start a new conversational interview session.

        Returns the same shape as InterviewEngine.start_interview() so the
        existing frontend code can switch modes transparently.
        """
        raise NotImplementedError(
            "ConversationalEngine is not yet implemented. "
            "Use InterviewEngine for production sessions."
        )

    def submit_turn(self, session_id: str, user_message: str) -> Dict:
        """
        Process one user turn and return the next assistant prompt.

        Side effects: updates session.extracted_cv_fields after each turn
        via FieldExtractor (also not yet implemented).
        """
        raise NotImplementedError

    def finalize(self, session_id: str):
        """
        End the conversation and build a CVData object from the extracted fields.

        Returns the same CVData shape as CVBuilder so the export pipeline
        works unchanged.
        """
        raise NotImplementedError

    # ── Private helpers (stubs) ───────────────────────────────────────────────

    def _build_system_prompt(self, session: ConversationalSession) -> str:
        """Render the system prompt for the current session language."""
        return _SYSTEM_PROMPT_TEMPLATE.format(
            language=session.language,
            max_turns=MAX_TURNS,
        )

    def _call_llm(self, system: str, history: List[Dict]) -> Optional[str]:
        """
        Call the local LLM with the conversation history.

        Falls back to None if llama-cpp-python is not installed or the
        model is not loaded — callers must handle the None case.
        """
        try:
            from ai.local_llm import chat as _chat
            return _chat(system=system, user=history[-1]["content"], max_tokens=300)
        except Exception as exc:
            logger.warning(f"LLM call failed: {exc}")
            return None

    def _extract_fields(self, turn: ConversationalTurn) -> Dict[str, str]:
        """
        Run structured field extraction on the latest turn.

        TODO: implement with a separate extraction prompt that outputs JSON
        mapping CV field names to extracted values.
        """
        return {}
