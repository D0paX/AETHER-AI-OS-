"""Public PC control interface for Aether (M2.3: application control).

SECURITY-SENSITIVE MODULE (AI_GENERATION_RULES_V2.md Section 13.1).

``PCControlAPI`` is the sole interface through which any PC control action is
taken. Every application *launch* passes through ``SafetyValidator`` before a
single call reaches the private ``_control``/``_adapters`` layers — there is no
fast path around that check. The ``SafetyValidator`` is injected, never
constructed here, so the gate can be exercised with a mock in tests.

This milestone implements application control only (launch, close, focus, list).
File operations (M2.4) and system monitoring (M2.5) extend this same module
later. Registry, service, and driver control are permanently out of scope.
"""

from typing import Literal

from pydantic import BaseModel, ConfigDict

from aether.core.logging import get_logger
from aether.security import SafetyValidator

logger = get_logger(__name__)


class PCAction(BaseModel):
    """A requested PC control action.

    Attributes:
        action_type: One of ``launch``, ``close``, ``focus``.
        executable: The target executable. For ``launch`` it is what gets
            launched (and what ``SafetyValidator`` checks). For ``close`` and
            ``focus`` it names the running application to act on; the concrete
            process id is resolved from the live process list.
        args: Command-line arguments (``launch`` only).
    """

    model_config = ConfigDict(frozen=True)

    action_type: Literal["launch", "close", "focus"]
    executable: str
    args: list[str] = []


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

        For ``launch``, ``SafetyValidator.validate_app_launch()`` is called and
        must allow the executable BEFORE any call into the private control layer
        — an unlisted or forbidden executable is denied and nothing is launched.
        ``close`` and ``focus`` operate on an already-running process (resolved
        from ``executable``) and are not launch-gated: terminating or focusing a
        process is not the privileged act that launching an arbitrary binary is.

        Args:
            action: The action to perform.
            confirmation_token: Reserved for the destructive-file-operation flow
                introduced in M2.4; unused for application actions.

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
            process_id = self._resolve_process_id(action.executable)
            if process_id is None:
                return ActionResult(
                    success=False,
                    message=f"No running process named '{action.executable}' to close.",
                    process_id=None,
                )
            return app_control.close_application(process_id)

        # action_type == "focus" (exhaustive over the Literal)
        process_id = self._resolve_process_id(action.executable)
        if process_id is None:
            return ActionResult(
                success=False,
                message=f"No running process named '{action.executable}' to focus.",
                process_id=None,
            )
        return app_control.focus_application(process_id)

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

    @staticmethod
    def _resolve_process_id(executable: str) -> int | None:
        """Resolve a running process id from an executable name (first match).

        Args:
            executable: An executable name or path; matched on the base name,
                case-insensitively.

        Returns:
            The process id of the first running match, or None.
        """
        from pathlib import PureWindowsPath

        from aether.pc_control._control import app_control

        target = PureWindowsPath(executable).name.lower()
        for app in app_control.list_running_applications():
            if app.name.lower() == target:
                return app.process_id
        return None
