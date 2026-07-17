import json
import re
from datetime import UTC, datetime

import structlog
import uuid_utils
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from ..models import MemoryFilter, MemoryRecord, MemorySource, MemoryType

logger = structlog.get_logger(__name__)


class SQLiteMemoryStore:
    """Internal relational storage for memory metadata and keyword search.

    Since M2.1 the backing database is PostgreSQL in production while SQLite
    remains the test-suite backend; keyword search dispatches per dialect
    (pg_trgm word similarity on PostgreSQL, FTS5 MATCH on SQLite). The class
    name is retained because V1_TECHNICAL_SPECIFICATION.md and the approved
    Phase 2 plan reference this module by its current path.
    """

    def __init__(self, db_url: str):
        self._engine = create_async_engine(db_url, echo=False)
        self._dialect_name: str = self._engine.dialect.name
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
            return result.rowcount > 0  # type: ignore

    async def delete_memory(self, memory_id: str) -> bool:
        query = text("DELETE FROM memories WHERE id = :id")
        async with self._session_factory() as session:
            result = await session.execute(query, {"id": memory_id})
            await session.commit()
            return result.rowcount > 0  # type: ignore

    async def search_fts(self, query: str, limit: int, filters: MemoryFilter) -> list[MemoryRecord]:
        """Keyword search, dispatching to the dialect-appropriate implementation.

        The public signature is locked (same inputs, same MemoryRecord list
        output). On PostgreSQL the implementation uses pg_trgm word similarity
        against the GIN indexes from migration 002_postgres_fts; on SQLite
        (the test-suite backend) it keeps the original Phase 1 FTS5 query.
        """
        if self._dialect_name == "postgresql":
            return await self._search_keyword_trigram(query, limit, filters)
        return await self._search_keyword_fts5(query, limit, filters)

    def _apply_shared_filters(
        self, conditions: list[str], params: dict[str, object], filters: MemoryFilter
    ) -> None:
        """Append the filter conditions shared by both keyword search dialects."""
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

    async def _search_keyword_fts5(
        self, query: str, limit: int, filters: MemoryFilter
    ) -> list[MemoryRecord]:
        """Original Phase 1 FTS5 keyword search (SQLite only)."""
        # Remove punctuation to avoid FTS5 syntax errors
        safe_query = re.sub(r"[^\w\s]", "", query).strip()
        if not safe_query:
            return []

        conditions = ["memories_fts MATCH :query"]
        params: dict[str, object] = {"query": safe_query, "limit": limit}
        self._apply_shared_filters(conditions, params, filters)

        # Join on the shared INTEGER rowid, not m.id. memories.id is a TEXT
        # UUIDv7, while memories_fts.rowid is FTS5's integer shadow-row alias;
        # comparing them can never match (DEBT-004). content_rowid='rowid'
        # (set in migration 001) means both sides refer to memories.rowid.
        sql = f"""
            SELECT m.*
            FROM memories_fts f
            JOIN memories m ON m.rowid = f.rowid
            WHERE {" AND ".join(conditions)}
            ORDER BY f.rank
            LIMIT :limit
        """

        return await self._execute_keyword_query(sql, params)

    async def _search_keyword_trigram(
        self, query: str, limit: int, filters: MemoryFilter
    ) -> list[MemoryRecord]:
        """PostgreSQL keyword search via pg_trgm word similarity.

        The <% operator (word_similarity) matches the query against the best
        matching word span of each column, mirroring FTS5's keyword semantics,
        and is served by the GIN gin_trgm_ops indexes from migration
        002_postgres_fts.
        """
        # Same query sanitisation as the FTS5 path, for behavioral parity.
        safe_query = re.sub(r"[^\w\s]", "", query).strip()
        if not safe_query:
            return []

        conditions = ["(:query <% m.content OR :query <% m.tags OR :query <% m.entities)"]
        params: dict[str, object] = {"query": safe_query, "limit": limit}
        self._apply_shared_filters(conditions, params, filters)

        sql = f"""
            SELECT m.*,
                   GREATEST(
                       word_similarity(:query, m.content),
                       word_similarity(:query, m.tags),
                       word_similarity(:query, m.entities)
                   ) AS keyword_rank
            FROM memories m
            WHERE {" AND ".join(conditions)}
            ORDER BY keyword_rank DESC
            LIMIT :limit
        """

        return await self._execute_keyword_query(sql, params)

    async def _execute_keyword_query(
        self, sql: str, params: dict[str, object]
    ) -> list[MemoryRecord]:
        """Run a keyword-search query, preserving the return-empty-on-failure contract.

        HybridRetrieval relies on keyword search degrading to an empty result
        (with a warning) rather than raising, so vector search can still serve
        the request when the relational backend is unavailable.
        """
        async with self._session_factory() as session:
            try:
                result = await session.execute(text(sql), params)
            except Exception as e:
                logger.warning("Keyword search failed", error=str(e))
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

    async def get_messages(self, conversation_id: str) -> list[dict[str, object]]:
        """Return all messages of a conversation, oldest first.

        Implements the accessor specified in V1_TECHNICAL_SPECIFICATION.md
        Section 3.2 (previously missing; added in M2.1.5). Each row carries
        role, content, token_count, and created_at. The id tiebreaker keeps
        ordering deterministic when created_at timestamps collide at
        millisecond precision (UUIDv7 ids are time-ordered).

        Args:
            conversation_id: The conversation whose messages to fetch.

        Returns:
            A list of raw row dicts ordered by created_at ascending.
        """
        query = text("""
            SELECT role, content, token_count, created_at
            FROM messages
            WHERE conversation_id = :conversation_id
            ORDER BY created_at ASC, id ASC
        """)
        async with self._session_factory() as session:
            result = await session.execute(query, {"conversation_id": conversation_id})
            return [dict(row) for row in result.mappings().all()]

    async def end_conversation(self, conversation_id: str) -> None:
        """Mark a conversation as ended and record its true message count.

        message_count is computed with a real COUNT(*) against the messages
        table — never accepted from a caller, so it cannot drift from the
        rows that actually exist.

        Args:
            conversation_id: The conversation to close.
        """
        query = text("""
            UPDATE conversations
            SET ended_at = :ended_at,
                message_count = (
                    SELECT COUNT(*) FROM messages
                    WHERE conversation_id = :conversation_id
                )
            WHERE id = :conversation_id
        """)
        async with self._session_factory() as session:
            await session.execute(
                query,
                {"ended_at": self._now_iso(), "conversation_id": conversation_id},
            )
            await session.commit()

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
