"""Live tests for immediate explicit-fact capture and the consolidation threshold (M2.1.8).

Exercises the REAL ConversationAgent fact-check and the REAL consolidation
pipeline against M2.1.7's isolated test stores (test database, test Qdrant
collection, test Redis index — never production; the autouse guard enforces
this). Uses the identity "Jordan", distinct from the "Alex" used in M2.1.5's
and M2.1.6's tests, so a successful recall cannot be attributed to leftover
data from an earlier milestone.
"""

import pytest
import uuid_utils

from aether.agents._implementations.conversation import (
    EXPLICIT_FACT_IMPORTANCE,
    ConversationAgent,
)
from aether.agents.base import AgentContext, AgentTask
from aether.core.config import get_config
from aether.llm import Message
from aether.llm.router import LLMRouter
from aether.memory.api import MemoryAPI
from aether.memory.models import ContextPackage, MemoryType
from aether.tools.registry import ToolRegistry


async def _make_agent() -> tuple[LLMRouter, MemoryAPI, ConversationAgent]:
    router = LLMRouter()
    await router._event_bus.connect()
    memory = MemoryAPI(router)
    await memory.initialize()
    agent = ConversationAgent(
        memory_api=memory,
        llm_router=router,
        tool_registry=ToolRegistry(),
        event_bus=router._event_bus,
    )
    return router, memory, agent


def _empty_context(session_id: str, user_text: str) -> AgentContext:
    return AgentContext(
        session_id=session_id,
        conversation_history=[Message(role="user", content=user_text)],
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


def _turn(user_text: str) -> AgentTask:
    return AgentTask(
        description="Conversational turn",
        goal="Respond to the user's message",
        input_data={"text": user_text},
    )


@pytest.mark.integration
@pytest.mark.asyncio
async def test_explicit_fact_stored_as_clean_fact():
    router, memory, agent = await _make_agent()
    try:
        session_id = str(uuid_utils.uuid7())
        agent._session_id = session_id

        # 1. Drive one real conversational turn stating a durable fact.
        await agent.execute(
            _turn("My name is Jordan."), _empty_context(session_id, "My name is Jordan.")
        )

        # 2. Await the ACTUAL background fact-check task handle (no sleep hack).
        assert agent._fact_check_task is not None, "fact-check task should have been launched"
        await agent._fact_check_task

        # 3. A clean MemoryType.FACT now exists naming Jordan.
        facts = await memory.search("Jordan", memory_type=MemoryType.FACT, limit=20)
        jordan_facts = [f for f in facts if "jordan" in f.content.lower()]
        assert jordan_facts, "no MemoryType.FACT memory naming Jordan was captured"
        fact = jordan_facts[0]

        # Not a bare token, not a generic episode — a real stated fact sentence.
        assert fact.memory_type == MemoryType.FACT
        assert len(fact.content.split()) > 1, f"fact looks like a bare token: {fact.content!r}"

        # 4. Importance is high, distinctly above the per-turn episode importance.
        assert fact.importance >= 0.8, f"fact importance {fact.importance} is not high"
        assert fact.importance == pytest.approx(EXPLICIT_FACT_IMPORTANCE)

        # Cleanup so re-runs stay idempotent (isolated test DB, but keep it tidy).
        for f in jordan_facts:
            await memory.forget(f.id, reason="M2.1.8 fact-capture test cleanup")
    finally:
        await router._event_bus.disconnect()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_no_fact_produces_no_additional_memory():
    router, memory, agent = await _make_agent()
    try:
        session_id = str(uuid_utils.uuid7())
        agent._session_id = session_id

        # A pure question states no durable personal fact.
        question = "What is two plus two?"
        await agent.execute(_turn(question), _empty_context(session_id, question))

        assert agent._fact_check_task is not None
        await agent._fact_check_task

        # No FACT should have been fabricated from a non-fact turn.
        for keyword in ("two plus two", "four", "arithmetic"):
            facts = await memory.search(keyword, memory_type=MemoryType.FACT, limit=20)
            fabricated = [
                f
                for f in facts
                if "two plus two" in f.content.lower() or "arithmetic" in f.content.lower()
            ]
            assert not fabricated, f"a FACT was fabricated from a non-fact turn: {fabricated}"
    finally:
        await router._event_bus.disconnect()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_consolidation_triggers_at_three_messages():
    router = LLMRouter()
    await router._event_bus.connect()
    memory = MemoryAPI(router)
    await memory.initialize()
    try:
        # Threshold is now 3 (M2.1.8). Exactly 3 messages must NOT skip for
        # being below the threshold — contrast with M2.1.5's test proving a
        # below-threshold conversation DOES skip with 'insufficient_messages'.
        assert get_config().memory.consolidation_min_messages == 3

        conv = await memory.start_conversation("text")
        await memory.record_message(conv, "user", "I just adopted a cat named Mochi.")
        await memory.record_message(conv, "assistant", "Congratulations on adopting Mochi.")
        await memory.record_message(conv, "user", "Mochi is a grey tabby.")

        report = await memory.consolidate(conv)

        # The threshold was crossed: whatever happens next (summary success or an
        # environment-level summarization failure), it is NOT the below-threshold
        # skip. That distinction is exactly what proves the 5->3 change.
        assert report.skip_reason != "insufficient_messages"
    finally:
        await router._event_bus.disconnect()
