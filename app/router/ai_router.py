"""
AI Intelligence Layer — FastAPI Router.

Endpoints:
  POST /ai/ask    — Full pipeline: question → engineering answer
  GET  /ai/route  — Debug endpoint: shows RouteDecision for a question
  GET  /ai/health — Liveness check for the AI layer
"""
from __future__ import annotations

import logging

from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel

from app.ai.agent.engineering_agent import EngineeringAgent
from app.ai.models.schemas import AIRequest, AIResponse
from app.ai.router.router_service import RouterService
from app.ai.router.schemas import RouteDecision

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ai", tags=["AI Intelligence"])

# Singleton agent — instantiated once at module load time
_agent = EngineeringAgent()
_router_service = RouterService()


# ────────────────────────────────────────────────────────────────────────── #
# POST /ai/ask
# ────────────────────────────────────────────────────────────────────────── #

@router.post(
    "/ask",
    response_model=AIResponse,
    summary="Ask an engineering question about a repository",
    description=(
        "Runs the full 6-phase AI Intelligence Pipeline:\n"
        "1. Query Router → 2. Retrieval → 3. Context Builder → "
        "4. Engineering Skill → 5. AI Agent → 6. LLM Response Generator.\n\n"
        "Provide an optional `repo_id` to scope retrieval to a specific repository."
    ),
)
async def ask(request: AIRequest) -> AIResponse:
    """
    Ask an engineering question about a repository.

    The agent will:
    - Classify intent and select the appropriate skill
    - Retrieve relevant information from PostgreSQL, Neo4j, and/or Qdrant
    - Build an LLM-ready context package
    - Generate a precise engineering answer via Gemini
    """
    if not request.question or not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    try:
        response = await _agent.answer(request)
        return response
    except Exception as exc:
        logger.exception("AI pipeline error: %s", exc)
        raise HTTPException(
            status_code=500,
            detail=f"AI pipeline encountered an error: {str(exc)}",
        )


# ────────────────────────────────────────────────────────────────────────── #
# GET /ai/route
# ────────────────────────────────────────────────────────────────────────── #

class RouteDebugResponse(BaseModel):
    question: str
    intent: str
    skill: str
    strategy: str
    required_sources: list[str]
    confidence: float
    reasoning: str
    filters: dict


@router.get(
    "/route",
    response_model=RouteDebugResponse,
    summary="Debug: show routing decision for a question",
    description=(
        "Returns the RouteDecision for a given question without executing "
        "the full pipeline. Useful for debugging intent classification and "
        "source selection."
    ),
)
def debug_route(
    q: str = Query(..., description="The engineering question to route"),
) -> RouteDebugResponse:
    """
    Debug endpoint — shows how the Query Router classifies a question.
    """
    if not q or not q.strip():
        raise HTTPException(status_code=400, detail="Query parameter 'q' cannot be empty.")

    route: RouteDecision = _router_service.route(q)
    return RouteDebugResponse(
        question=route.question,
        intent=route.intent.value,
        skill=route.skill.value,
        strategy=route.strategy.value,
        required_sources=[s.value for s in route.required_sources],
        confidence=route.confidence,
        reasoning=route.reasoning,
        filters=route.filters.model_dump() if route.filters else {},
    )


# ────────────────────────────────────────────────────────────────────────── #
# GET /ai/health
# ────────────────────────────────────────────────────────────────────────── #

@router.get(
    "/health",
    summary="AI layer health check",
)
def health() -> dict:
    """Liveness check for the AI Intelligence Layer."""
    return {
        "status": "ok",
        "layer": "AI Intelligence Layer",
        "phases": ["router", "retrieval", "context", "skills", "agent", "llm"],
    }
