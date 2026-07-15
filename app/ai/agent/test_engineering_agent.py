import pytest
from unittest.mock import AsyncMock, MagicMock

from app.ai.agent.engineering_agent import EngineeringAgent
from app.ai.models.schemas import AIRequest, AIResponse, LLMResponse
from app.ai.router.schemas import RouteDecision, QueryFilters
from app.ai.router.enums import Intent, Skill, DataSource, RetrievalStrategy
from app.ai.retrieval.schemas import RetrievalResult, RetrievedDocument, RetrievalStatistics
from app.ai.context.schemas import ContextPackage, Citation, ContextMetadata
from app.ai.memory.conversation_memory import memory


@pytest.mark.anyio
async def test_engineering_agent_full_stage5_pipeline():
    # 1. Setup session_id
    session_id = "test-agent-session"
    memory.clear(session_id)

    # 2. Setup mock router
    mock_router = MagicMock()
    route_decision = RouteDecision(
        question="Explain the authentication architecture",
        intent=Intent.ARCHITECTURE,
        confidence=0.9,
        required_sources=[DataSource.QDRANT],
        skill=Skill.ARCHITECTURE,
        strategy=RetrievalStrategy.VECTOR,
        reasoning="Test routing",
        filters=QueryFilters()
    )
    mock_router.route.return_value = route_decision

    # 3. Setup mock orchestrator and context builder
    mock_orchestrator = AsyncMock()
    mock_orchestrator.retrieve.return_value = RetrievalResult(
        documents=[
            RetrievedDocument(
                title="auth.py",
                content="def authenticate(): pass",
                source=DataSource.QDRANT,
                document_type="code_file",
                score=0.95
            )
        ],
        statistics=RetrievalStatistics(total_documents=1, sources_used=[DataSource.QDRANT])
    )

    mock_context_builder = MagicMock()
    mock_context_builder.build.return_value = ContextPackage(
        summary="Summary of context",
        documents=[
            {
                "index": 1,
                "title": "auth.py",
                "source": "qdrant",
                "document_type": "code_file",
                "content": "def authenticate(): pass",
                "score": 0.95
            }
        ],
        citations=[
            Citation(index=1, title="auth.py", source=DataSource.QDRANT, document_type="code_file", score=0.95)
        ],
        metadata=ContextMetadata(total_documents_before_compression=1, total_documents_after_compression=1)
    )

    # 4. Setup mock LLM generator (used by rewriter and reporter)
    mock_llm = AsyncMock()
    # Mock LLM returns for:
    # - Query Rewriter (first call, if any, wait, we mock client for rewriter or rewriter itself? We can mock query_rewriter directly)
    # - Reporter (generate_async)
    mock_llm.generate_async.return_value = LLMResponse(
        answer="Final report: auth architecture details.",
        model_used="gemini-2.5-flash",
        skill_used="architecture"
    )

    # Mock QueryRewriter
    mock_rewriter = AsyncMock()
    mock_rewriter.rewrite.return_value = "Explain the authentication architecture"

    # Instantiate Agent with mocked components
    agent = EngineeringAgent(
        router=mock_router,
        orchestrator=mock_orchestrator,
        context_builder=mock_context_builder,
        llm_generator=mock_llm,
        query_rewriter=mock_rewriter
    )

    # Make Request
    request = AIRequest(
        question="Explain the authentication architecture",
        repo_id=1,
        session_id=session_id
    )

    response = await agent.answer(request)

    # Asserts
    assert isinstance(response, AIResponse)
    assert response.answer == "Final report: auth architecture details."
    assert response.question == "Explain the authentication architecture"
    assert response.skill_used == "architecture"
    assert "search_code" in response.sources_used
    assert response.session_id == session_id

    # Verify history was saved
    history = memory.get_history(session_id)
    assert len(history) == 1
    assert history[0].question == "Explain the authentication architecture"
    assert history[0].answer == "Final report: auth architecture details."

    # Clean up
    memory.clear(session_id)
