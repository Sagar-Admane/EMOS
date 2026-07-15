"""
Planner Module — Phase 5.1.
Generates a structured checklist of tasks based on a RouteDecision or user goal.
"""
from __future__ import annotations

import json
import logging
import re
from typing import Any

from pydantic import BaseModel, Field
from google import genai
from google.genai import types

from app.ai.router.schemas import RouteDecision
from app.ai.router.enums import Skill
from app.ai.prompts.loader import PromptLoader
from app.core.config import settings

logger = logging.getLogger(__name__)

# Map Skill Enum to Skill class names
SKILL_CLASS_MAP = {
    Skill.ARCHITECTURE: "ArchitectureSkill",
    Skill.REPOSITORY_SUMMARY: "RepositorySummarySkill",
    Skill.CODE_SEARCH: "CodeSearchSkill",
    Skill.OWNERSHIP: "OwnershipSkill",
    Skill.REVIEWER: "ReviewerSkill",
    Skill.DEPENDENCY: "DependencySkill",
    Skill.DEPLOYMENT: "DeploymentSkill",
    Skill.DECISION_RECALL: "DecisionRecallSkill",
}


class Task(BaseModel):
    """A single step in the engineering investigation plan."""
    id: int
    type: str  # search_graph, search_code, search_metadata, generate_report
    description: str | None = None


class TaskPlan(BaseModel):
    """A standardized plan containing a checklist of tasks."""
    goal: str
    skill: str
    tasks: list[Task] = Field(default_factory=list)


# ────────────────────────────────────────────────────────────────────────── #
# LEVEL 1 MAPPINGS: Skill to Predefined Task List
# ────────────────────────────────────────────────────────────────────────── #
LEVEL1_WORKFLOWS: dict[Skill, list[dict[str, Any]]] = {
    Skill.ARCHITECTURE: [
        {"id": 1, "type": "search_graph", "description": "Search repository and service relations in the dependency graph"},
        {"id": 2, "type": "search_code", "description": "Search architectural components and code structure"},
        {"id": 3, "type": "generate_report", "description": "Generate final architecture analysis report"}
    ],
    Skill.REPOSITORY_SUMMARY: [
        {"id": 1, "type": "search_metadata", "description": "Retrieve repository details, contributors, and recent activity"},
        {"id": 2, "type": "generate_report", "description": "Generate final repository summary report"}
    ],
    Skill.CODE_SEARCH: [
        {"id": 1, "type": "search_code", "description": "Retrieve relevant code snippets and files"},
        {"id": 2, "type": "generate_report", "description": "Generate code explanation report"}
    ],
    Skill.OWNERSHIP: [
        {"id": 1, "type": "search_graph", "description": "Retrieve file ownership and contributor graphs"},
        {"id": 2, "type": "search_metadata", "description": "Retrieve file path history, authors, and commit count metadata"},
        {"id": 3, "type": "generate_report", "description": "Generate ownership analysis report"}
    ],
    Skill.REVIEWER: [
        {"id": 1, "type": "search_metadata", "description": "Retrieve PR review activity, comments, and approvals"},
        {"id": 2, "type": "search_graph", "description": "Search code reviewer relationship networks"},
        {"id": 3, "type": "generate_report", "description": "Generate code reviewer activity report"}
    ],
    Skill.DEPENDENCY: [
        {"id": 1, "type": "search_graph", "description": "Trace package, library, and module dependencies in the graph"},
        {"id": 2, "type": "generate_report", "description": "Generate dependency analysis report"}
    ],
    Skill.DEPLOYMENT: [
        {"id": 1, "type": "search_metadata", "description": "Fetch deployment logs, server status, and release metadata"},
        {"id": 2, "type": "search_graph", "description": "Check service mapping and infrastructure layout"},
        {"id": 3, "type": "generate_report", "description": "Generate deployment investigation report"}
    ],
    Skill.DECISION_RECALL: [
        {"id": 1, "type": "search_code", "description": "Retrieve design decisions, ADR files, and architectural notes"},
        {"id": 2, "type": "generate_report", "description": "Generate decision recall report"}
    ],
}


