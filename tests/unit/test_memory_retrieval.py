from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock

import pytest

from aether.core.exceptions import InfrastructureError
from aether.memory._retrieval.hybrid import HybridRetrieval
from aether.memory._retrieval.reranker import MemoryReranker
from aether.memory.models import MemoryFilter, MemoryRecord, MemorySource, MemoryType


def create_mock_record(
    memory_id: str,
    content: str,
    created_at: datetime,
    importance: float = 0.5,
    memory_type: MemoryType = MemoryType.FACT,
):
    return MemoryRecord(
        id=memory_id,
        content=content,
        memory_type=memory_type,
        importance=importance,
        confidence=0.9,
        source=MemorySource.CONVERSATION,
        tags=[],
        entities=[],
        created_at=created_at,
        last_accessed_at=created_at,
        access_count=0,
    )


def test_reranker_applies_correct_weights():
    reranker = MemoryReranker()
    now = datetime.now(UTC)

    rec_old = create_mock_record("1", "old", now - timedelta(days=40), importance=0.5)
    rec_new = create_mock_record("2", "new", now, importance=0.5)

    candidates = [(rec_old, 1.0), (rec_new, 1.0)]
    ranked = reranker.rerank(candidates, token_budget=1000)

    # New should rank higher due to recency
    assert ranked[0].id == "2"
    assert ranked[1].id == "1"


def test_reranker_respects_token_budget():
    reranker = MemoryReranker()
    now = datetime.now(UTC)

    # 5 words ~ 6.5 tokens
    rec1 = create_mock_record("1", "word word word word word", now)
    rec2 = create_mock_record("2", "word word word word word", now)

    candidates = [(rec1, 1.0), (rec2, 0.9)]
    # Budget of 10 tokens allows only 1 record
    ranked = reranker.rerank(candidates, token_budget=10)

    assert len(ranked) == 1
    assert ranked[0].id == "1"


def test_reranker_sorts_by_composite_score_descending():
    reranker = MemoryReranker()
    now = datetime.now(UTC)

    rec1 = create_mock_record("1", "low importance", now, importance=0.1)
    rec2 = create_mock_record("2", "high importance", now, importance=1.0)

    # Same similarity, different importance
    candidates = [(rec1, 0.5), (rec2, 0.5)]
    ranked = reranker.rerank(candidates, token_budget=1000)

    assert ranked[0].id == "2"
    assert ranked[1].id == "1"


def test_high_importance_fact_outranks_more_similar_episode():
    """DEBT-012: a durable FACT must not be buried by a merely-similar episode.

    The episode here has a HIGHER raw similarity and identical recency; only the
    categorical FACT boost lets the high-importance fact win. Under the old
    0.6/0.3/0.1 formula the episode ranked first.
    """
    reranker = MemoryReranker()
    now = datetime.now(UTC)

    fact = create_mock_record(
        "fact", "The user's name is Jordan", now, importance=0.85, memory_type=MemoryType.FACT
    )
    episode = create_mock_record(
        "episode", "User Task: greeting", now, importance=0.7, memory_type=MemoryType.EPISODE
    )

    # Episode is MORE similar (0.80 > 0.70) yet the fact must still rank first.
    ranked = reranker.rerank([(fact, 0.70), (episode, 0.80)], token_budget=10000)
    assert ranked[0].id == "fact"
    assert ranked[1].id == "episode"


def test_fact_boost_does_not_bury_a_much_more_relevant_episode():
    """DEBT-012 precision guard: the boost is bounded, not absolute.

    An essentially-irrelevant FACT (very low similarity) must NOT displace a
    highly-relevant EPISODE — otherwise the boost would make facts dominate
    indiscriminately.
    """
    reranker = MemoryReranker()
    now = datetime.now(UTC)

    weak_fact = create_mock_record(
        "weak_fact", "unrelated fact", now, importance=0.85, memory_type=MemoryType.FACT
    )
    strong_episode = create_mock_record(
        "strong_episode", "highly relevant", now, importance=0.7, memory_type=MemoryType.EPISODE
    )

    # Fact barely matches (0.05); episode is a strong match (0.95).
    ranked = reranker.rerank([(weak_fact, 0.05), (strong_episode, 0.95)], token_budget=10000)
    assert ranked[0].id == "strong_episode"
    assert ranked[1].id == "weak_fact"


@pytest.mark.asyncio
async def test_hybrid_search_merges_vector_and_keyword_results():
    mock_sqlite = AsyncMock()
    mock_qdrant = AsyncMock()

    hybrid = HybridRetrieval(mock_sqlite, mock_qdrant)

    now = datetime.now(UTC)
    rec1 = create_mock_record("1", "vector match", now)
    rec2 = create_mock_record("2", "fts match", now)

    mock_qdrant.search.return_value = [("1", 0.9)]
    mock_sqlite.search_fts.return_value = [rec2]
    mock_sqlite.get_memory.return_value = rec1

    pkg = await hybrid.search("query", [0.1], 10, MemoryFilter(), 1000)

    assert len(pkg.memories) == 2
    ids = {m.id for m in pkg.memories}
    assert "1" in ids
    assert "2" in ids


@pytest.mark.asyncio
async def test_hybrid_search_deduplicates_by_memory_id():
    mock_sqlite = AsyncMock()
    mock_qdrant = AsyncMock()

    hybrid = HybridRetrieval(mock_sqlite, mock_qdrant)

    now = datetime.now(UTC)
    rec1 = create_mock_record("1", "match", now)

    mock_qdrant.search.return_value = [("1", 0.9)]
    mock_sqlite.search_fts.return_value = [rec1]
    mock_sqlite.get_memory.return_value = rec1

    pkg = await hybrid.search("query", [0.1], 10, MemoryFilter(), 1000)

    assert len(pkg.memories) == 1
    assert pkg.memories[0].id == "1"


@pytest.mark.asyncio
async def test_hybrid_partial_failure_qdrant_unavailable_uses_fts():
    mock_sqlite = AsyncMock()
    mock_qdrant = AsyncMock()

    hybrid = HybridRetrieval(mock_sqlite, mock_qdrant)

    now = datetime.now(UTC)
    rec1 = create_mock_record("1", "fts match", now)

    mock_qdrant.search.side_effect = InfrastructureError("Qdrant down")
    mock_sqlite.search_fts.return_value = [rec1]

    pkg = await hybrid.search("query", [0.1], 10, MemoryFilter(), 1000)

    assert len(pkg.memories) == 1
    assert pkg.memories[0].id == "1"


@pytest.mark.asyncio
async def test_hybrid_partial_failure_fts_unavailable_uses_vector():
    mock_sqlite = AsyncMock()
    mock_qdrant = AsyncMock()

    hybrid = HybridRetrieval(mock_sqlite, mock_qdrant)

    now = datetime.now(UTC)
    rec1 = create_mock_record("1", "vector match", now)

    mock_qdrant.search.return_value = [("1", 0.9)]
    mock_sqlite.search_fts.side_effect = Exception("SQLite locked")
    mock_sqlite.get_memory.return_value = rec1

    pkg = await hybrid.search("query", [0.1], 10, MemoryFilter(), 1000)

    assert len(pkg.memories) == 1
    assert pkg.memories[0].id == "1"
