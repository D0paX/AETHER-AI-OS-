import asyncio
from datetime import datetime
from unittest.mock import AsyncMock

import pytest

from aether.tasks.models import Task, TaskPriority, TaskStatus
from aether.tools._implementations.datetime_tools import GetCurrentDatetimeTool
from aether.tools._implementations.search_tools import WebSearchTool
from aether.tools._implementations.task_tools import (
    CreateTaskTool,
    ListTasksTool,
    UpdateTaskStatusTool,
)


@pytest.mark.asyncio
async def test_datetime_tool_returns_current_time():
    tool = GetCurrentDatetimeTool()
    result = await tool.execute(GetCurrentDatetimeTool.Input())
    assert result.success
    assert "date" in result.data
    assert "time" in result.data
    assert "timezone" in result.data


def test_datetime_tool_output_schema_valid():
    tool = GetCurrentDatetimeTool()
    schema = tool.output_schema.model_json_schema()
    assert schema["type"] == "object"
    assert "datetime_iso" in schema["properties"]


@pytest.mark.asyncio
async def test_web_search_returns_results(monkeypatch):
    tool = WebSearchTool()

    async def mock_search(query: str, max_results: int):
        return [{"title": "Title", "url": "http://test", "snippet": "Body"}]

    monkeypatch.setattr(tool, "_perform_search", mock_search)

    result = await tool.execute(WebSearchTool.Input(query="Python asyncio", num_results=2))
    assert result.success
    assert result.data["results_count"] > 0
    assert len(result.data["results"]) <= 2


@pytest.mark.asyncio
async def test_web_search_timeout_returns_error_result(monkeypatch):
    tool = WebSearchTool()

    async def slow_search(*args, **kwargs):
        await asyncio.sleep(0.1)
        raise TimeoutError()

    monkeypatch.setattr(tool, "_perform_search", slow_search)

    result = await tool.execute(WebSearchTool.Input(query="timeout test"))
    assert not result.success
    assert result.error == "Search timed out"
    assert result.error_code == "SEARCH_TIMEOUT"


@pytest.mark.asyncio
async def test_create_task_tool_creates_task():
    mock_manager = AsyncMock()
    mock_manager.create.return_value = Task(
        id="task-123",
        title="Test Task",
        description="Desc",
        status=TaskStatus.PENDING,
        priority=TaskPriority.MEDIUM,
        category=None,
        due_at=None,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        completed_at=None,
        parent_task_id=None,
        agent_type=None,
        meta={},
    )

    tool = CreateTaskTool(task_manager=mock_manager)
    result = await tool.execute(CreateTaskTool.Input(title="Test Task", priority="medium"))

    assert result.success
    assert result.data["task_id"] == "task-123"
    assert result.data["status"] == "PENDING"


@pytest.mark.asyncio
async def test_list_tasks_tool_returns_list():
    mock_manager = AsyncMock()
    mock_manager.list.return_value = [
        Task(
            id="task-123",
            title="Test Task",
            description=None,
            status=TaskStatus.PENDING,
            priority=TaskPriority.MEDIUM,
            category=None,
            due_at=None,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            completed_at=None,
            parent_task_id=None,
            agent_type=None,
            meta={},
        )
    ]

    tool = ListTasksTool(task_manager=mock_manager)
    result = await tool.execute(ListTasksTool.Input(status="pending"))

    assert result.success
    assert len(result.data["tasks"]) == 1
    assert result.data["tasks"][0]["id"] == "task-123"


@pytest.mark.asyncio
async def test_update_status_tool_changes_status():
    mock_manager = AsyncMock()
    mock_manager.update_status.return_value = Task(
        id="task-123",
        title="Test Task",
        description=None,
        status=TaskStatus.ACTIVE,
        priority=TaskPriority.MEDIUM,
        category=None,
        due_at=None,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        completed_at=None,
        parent_task_id=None,
        agent_type=None,
        meta={},
    )

    tool = UpdateTaskStatusTool(task_manager=mock_manager)
    result = await tool.execute(UpdateTaskStatusTool.Input(task_id="task-123", status="active"))

    assert result.success
    assert result.data["status"] == "ACTIVE"
