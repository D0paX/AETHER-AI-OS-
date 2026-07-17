"""Aether text-based CLI interface (TEXT MILESTONE surface).

Contains zero business logic: every conversational turn flows through
SessionManager.build_agent_context() -> AgentRuntime.execute() ->
SessionManager.update_context(), and every command delegates to the
kernel's public components. Corrected in M2.1.6 — the previous version
constructed AgentTask/SessionContext with fields that do not exist on the
locked models and called a SessionManager method that was never implemented.
"""

import asyncio
import sys
from datetime import UTC, datetime

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from aether.agents.base import AgentTask
from aether.core.exceptions import AetherError, InfrastructureError
from aether.core.kernel import AetherKernel
from aether.llm import Message
from aether.session.manager import SessionManager
from aether.session.models import Session, SessionMode
from aether.tasks.manager import TaskManager
from aether.tasks.models import TaskFilter, TaskStatus

# Grace period after end_session() so the background consolidation task can
# begin before the process exits.
CONSOLIDATION_GRACE_SECONDS: float = 2.0

# Display order for task priorities in /tasks (lowest number renders first).
PRIORITY_DISPLAY_ORDER: dict[str, int] = {"critical": 0, "high": 1, "medium": 2, "low": 3}
UNKNOWN_PRIORITY_ORDER: int = 99

MEMORY_PREVIEW_LENGTH: int = 80
MEMORY_SEARCH_LIMIT: int = 5


