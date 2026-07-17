"""Real SQLite FTS5 keyword-search tests for SQLiteMemoryStore (M2.1.7, DEBT-004).

Exercises the actual FTS5 query path against a file-backed SQLite database with
the full alembic schema (including the memories_fts virtual table and its sync
triggers). Before M2.1.7 the join used `memories.id = memories_fts.rowid`
(TEXT vs INTEGER) and could never match, so every FTS search silently returned
nothing; these tests would have failed against that bug and now prove the
corrected `memories.rowid = memories_fts.rowid` join returns real matches.
"""

from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy.ext.asyncio import create_async_engine

from aether.memory._stores.sqlite_store import SQLiteMemoryStore
from aether.memory.models import MemoryFilter, MemorySource, MemoryType


async def _make_store(db_path: Path) -> SQLiteMemoryStore:
    url = f"sqlite+aiosqlite:///{db_path}"
    engine = create_async_engine(url)
    alembic_cfg = Config("alembic.ini")

    def run_upgrade(connection, cfg):
        cfg.attributes["connection"] = connection
        command.upgrade(cfg, "head")

    async with engine.begin() as conn:
        await conn.run_sync(run_upgrade, alembic_cfg)
    await engine.dispose()
    return SQLiteMemoryStore(url)


@pytest.mark.asyncio
async def test_fts_returns_real_match_for_present_content(tmp_path):
    store = await _make_store(tmp_path / "fts.db")
    mem_id = await store.create_memory(
        content="The secret code is XYZ-1234",
        memory_type=MemoryType.FACT,
        importance=0.9,
        confidence=0.9,
        source=MemorySource.USER,
        source_id=None,
        tags=[],
        entities=[],
    )

    results = await store.search_fts("secret", limit=10, filters=MemoryFilter())

    assert len(results) == 1, "corrected FTS5 join must return the matching row"
    assert results[0].id == mem_id
    assert results[0].content == "The secret code is XYZ-1234"


@pytest.mark.asyncio
async def test_fts_does_not_match_absent_content(tmp_path):
    store = await _make_store(tmp_path / "fts.db")
    await store.create_memory(
        content="The secret code is XYZ-1234",
        memory_type=MemoryType.FACT,
        importance=0.9,
        confidence=0.9,
        source=MemorySource.USER,
        source_id=None,
        tags=[],
        entities=[],
    )

    results = await store.search_fts("banana", limit=10, filters=MemoryFilter())

    assert results == []


@pytest.mark.asyncio
async def test_fts_returns_correct_row_among_several(tmp_path):
    store = await _make_store(tmp_path / "fts.db")
    await store.create_memory(
        content="User enjoys hiking in the mountains",
        memory_type=MemoryType.PREFERENCE,
        importance=0.6,
        confidence=0.8,
        source=MemorySource.CONVERSATION,
        source_id=None,
        tags=[],
        entities=[],
    )
    target_id = await store.create_memory(
        content="User is deploying a PostgreSQL database this week",
        memory_type=MemoryType.EPISODE,
        importance=0.7,
        confidence=0.8,
        source=MemorySource.CONVERSATION,
        source_id=None,
        tags=[],
        entities=[],
    )
    await store.create_memory(
        content="User prefers concise answers",
        memory_type=MemoryType.PREFERENCE,
        importance=0.5,
        confidence=0.8,
        source=MemorySource.CONVERSATION,
        source_id=None,
        tags=[],
        entities=[],
    )

    results = await store.search_fts("PostgreSQL", limit=10, filters=MemoryFilter())

    assert len(results) == 1
    assert results[0].id == target_id


@pytest.mark.asyncio
async def test_fts_respects_memory_type_filter(tmp_path):
    store = await _make_store(tmp_path / "fts.db")
    await store.create_memory(
        content="deployment notes for the server",
        memory_type=MemoryType.EPISODE,
        importance=0.6,
        confidence=0.8,
        source=MemorySource.CONVERSATION,
        source_id=None,
        tags=[],
        entities=[],
    )

    # Same keyword, but filtering to a type the row does not have -> no match.
    filtered = await store.search_fts(
        "deployment", limit=10, filters=MemoryFilter(memory_types=[MemoryType.FACT])
    )
    assert filtered == []

    unfiltered = await store.search_fts("deployment", limit=10, filters=MemoryFilter())
    assert len(unfiltered) == 1
