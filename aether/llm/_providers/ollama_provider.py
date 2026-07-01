"""Ollama local API provider implementation using litellm."""

import time
from collections.abc import AsyncIterator

import litellm
from pydantic import BaseModel

from aether.core.exceptions import InfrastructureError, LLMProviderError, LLMTimeoutError
from aether.llm._models import LLMResponse, Message, ModelTier
from aether.llm._providers.base import BaseProvider


class OllamaProvider(BaseProvider):
    """Provider for local Ollama models."""

    name = "ollama"

    async def complete(
        self,
        messages: list[Message],
        model: str,
        max_tokens: int,
        temperature: float,
        response_schema: type[BaseModel] | None,
    ) -> LLMResponse:
        """Generate a complete response from Ollama."""
        start_time = time.perf_counter()
        litellm_messages = [{"role": m.role, "content": m.content} for m in messages]

        try:
            kwargs = {
                "model": model,
                "messages": litellm_messages,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "api_base": "http://localhost:11434",
            }
            if response_schema:
                kwargs["response_format"] = response_schema

            response = await litellm.acompletion(**kwargs)

            duration_ms = int((time.perf_counter() - start_time) * 1000)
            content = response.choices[0].message.content or ""

            prompt_tokens = response.usage.prompt_tokens if response.usage else 0
            completion_tokens = response.usage.completion_tokens if response.usage else 0
            total_tokens = response.usage.total_tokens if response.usage else 0

            return LLMResponse(
                content=content,
                model_used=model,
                tier_used=ModelTier.LOCAL,  # Handled by router
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens,
                cost_usd=0.0,  # Local models are always free
                duration_ms=duration_ms,
            )

        except litellm.exceptions.APIConnectionError as e:
            raise InfrastructureError(
                f"Ollama is not running. Start with: ollama serve. Error: {e}"
            ) from e
        except litellm.exceptions.Timeout as e:
            raise LLMTimeoutError(f"Ollama local API timed out: {e}.") from e
        except Exception as e:
            raise LLMProviderError(f"Ollama local API failed: {e}") from e

    async def stream(
        self,
        messages: list[Message],
        model: str,
        max_tokens: int,
    ) -> AsyncIterator[str]:
        """Stream a response from Ollama."""
        litellm_messages = [{"role": m.role, "content": m.content} for m in messages]

        try:
            response_stream = await litellm.acompletion(
                model=model,
                messages=litellm_messages,
                max_tokens=max_tokens,
                stream=True,
                api_base="http://localhost:11434",
            )

            async for chunk in response_stream:
                content = chunk.choices[0].delta.content
                if content:
                    yield content

        except litellm.exceptions.APIConnectionError as e:
            raise InfrastructureError(
                f"Ollama is not running. Start with: ollama serve. Error: {e}"
            ) from e
        except litellm.exceptions.Timeout as e:
            raise LLMTimeoutError(f"Ollama local streaming API timed out: {e}.") from e
        except Exception as e:
            raise LLMProviderError(f"Ollama local streaming API failed: {e}") from e
