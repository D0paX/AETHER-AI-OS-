from typing import Any

import structlog

from aether.core.config import get_config
from aether.llm.router import LLMRouter

from ._consolidation.pipeline import ConsolidationPipeline
from ._retrieval.hybrid import HybridRetrieval
from ._stores.sqlite_store import SQLiteMemoryStore
from ._stores.vector_store import QdrantMemoryStore
from .models import (
    ConsolidationReport,
    ContextPackage,
    MemoryFilter,
    MemoryRecord,
    MemorySource,
    MemoryType,
)

logger = structlog.get_logger(__name__)


class MemoryAPI:
    """The sole public interface for all memory operations."""

    def __init__(self, llm_router: LLMRouter):
        config = get_config()
        self._llm_router = llm_router

        self._sqlite_store = SQLiteMemoryStore(db_url=config.database.url)
        self._vector_store = QdrantMemoryStore(
            host=config.qdrant.host,
            port=config.qdrant.port,
            grpc_port=config.qdrant.grpc_port,
            prefer_grpc=True,
        )

        self._hybrid = HybridRetrieval(self._sqlite_store, self._vector_store)
        self._consolidation_pipeline = ConsolidationPipeline()
        self._event_bus = llm_router._event_bus  # Use router's event bus

    async def initialize(self) -> None:
        """Initialize connections and create Qdrant collection if needed."""
        await self._vector_store.initialize_collection()
        logger.info("Memory API initialized.")

    async def remember(
        self,
        content: str,
        memory_type: MemoryType,
        importance: float,
        metadata: dict[str, Any] = {},
        session_id: str | None = None,
        source: MemorySource = MemorySource.CONVERSATION,
    ) -> str:
        # 1. Generate embedding
        embedding = await self._llm_router._embedding_service.embed(content)

        # 2. Create record in SQLite
        memory_id = await self._sqlite_store.create_memory(
            content=content,
            memory_type=memory_type,
            importance=importance,
            confidence=0.9,  # Default or parameter
            source=source,
            source_id=session_id,
            tags=metadata.get("tags", []),
            entities=metadata.get("entities", []),
        )

        # 3. Upsert to Qdrant
        payload = {
            "memory_type": memory_type.value,
            "source": source.value,
            "importance": importance,
            "confidence": 0.9,
            "session_id": session_id,
        }
        await self._vector_store.upsert(
            memory_id=memory_id, vector=embedding.vector, payload=payload
        )

        # 4. Emit event
        if self._event_bus:
            await self._event_bus.emit(
                "memory.store.created", {"memory_id": memory_id, "type": memory_type.value}
            )

        return memory_id

    async def recall(
        self,
        query: str,
        k: int = 10,
        filters: MemoryFilter = MemoryFilter(),  # noqa: B006
        token_budget: int = 4096,
    ) -> ContextPackage:
        # 1. Generate query embedding
        embedding = await self._llm_router._embedding_service.embed(query)

        # 2. Search
        context_package = await self._hybrid.search(
            query=query,
            query_embedding=embedding.vector,
            k=k,
            filters=filters,
            token_budget=token_budget,
        )

        # 3. Update access logic
        for record in context_package.memories:
            await self._sqlite_store.update_access(record.id)

        return context_package

    async def forget(self, memory_id: str, reason: str) -> bool:
        if not reason or not reason.strip():
            raise ValueError("A reason must be provided to forget a memory.")

        sqlite_deleted = await self._sqlite_store.delete_memory(memory_id)
        if not sqlite_deleted:
            return False

        await self._vector_store.delete(memory_id)

        if self._event_bus:
            await self._event_bus.emit(
                "memory.store.deleted", {"memory_id": memory_id, "reason": reason}
            )

        return True

    async def consolidate(self, session_id: str) -> ConsolidationReport:
        return await self._consolidation_pipeline.run(
            session_id=session_id, llm_router=self._llm_router, memory_api=self
        )

    async def search(
        self,
        query: str,
        memory_type: MemoryType | None = None,
        limit: int = 20,
        min_importance: float = 0.0,
    ) -> list[MemoryRecord]:
        """Direct search for UI/dashboard."""
        filters = MemoryFilter(
            memory_types=[memory_type] if memory_type else None, min_importance=min_importance
        )
        return await self._sqlite_store.search_fts(query=query, limit=limit, filters=filters)

    async def update_importance(self, memory_id: str, new_importance: float) -> bool:
        success = await self._sqlite_store.update_memory_importance(memory_id, new_importance)
        if success:
            # Also update Qdrant payload if needed.
            # In Qdrant, to update a payload we'd need to set the new payload field.
            # But the vector store interface only exposes upsert right now.
            # If we skip it, it means vector search might use old importance for filtering,
            # but the sqlite DB has the true value. Ideally we'd update Qdrant too.
            pass
        return success

    async def get_stats(self) -> dict[str, Any]:
        # Return basic stats. SQLite count etc.
        return {
            "status": "online",
            # Additional stats can be implemented by querying SQLite
        }
