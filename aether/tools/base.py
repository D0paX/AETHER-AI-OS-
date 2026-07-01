from abc import ABC, abstractmethod
from typing import Any, ClassVar

from pydantic import BaseModel, ConfigDict, Field


class ToolResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    success: bool
    data: dict[str, Any] | None = None
    error: str | None = None
    error_code: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class ToolManifest(BaseModel):
    model_config = ConfigDict(frozen=True)

    name: str
    description: str
    required_permissions: list[str]


class BaseTool(ABC):
    """Abstract base class for all callable tools."""

    name: ClassVar[str]
    description: ClassVar[str]
    input_schema: ClassVar[type[BaseModel]]
    output_schema: ClassVar[type[BaseModel]]
    required_permissions: ClassVar[list[str]] = []

    @abstractmethod
    async def execute(self, input: BaseModel) -> ToolResult:  # noqa: A002
        """Execute the tool with the provided input."""
        pass

    def to_function_schema(self) -> dict[str, Any]:
        """Convert tool to Anthropic/OpenAI function calling schema."""
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self.input_schema.model_json_schema(),
        }

    async def check_permissions(self) -> bool:
        """Check if the agent has permission to execute this tool."""
        # Default: returns True (Phase 1 — PC control not yet implemented)
        # Phase 2 will override for PC control tools.
        return True
