"""Live end-to-end consolidation test (M2.1.5 centerpiece deliverable).

Exercises the REAL consolidation path with no mocking of the pipeline, the
store, or MemoryAPI: messages are persisted through the new public
conversation accessors, consolidate() summarizes the transcript and extracts
facts through the live local LLM, and the resulting memories are proven
retrievable through recall(). Requires the full stack (PostgreSQL/SQLite via
config, Qdrant, Redis) and a working ModelTier.LOCAL model (Ollama).
"""

import pytest
import uuid_utils

from aether.core.config import get_config
from aether.llm.router import LLMRouter
from aether.memory.api import MemoryAPI
from aether.memory.models import MemoryFilter, MemoryType


async def _make_memory_api() -> tuple[LLMRouter, MemoryAPI]:
    router = LLMRouter()
    await router._event_bus.connect()
    memory = MemoryAPI(router)
    await memory.initialize()
    return router, memory


def _memory_ids(package) -> set[str]:
    return {record.id for record in package.memories}


@pytest.mark.integration
@pytest.mark.asyncio
async def test_consolidation_produces_real_memories():
    router, memory = await _make_memory_api()
    try:
        codename = f"Starlight{uuid_utils.uuid7().hex[:6]}"
        probe_query = f"What is the codename of the user's tracking project {codename}?"

        # Snapshot recall results BEFORE consolidation so we can prove a new
        # memory appears afterward (asserting consolidate() merely returned
        # is not sufficient fidelity).
        before = await memory.recall(probe_query)
        before_ids = _memory_ids(before)

        # 1. Start a session-equivalent conversation.
        conversation_id = await memory.start_conversation("text")

        # 2. Record a realistic conversation establishing verifiable facts.
        min_messages = get_config().memory.consolidation_min_messages
        turns = [
            ("user", f"I started a new satellite tracking project called {codename}."),
            ("assistant", f"Noted — {codename} is your satellite tracking project."),
            ("user", f"{codename} is written in Python and tracks satellites in real time."),
            ("assistant", f"Understood, {codename} tracks satellites in real time using Python."),
            ("user", f"Please remember the project codename {codename} for future sessions."),
            ("assistant", f"I will remember that your project is called {codename}."),
        ]
        assert len(turns) >= min_messages
        for role, content in turns:
            await memory.record_message(conversation_id, role, content)

        # 3. Run the REAL consolidation pipeline (live local LLM).
        report = await memory.consolidate(conversation_id)

        # 4. The report proves consolidation executed, not skipped.
        assert report.skipped is False, f"consolidation skipped: {report.skip_reason}"
        assert report.memories_created > 0

        # 5. Fidelity: recall now surfaces at least one memory that did not
        # exist before consolidation ran.
        after = await memory.recall(probe_query)
        new_ids = _memory_ids(after) - before_ids
        assert new_ids, "consolidation created memories but recall() surfaced none of them"

        # 6. A MemoryType.EPISODE summary memory exists for the session.
        episodes = await memory.recall(
            probe_query,
            filters=MemoryFilter(memory_types=[MemoryType.EPISODE]),
        )
        new_episode_ids = _memory_ids(episodes) - before_ids
        assert new_episode_ids, "no new EPISODE summary memory found for the session"
    finally:
        await router._event_bus.disconnect()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_consolidation_skips_below_message_threshold():
    router, memory = await _make_memory_api()
    try:
        conversation_id = await memory.start_conversation("text")

        min_messages = get_config().memory.consolidation_min_messages
        for i in range(min_messages - 1):
            await memory.record_message(conversation_id, "user", f"short message {i}")

        report = await memory.consolidate(conversation_id)

        assert report.skipped is True
        assert report.skip_reason == "insufficient_messages"
        assert report.memories_created == 0
    finally:
        await router._event_bus.disconnect()
