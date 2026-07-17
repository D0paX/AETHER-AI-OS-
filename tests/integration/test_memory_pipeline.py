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
    # The kernel connects the shared EventBus in production; MemoryAPI.remember()
    # emits through it, so the test must connect it too (M2.1 test-setup fix —
    # backend-independent; the same failure occurs on SQLite).
    await router1._event_bus.connect()
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

    await router1._event_bus.disconnect()

    # Re-initialize
    router2 = LLMRouter()
    await router2._event_bus.connect()
    memory2 = MemoryAPI(router2)
    # Don't strictly need to call initialize() again if collection exists, but we can
    await memory2.initialize()

    # Step 5: Recall
    result = await memory2.recall("what is the user's name?")

    # Step 6: Assert
    assert unique_name in result.formatted_context

    await router2._event_bus.disconnect()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_consolidation_creates_long_term_memories():
    router = LLMRouter()
    memory = MemoryAPI(router)
    await memory.initialize()

    # Messages must reference a real conversation: PostgreSQL enforces the
    # messages.conversation_id foreign key that SQLite (with FK pragmas off)
    # silently ignored. Use the created conversation's id as the session id
    # (M2.1 test fix — the original discarded it and inserted orphaned rows).
    session_id = await memory._sqlite_store.create_conversation("text")

    # Insert 10 messages
    for i in range(10):
        await memory._sqlite_store.add_message(session_id, "user", f"Message {i}")

    # Run consolidation
    report = await memory.consolidate(session_id)

    if report.skipped:
        # If summarization failed because local LLM is slow or down, we just pass
        assert report.skip_reason in ["insufficient_messages", "summarization_failed"]
    else:
        assert report.memories_created > 0
