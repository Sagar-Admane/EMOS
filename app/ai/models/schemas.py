"""
Shared Pydantic models for the AI Intelligence Layer.

These are the canonical data contracts passed between
Phase 4.4 (Skills) → Phase 4.5 (Agent) → Phase 4.6 (LLM).
"""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class SkillOutput(BaseModel):
    """
    The output of an Engineering Skill.
    Contains everything the LLM Response Generator needs to call the LLM.
    """

    skill_name: str
    prompt: str
    context_text: str
    temperature: float = 0.3
    model: str = "gemini-2.5-flash"
    citations_text: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)


class LLMResponse(BaseModel):
    """
    The response produced by the LLM Response Generator.
    """

    answer: str
    model_used: str
    skill_used: str
    citations: list[str] = Field(default_factory=list)
    generation_time_ms: float = 0.0
    estimated_tokens: int = 0


class AIRequest(BaseModel):
    """Inbound request to the AI agent endpoint."""

    question: str
    repo_id: int | None = None
    session_id: str | None = None


class AIResponse(BaseModel):
    """Outbound response from the AI agent endpoint."""

    question: str
    answer: str
    skill_used: str
    intent: str
    sources_used: list[str] = Field(default_factory=list)
    citations: list[str] = Field(default_factory=list)
    session_id: str | None = None
    execution_time_ms: float = 0.0
