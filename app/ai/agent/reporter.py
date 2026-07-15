"""
Reporter Module — Phase 5.4.
Synthesizes the findings stored in Working Memory into a structured engineering report.
"""
from __future__ import annotations

import logging

from app.ai.agent.working_memory import WorkingMemory
from app.ai.models.schemas import LLMResponse, SkillOutput
from app.ai.llm.generator import LLMResponseGenerator
from app.ai.prompts.loader import PromptLoader

logger = logging.getLogger(__name__)


class Reporter:
    """
    Synthesizes working memory evidence into a comprehensive engineering report.
    Reuses the existing LLMResponseGenerator to call Gemini with a structured prompt.
    """

    def __init__(self, llm_generator: LLMResponseGenerator | None = None) -> None:
        self._llm = llm_generator or LLMResponseGenerator()

    async def generate_report(self, memory: WorkingMemory, target_skill: str = "reporter") -> LLMResponse:
        """
        Synthesize the collected evidence in WorkingMemory into a final LLMResponse.
        """
        logger.info("[Reporter] Generating engineering report for goal: '%s'", memory.goal)

        # 1. Load the synthesis prompt
        prompt_template = PromptLoader.load("reporter")

        # 2. Format with the goal and memory content
        working_memory_text = memory.as_text()
        prompt = prompt_template.replace("{goal}", memory.goal).replace("{working_memory}", working_memory_text)

        # 3. Create the SkillOutput payload
        skill_output = SkillOutput(
            skill_name=target_skill,
            prompt=prompt,
            context_text=working_memory_text,
            temperature=0.2,  # Low temperature for analytical precision
            model="gemini-2.5-flash",
            citations_text=""  # Citations are embedded within findings
        )

        # 4. Generate the final response using the LLM Generator
        llm_response = await self._llm.generate_async(skill_output)
        return llm_response
