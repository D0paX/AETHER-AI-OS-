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


class VoiceConfig(BaseModel):
    """Configuration for the speech-to-text and text-to-speech pipelines."""

    enabled: bool = True


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


class QdrantConfig(BaseModel):
    """Configuration for the Qdrant vector database."""

    host: str = "127.0.0.1"
    port: int = 6333
    grpc_port: int = 6334


class DatabaseConfig(BaseModel):
    """Configuration for the SQLite relational database."""

    url: str = "sqlite+aiosqlite:///aether.db"


class PermissionsConfig(BaseModel):
    """Configuration for agent permissions."""

    allow_shell: bool = False


class AetherConfig(BaseSettings):
    """Global configuration object for Aether OS."""

    model_config = SettingsConfigDict(
        env_prefix="AETHER_",
        env_nested_delimiter="__",
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
        """Configure settings sources to include YAML parsing."""
        return (
            init_settings,
            env_settings,
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
