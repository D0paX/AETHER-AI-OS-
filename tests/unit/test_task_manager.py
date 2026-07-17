from unittest.mock import AsyncMock

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from aether.core.exceptions import AgentError
from aether.memory.models import Base
from aether.tasks.manager import TaskManager
from aether.tasks.models import TaskFilter, TaskPriority, TaskStatus


@pytest.fixture
async def sqlite_session_factory():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    yield session_factory

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture
def mock_event_bus():
    bus = AsyncMock()
    return bus


@pytest.fixture
def task_manager(sqlite_session_factory, mock_event_bus):
    return TaskManager(session_factory=sqlite_session_factory, event_bus=mock_event_bus)


@pytest.mark.asyncio
async def test_create_task_stores_in_sqlite(task_manager, mock_event_bus):
    task = await task_manager.create(title="Test DB Task")

    assert task.title == "Test DB Task"
    assert task.status == TaskStatus.PENDING

    # Event should be emitted
    mock_event_bus.emit.assert_called_once()
    args, kwargs = mock_event_bus.emit.call_args
    assert args[0] == "task.lifecycle.created"
    assert args[1]["task_id"] == task.id


@pytest.mark.asyncio
async def test_pending_to_active_transition_valid(task_manager):
    task = await task_manager.create(title="Task to Active")
    updated = await task_manager.update_status(task.id, TaskStatus.ACTIVE)
    assert updated.status == TaskStatus.ACTIVE


@pytest.mark.asyncio
async def test_completed_to_active_transition_invalid_raises(task_manager):
    task = await task_manager.create(title="Task to Complete")
    await task_manager.update_status(task.id, TaskStatus.ACTIVE)
    await task_manager.update_status(task.id, TaskStatus.COMPLETED)

    with pytest.raises(AgentError) as exc:
        await task_manager.update_status(task.id, TaskStatus.ACTIVE)
    assert "Invalid transition" in str(exc.value)


@pytest.mark.asyncio
async def test_list_filters_by_status(task_manager):
    await task_manager.create(title="Task 1")
    t2 = await task_manager.create(title="Task 2")
    await task_manager.update_status(t2.id, TaskStatus.ACTIVE)

    pending_tasks = await task_manager.list(task_filter=TaskFilter(status=TaskStatus.PENDING))
    assert len(pending_tasks) == 1
    assert pending_tasks[0].title == "Task 1"

    active_tasks = await task_manager.list(task_filter=TaskFilter(status=TaskStatus.ACTIVE))
    assert len(active_tasks) == 1
    assert active_tasks[0].title == "Task 2"


@pytest.mark.asyncio
async def test_active_summary_includes_task_titles(task_manager):
    await task_manager.create(title="Critical Fix", priority=TaskPriority.CRITICAL)
    t2 = await task_manager.create(title="Medium Feature", priority=TaskPriority.MEDIUM)
    await task_manager.update_status(t2.id, TaskStatus.ACTIVE)

    summary = await task_manager.get_active_summary()
    assert "2 active tasks" in summary
    assert "[CRITICAL] Critical Fix" in summary
    assert "[MEDIUM] Medium Feature" in summary


@pytest.mark.asyncio
async def test_status_change_emits_event(task_manager, mock_event_bus):
    task = await task_manager.create(title="Event Task")
    mock_event_bus.reset_mock()

    await task_manager.update_status(task.id, TaskStatus.ACTIVE)
    mock_event_bus.emit.assert_called_once()
    args, kwargs = mock_event_bus.emit.call_args
    assert args[0] == "task.lifecycle.status_changed"
    assert args[1]["task_id"] == task.id
    assert args[1]["new_status"] == "ACTIVE"
