import pytest
from pydantic import BaseModel, Field

from aether.core.exceptions import ToolError, ToolNotFoundError
from aether.tools.base import BaseTool, ToolResult
from aether.tools.registry import ToolRegistry


class DummyInput(BaseModel):
    query: str = Field(description="dummy input")


class DummyOutput(BaseModel):
    result: str


class DummyTool(BaseTool):
    name = "dummy_tool"
    description = "A dummy tool"
    input_schema = DummyInput
    output_schema = DummyOutput
    required_permissions = []

    async def execute(self, input: DummyInput) -> ToolResult:
        return ToolResult(success=True, data={"result": "ok"})


@pytest.fixture
def empty_registry():
    # Since it's a singleton, we need to clear it for clean testing
    registry = ToolRegistry.get_instance()
    registry._tools.clear()
    return registry


def test_register_and_retrieve_tool(empty_registry):
    tool = DummyTool()
    empty_registry.register(tool)

    assert empty_registry.is_registered("dummy_tool")
    retrieved = empty_registry.get("dummy_tool")
    assert retrieved is tool

    with pytest.raises(ToolError):
        empty_registry.register(DummyTool())


def test_get_nonexistent_raises_tool_not_found_error(empty_registry):
    with pytest.raises(ToolNotFoundError):
        empty_registry.get("nonexistent_tool")


def test_list_returns_all_registered_tools(empty_registry):
    tool = DummyTool()
    empty_registry.register(tool)

    manifests = empty_registry.list()
    assert len(manifests) == 1
    assert manifests[0].name == "dummy_tool"
    assert manifests[0].description == "A dummy tool"
    assert manifests[0].required_permissions == []


def test_get_function_schema_returns_valid_anthropic_format(empty_registry):
    tool = DummyTool()
    empty_registry.register(tool)

    schemas = empty_registry.get_function_schemas(["dummy_tool"])
    assert len(schemas) == 1
    schema = schemas[0]

    assert schema["name"] == "dummy_tool"
    assert schema["description"] == "A dummy tool"
    assert "input_schema" in schema
    assert schema["input_schema"]["type"] == "object"
    assert "query" in schema["input_schema"]["properties"]


def test_registry_is_singleton_across_imports():
    reg1 = ToolRegistry.get_instance()
    reg2 = ToolRegistry.get_instance()
    assert reg1 is reg2
