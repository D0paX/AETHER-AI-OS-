"""Agent runtime orchestrator."""

import asyncio
from datetime import UTC, datetime
from typing import Any

import uuid_utils

from aether.agents.base import AgentContext, AgentResult, AgentTask, BaseAgent
from aether.core.events import EventBus
from aether.memory.api import MemoryAPI
from aether.memory.models import AgentRunModel
from aether.tools.registry import ToolRegistry


class AgentError(Exception):
    """Exception raised for agent execution errors."""

    pass


class AgentRuntime:
    def __init__(
        self,
        memory_api: MemoryAPI,
        llm_router: Any,
        tool_registry: ToolRegistry,
        event_bus: EventBus,
        db_session_factory: Any,
    ) -> None:
        self._memory_api = memory_api
        self._llm_router = llm_router
        self._tool_registry = tool_registry
        self._event_bus = event_bus
        self._db_session_factory = db_session_factory
        self._registry: dict[str, type[BaseAgent]] = {}

    def register_agent(self, agent_type: str, agent_class: type[BaseAgent]) -> None:
        self._registry[agent_type] = agent_class

    def list_agents(self) -> list[str]:
        return list(self._registry.keys())

    async def execute(self, agent_type: str, task: AgentTask, context: AgentContext) -> AgentResult:
        run_id = str(uuid_utils.uuid7())
        started_at = datetime.now(UTC).isoformat()

        # Step 1: Resolve agent class from _registry dict
        agent_class = self._registry.get(agent_type)
        if not agent_class:
            raise AgentError(f"Unknown agent type: {agent_type!r}")

        # Step 2: Instantiate agent with injected dependencies
        agent = agent_class(
            memory_api=self._memory_api,
            llm_router=self._llm_router,
            tool_registry=self._tool_registry,
            event_bus=self._event_bus,
        )
        # Inject session_id if supported (as per base agent implementation)
        agent._session_id = context.session_id

        # Step 3: INSERT into agent_runs table
        async with self._db_session_factory() as session:
            run_model = AgentRunModel(
                id=run_id,
                agent_name=agent_type,
                task_description=task.description,
                session_id=context.session_id,
                status="running",
                started_at=started_at,
            )
            session.add(run_model)
            await session.commit()

        # Step 4: Emit agent.run.started event
        if self._event_bus:
            await self._event_bus.emit(
                "agent.run.started",
                {
                    "run_id": run_id,
                    "agent_name": agent_type,
                    "session_id": context.session_id,
                },
            )

        start_time = asyncio.get_running_loop().time()
        success = False
        error_msg = None
        result = None

        try:
            # Step 5: Execute with timeout
            # We enforce timeout here for the agent execution
            result = await asyncio.wait_for(
                agent.execute(task, context), timeout=task.timeout_seconds
            )

            # Since AgentResult run_id must match, but the agent creates it without knowing run_id?
            # Wait, AgentResult has run_id field. But the agent execution returns AgentResult.
            # The agent doesn't know the run_id unless we pass it to the agent, or we override it here.
            # Or the agent creates AgentResult and sets run_id to something, then we replace it?
            # Wait, `AgentResult` is frozen. So we create a new one using model_copy.
            result = result.model_copy(update={"run_id": run_id})

            success = result.success
            error_msg = result.error
        except TimeoutError:
            # Step 6: On timeout
            error_msg = "Timeout"
            result = AgentResult(
                run_id=run_id,
                success=False,
                response="",
                actions_taken=[],
                memories_created=[],
                tasks_modified=[],
                llm_tokens_used=0,
                llm_cost_usd=0.0,
                duration_ms=int((asyncio.get_running_loop().time() - start_time) * 1000),
                error=error_msg,
            )
        except Exception as e:
            # Step 7: On exception
            error_msg = str(e)
            result = AgentResult(
                run_id=run_id,
                success=False,
                response="",
                actions_taken=[],
                memories_created=[],
                tasks_modified=[],
                llm_tokens_used=0,
                llm_cost_usd=0.0,
                duration_ms=int((asyncio.get_running_loop().time() - start_time) * 1000),
                error=error_msg,
            )

        completed_at = datetime.now(UTC).isoformat()
        status_str = "completed" if success else "failed"

        # Safe attribute access on result
        tokens = getattr(result, "llm_tokens_used", 0)
        cost = getattr(result, "llm_cost_usd", 0.0)
        response_text = getattr(result, "response", "")
        result_preview = response_text[:200] if response_text else ""
        if error_msg:
            result_preview = f"ERROR: {error_msg}"[:200]

        # Step 8: UPDATE agent_runs
        async with self._db_session_factory() as session:
            run_record = await session.get(AgentRunModel, run_id)
            if run_record:
                run_record.status = status_str
                run_record.completed_at = completed_at
                run_record.llm_tokens_used = tokens
                run_record.llm_cost_usd = cost
                run_record.result_preview = result_preview
                run_record.error_message = error_msg
                await session.commit()

        # Step 9: Emit event
        if self._event_bus:
            event_name = "agent.run.completed" if success else "agent.run.failed"
            await self._event_bus.emit(
                event_name,
                {
                    "run_id": run_id,
                    "agent_name": agent_type,
                    "session_id": context.session_id,
                    "success": success,
                    "error": error_msg,
                },
            )

        # Step 10: Return AgentResult
        return result
