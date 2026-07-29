"""Private application-control orchestration for PC control (M2.3).

PRIVATE to ``aether.pc_control`` — never imported outside this package, and
reached only through ``PCControlAPI.execute_action`` (which gates launches
through ``SafetyValidator`` first). This layer holds orchestration, result
shaping, and logging; the raw OS interaction lives in ``_adapters.windows``.
"""

from aether.core.logging import get_logger
from aether.pc_control._adapters import windows
from aether.pc_control.api import ActionResult, ApplicationInfo

logger = get_logger(__name__)


def launch_application(executable: str, args: list[str]) -> ActionResult:
    """Launch an application via the Windows adapter.

    The caller (``PCControlAPI.execute_action``) has already cleared this
    executable through ``SafetyValidator``; this function performs no policy
    check of its own.

    Args:
        executable: The executable to launch.
        args: Command-line arguments.

    Returns:
        An ActionResult carrying the new process id on success.
    """
    ok, process_id, message = windows.windows_launch(executable, args)
    logger.info(
        "pc_control.launch",
        executable=executable,
        arg_count=len(args),
        success=ok,
        process_id=process_id,
        message=message,
    )
    return ActionResult(success=ok, message=message, process_id=process_id)


def close_application(process_id: int) -> ActionResult:
    """Terminate a running process by id via the Windows adapter.

    Args:
        process_id: The OS process id to terminate.

    Returns:
        An ActionResult; ``process_id`` is echoed back on success.
    """
    ok, message = windows.windows_close(process_id)
    logger.info(
        "pc_control.close",
        process_id=process_id,
        success=ok,
        message=message,
    )
    return ActionResult(success=ok, message=message, process_id=process_id if ok else None)


def focus_application(process_id: int) -> ActionResult:
    """Bring a running process's window to the foreground via the adapter.

    Args:
        process_id: The OS process id whose window to focus.

    Returns:
        An ActionResult; ``process_id`` is echoed back on success.
    """
    ok, message = windows.windows_focus(process_id)
    logger.info(
        "pc_control.focus",
        process_id=process_id,
        success=ok,
        message=message,
    )
    return ActionResult(success=ok, message=message, process_id=process_id if ok else None)


def list_running_applications() -> list[ApplicationInfo]:
    """Return the running applications observed by the Windows adapter.

    Returns:
        One ApplicationInfo per observable top-level application window.
    """
    apps = windows.windows_list_processes()
    logger.info("pc_control.list_running_applications", count=len(apps))
    return apps
