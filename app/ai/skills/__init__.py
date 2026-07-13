"""
Skills package — registry of all Engineering Skills.

Usage:
    from app.ai.skills import SkillRegistry
    skill = SkillRegistry.get(Skill.REVIEWER)
    output = skill.build(context, route)
"""
from app.ai.skills.base import BaseSkill
from app.ai.skills.architecture.skill import ArchitectureSkill
from app.ai.skills.reviewer.skill import ReviewerSkill
from app.ai.skills.ownership.skill import OwnershipSkill
from app.ai.skills.repository_summary.skill import RepositorySummarySkill
from app.ai.skills.dependency.skill import DependencySkill
from app.ai.skills.deployment.skill import DeploymentSkill
from app.ai.router.enums import Skill


class SkillRegistry:
    """
    Central registry that maps Skill enum values to
    concrete BaseSkill instances (singletons per type).
    """

    _instances: dict[Skill, BaseSkill] = {
        Skill.ARCHITECTURE: ArchitectureSkill(),
        Skill.REVIEWER: ReviewerSkill(),
        Skill.OWNERSHIP: OwnershipSkill(),
        Skill.REPOSITORY_SUMMARY: RepositorySummarySkill(),
        Skill.DEPENDENCY: DependencySkill(),
        Skill.DEPLOYMENT: DeploymentSkill(),
    }

    @classmethod
    def get(cls, skill: Skill) -> BaseSkill:
        """
        Return the skill instance for the given Skill enum.
        Falls back to ArchitectureSkill for unknown skills.
        """
        instance = cls._instances.get(skill)
        if instance is None:
            import logging
            logging.getLogger(__name__).warning(
                "Unknown skill '%s' — falling back to ArchitectureSkill.", skill
            )
            return cls._instances[Skill.ARCHITECTURE]
        return instance


__all__ = [
    "BaseSkill",
    "ArchitectureSkill",
    "ReviewerSkill",
    "OwnershipSkill",
    "RepositorySummarySkill",
    "DependencySkill",
    "DeploymentSkill",
    "SkillRegistry",
]
