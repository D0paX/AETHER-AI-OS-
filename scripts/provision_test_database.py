"""Provision the dedicated Aether test database (M2.1.7).

Creates the disposable test database if it does not exist and runs Alembic
migrations against it fresh. Standalone operational script — never imported by
application or test code. Run once before the integration suite:

    uv run python scripts/provision_test_database.py

or rely on the integration suite's session fixture, which calls
provision_test_database() automatically (tests/integration/conftest.py).

Safety: this script refuses to operate on any database whose name does not
clearly identify it as a test database, and it never issues CREATE DATABASE
against the production database. It creates a NEW, separate database; it never
drops or modifies an existing one.
"""

import argparse
import asyncio
import os
import re
import sys

import structlog
from alembic import command
from alembic.config import Config
from sqlalchemy import text
from sqlalchemy.engine import make_url
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import create_async_engine

logger = structlog.get_logger("provision_test_database")

# A database name is only accepted for provisioning if it is a plain SQL
# identifier AND contains a clear test marker — belt-and-suspenders against
# both injection and pointing at production.
_SAFE_IDENTIFIER = re.compile(r"^[A-Za-z0-9_]+$")
TEST_DB_MARKER = "test"
MAINTENANCE_DB = "postgres"


class TestDatabaseProvisionError(Exception):
    """Raised when the target is unsafe or provisioning fails."""


def _assert_safe_test_db_name(name: str) -> None:
    if not name or not _SAFE_IDENTIFIER.match(name):
        raise TestDatabaseProvisionError(
            f"Refusing to provision: database name {name!r} is not a plain "
            f"identifier ([A-Za-z0-9_])."
        )
    if TEST_DB_MARKER not in name.lower():
        raise TestDatabaseProvisionError(
            f"Refusing to provision: database name {name!r} does not contain "
            f"the required '{TEST_DB_MARKER}' marker. This script never creates "
            f"or touches the production database."
        )


async def _create_database_if_missing(test_url: str) -> None:
    """Create the target database via an AUTOCOMMIT connection to `postgres`."""
    url_obj = make_url(test_url)
    target_db = url_obj.database or ""
    _assert_safe_test_db_name(target_db)

    admin_url = url_obj.set(database=MAINTENANCE_DB).render_as_string(hide_password=False)
    engine = create_async_engine(admin_url, isolation_level="AUTOCOMMIT")
    try:
        async with engine.connect() as conn:
            exists = (
                await conn.execute(
                    text("SELECT 1 FROM pg_database WHERE datname = :name"),
                    {"name": target_db},
                )
            ).scalar()
            if exists:
                logger.info("test_db.exists", database=target_db)
                return
            # target_db validated as a safe identifier above; not user-facing input.
            await conn.execute(text(f'CREATE DATABASE "{target_db}"'))
            logger.info("test_db.created", database=target_db)
    finally:
        await engine.dispose()


async def _run_migrations(test_url: str) -> None:
    """Run `alembic upgrade head` against the test database via a live connection."""
    engine = create_async_engine(test_url)
    alembic_cfg = Config("alembic.ini")

    def run_upgrade(connection: object) -> None:
        alembic_cfg.attributes["connection"] = connection
        command.upgrade(alembic_cfg, "head")

    try:
        async with engine.begin() as conn:
            await conn.run_sync(run_upgrade)
        logger.info("test_db.migrated", database=make_url(test_url).database)
    finally:
        await engine.dispose()


async def provision_test_database(test_url: str) -> None:
    """Create the test database if missing and migrate it to head.

    Args:
        test_url: SQLAlchemy async URL of the dedicated test database.

    Raises:
        TestDatabaseProvisionError: If the target is unsafe or provisioning fails.
    """
    _assert_safe_test_db_name(make_url(test_url).database or "")
    try:
        await _create_database_if_missing(test_url)
        await _run_migrations(test_url)
    except SQLAlchemyError as e:
        raise TestDatabaseProvisionError(
            f"Failed to provision the test database: {type(e).__name__}: {e}"
        ) from e


def _assert_safe_test_collection(name: str) -> None:
    if not name or TEST_DB_MARKER not in name.lower():
        raise TestDatabaseProvisionError(
            f"Refusing to provision: Qdrant collection {name!r} does not contain "
            f"the required '{TEST_DB_MARKER}' marker. This script never creates or "
            f"touches the production collection."
        )


async def provision_test_qdrant_collection(
    host: str, port: int, grpc_port: int, collection: str
) -> None:
    """Create the test Qdrant collection if it does not exist.

    Reuses QdrantMemoryStore.initialize_collection() so the test collection is
    created with the exact production vector configuration (dim=1024, Cosine,
    int8 quantization) rather than a duplicated spec that could drift.

    Args:
        host: Qdrant host.
        port: Qdrant REST port.
        grpc_port: Qdrant gRPC port.
        collection: The test collection name (must contain a 'test' marker).

    Raises:
        TestDatabaseProvisionError: If the collection name is unsafe or creation fails.
    """
    _assert_safe_test_collection(collection)
    # Imported lazily so the DB-only CLI path does not require qdrant_client.
    from aether.memory._stores.vector_store import QdrantMemoryStore

    store = QdrantMemoryStore(
        host=host,
        port=port,
        grpc_port=grpc_port,
        prefer_grpc=True,
        collection_name=collection,
    )
    try:
        await store.initialize_collection()
        logger.info("test_qdrant.ready", collection=collection)
    except Exception as e:  # noqa: BLE001 - re-raised as a provisioning error
        raise TestDatabaseProvisionError(
            f"Failed to provision the test Qdrant collection {collection!r}: "
            f"{type(e).__name__}: {e}"
        ) from e


def _resolve_test_url() -> str:
    url = os.environ.get("AETHER_TEST_DATABASE_URL")
    if url:
        return url
    from aether.core.config import get_config

    return get_config().database.test_url


async def _provision_all(test_url: str) -> None:
    """Provision both the test database and the test Qdrant collection."""
    from aether.core.config import get_config

    await provision_test_database(test_url)

    qdrant = get_config().qdrant
    test_collection = os.environ.get("AETHER_TEST_QDRANT_COLLECTION") or qdrant.test_collection
    await provision_test_qdrant_collection(
        host=qdrant.host,
        port=qdrant.port,
        grpc_port=qdrant.grpc_port,
        collection=test_collection,
    )


def main() -> int:
    """CLI entry point: resolve the test targets and provision database + Qdrant."""
    structlog.configure(processors=[structlog.dev.ConsoleRenderer()])
    parser = argparse.ArgumentParser(
        description="Provision the Aether test database and Qdrant collection (M2.1.7)."
    )
    parser.add_argument(
        "--test-url",
        default=None,
        help="Async SQLAlchemy URL of the test DB (default: AETHER_TEST_DATABASE_URL "
        "env var, else config database.test_url).",
    )
    args = parser.parse_args()

    test_url = args.test_url or _resolve_test_url()
    if not test_url:
        logger.error("provision.no_test_url")
        return 1

    try:
        asyncio.run(_provision_all(test_url))
    except TestDatabaseProvisionError as e:
        logger.error("provision.failed", error=str(e))
        return 1
    logger.info("provision.succeeded", database=make_url(test_url).database)
    return 0


if __name__ == "__main__":
    sys.exit(main())
