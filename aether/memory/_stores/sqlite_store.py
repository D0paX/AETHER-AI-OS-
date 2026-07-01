import json
from datetime import UTC, datetime

import structlog
import uuid_utils
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from ..models import MemoryFilter, MemoryRecord, MemorySource, MemoryType

logger = structlog.get_logger(__name__)


class SQLiteMemoryStore:
    """Internal SQLite storage for memory metadata and FTS search."""

    def __init__(self, db_url: str):
        self._engine = create_async_engine(db_url, echo=False)
        self._session_factory = async_sessionmaker(
            bind=self._engine, expire_on_commit=False, class_=AsyncSession
        )

    def _now_iso(self) -> str:
        return datetime.now(UTC).isoformat()

    def _generate_id(self) -> str:
        return str(uuid_utils.uuid7())

    async def create_memory(
        self,
        content: str,
        memory_type: MemoryType,
        importance: float,
        confidence: float,
        source: MemorySource,
        source_id: str | None,
        tags: list[str],
        entities: list[str],
    ) -> str:
        memory_id = self._generate_id()
        now = self._now_iso()

        query = text("""
            INSERT INTO memories (
                id, content, memory_type, importance, confidence, 
                source, source_id, tags, entities, created_at, 
                last_accessed_at, access_count, meta
            ) VALUES (
                :id, :content, :memory_type, :importance, :confidence,
                :source, :source_id, :tags, :entities, :created_at,
                :last_accessed_at, :access_count, :meta
            )
        """)

        async with self._session_factory() as session:
            await session.execute(
                query,
                {
                    "id": memory_id,
                    "content": content,
                    "memory_type": memory_type.value,
                    "importance": importance,
                    "confidence": confidence,
                    "source": source.value,
                    "source_id": source_id,
                    "tags": json.dumps(tags),
                    "entities": json.dumps(entities),
                    "created_at": now,
                    "last_accessed_at": now,
                    "access_count": 0,
                    "meta": "{}",
                },
            )
            await session.commit()

        return memory_id

    async def get_memory(self, memory_id: str) -> MemoryRecord | None:
        query = text("SELECT * FROM memories WHERE id = :id")
        async with self._session_factory() as session:
            result = await session.execute(query, {"id": memory_id})
            row = result.mappings().first()

        if not row:
            return None

        return MemoryRecord(
            id=row["id"],
            content=row["content"],
            memory_type=MemoryType(row["memory_type"]),
            importance=row["importance"],
            confidence=row["confidence"],
            source=MemorySource(row["source"]),
            tags=json.loads(row["tags"]),
            entities=json.loads(row["entities"]),
            created_at=datetime.fromisoformat(row["created_at"]),
            last_accessed_at=datetime.fromisoformat(row["last_accessed_at"]),
            access_count=row["access_count"],
        )

    async def update_access(self, memory_id: str) -> None:
        now = self._now_iso()
        query = text("""
            UPDATE memories 
            SET access_count = access_count + 1, last_accessed_at = :now
            WHERE id = :id
        """)
        async with self._session_factory() as session:
            await session.execute(query, {"id": memory_id, "now": now})
            await session.commit()

    async def update_memory_importance(self, memory_id: str, importance: float) -> bool:
        query = text("UPDATE memories SET importance = :importance WHERE id = :id")
        async with self._session_factory() as session:
            result = await session.execute(query, {"id": memory_id, "importance": importance})
            await session.commit()
            return result.rowcount > 0

    async def delete_memory(self, memory_id: str) -> bool:
        query = text("DELETE FROM memories WHERE id = :id")
        async with self._session_factory() as session:
            result = await session.execute(query, {"id": memory_id})
            await session.commit()
            return result.rowcount > 0

    async def search_fts(self, query: str, limit: int, filters: MemoryFilter) -> list[MemoryRecord]:
        conditions = ["memories_fts MATCH :query"]
        params = {"query": query, "limit": limit}

        if filters.memory_types:
            placeholders = []
            for i, mt in enumerate(filters.memory_types):
                params[f"mt_{i}"] = mt.value
                placeholders.append(f":mt_{i}")
            conditions.append(f"m.memory_type IN ({','.join(placeholders)})")

        if filters.source:
            conditions.append("m.source = :source")
            params["source"] = filters.source.value

        conditions.append("m.importance >= :min_imp")
        params["min_imp"] = filters.min_importance

        conditions.append("m.confidence >= :min_conf")
        params["min_conf"] = filters.min_confidence

        sql = f"""
            SELECT m.* 
            FROM memories_fts f
            JOIN memories m ON m.id = f.rowid
            WHERE {" AND ".join(conditions)}
            ORDER BY f.rank
            LIMIT :limit
        """

        async with self._session_factory() as session:
            try:
                result = await session.execute(text(sql), params)
            except Exception as e:
                logger.warning("FTS search failed", error=str(e))
                return []

            rows = result.mappings().all()

        records = []
        for row in rows:
            records.append(
                MemoryRecord(
                    id=row["id"],
                    content=row["content"],
                    memory_type=MemoryType(row["memory_type"]),
                    importance=row["importance"],
                    confidence=row["confidence"],
                    source=MemorySource(row["source"]),
                    tags=json.loads(row["tags"]),
                    entities=json.loads(row["entities"]),
                    created_at=datetime.fromisoformat(row["created_at"]),
                    last_accessed_at=datetime.fromisoformat(row["last_accessed_at"]),
                    access_count=row["access_count"],
                )
            )
        return records

    async def create_conversation(self, mode: str) -> str:
        conv_id = self._generate_id()
        now = self._now_iso()
        query = text("""
            INSERT INTO conversations (id, started_at, mode, message_count, meta)
            VALUES (:id, :started_at, :mode, 0, '{}')
        """)
        async with self._session_factory() as session:
            await session.execute(query, {"id": conv_id, "started_at": now, "mode": mode})
            await session.commit()
        return conv_id

    async def add_message(
        self, conversation_id: str, role: str, content: str, token_count: int | None = None
    ) -> str:
        msg_id = self._generate_id()
        now = self._now_iso()

        query_msg = text("""
            INSERT INTO messages (id, conversation_id, role, content, token_count, created_at, meta)
            VALUES (:id, :conv_id, :role, :content, :tokens, :created_at, '{}')
        """)

        query_upd = text("""
            UPDATE conversations SET message_count = message_count + 1 WHERE id = :conv_id
        """)

        async with self._session_factory() as session:
            await session.execute(
                query_msg,
                {
                    "id": msg_id,
                    "conv_id": conversation_id,
                    "role": role,
                    "content": content,
                    "tokens": token_count,
                    "created_at": now,
                },
            )
            await session.execute(query_upd, {"conv_id": conversation_id})
            await session.commit()

        return msg_id
