import pytest
from unittest.mock import MagicMock

from app.ai.memory.conversation_memory import memory
from app.ai.agent.query_rewriter import QueryRewriter


@pytest.mark.anyio
async def test_query_rewriter_resolves_references():
    # 1. Setup mock client response
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "Who owns the auth-service?"
    mock_client.models.generate_content.return_value = mock_response

    # 2. Add history to memory
    session_id = "test-session-123"
    memory.clear(session_id)
    memory.add(session_id, "Explain the architecture of auth-service", "Auth-service handles logging and credentials.")

    # 3. Instantiate rewriter
    rewriter = QueryRewriter(client=mock_client)
    rewritten = await rewriter.rewrite("Who owns it?", session_id=session_id)

    # 4. Asserts
    assert rewritten == "Who owns the auth-service?"
    assert mock_client.models.generate_content.called

    # Clean up
    memory.clear(session_id)
