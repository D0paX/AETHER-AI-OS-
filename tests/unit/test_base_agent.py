from unittest.mock import AsyncMock, MagicMock

import pytest

from aether.agents.base import AgentResult, BaseAgent
from aether.llm import ModelTier
from aether.memory.models import MemoryType
from aether.tools.base import ToolResult


class DummyAgent(BaseAgent):
    name = "dummy"
    role = "dummy role"
    llm_tier = ModelTier.LOCAL
    allowed_tools = ["dummy_tool"]

    async def execute(self, task, context):
        return AgentResult(
            run_id="r1",
            success=True,
            response="ok",
            actions_taken=[],
            memories_created=[],
            tasks_modified=[],
            llm_tokens_used=0,
            llm_cost_usd=0.0,
            duration_ms=0,
        )


@pytest.mark.asyncio
async def test_base_agent_recall():
    memory_api = AsyncMock()
    memory_api.recall.return_value = "package"
    agent = DummyAgent(memory_api, None, None, None)
    res = await agent._recall("query")
    assert res == "package"
    assert agent._memory_reads_count == 1
    memory_api.recall.assert_called_once()


@pytest.mark.asyncio
async def test_base_agent_remember():
    memory_api = AsyncMock()
    memory_api.remember.return_value = "mem1"
    agent = DummyAgent(memory_api, None, None, None)
    agent._session_id = "s1"
    res = await agent._remember("content", MemoryType.EPISODE)
    assert res == "mem1"
    memory_api.remember.assert_called_with(
        content="content", memory_type=MemoryType.EPISODE, importance=0.5, session_id="s1"
    )


@pytest.mark.asyncio
async def test_base_agent_invoke_tool():
    tool = AsyncMock()
    tool.check_permissions.return_value = None
    tool.input_schema.return_value = {"k": "v"}
    tool.execute.return_value = ToolResult(success=True)
    registry = MagicMock()
    registry.get.return_value = tool
    event_bus = AsyncMock()

    agent = DummyAgent(None, None, registry, event_bus)
    res = await agent._invoke_tool("dummy_tool", {"k": "v"})
    assert res.success is True
    event_bus.emit.assert_called_with(
        "tool.execution.completed",
        {"tool_name": "dummy_tool", "success": True, "agent_name": "dummy", "session_id": None},
    )


@pytest.mark.asyncio
async def test_base_agent_invoke_tool_unallowed():
    agent = DummyAgent(None, None, None, None)
    res = await agent._invoke_tool("unallowed_tool", {})
    assert res.success is False
    assert "not in allowed_tools" in res.error
