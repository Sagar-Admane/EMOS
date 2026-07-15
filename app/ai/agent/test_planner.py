from unittest.mock import MagicMock
import pytest

from app.ai.agent.planner import TaskPlanner, TaskPlan
from app.ai.router.schemas import RouteDecision, QueryFilters
from app.ai.router.enums import Intent, Skill, DataSource, RetrievalStrategy


def test_level1_predefined_mappings():
    # Test Architecture Skill mapping
    route = RouteDecision(
        question="Explain the auth service design",
        intent=Intent.ARCHITECTURE,
        confidence=0.9,
        required_sources=[DataSource.NEO4J, DataSource.QDRANT],
        skill=Skill.ARCHITECTURE,
        strategy=RetrievalStrategy.HYBRID,
        reasoning="Test reasoning",
        filters=QueryFilters()
    )

    planner = TaskPlanner(client=MagicMock())
    plan = planner.plan(route)

    assert isinstance(plan, TaskPlan)
    assert plan.goal == "Explain the auth service design"
    assert plan.skill == "ArchitectureSkill"
    assert len(plan.tasks) == 3
    assert plan.tasks[0].type == "search_graph"
    assert plan.tasks[1].type == "search_code"
    assert plan.tasks[2].type == "generate_report"


def test_level2_rule_based_mappings():
    # Test deployment failure rule mapping
    route = RouteDecision(
        question="Why did the last deploy fail with error 500?",
        intent=Intent.DEPLOYMENT,
        confidence=0.9,
        required_sources=[DataSource.POSTGRES, DataSource.NEO4J],
        skill=Skill.DEPLOYMENT,
        strategy=RetrievalStrategy.HYBRID,
        reasoning="Test reasoning",
        filters=QueryFilters()
    )

    planner = TaskPlanner(client=MagicMock())
    plan = planner.plan(route)

    assert isinstance(plan, TaskPlan)
    assert plan.skill == "DeploymentSkill"
    assert len(plan.tasks) == 4
    assert plan.tasks[0].type == "search_metadata"
    assert plan.tasks[1].type == "search_graph"
    assert plan.tasks[2].type == "search_code"
    assert plan.tasks[3].type == "generate_report"


def test_level3_llm_planner_fallback():
    # Setup LLM Mock response
    mock_client = MagicMock()
    mock_response = MagicMock()
    # Mock return JSON for Level 3
    mock_response.text = """
    ```json
    {
      "goal": "Investigate why auth-service failed after Redis migration",
      "skill": "ArchitectureSkill",
      "tasks": [
        {
          "id": 1,
          "type": "search_graph",
          "description": "Trace graph dependencies"
        },
        {
          "id": 2,
          "type": "search_metadata",
          "description": "Fetch DB migration commits"
        },
        {
          "id": 3,
          "type": "generate_report",
          "description": "Synthesize results"
        }
      ]
    }
    ```
    """
    mock_client.models.generate_content.return_value = mock_response

    route = RouteDecision(
        question="Why did auth-service fail after Redis migration?",
        intent=Intent.ARCHITECTURE,
        confidence=0.9,
        required_sources=[DataSource.NEO4J],
        skill=Skill.ARCHITECTURE,
        strategy=RetrievalStrategy.HYBRID,
        reasoning="Test reasoning",
        filters=QueryFilters()
    )

    planner = TaskPlanner(client=mock_client)
    plan = planner.plan(route)

    assert isinstance(plan, TaskPlan)
    assert plan.skill == "ArchitectureSkill"
    assert len(plan.tasks) == 3
    assert plan.tasks[0].type == "search_graph"
    assert plan.tasks[1].type == "search_metadata"
    assert plan.tasks[2].type == "generate_report"
    assert mock_client.models.generate_content.called
