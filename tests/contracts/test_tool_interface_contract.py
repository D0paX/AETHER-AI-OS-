from aether.tools._implementations.datetime_tools import GetCurrentDatetimeTool
from aether.tools._implementations.search_tools import WebSearchTool
from aether.tools._implementations.task_tools import (
    CreateTaskTool,
    ListTasksTool,
    UpdateTaskStatusTool,
)
from aether.tools.base import BaseTool, ToolResult


def test_base_tool_has_execute_abstract_method():
    assert hasattr(BaseTool, "execute")
    assert getattr(BaseTool.execute, "__isabstractmethod__", False)


def test_base_tool_has_to_function_schema():
    assert hasattr(BaseTool, "to_function_schema")
    assert callable(BaseTool.to_function_schema)


def test_tool_result_is_frozen():
    # Pydantic v2: check model_config
    assert getattr(ToolResult, "model_config", {}).get("frozen") is True


def test_tool_result_has_success_field():
    fields = ToolResult.model_fields
    assert "success" in fields
    assert fields["success"].annotation is bool


def test_all_builtin_tools_have_name_classvar():
    builtin_tools = [
        GetCurrentDatetimeTool,
        WebSearchTool,
        CreateTaskTool,
        ListTasksTool,
        UpdateTaskStatusTool,
    ]
    for tool_class in builtin_tools:
        assert hasattr(tool_class, "name")
        assert isinstance(tool_class.name, str)


def test_all_builtin_tools_have_description_classvar():
    builtin_tools = [
        GetCurrentDatetimeTool,
        WebSearchTool,
        CreateTaskTool,
        ListTasksTool,
        UpdateTaskStatusTool,
    ]
    for tool_class in builtin_tools:
        assert hasattr(tool_class, "description")
        assert isinstance(tool_class.description, str)
