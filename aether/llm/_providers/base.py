"""Base interface for all LLM providers."""

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from typing import ClassVar

from pydantic import BaseModel

from aether.llm._models import LLMResponse, Message


class BaseProvider(ABC):
    """Abstract base class for all LLM providers."""

    name: ClassVar[str]

    @abstractmethod
    async def complete(
        self,
        messages: list[Message],
        model: str,
        max_tokens: int,
        temperature: float,
        response_schema: type[BaseModel] | None,
    ) -> LLMResponse:
        """Generate a complete response from the LLM.

        Args:
            messages: The chat history.
            model: The specific model string to use.
            max_tokens: Maximum tokens to generate.
            temperature: Sampling temperature.
            response_schema: Optional Pydantic model for structured output.

        Returns:
            An LLMResponse containing the output and metadata.
        """

    @abstractmethod
    def stream(
        self,
        messages: list[Message],
        model: str,
        max_tokens: int,
    ) -> AsyncIterator[str]:
        """Stream a response from the LLM.

        Args:
            messages: The chat history.
            model: The specific model string to use.
            max_tokens: Maximum tokens to generate.

        Yields:
            Chunks of text as they arrive.
        """
