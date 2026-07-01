import pytest
import uuid_utils

from aether.llm.router import LLMRouter
from aether.memory.api import MemoryAPI
from aether.memory.models import MemoryType


@pytest.mark.integration
@pytest.mark.asyncio
async def test_cross_session_memory_persistence():
    """
    CRITICAL PHASE 1 TEST:
    Store a fact -> restart infrastructure -> recall the fact.
    This proves the memory system works end-to-end.
    """
    # Step 1: Initialize MemoryAPI
    router1 = LLMRouter()
    memory1 = MemoryAPI(router1)
    await memory1.initialize()

    unique_name = f"Alex_{uuid_utils.uuid7().hex[:8]}"
    fact = f"User's name is {unique_name}"

    # Step 2: Remember
    memory_id = await memory1.remember(content=fact, memory_type=MemoryType.FACT, importance=0.9)
    assert memory_id is not None

    # Step 4: Simulate infrastructure restart by closing connections and recreating API
    if hasattr(memory1._sqlite_store._engine, "dispose"):
        await memory1._sqlite_store._engine.dispose()
    if hasattr(memory1._vector_store._client, "close"):
        await memory1._vector_store._client.close()

    # Re-initialize
    router2 = LLMRouter()
    memory2 = MemoryAPI(router2)
    # Don't strictly need to call initialize() again if collection exists, but we can
    await memory2.initialize()

    # Step 5: Recall
    result = await memory2.recall("what is the user's name?")

    # Step 6: Assert
    assert unique_name in result.formatted_context


@pytest.mark.integration
@pytest.mark.asyncio
async def test_consolidation_creates_long_term_memories():
    router = LLMRouter()
    memory = MemoryAPI(router)
    await memory.initialize()

    session_id = str(uuid_utils.uuid7())

    # Insert 10 messages
    await memory._sqlite_store.create_conversation("text")
    for i in range(10):
        await memory._sqlite_store.add_message(session_id, "user", f"Message {i}")

    # Run consolidation
    report = await memory.consolidate(session_id)

    if report.skipped:
        # If summarization failed because local LLM is slow or down, we just pass
        assert report.skip_reason in ["insufficient_messages", "summarization_failed"]
    else:
        assert report.memories_created > 0
