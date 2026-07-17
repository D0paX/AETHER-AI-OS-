import asyncio
import json
from datetime import UTC, datetime
from unittest.mock import AsyncMock

import pytest
from redis.asyncio import Redis

from aether.core.events import EventBus
from aether.memory.api import MemoryAPI
from aether.memory.models import ContextPackage
from aether.session.manager import SessionManager
from aether.session.models import SessionContext, SessionMode
from aether.session.startup import SessionStartupBuilder
from aether.tasks.models import Task, TaskPriority, TaskStatus


@pytest.fixture
def session_manager():
    # M2.1.5: SessionManager's constructor was corrected — conversation
    # persistence and consolidation now flow through MemoryAPI; there is no
    # db_session_factory and no direct consolidation pipeline.
    startup_builder = AsyncMock(spec=SessionStartupBuilder)
    memory_api = AsyncMock(spec=MemoryAPI)
    memory_api.start_conversation.return_value = "01932e4f-a7c2-7000-b3e2-000000000001"
    event_bus = AsyncMock(spec=EventBus)
    redis_client = AsyncMock(spec=Redis)
    redis_client.set = AsyncMock()
    redis_client.get = AsyncMock()
    redis_client.delete = AsyncMock()

    manager = SessionManager(
        startup_builder=startup_builder,
        memory_api=memory_api,
        event_bus=event_bus,
        redis_client=redis_client,
    )
    return manager


@pytest.mark.asyncio
async def test_start_session_creates_conversation_via_memory_api(session_manager):
    session_manager._startup_builder.build_context.return_value = SessionContext(
        session_id="dummy",
        messages=[],
        active_tasks=[],
        memory_context=ContextPackage(
            memories=[],
            total_found=0,
            token_estimate=0,
            formatted_context="",
            retrieval_query="",
            retrieval_duration_ms=0,
        ),
        working_summary="",
        last_activity=datetime.now(UTC),
    )

    session = await session_manager.start_session()

    assert session is not None
    assert session.status == "active"
    session_manager._memory_api.start_conversation.assert_called_once_with("text")
    assert session.id == "01932e4f-a7c2-7000-b3e2-000000000001"


@pytest.mark.asyncio
async def test_start_session_caches_context_in_redis(session_manager):
    session_id = "test-session"
    context = SessionContext(
        session_id=session_id,
        messages=[],
        active_tasks=[],
        memory_context=ContextPackage(
            memories=[],
            total_found=0,
            token_estimate=0,
            formatted_context="",
            retrieval_query="",
            retrieval_duration_ms=0,
        ),
        working_summary="test",
        last_activity=datetime.now(UTC),
    )
    session_manager._startup_builder.build_context.return_value = context

    session = await session_manager.start_session()

    session_manager._redis.set.assert_called_once()
    args, kwargs = session_manager._redis.set.call_args
    assert args[0] == f"aether:session:{session.id}:context"
    # Ensure it's valid JSON
    assert json.loads(args[1])["session_id"] == session_id
    assert kwargs["ex"] == 86400


@pytest.mark.asyncio
async def test_start_session_emits_lifecycle_event(session_manager):
    session_manager._startup_builder.build_context.return_value = SessionContext(
        session_id="dummy",
        messages=[],
        active_tasks=[],
        memory_context=ContextPackage(
            memories=[],
            total_found=0,
            token_estimate=0,
            formatted_context="",
            retrieval_query="",
            retrieval_duration_ms=0,
        ),
        working_summary="",
        last_activity=datetime.now(UTC),
    )

    session = await session_manager.start_session(mode=SessionMode.TASK)

    session_manager._event_bus.emit.assert_called_once_with(
        event_type="session.lifecycle.started",
        payload={"mode": "task"},
        session_id=session.id,
        correlation_id=session.id,
        source="aether.session",
    )


@pytest.mark.asyncio
async def test_end_session_emits_lifecycle_event(session_manager):
    session_id = "test-session"

    await session_manager.end_session(session_id, trigger="timeout")

    session_manager._event_bus.emit.assert_called_once_with(
        event_type="session.lifecycle.ended",
        payload={"trigger": "timeout"},
        session_id=session_id,
        correlation_id=session_id,
        source="aether.session",
    )


@pytest.mark.asyncio
async def test_end_session_triggers_consolidation_as_background_task(session_manager):
    session_id = "test-session"

    # We want to ensure consolidation is scheduled as a task and end_session returns immediately
    await session_manager.end_session(session_id)

    # Wait a tiny bit to allow the background task to run
    await asyncio.sleep(0.01)

    # M2.1.5: consolidation now runs through MemoryAPI's public method, not a
    # directly injected pipeline.
    session_manager._memory_api.consolidate.assert_called_once_with(session_id)


@pytest.mark.asyncio
async def test_end_session_closes_conversation_via_memory_api(session_manager):
    session_id = "test-session"

    await session_manager.end_session(session_id)

    session_manager._memory_api.end_conversation.assert_called_once_with(session_id)


