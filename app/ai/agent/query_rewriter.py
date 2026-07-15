"""
Query Rewriter Module — Phase 5.5.
Rewrites the latest user query using conversation history to resolve pronouns and relative references.
"""
from __future__ import annotations

import logging

from google import genai
from google.genai import types

from app.ai.memory.conversation_memory import memory
from app.ai.prompts.loader import PromptLoader
from app.core.config import settings

logger = logging.getLogger(__name__)


class QueryRewriter:
    """
    Resolves pronouns and context references in multi-turn chats.
    """

    def __init__(self, client: genai.Client | None = None) -> None:
        self._client = client or genai.Client(api_key=settings.api_key)

    async def rewrite(self, question: str, session_id: str | None) -> str:
        """
        Rewrite the user question if history is available and it contains relative references.
        """
        if not session_id:
            return question

        history_text = memory.format_history(session_id)
        if not history_text:
            return question

        logger.debug("[Rewriter] Found conversation history for session %s. Checking for rewrite.", session_id)

        try:
            # Load rewrite prompt template
            prompt_template = PromptLoader.load("query_rewriter")
            prompt = prompt_template.replace("{history}", history_text).replace("{question}", question)

            response = self._client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.1,
                    top_p=0.95,
                    max_output_tokens=512,
                )
            )

            rewritten = (response.text or "").strip()
            # Clean up any enclosing quotes added by the LLM
            if (rewritten.startswith('"') and rewritten.endswith('"')) or (rewritten.startswith("'") and rewritten.endswith("'")):
                rewritten = rewritten[1:-1].strip()

            if rewritten and rewritten != question:
                logger.info("[Rewriter] Rewrote query: '%s' ──> '%s'", question, rewritten)
                return rewritten

        except Exception as exc:
            logger.error("[Rewriter] Failed to rewrite query: %s. Using original.", exc)

        return question
