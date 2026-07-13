"""
LLMResponseGenerator — Phase 4.6.

Calls the Google Gemini API with a SkillOutput and returns
a structured LLMResponse. Handles streaming, temperature,
model selection, and citation formatting.
"""
from __future__ import annotations

import logging
import time

from google import genai
from google.genai import types

from app.ai.models.schemas import LLMResponse, SkillOutput
from app.core.config import settings

logger = logging.getLogger(__name__)

# Fallback model if SkillOutput.model is empty
_DEFAULT_MODEL = "gemini-2.5-flash"


class LLMResponseGenerator:
    """
    Phase 4.6: Takes a SkillOutput (containing the full assembled prompt,
    temperature, and model selection) and calls Google Gemini to produce
    an engineering answer.

    Responsibilities:
    - Model selection
    - Temperature application
    - Prompt submission
    - Response parsing and citation formatting
    - Timing measurement
    """

    def __init__(self) -> None:
        self._client = genai.Client(api_key=settings.api_key)

    def generate(self, skill_output: SkillOutput) -> LLMResponse:
        """
        Generate an LLM response from the given SkillOutput.
        Returns a structured LLMResponse.
        """
        model = skill_output.model or _DEFAULT_MODEL
        temperature = max(0.0, min(1.0, skill_output.temperature))

        start = time.monotonic()
        try:
            response = self._client.models.generate_content(
                model=model,
                contents=skill_output.prompt,
                config=types.GenerateContentConfig(
                    temperature=temperature,
                    top_p=0.90,
                    top_k=40,
                    max_output_tokens=4096,
                ),
            )
            raw_answer = response.text or ""
        except Exception as exc:
            logger.exception("LLM call failed: %s", exc)
            raw_answer = (
                "I encountered an error generating a response. "
                "Please try again or rephrase your question."
            )

        elapsed_ms = (time.monotonic() - start) * 1000

        # Format citations as a list of strings
        citations = self._parse_citations(skill_output.citations_text)

        # Append citations footer to answer if present
        answer = raw_answer
        if citations:
            answer += "\n\n---\n**Sources:**\n" + "\n".join(citations)

        estimated_tokens = max(1, len(skill_output.prompt + raw_answer) // 4)

        logger.info(
            "LLM response: skill=%s model=%s temp=%.2f tokens~%d time=%.1fms",
            skill_output.skill_name,
            model,
            temperature,
            estimated_tokens,
            elapsed_ms,
        )

        return LLMResponse(
            answer=answer,
            model_used=model,
            skill_used=skill_output.skill_name,
            citations=citations,
            generation_time_ms=elapsed_ms,
            estimated_tokens=estimated_tokens,
        )

    async def generate_async(self, skill_output: SkillOutput) -> LLMResponse:
        """
        Async wrapper around generate() — runs in a thread executor
        so it does not block the event loop.
        """
        import asyncio
        from functools import partial

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, partial(self.generate, skill_output))

    @staticmethod
    def _parse_citations(citations_text: str) -> list[str]:
        """Split the citations text into a list of individual citation strings."""
        if not citations_text or not citations_text.strip():
            return []
        return [
            line.strip()
            for line in citations_text.splitlines()
            if line.strip()
        ]
