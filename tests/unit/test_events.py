"""Unit tests for the Aether OS central event bus."""

import json
from unittest.mock import AsyncMock

import pytest
from pydantic import ValidationError

from aether.core.config import RedisConfig
from aether.core.events import AetherEvent, EventBus


def test_aether_event_is_frozen() -> None:
    """Test that AetherEvent instances cannot be mutated after creation."""
    event = AetherEvent(
        event_id="test-id",
        event_type="test",
        source="test",
        timestamp_utc="2026-06-29T00:00:00Z",
        correlation_id="test-id",
        payload={"key": "value"},
    )

    with pytest.raises(ValidationError):
        event.event_id = "new-id"  # type: ignore


def test_aether_event_requires_all_fields() -> None:
    """Test that AetherEvent validation fails if required fields are missing."""
    with pytest.raises(ValidationError):
        # Missing required fields like event_id, event_type, etc.
        AetherEvent(payload={})  # type: ignore


@pytest.mark.asyncio
async def test_emit_creates_valid_event_id(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that emit() generates a valid UUID event_id."""
    config = RedisConfig()
    bus = EventBus(config)

    # Mock Redis client
    mock_redis = AsyncMock()
    bus._redis = mock_redis

    event_id = await bus.emit(
        event_type="test.event",
        payload={"data": "test"},
    )

    # Check that xadd was called
    mock_redis.xadd.assert_called_once()

    # Check the event_id is a 36-char string (UUID format)
    assert isinstance(event_id, str)
    assert len(event_id) == 36
    assert "-" in event_id


@pytest.mark.asyncio
async def test_emit_sets_timestamp_utc(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that emit() adds a valid UTC timestamp in ISO 8601 format."""
    config = RedisConfig()
    bus = EventBus(config)

    mock_redis = AsyncMock()
    bus._redis = mock_redis

    await bus.emit(
        event_type="test.event",
        payload={"data": "test"},
    )

    # Get the fields passed to xadd
    call_args = mock_redis.xadd.call_args
    assert call_args is not None
    fields = call_args.kwargs.get("fields")

    # Parse the emitted event json
    event_json = fields["event"]
    event_dict = json.loads(event_json)

    # Ensure timestamp_utc is set and has format
    assert "timestamp_utc" in event_dict
    assert "T" in event_dict["timestamp_utc"]


@pytest.mark.asyncio
async def test_emit_returns_event_id_string(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that emit() returns a string."""
    config = RedisConfig()
    bus = EventBus(config)
    bus._redis = AsyncMock()

    event_id = await bus.emit(
        event_type="test.event",
        payload={"data": "test"},
    )

    assert isinstance(event_id, str)
