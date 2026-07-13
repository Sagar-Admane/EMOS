"""Architecture skill — explains the structural architecture of the codebase."""
from app.ai.context.schemas import ContextPackage
from app.ai.models.schemas import SkillOutput
from app.ai.router.schemas import RouteDecision
from app.ai.skills.base import BaseSkill


class ArchitectureSkill(BaseSkill):
    """
    Explains the engineering architecture of the repository.
    Uses graph relationships (services, imports, APIs) and
    vector-searched code chunks to reason about structure.
    """

    skill_name = "architecture"
    default_temperature = 0.3

    def build(self, context: ContextPackage, route: RouteDecision) -> SkillOutput:
        system_prompt = self._load_prompt()
        context_text = self._format_context(context)
        citations_text = context.citations_as_text()
        full_prompt = self._build_full_prompt(
            system_prompt=system_prompt,
            question=route.question,
            context_text=context_text,
            citations_text=citations_text,
        )
        return SkillOutput(
            skill_name=self.skill_name,
            prompt=full_prompt,
            context_text=context_text,
            temperature=self.default_temperature,
            model=self.default_model,
            citations_text=citations_text,
            metadata={
                "intent": route.intent.value,
                "sources": [s.value for s in route.required_sources],
            },
        )
