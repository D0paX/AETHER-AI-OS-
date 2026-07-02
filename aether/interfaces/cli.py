import sys
import asyncio
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
import time

from aether.core.kernel import AetherKernel
from aether.session.models import SessionMode
from aether.agents.base import AgentTask

class AetherCLI:
    def __init__(self, kernel: AetherKernel):
        self.kernel = kernel
        self.console = Console()
        self.session_context = None

    async def run(self) -> None:
        self.console.print(Panel("[bold magenta]Aether AI OS[/bold magenta] v1.0", border_style="magenta"))
        self.console.print("Starting session...")
        
        try:
            self.session_context = await self.kernel.session_manager.start_session(SessionMode.TEXT)
            
            # Print morning briefing
            briefing = self.session_context.package().morning_briefing
            if briefing:
                self.console.print(Panel(briefing, title="Morning Briefing", border_style="yellow"))
            
            while True:
                # Use loop.run_in_executor to avoid completely blocking the async event loop, 
                # although console.input blocks the thread.
                # Actually, Rich's console.input can be run directly if we don't mind blocking background tasks,
                # but to be safe and responsive, we can run it in executor.
                user_input = await asyncio.get_running_loop().run_in_executor(
                    None, 
                    lambda: self.console.input("[bold cyan]Aether > [/bold cyan]")
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
        try:
            task = AgentTask(instruction=text)
            context = self.session_context.package()
            
            # The user's message is added to the session context transcript 
            self.session_context.transcript.append({"role": "user", "content": text})
            
            result = await self.kernel.agent_runtime.execute("conversation", task, context)
            
            self.console.print(Panel(result.output, title="Aether", border_style="cyan"))
            
            # Update session context transcript with agent response
            self.session_context.transcript.append({"role": "assistant", "content": result.output})
            
            # Sync to Redis
            await self.kernel.session_manager._cache_session(self.session_context)
            
        except Exception as e:
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
                self.console.print(f"[red]Unknown command:[/red] {command}. Type /help for a list of commands.")
        except Exception as e:
            self.console.print(Panel(str(e), title="Error executing command", border_style="red"))

    async def _cmd_tasks(self) -> None:
        # Pull latest tasks from kernel
        tasks = await self.kernel.task_manager.list_tasks(status="ACTIVE")
        pending = await self.kernel.task_manager.list_tasks(status="PENDING")
        all_tasks = tasks + pending
        
        # Sort by priority (CRITICAL first, etc). Assume HIGH/NORMAL/LOW strings.
        priority_map = {"CRITICAL": 0, "HIGH": 1, "NORMAL": 2, "LOW": 3}
        all_tasks.sort(key=lambda t: priority_map.get(t.priority.upper(), 99) if hasattr(t, 'priority') else 99)
        
        table = Table(title="Active Tasks")
        table.add_column("Priority", justify="left")
        table.add_column("Title", justify="left")
        table.add_column("Status", justify="left")
        table.add_column("Due Date", justify="left")
        
        for t in all_tasks:
            table.add_row(
                str(getattr(t, "priority", "")),
                str(getattr(t, "title", t.description[:30])),
                str(getattr(t, "status", "")),
                str(getattr(t, "due_date", "None"))
            )
            
        self.console.print(table)

    async def _cmd_memory(self, query: str) -> None:
        if not query:
            self.console.print("[red]Please provide a query: /memory <query>[/red]")
            return
            
        results = await self.kernel.memory_api.search(query, limit=5)
        if not results:
            self.console.print("[yellow]No memories found.[/yellow]")
            return
            
        for m in results:
            content = m.content
            if len(content) > 80:
                content = content[:80] + "..."
            self.console.print(f"[{m.memory_type}] {content} (importance: {m.importance:.2f})")

    async def _cmd_status(self) -> None:
        if not self.session_context:
            return
            
        session_id = self.session_context.session_id[:8]
        # Duration calculation
        duration_s = int(time.time() - self.session_context.created_at.timestamp())
        duration_str = f"{duration_s // 60}m {duration_s % 60}s"
        
        messages = len(self.session_context.transcript)
        
        # Retrieve budget if possible
        budget_str = "Unknown"
        if self.kernel.llm_router and hasattr(self.kernel.llm_router, "budget_manager"):
            budget = self.kernel.llm_router.budget_manager
            # Example property usage
            if hasattr(budget, "get_current_usage"):
                usage = await budget.get_current_usage()
                budget_str = f"${usage.get('daily_cost', 0):.2f}"
        
        self.console.print(f"Session ID: {session_id}")
        self.console.print(f"Duration: {duration_str}")
        self.console.print(f"Messages: {messages}")
        self.console.print(f"Budget today: {budget_str}")

    def _cmd_help(self) -> None:
        table = Table(title="Available Commands")
        table.add_column("Command", style="cyan")
        table.add_column("Description")
        
        table.add_row("/tasks", "List active tasks")
        table.add_row("/memory <query>", "Show top 5 memories matching query")
        table.add_row("/status", "Display session status and budget")
        table.add_row("/help", "Display this help message")
        table.add_row("/quit", "Save session and exit")
        
        self.console.print(table)

    async def _handle_quit(self) -> None:
        self.console.print("Ending session...")
        if self.session_context:
            # End session returns the consolidation task
            consolidation_task = await self.kernel.session_manager.end_session(
                self.session_context.session_id, 
                trigger="user"
            )
            
            if consolidation_task:
                # Wait up to 30 seconds for consolidation
                try:
                    await asyncio.wait_for(consolidation_task, timeout=30.0)
                except asyncio.TimeoutError:
                    self.console.print("[yellow]Consolidation timed out, continuing in background.[/yellow]")
                except Exception as e:
                    self.console.print(f"[red]Consolidation error: {e}[/red]")
                    
        self.console.print("Session saved. Goodbye.")
        sys.exit(0)
