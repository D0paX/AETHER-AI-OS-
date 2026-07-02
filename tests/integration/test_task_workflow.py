import pytest
import pytest_asyncio
import asyncio
from unittest.mock import AsyncMock, patch
import redis.asyncio as aioredis
from sqlalchemy import select

from aether.core.kernel import AetherKernel
from aether.core.config import get_config
from aether.agents.base import AgentTask
from aether.agents.base import AgentContext
from aether.session.models import ContextPackage
from aether.agents._implementations.conversation import AgentDecision
from aether.tasks.models import Task as DBTask

pytestmark = pytest.mark.integration

async def is_redis_reachable() -> bool:
    try:
        config = get_config()
        client = aioredis.from_url(config.redis.url)
        await client.ping()
        await client.aclose()
        return True
    except Exception:
        return False

_redis_reachable = asyncio.run(is_redis_reachable())
if not _redis_reachable:
    pytest.skip("Redis is not reachable. Skipping task workflow tests.", allow_module_level=True)

@pytest_asyncio.fixture
async def kernel() -> AetherKernel:
    # Use standard kernel but mock Qdrant to avoid needing vector DB for these specific tests, 
    # though prompt says "real Redis + SQLite", so Qdrant might also be real if start.ps1 is running.
    # We will let Qdrant be real too, but we need to mock LLM calls.
    k = AetherKernel()
    
    with patch("aether.core.kernel.LLMRouter._connect_bus", new_callable=AsyncMock):
        await k.boot()
        
    yield k
    
    await k.shutdown()


@pytest.mark.asyncio
async def test_create_task_via_agent(kernel: AetherKernel):
    # Mock LLM to return a tool call to create a task
    mock_complete = AsyncMock()
    
    # First turn: call create_task tool
    decision1 = AgentDecision(
        thought="I should create a task.",
        tool_calls=[{"id": "call_1", "name": "create_task", "arguments": {"title": "Fix memory module bug", "description": "Fix memory module bug", "priority": "NORMAL"}}]
    )
    # Second turn: final answer
    decision2 = AgentDecision(
        thought="Task created.",
        final_answer="I have created the task."
    )
    
    mock_complete.side_effect = [
        AsyncMock(usage=AsyncMock(total_tokens=10), cost_usd=0.01, content=decision1.model_dump_json()),
        AsyncMock(usage=AsyncMock(total_tokens=10), cost_usd=0.01, content=decision2.model_dump_json()),
    ]
    kernel.llm_router.complete = mock_complete
    
    # Mock embeddings to prevent outbound calls
    kernel.llm_router._embedding_service.embed = AsyncMock(return_value=AsyncMock(vector=[0.0] * 1536))
    
    agent_task = AgentTask(instruction="Create a task called Fix memory module bug")
    context = ContextPackage(active_tasks=[], transcript=[], relevant_memories=[])
    
    await kernel.agent_runtime.execute("conversation", agent_task, context)
    
    # Verify task exists in SQLite
    async with kernel.db_session_factory() as session:
        result = await session.execute(select(DBTask))
        tasks = result.scalars().all()
        
    # Check if task with "Fix memory" exists
    found = [t for t in tasks if "Fix memory" in t.title]
    assert len(found) > 0
    assert found[0].status in ["PENDING", "ACTIVE"]


@pytest.mark.asyncio
async def test_list_tasks_via_agent(kernel: AetherKernel):
    # Pre-create 3 tasks
    await kernel.task_manager.create_task(title="Task A", description="A", priority="NORMAL")
    await kernel.task_manager.create_task(title="Task B", description="B", priority="HIGH")
    await kernel.task_manager.create_task(title="Task C", description="C", priority="CRITICAL")
    
    # Active tasks should be in the context package!
    tasks = await kernel.task_manager.list_tasks()
    context = ContextPackage(active_tasks=tasks, transcript=[], relevant_memories=[])
    
    agent_task = AgentTask(instruction="What tasks do I have?")
    
    # Mock LLM to just answer directly based on context
    decision = AgentDecision(
        thought="I will list the tasks from context.",
        final_answer="You have Task A, Task B, and Task C."
    )
    
    mock_complete = AsyncMock()
    mock_complete.return_value = AsyncMock(
        usage=AsyncMock(total_tokens=10), cost_usd=0.01, content=decision.model_dump_json()
    )
    kernel.llm_router.complete = mock_complete
    kernel.llm_router._embedding_service.embed = AsyncMock(return_value=AsyncMock(vector=[0.0] * 1536))
    
    result = await kernel.agent_runtime.execute("conversation", agent_task, context)
    
    # Verify response mentions tasks
    assert "Task A" in result.output
    assert "Task B" in result.output
    assert "Task C" in result.output


@pytest.mark.asyncio
async def test_complete_task_via_agent(kernel: AetherKernel):
    # Pre-create a task
    task_id = await kernel.task_manager.create_task(title="Write unit tests", description="Write them", priority="HIGH")
    
    # First turn: call update_task_status tool
    decision1 = AgentDecision(
        thought="I should mark this as completed.",
        tool_calls=[{"id": "call_2", "name": "update_task_status", "arguments": {"task_id": task_id, "status": "COMPLETED"}}]
    )
    # Second turn: final answer
    decision2 = AgentDecision(
        thought="Task updated.",
        final_answer="The unit tests task has been marked as completed."
    )
    
    mock_complete = AsyncMock()
    mock_complete.side_effect = [
        AsyncMock(usage=AsyncMock(total_tokens=10), cost_usd=0.01, content=decision1.model_dump_json()),
        AsyncMock(usage=AsyncMock(total_tokens=10), cost_usd=0.01, content=decision2.model_dump_json()),
    ]
    kernel.llm_router.complete = mock_complete
    kernel.llm_router._embedding_service.embed = AsyncMock(return_value=AsyncMock(vector=[0.0] * 1536))
    
    agent_task = AgentTask(instruction="Mark the unit tests task as completed")
    tasks = await kernel.task_manager.list_tasks()
    context = ContextPackage(active_tasks=tasks, transcript=[], relevant_memories=[])
    
    await kernel.agent_runtime.execute("conversation", agent_task, context)
    
    # Verify task status = COMPLETED in SQLite
    async with kernel.db_session_factory() as session:
        result = await session.execute(select(DBTask).where(DBTask.id == task_id))
        db_task = result.scalar_one_or_none()
        
    assert db_task is not None
    assert db_task.status == "COMPLETED"
