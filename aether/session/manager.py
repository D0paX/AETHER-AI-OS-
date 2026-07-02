import asyncio
import json
from datetime import datetime, UTC
from typing import Any, Literal

import structlog
from redis.asyncio import Redis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
import uuid_utils

from aether.core.events import EventBus
from aether.llm._models import Message
from aether.memory.api import MemoryAPI
from aether.memory._consolidation.pipeline import ConsolidationPipeline

from .models import Session, SessionContext, SessionMode
from .startup import SessionStartupBuilder

logger = structlog.get_logger(__name__)


class SessionManager:
    """Manages the lifecycle of an interaction session."""

    SESSION_CONTEXT_TTL_SECONDS: int = 86400  # 24 hours

    def __init__(
        self,
        startup_builder: SessionStartupBuilder,
        memory_api: MemoryAPI,
        event_bus: EventBus,
        redis_client: Redis,
        db_session_factory: async_sessionmaker[AsyncSession],
        consolidation_pipeline: ConsolidationPipeline,
    ):
        self._startup_builder = startup_builder
        self._memory_api = memory_api
        self._event_bus = event_bus
        self._redis = redis_client
        self._db_session_factory = db_session_factory
        self._consolidation = consolidation_pipeline

    def _cache_key(self, session_id: str) -> str:
        return f"aether:session:{session_id}:context"

    async def start_session(self, mode: SessionMode = SessionMode.TEXT) -> Session:
        """Starts a new session, caches context, and emits event."""
        session_id = str(uuid_utils.uuid7())
        now = datetime.now(UTC)

        # 1. Create session record in SQLite (conversations table)
        # Using a raw SQL insert assuming the conversations table exists. 
        # (Alternatively could use SQLAlchemy ORM models if available)
        async with self._db_session_factory() as db:
            await db.execute(
                text("""
                    INSERT INTO conversations (id, started_at, mode)
                    VALUES (:id, :started_at, :mode)
                """),
                {"id": session_id, "started_at": now.isoformat(), "mode": mode.value},
            )
            await db.commit()

        # 2. Build context
        context = await self._startup_builder.build_context(session_id)

        # 3. Cache SessionContext in Redis
        # model_dump_json handles the serialization securely (no pickle)
        await self._redis.set(
            self._cache_key(session_id),
            context.model_dump_json(),
            ex=self.SESSION_CONTEXT_TTL_SECONDS,
        )

        # 4. Emit session.lifecycle.started
        await self._event_bus.emit(
            event_type="session.lifecycle.started",
            payload={"mode": mode.value},
            session_id=session_id,
            correlation_id=session_id,
            source="aether.session",
        )

        return Session(
            id=session_id,
            started_at=now,
            mode=mode,
            status="active",
            message_count=0,
        )

    async def end_session(
        self, session_id: str, trigger: Literal["user", "timeout", "system"] = "user"
    ) -> None:
        """Ends the session and triggers non-blocking consolidation."""
        now = datetime.now(UTC)

        # 1. Update conversations table
        async with self._db_session_factory() as db:
            await db.execute(
                text("""
                    UPDATE conversations
                    SET ended_at = :ended_at
                    WHERE id = :id
                """),
                {"ended_at": now.isoformat(), "id": session_id},
            )
            await db.commit()

        # 2. Emit session.lifecycle.ended
        await self._event_bus.emit(
            event_type="session.lifecycle.ended",
            payload={"trigger": trigger},
            session_id=session_id,
            correlation_id=session_id,
            source="aether.session",
        )

        # 3. Trigger consolidation (NON-BLOCKING)
        asyncio.create_task(self._run_consolidation(session_id))

        # 4. Delete Redis session cache key
        await self._redis.delete(self._cache_key(session_id))

    async def get_context(self, session_id: str) -> SessionContext:
        """Retrieves session context from Redis or rebuilds it if missing."""
        cached_data = await self._redis.get(self._cache_key(session_id))

        if cached_data:
            # 2. Deserialize and return
            return SessionContext.model_validate_json(cached_data)

        # 3. Cache miss: rebuild from SQLite + startup_builder
        logger.info("Session context cache miss, rebuilding", session_id=session_id)
        
        # Load from DB to check message_count (simplified rebuild logic here just calls build_context)
        # Realistically, you would also load past messages here, but we will just rely on startup_builder
        # to re-fetch the base context.
        rebuilt_context = await self._startup_builder.build_context(session_id)

        # 4. Re-cache the rebuilt context
        await self._redis.set(
            self._cache_key(session_id),
            rebuilt_context.model_dump_json(),
            ex=self.SESSION_CONTEXT_TTL_SECONDS,
        )

        return rebuilt_context

    async def update_context(self, session_id: str, new_messages: list[Message]) -> None:
        """Updates the session context with new messages."""
        context = await self.get_context(session_id)
        
        updated_messages = list(context.messages) + new_messages
        message_count_increment = len(new_messages)
        
        updated_context = SessionContext(
            session_id=context.session_id,
            messages=updated_messages,
            active_tasks=context.active_tasks,
            memory_context=context.memory_context,
            working_summary=context.working_summary,
            last_activity=datetime.now(UTC),
        )

        # Re-serialize and store back to Redis with same TTL
        await self._redis.set(
            self._cache_key(session_id),
            updated_context.model_dump_json(),
            ex=self.SESSION_CONTEXT_TTL_SECONDS,
        )
        
        # Update message_count in SQLite
        async with self._db_session_factory() as db:
            await db.execute(
                text("""
                    UPDATE conversations
                    SET message_count = message_count + :inc
                    WHERE id = :id
                """),
                {"inc": message_count_increment, "id": session_id},
            )
            await db.commit()

    async def get_morning_briefing(self, session_id: str) -> str:
        """Delegates to startup_builder.build_morning_briefing(context)."""
        context = await self.get_context(session_id)
        return await self._startup_builder.build_morning_briefing(context)

    async def _run_consolidation(self, session_id: str) -> None:
        """Background task — NEVER awaited from end_session()"""
        try:
            await self._consolidation.run(
                session_id=session_id,
                llm_router=self._memory_api._llm_router,
                memory_api=self._memory_api,
            )
        except Exception as e:
            logger.error("session.consolidation.failed", session_id=session_id, error=str(e))
            # Do NOT re-raise — consolidation failure must not propagate
