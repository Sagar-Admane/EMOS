"""
FastAPI Router — Phase 6.7.
Exposes REST endpoints for Change Impact, Risk Analysis, and Decision Advisor.
"""
from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

# Stage 4 / 5 Components
from app.ai.router.router_service import RouterService
from app.ai.router.schemas import RouteDecision, QueryFilters
from app.ai.router.enums import Intent, Skill, DataSource, RetrievalStrategy
from app.ai.agent.planner import TaskPlanner
from app.ai.agent.executor import TaskExecutor

# Stage 6 Components
from app.prediction.models import DependencyGraph
from app.prediction.dependency_analyzer import DependencyAnalyzer
from app.prediction.impact_analyzer import ImpactAnalyzer
from app.prediction.risk_engine import RiskEngine
from app.prediction.blast_radius import BlastRadiusAnalyzer
from app.prediction.recommendation_engine import RecommendationEngine
from app.prediction.report_generator import ReportGenerator
from app.prediction.decision_engine import DecisionEngine

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/predict", tags=["Predictive Intelligence"])

# Instantiate coordinators
_router_service = RouterService()
_planner = TaskPlanner()
_executor = TaskExecutor()

_dependency_analyzer = DependencyAnalyzer()
_impact_analyzer = ImpactAnalyzer()
_risk_engine = RiskEngine()
_blast_radius = BlastRadiusAnalyzer()
_recs_engine = RecommendationEngine()
_report_generator = ReportGenerator()
_decision_engine = DecisionEngine()


class ImpactRequest(BaseModel):
    entity: str
    repo_id: int | None = None
    max_depth: int = 5


class DecisionRequest(BaseModel):
    question: str
    entity: str
    repo_id: int | None = None
    max_depth: int = 5


@router.post("/impact")
async def predict_impact(request: ImpactRequest) -> dict[str, Any]:
    """
    Simulates the cascading blast radius, risk level, and recommendations of a code change.
    """
    if not request.entity or not request.entity.strip():
        raise HTTPException(status_code=400, detail="Entity cannot be empty.")

    try:
        # 1. Setup virtual Stage 4/5 routing decision targeting dependency queries
        # Carry over the repository filter if provided
        filters = QueryFilters(repository=str(request.repo_id) if request.repo_id is not None else None)
        route = RouteDecision(
            question=f"Analyze dependencies and ownership of {request.entity}",
            intent=Intent.DEPENDENCY,
            confidence=1.0,
            required_sources=[DataSource.NEO4J, DataSource.POSTGRES],
            skill=Skill.DEPENDENCY,
            strategy=RetrievalStrategy.HYBRID,
            filters=filters,
            reasoning="REST API trigger for change impact simulation"
        )

        # 2. Plan search tasks (Stage 5 Planner)
        plan = _planner.plan(route)

        # 3. Retrieve facts into Working Memory (Stage 5 Executor)
        working_memory = await _executor.execute(plan, route)

        # 4. Phase 6.1: Run Dependency Analysis
        dep_graph = _dependency_analyzer.analyze(
            working_memory=working_memory,
            entity=request.entity,
            level="auto",
            max_depth=request.max_depth
        )

        # 5. Phase 6.2: Run Change Impact Simulation
        impact_results = _impact_analyzer.analyze_impact(dep_graph, working_memory)

        # 6. Phase 6.3: Calculate Risk Score
        risk_results = _risk_engine.calculate_risk(dep_graph, working_memory)

        # 7. Phase 6.4: Build Blast Radius Tree
        change_tree = _blast_radius.build_change_tree(dep_graph)
        scope_est = _blast_radius.estimate_scope(dep_graph)

        # 8. Phase 6.5: Generate Actionable Safeguards
        reviewers = _recs_engine.suggest_reviewers(working_memory, impact_results["affected_files"])
        tests = _recs_engine.suggest_tests(impact_results["affected_files"])
        rollout = _recs_engine.suggest_rollout(risk_results["score"])
        monitoring = _recs_engine.suggest_monitoring(impact_results["affected_files"], impact_results["affected_apis"])

        recs = {
            "reviewers": reviewers,
            "tests": tests,
            "rollout": rollout,
            "monitoring": monitoring
        }

        # 9. Phase 6.6: Render final Markdown Report
        markdown_report = _report_generator.generate_impact_report(
            root=request.entity,
            impact_results=impact_results,
            risk_results=risk_results,
            recs=recs
        )

        return {
            "entity": request.entity,
            "dependency_graph": dep_graph.model_dump(),
            "impact_summary": impact_results,
            "risk_profile": risk_results,
            "blast_radius_tree": change_tree,
            "scope_estimation": scope_est,
            "recommendations": recs,
            "markdown_report": markdown_report
        }

    except Exception as exc:
        logger.exception("Impact simulation error: %s", exc)
        raise HTTPException(
            status_code=500,
            detail=f"Predictive simulation encountered an error: {str(exc)}"
        )


@router.post("/decision")
async def evaluate_architecture_decision(request: DecisionRequest) -> dict[str, Any]:
    """
    Evaluates architectural migration or refactoring questions using evidence and metrics.
    """
    if not request.question or not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")
    if not request.entity or not request.entity.strip():
        raise HTTPException(status_code=400, detail="Entity cannot be empty.")

    try:
        # 1. Setup virtual Stage 4/5 routing decision
        filters = QueryFilters(repository=str(request.repo_id) if request.repo_id is not None else None)
        route = RouteDecision(
            question=request.question,
            intent=Intent.DEPENDENCY,
            confidence=1.0,
            required_sources=[DataSource.NEO4J, DataSource.POSTGRES],
            skill=Skill.DEPENDENCY,
            strategy=RetrievalStrategy.HYBRID,
            filters=filters,
            reasoning="REST API trigger for architectural decision advisory"
        )

        # 2. Plan search tasks (Stage 5 Planner)
        plan = _planner.plan(route)

        # 3. Retrieve facts into Working Memory (Stage 5 Executor)
        working_memory = await _executor.execute(plan, route)

        # 4. Generate Graph, Impact, and Risk metrics
        dep_graph = _dependency_analyzer.analyze(working_memory, request.entity, "auto", request.max_depth)
        risk_results = _risk_engine.calculate_risk(dep_graph, working_memory)

        # 5. Phase 6.7: Run Decision Engine Advisor
        llm_response = await _decision_engine.evaluate_decision(
            question=request.question,
            dep_graph=dep_graph,
            risk_report=risk_results,
            working_memory=working_memory
        )

        return {
            "question": request.question,
            "entity": request.entity,
            "risk_score": risk_results["score"],
            "risk_level": risk_results["level"],
            "evaluation_report": llm_response.answer
        }

    except Exception as exc:
        logger.exception("Decision evaluation error: %s", exc)
        raise HTTPException(
            status_code=500,
            detail=f"Decision advisory layer encountered an error: {str(exc)}"
        )
