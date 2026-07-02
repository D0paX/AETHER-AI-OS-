from datetime import datetime
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict

from aether.llm._models import Message
from aether.memory.models import ContextPackage
from aether.tasks.models import Task


class SessionMode(StrEnum):
    VOICE = "voice"
    TEXT = "text"
    TASK = "task"


class Session(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: str  # UUIDv7
    started_at: datetime
    mode: SessionMode
    status: Literal["active", "consolidating", "ended"]
    message_count: int = 0


class SessionContext(BaseModel):
    model_config = ConfigDict(frozen=True)

    session_id: str
    messages: list[Message]
    active_tasks: list[Task]
    memory_context: ContextPackage
    working_summary: str
    last_activity: datetime
