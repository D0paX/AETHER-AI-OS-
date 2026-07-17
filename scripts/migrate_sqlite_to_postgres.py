"""One-time SQLite to PostgreSQL data migration for Aether OS (Milestone M2.1).

Copies every row of every Phase 1 table from the SQLite database into the
already-migrated-schema PostgreSQL database (run ``alembic upgrade head``
against PostgreSQL first), preserving all column values exactly — including
UUIDv7 primary keys, which are never regenerated. Tables are copied in
foreign-key dependency order, and after each table the copied row count is
verified against a fresh COUNT(*) on the SQLite source; any mismatch aborts
the run with exit code 1 before the next table is touched.

This is a standalone operational script run manually, once, by the developer.
It is not called by any application code and is never imported by aether/.

Usage:
    uv run python scripts/migrate_sqlite_to_postgres.py [--sqlite-path data/aether.db]

The PostgreSQL target URL is read from the application configuration
(config/local.yaml -> database.url) and must be a postgresql+asyncpg URL.

ADR-010 note: this is part of a Level 4 operation. A verified backup
(backup.ps1 manifest showing "verified": true) is mandatory before running.
"""

import argparse
import asyncio
import sys
from dataclasses import dataclass

import structlog
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

logger = structlog.get_logger("migrate_sqlite_to_postgres")

# Copy order respects foreign keys:
#   messages -> conversations, llm_costs -> agent_runs, tasks -> tasks (self).
# Table and column identifiers used in SQL below come exclusively from this
# constant list and from the migrated schema itself — never from user input —
# so f-string interpolation of identifiers is safe; all VALUES are bound.
TABLE_COPY_ORDER: tuple[tuple[str, str], ...] = (
    ("system_kv", "key"),
    ("conversations", "id"),
    ("memories", "id"),
    # created_at first so parent tasks are inserted before their children
    # (parent_task_id self-FK); id as a deterministic tiebreaker.
    ("tasks", "created_at, id"),
    ("messages", "id"),
    ("tool_executions", "id"),
    ("agent_runs", "id"),
    ("llm_costs", "id"),
)

INSERT_CHUNK_SIZE: int = 500

# system_kv is pre-seeded by migration 001 on the target, so its rows are
# upserted (SQLite values win) instead of plainly inserted.
UPSERTED_TABLES: frozenset[str] = frozenset({"system_kv"})


@dataclass(frozen=True)
class TableResult:
    """Per-table outcome of the copy: source and target row counts."""

    table: str
    source_count: int
    target_count: int

    @property
    def matched(self) -> bool:
        """Whether the target row count exactly matches the source."""
        return self.source_count == self.target_count


async def _count_rows(engine: AsyncEngine, table: str) -> int:
    """Return a fresh COUNT(*) for a table (identifier from TABLE_COPY_ORDER)."""
    async with engine.connect() as conn:
        result = await conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
        count = result.scalar()
    return int(count or 0)


async def _fetch_all_rows(
    engine: AsyncEngine, table: str, order_by: str
) -> list[dict[str, object]]:
    """Read every row of a source table in deterministic order."""
    async with engine.connect() as conn:
        result = await conn.execute(text(f"SELECT * FROM {table} ORDER BY {order_by}"))
        return [dict(row) for row in result.mappings().all()]


def _build_insert_sql(table: str, columns: list[str]) -> str:
    """Build a parameterized INSERT (or upsert for system_kv) for a table.

    Identifiers come from the migrated schema; every value is a named bind.
    """
    column_list = ", ".join(columns)
    bind_list = ", ".join(f":{column}" for column in columns)
    sql = f"INSERT INTO {table} ({column_list}) VALUES ({bind_list})"
    if table in UPSERTED_TABLES:
        updates = ", ".join(
            f"{column} = excluded.{column}" for column in columns if column != "key"
        )
        sql += f" ON CONFLICT (key) DO UPDATE SET {updates}"
    return sql


