"""Row-for-row fidelity tests for scripts/migrate_sqlite_to_postgres.py (M2.1).

The migration logic is backend-agnostic above the SQLAlchemy dialect boundary,
so fidelity is proven here by migrating a fixture SQLite database into a
second, freshly alembic-migrated SQLite database and verifying exact row
counts, preserved UUIDv7 primary keys, preserved column values, and the
system_kv upsert semantics. The PostgreSQL-specific pieces (target URL
enforcement, pg_isready, alembic against PostgreSQL) are exercised manually
during the real migration run per the M2.1 validation checklist.
"""

import importlib.util
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from uuid_utils import uuid7

_SCRIPT_PATH = Path(__file__).resolve().parents[2] / "scripts" / "migrate_sqlite_to_postgres.py"
_spec = importlib.util.spec_from_file_location("migrate_sqlite_to_postgres", _SCRIPT_PATH)
assert _spec is not None
assert _spec.loader is not None
migrate_script = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(migrate_script)


async def _create_migrated_db(db_path: Path) -> str:
    """Create a file-based SQLite database with the full alembic schema applied."""
    url = f"sqlite+aiosqlite:///{db_path}"
    engine = create_async_engine(url)
    alembic_cfg = Config("alembic.ini")

    def run_upgrade(connection, cfg):
        cfg.attributes["connection"] = connection
        command.upgrade(cfg, "head")

    async with engine.begin() as conn:
        await conn.run_sync(run_upgrade, alembic_cfg)
    await engine.dispose()
    return url


async def _seed_source(url: str) -> dict[str, str]:
    """Insert one row per table into the source database; return the IDs used."""
    ids = {
        "conversation": str(uuid7()),
        "memory": str(uuid7()),
        "task_parent": str(uuid7()),
        "task_child": str(uuid7()),
        "message": str(uuid7()),
        "tool_execution": str(uuid7()),
        "agent_run": str(uuid7()),
        "llm_cost": str(uuid7()),
    }
    engine = create_async_engine(url)
    async with engine.begin() as conn:
        await conn.execute(
            text("UPDATE system_kv SET value = '7' WHERE key = 'aether.total_sessions'")
        )
        await conn.execute(
            text("INSERT INTO conversations (id, mode, title) VALUES (:id, 'text', 'Fixture')"),
            {"id": ids["conversation"]},
        )
        await conn.execute(
            text(
                "INSERT INTO memories (id, content, memory_type, importance, confidence, "
                "source, tags, entities) VALUES (:id, 'User prefers PostgreSQL', 'PREFERENCE', "
                "0.9, 0.8, 'CONVERSATION', '[\"db\"]', '[\"PostgreSQL\"]')"
            ),
            {"id": ids["memory"]},
        )
        await conn.execute(
            text("INSERT INTO tasks (id, title) VALUES (:id, 'Parent task')"),
            {"id": ids["task_parent"]},
        )
        await conn.execute(
            text(
                "INSERT INTO tasks (id, title, parent_task_id) VALUES (:id, 'Child task', :parent)"
            ),
            {"id": ids["task_child"], "parent": ids["task_parent"]},
        )
        await conn.execute(
            text(
                "INSERT INTO messages (id, conversation_id, role, content) "
                "VALUES (:id, :conv, 'user', 'hello aether')"
            ),
            {"id": ids["message"], "conv": ids["conversation"]},
        )
        await conn.execute(
            text(
                "INSERT INTO tool_executions (id, tool_name, agent_name, input_preview, "
                "success, duration_ms) VALUES (:id, 'web_search', 'conversation', "
                '\'{"query": "x"}\', 1, 42)'
            ),
            {"id": ids["tool_execution"]},
        )
        await conn.execute(
            text(
                "INSERT INTO agent_runs (id, agent_name, task_description) "
                "VALUES (:id, 'conversation', 'fixture run')"
            ),
            {"id": ids["agent_run"]},
        )
        await conn.execute(
            text(
                "INSERT INTO llm_costs (id, provider, model, tier, prompt_tokens, "
                "completion_tokens, cost_usd, agent_run_id) VALUES (:id, 'ollama', "
                "'local-model', 'local', 100, 20, 0.0, :run)"
            ),
            {"id": ids["llm_cost"], "run": ids["agent_run"]},
        )
    await engine.dispose()
    return ids


@pytest.mark.asyncio
async def test_migrate_copies_every_table_with_matching_counts_and_values(tmp_path):
    source_url = await _create_migrated_db(tmp_path / "source.db")
    target_url = await _create_migrated_db(tmp_path / "target.db")
    ids = await _seed_source(source_url)

    assert await migrate_script.migrate(source_url, target_url) is True

    source = create_async_engine(source_url)
    target = create_async_engine(target_url)
    try:
        for table, _ in migrate_script.TABLE_COPY_ORDER:
            async with source.connect() as conn:
                src_count = (await conn.execute(text(f"SELECT COUNT(*) FROM {table}"))).scalar()
            async with target.connect() as conn:
                dst_count = (await conn.execute(text(f"SELECT COUNT(*) FROM {table}"))).scalar()
            assert src_count == dst_count, f"count mismatch for {table}"

        async with target.connect() as conn:
            row = (
                await conn.execute(
                    text("SELECT id, content, tags FROM memories WHERE id = :id"),
                    {"id": ids["memory"]},
                )
            ).first()
            assert row is not None
            assert row.id == ids["memory"]  # UUIDv7 preserved byte-for-byte
            assert row.content == "User prefers PostgreSQL"
            assert row.tags == '["db"]'

            child = (
                await conn.execute(
                    text("SELECT parent_task_id FROM tasks WHERE id = :id"),
                    {"id": ids["task_child"]},
                )
            ).first()
            assert child is not None
            assert child.parent_task_id == ids["task_parent"]

            kv = (
                await conn.execute(
                    text("SELECT value FROM system_kv WHERE key = 'aether.total_sessions'")
                )
            ).first()
            assert kv is not None
            assert kv.value == "7"  # source value won the upsert over the 001 seed
    finally:
        await source.dispose()
        await target.dispose()


@pytest.mark.asyncio
async def test_migrate_refuses_to_run_against_non_empty_target(tmp_path):
    source_url = await _create_migrated_db(tmp_path / "source.db")
    target_url = await _create_migrated_db(tmp_path / "target.db")
    await _seed_source(source_url)

    assert await migrate_script.migrate(source_url, target_url) is True
    # Second run must abort in preflight rather than duplicate or clobber rows.
    assert await migrate_script.migrate(source_url, target_url) is False
