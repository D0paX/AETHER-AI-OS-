"""Aether OS Core Infrastructure API.

This module exposes the locked API surface for the core infrastructure components,
including configuration, logging, the event bus, and the global exception hierarchy.
"""

from aether.core.config import EMBEDDING_DIMENSION, AetherConfig, get_config
from aether.core.events import AetherEvent, EventBus
from aether.core.exceptions import (
    AetherError,
    AgentError,
    AgentIterationError,
    AgentTimeoutError,
    ConfigurationError,
    InfrastructureError,
    LLMBudgetError,
    LLMError,
    LLMProviderError,
    LLMTimeoutError,
    MemoryRetrievalError,
    MemoryStorageError,
    MemoryValidationError,
    ToolError,
    ToolExecutionError,
    ToolNotFoundError,
    ToolPermissionError,
    VoiceError,
    VoiceSynthesisError,
    VoiceTranscriptionError,
)
from aether.core.logging import (
    bind_contextvars,
    clear_contextvars,
    configure_logging,
    get_logger,
)

__all__ = [
    # Config
    "AetherConfig",
    "get_config",
    "EMBEDDING_DIMENSION",
    # Logging
    "configure_logging",
    "get_logger",
    "bind_contextvars",
    "clear_contextvars",
    # Events
    "EventBus",
    "AetherEvent",
    # Exceptions
    "AetherError",
    "ConfigurationError",
    "LLMError",
    "LLMTimeoutError",
    "LLMProviderError",
    "LLMBudgetError",
    "MemoryRetrievalError",
    "MemoryStorageError",
    "MemoryValidationError",
    "ToolError",
    "ToolNotFoundError",
    "ToolExecutionError",
    "ToolPermissionError",
    "AgentError",
    "AgentTimeoutError",
    "AgentIterationError",
    "VoiceError",
    "VoiceTranscriptionError",
    "VoiceSynthesisError",
    "InfrastructureError",
]
