"""Hard database-safety guard for the Aether test suite (M2.1.7).

This module makes it structurally impossible for a test run to touch the real
production database. It runs FIRST, as a session-scoped autouse fixture, and
FAILS CLOSED: if the configured test database URL does not unambiguously
identify a test database, the entire suite refuses to run before any test body
executes.

Mechanism:
  1. Resolve the dedicated test database URL (AETHER_TEST_DATABASE_URL env var,
     or database.test_url from config).
  2. Verify it names a clearly test-marked database (fail closed otherwise).
  3. Override the process-wide config so every code path that reads
     config.database.url during the session gets the test database — the
     production URL becomes unreachable through config for the whole session.
  4. Re-verify the now-active URL as defense in depth.

Redis and Qdrant isolation are explicitly out of scope for M2.1.7 (see the
milestone note); this guard covers the relational database only.
"""

import os
from urllib.parse import urlparse

import pytest
from sqlalchemy.engine import make_url

import aether.core.config as config_module
from aether.core.config import get_config

# Substring (case-insensitive) a database/collection name must contain to be
# accepted as a test target. Production names ("aether", "episodic_memory")
# lack it and are therefore rejected.
TEST_DB_MARKER = "test"

# The production Redis logical DB index; tests must never use it.
PRODUCTION_REDIS_DB_INDEX = 0

# Environment variables that override the configured test targets.
TEST_DB_ENV_VAR = "AETHER_TEST_DATABASE_URL"
TEST_QDRANT_ENV_VAR = "AETHER_TEST_QDRANT_COLLECTION"
TEST_REDIS_ENV_VAR = "AETHER_TEST_REDIS_URL"

# Nested config env vars pydantic-settings maps to config fields. Setting these
# (plus resetting the singleton) redirects every reader of the corresponding
# config value for the whole test session.
ACTIVE_DB_ENV_VAR = "AETHER_DATABASE__URL"
ACTIVE_QDRANT_ENV_VAR = "AETHER_QDRANT__COLLECTION"
ACTIVE_REDIS_ENV_VAR = "AETHER_REDIS__URL"


class DatabaseSafetyError(Exception):
    """Raised when the configured database is not a safe, clearly-marked test DB.

    Deliberately not an AetherError: this is test-harness infrastructure, not
    application-domain logic, and it must halt the whole session regardless of
    any domain-level exception handling.
    """


def _is_ephemeral_sqlite(url_obj: object, raw_url: str) -> bool:
    """True for in-memory SQLite, which is inherently isolated from production."""
    backend = url_obj.get_backend_name()  # type: ignore[attr-defined]
    return backend.startswith("sqlite") and ":memory:" in raw_url


def verify_test_database_url(url: str) -> None:
    """Raise unless url unambiguously identifies a test database.

    Args:
        url: The database URL the test suite is configured to use.

    Raises:
        DatabaseSafetyError: If url is empty, unparseable, or its database
            name lacks a clear test marker. The message is actionable and never
            includes the URL's password.
    """
    if not url:
        raise DatabaseSafetyError(
            "No test database URL is configured. Set database.test_url in "
            "config/local.yaml or the AETHER_TEST_DATABASE_URL environment "
            "variable to a dedicated test database (its name must contain "
            f"'{TEST_DB_MARKER}', e.g. 'aether_test'). Refusing to run tests."
        )

    try:
        url_obj = make_url(url)
    except Exception as e:  # noqa: BLE001 - re-raised as a safety error, not swallowed
        raise DatabaseSafetyError(
            "The configured test database URL could not be parsed. Fix "
            f"database.test_url / {TEST_DB_ENV_VAR}. Refusing to run tests. "
            f"(parse error: {type(e).__name__})"
        ) from e

    if _is_ephemeral_sqlite(url_obj, url):
        return

    db_name = url_obj.database or ""
    if TEST_DB_MARKER not in db_name.lower():
        # Never echo the password; show only host/port/db-name.
        raise DatabaseSafetyError(
            f"Refusing to run tests: the configured database name {db_name!r} "
            f"(host {url_obj.host}:{url_obj.port}) does not look like a test "
            f"database. Its name must contain '{TEST_DB_MARKER}' (e.g. "
            f"'aether_test'). This guard exists so tests can never touch the "
            f"production database."
        )


