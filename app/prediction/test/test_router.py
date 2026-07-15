import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient

from app.main import app
from app.prediction.models import DependencyGraph
from app.ai.agent.working_memory import WorkingMemory
from app.ai.retrieval.schemas import RetrievalResult, RetrievedDocument, RetrievalMetadata, RetrievalStatistics
from app.ai.router.enums import DataSource
from app.ai.models.schemas import LLMResponse


@pytest.fixture
def mock_working_memory():
    # Setup mock documents for service & endpoints
    services_data = [{"service": "auth-service", "files": ["app/auth.py"]}]
    endpoints_data = [{"method": "POST", "endpoint": "/login", "handler_file": "app/auth.py"}]
    owners_data = [{"owner": "alice", "file_path": "app/auth.py"}]
    modifiers_data = [{"engineer": "alice", "modifications": 10}]

    docs = [
        RetrievedDocument(
            title="Services", content="Services", source=DataSource.NEO4J, document_type="services",
            metadata=RetrievalMetadata(data={"services": services_data}), score=1.0
        ),
        RetrievedDocument(
            title="Endpoints", content="Endpoints", source=DataSource.NEO4J, document_type="api_endpoints",
            metadata=RetrievalMetadata(data={"endpoints": endpoints_data}), score=1.0
        ),
        RetrievedDocument(
            title="Owners", content="Owners", source=DataSource.NEO4J, document_type="file_ownership",
            metadata=RetrievalMetadata(data={"owners": owners_data}), score=1.0
        ),
        RetrievedDocument(
            title="Activity", content="Activity", source=DataSource.NEO4J, document_type="file_activity",
            metadata=RetrievalMetadata(data={"modifiers": modifiers_data}), score=1.0
        ),
        RetrievedDocument(
            title="Imports", content="Imports", source=DataSource.NEO4J, document_type="imports",
            metadata=RetrievalMetadata(data={"imports": [
                {"source": "app/main.py", "dependency": "app/auth.py"},
                {"source": "app/auth.py", "dependency": "app/db.py"}
            ]}), score=1.0
        )
    ]

    mem = WorkingMemory(goal="Test router")
    mem.add_step(
        task_id=1, task_type="search_graph", description="Fetch info", result="Text",
        raw_result=RetrievalResult(documents=docs, statistics=RetrievalStatistics())
    )
    return mem


@patch("app.prediction.router._executor.execute", new_callable=AsyncMock)
@patch("app.prediction.router._planner.plan")
@patch("app.prediction.router._router_service.route")
def test_predict_impact_endpoint(mock_route, mock_plan, mock_execute, mock_working_memory):
    mock_execute.return_value = mock_working_memory
    
    client = TestClient(app)
    response = client.post(
        "/predict/impact",
        json={"entity": "app/auth.py", "repo_id": 1, "max_depth": 3}
    )
    
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["entity"] == "app/auth.py"
    assert "dependency_graph" in res_data
    assert "impact_summary" in res_data
    assert "risk_profile" in res_data
    assert "blast_radius_tree" in res_data
    assert "markdown_report" in res_data
    
    # Assert specific risk score calculated
    # direct dependents: 0
    # indirect: 0
    # cycles: 0
    # bus factor: 1 -> penalty = 15
    # modifications: 10 -> penalty = 10
    # Score = 0 + 0 + 0 + 15 + 10 = 25 -> LOW RISK
    assert res_data["risk_profile"]["score"] == 25
    assert res_data["risk_profile"]["level"] == "LOW"


@patch("app.prediction.router._decision_engine.evaluate_decision", new_callable=AsyncMock)
@patch("app.prediction.router._executor.execute", new_callable=AsyncMock)
@patch("app.prediction.router._planner.plan")
@patch("app.prediction.router._router_service.route")
def test_evaluate_decision_endpoint(mock_route, mock_plan, mock_execute, mock_decision, mock_working_memory):
    mock_execute.return_value = mock_working_memory
    mock_decision.return_value = LLMResponse(
        answer="Recommendation: PROCEED. The dependency analysis shows minimal risk.",
        raw_output="Raw output",
        tokens_used=100,
        model_used="gemini-2.5-flash",
        skill_used="decision_advisor"
    )
    
    client = TestClient(app)
    response = client.post(
        "/predict/decision",
        json={
            "question": "Should we split UserService from main database?",
            "entity": "app/auth.py",
            "repo_id": 1,
            "max_depth": 3
        }
    )
    
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["question"] == "Should we split UserService from main database?"
    assert res_data["entity"] == "app/auth.py"
    assert "risk_score" in res_data
    assert "PROCEED" in res_data["evaluation_report"]
