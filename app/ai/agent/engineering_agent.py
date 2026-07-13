"""
EngineeringAgent — Phase 4.5.

The top-level pipeline coordinator for the AI Intelligence Layer.
Orchestrates all six phases without ever knowing about SQL,
Cypher queries, or embedding models directly.

Pipeline:
  1. Query Router    →  RouteDecision
  2. Retrieval       →  RetrievalResult
  3. Context Builder →  ContextPackage
  4. Skill           →  SkillOutput
  5. LLM Generator   →  LLMResponse
  6. Memory          →  persists turn

The agent also:
- Enriches the RouteDecision with repo_id when provided
- Retries retrieval on failure (up to 2 attempts)
- Logs execution time per phase
- Catches and degrades gracefully on partial failures
"""
from __future__ import annotations

import logging
import time
import uuid

from app.ai.router.router_service import RouterService
from app.ai.router.schemas import RouteDecision
from app.ai.retrieval.orchestrator import RetrievalOrchestrator
from app.ai.retrieval.schemas import RetrievalResult
from app.ai.context.builder import ContextBuilder
from app.ai.context.schemas import ContextPackage
from app.ai.skills import SkillRegistry
from app.ai.models.schemas import AIRequest, AIResponse, LLMResponse, SkillOutput
from app.ai.llm.generator import LLMResponseGenerator
from app.ai.memory.conversation_memory import memory

logger = logging.getLogger(__name__)

_MAX_RETRIEVAL_RETRIES = 2


class EngineeringAgent:
    """
    Coordinates the full AI Intelligence pipeline.

    Designed to be stateless between calls (state lives in memory module).
    Can be instantiated once at startup and reused across requests.
    """

    def __init__(
        self,
        router: RouterService | None = None,
        orchestrator: RetrievalOrchestrator | None = None,
        context_builder: ContextBuilder | None = None,
        llm_generator: LLMResponseGenerator | None = None,
    ) -> None:
        self._router = router or RouterService()
        self._orchestrator = orchestrator or RetrievalOrchestrator()
        self._context_builder = context_builder or ContextBuilder()
        self._llm = llm_generator or LLMResponseGenerator()

    async def answer(self, request: AIRequest) -> AIResponse:
        """
        Execute the full 5-phase pipeline for the given AIRequest.
        Returns a structured AIResponse.
        """
        total_start = time.monotonic()
        session_id = request.session_id or str(uuid.uuid4())

        logger.info(
            "[Agent] Starting pipeline | session=%s | question='%s'",
            session_id,
            request.question[:100],
        )

        # ── Phase 4.1: Route ─────────────────────────────────────────────
        t0 = time.monotonic()
        route = self._route(request)
        logger.info("[Agent] Phase 4.1 Route: intent=%s skill=%s (%.1fms)",
                    route.intent.value, route.skill.value, (time.monotonic() - t0) * 1000)

        # ── Phase 4.2: Retrieve (with retry) ─────────────────────────────
        t0 = time.monotonic()
        retrieval_result = await self._retrieve_with_retry(route)
        logger.info("[Agent] Phase 4.2 Retrieval: %d docs (%.1fms)",
                    retrieval_result.statistics.total_documents, (time.monotonic() - t0) * 1000)

        # ── Phase 4.3: Build Context ──────────────────────────────────────
        t0 = time.monotonic()
        context_package = self._build_context(retrieval_result, route)
        logger.info("[Agent] Phase 4.3 Context: %d→%d docs ~%d tokens (%.1fms)",
                    context_package.metadata.total_documents_before_compression,
                    context_package.metadata.total_documents_after_compression,
                    context_package.metadata.estimated_tokens,
                    (time.monotonic() - t0) * 1000)

        # ── Phase 4.4: Select Skill ───────────────────────────────────────
        t0 = time.monotonic()
        skill_output = self._run_skill(context_package, route)
        logger.info("[Agent] Phase 4.4 Skill: %s (%.1fms)",
                    skill_output.skill_name, (time.monotonic() - t0) * 1000)

        # ── Phase 4.6: Generate LLM Response ─────────────────────────────
        t0 = time.monotonic()
        llm_response = await self._llm.generate_async(skill_output)
        logger.info("[Agent] Phase 4.6 LLM: model=%s ~%d tokens (%.1fms)",
                    llm_response.model_used, llm_response.estimated_tokens,
                    (time.monotonic() - t0) * 1000)

        # ── Memory: persist turn ──────────────────────────────────────────
        memory.add(session_id, request.question, llm_response.answer)

        total_ms = (time.monotonic() - total_start) * 1000
        logger.info("[Agent] Pipeline complete: %.1fms", total_ms)

        return AIResponse(
            question=request.question,
            answer=llm_response.answer,
            skill_used=llm_response.skill_used,
            intent=route.intent.value,
            sources_used=[s.value for s in retrieval_result.statistics.sources_used],
            citations=llm_response.citations,
            session_id=session_id,
            execution_time_ms=total_ms,
        )

    # ------------------------------------------------------------------ #
    # Phase helpers
    # ------------------------------------------------------------------ #

    def _route(self, request: AIRequest) -> RouteDecision:
        """Phase 4.1 — Route the question to the right skill and sources."""
        route = self._router.route(request.question)

        # Enrich filters with repo_id if provided by the caller
        if request.repo_id is not None and route.filters is not None:
            # Store repo_id as a string in the repository filter
            route.filters.repository = str(request.repo_id)

        return route

    async def _retrieve_with_retry(
        self,
        route: RouteDecision,
        attempt: int = 0,
    ) -> RetrievalResult:
        """Phase 4.2 — Retrieve with up to _MAX_RETRIEVAL_RETRIES retries."""
        try:
            result = await self._orchestrator.retrieve(route)

            # If all retrievers failed and we have retries left, try again
            if (
                result.statistics.total_documents == 0
                and result.errors
                and attempt < _MAX_RETRIEVAL_RETRIES
            ):
                logger.warning(
                    "[Agent] Retrieval returned 0 docs on attempt %d — retrying.",
                    attempt + 1,
                )
                return await self._retrieve_with_retry(route, attempt + 1)

            return result

        except Exception as exc:
            if attempt < _MAX_RETRIEVAL_RETRIES:
                logger.warning("[Agent] Retrieval error (attempt %d): %s — retrying.", attempt + 1, exc)
                return await self._retrieve_with_retry(route, attempt + 1)
            logger.error("[Agent] Retrieval failed after %d attempts.", _MAX_RETRIEVAL_RETRIES)
            # Return an empty result rather than crashing
            from app.ai.retrieval.schemas import RetrievalStatistics
            return RetrievalResult(
                statistics=RetrievalStatistics()
            )

    def _build_context(
        self,
        retrieval_result: RetrievalResult,
        route: RouteDecision,
    ) -> ContextPackage:
        """Phase 4.3 — Transform retrieval results into an LLM-ready context."""
        return self._context_builder.build(
            retrieval_result=retrieval_result,
            intent=route.intent,
            question=route.question,
        )

    @staticmethod
    def _run_skill(
        context_package: ContextPackage,
        route: RouteDecision,
    ) -> SkillOutput:
        """Phase 4.4 — Select and execute the appropriate engineering skill."""
        skill = SkillRegistry.get(route.skill)
        return skill.build(context_package, route)
