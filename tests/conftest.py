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
