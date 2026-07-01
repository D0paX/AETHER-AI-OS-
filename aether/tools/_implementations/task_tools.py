from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from aether.tasks.manager import TaskManager
from aether.tasks.models import TaskFilter, TaskPriority, TaskStatus

from ..base import BaseTool, ToolResult


class CreateTaskTool(BaseTool):
    name = "create_task"
    description = "Creates a new task to track work items."

    class Input(BaseModel):
        title: str = Field(description="The title of the task")
        description: str | None = Field(
            default=None, description="Detailed description of the task"
        )
        priority: str = Field(default="medium", description="Priority: low, medium, high, critical")
        due_date: str | None = Field(default=None, description="ISO 8601 formatted due date")

    class Output(BaseModel):
        model_config = ConfigDict(frozen=True)
        task_id: str
        title: str
        status: str
        priority: str

    input_schema = Input
    output_schema = Output
    required_permissions = []

    def __init__(self, task_manager: TaskManager):
        self.task_manager = task_manager

    async def execute(self, input: BaseModel) -> ToolResult:  # noqa: A002
        if not isinstance(input, self.Input):
            raise TypeError("Invalid input type")
        try:
            priority_enum = TaskPriority(input.priority.upper())

            due_at = None
            if input.due_date:
                try:
                    due_at = datetime.fromisoformat(input.due_date)
                except ValueError:
                    return ToolResult(
                        success=False, error="Invalid due_date format. Must be ISO 8601."
                    )

            task = await self.task_manager.create(
                title=input.title,
                description=input.description,
                priority=priority_enum,
                due_at=due_at,
            )

            output = self.Output(
                task_id=task.id,
                title=task.title,
                status=task.status.value,
                priority=task.priority.value,
            )

            return ToolResult(success=True, data=output.model_dump())
        except Exception as e:
            return ToolResult(success=False, error=str(e))


class ListTasksTool(BaseTool):
    name = "list_tasks"
    description = "Lists tasks filtered by status and/or priority."

    class Input(BaseModel):
        status: str | None = Field(
            default=None,
            description="Filter by status: pending, active, completed, cancelled, failed",
        )
        priority: str | None = Field(
            default=None, description="Filter by priority: low, medium, high, critical"
        )
        limit: int = Field(default=10, description="Maximum number of tasks to return")

    class Output(BaseModel):
        model_config = ConfigDict(frozen=True)
        tasks: list[dict[str, str]]

    input_schema = Input
    output_schema = Output
    required_permissions = []

    def __init__(self, task_manager: TaskManager):
        self.task_manager = task_manager

    async def execute(self, input: BaseModel) -> ToolResult:  # noqa: A002
        if not isinstance(input, self.Input):
            raise TypeError("Invalid input type")
        try:
            filter_status = TaskStatus(input.status.upper()) if input.status else None
            filter_priority = TaskPriority(input.priority.upper()) if input.priority else None

            task_filter = TaskFilter(status=filter_status, priority=filter_priority)

            tasks = await self.task_manager.list(task_filter=task_filter, limit=input.limit)

            formatted_tasks = []
            for t in tasks:
                formatted_tasks.append(
                    {
                        "id": t.id,
                        "title": t.title,
                        "status": t.status.value,
                        "priority": t.priority.value,
                    }
                )

            return ToolResult(success=True, data=self.Output(tasks=formatted_tasks).model_dump())
        except ValueError as ve:
            return ToolResult(success=False, error=f"Invalid filter value: {str(ve)}")
        except Exception as e:
            return ToolResult(success=False, error=str(e))


class UpdateTaskStatusTool(BaseTool):
    name = "update_task_status"
    description = "Updates the status of an existing task."

    class Input(BaseModel):
        task_id: str = Field(description="The ID of the task to update")
        status: str = Field(
            description="The new status: pending, active, completed, cancelled, failed"
        )
        note: str | None = Field(default=None, description="Optional note about the status change")

    class Output(BaseModel):
        model_config = ConfigDict(frozen=True)
        task_id: str
        status: str

    input_schema = Input
    output_schema = Output
    required_permissions = []

    def __init__(self, task_manager: TaskManager):
        self.task_manager = task_manager

    async def execute(self, input: BaseModel) -> ToolResult:  # noqa: A002
        if not isinstance(input, self.Input):
            raise TypeError("Invalid input type")
        if not input.task_id or not input.task_id.strip():
            return ToolResult(success=False, error="task_id cannot be empty")

        try:
            new_status_enum = TaskStatus(input.status.upper())

            task = await self.task_manager.update_status(
                task_id=input.task_id, new_status=new_status_enum, note=input.note
            )

            output = self.Output(task_id=task.id, status=task.status.value)

            return ToolResult(success=True, data=output.model_dump())
        except ValueError:
            return ToolResult(success=False, error=f"Invalid status: {input.status}")
        except Exception as e:
            return ToolResult(success=False, error=str(e))
