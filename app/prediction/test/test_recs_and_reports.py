import pytest
from unittest.mock import MagicMock

from app.prediction.models import DependencyGraph
from app.prediction.recommendation_engine import RecommendationEngine
from app.prediction.report_generator import ReportGenerator
from app.ai.agent.working_memory import WorkingMemory
from app.ai.retrieval.schemas import RetrievalResult, RetrievedDocument, RetrievalMetadata, RetrievalStatistics
from app.ai.router.enums import DataSource


def test_recommendation_engine_provides_safeguards():
    # 1. Setup mock activity logs
    owners_data = [{"owner": "charlie", "file_path": "app/auth.py"}]
    modifiers_data = [{"engineer": "charlie", "modifications": 5}]

    mock_owner_doc = RetrievedDocument(
        title="Owners", content="Owners", source=DataSource.NEO4J,
        document_type="file_ownership", metadata=RetrievalMetadata(data={"owners": owners_data}), score=1.0
    )
    mock_activity_doc = RetrievedDocument(
        title="Activity", content="Activity", source=DataSource.NEO4J,
        document_type="file_activity", metadata=RetrievalMetadata(data={"modifiers": modifiers_data}), score=1.0
    )

    memory = WorkingMemory(goal="Safeguards")
    memory.add_step(
        task_id=1, task_type="search_graph", description="Fetch", result="Mock",
        raw_result=RetrievalResult(documents=[mock_owner_doc, mock_activity_doc], statistics=RetrievalStatistics())
    )

    # 2. Get recommendations
    recs_engine = RecommendationEngine()
    reviewers = recs_engine.suggest_reviewers(memory, affected_files=["app/auth.py"])
    tests = recs_engine.suggest_tests(affected_files=["app/auth.py"])
    rollout = recs_engine.suggest_rollout(risk_score=75)
    monitoring = recs_engine.suggest_monitoring(affected_files=["app/auth.py"], affected_apis=["POST /login"])

    # 3. Asserts
    assert "charlie" in reviewers
    assert "pytest tests/test_auth.py" in tests
    assert "progressive rollout" in rollout.lower()
    assert any("POST /login" in m for m in monitoring)


def test_report_generator_formats_markdown():
    generator = ReportGenerator()
    
    impact = {
        "affected_files": ["app/auth.py", "app/main.py"],
        "affected_services": ["auth-service"],
        "affected_apis": ["POST /login"],
        "total_files": 2,
        "total_services": 1,
        "total_apis": 1
    }
    
    risk = {
        "score": 45,
        "level": "MEDIUM",
        "justifications": ["Directly affects 2 files.", "Single point of failure."]
    }
    
    recs = {
        "reviewers": ["charlie"],
        "tests": ["pytest tests/test_auth.py"],
        "rollout": "Deploy to canary 10%.",
        "monitoring": ["Monitor Latency"]
    }

    report = generator.generate_impact_report("app/auth.py", impact, risk, recs)
    
    assert "# Change Impact Assessment Report" in report
    assert "## Executive Summary" in report
    assert "Risk Score" in report
    assert "45/100" in report
    assert "Actionable Safeguards" in report
    assert "@charlie" in report
    assert "pytest tests/test_auth.py" in report
