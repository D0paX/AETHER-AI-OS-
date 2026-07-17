from typing import Any, Literal

import structlog

from aether.core.config import get_config
from aether.llm import Message
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
            collection_name=config.qdrant.collection,
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
        metadata: dict[str, Any] = {},  # noqa: B006
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
        filters: MemoryFilter = MemoryFilter(),  # noqa: B008
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

    # ------------------------------------------------------------------
    # Conversation accessors (added in M2.1.5 — purely additive; the seven
    # original locked methods above are unchanged). These are the single
    # public path to conversation records for every caller outside the
    # memory module, including SessionManager and the consolidation
    # pipeline.
    # ------------------------------------------------------------------

    async def start_conversation(self, mode: str = "voice") -> str:
        """Create a new conversation record.

        Args:
            mode: Interaction mode ("voice", "text", or "task").

        Returns:
            The new conversation's id (UUIDv7 string).
        """
        return await self._sqlite_store.create_conversation(mode)

    async def record_message(
        self,
        conversation_id: str,
        role: Literal["user", "assistant", "system", "tool"],
        content: str,
        token_count: int | None = None,
    ) -> str:
        """Persist one message turn of a conversation.

        Args:
            conversation_id: The conversation the message belongs to.
            role: The speaker role for the turn.
            content: The message text.
            token_count: Optional estimated token count for the turn.

        Returns:
            The new message's id (UUIDv7 string).
        """
        return await self._sqlite_store.add_message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            token_count=token_count,
        )

    async def end_conversation(self, conversation_id: str) -> None:
        """Close a conversation, setting ended_at and its true message count.

        The message count is computed inside the store from the persisted
        message rows, never supplied by the caller.

        Args:
            conversation_id: The conversation to close.
        """
        await self._sqlite_store.end_conversation(conversation_id)

    async def get_conversation_messages(self, conversation_id: str) -> list[Message]:
        """Return a conversation's messages as typed Message objects, oldest first.

        The internal store returns raw row dicts; this public method
        transforms them into the locked aether.llm Message model, keeping
        typed domain objects at the module boundary.

        Args:
            conversation_id: The conversation whose transcript to fetch.

        Returns:
            The conversation's messages ordered by created_at ascending.
        """
        rows = await self._sqlite_store.get_messages(conversation_id)
        return [
            Message.model_validate({"role": row["role"], "content": row["content"]}) for row in rows
        ]
