from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict


class TaskStatus(StrEnum):
    PENDING = "PENDING"
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    FAILED = "FAILED"


class TaskPriority(StrEnum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class Task(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: str
    title: str
    description: str | None
    status: TaskStatus
    priority: TaskPriority
    category: str | None
    due_at: datetime | None
    created_at: datetime
    updated_at: datetime
    completed_at: datetime | None
    parent_task_id: str | None
    agent_type: str | None
    meta: dict[str, Any]


class TaskFilter(BaseModel):
    status: TaskStatus | None = None
    priority: TaskPriority | None = None
    category: str | None = None
