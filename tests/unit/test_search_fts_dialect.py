"""Unit tests for the dialect-dispatching keyword search in SQLiteMemoryStore (M2.1).

search_fts()'s public signature is locked; these tests assert that the
internal SQL dispatches correctly per dialect: pg_trgm word similarity on
PostgreSQL, the original FTS5 MATCH query on SQLite, with identical
sanitisation and failure semantics on both paths.
"""

from datetime import UTC, datetime

import pytest
from sqlalchemy.exc import SQLAlchemyError

from aether.memory._stores.sqlite_store import SQLiteMemoryStore
from aether.memory.models import MemoryFilter, MemorySource, MemoryType


def _fake_row(content: str = "test fact") -> dict[str, object]:
    now = datetime.now(UTC).isoformat()
    return {
        "id": "01932e4f-a7c2-7000-b3e2-000000000001",
        "content": content,
        "memory_type": MemoryType.FACT.value,
        "importance": 0.7,
        "confidence": 0.9,
        "source": MemorySource.CONVERSATION.value,
        "tags": "[]",
        "entities": "[]",
        "created_at": now,
        "last_accessed_at": now,
        "access_count": 0,
    }


class _FakeResult:
    def __init__(self, rows: list[dict[str, object]]):
        self._rows = rows

    def mappings(self) -> "_FakeResult":
        return self

    def all(self) -> list[dict[str, object]]:
        return self._rows


class _FakeSession:
    """Async-context session capturing executed SQL and bound parameters."""

    def __init__(self, rows: list[dict[str, object]], error: Exception | None = None):
        self.rows = rows
        self.error = error
        self.executed: list[tuple[str, dict[str, object]]] = []

    async def __aenter__(self) -> "_FakeSession":
        return self

    async def __aexit__(self, *exc_info: object) -> bool:
        return False

    async def execute(self, statement: object, params: dict[str, object]) -> _FakeResult:
        self.executed.append((str(statement), params))
        if self.error is not None:
            raise self.error
        return _FakeResult(self.rows)


def _make_store(
    dialect: str, rows: list[dict[str, object]] | None = None, error: Exception | None = None
) -> tuple[SQLiteMemoryStore, _FakeSession]:
    store = SQLiteMemoryStore("sqlite+aiosqlite:///:memory:")
    store._dialect_name = dialect
    session = _FakeSession(rows or [], error=error)
    store._session_factory = lambda: session  # type: ignore[assignment]
    return store, session


@pytest.mark.asyncio
async def test_search_fts_postgresql_dialect_uses_trigram_sql():
    store, session = _make_store("postgresql", rows=[_fake_row()])

    records = await store.search_fts("test", limit=5, filters=MemoryFilter())

    assert len(session.executed) == 1
    sql, params = session.executed[0]
    assert "word_similarity" in sql
    assert "<%" in sql
    assert "MATCH" not in sql
    assert "memories_fts" not in sql
    assert params["query"] == "test"
    assert params["limit"] == 5
    assert len(records) == 1
    assert records[0].content == "test fact"
    assert records[0].memory_type == MemoryType.FACT


@pytest.mark.asyncio
async def test_search_fts_sqlite_dialect_keeps_fts5_match_sql():
    store, session = _make_store("sqlite", rows=[_fake_row()])

    records = await store.search_fts("test", limit=5, filters=MemoryFilter())

    assert len(session.executed) == 1
    sql, _ = session.executed[0]
    assert "memories_fts MATCH :query" in sql
    assert "word_similarity" not in sql
    assert len(records) == 1


@pytest.mark.asyncio
async def test_search_fts_punctuation_only_query_returns_empty_without_executing():
    for dialect in ("postgresql", "sqlite"):
        store, session = _make_store(dialect)

        records = await store.search_fts("?!...", limit=5, filters=MemoryFilter())

        assert records == []
        assert session.executed == []


@pytest.mark.asyncio
async def test_search_fts_applies_filters_identically_on_both_dialects():
    filters = MemoryFilter(
        memory_types=[MemoryType.FACT, MemoryType.PREFERENCE],
        source=MemorySource.USER,
        min_importance=0.4,
        min_confidence=0.6,
    )

    for dialect in ("postgresql", "sqlite"):
        store, session = _make_store(dialect, rows=[])
        await store.search_fts("query", limit=3, filters=filters)

        sql, params = session.executed[0]
        assert "m.memory_type IN (:mt_0,:mt_1)" in sql
        assert "m.source = :source" in sql
        assert "m.importance >= :min_imp" in sql
        assert "m.confidence >= :min_conf" in sql
        assert params["mt_0"] == MemoryType.FACT.value
        assert params["mt_1"] == MemoryType.PREFERENCE.value
        assert params["source"] == MemorySource.USER.value
        assert params["min_imp"] == 0.4
        assert params["min_conf"] == 0.6


@pytest.mark.asyncio
async def test_search_fts_query_failure_returns_empty_list_on_both_dialects():
    for dialect in ("postgresql", "sqlite"):
        store, _ = _make_store(dialect, error=SQLAlchemyError("backend unavailable"))

        records = await store.search_fts("test", limit=5, filters=MemoryFilter())

        assert records == []
