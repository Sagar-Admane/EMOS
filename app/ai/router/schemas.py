from app.ai.router.enums import DataSource, Skill, Intent, RetrievalStrategy

from pydantic import BaseModel, Field
from typing import Any


class Entity(BaseModel):
    typing: str
    value: Any


class QueryFilters(BaseModel):
    repository: str | None = None
    branch: str | None = None
    author: str | None = None
    file: str | None = None


class RouteDecision(BaseModel):
    question: str
    intent: Intent
    confidence: float
    entities: list[Entity] = Field(default_factory=list)
    required_sources: list[DataSource]
    skill: Skill
    strategy: RetrievalStrategy
    filters: QueryFilters = Field(default_factory=QueryFilters)
    reasoning: str

    @property
    def entities(self) -> list[Entity]:
        return self.entities