from datetime import datetime

from aether.memory.api import MemoryAPI
from aether.tasks.manager import TaskManager
from aether.tasks.models import Task, TaskFilter, TaskStatus

from .models import SessionContext


class SessionStartupBuilder:
    """Assembles the initial working context and morning briefing for a new session."""

    def __init__(self, memory_api: MemoryAPI, task_manager: TaskManager):
        self._memory_api = memory_api
        self._task_manager = task_manager

    async def build_context(self, session_id: str) -> SessionContext:
        """Assembles the initial context for a new session."""
        active_tasks = await self._task_manager.list(
            task_filter=TaskFilter(status=TaskStatus.ACTIVE), limit=10
        )

        recent_context = await self._memory_api.recall("recent projects tasks and goals", k=5)

        now = datetime.now()

        return SessionContext(
            session_id=session_id,
            messages=[],
            active_tasks=active_tasks,
            memory_context=recent_context,
            working_summary="Started a new session.",
            last_activity=now,
        )

    @staticmethod
    def _select_top_task(active_tasks: list[Task]) -> Task:
        """Return the highest-priority active task.

        Scans "high", then "medium", then "low", returning the first task
        matching each in turn; falls back to the first active task when none
        carries a recognized priority. Extracted from build_morning_briefing
        in M2.1.9 solely to satisfy C901 — the selection order and fallback
        are unchanged. Callers must pass a non-empty list.
        """
        for priority in ["high", "medium", "low"]:
            for task in active_tasks:
                if task.priority == priority:
                    return task
        return active_tasks[0]

    async def build_morning_briefing(self, context: SessionContext) -> str:
        """Generates a concise greeting and status briefing based on the session context."""
        now = datetime.now()
        hour = now.hour

        if 0 <= hour < 12:
            greeting = "Good morning"
        elif 12 <= hour < 18:
            greeting = "Good afternoon"
        else:
            greeting = "Good evening"

        task_count = len(context.active_tasks)
        if task_count == 0:
            tasks_part = "No active tasks."
            top_priority_task = ""
        else:
            tasks_part = f"{task_count} active task(s)."
            top_task = self._select_top_task(context.active_tasks)
            top_priority_task = f"Top priority: {top_task.title}."

        context_summary = "Ready to proceed."
        if context.memory_context.memories:
            # Grab a brief snippet from the most relevant memory
            context_summary = "Continuing previous work."

        # Assemble briefing
        parts = [p for p in [greeting + ".", tasks_part, top_priority_task, context_summary] if p]
        briefing = " ".join(parts)

        # Enforce < 50 words rule
        words = briefing.split()
        if len(words) > 50:
            briefing = " ".join(words[:50]) + "..."

        assert len(briefing.split()) <= 50

        return briefing