async def _copy_table(
    source: AsyncEngine, target: AsyncEngine, table: str, order_by: str
) -> TableResult:
    """Copy one table from source to target and verify row counts afterward."""
    rows = await _fetch_all_rows(source, table, order_by)
    logger.info("table.copy.started", table=table, source_rows=len(rows))

    if rows:
        insert_sql = _build_insert_sql(table, list(rows[0].keys()))
        async with target.begin() as conn:
            for start in range(0, len(rows), INSERT_CHUNK_SIZE):
                chunk = rows[start : start + INSERT_CHUNK_SIZE]
                await conn.execute(text(insert_sql), chunk)

    source_count = await _count_rows(source, table)
    target_count = await _count_rows(target, table)
    result = TableResult(table=table, source_count=source_count, target_count=target_count)

    if result.matched:
        logger.info(
            "table.copy.completed",
            table=table,
            source_count=source_count,
            target_count=target_count,
        )
    else:
        logger.error(
            "table.copy.count_mismatch",
            table=table,
            source_count=source_count,
            target_count=target_count,
        )
    return result


async def _preflight_target_empty(target: AsyncEngine) -> bool:
    """Verify the target holds no data yet (except migration 001's system_kv seed).

    Prevents an accidental second run from silently duplicating or clobbering
    rows. system_kv is exempt because migration 001 pre-seeds it on the target.
    """
    for table, _ in TABLE_COPY_ORDER:
        if table in UPSERTED_TABLES:
            continue
        count = await _count_rows(target, table)
        if count > 0:
            logger.error(
                "preflight.target_not_empty",
                table=table,
                existing_rows=count,
                hint="The target database already contains data. This script is "
                "one-time-use against a freshly migrated, empty schema.",
            )
            return False
    return True


async def migrate(source_url: str, target_url: str) -> bool:
    """Copy all Phase 1 tables from source_url to target_url with verification.

    Args:
        source_url: SQLAlchemy async URL of the SQLite source database.
        target_url: SQLAlchemy async URL of the target database whose schema
            has already been created via ``alembic upgrade head``.

    Returns:
        True when every table copied with exactly matching row counts.
    """
    source = create_async_engine(source_url, echo=False)
    target = create_async_engine(target_url, echo=False)
    results: list[TableResult] = []

    try:
        if not await _preflight_target_empty(target):
            return False

        for table, order_by in TABLE_COPY_ORDER:
            result = await _copy_table(source, target, table, order_by)
            results.append(result)
            if not result.matched:
                logger.error(
                    "migration.aborted",
                    failed_table=table,
                    reason="Row counts do not match; not proceeding to the next table.",
                )
                return False

        logger.info("migration.summary.header", tables_migrated=len(results))
        for result in results:
            logger.info(
                "migration.summary.table",
                table=result.table,
                source_count=result.source_count,
                target_count=result.target_count,
                status="OK",
            )
        return True
    except (SQLAlchemyError, OSError) as e:
        logger.error("migration.failed", error=str(e), error_type=type(e).__name__)
        return False
    finally:
        await source.dispose()
        await target.dispose()


def main() -> int:
    """CLI entry point: resolve URLs, enforce target dialect, run the migration."""
    structlog.configure(processors=[structlog.dev.ConsoleRenderer()])

    parser = argparse.ArgumentParser(
        description="One-time SQLite to PostgreSQL data migration (M2.1)."
    )
    parser.add_argument(
        "--sqlite-path",
        default="data/aether.db",
        help="Path to the source SQLite database file (default: data/aether.db).",
    )
    args = parser.parse_args()

    from aether.core.config import get_config

    target_url = get_config().database.url
    if not target_url.startswith("postgresql+asyncpg://"):
        logger.error(
            "config.target_not_postgresql",
            configured_url_scheme=target_url.split("://", 1)[0],
            hint="Set database.url in config/local.yaml to the "
            "postgresql+asyncpg URL before running this script.",
        )
        return 1

    source_url = f"sqlite+aiosqlite:///{args.sqlite_path}"
    logger.info("migration.starting", source=args.sqlite_path, target_dialect="postgresql")

    success = asyncio.run(migrate(source_url, target_url))
    if success:
        logger.info(
            "migration.succeeded",
            next_step="Archive the SQLite file (rename to "
            "data/aether.db.pre-postgres-migration); never delete it.",
        )
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
