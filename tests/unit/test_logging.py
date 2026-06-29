"""Unit tests for the Aether OS logging module."""

import pytest

from aether.core.config import get_config
from aether.core.logging import (
    bind_contextvars,
    clear_contextvars,
    configure_logging,
    get_logger,
)


@pytest.fixture(autouse=True)
def setup_logging() -> None:
    """Ensure logging is configured before tests."""
    configure_logging(get_config().logging)


def test_get_logger_returns_bound_logger() -> None:
    """Test that get_logger returns a structlog BoundLogger."""
    log = get_logger("test.module")
    assert log is not None
    # Depending on configuration, it could be a BoundLogger or stdlib.BoundLogger
    assert hasattr(log, "info")
    assert hasattr(log, "error")


def test_logger_does_not_raise_on_info() -> None:
    """Test that the logger can write an info event without raising errors."""
    log = get_logger("test.module")
    # This just ensures we don't crash when emitting a log
    log.info("test_event", key="value")


def test_logger_does_not_raise_on_error() -> None:
    """Test that the logger can write an error event without raising errors."""
    log = get_logger("test.module")
    log.error("test_error", error="test")


def test_bind_contextvars_does_not_raise() -> None:
    """Test that context variables can be bound and cleared without errors."""
    bind_contextvars(session_id="test-session")
    log = get_logger("test.module")
    log.info("test_with_context")

    clear_contextvars()
    log.info("test_without_context")