@pytest.mark.asyncio
async def test_update_context_persists_messages_via_memory_api(session_manager):
    from aether.llm import Message

    session_id = "test-session"
    context = SessionContext(
        session_id=session_id,
        messages=[],
        active_tasks=[],
        memory_context=ContextPackage(
            memories=[],
            total_found=0,
            token_estimate=0,
            formatted_context="",
            retrieval_query="",
            retrieval_duration_ms=0,
        ),
        working_summary="",
        last_activity=datetime.now(UTC),
    )
    session_manager._redis.get.return_value = context.model_dump_json()

    new_messages = [
        Message(role="user", content="hello"),
        Message(role="assistant", content="hi there"),
    ]
    await session_manager.update_context(session_id, new_messages)

    assert session_manager._memory_api.record_message.call_count == 2
    first_call = session_manager._memory_api.record_message.call_args_list[0]
    assert first_call.kwargs["conversation_id"] == session_id
    assert first_call.kwargs["role"] == "user"
    assert first_call.kwargs["content"] == "hello"


@pytest.mark.asyncio
async def test_get_context_loads_from_redis(session_manager):
    session_id = "test-session"
    context = SessionContext(
        session_id=session_id,
        messages=[],
        active_tasks=[],
        memory_context=ContextPackage(
            memories=[],
            total_found=0,
            token_estimate=0,
            formatted_context="",
            retrieval_query="",
            retrieval_duration_ms=0,
        ),
        working_summary="test",
        last_activity=datetime.now(UTC),
    )
    session_manager._redis.get.return_value = context.model_dump_json()

    result = await session_manager.get_context(session_id)

    assert result.session_id == session_id
    session_manager._startup_builder.build_context.assert_not_called()


@pytest.mark.asyncio
async def test_get_context_rebuilds_on_cache_miss(session_manager):
    session_id = "test-session"
    session_manager._redis.get.return_value = None

    context = SessionContext(
        session_id=session_id,
        messages=[],
        active_tasks=[],
        memory_context=ContextPackage(
            memories=[],
            total_found=0,
            token_estimate=0,
            formatted_context="",
            retrieval_query="",
            retrieval_duration_ms=0,
        ),
        working_summary="rebuilt",
        last_activity=datetime.now(UTC),
    )
    session_manager._startup_builder.build_context.return_value = context

    result = await session_manager.get_context(session_id)

    assert result.working_summary == "rebuilt"
    session_manager._startup_builder.build_context.assert_called_once_with(session_id)
    session_manager._redis.set.assert_called_once()


@pytest.mark.asyncio
async def test_morning_briefing_under_50_words():
    # Real builder without mocks
    builder = SessionStartupBuilder(memory_api=AsyncMock(), task_manager=AsyncMock())

    task = Task(
        id="t1",
        title="A very long task title that might cause briefing to exceed fifty words easily if we are not careful",
        description=None,
        category=None,
        due_at=None,
        completed_at=None,
        parent_task_id=None,
        agent_type=None,
        meta={},
        priority=TaskPriority.HIGH,
        status=TaskStatus.ACTIVE,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    context = SessionContext(
        session_id="dummy",
        messages=[],
        active_tasks=[task] * 10,  # Many tasks
        memory_context=ContextPackage(
            memories=[],
            total_found=1,
            token_estimate=10,
            formatted_context="mock",
            retrieval_query="mock",
            retrieval_duration_ms=10,
        ),
        working_summary="",
        last_activity=datetime.now(UTC),
    )

    briefing = await builder.build_morning_briefing(context)

    word_count = len(briefing.split())
    assert word_count <= 50


@pytest.mark.asyncio
async def test_morning_briefing_correct_greeting_by_time_of_day():
    from unittest.mock import patch

    builder = SessionStartupBuilder(memory_api=AsyncMock(), task_manager=AsyncMock())
    context = SessionContext(
        session_id="dummy",
        messages=[],
        active_tasks=[],
        memory_context=ContextPackage(
            memories=[],
            total_found=0,
            token_estimate=0,
            formatted_context="",
            retrieval_query="",
            retrieval_duration_ms=0,
        ),
        working_summary="",
        last_activity=datetime.now(UTC),
    )

    with patch("aether.session.startup.datetime") as mock_dt:
        # Mock 9 AM
        mock_dt.now.return_value = datetime(2026, 1, 1, 9, 0, 0)
        briefing = await builder.build_morning_briefing(context)
        assert "Good morning" in briefing

        # Mock 2 PM
        mock_dt.now.return_value = datetime(2026, 1, 1, 14, 0, 0)
        briefing = await builder.build_morning_briefing(context)
        assert "Good afternoon" in briefing

        # Mock 8 PM
        mock_dt.now.return_value = datetime(2026, 1, 1, 20, 0, 0)
        briefing = await builder.build_morning_briefing(context)
        assert "Good evening" in briefing
