import json
from datetime import UTC, datetime
from enum import Enum
from typing import Any

import uuid_utils
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from aether.core.events import EventBus
from aether.core.exceptions import AgentError
from aether.memory.models import TaskModel

from .models import Task, TaskFilter, TaskPriority, TaskStatus


class TaskManager:
    """Manages the creation, state transitions, and retrieval of tracking tasks."""

    _VALID_TRANSITIONS = {
        TaskStatus.PENDING: {TaskStatus.ACTIVE, TaskStatus.CANCELLED},
        TaskStatus.ACTIVE: {TaskStatus.COMPLETED, TaskStatus.CANCELLED, TaskStatus.FAILED},
        TaskStatus.COMPLETED: set(),
        TaskStatus.CANCELLED: set(),
        TaskStatus.FAILED: set(),
    }

    def __init__(self, session_factory: async_sessionmaker[AsyncSession], event_bus: EventBus):
        self._session_factory = session_factory
        self._event_bus = event_bus

    def _now_iso(self) -> str:
        return datetime.now(UTC).isoformat()

    def _to_pydantic(self, row: TaskModel) -> Task:
        return Task(
            id=str(row.id),
            title=str(row.title),
            description=str(row.description) if row.description else None,
            status=TaskStatus(str(row.status).upper()),
            priority=TaskPriority(str(row.priority).upper()),
            category=str(row.category) if row.category else None,
            due_at=datetime.fromisoformat(str(row.due_at)) if row.due_at else None,
            created_at=datetime.fromisoformat(str(row.created_at))
            if row.created_at
            else datetime.now(UTC),
            updated_at=datetime.fromisoformat(str(row.updated_at))
            if row.updated_at
            else datetime.now(UTC),
            completed_at=datetime.fromisoformat(str(row.completed_at))
            if row.completed_at
            else None,
            parent_task_id=str(row.parent_task_id) if row.parent_task_id else None,
            agent_type=str(row.agent_type) if row.agent_type else None,
            meta=json.loads(str(row.meta)) if row.meta else {},
        )

    async def create(
        self,
        title: str,
        description: str | None = None,
        priority: TaskPriority = TaskPriority.MEDIUM,
        due_at: datetime | None = None,
        category: str | None = None,
        parent_task_id: str | None = None,
    ) -> Task:
        task_id = str(uuid_utils.uuid7())
        now = self._now_iso()

        due_at_str = due_at.isoformat() if due_at else None

        task_model = TaskModel(
            id=task_id,
            title=title,
            description=description,
            status=TaskStatus.PENDING.value.lower(),
            priority=priority.value.lower(),
            category=category,
            due_at=due_at_str,
            created_at=now,
            updated_at=now,
            completed_at=None,
            parent_task_id=parent_task_id,
            agent_type=None,
            meta="{}",
        )

        async with self._session_factory() as session:
            session.add(task_model)
            await session.commit()

            pydantic_task = self._to_pydantic(task_model)

        if self._event_bus:
            await self._event_bus.emit(
                "task.lifecycle.created", {"task_id": task_id, "title": title}
            )

        return pydantic_task

    async def get(self, task_id: str) -> Task:
        async with self._session_factory() as session:
            result = await session.execute(select(TaskModel).where(TaskModel.id == task_id))
            row = result.scalars().first()
            if not row:
                raise AgentError(f"Task not found: {task_id}")
            return self._to_pydantic(row)

    async def list(self, task_filter: TaskFilter | None = None, limit: int = 50) -> list[Task]:
        task_filter = task_filter or TaskFilter()
        stmt = select(TaskModel)

        if task_filter.status:
            stmt = stmt.where(TaskModel.status == task_filter.status.value.lower())
        if task_filter.priority:
            stmt = stmt.where(TaskModel.priority == task_filter.priority.value.lower())
        if task_filter.category:
            stmt = stmt.where(TaskModel.category == task_filter.category)

        stmt = stmt.limit(limit)

        async with self._session_factory() as session:
            result = await session.execute(stmt)
            rows = result.scalars().all()
            return [self._to_pydantic(row) for row in rows]

    async def update_status(
        self, task_id: str, new_status: TaskStatus, note: str | None = None
    ) -> Task:
        async with self._session_factory() as session:
            result = await session.execute(select(TaskModel).where(TaskModel.id == task_id))
            row = result.scalars().first()
            if not row:
                raise AgentError(f"Task not found: {task_id}")

            current_status = TaskStatus(row.status.upper())

            if new_status not in self._VALID_TRANSITIONS[current_status]:
                raise AgentError(
                    f"Invalid transition from {current_status.value} to {new_status.value}"
                )

            row.status = new_status.value.lower()  # type: ignore
            now = self._now_iso()
            row.updated_at = now  # type: ignore

            if new_status == TaskStatus.COMPLETED:
                row.completed_at = now  # type: ignore

            if note:
                meta = json.loads(str(row.meta)) if row.meta else {}
                meta["status_note"] = note
                row.meta = json.dumps(meta)  # type: ignore

            await session.commit()
            await session.refresh(row)
            pydantic_task = self._to_pydantic(row)

        # Emit task created event
        if self._event_bus:
            await self._event_bus.emit(
                "task.lifecycle.status_changed",
                {
                    "task_id": task_id,
                    "old_status": current_status.value,
                    "new_status": new_status.value,
                },
            )
        return pydantic_task

    async def update(self, task_id: str, **updates: Any) -> Task:
        async with self._session_factory() as session:
            result = await session.execute(select(TaskModel).where(TaskModel.id == task_id))
            row = result.scalars().first()
            if not row:
                raise AgentError(f"Task not found: {task_id}")

            for key, value in updates.items():
                if hasattr(row, key):
                    if isinstance(value, Enum):
                        setattr(row, key, value.value.lower())
                    elif isinstance(value, datetime):
                        setattr(row, key, value.isoformat())
                    else:
                        setattr(row, key, value)

            row.updated_at = self._now_iso()
            await session.commit()
            await session.refresh(row)
            pydantic_task = self._to_pydantic(row)

        if self._event_bus:
            await self._event_bus.emit(
                "task.lifecycle.updated", {"task_id": task_id, "updates": list(updates.keys())}
            )
        return pydantic_task

    async def delete(self, task_id: str) -> bool:
        async with self._session_factory() as session:
            result = await session.execute(delete(TaskModel).where(TaskModel.id == task_id))
            await session.commit()

            success = getattr(result, "rowcount", 0) > 0

        if success and self._event_bus:
            await self._event_bus.emit("task.lifecycle.deleted", {"task_id": task_id})
        return bool(success)

    async def get_active_summary(self) -> str:
        # PENDING and ACTIVE tasks
        stmt = select(TaskModel).where(TaskModel.status.in_(["pending", "active"]))

        async with self._session_factory() as session:
            result = await session.execute(stmt)
            rows = result.scalars().all()

        if not rows:
            return "0 active tasks."

        summary_lines = []
        for row in rows:
            priority = row.priority.upper()
            summary_lines.append(f"[{priority}] {row.title}")

        return f"{len(rows)} active tasks: " + ", ".join(summary_lines)
