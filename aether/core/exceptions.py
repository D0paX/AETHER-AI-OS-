"""Aether OS Global Exception Hierarchy.

This module defines the locked exception hierarchy for all Aether subsystems.
All domain exceptions inherit from AetherError.
"""


class AetherError(Exception):
    """Base class for all Aether domain exceptions."""

    def __init__(self, message: str, error_code: str | None = None) -> None:
        """Initialize the base Aether error.

        Args:
            message: The human-readable error message.
            error_code: Optional machine-readable error code.
        """
        super().__init__(message)
        self.error_code = error_code


class ConfigurationError(AetherError):
    """Raised when there is missing or invalid configuration."""


class MemoryRetrievalError(AetherError):
    """Raised on memory recall or search failures."""


class MemoryStorageError(AetherError):
    """Raised on memory write failures."""


class MemoryValidationError(AetherError):
    """Raised on invalid memory parameters."""


class LLMError(AetherError):
    """Base exception for all LLM subsystem failures."""


class LLMTimeoutError(LLMError):
    """Raised when an LLM request times out."""


class LLMProviderError(LLMError):
    """Raised on provider-side failures."""


class LLMBudgetError(LLMError):
    """Raised when the budget is exceeded with no fallback."""


class ToolError(AetherError):
    """Base exception for all tool execution failures."""


class ToolNotFoundError(ToolError):
    """Raised when a tool name is not in the registry."""


class ToolExecutionError(ToolError):
    """Raised when a tool.execute() call fails."""


class ToolPermissionError(ToolError):
    """Raised when a permission check for a tool fails."""


class AgentError(AetherError):
    """Base exception for all agent execution failures."""


class AgentTimeoutError(AgentError):
    """Raised when an agent exceeds its time limit."""


class AgentIterationError(AgentError):
    """Raised when an agent exceeds its iteration limit."""


class VoiceError(AetherError):
    """Base exception for all voice pipeline failures."""


class VoiceTranscriptionError(VoiceError):
    """Raised on Speech-to-Text (STT) failures."""


class VoiceSynthesisError(VoiceError):
    """Raised on Text-to-Speech (TTS) failures."""


class InfrastructureError(AetherError):
    """Raised on Redis or Qdrant connectivity failures."""
