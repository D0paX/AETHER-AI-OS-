"""Unit tests for PCControlAPI application control (M2.3).

All OS interaction is mocked at the ``_adapters.windows`` boundary and the
SafetyValidator is mocked (or the real one loaded from permissions.yaml for the
defense-in-depth check). No process is ever really launched. The load-bearing
assertion is that ``validate_app_launch`` runs, and allows, BEFORE any adapter
call — and that a denied launch reaches the adapter not at all.

Pure unit tests — no database, Qdrant, or Redis fixture.
"""

import statistics
import time
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import yaml
from pydantic import ValidationError

from aether.pc_control import ActionResult, ApplicationInfo, PCAction, PCControlAPI
from aether.security import SafetyValidator, ValidationResult

REPO_ROOT = Path(__file__).resolve().parents[2]
REAL_PERMISSIONS_PATH = REPO_ROOT / ".aether" / "permissions.yaml"
_RAW = yaml.safe_load(REAL_PERMISSIONS_PATH.read_text(encoding="utf-8"))
FORBIDDEN_LAUNCH: list[str] = _RAW["applications"]["forbidden_launch"]
ALLOWED_LAUNCH: list[str] = _RAW["applications"]["allowed_launch"]

_ADAPTER = "aether.pc_control._adapters.windows"


def _allow(reason: str = "allowed") -> ValidationResult:
    return ValidationResult(allowed=True, reason=reason)


def _deny(reason: str = "denied") -> ValidationResult:
    return ValidationResult(allowed=False, reason=reason)


def _mock_validator(result: ValidationResult) -> MagicMock:
    v = MagicMock(spec=SafetyValidator)
    v.validate_app_launch = AsyncMock(return_value=result)
    return v


# =============================================================================
# Launch — gated through SafetyValidator
# =============================================================================
async def test_launch_allowed_dispatches_to_adapter() -> None:
    validator = _mock_validator(_allow())
    api = PCControlAPI(validator)
    with patch(f"{_ADAPTER}.windows_launch", return_value=(True, 4321, "ok")) as wl:
        result = await api.execute_action(
            PCAction(action_type="launch", executable="notepad.exe", args=["a.txt"])
        )
    validator.validate_app_launch.assert_awaited_once_with("notepad.exe")
    wl.assert_called_once_with("notepad.exe", ["a.txt"])
    assert result.success is True
    assert result.process_id == 4321


async def test_launch_denied_never_reaches_adapter() -> None:
    validator = _mock_validator(_deny("in the forbidden_launch list"))
    api = PCControlAPI(validator)
    with patch(f"{_ADAPTER}.windows_launch") as wl:
        result = await api.execute_action(PCAction(action_type="launch", executable="cmd.exe"))
    validator.validate_app_launch.assert_awaited_once_with("cmd.exe")
    wl.assert_not_called()
    assert result.success is False
    assert result.process_id is None
    assert "denied" in result.message.lower()


async def test_validate_is_called_before_adapter_dispatch() -> None:
    """The single most important ordering in this module: gate before action."""
    validator = _mock_validator(_allow())
    api = PCControlAPI(validator)
    manager = MagicMock()
    manager.attach_mock(validator.validate_app_launch, "validate")
    with patch(f"{_ADAPTER}.windows_launch", return_value=(True, 1, "ok")) as wl:
        manager.attach_mock(wl, "launch")
        await api.execute_action(PCAction(action_type="launch", executable="notepad.exe"))
    names = [c[0] for c in manager.mock_calls if c[0] in {"validate", "launch"}]
    assert names == ["validate", "launch"], f"validate must precede launch: {names}"


# =============================================================================
# Defense in depth — every forbidden_launch entry rejected at THIS layer too
# =============================================================================
@pytest.mark.parametrize("executable", FORBIDDEN_LAUNCH)
async def test_forbidden_entry_denied_at_api_layer_with_real_validator(
    executable: str,
) -> None:
    """With the REAL SafetyValidator, each forbidden exe is denied before dispatch."""
    api = PCControlAPI(SafetyValidator(REAL_PERMISSIONS_PATH))
    with patch(f"{_ADAPTER}.windows_launch") as wl:
        result = await api.execute_action(PCAction(action_type="launch", executable=executable))
    assert result.success is False
    wl.assert_not_called()


@pytest.mark.parametrize("executable", ALLOWED_LAUNCH)
async def test_allowed_entry_dispatches_with_real_validator(executable: str) -> None:
    api = PCControlAPI(SafetyValidator(REAL_PERMISSIONS_PATH))
    with patch(f"{_ADAPTER}.windows_launch", return_value=(True, 7, "ok")) as wl:
        result = await api.execute_action(PCAction(action_type="launch", executable=executable))
    assert result.success is True
    wl.assert_called_once()


