"""Agent base classes and frozen data models."""

import asyncio
from abc import ABC, abstractmethod
from typing import Any, ClassVar

import uuid_utils
from pydantic import BaseModel, ConfigDict, Field

from aether.core.events import EventBus
from aether.llm import Message, ModelTier
from aether.memory.api import MemoryAPI
from aether.memory.models import ContextPackage, MemoryFilter, MemoryType
from aether.tasks.models import Task
from aether.tools.base import ToolResult
from aether.tools.registry import ToolRegistry


class AgentTask(BaseModel):
    model_config = ConfigDict(frozen=True)
    task_id: str = Field(default_factory=lambda: str(uuid_utils.uuid7()))
    description: str
    goal: str
    input_data: dict[str, Any] = Field(default_factory=dict)
    max_iterations: int = 10
    timeout_seconds: float = 120.0


class AgentContext(BaseModel):
    model_config = ConfigDict(frozen=True)
    session_id: str
    conversation_history: list[Message]
    memory_context: ContextPackage
    active_tasks: list[Task]
    system_state: dict[str, Any] = Field(default_factory=dict)


class AgentResult(BaseModel):
    model_config = ConfigDict(frozen=True)
    run_id: str
    success: bool
    response: str
    actions_taken: list[str]
    memories_created: list[str]
    tasks_modified: list[str]
    llm_tokens_used: int
    llm_cost_usd: float
    duration_ms: int
    error: str | None = None


class BaseAgent(ABC):
    name: ClassVar[str]
    role: ClassVar[str]
    llm_tier: ClassVar[ModelTier]
    allowed_tools: ClassVar[list[str]]
    max_iterations: ClassVar[int] = 10

    def __init__(
        self,
        memory_api: MemoryAPI,
        llm_router: Any,  # LLMRouter
        tool_registry: ToolRegistry,
        event_bus: EventBus,
    ) -> None:
        self._memory_api = memory_api
        self._llm_router = llm_router
        self._tool_registry = tool_registry
        self._event_bus = event_bus
        self._memory_reads_count = 0
        self._session_id: str | None = None

    @abstractmethod
    async def execute(self, task: AgentTask, context: AgentContext) -> AgentResult: ...

    async def _recall(
        self, query: str, k: int = 10, filters: MemoryFilter | None = None
    ) -> ContextPackage:
        if filters is None:
            filters = MemoryFilter()
        self._memory_reads_count += 1
        return await self._memory_api.recall(query=query, k=k, filters=filters)

    async def _remember(
        self, content: str, memory_type: MemoryType, importance: float = 0.5
    ) -> str:
        return await self._memory_api.remember(
            content=content,
            memory_type=memory_type,
            importance=importance,
            session_id=self._session_id,
        )

    async def _invoke_tool(self, tool_name: str, input_data: dict[str, Any]) -> ToolResult:
        # Step 1: Verify tool_name in self.allowed_tools
        if tool_name not in self.allowed_tools:
            return ToolResult(success=False, error=f"Tool {tool_name!r} not in allowed_tools")

        # Step 2: registry.get(tool_name)
        try:
            tool = self._tool_registry.get(tool_name)
        except Exception as e:
            return ToolResult(success=False, error=str(e))

        try:
            # Step 3: Validate permissions
            await tool.check_permissions()

            # Step 4: Validate input
            validated_input = tool.input_schema(**input_data)

            # Step 5: Execute
            result = await asyncio.wait_for(tool.execute(validated_input), timeout=30.0)

            # Step 6: Log to tool_executions table
            # Handled in AgentRuntime via EventBus or here?
            # Emitting an event is the architectural way to prevent direct DB access.

            # Step 7: Emit tool.execution.completed event
            if self._event_bus:
                await self._event_bus.emit(
                    "tool.execution.completed",
                    {
                        "tool_name": tool_name,
                        "success": result.success,
                        "agent_name": self.name,
                        "session_id": self._session_id,
                    },
                )
            return result
        except TimeoutError:
            result = ToolResult(success=False, error="Timeout")
            if self._event_bus:
                await self._event_bus.emit(
                    "tool.execution.completed",
                    {
                        "tool_name": tool_name,
                        "success": False,
                        "agent_name": self.name,
                        "session_id": self._session_id,
                    },
                )
            return result
        except Exception as e:
            result = ToolResult(success=False, error=str(e))
            if self._event_bus:
                await self._event_bus.emit(
                    "tool.execution.completed",
                    {
                        "tool_name": tool_name,
                        "success": False,
                        "agent_name": self.name,
                        "session_id": self._session_id,
                    },
                )
            return result
