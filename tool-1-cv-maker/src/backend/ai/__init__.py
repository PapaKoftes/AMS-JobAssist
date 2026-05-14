"""AI integration layer for AMS JobAssist.

Architecture:
  1. Rule-based engine (primary) — verb enforcement, skill normalization, structure
  2. Knowledge base (RAG) — Austrian job data for domain-aware polish and coaching
  3. Local LLM (enhancement) — natural rephrasing of rule-polished text
  4. Ollama (fallback) — trainer power-user path

Priority chain for LLM: Local GGUF model > Ollama > Rule output used as-is.
"""
from .local_llm import (
    is_ready as is_local_ready,
    get_status as get_local_status,
    polish_answer as local_polish,
    enhance_polished as local_enhance,
    model_exists,
    download_model,
    get_available_tiers,
    MODEL_TIERS,
)
from .ollama import polish_with_ollama, detect_ollama, get_status as get_ollama_status

try:
    from .knowledge import (
        find_job,
        get_context_for_prompt,
        get_verbs_for_job,
        get_skills_for_job,
        get_example_phrases,
        get_all_jobs,
        get_stats as get_knowledge_stats,
        is_loaded as is_knowledge_loaded,
    )
except ImportError:
    pass  # knowledge module optional — functions used via direct import in engine.py
