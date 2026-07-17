"""Data models for the LLM abstraction layer."""

from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, model_validator

from aether.core.config import EMBEDDING_DIMENSION


class ModelTier(str, Enum):  # noqa: UP042
    """The locked set of model tiers used for routing.

    UP042 (convert to StrEnum) is deliberately suppressed: StrEnum changes
    `str()`/f-string rendering from "ModelTier.LOCAL" to "local", which is an
    observable behavior change across logging and display, and this is a
    locked contract (V1_TECHNICAL_SPECIFICATION.md Section 2.4). M2.1.9 is a
    lint/type pass that must change no behavior.
    """

    LOCAL = "local"
    CHEAP = "cheap"
    STANDARD = "standard"
    PREMIUM = "premium"


class Message(BaseModel):
    """A standard chat message format used across all providers."""

    model_config = ConfigDict(frozen=True)

    role: Literal["system", "user", "assistant", "tool"]
    content: str
    tool_call_id: str | None = None
    name: str | None = None


class LLMResponse(BaseModel):
    """The unified LLM response format returned to agents."""

    model_config = ConfigDict(frozen=True)

    content: str
    model_used: str
    tier_used: ModelTier
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    cost_usd: float
    duration_ms: int
    cached: bool = False
    structured: Any | None = None


class Embedding(BaseModel):
    """A high-dimensional vector embedding for text."""

    model_config = ConfigDict(frozen=True)

    vector: list[float]
    text: str
    model: str

    @model_validator(mode="after")
    def validate_dimension(self) -> "Embedding":
        """Ensure the vector matches the locked embedding dimension."""
        if len(self.vector) != EMBEDDING_DIMENSION:
            raise ValueError(
                f"Vector dimension must be {EMBEDDING_DIMENSION}, got {len(self.vector)}"
            )
        return self


class BudgetStatus(BaseModel):
    """Current snapshot of the LLM financial budget."""

    model_config = ConfigDict(frozen=True)

    daily_spent_usd: float
    daily_limit_usd: float
    daily_percent: float
    monthly_spent_usd: float
    monthly_limit_usd: float
    monthly_percent: float
    active_tier_override: ModelTier | None = None
