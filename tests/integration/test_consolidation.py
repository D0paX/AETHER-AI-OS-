import asyncio
from datetime import datetime, UTC
import uuid_utils

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from aether.llm.router import LLMRouter
from aether.memory.api import MemoryAPI
from aether.memory.models import Base, ConsolidationReport
from aether.memory._consolidation.pipeline import ConsolidationPipeline
from aether.core.events import EventBus

@pytest.fixture
async def sqlite_db():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    factory = async_sessionmaker(
        bind=engine, expire_on_commit=False, class_=AsyncSession
    )
    yield factory
    await engine.dispose()

@pytest.fixture
def consolidation_pipeline():
    return ConsolidationPipeline()

@pytest.mark.asyncio
async def test_consolidation_skips_with_insufficient_messages(sqlite_db, consolidation_pipeline):
    session_id = str(uuid_utils.uuid7())
    
    # Insert conversation
    async with sqlite_db() as db:
        await db.execute(text("INSERT INTO conversations (id, started_at, message_count) VALUES (:id, :ts, :mc)"),
                         {"id": session_id, "ts": datetime.now(UTC).isoformat(), "mc": 2})
        # Insert 2 messages
        for i in range(2):
            msg_id = str(uuid_utils.uuid7())
            await db.execute(
                text("INSERT INTO messages (id, conversation_id, role, content, created_at) VALUES (:id, :sid, :role, :content, :ts)"),
                {"id": msg_id, "sid": session_id, "role": "user", "content": "hello", "ts": datetime.now(UTC).isoformat()}
            )
        await db.commit()
    
    # Mock memory_api
    class MockSQLiteStore:
        async def get_messages(self, sid):
            return [{"role": "user", "content": "hello"}] * 2
            
    class MockMemoryAPI:
        def __init__(self):
            self._sqlite_store = MockSQLiteStore()
            
    memory_api = MockMemoryAPI()
    llm_router = LLMRouter() # won't be used since it returns early
    
    report = await consolidation_pipeline.run(session_id, llm_router, memory_api)
    
    assert isinstance(report, ConsolidationReport)
    assert report.skipped is True
    assert report.skip_reason == "insufficient_messages"
    assert report.memories_created == 0

@pytest.mark.asyncio
async def test_consolidation_creates_long_term_memories(sqlite_db, consolidation_pipeline):
    session_id = str(uuid_utils.uuid7())
    
    # Insert conversation
    async with sqlite_db() as db:
        await db.execute(text("INSERT INTO conversations (id, started_at, message_count) VALUES (:id, :ts, :mc)"),
                         {"id": session_id, "ts": datetime.now(UTC).isoformat(), "mc": 10})
        # Insert 10 messages
        for i in range(10):
            msg_id = str(uuid_utils.uuid7())
            await db.execute(
                text("INSERT INTO messages (id, conversation_id, role, content, created_at) VALUES (:id, :sid, :role, :content, :ts)"),
                {"id": msg_id, "sid": session_id, "role": "user" if i%2==0 else "assistant", "content": f"msg {i}", "ts": datetime.now(UTC).isoformat()}
            )
        await db.commit()
        
    class MockSQLiteStore:
        async def get_messages(self, sid):
            return [{"role": "user" if i%2==0 else "assistant", "content": f"msg {i}"} for i in range(10)]
            
    class MockMemoryAPI:
        def __init__(self):
            self._sqlite_store = MockSQLiteStore()
            
        async def remember(self, content, memory_type, importance, metadata={}, session_id=None, source="CONVERSATION"):
            return "mem_1"
            
    memory_api = MockMemoryAPI()
    
    # We need to mock LLMRouter to return a summary and facts
    from aether.llm._models import LLMResponse
    class MockLLMRouter:
        async def complete(self, messages, tier):
            import json
            if "Summarize" in messages[0].content:
                return LLMResponse(
                    content="Summary of session",
                    model_used="mock", tier_used=tier, prompt_tokens=5, completion_tokens=5, total_tokens=10, cost_usd=0.01, duration_ms=10
                )
            if "Extract atomic facts" in messages[0].content:
                # Mock JSON response of extracted facts
                return LLMResponse(
                    content=json.dumps([
                        {"fact": "User likes test", "tags": ["test"], "entities": ["User"]}
                    ]),
                    model_used="mock", tier_used=tier, prompt_tokens=5, completion_tokens=5, total_tokens=10, cost_usd=0.01, duration_ms=10
                )
    
    llm_router = MockLLMRouter()
    
    report = await consolidation_pipeline.run(session_id, llm_router, memory_api)
    
    assert report.skipped is False
    assert report.memories_created >= 1
    assert report.facts_extracted == 1
