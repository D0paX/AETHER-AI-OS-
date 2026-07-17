"""Integration-suite fixtures (M2.1.7).

Provisions the dedicated test database once per integration session. This
conftest only loads when integration tests are collected, so unit-only runs
(which never need PostgreSQL) are unaffected and keep passing with the stack
down. The database-safety guard in tests/conftest_db_guard.py has already
redirected config.database.url to the verified test database before this runs.
"""

import asyncio
import importlib.util
from pathlib import Path

import pytest

# Load the standalone provisioning script by path (it is intentionally not an
# importable package member — same pattern as tests/unit/test_migrate_script.py).
_PROVISION_SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "provision_test_database.py"
_spec = importlib.util.spec_from_file_location("provision_test_database", _PROVISION_SCRIPT)
assert _spec is not None
assert _spec.loader is not None
_provision = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_provision)


async def _provision_all(db_url: str) -> None:
    """Provision the test database and the test Qdrant collection.

    Reads Qdrant settings from config, which the guard has already redirected
    to the test collection (config.qdrant.collection == the test collection).
    """
    from aether.core.config import get_config

    await _provision.provision_test_database(db_url)

    qdrant = get_config().qdrant
    await _provision.provision_test_qdrant_collection(
        host=qdrant.host,
        port=qdrant.port,
        grpc_port=qdrant.grpc_port,
        collection=qdrant.collection,
    )


@pytest.fixture(scope="session", autouse=True)
def _provisioned_test_database(_db_safety_guard: str) -> str:
    """Provision the test database AND Qdrant collection before any integration test.

    Depends on `_db_safety_guard` so all data-store targets are verified and
    config is already redirected before provisioning. Runs the async provisioner
    via asyncio.run() (safe here: no event loop is running during session
    setup), avoiding event-loop-scope mismatches with the suite's
    function-scoped async fixtures. Both test stores are disposable and
    re-provisioned each run, so no teardown is needed. Redis needs no
    provisioning — a non-zero logical DB index always exists.

    Args:
        _db_safety_guard: The verified, active test database URL from the guard.

    Returns:
        The active test database URL.
    """
    asyncio.run(_provision_all(_db_safety_guard))
    return _db_safety_guard
