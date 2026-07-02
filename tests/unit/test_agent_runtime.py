import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock

from aether.agents.runtime import AgentRuntime, AgentError
from aether.agents.base import BaseAgent, AgentTask, AgentContext, AgentResult
from aether.memory.models import ContextPackage

class DummyAgent(BaseAgent):
    name = "dummy"
    role = "dummy"
    llm_tier = None
    allowed_tools = []
    
    async def execute(self, task, context):
        if task.description == "timeout":
            await asyncio.sleep(10)
        elif task.description == "error":
            raise ValueError("test error")
        return AgentResult(run_id="pending", success=True, response="ok", actions_taken=[], memories_created=[], tasks_modified=[], llm_tokens_used=10, llm_cost_usd=0.1, duration_ms=100)

@pytest.fixture
def mock_db_session_factory():
    session = AsyncMock()
    factory = MagicMock()
    
    class CM:
        async def __aenter__(self):
            return session
        async def __aexit__(self, exc_type, exc_val, exc_tb):
            pass
            
    factory.return_value = CM()
    return factory, session

@pytest.mark.asyncio
async def test_agent_runtime_success(mock_db_session_factory):
    factory, session = mock_db_session_factory
    event_bus = AsyncMock()
    runtime = AgentRuntime(None, None, None, event_bus, factory)
    runtime.register_agent("dummy", DummyAgent)
    
    task = AgentTask(description="test", goal="test", timeout_seconds=1.0)
    # memory_context conceptually shouldn't be None, but for this mock test it's fine.
    context = AgentContext(session_id="s1", conversation_history=[], memory_context=ContextPackage(memories=[], total_found=0, token_estimate=0, formatted_context="", retrieval_query="", retrieval_duration_ms=0), active_tasks=[])
    
    result = await runtime.execute("dummy", task, context)
    assert result.success is True
    assert result.response == "ok"
    assert result.llm_tokens_used == 10
    
    # Check DB
    assert session.add.called
    assert session.commit.called
    
    # Check Events
    event_bus.emit.assert_any_call("agent.run.started", {"run_id": result.run_id, "agent_name": "dummy", "session_id": "s1"})
    event_bus.emit.assert_any_call("agent.run.completed", {"run_id": result.run_id, "agent_name": "dummy", "session_id": "s1", "success": True, "error": None})

@pytest.mark.asyncio
async def test_agent_runtime_timeout(mock_db_session_factory):
    factory, session = mock_db_session_factory
    event_bus = AsyncMock()
    runtime = AgentRuntime(None, None, None, event_bus, factory)
    runtime.register_agent("dummy", DummyAgent)
    
    task = AgentTask(description="timeout", goal="test", timeout_seconds=0.1)
    context = AgentContext(session_id="s1", conversation_history=[], memory_context=ContextPackage(memories=[], total_found=0, token_estimate=0, formatted_context="", retrieval_query="", retrieval_duration_ms=0), active_tasks=[])
    
    result = await runtime.execute("dummy", task, context)
    assert result.success is False
    assert result.error == "Timeout"

@pytest.mark.asyncio
async def test_agent_runtime_exception(mock_db_session_factory):
    factory, session = mock_db_session_factory
    event_bus = AsyncMock()
    runtime = AgentRuntime(None, None, None, event_bus, factory)
    runtime.register_agent("dummy", DummyAgent)
    
    task = AgentTask(description="error", goal="test", timeout_seconds=1.0)
    context = AgentContext(session_id="s1", conversation_history=[], memory_context=ContextPackage(memories=[], total_found=0, token_estimate=0, formatted_context="", retrieval_query="", retrieval_duration_ms=0), active_tasks=[])
    
    result = await runtime.execute("dummy", task, context)
    assert result.success is False
    assert result.error == "test error"

@pytest.mark.asyncio
async def test_agent_runtime_unknown_agent():
    runtime = AgentRuntime(None, None, None, None, None)
    task = AgentTask(description="test", goal="test")
    context = AgentContext(session_id="s1", conversation_history=[], memory_context=ContextPackage(memories=[], total_found=0, token_estimate=0, formatted_context="", retrieval_query="", retrieval_duration_ms=0), active_tasks=[])
    with pytest.raises(AgentError):
        await runtime.execute("unknown", task, context)
