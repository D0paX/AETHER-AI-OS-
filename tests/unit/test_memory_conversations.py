"""Unit tests for SQLiteMemoryStore conversation accessors (M2.1.5).

Runs against a real file-based SQLite database with the full alembic schema,
covering get_messages() (newly implemented — specified in
V1_TECHNICAL_SPECIFICATION.md Section 3.2 since Phase 1 but missing until
now) and end_conversation()'s COUNT-derived message_count.
"""

from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from aether.memory._stores.sqlite_store import SQLiteMemoryStore


async def _create_store(db_path: Path) -> SQLiteMemoryStore:
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
async def test_get_messages_returns_rows_oldest_first_with_expected_fields(tmp_path):
    store = await _create_store(tmp_path / "conv.db")
    conv_id = await store.create_conversation("text")

    await store.add_message(conv_id, "user", "first", token_count=3)
    await store.add_message(conv_id, "assistant", "second", token_count=None)
    await store.add_message(conv_id, "user", "third", token_count=7)

    messages = await store.get_messages(conv_id)

    assert [m["content"] for m in messages] == ["first", "second", "third"]
    assert [m["role"] for m in messages] == ["user", "assistant", "user"]
    assert messages[0]["token_count"] == 3
    assert messages[1]["token_count"] is None
    assert all("created_at" in m for m in messages)


@pytest.mark.asyncio
async def test_get_messages_scopes_to_the_requested_conversation(tmp_path):
    store = await _create_store(tmp_path / "conv.db")
    conv_a = await store.create_conversation("text")
    conv_b = await store.create_conversation("text")

    await store.add_message(conv_a, "user", "only in A")
    await store.add_message(conv_b, "user", "only in B")

    messages_a = await store.get_messages(conv_a)

    assert len(messages_a) == 1
    assert messages_a[0]["content"] == "only in A"


@pytest.mark.asyncio
async def test_get_messages_returns_empty_list_for_unknown_conversation(tmp_path):
    store = await _create_store(tmp_path / "conv.db")

    assert await store.get_messages("nonexistent-id") == []


@pytest.mark.asyncio
async def test_end_conversation_sets_ended_at_and_counted_message_count(tmp_path):
    store = await _create_store(tmp_path / "conv.db")
    conv_id = await store.create_conversation("voice")

    for i in range(4):
        await store.add_message(conv_id, "user", f"msg {i}")

    await store.end_conversation(conv_id)

    engine = create_async_engine(f"sqlite+aiosqlite:///{tmp_path / 'conv.db'}")
    try:
        async with engine.connect() as conn:
            row = (
                await conn.execute(
                    text("SELECT ended_at, message_count FROM conversations WHERE id = :id"),
                    {"id": conv_id},
                )
            ).first()
    finally:
        await engine.dispose()

    assert row is not None
    assert row.ended_at is not None
    # The count is derived from the persisted rows, never caller-supplied.
    assert row.message_count == 4
