import builtins
import threading
from typing import Any, ClassVar

from aether.core.exceptions import ToolError, ToolNotFoundError

from .base import BaseTool, ToolManifest


class ToolRegistry:
    """Thread-safe singleton registry for managing agent tools."""

    _instance: ClassVar["ToolRegistry | None"] = None
    _lock: ClassVar[threading.Lock] = threading.Lock()

    def __init__(self) -> None:
        self._tools: dict[str, BaseTool] = {}

    @classmethod
    def get_instance(cls) -> "ToolRegistry":
        with cls._lock:
            if cls._instance is None:
                cls._instance = cls()
            return cls._instance

    def register(self, tool: BaseTool) -> None:
        """Register a tool. Raises ToolError if a tool with the same name exists."""
        with self._lock:
            if tool.name in self._tools:
                raise ToolError(f"Tool '{tool.name}' is already registered.")
            self._tools[tool.name] = tool

    def get(self, name: str) -> BaseTool:
        """Retrieve a tool by name. Raises ToolNotFoundError if not found."""
        with self._lock:
            tool = self._tools.get(name)
            if tool is None:
                raise ToolNotFoundError(f"Tool '{name}' not found.")
            return tool

    def list(self) -> list[ToolManifest]:  # noqa: A003
        """Return a list of all registered tools as ToolManifest objects."""
        with self._lock:
            return [
                ToolManifest(
                    name=tool.name,
                    description=tool.description,
                    required_permissions=tool.required_permissions,
                )
                for tool in self._tools.values()
            ]

    def get_function_schemas(self, tool_names: builtins.list[str]) -> builtins.list[dict[str, Any]]:  # noqa: A003
        """Return Anthropic function calling schemas for specified tools."""
        schemas = []
        with self._lock:
            for name in tool_names:
                tool = self._tools.get(name)
                if tool is None:
                    raise ToolNotFoundError(f"Tool '{name}' not found.")
                schemas.append(tool.to_function_schema())
        return schemas

    def is_registered(self, name: str) -> bool:
        """Check if a tool is registered."""
        with self._lock:
            return name in self._tools
