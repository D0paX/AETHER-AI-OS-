"""Integration tests for the Aether OS Event Bus and Configuration."""

import asyncio
import json

import pytest
import redis.asyncio as aioredis

from aether.core.config import get_config
from aether.core.events import EventBus

pytestmark = pytest.mark.integration


# Skip these tests if Redis is not running
async def is_redis_reachable() -> bool:
    try:
        config = get_config()
        client = aioredis.from_url(config.redis.url)
        await client.ping()
        await client.aclose()
        return True
    except Exception:
        return False


# Evaluate synchronously at import time by running a tiny event loop
_redis_reachable = asyncio.run(is_redis_reachable())
if not _redis_reachable:
    pytest.skip("Redis is not reachable. Skipping integration tests.", allow_module_level=True)


@pytest.fixture
async def event_bus() -> EventBus:
    """Provide a connected EventBus instance for testing."""
    config = get_config()
    bus = EventBus(config.redis)
    await bus.connect()
    yield bus
    await bus.disconnect()


@pytest.mark.asyncio
async def test_event_bus_connects_to_redis() -> None:
    """Test that EventBus successfully connects to the real Redis instance."""
    config = get_config()
    bus = EventBus(config.redis)
    await bus.connect()
    assert bus._redis is not None
    await bus.disconnect()


@pytest.mark.asyncio
async def test_emit_and_stream_exists(event_bus: EventBus) -> None:
    """Test that emitting an event creates the stream and adds length."""
    await event_bus.emit(
        event_type="test.integration.fired",
        payload={"msg": "hello"},
    )

    assert event_bus._redis is not None
    xlen = await event_bus._redis.xlen(event_bus._stream_name)
    assert xlen > 0


@pytest.mark.asyncio
async def test_emitted_event_has_correct_type(event_bus: EventBus) -> None:
    """Test that an emitted event can be read back and has the correct type."""
    assert event_bus._redis is not None

    # Emit
    event_id = await event_bus.emit(
        event_type="test.integration.readback",
        payload={"msg": "verify_type"},
    )

    # Read back exactly that event using XRANGE
    response = await event_bus._redis.xrange(
        name=event_bus._stream_name,
        min=b"-",
        max=b"+",
    )

    found = False
    for _, fields in response:
        event_json = fields.get(b"event")
        if event_json:
            event_dict = json.loads(event_json)
            if event_dict["event_id"] == event_id:
                assert event_dict["event_type"] == "test.integration.readback"
                found = True
                break

    assert found, "Emitted event was not found in the stream."
