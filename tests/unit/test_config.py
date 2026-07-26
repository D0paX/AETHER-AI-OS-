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


# --- M2.1.10 Part 2: .env loading and the Porcupine wake-word key ---------


def test_dotenv_file_populates_porcupine_key(
    tmp_path: object, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A value in a .env file resolves to config.voice.porcupine_access_key.

    Proves the whole chain M1.2 originally left broken: env_file on the
    settings config PLUS dotenv_settings included in the source chain. The
    nested AETHER_VOICE__ prefix maps to VoiceConfig.
    """
    monkeypatch.delenv("AETHER_VOICE__PORCUPINE_ACCESS_KEY", raising=False)
    env_file = tmp_path / ".env"  # type: ignore[attr-defined]
    env_file.write_text("AETHER_VOICE__PORCUPINE_ACCESS_KEY=test-value-12345\n", encoding="utf-8")
    config = AetherConfig(_env_file=str(env_file))
    assert config.voice.porcupine_access_key == "test-value-12345"


def test_porcupine_key_defaults_to_none(tmp_path: object) -> None:
    """With nothing configured, the key is None — never a silent fallback."""
    env_file = tmp_path / ".env"  # type: ignore[attr-defined]
    env_file.write_text("", encoding="utf-8")
    config = AetherConfig(_env_file=str(env_file))
    assert config.voice.porcupine_access_key is None


def test_real_env_var_takes_precedence_over_dotenv(
    tmp_path: object, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A real process env var outranks the .env file (standard precedence)."""
    monkeypatch.setenv("AETHER_VOICE__PORCUPINE_ACCESS_KEY", "from-real-env")
    env_file = tmp_path / ".env"  # type: ignore[attr-defined]
    env_file.write_text("AETHER_VOICE__PORCUPINE_ACCESS_KEY=from-dotenv\n", encoding="utf-8")
    config = AetherConfig(_env_file=str(env_file))
    assert config.voice.porcupine_access_key == "from-real-env"


def test_dotenv_addition_does_not_break_other_sections(
    tmp_path: object, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Regression: enabling .env loading leaves every other section intact.

    Adding env_file/dotenv_settings is additive — YAML defaults and the other
    config sections must still resolve exactly as before.
    """
    monkeypatch.delenv("AETHER_VOICE__PORCUPINE_ACCESS_KEY", raising=False)
    env_file = tmp_path / ".env"  # type: ignore[attr-defined]
    env_file.write_text("AETHER_VOICE__PORCUPINE_ACCESS_KEY=test-value-12345\n", encoding="utf-8")
    config = AetherConfig(_env_file=str(env_file))
    assert config.version == "1.0.0"
    assert config.environment in ("development", "production")
    assert config.memory is not None
    assert config.budget.daily_limit_usd == 2.00
    assert config.voice.enabled is True
    assert config.voice.porcupine_access_key == "test-value-12345"
