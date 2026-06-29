"""Unit tests for the Aether OS configuration module."""

from collections.abc import Generator

import pytest

from aether.core import config as config_module
from aether.core.config import EMBEDDING_DIMENSION, AetherConfig, get_config


@pytest.fixture(autouse=True)
def reset_singleton() -> Generator[None, None, None]:
    """Reset the configuration singleton before and after each test."""
    config_module._config_instance = None
    yield
    config_module._config_instance = None


def test_config_loads_from_default_yaml() -> None:
    """Test that AetherConfig loads without error and has correct version."""
    config = AetherConfig()
    assert config.version == "1.0.0"


def test_env_var_overrides_yaml(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that environment variables override default configuration."""
    monkeypatch.setenv("AETHER_LLM__TIERS__LOCAL", "ollama/test-model")
    config = AetherConfig()
    assert config.llm.tiers.local == "ollama/test-model"


def test_missing_api_key_does_not_crash() -> None:
    """Test that AetherConfig loads even when API key env vars are not set."""
    # API keys are not required at config load time
    config = AetherConfig()
    assert config is not None


def test_get_config_returns_singleton() -> None:
    """Test that get_config returns the exact same instance on multiple calls."""
    config1 = get_config()
    config2 = get_config()
    assert config1 is config2


def test_all_sections_present() -> None:
    """Test that all required configuration sections are present."""
    config = get_config()
    assert config.llm is not None
    assert config.memory is not None
    assert config.voice is not None
    assert config.budget is not None
    assert config.redis is not None
    assert config.qdrant is not None
    assert config.database is not None
    assert config.logging is not None
    assert config.task is not None
    assert config.tool is not None
    assert config.permissions is not None


def test_embedding_dimension_constant() -> None:
    """Test that the embedding dimension is strictly 1024."""
    assert EMBEDDING_DIMENSION == 1024


def test_budget_defaults() -> None:
    """Test that the budget configuration has the correct default limits."""
    config = get_config()
    assert config.budget.daily_limit_usd == 2.00
    assert config.budget.monthly_limit_usd == 30.00
