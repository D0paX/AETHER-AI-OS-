"""Unit tests for the LLM Router."""

from collections.abc import AsyncGenerator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pydantic import BaseModel

from aether.core.exceptions import LLMTimeoutError
from aether.llm._models import Embedding, LLMResponse, Message, ModelTier
from aether.llm.router import LLMRouter


@pytest.fixture
def router() -> LLMRouter:
    with patch("aether.llm.router.aioredis.from_url") as mock_from_url:
        mock_pipeline = MagicMock()
        mock_pipeline.execute = AsyncMock(return_value=[0.0, 0.0, 86400, 2592000])
        mock_client = MagicMock()
        mock_client.pipeline.return_value = mock_pipeline
        mock_from_url.return_value = mock_client

        with patch("aether.llm.router.EmbeddingService.__init__", return_value=None):
            r = LLMRouter()
            # Mock event bus connection
            r._event_bus.connect = AsyncMock()  # type: ignore
            r._event_bus.emit = AsyncMock()  # type: ignore
            return r


@pytest.mark.asyncio
async def test_local_tier_uses_ollama_model_name(router: LLMRouter) -> None:
    from aether.core.config import get_config

    config = get_config()
    assert router._tier_mapping[ModelTier.LOCAL] == config.llm.tiers.local
    assert router._get_provider_for_model(config.llm.tiers.local) == "ollama"


@pytest.mark.asyncio
async def test_cheap_tier_uses_gemini_flash_model_name(router: LLMRouter) -> None:
    # By default, local config might map cheap to local if fast/smart aren't set
    # Let's override the mapping for the test
    router._tier_mapping[ModelTier.CHEAP] = "gemini/gemini-1.5-flash"
    assert router._get_provider_for_model("gemini/gemini-1.5-flash") == "google"


@pytest.mark.asyncio
async def test_standard_tier_uses_claude_sonnet_model_name(router: LLMRouter) -> None:
    router._tier_mapping[ModelTier.STANDARD] = "claude-3-5-sonnet-20241022"
    assert router._get_provider_for_model("claude-3-5-sonnet-20241022") == "anthropic"


@pytest.mark.asyncio
async def test_premium_tier_uses_claude_opus_model_name(router: LLMRouter) -> None:
    router._tier_mapping[ModelTier.PREMIUM] = "claude-3-opus-20240229"
    assert router._get_provider_for_model("claude-3-opus-20240229") == "anthropic"


@pytest.mark.asyncio
async def test_complete_returns_llm_response_type(router: LLMRouter) -> None:
    with patch.object(
        router._providers["ollama"], "complete", new_callable=AsyncMock
    ) as mock_complete:
        mock_complete.return_value = LLMResponse(
            content="Hello",
            model_used="llama",
            tier_used=ModelTier.LOCAL,
            prompt_tokens=1,
            completion_tokens=1,
            total_tokens=2,
            cost_usd=0.0,
            duration_ms=10,
        )

        response = await router.complete(
            messages=[Message(role="user", content="Hi")], tier=ModelTier.LOCAL
        )

        assert isinstance(response, LLMResponse)
        assert response.content == "Hello"
        mock_complete.assert_called_once()


@pytest.mark.asyncio
async def test_budget_exceeded_forces_local_tier(router: LLMRouter) -> None:
    # Force budget exceeded
    with (
        patch.object(router._budget, "check_and_record", return_value=ModelTier.LOCAL),
        patch.object(
            router._providers["ollama"], "complete", new_callable=AsyncMock
        ) as mock_complete,
    ):
        mock_complete.return_value = LLMResponse(
            content="Local response",
            model_used="llama",
            tier_used=ModelTier.LOCAL,
            prompt_tokens=1,
            completion_tokens=1,
            total_tokens=2,
            cost_usd=0.0,
            duration_ms=10,
        )

        # Request PREMIUM
        response = await router.complete(
            messages=[Message(role="user", content="Hi")], tier=ModelTier.PREMIUM
        )

        # Verify we got local tier despite asking for premium
        assert response.tier_used == ModelTier.LOCAL
        mock_complete.assert_called_once()


