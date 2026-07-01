import time

import structlog

from ...core.exceptions import MemoryRetrievalError
from .._stores.sqlite_store import SQLiteMemoryStore
from .._stores.vector_store import QdrantMemoryStore
from ..models import ContextPackage, MemoryFilter, MemoryRecord
from .reranker import MemoryReranker

logger = structlog.get_logger(__name__)


class HybridRetrieval:
    """Internal module for blending vector and keyword search."""

    def __init__(self, sqlite_store: SQLiteMemoryStore, vector_store: QdrantMemoryStore):
        self._sqlite_store = sqlite_store
        self._vector_store = vector_store
        self._reranker = MemoryReranker()

    async def search(
        self,
        query: str,
        query_embedding: list[float],
        k: int,
        filters: MemoryFilter,
        token_budget: int,
    ) -> ContextPackage:
        start_time = time.perf_counter()

        vector_failed = False
        vector_results: list[tuple[str, float]] = []
        try:
            vector_results = await self._vector_store.search(
                query_vector=query_embedding, limit=k * 2, score_threshold=0.0, filters=filters
            )
        except Exception as e:
            logger.warning("Qdrant unavailable for retrieval", error=str(e))
            vector_failed = True

        fts_failed = False
        fts_results: list[MemoryRecord] = []
        try:
            fts_results = await self._sqlite_store.search_fts(query=query, limit=k, filters=filters)
        except Exception as e:
            logger.warning("SQLite FTS unavailable for retrieval", error=str(e))
            fts_failed = True

        if vector_failed and fts_failed:
            raise MemoryRetrievalError("Both vector and FTS retrieval failed.")

        # Step 3: Merge and load full records for vector results
        combined_candidates: list[tuple[MemoryRecord, float]] = []

        for vid, score in vector_results:
            record = await self._sqlite_store.get_memory(vid)
            if record:
                combined_candidates.append((record, score))

        # Step 4: Deduplicate FTS results and assign default similarity for keyword matches
        seen_ids = {record.id for record, _ in combined_candidates}
        for record in fts_results:
            if record.id not in seen_ids:
                combined_candidates.append((record, 0.5))
                seen_ids.add(record.id)

        # Step 5: Rerank combined candidates
        ranked = self._reranker.rerank(combined_candidates, token_budget)

        duration_ms = int((time.perf_counter() - start_time) * 1000)

        # Step 6: Return ContextPackage
        return self._reranker.assemble_context_package(
            ranked=ranked, query=query, token_budget=token_budget, duration_ms=duration_ms
        )
