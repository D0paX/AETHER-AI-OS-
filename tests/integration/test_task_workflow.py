"""Task workflow integration tests, driven through the real agent runtime.

Corrected in the DEBT-006 cleanup. Every construct here was written against an
architecture that no longer exists (and in places never did): `AgentTask(
instruction=...)`, `ContextPackage(active_tasks=, transcript=,
relevant_memories=)`, `AgentDecision(tool_calls=[...])`,
`task_manager.create_task()/list_tasks()`, `result.output`, and an LLM response
carrying `.usage`. All are now asserted against the locked contracts:

- AgentTask  -> description / goal / input_data  (agents/base.py)
- AgentContext -> session_id / conversation_history / memory_context / active_tasks
- AgentDecision -> thought / action / action_input / final_answer
- AgentResult -> .response (never .output)
- LLMResponse -> total_tokens at top level, no .usage (M2.1.6)
- TaskManager -> create() / list() / get() / update_status()

Assertions go through TaskManager's public API rather than raw SQL, so they
verify the locked `Task` model's shape (a real `TaskStatus` enum) instead of a
storage detail — the manager persists status lower-cased internally.
"""

import asyncio
from collections.abc import AsyncGenerator
from unittest.mock import AsyncMock, patch

import pytest
import pytest_asyncio
import redis.asyncio as aioredis

from aether.agents._implementations.conversation import AgentDecision
from aether.agents.base import AgentContext, AgentTask
from aether.core.config import EMBEDDING_DIMENSION, get_config
from aether.core.kernel import AetherKernel
from aether.memory.models import ContextPackage
from aether.tasks.models import Task, TaskPriority, TaskStatus

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


def _llm_response(content: str) -> AsyncMock:
    """A stand-in LLMResponse using the locked field shape.

    The agent reads `total_tokens` and `cost_usd` at the top level; LLMResponse
    has no `.usage` attribute (the old mock's shape crashed every real call,
    fixed in M2.1.6).
    """
    return AsyncMock(total_tokens=10, cost_usd=0.01, content=content)


def _agent_context(active_tasks: list[Task] | None = None) -> AgentContext:
    """A minimal, correctly-shaped AgentContext."""
    return AgentContext(
        session_id="task-workflow-session",
        conversation_history=[],
        memory_context=ContextPackage(
            memories=[],
            total_found=0,
            token_estimate=0,
            formatted_context="",
            retrieval_query="",
            retrieval_duration_ms=0,
        ),
        active_tasks=active_tasks or [],
    )


def _agent_task(text: str, goal: str) -> AgentTask:
    """AgentTask in its locked shape — description/goal/input_data."""
    return AgentTask(description=text, goal=goal, input_data={"text": text})


@pytest_asyncio.fixture(scope="module", loop_scope="module")
async def kernel() -> AsyncGenerator[AetherKernel, None]:
    """One booted kernel for the whole module.

    Deliberately module-scoped. Booting per test loads the sentence-transformers
    embedding model again in the same process, and the SECOND load reliably
    triggers `Windows fatal exception: access violation` — DEBT-011, which these
    tests now reach because the corrected versions actually execute the agent
    path (the old broken ones raised ValidationError long before it). Booting a
    full kernel per test was also simply wasteful. This does not fix DEBT-011;
    the underlying torch/Windows fault is reported there and remains open.
    """
    k = AetherKernel()
    with patch("aether.core.kernel.LLMRouter._connect_bus", new_callable=AsyncMock):
        await k.boot()
    yield k
    await k.shutdown()


def _stub_llm(kernel: AetherKernel, *decisions: AgentDecision) -> None:
    """Drive the agent's ReAct loop with a fixed sequence of decisions."""
    kernel.llm_router.complete = AsyncMock(
        side_effect=[_llm_response(d.model_dump_json()) for d in decisions]
    )
    kernel.llm_router._embedding_service.embed = AsyncMock(
        return_value=AsyncMock(vector=[0.0] * EMBEDDING_DIMENSION)
    )


@pytest.mark.asyncio(loop_scope="module")
async def test_create_task_via_agent(kernel: AetherKernel) -> None:
    """The agent calls the real create_task tool and the task is persisted."""
    title = "Fix memory module bug"
    _stub_llm(
        kernel,
        AgentDecision(
            thought="I should create a task.",
            action="create_task",
            action_input={
                "title": title,
                "description": "Fix the memory module bug",
                "priority": "medium",
            },
        ),
        AgentDecision(thought="Task created.", final_answer="I have created the task."),
    )

    result = await kernel.agent_runtime.execute(
        "conversation",
        _agent_task(f"Create a task called {title}", "Create the task"),
        _agent_context(),
    )

    assert result.success is True
    assert "create_task" in result.actions_taken

    # Persisted, and readable back through the locked public API.
    tasks = await kernel.task_manager.list()
    found = [t for t in tasks if t.title == title]
    assert found, f"no task titled {title!r} was persisted"
    assert found[0].status in (TaskStatus.PENDING, TaskStatus.ACTIVE)
    assert found[0].priority == TaskPriority.MEDIUM


@pytest.mark.asyncio(loop_scope="module")
async def test_list_tasks_via_agent(kernel: AetherKernel) -> None:
    """Active tasks supplied in AgentContext reach the agent's response."""
    created = [
        await kernel.task_manager.create(
            title="Task A", description="A", priority=TaskPriority.LOW
        ),
        await kernel.task_manager.create(
            title="Task B", description="B", priority=TaskPriority.HIGH
        ),
        await kernel.task_manager.create(
            title="Task C", description="C", priority=TaskPriority.CRITICAL
        ),
    ]
    assert all(isinstance(t, Task) for t in created), "create() returns the locked Task model"

    _stub_llm(
        kernel,
        AgentDecision(
            thought="I will list the tasks from context.",
            final_answer="You have Task A, Task B, and Task C.",
        ),
    )

    result = await kernel.agent_runtime.execute(
        "conversation",
        _agent_task("What tasks do I have?", "List the user's tasks"),
        _agent_context(active_tasks=created),
    )

    assert result.success is True
    # AgentResult exposes `response`, not `output`.
    assert "Task A" in result.response
    assert "Task B" in result.response
    assert "Task C" in result.response


@pytest.mark.asyncio(loop_scope="module")
async def test_complete_task_via_agent(kernel: AetherKernel) -> None:
    """The agent completes a task through the real update_task_status tool."""
    created = await kernel.task_manager.create(
        title="Write unit tests", description="Write them", priority=TaskPriority.HIGH
    )
    # The locked state machine allows PENDING -> ACTIVE -> COMPLETED, never
    # PENDING -> COMPLETED directly, so activate it first rather than weakening
    # the transition rules to suit the test.
    await kernel.task_manager.update_status(created.id, TaskStatus.ACTIVE)

    _stub_llm(
        kernel,
        AgentDecision(
            thought="I should mark this as completed.",
            action="update_task_status",
            action_input={"task_id": created.id, "status": "completed"},
        ),
        AgentDecision(
            thought="Task updated.",
            final_answer="The unit tests task has been marked as completed.",
        ),
    )

    result = await kernel.agent_runtime.execute(
        "conversation",
        _agent_task("Mark the unit tests task as completed", "Complete the task"),
        _agent_context(active_tasks=[created]),
    )

    assert result.success is True
    assert "update_task_status" in result.actions_taken

    updated = await kernel.task_manager.get(created.id)
    assert updated.status == TaskStatus.COMPLETED