class AetherCLI:
    """Terminal interface for interactive Aether sessions."""

    def __init__(self, kernel: AetherKernel):
        self.kernel = kernel
        self.console = Console()
        self.session: Session | None = None

    def _session_manager(self) -> SessionManager:
        if self.kernel.session_manager is None:
            raise InfrastructureError("Kernel not fully booted: SessionManager unavailable.")
        return self.kernel.session_manager

    def _task_manager(self) -> TaskManager:
        if self.kernel.task_manager is None:
            raise InfrastructureError("Kernel not fully booted: TaskManager unavailable.")
        return self.kernel.task_manager

    def _require_session(self) -> Session:
        if self.session is None:
            raise InfrastructureError("No active session.")
        return self.session

    async def run(self) -> None:
        """Start a session and enter the interactive conversation loop."""
        self.console.print(
            Panel("[bold magenta]Aether AI OS[/bold magenta] v1.0", border_style="magenta")
        )
        self.console.print("Starting session...")

        try:
            self.session = await self._session_manager().start_session(SessionMode.TEXT)

            briefing = await self._session_manager().get_morning_briefing(self.session.id)
            if briefing:
                self.console.print(Panel(briefing, title="Morning Briefing", border_style="yellow"))

            while True:
                user_input = await asyncio.get_running_loop().run_in_executor(
                    None, lambda: self.console.input("[bold cyan]Aether > [/bold cyan]")
                )

                user_input = user_input.strip()
                if not user_input:
                    continue

                if user_input.startswith("/"):
                    await self._handle_command(user_input)
                else:
                    await self._handle_conversation(user_input)

        except (KeyboardInterrupt, EOFError):
            await self._handle_quit()

    async def _handle_conversation(self, text: str) -> None:
        """Run one conversational turn through the shared context-assembly path."""
        try:
            session = self._require_session()
            context = await self._session_manager().build_agent_context(session.id, text)
            task = AgentTask(
                description="Conversational turn",
                goal="Respond to the user's message",
                input_data={"text": text},
            )
            if self.kernel.agent_runtime is None:
                raise InfrastructureError("Kernel not fully booted: AgentRuntime unavailable.")
            result = await self.kernel.agent_runtime.execute("conversation", task, context)

            if not result.success:
                self.console.print(
                    Panel(
                        result.error or "The agent could not complete this request.",
                        title="Aether (error)",
                        border_style="red",
                    )
                )
                return

            self.console.print(Panel(result.response, title="Aether", border_style="cyan"))

            # Exactly the new turn's two messages — never the accumulated
            # history (M2.1.5 delta contract).
            await self._session_manager().update_context(
                session.id,
                new_messages=[
                    Message(role="user", content=text),
                    Message(role="assistant", content=result.response),
                ],
            )
        except AetherError as e:
            self.console.print(Panel(str(e), title="Error", border_style="red"))

    async def _handle_command(self, cmd_string: str) -> None:
        parts = cmd_string.split(maxsplit=1)
        command = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""

        try:
            if command == "/tasks":
                await self._cmd_tasks()
            elif command == "/memory":
                await self._cmd_memory(args)
            elif command == "/status":
                await self._cmd_status()
            elif command == "/help":
                self._cmd_help()
            elif command == "/quit":
                await self._handle_quit()
            else:
                self.console.print(
                    f"[red]Unknown command:[/red] {command}. Type /help for a list of commands."
                )
        except AetherError as e:
            self.console.print(Panel(str(e), title="Error executing command", border_style="red"))

    async def _cmd_tasks(self) -> None:
        task_manager = self._task_manager()
        active = await task_manager.list(task_filter=TaskFilter(status=TaskStatus.ACTIVE))
        pending = await task_manager.list(task_filter=TaskFilter(status=TaskStatus.PENDING))
        all_tasks = active + pending

        all_tasks.sort(
            key=lambda t: PRIORITY_DISPLAY_ORDER.get(str(t.priority), UNKNOWN_PRIORITY_ORDER)
        )

        table = Table(title="Active Tasks")
        table.add_column("Priority", justify="left")
        table.add_column("Title", justify="left")
        table.add_column("Status", justify="left")
        table.add_column("Due Date", justify="left")

        for t in all_tasks:
            table.add_row(
                str(t.priority),
                t.title,
                str(t.status),
                str(t.due_at) if t.due_at else "None",
            )

        self.console.print(table)

    async def _cmd_memory(self, query: str) -> None:
        if not query:
            self.console.print("[red]Please provide a query: /memory <query>[/red]")
            return

        if self.kernel.memory_api is None:
            raise InfrastructureError("Kernel not fully booted: MemoryAPI unavailable.")
        results = await self.kernel.memory_api.search(query, limit=MEMORY_SEARCH_LIMIT)
        if not results:
            self.console.print("[yellow]No memories found.[/yellow]")
            return

        for m in results:
            content = m.content
            if len(content) > MEMORY_PREVIEW_LENGTH:
                content = content[:MEMORY_PREVIEW_LENGTH] + "..."
            self.console.print(
                f"[{m.memory_type.value}] {content} (importance: {m.importance:.2f})"
            )

    async def _cmd_status(self) -> None:
        session = self._require_session()

        duration_s = int((datetime.now(UTC) - session.started_at).total_seconds())
        duration_str = f"{duration_s // 60}m {duration_s % 60}s"

        context = await self._session_manager().get_context(session.id)

        self.console.print(f"Session ID: {session.id[:8]}")
        self.console.print(f"Duration: {duration_str}")
        self.console.print(f"Messages: {len(context.messages)}")

    def _cmd_help(self) -> None:
        table = Table(title="Available Commands")
        table.add_column("Command", style="cyan")
        table.add_column("Description")

        table.add_row("/tasks", "List active tasks")
        table.add_row("/memory <query>", "Show top 5 memories matching query")
        table.add_row("/status", "Display session status")
        table.add_row("/help", "Display this help message")
        table.add_row("/quit", "Save session and exit")

        self.console.print(table)

    async def _handle_quit(self) -> None:
        self.console.print("Ending session...")
        if self.session is not None:
            await self._session_manager().end_session(self.session.id, trigger="user")
            # end_session() schedules consolidation as a background task; give
            # it a moment to begin before the process exits.
            await asyncio.sleep(CONSOLIDATION_GRACE_SECONDS)

        self.console.print("Session saved. Goodbye.")
        sys.exit(0)
