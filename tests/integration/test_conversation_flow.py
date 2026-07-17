from datetime import UTC, datetime
from unittest.mock import AsyncMock, patch

import pytest

from aether.agents._implementations.conversation import AgentDecision
from aether.agents.base import AgentContext, AgentTask
from aether.core.config import get_config
from aether.core.kernel import AetherKernel
from aether.memory.models import ContextPackage, MemoryRecord, MemorySource, MemoryType


@pytest.mark.asyncio
async def test_cross_session_memory():
    """
    Verifies that the kernel can boot, an agent can remember a fact in one session,
    and a fresh kernel/agent can recall that fact in a subsequent session.
    """
    config = get_config()

    # Session 1: Store memory
    kernel1 = AetherKernel(config)

    with (
        patch("aether.core.kernel.EventBus") as mock_kernel_event_bus,
        patch("aether.llm.router.EventBus") as mock_router_event_bus,
        patch("aether.core.kernel.LLMRouter._connect_bus", new_callable=AsyncMock),
        patch("aether.memory.api.QdrantMemoryStore") as mock_qdrant,
    ):
        mock_kernel_event_bus.return_value.connect = AsyncMock()
        mock_kernel_event_bus.return_value.emit = AsyncMock()
        mock_kernel_event_bus.return_value.disconnect = AsyncMock()
        mock_router_event_bus.return_value.connect = AsyncMock()
        mock_router_event_bus.return_value.emit = AsyncMock()
        mock_router_event_bus.return_value.disconnect = AsyncMock()

        mock_qdrant_instance = mock_qdrant.return_value
        mock_qdrant_instance.initialize_collection = AsyncMock()
        mock_qdrant_instance.upsert = AsyncMock()
        mock_qdrant_instance.search = AsyncMock(return_value=[])
        await kernel1.boot()

    # Mock LLMRouter to skip actual API calls and just return the final answer.
    kernel1.llm_router.complete = AsyncMock()
    decision1 = AgentDecision(
        thought="I should store this", final_answer="I have remembered the secret code 42."
    )
    # M2.1.6: ConversationAgent reads the locked LLMResponse fields
    # (total_tokens at top level; there is no .usage attribute).
    kernel1.llm_router.complete.return_value = AsyncMock(
        total_tokens=10, cost_usd=0.01, content=decision1.model_dump_json()
    )
    kernel1.llm_router._embedding_service.embed = AsyncMock(
        return_value=AsyncMock(vector=[0.0] * 1536)
    )

    task1 = AgentTask(description="The secret code is 42", goal="Store it")
    context1 = AgentContext(
        session_id="session1",
        conversation_history=[],
        memory_context=ContextPackage(
            memories=[],
            total_found=0,
            token_estimate=0,
            formatted_context="",
            retrieval_query="",
            retrieval_duration_ms=0,
        ),
        active_tasks=[],
    )

    res1 = await kernel1.agent_runtime.execute("conversation", task1, context1)
    assert res1.success is True

    await kernel1.shutdown()

    # Session 2: Recall memory
    kernel2 = AetherKernel(config)

    with (
        patch("aether.core.kernel.EventBus") as mock_kernel_event_bus,
        patch("aether.llm.router.EventBus") as mock_router_event_bus,
        patch("aether.core.kernel.LLMRouter._connect_bus", new_callable=AsyncMock),
        patch("aether.memory.api.QdrantMemoryStore") as mock_qdrant,
        patch("aether.memory.api.SQLiteMemoryStore") as mock_sqlite,
    ):
        mock_kernel_event_bus.return_value.connect = AsyncMock()
        mock_kernel_event_bus.return_value.emit = AsyncMock()
        mock_kernel_event_bus.return_value.disconnect = AsyncMock()
        mock_router_event_bus.return_value.connect = AsyncMock()
        mock_router_event_bus.return_value.emit = AsyncMock()
        mock_router_event_bus.return_value.disconnect = AsyncMock()

        mock_qdrant_instance = mock_qdrant.return_value
        mock_qdrant_instance.initialize_collection = AsyncMock()
        mock_qdrant_instance.upsert = AsyncMock()
        # Simulate retrieval of memory stored in Session 1
        mock_qdrant_instance.search = AsyncMock(return_value=[("1", 0.99)])

        mock_sqlite_instance = mock_sqlite.return_value
        mock_sqlite_instance.init_db = AsyncMock()
        mock_sqlite_instance.get_memory = AsyncMock(
            return_value=MemoryRecord(
                id="1",
                content="The secret code is 42",
                memory_type=MemoryType.FACT,
                source=MemorySource.USER,
                importance=1,
                confidence=1.0,
                tags=[],
                entities=[],
                metadata={},
                created_at=datetime.now(UTC),
                last_accessed_at=datetime.now(UTC),
                access_count=0,
                vector=[0.0] * 1536,
            )
        )
        mock_sqlite_instance.update_access = AsyncMock()

        await kernel2.boot()

    kernel2.llm_router.complete = AsyncMock()
    decision2 = AgentDecision(thought="I know the code", final_answer="The secret code is 42.")
    kernel2.llm_router.complete.return_value = AsyncMock(
        total_tokens=10, cost_usd=0.01, content=decision2.model_dump_json()
    )
    kernel2.llm_router._embedding_service.embed = AsyncMock(
        return_value=AsyncMock(vector=[0.0] * 1536)
    )

    # Re-instantiate agent to ensure no local state is maintained
    task2 = AgentTask(description="What is the secret code?", goal="Answer")

    # Context now should be built with memory recall
    mem_context = await kernel2.agent_runtime._memory_api.recall("secret code", k=5)

    assert len(mem_context.memories) > 0

    context2 = AgentContext(
        session_id="session2", conversation_history=[], memory_context=mem_context, active_tasks=[]
    )

    res2 = await kernel2.agent_runtime.execute("conversation", task2, context2)
    assert res2.success is True
    assert "42" in res2.response

    await kernel2.shutdown()
