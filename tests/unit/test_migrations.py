"""Unit tests for SQLite schema and Alembic migrations (M1.4)."""

import asyncio

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import text
from uuid_utils import uuid7


@pytest.mark.asyncio
async def test_upgrade_creates_all_tables(test_db):
    """Verify that `upgrade head` creates all 8 standard tables and FTS virtual tables."""
    async with test_db.begin() as conn:
        result = await conn.execute(
            text("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
        )
        tables = {row[0] for row in result.fetchall()}

    core_expected = {
        "system_kv",
        "conversations",
        "memories",
        "tasks",
        "messages",
        "tool_executions",
        "agent_runs",
        "llm_costs",
        "memories_fts",
        "tasks_fts",
    }
    assert core_expected.issubset(tables)


@pytest.mark.asyncio
async def test_downgrade_removes_tables(test_db):
    """Verify that `downgrade base` removes all non-alembic tables safely."""
    alembic_cfg = Config("alembic.ini")

    def run_downgrade(connection):
        alembic_cfg.attributes["connection"] = connection
        command.downgrade(alembic_cfg, "base")

    async with test_db.begin() as conn:
        await conn.run_sync(run_downgrade)
        result = await conn.execute(
            text("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
        )
        tables = {row[0] for row in result.fetchall()}

    assert tables == {"alembic_version"} or tables == set()


@pytest.mark.asyncio
async def test_upgrade_after_downgrade_succeeds(test_db):
    """Verify that migrating down and back up works (idempotency)."""
    alembic_cfg = Config("alembic.ini")

    def run_downgrade(connection):
        alembic_cfg.attributes["connection"] = connection
        command.downgrade(alembic_cfg, "base")

    def run_upgrade(connection):
        alembic_cfg.attributes["connection"] = connection
        command.upgrade(alembic_cfg, "head")

    async with test_db.begin() as conn:
        await conn.run_sync(run_downgrade)
        await conn.run_sync(run_upgrade)
        result = await conn.execute(
            text("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
        )
        tables = {row[0] for row in result.fetchall()}

    assert "tasks" in tables
    assert "memories_fts" in tables


@pytest.mark.asyncio
async def test_fts5_insert_is_searchable(test_db):
    """Verify that FTS5 triggers sync data correctly on INSERT, UPDATE, DELETE."""
    async with test_db.begin() as conn:
        id1 = str(uuid7())
        await conn.execute(
            text(
                "INSERT INTO memories (id, content, memory_type, source) VALUES (:id, 'The secret code is XYZ-1234', 'episodic', 'user')"
            ),
            {"id": id1},
        )

        # Search FTS5
        result = await conn.execute(
            text("SELECT rowid FROM memories_fts WHERE memories_fts MATCH 'secret'")
        )
        rows = result.fetchall()
        assert len(rows) == 1

        # Test trigger update
        await conn.execute(
            text("UPDATE memories SET content = 'The hidden code is XYZ-1234' WHERE id = :id"),
            {"id": id1},
        )
        result2 = await conn.execute(
            text("SELECT rowid FROM memories_fts WHERE memories_fts MATCH 'secret'")
        )
        assert len(result2.fetchall()) == 0

        result3 = await conn.execute(
            text("SELECT rowid FROM memories_fts WHERE memories_fts MATCH 'hidden'")
        )
        assert len(result3.fetchall()) == 1

        # Test delete
        await conn.execute(text("DELETE FROM memories WHERE id = :id"), {"id": id1})
        result4 = await conn.execute(
            text("SELECT rowid FROM memories_fts WHERE memories_fts MATCH 'hidden'")
        )
        assert len(result4.fetchall()) == 0


@pytest.mark.asyncio
async def test_system_kv_prepopulated(test_db):
    """Verify that `system_kv` is seeded with initial configuration on upgrade."""
    async with test_db.begin() as conn:
        result = await conn.execute(
            text("SELECT value FROM system_kv WHERE key = 'aether.version'")
        )
        row = result.fetchone()
        assert row is not None
        assert row[0] == '"1.0.0"'


@pytest.mark.asyncio
async def test_tasks_updated_at_trigger(test_db):
    """Verify that the updated_at column automatically shifts on row modification."""
    async with test_db.begin() as conn:
        id1 = str(uuid7())
        await conn.execute(
            text("INSERT INTO tasks (id, title) VALUES (:id, 'Test task')"), {"id": id1}
        )

        result1 = await conn.execute(
            text("SELECT updated_at FROM tasks WHERE id = :id"), {"id": id1}
        )
        updated1 = result1.fetchone()[0]

        # SQLite strftime('%Y-%m-%dT%H:%M:%fZ') resolution has ms precision.
        # A tiny sleep ensures the clock shifts enough for a test.
        await asyncio.sleep(0.01)

        await conn.execute(
            text("UPDATE tasks SET status = 'in_progress' WHERE id = :id"), {"id": id1}
        )

        result2 = await conn.execute(
            text("SELECT updated_at FROM tasks WHERE id = :id"), {"id": id1}
        )
        updated2 = result2.fetchone()[0]

        assert updated1 != updated2


@pytest.mark.asyncio
async def test_primary_keys_accept_uuidv7(test_db):
    """Verify UUIDv7 PK insertion works flawlessly."""
    async with test_db.begin() as conn:
        id1 = str(uuid7())
        await conn.execute(text("INSERT INTO conversations (id) VALUES (:id)"), {"id": id1})
        result = await conn.execute(
            text("SELECT id FROM conversations WHERE id = :id"), {"id": id1}
        )
        row = result.fetchone()
        assert row is not None
        assert row[0] == id1


@pytest.mark.asyncio
async def test_conversations_messages_cascade_delete(test_db):
    """Verify that ON DELETE CASCADE removes child messages when conversation is deleted."""
    async with test_db.begin() as conn:
        # SQLite requires PRAGMA foreign_keys = ON per connection.
        await conn.execute(text("PRAGMA foreign_keys = ON;"))

        conv_id = str(uuid7())
        msg_id = str(uuid7())
        await conn.execute(text("INSERT INTO conversations (id) VALUES (:id)"), {"id": conv_id})
        await conn.execute(
            text(
                "INSERT INTO messages (id, conversation_id, role, content) VALUES (:mid, :cid, 'user', 'hello')"
            ),
            {"mid": msg_id, "cid": conv_id},
        )

        await conn.execute(text("DELETE FROM conversations WHERE id = :id"), {"id": conv_id})

        result = await conn.execute(
            text("SELECT id FROM messages WHERE id = :mid"), {"mid": msg_id}
        )
        assert result.fetchone() is None
