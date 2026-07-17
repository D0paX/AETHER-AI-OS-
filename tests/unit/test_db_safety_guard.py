"""Tests for the database-safety guard (M2.1.7).

Proves the guard fails closed: any database URL that does not unambiguously
identify a test database is rejected before it could ever be used. These are
the automated counterpart to the milestone's manual "deliberately misconfigure
and confirm the suite refuses to run" validation.
"""

import pytest
from conftest_db_guard import (
    TestDatabaseSafetyError,
    redis_db_index,
    verify_test_database_url,
    verify_test_qdrant_collection,
    verify_test_redis_db_index,
)


def test_rejects_production_database_name():
    prod_url = "postgresql+asyncpg://aether:pw@localhost:5432/aether"
    with pytest.raises(TestDatabaseSafetyError, match="does not look like a test database"):
        verify_test_database_url(prod_url)


def test_rejects_empty_url():
    with pytest.raises(TestDatabaseSafetyError, match="No test database URL"):
        verify_test_database_url("")


def test_rejects_unparseable_url():
    with pytest.raises(TestDatabaseSafetyError, match="could not be parsed"):
        verify_test_database_url("this is not a url")


def test_error_message_never_contains_password():
    prod_url = "postgresql+asyncpg://aether:SuperSecretPassword123@localhost:5432/aether"
    with pytest.raises(TestDatabaseSafetyError) as exc_info:
        verify_test_database_url(prod_url)
    assert "SuperSecretPassword123" not in str(exc_info.value)


def test_accepts_suffix_test_marker():
    # aether_test contains the required marker; must NOT raise.
    verify_test_database_url("postgresql+asyncpg://aether:pw@localhost:5432/aether_test")


def test_accepts_prefix_test_marker():
    verify_test_database_url("postgresql+asyncpg://aether:pw@localhost:5432/test_aether")


def test_accepts_in_memory_sqlite():
    # Ephemeral in-memory SQLite is inherently isolated; must NOT raise.
    verify_test_database_url("sqlite+aiosqlite:///:memory:")


def test_rejects_file_sqlite_without_test_marker():
    with pytest.raises(TestDatabaseSafetyError):
        verify_test_database_url("sqlite+aiosqlite:///data/aether.db")


def test_marker_check_is_case_insensitive():
    verify_test_database_url("postgresql+asyncpg://aether:pw@localhost:5432/AetherTESTdb")


# --- Qdrant collection guard (M2.1.7 Part 2) ---


def test_rejects_production_qdrant_collection():
    with pytest.raises(TestDatabaseSafetyError, match="does not look like a test collection"):
        verify_test_qdrant_collection("episodic_memory")


def test_rejects_empty_qdrant_collection():
    with pytest.raises(TestDatabaseSafetyError, match="No test Qdrant collection"):
        verify_test_qdrant_collection("")


def test_accepts_test_qdrant_collection():
    verify_test_qdrant_collection("episodic_memory_test")


def test_qdrant_marker_check_is_case_insensitive():
    verify_test_qdrant_collection("Episodic_TEST")


# --- Redis DB index guard (M2.1.7 Part 2) ---


def test_rejects_production_redis_index_zero():
    with pytest.raises(TestDatabaseSafetyError, match="production default"):
        verify_test_redis_db_index(0)


def test_accepts_nonzero_redis_index():
    verify_test_redis_db_index(1)
    verify_test_redis_db_index(2)


def test_redis_db_index_parses_url_path():
    assert redis_db_index("redis://127.0.0.1:6379/1") == 1
    assert redis_db_index("redis://127.0.0.1:6379/5") == 5


def test_redis_db_index_defaults_to_zero_when_absent():
    # No path segment -> production index 0 -> must be rejected by the verifier.
    assert redis_db_index("redis://127.0.0.1:6379") == 0
    with pytest.raises(TestDatabaseSafetyError):
        verify_test_redis_db_index(redis_db_index("redis://127.0.0.1:6379"))


def test_production_redis_url_is_rejected_end_to_end():
    prod_redis = "redis://127.0.0.1:6379/0"
    with pytest.raises(TestDatabaseSafetyError, match="production default"):
        verify_test_redis_db_index(redis_db_index(prod_redis))
