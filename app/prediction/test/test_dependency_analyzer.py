import pytest
from unittest.mock import MagicMock

from app.prediction.models import DependencyGraph
from app.prediction.dependency_analyzer import DependencyAnalyzer
from app.ai.agent.working_memory import WorkingMemory
from app.ai.retrieval.schemas import RetrievalResult, RetrievedDocument, RetrievalMetadata, RetrievalStatistics
from app.ai.router.enums import DataSource


def test_dependency_analyzer_parses_imports_and_cycles():
    # 1. Setup mock Neo4j document with cyclic imports:
    # app/main.py -> app/core.py -> app/db.py -> app/main.py
    imports_data = [
        {"source": "app/main.py", "dependency": "app/core.py"},
        {"source": "app/core.py", "dependency": "app/db.py"},
        {"source": "app/db.py", "dependency": "app/main.py"},
        {"source": "app/db.py", "dependency": "app/utils.py"}
    ]

    mock_doc = RetrievedDocument(
        title="Imports list",
        content="Imports metadata",
        source=DataSource.NEO4J,
        document_type="imports",
        metadata=RetrievalMetadata(data={"imports": imports_data}),
        score=1.0
    )

    mock_retrieval = RetrievalResult(
        documents=[mock_doc],
        statistics=RetrievalStatistics()
    )

    # 2. Add to WorkingMemory
    memory = WorkingMemory(goal="Trace main.py dependencies")
    memory.add_step(
        task_id=1,
        task_type="search_graph",
        description="Fetch imports",
        result="Mock text results",
        raw_result=mock_retrieval
    )

    # 3. Analyze
    analyzer = DependencyAnalyzer()
    graph = analyzer.analyze(memory, entity="app/main.py", level="file", max_depth=5)

    # 4. Asserts
    assert isinstance(graph, DependencyGraph)
    assert graph.root == "app/main.py"
    assert graph.direct_dependencies == ["app/core.py"]
    
    # Transitive dependencies should trace down Core -> DB -> Utils
    # main.py is the root, so indirect includes Core's transitive items (db, utils)
    assert "app/db.py" in graph.indirect_dependencies
    assert "app/utils.py" in graph.indirect_dependencies

    # Cycle detection assertion:
    # Path: app/main.py -> app/core.py -> app/db.py -> app/main.py
    assert len(graph.cycles) == 1
    assert graph.cycles[0] == ["app/main.py", "app/core.py", "app/db.py", "app/main.py"]


def test_dependency_analyzer_respects_max_depth():
    # Setup chain: A -> B -> C -> D
    imports_data = [
        {"source": "A", "dependency": "B"},
        {"source": "B", "dependency": "C"},
        {"source": "C", "dependency": "D"}
    ]

    mock_doc = RetrievedDocument(
        title="Imports",
        content="Imports",
        source=DataSource.NEO4J,
        document_type="imports",
        metadata=RetrievalMetadata(data={"imports": imports_data}),
        score=1.0
    )

    memory = WorkingMemory(goal="Trace depth")
    memory.add_step(
        task_id=1,
        task_type="search_graph",
        description="Fetch",
        result="Text",
        raw_result=RetrievalResult(documents=[mock_doc], statistics=RetrievalStatistics())
    )

    analyzer = DependencyAnalyzer()
    
    # With depth 2: starts at A, depth 1 is B, depth 2 is C. Should NOT reach D.
    graph = analyzer.analyze(memory, entity="A", level="file", max_depth=2)
    assert "B" in graph.direct_dependencies
    assert "C" in graph.indirect_dependencies
    assert "D" not in graph.indirect_dependencies