def verify_test_qdrant_collection(collection_name: str) -> None:
    """Raise unless collection_name unambiguously identifies a test collection.

    Same fail-closed contract as verify_test_database_url(): the production
    collection ("episodic_memory") and any name lacking a clear test marker are
    rejected before any test body executes.

    Args:
        collection_name: The Qdrant collection the test suite is configured to use.

    Raises:
        DatabaseSafetyError: If the name is empty or lacks a 'test' marker.
    """
    if not collection_name:
        raise DatabaseSafetyError(
            "No test Qdrant collection is configured. Set qdrant.test_collection "
            f"in config or the {TEST_QDRANT_ENV_VAR} environment variable to a "
            f"name containing '{TEST_DB_MARKER}' (e.g. 'episodic_memory_test'). "
            "Refusing to run tests."
        )
    if TEST_DB_MARKER not in collection_name.lower():
        raise DatabaseSafetyError(
            f"Refusing to run tests: the configured Qdrant collection "
            f"{collection_name!r} does not look like a test collection. Its name "
            f"must contain '{TEST_DB_MARKER}' (e.g. 'episodic_memory_test'). This "
            f"guard exists so tests can never write vectors into the production "
            f"collection."
        )


def redis_db_index(url: str) -> int:
    """Return the logical DB index encoded in a redis:// URL (0 if unspecified)."""
    path = urlparse(url).path.lstrip("/")
    if not path:
        return PRODUCTION_REDIS_DB_INDEX
    try:
        return int(path)
    except ValueError as e:
        raise DatabaseSafetyError(
            f"Could not determine the Redis DB index from the configured test "
            f"URL (path segment {path!r} is not an integer). Refusing to run tests."
        ) from e


def verify_test_redis_db_index(db_index: int) -> None:
    """Raise unless db_index is a non-zero (test) Redis logical database.

    Production uses index 0; tests must use a different, non-zero index.

    Args:
        db_index: The Redis logical DB index the test suite is configured to use.

    Raises:
        DatabaseSafetyError: If db_index is the production index (0).
    """
    if db_index == PRODUCTION_REDIS_DB_INDEX:
        raise DatabaseSafetyError(
            f"Refusing to run tests: Redis DB index {db_index} is the production "
            f"default. Tests must use a non-zero index (e.g. 1). Set redis.test_url "
            f"or {TEST_REDIS_ENV_VAR}. This guard exists so tests can never write "
            f"into the production Redis database."
        )


def resolve_test_database_url() -> str:
    """Return the configured test database URL (env var wins over config)."""
    return os.environ.get(TEST_DB_ENV_VAR) or get_config().database.test_url


def resolve_test_qdrant_collection() -> str:
    """Return the configured test Qdrant collection (env var wins over config)."""
    return os.environ.get(TEST_QDRANT_ENV_VAR) or get_config().qdrant.test_collection


def resolve_test_redis_url() -> str:
    """Return the configured test Redis URL (env var wins over config)."""
    return os.environ.get(TEST_REDIS_ENV_VAR) or get_config().redis.test_url


def _reset_config_singleton() -> None:
    """Force the next get_config() to reload from the (now-updated) environment."""
    with config_module._config_lock:
        config_module._config_instance = None


def enforce_test_datastores() -> str:
    """Verify and redirect ALL production data stores to their test equivalents.

    Covers the relational database (config.database.url), the Qdrant vector
    collection (config.qdrant.collection), and the Redis logical database
    (config.redis.url). Every target is verified fail-closed BEFORE any
    redirection, then all three are redirected in one config-singleton reset,
    then each active value is re-verified as defense in depth. After this runs,
    no production data store is reachable through config for the session.

    Returns:
        The active (test) database URL — used by the integration suite to
        provision the test database.

    Raises:
        DatabaseSafetyError: If any configured or resulting target is not a
            clearly-marked test resource.
    """
    test_db_url = resolve_test_database_url()
    test_collection = resolve_test_qdrant_collection()
    test_redis_url = resolve_test_redis_url()

    # Verify every target first — fail closed before touching anything.
    verify_test_database_url(test_db_url)
    verify_test_qdrant_collection(test_collection)
    verify_test_redis_db_index(redis_db_index(test_redis_url))

    # Redirect all three readers for the rest of the session, then reload once.
    os.environ[ACTIVE_DB_ENV_VAR] = test_db_url
    os.environ[ACTIVE_QDRANT_ENV_VAR] = test_collection
    os.environ[ACTIVE_REDIS_ENV_VAR] = test_redis_url
    _reset_config_singleton()

    # Defense in depth: whatever is now active through config must also be safe.
    active = get_config()
    verify_test_database_url(active.database.url)
    verify_test_qdrant_collection(active.qdrant.collection)
    verify_test_redis_db_index(redis_db_index(active.redis.url))
    return active.database.url


# Backwards-compatible alias: Part 1 named the database-only enforcer this.
def enforce_test_database() -> str:
    """Deprecated alias for enforce_test_datastores() (M2.1.7 Part 1 name)."""
    return enforce_test_datastores()


@pytest.fixture(scope="session", autouse=True)
def _db_safety_guard() -> str:
    """Session-scoped, autouse: enforce test isolation for ALL data stores.

    Autouse guarantees no test can opt out. Because it redirects the config
    singleton at session start, the production database, Qdrant collection, and
    Redis logical database are all unreachable through config for the whole run.
    """
    return enforce_test_datastores()
