"""Aether OS Structured Logging Module.

This module provides the global structured logging configuration using structlog.
It supports JSON output for production, colored output for development,
and context variables for distributed tracing.
"""

import logging
import logging.handlers
from typing import Any

import structlog

from aether.core.config import LoggingConfig, get_config


def configure_logging(config: LoggingConfig) -> None:
    """Configure structlog processors and the underlying standard logging.

    Args:
        config: The logging configuration settings.
    """
    environment = get_config().environment

    # Define structlog processors
    processors: list[structlog.types.Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    # Configure the standard logging handlers
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    # Remove existing handlers to avoid duplicates during tests or reloads
    root_logger.handlers.clear()

    # File Handler (always JSON)
    config.file_path.parent.mkdir(parents=True, exist_ok=True)
    file_handler = logging.handlers.RotatingFileHandler(
        filename=config.file_path,
        maxBytes=config.max_file_mb * 1024 * 1024,
        backupCount=config.backup_count,
        encoding="utf-8",
    )

    # We use structlog.stdlib.ProcessorFormatter to format standard logs
    file_formatter = structlog.stdlib.ProcessorFormatter(
        processors=[structlog.processors.JSONRenderer()]
    )
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)

    # Console Handler (JSON in prod, colored in dev)
    console_handler = logging.StreamHandler()
    if environment == "production":
        console_formatter = structlog.stdlib.ProcessorFormatter(
            processors=[structlog.processors.JSONRenderer()]
        )
    else:
        console_formatter = structlog.stdlib.ProcessorFormatter(
            processors=[structlog.dev.ConsoleRenderer(colors=True)]
        )
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)

    # Configure structlog bound logger settings
    structlog.configure(
        processors=processors
        + [
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> structlog.BoundLogger:
    """Get a structured logger bound to the given module name.

    Args:
        name: The name of the logger (usually __name__).

    Returns:
        A structlog bound logger.
    """
    from typing import cast

    return cast(structlog.BoundLogger, structlog.get_logger(name))


def clear_contextvars() -> None:
    """Clear all logging context variables for a new request."""
    structlog.contextvars.clear_contextvars()


def bind_contextvars(**kwargs: Any) -> None:
    """Bind context variables to all subsequent log entries.

    Args:
        **kwargs: Key-value pairs to bind to the context.
    """
    structlog.contextvars.bind_contextvars(**kwargs)