class TaskPlanner:
    """
    Planning Engine (Phase 5.1).
    Responsible for generating a checklist of tasks (TaskPlan) for a given RouteDecision.
    Uses Level 1 (predefined), Level 2 (rules), and Level 3 (LLM) workflows.
    """

    def __init__(self, client: genai.Client | None = None) -> None:
        self._client = client or genai.Client(api_key=settings.api_key)

    def plan(self, route: RouteDecision) -> TaskPlan:
        """
        Create a TaskPlan for the given RouteDecision.
        """
        logger.info("[Planner] Planning for goal: '%s' | skill=%s", route.question, route.skill.value)

        # 1. Level 2: Rule-Based Workflows (Keyword pattern matching)
        plan_level2 = self._apply_level2_rules(route)
        if plan_level2:
            logger.info("[Planner] Plan generated using Level 2 (Rule-Based)")
            return plan_level2

        # 2. Level 3 fallback check:
        # We only use Level 3 LLM planner if the question is complex/mixed (contains comparison, multi-step requests, etc.)
        # If it is a straightforward query, we default to Level 1.
        if self._is_complex_query(route.question):
            try:
                plan_level3 = self._generate_level3_plan(route)
                logger.info("[Planner] Plan generated using Level 3 (LLM Fallback)")
                return plan_level3
            except Exception as exc:
                logger.error("[Planner] Level 3 LLM planning failed: %s. Falling back to Level 1.", exc)

        # 3. Level 1: Existing Skills Predefined Workflows
        plan_level1 = self._apply_level1_mappings(route)
        logger.info("[Planner] Plan generated using Level 1 (Predefined)")
        return plan_level1

    def _apply_level1_mappings(self, route: RouteDecision) -> TaskPlan:
        """Level 1: Map skill directly to static checklist."""
        skill_class = SKILL_CLASS_MAP.get(route.skill, "ArchitectureSkill")
        tasks_data = LEVEL1_WORKFLOWS.get(route.skill)
        
        if not tasks_data:
            # Fallback to a default simple plan
            tasks_data = [
                {"id": 1, "type": "search_code", "description": "Search code repository for relevant snippets"},
                {"id": 2, "type": "generate_report", "description": "Generate final report"}
            ]

        tasks = [Task(**t) for t in tasks_data]
        return TaskPlan(goal=route.question, skill=skill_class, tasks=tasks)

    def _apply_level2_rules(self, route: RouteDecision) -> TaskPlan | None:
        """Level 2: Predefined rule-based pattern matching."""
        q_lower = route.question.lower()
        skill_class = SKILL_CLASS_MAP.get(route.skill, "ArchitectureSkill")

        # Incident / Deployment failure investigation
        if "deploy" in q_lower and ("fail" in q_lower or "issue" in q_lower or "error" in q_lower):
            tasks = [
                Task(id=1, type="search_metadata", description="Find recent deployments, releases, and related commits"),
                Task(id=2, type="search_graph", description="Trace downstream dependencies and affected services"),
                Task(id=3, type="search_code", description="Analyze error logs, configurations, and crash-related source files"),
                Task(id=4, type="generate_report", description="Synthesize deployment root cause investigation report")
            ]
            return TaskPlan(goal=route.question, skill="DeploymentSkill", tasks=tasks)

        # Compare/Comparison query
        if "compare" in q_lower or "difference between" in q_lower or "before and after" in q_lower:
            tasks = [
                Task(id=1, type="search_graph", description="Identify components and relationships involved in the comparison"),
                Task(id=2, type="search_code", description="Search implementation differences across files"),
                Task(id=3, type="search_metadata", description="Search historical commits to find design decision modifications"),
                Task(id=4, type="generate_report", description="Synthesize comparative analysis report")
            ]
            return TaskPlan(goal=route.question, skill=skill_class, tasks=tasks)

        return None

    def _is_complex_query(self, question: str) -> bool:
        """Detect whether a query is complex enough to trigger LLM fallback."""
        q_lower = question.lower()
        complex_keywords = ["why", "how did", "investigate", "trace", "impact of", "consequence", "risk", "root cause"]
        return any(kw in q_lower for kw in complex_keywords)

    def _generate_level3_plan(self, route: RouteDecision) -> TaskPlan:
        """Level 3: Query LLM to generate a custom task list."""
        skill_class = SKILL_CLASS_MAP.get(route.skill, "ArchitectureSkill")
        prompt_template = PromptLoader.load("planner")
        prompt = prompt_template.replace("{goal}", route.question).replace("{skill}", skill_class)

        response = self._client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.1,
                top_p=0.95,
                max_output_tokens=2048,
            )
        )

        raw_text = response.text or ""
        logger.debug("[Planner] LLM raw plan response: %s", raw_text)

        parsed = self._parse_json(raw_text)
        
        # Validate tasks format from JSON
        tasks_data = parsed.get("tasks", [])
        if not tasks_data:
            raise ValueError("No tasks found in LLM planner response JSON")

        tasks = []
        for i, task_dict in enumerate(tasks_data, start=1):
            t_type = task_dict.get("type", "search_code")
            desc = task_dict.get("description", f"Task {i}")
            tasks.append(Task(id=i, type=t_type, description=desc))

        # Ensure the plan ends with a report task
        if not tasks or tasks[-1].type != "generate_report":
            tasks.append(Task(id=len(tasks) + 1, type="generate_report", description="Synthesize final engineering report"))

        return TaskPlan(
            goal=parsed.get("goal", route.question),
            skill=parsed.get("skill", skill_class),
            tasks=tasks
        )

    @staticmethod
    def _parse_json(text: str) -> dict:
        """Extract and parse JSON from the LLM output."""
        match = re.search(r'```json\s*(.*?)\s*```', text, re.DOTALL)
        if match:
            text = match.group(1)
        else:
            match_plain = re.search(r'```\s*(.*?)\s*```', text, re.DOTALL)
            if match_plain:
                text = match_plain.group(1)
        text = text.strip()
        return json.loads(text)
