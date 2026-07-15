"""
EngineeringAgent — Stage 5 Engineering Agent Layer.

The top-level coordinator for the agentic engineering pipeline.
Orchestrates the new five-step workflow:
1. Query Rewrite (Phase 5.5) — Resolves conversational relative references.
2. Query Router (Phase 4.1) — Classifies intent and selects target skill.
3. Task Planner (Phase 5.1) — Generates a task plan checklist.
4. Task Executor (Phase 5.2) — Runs search tasks using retrieval orchestrator and context builder.
5. Working Memory (Phase 5.3) — Caches and logs findings.
6. Reporter (Phase 5.4) — Synthesizes findings into a structured report.
7. Memory Persistence — Persists chat history.
"""
from __future__ import annotations

import logging
import time
import uuid

from app.ai.router.router_service import RouterService
from app.ai.router.schemas import RouteDecision
from app.ai.retrieval.orchestrator import RetrievalOrchestrator
from app.ai.context.builder import ContextBuilder
from app.ai.models.schemas import AIRequest, AIResponse
from app.ai.llm.generator import LLMResponseGenerator
from app.ai.memory.conversation_memory import memory

# Stage 5 Components
from app.ai.agent.query_rewriter import QueryRewriter
from app.ai.agent.planner import TaskPlanner
from app.ai.agent.executor import TaskExecutor
from app.ai.agent.reporter import Reporter

logger = logging.getLogger(__name__)


class EngineeringAgent:
    """
    Coordinates the Stage 5 agentic pipeline.
    Stateless between calls, relying on conversation memory for context.
    """

    def __init__(
        self,
        router: RouterService | None = None,
        orchestrator: RetrievalOrchestrator | None = None,
        context_builder: ContextBuilder | None = None,
        llm_generator: LLMResponseGenerator | None = None,
        query_rewriter: QueryRewriter | None = None,
        planner: TaskPlanner | None = None,
        executor: TaskExecutor | None = None,
        reporter: Reporter | None = None,
    ) -> None:
        self._router = router or RouterService()
        self._orchestrator = orchestrator or RetrievalOrchestrator()
        self._context_builder = context_builder or ContextBuilder()
        self._llm = llm_generator or LLMResponseGenerator()

        # Instantiate Stage 5 components
        self._query_rewriter = query_rewriter or QueryRewriter()
        self._planner = planner or TaskPlanner()
        self._executor = executor or TaskExecutor(
            orchestrator=self._orchestrator,
            context_builder=self._context_builder
        )
        self._reporter = reporter or Reporter(llm_generator=self._llm)

    async def answer(self, request: AIRequest) -> AIResponse:
        """
        Execute the Stage 5 planning, execution, and reporting pipeline.
        Returns a structured AIResponse.
        """
        total_start = time.monotonic()
        session_id = request.session_id or str(uuid.uuid4())

        logger.info(
            "[Agent] Starting Stage 5 pipeline | session=%s | question='%s'",
            session_id,
            request.question[:100],
        )

        # ── Step 1: Query Rewrite (Phase 5.5) ────────────────────────────
        t0 = time.monotonic()
        rewritten_question = await self._query_rewriter.rewrite(request.question, session_id)
        logger.info("[Agent] Step 1 Query Rewrite: '%s' (%.1fms)",
                    rewritten_question[:100], (time.monotonic() - t0) * 1000)

        # ── Step 2: Route (Phase 4.1) ───────────────────────────────────
        t0 = time.monotonic()
        route = self._route(rewritten_question, request.repo_id)
        logger.info("[Agent] Step 2 Route: intent=%s skill=%s (%.1fms)",
                    route.intent.value, route.skill.value, (time.monotonic() - t0) * 1000)

        # ── Step 3: Plan (Phase 5.1) ────────────────────────────────────
        t0 = time.monotonic()
        plan = self._planner.plan(route)
        logger.info("[Agent] Step 3 Plan: goal='%s' with %d tasks (%.1fms)",
                    plan.goal[:100], len(plan.tasks), (time.monotonic() - t0) * 1000)

        # ── Step 4 & 5: Execute and Working Memory (Phases 5.2 & 5.3) ───
        t0 = time.monotonic()
        working_memory = await self._executor.execute(plan, route)
        logger.info("[Agent] Step 4 & 5 Execution: completed %d steps (%.1fms)",
                    len(working_memory.steps), (time.monotonic() - t0) * 1000)

        # ── Step 6: Report Synthesis (Phase 5.4) ────────────────────────
        t0 = time.monotonic()
        llm_response = await self._reporter.generate_report(working_memory, target_skill=route.skill.value)
        logger.info("[Agent] Step 6 Report: model=%s ~%d tokens (%.1fms)",
                    llm_response.model_used, llm_response.estimated_tokens,
                    (time.monotonic() - t0) * 1000)

        # ── Step 7: Memory Persistence ──────────────────────────────────
        memory.add(session_id, request.question, llm_response.answer)

        total_ms = (time.monotonic() - total_start) * 1000
        logger.info("[Agent] Stage 5 Pipeline complete: %.1fms", total_ms)

        # Retrieve list of unique sources queried during execution
        sources_used = sorted(list({step["type"] for step in working_memory.steps}))

        return AIResponse(
            question=request.question,
            answer=llm_response.answer,
            skill_used=llm_response.skill_used,
            intent=route.intent.value,
            sources_used=sources_used,
            citations=llm_response.citations,
            session_id=session_id,
            execution_time_ms=total_ms,
        )

    def _route(self, question: str, repo_id: int | None) -> RouteDecision:
        """Route the query to the correct skill and sources."""
        route = self._router.route(question)

        # Enrich filters with repo_id if provided by the caller
        if repo_id is not None and route.filters is not None:
            route.filters.repository = str(repo_id)

        return route
