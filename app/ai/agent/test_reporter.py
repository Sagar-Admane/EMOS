import pytest
from unittest.mock import AsyncMock

from app.ai.agent.working_memory import WorkingMemory
from app.ai.agent.reporter import Reporter
from app.ai.models.schemas import LLMResponse, SkillOutput


@pytest.mark.anyio
async def test_reporter_generates_final_synthesis():
    # 1. Setup mock LLM generator
    mock_llm = AsyncMock()
    mock_response = LLMResponse(
        answer="Executive Summary: Success.\nTechnical Analysis: Clean run.",
        model_used="gemini-2.5-flash",
        skill_used="reporter"
    )
    mock_llm.generate_async.return_value = mock_response

    # 2. Setup WorkingMemory with mock steps
    memory = WorkingMemory(goal="Investigate memory leaks")
    memory.add_step(
        task_id=1,
        task_type="search_code",
        description="Search cache logic",
        result="Found unbound cache in cache.py"
    )

    # 3. Instantiate Reporter and run
    reporter = Reporter(llm_generator=mock_llm)
    response = await reporter.generate_report(memory)

    # 4. Asserts
    assert response.answer == "Executive Summary: Success.\nTechnical Analysis: Clean run."
    assert mock_llm.generate_async.called

    # Verify that the SkillOutput passed to the LLM generator contains our findings
    skill_output: SkillOutput = mock_llm.generate_async.call_args[0][0]
    assert isinstance(skill_output, SkillOutput)
    assert skill_output.skill_name == "reporter"
    assert "Investigate memory leaks" in skill_output.prompt
    assert "Found unbound cache in cache.py" in skill_output.prompt
    assert skill_output.temperature == 0.2
