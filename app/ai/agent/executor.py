"""
Task Executor Module — Phase 5.2.
Iterates over a TaskPlan, executes each search task using Stage 4 retrievers,
and records the findings in Working Memory.
"""
from __future__ import annotations

import logging
from typing import Any

from app.ai.agent.planner import TaskPlan, Task
from app.ai.agent.working_memory import WorkingMemory
from app.ai.router.schemas import RouteDecision
from app.ai.router.enums import DataSource, RetrievalStrategy
from app.ai.retrieval.orchestrator import RetrievalOrchestrator
from app.ai.context.builder import ContextBuilder

logger = logging.getLogger(__name__)


class TaskExecutor:
    """
    Executes a checklist of tasks sequentially.
    Uses RetrievalOrchestrator and ContextBuilder to gather facts for each step,
    caching the findings in WorkingMemory.
    """

    def __init__(
        self,
        orchestrator: RetrievalOrchestrator | None = None,
        context_builder: ContextBuilder | None = None,
    ) -> None:
        self._orchestrator = orchestrator or RetrievalOrchestrator()
        self._context_builder = context_builder or ContextBuilder()

    async def execute(self, plan: TaskPlan, parent_route: RouteDecision) -> WorkingMemory:
        """
        Execute all tasks in the plan sequentially and return the populated WorkingMemory.
        """
        memory = WorkingMemory(goal=plan.goal)
        logger.info("[Executor] Starting execution for plan goal: '%s'", plan.goal)

        for task in plan.tasks:
            if task.type == "generate_report":
                # Report generation is handled by the Reporter phase, skip execution here.
                logger.debug("[Executor] Skipping generate_report task (handled by Reporter)")
                continue

            logger.info("[Executor] Executing task %d: [%s] '%s'", task.id, task.type, task.description)
            try:
                result_text = await self._execute_task(task, parent_route)
                memory.add_step(
                    task_id=task.id,
                    task_type=task.type,
                    description=task.description or "Querying data source",
                    result=result_text
                )
            except Exception as exc:
                logger.exception("[Executor] Error executing task %d: %s", task.id, exc)
                memory.add_step(
                    task_id=task.id,
                    task_type=task.type,
                    description=task.description or "Querying data source",
                    result=f"Failed to retrieve data: {str(exc)}"
                )

        logger.info("[Executor] Finished executing all search tasks.")
        return memory

    async def _execute_task(self, task: Task, parent_route: RouteDecision) -> str:
        """Execute a single search task and return its formatted string findings."""
        # 1. Map task type to DataSource and RetrievalStrategy
        if task.type == "search_graph":
            source = DataSource.NEO4J
            strategy = RetrievalStrategy.GRAPH
        elif task.type == "search_code":
            source = DataSource.QDRANT
            strategy = RetrievalStrategy.VECTOR
        elif task.type == "search_metadata":
            source = DataSource.POSTGRES
            strategy = RetrievalStrategy.SQL
        else:
            logger.warning("[Executor] Unknown task type '%s' — defaulting to search_code", task.type)
            source = DataSource.QDRANT
            strategy = RetrievalStrategy.VECTOR

        # 2. Build virtual RouteDecision for the sub-task, carrying over filters
        route = RouteDecision(
            question=task.description or parent_route.question,
            intent=parent_route.intent,
            confidence=1.0,
            required_sources=[source],
            skill=parent_route.skill,
            strategy=strategy,
            filters=parent_route.filters,
            reasoning=f"Executing sub-task of type {task.type}"
        )

        # 3. Retrieve documents/records
        retrieval_result = await self._orchestrator.retrieve(route)

        if not retrieval_result.documents:
            return "No documents or records found."

        # 4. Build compressed context
        context_package = self._context_builder.build(
            retrieval_result=retrieval_result,
            intent=route.intent,
            question=route.question
        )

        # 5. Format results as plain text
        return context_package.as_text()