# =============================================================================
# list_applications — read-only, no gate
# =============================================================================
async def test_list_applications_returns_adapter_data() -> None:
    api = PCControlAPI(_mock_validator(_allow()))
    fake = [
        ApplicationInfo(name="notepad.exe", process_id=111, window_title="Untitled"),
        ApplicationInfo(name="chrome.exe", process_id=222, window_title="Web"),
    ]
    with patch(f"{_ADAPTER}.windows_list_processes", return_value=fake):
        apps = await api.list_applications()
    assert apps == fake
    # No validator gate on a read-only observation.
    api._safety_validator.validate_app_launch.assert_not_called()  # type: ignore[attr-defined]


# =============================================================================
# close / focus — resolve pid by name, then act
# =============================================================================
async def test_close_resolves_pid_and_calls_adapter() -> None:
    api = PCControlAPI(_mock_validator(_allow()))
    running = [ApplicationInfo(name="notepad.exe", process_id=909, window_title="x")]
    with (
        patch(f"{_ADAPTER}.windows_list_processes", return_value=running),
        patch(f"{_ADAPTER}.windows_close", return_value=(True, "terminated")) as wc,
    ):
        result = await api.execute_action(PCAction(action_type="close", executable="notepad.exe"))
    wc.assert_called_once_with(909)
    assert result.success is True
    assert result.process_id == 909


async def test_close_unknown_process_reports_failure() -> None:
    api = PCControlAPI(_mock_validator(_allow()))
    with (
        patch(f"{_ADAPTER}.windows_list_processes", return_value=[]),
        patch(f"{_ADAPTER}.windows_close") as wc,
    ):
        result = await api.execute_action(PCAction(action_type="close", executable="nothere.exe"))
    wc.assert_not_called()
    assert result.success is False


async def test_focus_resolves_pid_and_calls_adapter() -> None:
    api = PCControlAPI(_mock_validator(_allow()))
    running = [ApplicationInfo(name="notepad.exe", process_id=515, window_title="x")]
    with (
        patch(f"{_ADAPTER}.windows_list_processes", return_value=running),
        patch(f"{_ADAPTER}.windows_focus", return_value=(True, "focused")) as wf,
    ):
        result = await api.execute_action(PCAction(action_type="focus", executable="NOTEPAD.EXE"))
    wf.assert_called_once_with(515)
    assert result.success is True


# =============================================================================
# Models
# =============================================================================
def test_pcaction_frozen_and_defaults() -> None:
    a = PCAction(action_type="launch", executable="notepad.exe")
    assert a.args == []
    with pytest.raises(ValidationError):  # frozen
        a.executable = "cmd.exe"  # type: ignore[misc]


def test_actionresult_and_applicationinfo_shapes() -> None:
    r = ActionResult(success=True, message="done", process_id=5)
    assert (r.success, r.message, r.process_id) == (True, "done", 5)
    info = ApplicationInfo(name="notepad.exe", process_id=5, window_title=None)
    assert info.window_title is None


# =============================================================================
# Architecture — only the adapter imports the automation libs; adapter is private
# =============================================================================
def test_only_windows_adapter_imports_automation_libs() -> None:
    pc_root = REPO_ROOT / "aether" / "pc_control"
    adapter = pc_root / "_adapters" / "windows.py"
    for py_file in pc_root.rglob("*.py"):
        if py_file == adapter:
            continue
        text = py_file.read_text(encoding="utf-8")
        assert "pywinauto" not in text, f"pywinauto import outside adapter: {py_file}"
        assert "pyautogui" not in text, f"pyautogui import outside adapter: {py_file}"


def test_no_external_module_imports_private_adapters() -> None:
    """Nothing outside aether/pc_control/ reaches into _adapters or _control."""
    aether_root = REPO_ROOT / "aether"
    for py_file in aether_root.rglob("*.py"):
        if "pc_control" in py_file.parts:
            continue
        text = py_file.read_text(encoding="utf-8")
        assert "pc_control._adapters" not in text, f"{py_file} imports private _adapters"
        assert "pc_control._control" not in text, f"{py_file} imports private _control"


# =============================================================================
# Performance — execute_action (non-destructive) p50 < 500ms, p95 < 1000ms
# =============================================================================
async def test_performance_targets() -> None:
    api = PCControlAPI(_mock_validator(_allow()))
    samples: list[float] = []
    with patch(f"{_ADAPTER}.windows_launch", return_value=(True, 1, "ok")):
        action = PCAction(action_type="launch", executable="notepad.exe")
        for _ in range(500):
            start = time.perf_counter()
            await api.execute_action(action)
            samples.append((time.perf_counter() - start) * 1000.0)
    samples.sort()
    p50 = statistics.median(samples)
    p95 = samples[int(len(samples) * 0.95)]
    assert p50 < 500.0, f"p50 {p50:.3f}ms exceeds 500ms"
    assert p95 < 1000.0, f"p95 {p95:.3f}ms exceeds 1000ms"
