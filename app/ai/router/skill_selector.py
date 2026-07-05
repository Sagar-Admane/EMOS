from app.ai.router.enums import Intent, Skill
from app.ai.router.rules import INTENT_RULES


class SkillSelector:

    def select(self, intent: Intent, question: str | None = None) -> Skill:
        if not isinstance(intent, Intent):
            intent = Intent(str(intent))

        config = INTENT_RULES.get(intent, {})
        skill = config.get("skill")
        if skill is None:
            if intent == Intent.REVIEW_HISTORY:
                return Skill.REVIEWER
            if intent == Intent.REPOSITORY_SUMMARY:
                return Skill.REPOSITORY_SUMMARY
            return Skill.ARCHITECTURE

        return Skill(skill)