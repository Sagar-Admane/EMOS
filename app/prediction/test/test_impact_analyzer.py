import pytest
from unittest.mock import MagicMock

from app.prediction.models import DependencyGraph
from app.prediction.impact_analyzer import ImpactAnalyzer
from app.ai.agent.working_memory import WorkingMemory
from app.ai.retrieval.schemas import RetrievalResult, RetrievedDocument, RetrievalMetadata, RetrievalStatistics
from app.ai.router.enums import DataSource


def test_impact_analyzer_calculates_affected_elements():
    # 1. Setup mock services and api endpoints documents:
    services_data = [
        {"service": "auth-service", "files": ["app/main.py", "app/auth.py"]}
    ]
    endpoints_data = [
        {"method": "POST", "endpoint": "/login", "handler_file": "app/auth.py"},
        {"method": "GET", "endpoint": "/health", "handler_file": "app/main.py"}
    ]

    mock_service_doc = RetrievedDocument(
        title="Services",
        content="Services data",
        source=DataSource.NEO4J,
        document_type="services",
        metadata=RetrievalMetadata(data={"services": services_data}),
        score=1.0
    )

    mock_endpoint_doc = RetrievedDocument(
        title="Endpoints",
        content="Endpoints data",
        source=DataSource.NEO4J,
        document_type="api_endpoints",
        metadata=RetrievalMetadata(data={"endpoints": endpoints_data}),
        score=1.0
    )

    mock_retrieval = RetrievalResult(
        documents=[mock_service_doc, mock_endpoint_doc],
        statistics=RetrievalStatistics()
    )

    # 2. Add to WorkingMemory
    memory = WorkingMemory(goal="Analyze changes")
    memory.add_step(
        task_id=1,
        task_type="search_graph",
        description="Fetch architectural metadata",
        result="Mock text results",
        raw_result=mock_retrieval
    )

    # 3. Create dummy DependencyGraph
    # root: app/auth.py, dependents: [app/main.py, app/test_auth.py]
    dep_graph = DependencyGraph(
        root="app/auth.py",
        direct_dependencies=[],
        indirect_dependencies=[],
        dependents=["app/main.py", "app/test_auth.py"],
        call_chain=[],
        import_chain=[],
        cycles=[]
    )

    # 4. Analyze Impact
    analyzer = ImpactAnalyzer()
    report = analyzer.analyze_impact(dep_graph, memory)

    # 5. Asserts
    assert report["root"] == "app/auth.py"
    
    # Affected files should include root, main.py, and test_auth.py
    assert "app/auth.py" in report["affected_files"]
    assert "app/main.py" in report["affected_files"]
    assert "app/test_auth.py" in report["affected_files"]
    assert report["total_files"] == 3

    # Affected services should include "auth-service"
    assert "auth-service" in report["affected_services"]
    assert report["total_services"] == 1

    # Affected APIs should include "/login" (handled by auth.py) and "/health" (handled by main.py)
    assert "POST /login" in report["affected_apis"]
    assert "GET /health" in report["affected_apis"]
    assert report["total_apis"] == 2

    # Affected tests should include test_auth.py
    assert "app/test_auth.py" in report["affected_tests"]
    assert report["total_tests"] == 1
