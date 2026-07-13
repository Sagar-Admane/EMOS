"""
BaseSkill — abstract base class for all Engineering Skills.

Every skill takes a ContextPackage + RouteDecision and returns
a SkillOutput that the LLM Response Generator can consume directly.
"""
from __future__ import annotations

from abc import ABC, abstractmethod

from app.ai.context.schemas import ContextPackage
from app.ai.models.schemas import SkillOutput
from app.ai.prompts.loader import PromptLoader
from app.ai.router.schemas import RouteDecision


class BaseSkill(ABC):
    """
    Abstract base for Engineering Skills.

    Each subclass must declare a `skill_name` class attribute
    matching the corresponding prompt file name (without .txt).

    The `build` method is the sole public interface — it receives
    the assembled ContextPackage and the original RouteDecision,
    and returns a SkillOutput ready for the LLM generator.
    """

    skill_name: str = ""
    default_temperature: float = 0.3
    default_model: str = "gemini-2.5-flash"

    @abstractmethod
    def build(
        self,
        context: ContextPackage,
        route: RouteDecision,
    ) -> SkillOutput:
        """
        Build a SkillOutput from the given context and routing decision.
        """
        raise NotImplementedError

    def _load_prompt(self) -> str:
        """Load this skill's system prompt from the prompt library."""
        return PromptLoader.load(self.skill_name)

    def _format_context(self, context: ContextPackage) -> str:
        """Render the ContextPackage as a plain-text block for the LLM."""
        return context.as_text()

    def _build_full_prompt(
        self,
        system_prompt: str,
        question: str,
        context_text: str,
        citations_text: str,
    ) -> str:
        """
        Assemble the final prompt from the system instructions,
        user question, and retrieved context.
        """
        citations_section = (
            f"\n\nSOURCE REFERENCES:\n{citations_text}"
            if citations_text
            else ""
        )
        return (
            f"{system_prompt}\n\n"
            f"QUESTION:\n{question}\n\n"
            f"CONTEXT:\n{context_text}"
            f"{citations_section}\n\n"
            f"ANSWER:"
        )
