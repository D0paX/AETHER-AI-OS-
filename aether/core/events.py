"""Aether OS Central Event Bus.

This module implements the event-driven backbone of Aether, using Redis Streams
to coordinate communication between the core kernel, memory subsystem, LLM router,
and independent agents.
"""

import asyncio
from collections.abc import Awaitable, Callable
from datetime import UTC, datetime
from typing import Any

import redis.asyncio as aioredis
import redis.exceptions as redis_exceptions
import uuid_utils
from pydantic import BaseModel, ConfigDict

from aether.core.config import RedisConfig
from aether.core.exceptions import InfrastructureError


class AetherEvent(BaseModel):
    """The central, locked event schema for the Aether OS event bus.

    CRITICAL: This schema is locked and versioned. Do not modify field names.
    """

    model_config = ConfigDict(frozen=True, strict=True)

    event_id: str
    event_type: str
    schema_version: str = "1.0"
    source: str
    timestamp_utc: str
    session_id: str | None = None
    correlation_id: str
    causation_id: str | None = None
    payload: dict[str, Any]
    metadata: dict[str, Any] = {}


class EventBus:
    """Redis Streams-based event bus for reliable, asynchronous event delivery."""

    def __init__(self, config: RedisConfig) -> None:
        """Initialize the event bus.

        Args:
            config: The Redis configuration.
        """
        self._redis_url = config.url
        self._redis: aioredis.Redis | None = None
        self._stream_name = "aether:events"
        self._maxlen = 100000
        self._tasks: list[asyncio.Task[None]] = []

    async def connect(self) -> None:
        """Connect to Redis and ensure the primary event stream exists.

        Raises:
            InfrastructureError: If Redis is unreachable.
        """
        try:
            self._redis = aioredis.from_url(self._redis_url)  # type: ignore
            await self._redis.ping()
        except Exception as e:
            raise InfrastructureError(f"Failed to connect to Redis Event Bus: {e}") from e

    async def disconnect(self) -> None:
        """Gracefully disconnect from Redis and cancel subscriber tasks."""
        for task in self._tasks:
            task.cancel()

        if self._tasks:
            await asyncio.gather(*self._tasks, return_exceptions=True)
            self._tasks.clear()

        if self._redis is not None:
            await self._redis.aclose()
            self._redis = None

    async def emit(
        self,
        event_type: str,
        payload: dict[str, Any],
        session_id: str | None = None,
        correlation_id: str | None = None,
        source: str = "aether.core",
    ) -> str:
        """Emit a new event to the bus.

        Args:
            event_type: The type of event (e.g., "memory.retrieved").
            payload: The unstructured payload for this event.
            session_id: Optional session identifier.
            correlation_id: Optional correlation identifier.
            source: The module emitting the event.

        Returns:
            The unique UUIDv7 event identifier.

        Raises:
            InfrastructureError: If the bus is not connected or the publish fails.
        """
        if self._redis is None:
            raise InfrastructureError("EventBus is not connected.")

        event_id = str(uuid_utils.uuid7())
        corr_id = correlation_id if correlation_id is not None else event_id

        event = AetherEvent(
            event_id=event_id,
            event_type=event_type,
            source=source,
            timestamp_utc=datetime.now(UTC).isoformat(),
            session_id=session_id,
            correlation_id=corr_id,
            payload=payload,
        )

        try:
            # We store the raw JSON strings of the model inside Redis Hash format for the stream
            await self._redis.xadd(
                name=self._stream_name,
                fields={"event": event.model_dump_json()},
                maxlen=self._maxlen,
                approximate=True,
            )
            return event_id
        except Exception as e:
            raise InfrastructureError(f"Failed to emit event {event_id}: {e}") from e

    async def subscribe(
        self,
        event_types: list[str],
        consumer_group: str,
        handler: Callable[[AetherEvent], Awaitable[None]],
        batch_size: int = 10,
    ) -> None:
        """Subscribe to a set of event types using a Redis consumer group.

        Args:
            event_types: The event types to subscribe to (supports 'domain.*' matching).
            consumer_group: The name of the consumer group (usually the component name).
            handler: The async callback to execute when an event matches.
            batch_size: The number of events to read per batch.

        Raises:
            InfrastructureError: If the bus is not connected.
        """
        if self._redis is None:
            raise InfrastructureError("EventBus is not connected.")

        try:
            await self._redis.xgroup_create(
                name=self._stream_name,
                groupname=consumer_group,
                id="0",
                mkstream=True,
            )
        except redis_exceptions.ResponseError as e:
            if "BUSYGROUP" not in str(e):
                raise InfrastructureError(f"Failed to create consumer group: {e}") from e

        consumer_name = str(uuid_utils.uuid7())

        task = asyncio.create_task(
            self._consume_loop(
                consumer_group=consumer_group,
                consumer_name=consumer_name,
                event_types=event_types,
                handler=handler,
                batch_size=batch_size,
            )
        )
        self._tasks.append(task)

    def _matches_pattern(self, event_type: str, patterns: list[str]) -> bool:
        """Check if an event type matches any of the given patterns."""
        for pattern in patterns:
            if pattern.endswith(".*"):
                if event_type.startswith(pattern[:-2]):
                    return True
            elif event_type == pattern:
                return True
        return False

    async def _consume_loop(
        self,
        consumer_group: str,
        consumer_name: str,
        event_types: list[str],
        handler: Callable[[AetherEvent], Awaitable[None]],
        batch_size: int,
    ) -> None:
        """Background task for reading and processing events."""
        if self._redis is None:
            return

        while True:
            try:
                # Block for 1 second, reading from ">" (messages never delivered to other consumers)
                response = await self._redis.xreadgroup(
                    groupname=consumer_group,
                    consumername=consumer_name,
                    streams={self._stream_name: ">"},
                    count=batch_size,
                    block=1000,
                )

                if not response:
                    continue

                stream, messages = response[0]

                for message_id, fields in messages:
                    try:
                        event_json = fields.get(b"event")
                        if event_json:
                            event = AetherEvent.model_validate_json(event_json)
                            if self._matches_pattern(event.event_type, event_types):
                                await handler(event)

                        # Acknowledge regardless of match to advance the consumer offset
                        await self._redis.xack(self._stream_name, consumer_group, message_id)
                    except Exception:
                        # Log error but don't crash consumer loop
                        pass

            except asyncio.CancelledError:
                break
            except Exception:
                # Connection dropped or other error, back off briefly
                await asyncio.sleep(1)
