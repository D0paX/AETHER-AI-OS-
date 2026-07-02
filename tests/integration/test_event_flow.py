import asyncio
from typing import AsyncGenerator
import json
import uuid_utils

import pytest
import pytest_asyncio
import redis.asyncio as aioredis
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from aether.core.config import get_config
from aether.core.events import EventBus
from aether.memory.api import MemoryAPI
from aether.memory.models import Base
from aether.memory._consolidation.pipeline import ConsolidationPipeline
from aether.session.manager import SessionManager
from aether.session.models import SessionMode
from aether.session.startup import SessionStartupBuilder

pytestmark = pytest.mark.integration

# Skip these tests if Redis is not running
async def is_redis_reachable() -> bool:
    try:
        config = get_config()
        client = aioredis.from_url(config.redis.url)
        await client.ping()
        await client.aclose()
        return True
    except Exception:
        return False

# Evaluate synchronously at import time by running a tiny event loop
_redis_reachable = asyncio.run(is_redis_reachable())
if not _redis_reachable:
    pytest.skip("Redis is not reachable. Skipping integration tests.", allow_module_level=True)

@pytest_asyncio.fixture
async def integration_setup() -> AsyncGenerator[tuple[SessionManager, EventBus, aioredis.Redis], None]:
    config = get_config()
    redis_client = aioredis.from_url(config.redis.url)
    
    # Clean stream for tests
    await redis_client.delete("aether:events")
    
    event_bus = EventBus(config.redis)
    await event_bus.connect()
    
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    db_factory = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)
    
    # Mock MemoryAPI & TaskManager to bypass LLM and Qdrant in this integration test
    class MockTaskManager:
        async def list(self, filter, limit):
            return []
            
    class MockMemoryAPI:
        def __init__(self):
            self._llm_router = None
        async def recall(self, query, k):
            from aether.memory.models import ContextPackage
            return ContextPackage(memories=[])
            
    memory_api = MockMemoryAPI()
    startup_builder = SessionStartupBuilder(memory_api=memory_api, task_manager=MockTaskManager())  # type: ignore
    
    # We mock consolidation run to just emit an event to the bus to test flow, or we can use the real one 
    # but that requires LLM calls. The test is about event sequence from manager.
    class MockConsolidationPipeline(ConsolidationPipeline):
        async def run(self, session_id, llm_router, memory_api):
            await event_bus.emit(
                event_type="memory.consolidation.completed",
                payload={"memories_created": 1, "facts_extracted": 1},
                session_id=session_id,
                correlation_id=session_id,
                source="aether.memory",
            )
            from aether.memory.models import ConsolidationReport
            return ConsolidationReport(
                session_id=session_id, memories_created=1, facts_extracted=1, 
                duration_ms=10, llm_cost_usd=0.01, skipped=False
            )
            
    manager = SessionManager(
        startup_builder=startup_builder,
        memory_api=memory_api, # type: ignore
        event_bus=event_bus,
        redis_client=redis_client,
        db_session_factory=db_factory,
        consolidation_pipeline=MockConsolidationPipeline()
    )
    
    yield manager, event_bus, redis_client
    
    await redis_client.delete("aether:events")
    await event_bus.disconnect()
    await redis_client.aclose()
    await engine.dispose()


@pytest.mark.asyncio
async def test_session_start_to_end_event_sequence(integration_setup):
    manager, event_bus, redis_client = integration_setup
    
    # Start
    session = await manager.start_session(mode=SessionMode.TEXT)
    
    # Update
    from aether.llm._models import Message
    msg = Message(role="user", content="hello")
    await manager.update_context(session.id, [msg])
    
    # End
    await manager.end_session(session.id, trigger="user")
    
    # Wait for background consolidation event to fire
    await asyncio.sleep(0.1)
    
    # Read from Redis stream
    events = await redis_client.xrange("aether:events")
    
    # We expect:
    # 1. session.lifecycle.started
    # 2. session.lifecycle.ended
    # 3. memory.consolidation.completed
    assert len(events) >= 3
    
    event_types = []
    for _stream_id, event_data in events:
        event_json = json.loads(event_data[b"event"])
        if event_json.get("session_id") == session.id:
            event_types.append(event_json["event_type"])
            
    assert "session.lifecycle.started" in event_types
    assert "session.lifecycle.ended" in event_types
    
    # Check ordering
    start_idx = event_types.index("session.lifecycle.started")
    end_idx = event_types.index("session.lifecycle.ended")
    assert start_idx < end_idx


@pytest.mark.asyncio
async def test_consolidation_emits_completed_event(integration_setup):
    manager, event_bus, redis_client = integration_setup
    
    session = await manager.start_session()
    await manager.end_session(session.id)
    
    # Wait for task
    await asyncio.sleep(0.1)
    
    events = await redis_client.xrange("aether:events")
    consolidation_events = []
    for _stream_id, event_data in events:
        event_json = json.loads(event_data[b"event"])
        if event_json["event_type"] == "memory.consolidation.completed":
            consolidation_events.append(event_json)
            
    assert len(consolidation_events) == 1
    assert consolidation_events[0]["session_id"] == session.id
    assert consolidation_events[0]["payload"]["memories_created"] == 1
