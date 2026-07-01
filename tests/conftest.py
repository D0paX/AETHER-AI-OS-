"""Global pytest configuration and shared fixtures for Aether OS tests."""

from unittest.mock import AsyncMock

import pytest

from aether.core.events import EventBus


@pytest.fixture
def mock_event_bus() -> EventBus:
    """Provide a mock EventBus that bypasses real Redis for unit tests."""
    # We don't actually pass config to the mock
    bus = EventBus(config=AsyncMock())

    bus._redis = AsyncMock()
    bus.connect = AsyncMock()  # type: ignore
    bus.disconnect = AsyncMock()  # type: ignore

    # We still want emit to run through its logic, so we just mock xadd
    bus._redis.xadd = AsyncMock()
    bus._redis.xgroup_create = AsyncMock()
    bus._redis.xreadgroup = AsyncMock()
    bus._redis.xack = AsyncMock()

    return bus


@pytest.fixture
def mock_llm_router() -> AsyncMock:
    """Provide a mock LLMRouter that bypasses real API calls."""
    from aether.llm._models import LLMResponse, ModelTier

    router = AsyncMock()

    # Setup complete() to return a valid dummy response
    mock_response = LLMResponse(
        content="Dummy response",
        model_used="dummy-model",
        tier_used=ModelTier.LOCAL,
        prompt_tokens=10,
        completion_tokens=20,
        total_tokens=30,
        cost_usd=0.0,
        duration_ms=100,
    )
    router.complete.return_value = mock_response

    return router


@pytest.fixture
async def test_db():
    """Create in-memory SQLite database and run alembic migrations."""
    from alembic import command
    from alembic.config import Config
    from sqlalchemy.ext.asyncio import create_async_engine
    from sqlalchemy.pool import StaticPool

    # We must use StaticPool so that the in-memory database persists across connections.
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        poolclass=StaticPool,
    )

    alembic_cfg = Config("alembic.ini")

    def run_upgrade(connection, cfg):
        cfg.attributes["connection"] = connection
        command.upgrade(cfg, "head")

    def run_downgrade(connection, cfg):
        cfg.attributes["connection"] = connection
        command.downgrade(cfg, "base")

    async with engine.begin() as conn:
        await conn.run_sync(run_upgrade, alembic_cfg)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(run_downgrade, alembic_cfg)

    await engine.dispose()
