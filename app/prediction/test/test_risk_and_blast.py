import pytest
from unittest.mock import MagicMock

from app.prediction.models import DependencyGraph
from app.prediction.risk_engine import RiskEngine
from app.prediction.blast_radius import BlastRadiusAnalyzer
from app.ai.agent.working_memory import WorkingMemory
from app.ai.retrieval.schemas import RetrievalResult, RetrievedDocument, RetrievalMetadata, RetrievalStatistics
from app.ai.router.enums import DataSource


def test_risk_engine_calculates_correct_score():
    # 1. Setup mock ownership and activity documents:
    # 2 modifiers, total modifications = 12, 1 formal owner
    owners_data = [{"owner": "alice", "file_path": "app/auth.py"}]
    modifiers_data = [
        {"engineer": "alice", "modifications": 8},
        {"engineer": "bob", "modifications": 4}
    ]

    mock_owner_doc = RetrievedDocument(
        title="Owners",
        content="Owners",
        source=DataSource.NEO4J,
        document_type="file_ownership",
        metadata=RetrievalMetadata(data={"owners": owners_data}),
        score=1.0
    )

    mock_activity_doc = RetrievedDocument(
        title="Activity",
        content="Activity",
        source=DataSource.NEO4J,
        document_type="file_activity",
        metadata=RetrievalMetadata(data={"modifiers": modifiers_data}),
        score=1.0
    )

    mock_retrieval = RetrievalResult(
        documents=[mock_owner_doc, mock_activity_doc],
        statistics=RetrievalStatistics()
    )

    memory = WorkingMemory(goal="Calculate risk")
    memory.add_step(
        task_id=1,
        task_type="search_graph",
        description="Fetch owners and mods",
        result="Mock text results",
        raw_result=mock_retrieval
    )

    # Create DependencyGraph with 2 dependents, 1 cycle
    dep_graph = DependencyGraph(
        root="app/auth.py",
        direct_dependencies=["app/core.py"],
        indirect_dependencies=["app/db.py"],
        dependents=["app/main.py", "app/routes.py"],
        call_chain=[],
        import_chain=[],
        cycles=[["app/auth.py", "app/core.py", "app/auth.py"]]
    )

    # 2. Calculate Risk
    risk_engine = RiskEngine()
    risk_report = risk_engine.calculate_risk(dep_graph, memory)

    # 3. Asserts
    # dependent_weight = 2 * 8 = 16
    # indirect_weight = 1 * 3 = 3
    # cycle_penalty = 15 (since cycles present)
    # bus_factor = 1 (formal owner count is 1) -> bus_factor_penalty = 15
    # total modifications = 12 -> frequency_penalty = (12 // 5) * 5 = 10
    # Expected Score = 16 + 3 + 15 + 15 + 10 = 59
    assert risk_report["score"] == 59
    assert risk_report["level"] == "MEDIUM"
    assert risk_report["bus_factor"] == 1
    assert risk_report["total_modifications"] == 12
    assert any("Warning: Single point of failure" in j for j in risk_report["justifications"])


def test_blast_radius_models_correct_scope():
    dep_graph = DependencyGraph(
        root="app/auth.py",
        direct_dependencies=[],
        indirect_dependencies=["app/db.py", "app/utils.py"],
        dependents=["app/main.py"],
        call_chain=[],
        import_chain=[],
        cycles=[]
    )

    analyzer = BlastRadiusAnalyzer()
    
    # 1. Test change tree build
    tree = analyzer.build_change_tree(dep_graph)
    assert tree["name"] == "app/auth.py"
    assert len(tree["children"]) == 3  # 1 dependent + 2 transitive dependents
    
    # 2. Test scope estimation
    scope = analyzer.estimate_scope(dep_graph)
    assert scope["root"] == "app/auth.py"
    assert scope["direct_impact_count"] == 1
    assert scope["indirect_impact_count"] == 2
    assert scope["total_impact_count"] == 3
    assert scope["scope_classification"] == "SIGNIFICANT"
