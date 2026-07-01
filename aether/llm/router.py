"""LLM Router acting as the sole entry point for LLM interactions."""

import asyncio
from collections.abc import AsyncIterator

import redis.asyncio as aioredis
from pydantic import BaseModel

from aether.core.config import get_config
from aether.core.events import EventBus
from aether.core.exceptions import LLMProviderError, LLMTimeoutError
from aether.core.logging import get_logger
from aether.llm._embedding import EmbeddingService
from aether.llm._models import BudgetStatus, Embedding, LLMResponse, Message, ModelTier
from aether.llm._providers.anthropic_provider import AnthropicProvider
from aether.llm._providers.google_provider import GoogleProvider
from aether.llm._providers.ollama_provider import OllamaProvider
from aether.llm.budget import BudgetManager

logger = get_logger("aether.llm.router")


class LLMRouter:
    """The model-agnostic router for all LLM calls in Aether."""

    def __init__(self) -> None:
        """Initialize the router, providers, budget manager, and embedding service."""
        config = get_config()

        # Initialize providers
        self._providers = {
            "anthropic": AnthropicProvider(),
            "google": GoogleProvider(),
            "ollama": OllamaProvider(),
        }

        # Initialize Budget Manager
        self._redis = aioredis.from_url(config.redis.url)  # type: ignore
        self._budget = BudgetManager(config.budget, self._redis)

        # Initialize Event Bus
        self._event_bus = EventBus(config.redis)

        # Initialize Embedding Service lazily or here
        self._embedding_service = EmbeddingService()

        # Resolve tier mappings from config
        self._tier_mapping = {
            ModelTier.LOCAL: config.llm.tiers.local,
            ModelTier.CHEAP: config.llm.tiers.fast or config.llm.tiers.local,
            ModelTier.STANDARD: config.llm.tiers.smart
            or config.llm.tiers.fast
            or config.llm.tiers.local,
            ModelTier.PREMIUM: config.llm.tiers.smart or config.llm.tiers.local,
        }

        # Hardcode fallback chains for robustness
        self._fallback_chain = {
            ModelTier.PREMIUM: [
                ModelTier.PREMIUM,
                ModelTier.STANDARD,
                ModelTier.CHEAP,
                ModelTier.LOCAL,
            ],
            ModelTier.STANDARD: [ModelTier.STANDARD, ModelTier.CHEAP, ModelTier.LOCAL],
            ModelTier.CHEAP: [ModelTier.CHEAP, ModelTier.LOCAL],
            ModelTier.LOCAL: [ModelTier.LOCAL],
        }

        self._max_retries = config.task.max_retries

    async def _connect_bus(self) -> None:
        """Ensure event bus is connected."""
        if not self._event_bus._redis:
            await self._event_bus.connect()

    def _get_provider_for_model(self, model: str) -> str:
        """Route model string to provider name."""
        if model.startswith("claude"):
            return "anthropic"
        elif model.startswith("gemini"):
            return "google"
        elif model.startswith("ollama/"):
            return "ollama"
        # Default fallback to ollama for local models without prefix
        return "ollama"

    async def complete(
        self,
        messages: list[Message],
        tier: ModelTier,
        response_schema: type[BaseModel] | None = None,
        max_tokens: int = 2048,
        temperature: float = 0.7,
        stop_sequences: list[str] | None = None,
    ) -> LLMResponse:
        """Generate a complete response using the fallback chain and budget limits."""
        # 1. Budget Circuit Breaker
        # For check_and_record, we pass 0.0 as estimated cost, then record actual later.
        active_tier = await self._budget.check_and_record(tier, estimated_cost_usd=0.0)
        if active_tier != tier:
            logger.warning(
                "Budget circuit breaker altered requested tier",
                requested=tier.value,
                actual=active_tier.value,
            )

        # 2. Execution with Fallbacks and Retries
        fallback_tiers = self._fallback_chain[active_tier]
        last_exception: Exception | None = None

        for current_tier in fallback_tiers:
            model = self._tier_mapping[current_tier]
            provider_name = self._get_provider_for_model(model)
            provider = self._providers[provider_name]

            for attempt in range(self._max_retries):
                try:
                    logger.info(
                        "Attempting LLM call",
                        tier=current_tier.value,
                        model=model,
                        attempt=attempt + 1,
                    )

                    response = await provider.complete(
                        messages=messages,
                        model=model,
                        max_tokens=max_tokens,
                        temperature=temperature,
                        response_schema=response_schema,
                    )

                    # Rebuild the response with the exact tier used
                    final_response = LLMResponse(
                        content=response.content,
                        model_used=response.model_used,
                        tier_used=current_tier,
                        prompt_tokens=response.prompt_tokens,
                        completion_tokens=response.completion_tokens,
                        total_tokens=response.total_tokens,
                        cost_usd=response.cost_usd,
                        duration_ms=response.duration_ms,
                        cached=response.cached,
                        structured=response.structured,
                    )

                    # 3. Record Actual Cost
                    await self._budget.record_actual_cost(final_response.cost_usd, current_tier)

                    # 4. Emit Event
                    await self._connect_bus()
                    await self._event_bus.emit(
                        event_type="llm.call.completed",
                        payload={
                            "tier": current_tier.value,
                            "model": model,
                            "cost": final_response.cost_usd,
                            "duration_ms": final_response.duration_ms,
                            "tokens": final_response.total_tokens,
                        },
                    )

                    logger.info(
                        "LLM call successful",
                        tier=current_tier.value,
                        model=model,
                        cost=final_response.cost_usd,
                        duration_ms=final_response.duration_ms,
                    )
                    return final_response

                except (LLMTimeoutError, LLMProviderError) as e:
                    logger.warning(
                        "LLM Provider transient error",
                        tier=current_tier.value,
                        model=model,
                        attempt=attempt + 1,
                        error=str(e),
                    )
                    last_exception = e
                    # Exponential backoff
                    await asyncio.sleep(2**attempt)
                except Exception as e:
                    # Non-transient errors (like InfrastructureError for Ollama) break the retry loop
                    logger.error(
                        "LLM Provider fatal error",
                        tier=current_tier.value,
                        model=model,
                        error=str(e),
                    )
                    last_exception = e
                    break  # Break retry loop, move to next fallback tier

        # If we exhausted all fallbacks and retries
        raise last_exception or Exception("All LLM providers in the fallback chain failed.")

    async def stream(
        self,
        messages: list[Message],
        tier: ModelTier,
        max_tokens: int = 2048,
    ) -> AsyncIterator[str]:
        """Stream a response (no cost tracking natively supported here for simplicity)."""
        active_tier = await self._budget.check_and_record(tier, estimated_cost_usd=0.0)
        model = self._tier_mapping[active_tier]
        provider_name = self._get_provider_for_model(model)
        provider = self._providers[provider_name]

        # For streams, we don't handle automatic fallback to keep the iterator clean
        async for chunk in provider.stream(messages=messages, model=model, max_tokens=max_tokens):
            yield chunk

    async def embed(
        self,
        text: str,
        batch: list[str] | None = None,
    ) -> Embedding | list[Embedding]:
        """Generate vector embeddings."""
        if batch:
            return await self._embedding_service.embed_batch(batch)
        return await self._embedding_service.embed(text)

    def get_available_models(self) -> dict[ModelTier, str]:
        """Return the current mapping of tiers to model strings."""
        return self._tier_mapping

    async def get_current_costs(self) -> BudgetStatus:
        """Return the current financial status."""
        return await self._budget.get_status()
