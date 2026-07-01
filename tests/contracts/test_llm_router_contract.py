"""Contract tests verifying the strict structure of the LLM Abstraction Layer."""

import inspect

import pytest

from aether.llm._models import Embedding, LLMResponse, ModelTier
from aether.llm.router import LLMRouter


def test_router_has_complete_method_with_correct_signature() -> None:
    sig = inspect.signature(LLMRouter.complete)
    assert "messages" in sig.parameters
    assert "tier" in sig.parameters
    assert "response_schema" in sig.parameters
    assert "max_tokens" in sig.parameters
    assert "temperature" in sig.parameters

    assert sig.return_annotation == LLMResponse


def test_router_has_stream_method() -> None:
    sig = inspect.signature(LLMRouter.stream)
    assert "messages" in sig.parameters
    assert "tier" in sig.parameters
    assert "max_tokens" in sig.parameters

    assert "AsyncIterator" in str(sig.return_annotation)


def test_router_has_embed_method() -> None:
    sig = inspect.signature(LLMRouter.embed)
    assert "text" in sig.parameters
    assert "batch" in sig.parameters
    assert sig.return_annotation == Embedding | list[Embedding]


def test_model_tier_has_four_values() -> None:
    tiers = [t.value for t in ModelTier]
    assert len(tiers) == 4
    assert "local" in tiers
    assert "cheap" in tiers
    assert "standard" in tiers
    assert "premium" in tiers


def test_embedding_vector_always_1024_dimension() -> None:
    with pytest.raises(ValueError, match="Vector dimension must be 1024"):
        Embedding(vector=[0.1] * 1023, text="Test", model="dummy")

    # Should pass
    emb = Embedding(vector=[0.1] * 1024, text="Test", model="dummy")
    assert len(emb.vector) == 1024


def test_llm_response_has_all_required_fields() -> None:
    fields = LLMResponse.model_fields.keys()
    assert "content" in fields
    assert "model_used" in fields
    assert "tier_used" in fields
    assert "prompt_tokens" in fields
    assert "completion_tokens" in fields
    assert "total_tokens" in fields
    assert "cost_usd" in fields
    assert "duration_ms" in fields
    assert "cached" in fields
    assert "structured" in fields
