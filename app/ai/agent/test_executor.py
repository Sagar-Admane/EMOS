import pytest
from unittest.mock import AsyncMock, MagicMock

from app.ai.agent.planner import TaskPlan, Task
from app.ai.agent.executor import TaskExecutor
from app.ai.agent.working_memory import WorkingMemory
from app.ai.router.schemas import RouteDecision, QueryFilters
from app.ai.router.enums import Intent, Skill, DataSource, RetrievalStrategy
from app.ai.retrieval.schemas import RetrievalResult, RetrievedDocument, RetrievalStatistics
from app.ai.context.schemas import ContextPackage, Citation, ContextMetadata


@pytest.mark.anyio
async def test_task_executor_runs_tasks_and_records_in_memory():
    # 1. Setup mock RetrievalResult and ContextPackage
    mock_retrieval_result = RetrievalResult(
        documents=[
            RetrievedDocument(
                title="test_file.py",
                content="def hello(): pass",
                source=DataSource.QDRANT,
                document_type="code_file",
                score=0.9
            )
        ],
        statistics=RetrievalStatistics(total_documents=1, sources_used=[DataSource.QDRANT])
    )

    mock_context_package = ContextPackage(
        summary="Context summary",
        documents=[
            {
                "index": 1,
                "title": "test_file.py",
                "source": "qdrant",
                "document_type": "code_file",
                "content": "def hello(): pass",
                "score": 0.9
            }
        ],
        citations=[
            Citation(index=1, title="test_file.py", source=DataSource.QDRANT, document_type="code_file", score=0.9)
        ],
        metadata=ContextMetadata(total_documents_before_compression=1, total_documents_after_compression=1)
    )

    # 2. Setup mock Orchestrator and ContextBuilder
    mock_orchestrator = AsyncMock()
    mock_orchestrator.retrieve.return_value = mock_retrieval_result

    mock_context_builder = MagicMock()
    mock_context_builder.build.return_value = mock_context_package

    # 3. Instantiate TaskExecutor
    executor = TaskExecutor(
        orchestrator=mock_orchestrator,
        context_builder=mock_context_builder
    )

    # 4. Create dummy Plan and parent RouteDecision
    plan = TaskPlan(
        goal="Explain hello function",
        skill="ArchitectureSkill",
        tasks=[
            Task(id=1, type="search_code", description="Search hello implementation"),
            Task(id=2, type="search_graph", description="Trace hello dependencies"),
            Task(id=3, type="generate_report", description="Synthesize report")
        ]
    )

    parent_route = RouteDecision(
        question="Explain hello function",
        intent=Intent.ARCHITECTURE,
        confidence=0.9,
        required_sources=[DataSource.QDRANT, DataSource.NEO4J],
        skill=Skill.ARCHITECTURE,
        strategy=RetrievalStrategy.HYBRID,
        reasoning="Reasoning text",
        filters=QueryFilters(repository="demo")
    )

    # 5. Execute
    memory = await executor.execute(plan, parent_route)

    # 6. Asserts
    assert isinstance(memory, WorkingMemory)
    assert memory.goal == "Explain hello function"
    assert len(memory.steps) == 2  # generate_report should be skipped

    # Check Task 1
    assert memory.steps[0]["task_id"] == 1
    assert memory.steps[0]["type"] == "search_code"
    assert "test_file.py" in memory.steps[0]["result"]

    # Check Task 2
    assert memory.steps[1]["task_id"] == 2
    assert memory.steps[1]["type"] == "search_graph"
    assert "test_file.py" in memory.steps[1]["result"]

    # Verify mocks were called
    assert mock_orchestrator.retrieve.call_count == 2
    assert mock_context_builder.build.call_count == 2

    # Check text rendering of memory
    memory_text = memory.as_text()
    assert "INVESTIGATION GOAL: Explain hello function" in memory_text
    assert "[Task 1 - SEARCH_CODE]" in memory_text
    assert "def hello(): pass" in memory_text
