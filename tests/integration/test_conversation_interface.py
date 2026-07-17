"""Live tests for the corrected conversation interfaces (M2.1.6).

Drives the REAL AetherCLI._handle_conversation() and the REAL
/conversation/message endpoint over a fully booted kernel (live PostgreSQL,
Qdrant, Redis). Only AgentRuntime.execute is replaced with a deterministic
canned AgentResult — the handlers under test, SessionManager, and MemoryAPI
all run for real, so the persistence assertions prove the M2.1.5 two-item
delta contract end to end.
"""

from unittest.mock import AsyncMock

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from rich.console import Console

from aether.agents.base import AgentResult
from aether.core.kernel import AetherKernel
from aether.interfaces.api import app
from aether.interfaces.cli import AetherCLI
from aether.session.models import SessionMode

CANNED_RESPONSE = "Teal is a lovely choice; I will remember it."


def _canned_result() -> AgentResult:
    return AgentResult(
        run_id="run-fixed",
        success=True,
        response=CANNED_RESPONSE,
        actions_taken=[],
        memories_created=[],
        tasks_modified=[],
        llm_tokens_used=12,
        llm_cost_usd=0.0,
        duration_ms=5,
    )


@pytest_asyncio.fixture
async def booted_kernel():
    kernel = AetherKernel()
    await kernel.boot()
    # The handlers are the units under test; the agent itself is exercised by
    # its own tests. A canned result keeps this deterministic.
    kernel.agent_runtime.execute = AsyncMock(return_value=_canned_result())
    yield kernel
    await kernel.shutdown()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_cli_conversation_turn_persists_and_displays(booted_kernel):
    cli = AetherCLI(booted_kernel)
    cli.console = Console(record=True, width=100)
    cli.session = await booted_kernel.session_manager.start_session(SessionMode.TEXT)
    session_id = cli.session.id

    before = await booted_kernel.memory_api.get_conversation_messages(session_id)

    await cli._handle_conversation("My favorite color is teal.")

    # 1. No exception was raised, and the displayed text is the real
    # AgentResult.response (not any nonexistent .output field).
    output = cli.console.export_text()
    assert CANNED_RESPONSE in output

    # 2. Exactly two new messages persisted — the user's input and the
    # agent's response — proving update_context() received a correct
    # two-item delta, not the full history and not a bypass.
    after = await booted_kernel.memory_api.get_conversation_messages(session_id)
    new_messages = after[len(before) :]
    assert len(new_messages) == 2
    assert new_messages[0].role == "user"
    assert new_messages[0].content == "My favorite color is teal."
    assert new_messages[1].role == "assistant"
    assert new_messages[1].content == CANNED_RESPONSE


@pytest.mark.integration
@pytest.mark.asyncio
async def test_api_conversation_turn_persists(booted_kernel):
    app.state.kernel = booted_kernel
    session = await booted_kernel.session_manager.start_session(SessionMode.TEXT)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        resp = await client.post(
            "/conversation/message",
            json={"session_id": session.id, "content": "Remember that my dog is called Nova."},
        )

    assert resp.status_code == 200
    body = resp.json()
    assert body["response"] == CANNED_RESPONSE
    assert body["session_id"] == session.id
    assert body["agent_run_id"] == "run-fixed"

    messages = await booted_kernel.memory_api.get_conversation_messages(session.id)
    assert len(messages) == 2
    assert messages[0].role == "user"
    assert messages[0].content == "Remember that my dog is called Nova."
    assert messages[1].role == "assistant"
    assert messages[1].content == CANNED_RESPONSE


@pytest.mark.integration
@pytest.mark.asyncio
async def test_build_agent_context_assembles_correctly(booted_kernel):
    session = await booted_kernel.session_manager.start_session(SessionMode.TEXT)
    user_input = "What tasks do I have open right now?"

    context = await booted_kernel.session_manager.build_agent_context(session.id, user_input)

    assert context.session_id == session.id
    # The current user input is appended as the final history message so the
    # agent actually sees the turn's input (approved M2.1.6 design).
    assert context.conversation_history[-1].role == "user"
    assert context.conversation_history[-1].content == user_input
    # memory_context comes from a real MemoryAPI.recall() call, not an empty
    # default-constructed package.
    assert context.memory_context.retrieval_query == user_input
    assert context.memory_context.retrieval_duration_ms >= 0
    assert isinstance(context.active_tasks, list)
