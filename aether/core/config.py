"""Aether OS Configuration Module.

This module provides the single source of truth for all configuration in Aether.
It reads from YAML files and environment variables, providing a typed, validated
settings singleton.
"""

import threading
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field, ValidationError
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    YamlConfigSettingsSource,
)

from aether.core.exceptions import ConfigurationError

# PERMANENT CONSTANT — never change after first run
EMBEDDING_DIMENSION: int = 1024


class ModelTierConfig(BaseModel):
    """Configuration for LLM model tiers."""

    local: str = "llama3.2:3b"
    fast: str | None = None
    smart: str | None = None


class LLMConfig(BaseModel):
    """Configuration for the LLM router and providers."""

    tiers: ModelTierConfig = Field(default_factory=ModelTierConfig)


class BudgetConfig(BaseModel):
    """Configuration for financial budgets on paid LLMs."""

    daily_limit_usd: float = 2.00
    monthly_limit_usd: float = 30.00


class MemoryConfig(BaseModel):
    """Configuration for the vector and episodic memory systems."""

    enabled: bool = True
    embedding_model: str = "all-MiniLM-L6-v2"
    embedding_device: str = "cpu"
    # Minimum messages a conversation needs before end-of-session consolidation
    # runs (V1_TECHNICAL_SPECIFICATION.md Section 2.1; value set in default.yaml).
    # M2.1.8: lowered 5 -> 3 so ordinary short exchanges still consolidate. Kept
    # in sync with default.yaml so the two never drift (unlike the original
    # 5-vs-10 mismatch fixed in M2.1.5).
    consolidation_min_messages: int = 3


class VoiceConfig(BaseModel):
    """Configuration for the speech-to-text and text-to-speech pipelines."""

    enabled: bool = True
    # Picovoice Porcupine wake-word access key. Sourced from
    # AETHER_VOICE__PORCUPINE_ACCESS_KEY (env or .env). None when unset; the
    # voice service validates it at startup and refuses to run the wake word on
    # a missing or placeholder value (M2.1.10 Part 2 / DEBT-018, D-002).
    porcupine_access_key: str | None = None


class TaskConfig(BaseModel):
    """Configuration for agent task execution."""

    max_retries: int = 3


class ToolConfig(BaseModel):
    """Configuration for tool execution."""

    enabled: bool = True


class LoggingConfig(BaseModel):
    """Configuration for structured logging."""

    file_path: Path = Path("logs/aether.log")
    max_file_mb: int = 10
    backup_count: int = 5


class RedisConfig(BaseModel):
    """Configuration for the Redis event bus and cache."""

    url: str = "redis://127.0.0.1:6379/0"
    # Dedicated test Redis logical database (M2.1.7 Part 2). Must use a
    # non-zero DB index (production uses index 0). The test-safety guard
    # refuses to run the suite unless the active Redis DB index is non-zero.
    test_url: str = "redis://127.0.0.1:6379/1"


class QdrantConfig(BaseModel):
    """Configuration for the Qdrant vector database."""

    host: str = "127.0.0.1"
    port: int = 6333
    grpc_port: int = 6334
    # Vector collection name. Configurable (M2.1.7 Part 2) so the test suite
    # can be redirected to a disposable test collection instead of writing
    # vectors into the production collection.
    collection: str = "episodic_memory"
    # Dedicated test collection — a DIFFERENT collection from `collection`.
    # The test-safety guard refuses to run unless the active collection is a
    # clearly test-marked name (never the production "episodic_memory").
    test_collection: str = "episodic_memory_test"


class DatabaseConfig(BaseModel):
    """Configuration for the relational database (SQLite in dev, PostgreSQL from M2.1)."""

    url: str = "sqlite+aiosqlite:///aether.db"
    # Dedicated, disposable test database — a DIFFERENT logical database from
    # `url`, used only by the test suite (M2.1.7). Set in config/local.yaml.
    # The test-safety guard refuses to run the suite unless the active URL
    # resolves to a clearly test-marked database.
    test_url: str = ""


class PermissionsConfig(BaseModel):
    """Configuration for agent permissions."""

    allow_shell: bool = False


class AetherConfig(BaseSettings):
    """Global configuration object for Aether OS."""

    model_config = SettingsConfigDict(
        env_prefix="AETHER_",
        env_nested_delimiter="__",
        # M2.1.10 Part 2: load .env from disk. This was omitted from Milestone
        # M1.2's original config.py (a specification gap, not a regression) — so
        # values documented in .env / .env.example (e.g.
        # AETHER_VOICE__PORCUPINE_ACCESS_KEY) never reached settings resolution,
        # only real process environment variables did. See also the dotenv
        # source added to settings_customise_sources below, which the same gap
        # had left out of the source chain.
        env_file=".env",
        env_file_encoding="utf-8",
        yaml_file=["config/default.yaml", "config/local.yaml"],
        yaml_file_encoding="utf-8",
        extra="ignore",
    )

    version: str = "1.0.0"
    environment: Literal["development", "production"] = "development"
    data_dir: Path = Path("data")
    log_dir: Path = Path("logs")
    backup_dir: Path = Path("backups")

    llm: LLMConfig = Field(default_factory=LLMConfig)
    budget: BudgetConfig = Field(default_factory=BudgetConfig)
    memory: MemoryConfig = Field(default_factory=MemoryConfig)
    voice: VoiceConfig = Field(default_factory=VoiceConfig)
    task: TaskConfig = Field(default_factory=TaskConfig)
    tool: ToolConfig = Field(default_factory=ToolConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    redis: RedisConfig = Field(default_factory=RedisConfig)
    qdrant: QdrantConfig = Field(default_factory=QdrantConfig)
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    permissions: PermissionsConfig = Field(default_factory=PermissionsConfig)

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        """Configure settings sources to include YAML parsing.

        Precedence (highest first): explicit init args, then real process
        environment variables, then the .env file, then YAML defaults, then
        file secrets. dotenv_settings must be listed explicitly: overriding
        this method replaces pydantic-settings' default chain entirely, and the
        original M1.2 implementation dropped it — so even with env_file set, the
        .env file was never actually consulted (M2.1.10 Part 2).
        """
        return (
            init_settings,
            env_settings,
            dotenv_settings,
            YamlConfigSettingsSource(settings_cls),
            file_secret_settings,
        )


_config_instance: AetherConfig | None = None
_config_lock = threading.Lock()


def get_config() -> AetherConfig:
    """Retrieve the global configuration singleton.

    Returns:
        AetherConfig: The validated configuration object.

    Raises:
        ConfigurationError: If the configuration is missing required fields or is invalid.
    """
    global _config_instance
    if _config_instance is None:
        with _config_lock:
            if _config_instance is None:
                try:
                    _config_instance = AetherConfig()
                except ValidationError as e:
                    raise ConfigurationError(f"Invalid or missing configuration: {e}") from e
    return _config_instance
