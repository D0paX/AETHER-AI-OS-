"""Public PC control interface for Aether (M2.3 application control; M2.4 files).

SECURITY-SENSITIVE MODULE (AI_GENERATION_RULES_V2.md Section 13.1).

``PCControlAPI`` is the sole interface through which any PC control action is
taken. Every application *launch* and every file operation passes through
``SafetyValidator`` before a single call reaches the private ``_control`` /
``_adapters`` layers — there is no fast path around that check, and every path is
resolved (``Path.resolve``) BEFORE it is validated. The ``SafetyValidator`` is
injected, never constructed here, so the gate can be exercised with a mock.

This module implements application control (launch, close, focus, list) and file
operations (search, read, move — no delete, ever). System monitoring (M2.5)
extends this same module later. Registry, service, and driver control are
permanently out of scope.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Literal

from pydantic import BaseModel, ConfigDict

from aether.core.exceptions import ToolExecutionError, ToolPermissionError
from aether.core.logging import get_logger
from aether.security import DenialReason, SafetyValidator, ValidationResult

if TYPE_CHECKING:
    from aether.pc_control._control.file_ops import (
        FileContent,
        FileInfo,
        FileSearchFilter,
    )

logger = get_logger(__name__)


class PCAction(BaseModel):
    """A requested PC control action.

    Attributes:
        action_type: One of ``launch``, ``close``, ``focus``, ``move``.
        executable: The target executable. For ``launch`` it is what gets
            launched (and what ``SafetyValidator`` checks). For ``close`` /
            ``focus`` it is descriptive only; for ``move`` it is unused.
        args: Command-line arguments (``launch`` only).
        process_id: The specific process to act on. REQUIRED for ``close`` and
            ``focus`` — these operate on exactly this pid and nothing else.
            There is deliberately no name-to-pid resolution here: turning a
            spoken "close notepad" into one specific pid is a higher-layer
            decision a future agent makes explicitly, never an implicit
            first-match inside this low-level API.
        source: The exact file to move. REQUIRED for ``move``. An explicit,
            caller-supplied path — never a name or query resolved internally
            (the generalized M2.3 rule).
        destination: The exact target path for ``move``. REQUIRED for ``move``.
            If it already exists, the move is a FILE_OVERWRITE and needs a
            ``confirmation_token``.
    """

    model_config = ConfigDict(frozen=True)

    action_type: Literal["launch", "close", "focus", "move"]
    executable: str = ""
    args: list[str] = []
    process_id: int | None = None
    source: Path | None = None
    destination: Path | None = None


class ActionResult(BaseModel):
    """The outcome of a PC control action.

    Attributes:
        success: Whether the action completed.
        message: Human-readable outcome or reason for failure — never empty.
        process_id: The affected process id when known, else None.
    """

    model_config = ConfigDict(frozen=True)

    success: bool
    message: str
    process_id: int | None = None


class ApplicationInfo(BaseModel):
    """A running application, as observed on the host.

    Attributes:
        name: The executable base name (e.g. ``notepad.exe``).
        process_id: The OS process id.
        window_title: The top-level window title, if the process has one.
    """

    model_config = ConfigDict(frozen=True)

    name: str
    process_id: int
    window_title: str | None


class PCControlAPI:
    """The single entry point for every PC control action.

    Args:
        safety_validator: The permission gate. Injected (never instantiated
            internally) so callers and tests supply their own — real or mocked.
    """

    def __init__(self, safety_validator: SafetyValidator) -> None:
        self._safety_validator = safety_validator

    async def execute_action(
        self, action: PCAction, confirmation_token: str | None = None
    ) -> ActionResult:
        """Perform an application action, gating launches through SafetyValidator.

        For ``launch``, ``SafetyValidator.validate_app_launch()`` must allow the
        executable BEFORE any call into the private control layer. For ``move``,
        both source and destination are resolved and cleared through
        ``SafetyValidator.validate_file_operation()`` first, and overwriting an
        existing destination requires ``confirmation_token``. ``close`` and
        ``focus`` operate ONLY on ``action.process_id`` — the exact pid supplied,
        with no name-to-pid resolution — and are not launch-gated.

        Args:
            action: The action to perform.
            confirmation_token: Required to overwrite an existing file during a
                ``move``. A destructive file operation without it is denied,
                never performed "just this once". Unused for launch/close/focus.

        Returns:
            An ActionResult; ``message`` is always populated.
        """
        # Local import keeps the public module free of the private submodule at
        # import time (avoids an api <-> _control import cycle; the models above
        # are what _control imports from here).
        from aether.pc_control._control import app_control

        logger.info(
            "pc_control.execute_action.requested",
            action_type=action.action_type,
            executable=action.executable,
            arg_count=len(action.args),
        )

        if action.action_type == "launch":
            decision = await self._safety_validator.validate_app_launch(action.executable)
            logger.info(
                "pc_control.execute_action.validated",
                action_type="launch",
                executable=action.executable,
                allowed=decision.allowed,
                reason=decision.reason,
            )
            if not decision.allowed:
                return ActionResult(
                    success=False,
                    message=f"Launch denied by SafetyValidator: {decision.reason}",
                    process_id=None,
                )
            return app_control.launch_application(action.executable, action.args)

        if action.action_type == "close":
            if action.process_id is None:
                return ActionResult(
                    success=False,
                    message=(
                        "close requires an explicit process_id; this API targets "
                        "one specific pid and never resolves a name to a process."
                    ),
                    process_id=None,
                )
            return app_control.close_application(action.process_id)

        if action.action_type == "focus":
            if action.process_id is None:
                return ActionResult(
                    success=False,
                    message=(
                        "focus requires an explicit process_id; this API targets "
                        "one specific pid and never resolves a name to a process."
                    ),
                    process_id=None,
                )
            return app_control.focus_application(action.process_id)

        # action_type == "move" (exhaustive over the Literal)
        return await self._execute_move(action, confirmation_token)

    async def _execute_move(self, action: PCAction, confirmation_token: str | None) -> ActionResult:
        """Validate and perform a move; overwrite requires confirmation_token."""
        from aether.pc_control._control import file_ops

        if action.source is None or action.destination is None:
            return ActionResult(
                success=False,
                message="move requires explicit source and destination paths.",
                process_id=None,
            )

        source = action.source.resolve()
        destination = action.destination.resolve()

        # Source: moving a file modifies its location, so it is a write op.
        source_decision = await self._safety_validator.validate_file_operation("file.move", source)
        self._log_file_decision("move.source", source, source_decision)
        if not source_decision.allowed:
            return ActionResult(
                success=False,
                message=f"Move denied (source): {source_decision.reason}",
                process_id=None,
            )

        # Destination: an existing target makes this a destructive overwrite.
        destination_exists = destination.exists()
        destination_operation = "file.overwrite_existing" if destination_exists else "file.move"
        destination_decision = await self._safety_validator.validate_file_operation(
            destination_operation, destination
        )
        self._log_file_decision("move.destination", destination, destination_decision)
        if not destination_decision.allowed:
            return ActionResult(
                success=False,
                message=f"Move denied (destination): {destination_decision.reason}",
                process_id=None,
            )

        if destination_exists and not confirmation_token:
            return ActionResult(
                success=False,
                message=(
                    f"Destination '{destination}' already exists; overwriting it "
                    f"requires a confirmation_token."
                ),
                process_id=None,
            )

        return file_ops.move_file(source, destination)

    async def search_files(
        self, query: str, root: Path, filters: FileSearchFilter
    ) -> list[FileInfo]:
        """Search for files under ``root``, gated by SafetyValidator.

        The root is resolved and validated for read access BEFORE the search
        runs; a root outside the permitted read paths (or inside a forbidden
        path) is denied. THEN every candidate is validated individually
        (DEBT-023) so a forbidden or hidden path nested under an otherwise-allowed
        root never leaks into the results — a candidate is kept only if it passes
        the same read check, except that a size-only denial still lists it
        (search reports a file's metadata, not its content). Results are
        candidates for a caller to choose from — this method never acts on them.

        Args:
            query: A glob pattern, or a file-name substring if it has no glob
                metacharacters.
            root: The directory to search under.
            filters: Optional extension / modified-after filters.

        Returns:
            Matching, individually-validated files as FileInfo candidates.

        Raises:
            ToolPermissionError: If the (resolved) root is not permitted.
        """
        from aether.pc_control._control import file_ops

        resolved_root = root.resolve()
        decision = await self._safety_validator.validate_file_operation("file.read", resolved_root)
        self._log_file_decision("search", resolved_root, decision)
        if not decision.allowed:
            raise ToolPermissionError(f"Search denied: {decision.reason}")

        candidates = file_ops.search_files(query, resolved_root, filters)
        approved: list[FileInfo] = []
        for candidate in candidates:
            result = await self._safety_validator.validate_file_operation(
                "file.read", Path(candidate.path)
            )
            # Keep on allow; keep an oversized-but-permitted file too (search
            # lists metadata, not content); drop forbidden / hidden / out-of-bounds.
            if result.allowed or result.denial_reason is DenialReason.SIZE_EXCEEDED:
                approved.append(candidate)
        logger.info(
            "pc_control.search_files.filtered",
            root=str(resolved_root),
            scanned=len(candidates),
            returned=len(approved),
        )
        return approved

    async def read_file(self, path: Path) -> FileContent:
        """Read a file's content, gated by SafetyValidator.

        The path is resolved and validated for read access BEFORE the file is
        opened. Oversized files are truncated to the configured
        ``max_file_size_mb`` (``truncated=True``), never rejected outright — a
        ``SIZE_EXCEEDED`` denial is downgraded to a truncated read, while a
        forbidden / out-of-bounds / hidden path stays a hard denial.

        Args:
            path: The file to read.

        Returns:
            The file content (possibly truncated).

        Raises:
            ToolPermissionError: If the path is forbidden, out of bounds, or
                hidden when hidden files are disallowed.
            ToolExecutionError: If the file cannot be read (e.g. does not exist).
        """
        from aether.pc_control._control import file_ops

        resolved = path.resolve()
        decision = await self._safety_validator.validate_file_operation("file.read", resolved)
        self._log_file_decision("read", resolved, decision)
        if not decision.allowed and decision.denial_reason is not DenialReason.SIZE_EXCEEDED:
            raise ToolPermissionError(f"Read denied: {decision.reason}")
        try:
            return await file_ops.read_file(resolved, self._safety_validator.max_file_size_bytes)
        except OSError as exc:
            raise ToolExecutionError(f"Could not read '{resolved}': {exc}") from exc

    @staticmethod
    def _log_file_decision(operation: str, path: Path, decision: ValidationResult) -> None:
        """Write the audit-trail entry for a file-operation validation."""
        logger.info(
            "pc_control.file_operation.validated",
            operation=operation,
            path=str(path),
            allowed=decision.allowed,
            requires_confirmation=decision.requires_confirmation,
            reason=decision.reason,
        )

    async def list_applications(self) -> list[ApplicationInfo]:
        """Return the currently running applications.

        Read-only: observing running processes is not a privileged write action,
        so no SafetyValidator gate is required. The call is still logged.

        Returns:
            One ApplicationInfo per observable top-level application window.
        """
        from aether.pc_control._control import app_control

        apps = app_control.list_running_applications()
        logger.info("pc_control.list_applications", count=len(apps))
        return apps
