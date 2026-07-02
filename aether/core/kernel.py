"""Aether Kernel - The heart of the OS."""

import asyncio
from typing import Any

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import text

from aether.core.config import AetherConfig as Settings, get_config
from aether.core.logging import configure_logging, get_logger
from aether.core.events import EventBus
from aether.memory.models import Base
from aether.llm.router import LLMRouter
from aether.memory.api import MemoryAPI
from aether.tools.registry import ToolRegistry
from aether.tasks.manager import TaskManager
from aether.agents.runtime import AgentRuntime
from aether.agents._implementations.conversation import ConversationAgent
from aether.session.manager import SessionManager
from aether.session.startup import SessionStartupBuilder
import redis.asyncio as aioredis


class AetherKernel:
    """Bootstraps and orchestrates all Aether OS modules in a strict sequence."""
    
    def __init__(self, config: Settings | None = None) -> None:
        # Step 1: Config
        self.config = config or get_config()
        
        # Step 2: Logging
        configure_logging(self.config.logging)
        self.logger = get_logger("kernel")
        
        # Core components
        self.event_bus: EventBus | None = None
        self._engine: Any = None
        self.db_session_factory: Any = None
        self.llm_router: LLMRouter | None = None
        self.memory_api: MemoryAPI | None = None
        self.tool_registry: ToolRegistry | None = None
        self.task_manager: TaskManager | None = None
        self.agent_runtime: AgentRuntime | None = None
        self.session_manager: SessionManager | None = None

    async def boot(self) -> None:
        """Execute the 11-step bootstrap sequence."""
        self.logger.info("Starting Aether Kernel boot sequence...")
        
        # Step 3: EventBus
        self.event_bus = EventBus(self.config.redis)
        await self.event_bus.connect()
        
        # Setup DB engine for migrations and factories
        self._engine = create_async_engine(self.config.database.url, echo=False)
        self.db_session_factory = async_sessionmaker(
            bind=self._engine, expire_on_commit=False, class_=AsyncSession
        )
        
        # Step 4: Migrations
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            
        # Step 5: VectorStore
        # Prepared implicitly by MemoryAPI in Step 7, but we acknowledge the step 
        # in the sequence. MemoryAPI manages the Qdrant connection natively.
        
        # Step 6: LLMRouter
        self.llm_router = LLMRouter()
        await self.llm_router._connect_bus()
        
        # Step 7: MemoryAPI
        self.memory_api = MemoryAPI(self.llm_router)
        await self.memory_api.initialize()
        
        # Step 8: ToolRegistry
        self.tool_registry = ToolRegistry()
        
        # Step 9: TaskManager
        self.task_manager = TaskManager(self.db_session_factory, self.event_bus)
        
        # Step 10: AgentRuntime
        self.agent_runtime = AgentRuntime(
            memory_api=self.memory_api,
            llm_router=self.llm_router,
            tool_registry=self.tool_registry,
            event_bus=self.event_bus,
            db_session_factory=self.db_session_factory
        )
        self.agent_runtime.register_agent(ConversationAgent.name, ConversationAgent)
        
        # Step 12: SessionManager
        redis_client = aioredis.from_url(self.config.redis.url)
        startup_builder = SessionStartupBuilder(
            memory_api=self.memory_api,
            task_manager=self.task_manager
        )
        self.session_manager = SessionManager(
            startup_builder=startup_builder,
            memory_api=self.memory_api,
            event_bus=self.event_bus,
            redis_client=redis_client,
            db_session_factory=self.db_session_factory,
            consolidation_pipeline=self.memory_api._consolidation_pipeline
        )
        
        # Step 13: Log "Kernel booted"
        self.logger.info("Kernel booted")

    async def shutdown(self) -> None:
        """Gracefully shutdown all components."""
        self.logger.info("Shutting down Aether Kernel...")
        if self._engine:
            await self._engine.dispose()
        # EventBus doesn't have an explicit disconnect in its current implementation, 
        # but we would call it here if it did.
