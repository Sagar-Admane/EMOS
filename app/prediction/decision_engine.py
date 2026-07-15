"""
Decision Engine Module — Phase 6.7.
Evaluates architectural decisions (Should we migrate / split / refactor?) using metrics and LLM.
"""
from __future__ import annotations

import logging

from app.prediction.models import DependencyGraph
from app.ai.agent.working_memory import WorkingMemory
from app.ai.models.schemas import SkillOutput, LLMResponse
from app.ai.llm.generator import LLMResponseGenerator
from app.ai.prompts.loader import PromptLoader

logger = logging.getLogger(__name__)


class DecisionEngine:
    """
    Acts as an advisor for large engineering changes and migration strategies.
    """

    def __init__(self, llm_generator: LLMResponseGenerator | None = None) -> None:
        self._llm = llm_generator or LLMResponseGenerator()

    async def evaluate_decision(
        self,
        question: str,
        dep_graph: DependencyGraph,
        risk_report: dict,
        working_memory: WorkingMemory
    ) -> LLMResponse:
        """
        Evaluate an architectural proposal and return a structured advice report.
        """
        logger.info("[DecisionEngine] Evaluating proposal: '%s'", question)

        # 1. Load prompt template
        prompt_template = PromptLoader.load("decision_advisor")

        # 2. Format variables
        evidence_text = working_memory.as_text()
        prompt = (
            prompt_template.replace("{question}", question)
            .replace("{root}", dep_graph.root)
            .replace("{direct_dependents}", str(dep_graph.dependents))
            .replace("{transitive_dependents}", str(dep_graph.indirect_dependencies))
            .replace("{cycles}", str(dep_graph.cycles))
            .replace("{risk_score}", str(risk_report["score"]))
            .replace("{risk_level}", risk_report["level"])
            .replace("{bus_factor}", str(risk_report["bus_factor"]))
            .replace("{modifications}", str(risk_report["total_modifications"]))
            .replace("{evidence}", evidence_text)
        )

        # 3. Formulate SkillOutput payload
        skill_output = SkillOutput(
            skill_name="decision_advisor",
            prompt=prompt,
            context_text=evidence_text,
            temperature=0.2,  # Analytical consensus
            model="gemini-2.5-flash"
        )

        # 4. Generate advice
        llm_response = await self._llm.generate_async(skill_output)
        return llm_response
