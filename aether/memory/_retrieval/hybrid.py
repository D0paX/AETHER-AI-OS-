import re
import time

import structlog

from ...core.exceptions import MemoryRetrievalError
from .._stores.sqlite_store import SQLiteMemoryStore
from .._stores.vector_store import QdrantMemoryStore
from ..models import ContextPackage, MemoryFilter, MemoryRecord
from .reranker import MemoryReranker

logger = structlog.get_logger(__name__)

# Function/question words dropped from the keyword query in the FTS-only
# fallback (DEBT-012). Vector search bridges a question to its declarative
# answer semantically ("what is my name?" -> "the user's name is Jordan"), but
# keyword search cannot: FTS5's implicit AND requires every query term present,
# so "what/is/my/name" fails to match a fact that contains only "name". When
# Qdrant is momentarily unavailable and we fall back to keyword-only, dropping
# these stop-words leaves just the content words ("name"), which the fact does
# contain. This is deliberately dialect-agnostic — a plain content-word string,
# no FTS5 OR-syntax — so it behaves correctly on both the SQLite FTS5 path
# (implicit AND over fewer, meaningful terms) and the production pg_trgm path
# (word_similarity over the same terms). Kept intentionally small: it targets
# question/function words, not domain vocabulary.
_FALLBACK_STOPWORDS = frozenset(
    {
        "a",
        "an",
        "the",
        "is",
        "are",
        "was",
        "were",
        "be",
        "been",
        "being",
        "am",
        "what",
        "whats",
        "which",
        "who",
        "whom",
        "whose",
        "when",
        "where",
        "why",
        "how",
        "do",
        "does",
        "did",
        "doing",
        "done",
        "i",
        "me",
        "my",
        "mine",
        "myself",
        "you",
        "your",
        "yours",
        "we",
        "our",
        "us",
        "it",
        "its",
        "this",
        "that",
        "these",
        "those",
        "there",
        "here",
        "of",
        "to",
        "in",
        "on",
        "at",
        "for",
        "with",
        "about",
        "from",
        "by",
        "as",
        "into",
        "and",
        "or",
        "but",
        "not",
        "no",
        "so",
        "if",
        "then",
        "s",
        "t",
        "m",
        "re",
        "ve",
        "ll",
        "d",
        "can",
        "could",
        "would",
        "should",
        "will",
        "shall",
        "may",
        "might",
        "must",
        "have",
        "has",
        "had",
        "tell",
        "say",
        "said",
        "know",
        "get",
        "give",
        "please",
        "just",
        "any",
        "some",
    }
)


class HybridRetrieval:
    """Internal module for blending vector and keyword search."""

    def __init__(self, sqlite_store: SQLiteMemoryStore, vector_store: QdrantMemoryStore):
        self._sqlite_store = sqlite_store
        self._vector_store = vector_store
        self._reranker = MemoryReranker()

    @staticmethod
    def _loosen_fallback_query(query: str) -> str:
        """Strip question/function words, leaving the content words (DEBT-012).

        Returns a plain space-joined content-word string. Returns "" when the
        query is nothing but stop-words, so the caller can keep the original
        query rather than search for nothing.
        """
        tokens = re.findall(r"\w+", query.lower())
        content = [t for t in tokens if t not in _FALLBACK_STOPWORDS]
        return " ".join(content)

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

        # In the FTS-only fallback (vector search failed), loosen the keyword
        # query so a question can still match its declarative answer (DEBT-012).
        # The normal path — where vector search works — is left exactly as it
        # was: the strict query preserves keyword precision when it is only a
        # secondary signal alongside vector results.
        fts_query = query
        if vector_failed:
            loosened = self._loosen_fallback_query(query)
            if loosened:
                fts_query = loosened

        fts_failed = False
        fts_results: list[MemoryRecord] = []
        try:
            fts_results = await self._sqlite_store.search_fts(
                query=fts_query, limit=k, filters=filters
            )
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
