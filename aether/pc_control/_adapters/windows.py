"""Private Windows adapter for application control (M2.3).

PRIVATE to ``aether.pc_control`` and the ONLY module in this milestone permitted
to import the automation libraries (``pywinauto``). It is reached only through
``app_control`` — itself reached only through ``PCControlAPI.execute_action``,
where every launch is gated by ``SafetyValidator``.

Every function catches the SPECIFIC exceptions the underlying library raises
(never a bare ``except``) and returns a structured value; a raw OS/library
exception never propagates to the caller. Launch, close, and process listing use
the pywin32 process APIs (already present); focus uses ``pywinauto`` (imported
lazily so the module loads, and unit tests run, without the automation stack
installed).
"""

import os
import subprocess

import pywintypes
import win32api
import win32gui
import win32process

from aether.core.logging import get_logger
from aether.pc_control.api import ApplicationInfo

logger = get_logger(__name__)

# Win32 process-access rights (winnt.h). Named here rather than pulled from a
# win32con import so the intent is explicit at the call site.
_PROCESS_TERMINATE = 0x0001
_PROCESS_QUERY_INFORMATION = 0x0400
_PROCESS_VM_READ = 0x0010


def windows_launch(executable: str, args: list[str]) -> tuple[bool, int | None, str]:
    """Launch an executable, returning (success, process_id, message).

    Args:
        executable: The executable name (resolved on PATH) or full path.
        args: Command-line arguments.

    Returns:
        (True, pid, message) on success; (False, None, message) on failure.
    """
    try:
        # SafetyValidator has already vetted `executable` upstream; shell=False.
        proc = subprocess.Popen([executable, *args])
    except FileNotFoundError:
        return (False, None, f"Executable not found: '{executable}'.")
    except (OSError, ValueError) as exc:
        return (False, None, f"Failed to launch '{executable}': {exc}")
    return (True, proc.pid, f"Launched '{executable}' (pid {proc.pid}).")


def windows_close(process_id: int) -> tuple[bool, str]:
    """Terminate a process by id, returning (success, message).

    Args:
        process_id: The OS process id to terminate.

    Returns:
        (True, message) on success; (False, message) on failure.
    """
    try:
        handle = win32api.OpenProcess(_PROCESS_TERMINATE, False, process_id)
    except pywintypes.error as exc:
        return (False, f"Cannot open process {process_id} to terminate: {exc}")
    try:
        win32process.TerminateProcess(handle, 0)
    except pywintypes.error as exc:
        return (False, f"Failed to terminate process {process_id}: {exc}")
    finally:
        win32api.CloseHandle(handle)
    return (True, f"Terminated process {process_id}.")


def windows_focus(process_id: int) -> tuple[bool, str]:
    """Bring a process's top window to the foreground, returning (success, message).

    Args:
        process_id: The OS process id whose window to focus.

    Returns:
        (True, message) on success; (False, message) on failure.
    """
    try:
        from pywinauto import Application
        from pywinauto.application import ProcessNotFoundError
        from pywinauto.findwindows import ElementNotFoundError
    except ImportError as exc:
        return (False, f"pywinauto is not installed; cannot focus: {exc}")

    try:
        app = Application(backend="uia").connect(process=process_id, timeout=5)
        app.top_window().set_focus()
    except ProcessNotFoundError:
        return (False, f"No running process {process_id} to focus.")
    except (ElementNotFoundError, RuntimeError) as exc:
        return (False, f"Could not focus process {process_id}: {exc}")
    return (True, f"Focused process {process_id}.")


def windows_list_processes() -> list[ApplicationInfo]:
    """List running applications by enumerating visible, titled top-level windows.

    Returns:
        One ApplicationInfo per visible top-level window that has a title.
    """
    apps: list[ApplicationInfo] = []

    def _collect(hwnd: int, _extra: object) -> bool:
        if not win32gui.IsWindowVisible(hwnd):
            return True
        title = win32gui.GetWindowText(hwnd)
        if not title:
            return True
        _thread_id, process_id = win32process.GetWindowThreadProcessId(hwnd)
        apps.append(
            ApplicationInfo(
                name=_process_name(process_id),
                process_id=process_id,
                window_title=title,
            )
        )
        return True

    try:
        win32gui.EnumWindows(_collect, None)
    except pywintypes.error as exc:
        logger.warning("pc_control.list.enum_failed", error=str(exc))
    return apps


def _process_name(process_id: int) -> str:
    """Return a process's executable base name, or '' if it cannot be read."""
    try:
        handle = win32api.OpenProcess(
            _PROCESS_QUERY_INFORMATION | _PROCESS_VM_READ, False, process_id
        )
    except pywintypes.error:
        return ""
    try:
        return os.path.basename(str(win32process.GetModuleFileNameEx(handle, 0)))
    except pywintypes.error:
        return ""
    finally:
        win32api.CloseHandle(handle)