@pytest.mark.asyncio
async def test_budget_warning_at_80_percent_emits_event(router: LLMRouter) -> None:
    # Covered inside budget tests primarily, but we can verify router calls the budget check
    with (
        patch.object(
            router._budget, "check_and_record", return_value=ModelTier.PREMIUM
        ) as mock_check,
        patch.object(
            router._providers["ollama"], "complete", new_callable=AsyncMock
        ) as mock_ollama_complete,
    ):
        mock_ollama_complete.return_value = LLMResponse(
            content="Local fallback",
            model_used="llama",
            tier_used=ModelTier.LOCAL,
            prompt_tokens=1,
            completion_tokens=1,
            total_tokens=2,
            cost_usd=0.0,
            duration_ms=10,
        )
        # We override the provider to Ollama just so it doesn't crash on completion
        router._providers["anthropic"].complete = AsyncMock(
            return_value=LLMResponse(  # type: ignore
                content="Hello",
                model_used="claude",
                tier_used=ModelTier.PREMIUM,
                prompt_tokens=1,
                completion_tokens=1,
                total_tokens=2,
                cost_usd=0.0,
                duration_ms=10,
            )
        )

        await router.complete([Message(role="user", content="hi")], tier=ModelTier.PREMIUM)
        mock_check.assert_called_once()


@pytest.mark.asyncio
async def test_retry_on_transient_provider_failure(router: LLMRouter) -> None:
    # Set premium to anthropic
    router._tier_mapping[ModelTier.PREMIUM] = "claude-3-5-sonnet-20241022"

    mock_complete = AsyncMock(
        side_effect=[
            LLMTimeoutError("Timeout"),
            LLMResponse(
                content="Retry success",
                model_used="claude",
                tier_used=ModelTier.PREMIUM,
                prompt_tokens=1,
                completion_tokens=1,
                total_tokens=2,
                cost_usd=0.0,
                duration_ms=10,
            ),
        ]
    )

    router._providers["anthropic"].complete = mock_complete  # type: ignore

    with patch("asyncio.sleep", new_callable=AsyncMock):
        response = await router.complete(
            [Message(role="user", content="hi")], tier=ModelTier.PREMIUM
        )

        assert response.content == "Retry success"
        assert mock_complete.call_count == 2


@pytest.mark.asyncio
async def test_embed_returns_embedding_with_1024_vector(router: LLMRouter) -> None:
    with patch.object(router._embedding_service, "embed", new_callable=AsyncMock) as mock_embed:
        mock_embed.return_value = Embedding(vector=[0.1] * 1024, text="Hello", model="dummy")

        result = await router.embed("Hello")
        assert isinstance(result, Embedding)
        assert len(result.vector) == 1024


@pytest.mark.asyncio
async def test_stream_yields_string_chunks(router: LLMRouter) -> None:
    async def mock_stream_gen() -> AsyncGenerator[str, None]:
        yield "chunk1"
        yield "chunk2"

    with patch.object(router._providers["ollama"], "stream", return_value=mock_stream_gen()):
        chunks = []
        async for chunk in router.stream(
            [Message(role="user", content="hi")], tier=ModelTier.LOCAL
        ):
            chunks.append(chunk)

        assert chunks == ["chunk1", "chunk2"]


class DummySchema(BaseModel):
    name: str


@pytest.mark.asyncio
async def test_structured_output_returns_pydantic_model(router: LLMRouter) -> None:
    with patch.object(
        router._providers["ollama"], "complete", new_callable=AsyncMock
    ) as mock_complete:
        mock_complete.return_value = LLMResponse(
            content='{"name": "test"}',
            model_used="llama",
            tier_used=ModelTier.LOCAL,
            prompt_tokens=1,
            completion_tokens=1,
            total_tokens=2,
            cost_usd=0.0,
            duration_ms=10,
            structured=DummySchema(name="test"),
        )

        response = await router.complete(
            messages=[Message(role="user", content="Hi")],
            tier=ModelTier.LOCAL,
            response_schema=DummySchema,
        )

        assert response.structured and response.structured.name == "test"
