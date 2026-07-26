"""FTS-only fallback retrieval tests (DEBT-012).

When Qdrant is momentarily unavailable, HybridRetrieval falls back to keyword
search. Before this fix, keyword search could not bridge a question to its
declarative answer — FTS5's implicit AND required every query term present, so
"What is my name?" failed to match "The user's name is Jordan." These tests
exercise the real SQLite FTS5 path (full alembic schema, real virtual table)
with the vector store deliberately made to raise, so the fallback is the only
retrieval route. They confirm the loosening recovers question-form recall while
staying precise for genuinely unrelated queries, and that the categorical FACT
boost surfaces the fact above a more-textually-matching episode.
"""

from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy.ext.asyncio import create_async_engine

from aether.core.exceptions import InfrastructureError
from aether.memory._retrieval.hybrid import HybridRetrieval
from aether.memory._stores.sqlite_store import SQLiteMemoryStore
from aether.memory.models import MemoryFilter, MemorySource, MemoryType

_DUMMY_EMBEDDING = [0.1] * 1024


async def _make_store(db_path: Path) -> SQLiteMemoryStore:
    url = f"sqlite+aiosqlite:///{db_path}"
    engine = create_async_engine(url)
    cfg = Config("alembic.ini")

    def run_upgrade(connection, c):
        c.attributes["connection"] = connection
        command.upgrade(c, "head")

    async with engine.begin() as conn:
        await conn.run_sync(run_upgrade, cfg)
    await engine.dispose()
    return SQLiteMemoryStore(url)


class _UnavailableVectorStore:
    """Stands in for Qdrant being momentarily unavailable — every search raises."""

    async def search(self, *args, **kwargs):
        raise InfrastructureError("Qdrant unavailable (simulated)")


async def _fact_store(db_path: Path) -> SQLiteMemoryStore:
    store = await _make_store(db_path)
    await store.create_memory(
        content="The user's name is Jordan.",
        memory_type=MemoryType.FACT,
        importance=0.85,
        confidence=0.9,
        source=MemorySource.CONVERSATION,
        source_id=None,
        tags=[],
        entities=[],
    )
    return store


@pytest.mark.asyncio
async def test_question_form_recall_via_fts_only_fallback(tmp_path):
    """A question recalls its declarative answer when Qdrant is unavailable."""
    store = await _fact_store(tmp_path / "fb.db")
    hybrid = HybridRetrieval(store, _UnavailableVectorStore())  # type: ignore[arg-type]

    pkg = await hybrid.search(
        query="What is my name?",
        query_embedding=_DUMMY_EMBEDDING,
        k=10,
        filters=MemoryFilter(),
        token_budget=4096,
    )

    assert pkg.memories, "FTS-only fallback returned nothing for the question form"
    assert any("Jordan" in m.content for m in pkg.memories)


@pytest.mark.asyncio
async def test_m218_scenario_qdrant_down_what_is_my_name(tmp_path):
    """The exact scenario M2.1.8 observed: Qdrant momentarily down, 'What is my
    name?' must still recall the Jordan FACT via the FTS fallback."""
    store = await _fact_store(tmp_path / "fb.db")
    hybrid = HybridRetrieval(store, _UnavailableVectorStore())  # type: ignore[arg-type]

    pkg = await hybrid.search(
        query="What is my name?",
        query_embedding=_DUMMY_EMBEDDING,
        k=10,
        filters=MemoryFilter(),
        token_budget=4096,
    )

    assert "Jordan" in pkg.formatted_context
    top = pkg.memories[0]
    assert top.memory_type == MemoryType.FACT
    assert "Jordan" in top.content


@pytest.mark.asyncio
async def test_fallback_stays_precise_for_unrelated_query(tmp_path):
    """Loosening must not make matching indiscriminate: an unrelated question,
    sharing no content word with the fact, returns nothing via the fallback."""
    store = await _fact_store(tmp_path / "fb.db")
    hybrid = HybridRetrieval(store, _UnavailableVectorStore())  # type: ignore[arg-type]

    pkg = await hybrid.search(
        query="What is the weather today?",
        query_embedding=_DUMMY_EMBEDDING,
        k=10,
        filters=MemoryFilter(),
        token_budget=4096,
    )

    assert not any("Jordan" in m.content for m in pkg.memories), (
        "an unrelated query must not match the name fact"
    )


@pytest.mark.asyncio
async def test_fallback_fact_boost_surfaces_fact_above_episode(tmp_path):
    """Both fixes together: with Qdrant down, a question that keyword-matches both
    a FACT and a more-verbose EPISODE ranks the FACT first (loosening finds both;
    the categorical boost orders the fact above the episode)."""
    store = await _make_store(tmp_path / "fb.db")
    await store.create_memory(
        content="The user's name is Jordan.",
        memory_type=MemoryType.FACT,
        importance=0.85,
        confidence=0.9,
        source=MemorySource.CONVERSATION,
        source_id=None,
        tags=[],
        entities=[],
    )
    # An episode that also contains "name", so both surface on the loosened query.
    await store.create_memory(
        content="User Task: the assistant asked the user for their name politely.",
        memory_type=MemoryType.EPISODE,
        importance=0.7,
        confidence=0.9,
        source=MemorySource.CONVERSATION,
        source_id=None,
        tags=[],
        entities=[],
    )

    hybrid = HybridRetrieval(store, _UnavailableVectorStore())  # type: ignore[arg-type]
    pkg = await hybrid.search(
        query="What is my name?",
        query_embedding=_DUMMY_EMBEDDING,
        k=10,
        filters=MemoryFilter(),
        token_budget=4096,
    )

    assert len(pkg.memories) >= 2, "both the fact and the episode should match 'name'"
    assert pkg.memories[0].memory_type == MemoryType.FACT
    assert "Jordan" in pkg.memories[0].content
