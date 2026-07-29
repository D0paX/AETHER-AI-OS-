"""Unit tests for PCControlAPI file operations (M2.4).

Real SafetyValidator (loaded from a temp permissions.yaml pointing at pytest's
tmp_path) plus real files under tmp_path — no mocking of the file layer, no
database/Qdrant/Redis. Every path is proven resolved-then-validated, forbidden
paths proven unreachable, destructive overwrite proven token-gated, and move
proven to act on exactly its passed source.

Manual/scratch discipline: every file these tests touch is created by the test
under tmp_path; nothing pre-existing is read, moved, or overwritten.
"""

import os
from pathlib import Path
from typing import Any

import pytest
import yaml

from aether.core.exceptions import ToolExecutionError, ToolPermissionError
from aether.pc_control import FileSearchFilter, PCAction, PCControlAPI
from aether.security import SafetyValidator

REPO_ROOT = Path(__file__).resolve().parents[2]
REAL_PERMISSIONS_PATH = REPO_ROOT / ".aether" / "permissions.yaml"
_REAL = yaml.safe_load(REAL_PERMISSIONS_PATH.read_text(encoding="utf-8"))
REAL_FORBIDDEN_PATHS: list[str] = [
    os.path.expandvars(p) for p in _REAL["filesystem"]["forbidden_paths"]
]

TOKEN = "user-confirmed"


def _write_permissions(
    tmp_path: Path,
    *,
    read: list[str] | None = None,
    write: list[str] | None = None,
    forbidden: list[str] | None = None,
    max_mb: int = 50,
    allow_hidden: bool = False,
) -> Path:
    config: dict[str, Any] = {
        "version": "1.0",
        "filesystem": {
            "read_paths": read if read is not None else [str(tmp_path)],
            "write_paths": write if write is not None else [str(tmp_path)],
            "forbidden_paths": forbidden if forbidden is not None else [],
            "max_file_size_mb": max_mb,
            "allow_hidden_files": allow_hidden,
        },
        "applications": {"allowed_launch": [], "forbidden_launch": []},
        "network": {"browser_automation_enabled": True, "blocked_domains": []},
        "destructive_operations": {
            "require_confirmation": True,
            "operations": [
                "file.delete",
                "file.move",
                "file.overwrite_existing",
                "process.terminate",
            ],
        },
        "memory": {
            "allow_memory_deletion": True,
            "require_confirmation_bulk_delete": True,
        },
    }
    dest = tmp_path / "permissions.yaml"
    dest.write_text(yaml.safe_dump(config), encoding="utf-8")
    return dest


def _api(tmp_path: Path, **kw: Any) -> PCControlAPI:
    return PCControlAPI(SafetyValidator(_write_permissions(tmp_path, **kw)))


# =============================================================================
# read_file
# =============================================================================
async def test_read_file_within_read_path(tmp_path: Path) -> None:
    target = tmp_path / "note.txt"
    target.write_text("hello world", encoding="utf-8")
    api = _api(tmp_path)
    result = await api.read_file(target)
    assert result.content == "hello world"
    assert result.truncated is False
    assert result.size_bytes == len(b"hello world")


async def test_read_file_outside_read_path_denied(tmp_path: Path) -> None:
    inside = tmp_path / "inside"
    inside.mkdir()
    outside = tmp_path / "outside.txt"
    outside.write_text("secret", encoding="utf-8")
    api = _api(tmp_path, read=[str(inside)], write=[str(inside)])
    with pytest.raises(ToolPermissionError):
        await api.read_file(outside)


@pytest.mark.parametrize("forbidden_dir", REAL_FORBIDDEN_PATHS)
async def test_read_forbidden_path_denied_real_config(forbidden_dir: str) -> None:
    api = PCControlAPI(SafetyValidator(REAL_PERMISSIONS_PATH))
    with pytest.raises(ToolPermissionError):
        await api.read_file(Path(forbidden_dir) / "probe.txt")


async def test_read_oversized_is_truncated_not_rejected(tmp_path: Path) -> None:
    big = tmp_path / "big.txt"
    big.write_bytes(b"a" * (2 * 1024 * 1024))  # 2 MB
    api = _api(tmp_path, max_mb=1)  # 1 MB cap
    result = await api.read_file(big)
    assert result.truncated is True
    assert result.size_bytes == 2 * 1024 * 1024
    assert len(result.content) == 1 * 1024 * 1024  # only the cap was read


async def test_read_within_limit_not_truncated(tmp_path: Path) -> None:
    small = tmp_path / "small.txt"
    small.write_bytes(b"a" * 2048)
    api = _api(tmp_path, max_mb=1)
    result = await api.read_file(small)
    assert result.truncated is False
    assert len(result.content) == 2048


async def test_read_hidden_denied_then_allowed(tmp_path: Path) -> None:
    hidden = tmp_path / ".secret"
    hidden.write_text("shh", encoding="utf-8")
    denied_api = _api(tmp_path, allow_hidden=False)
    with pytest.raises(ToolPermissionError):
        await denied_api.read_file(hidden)
    allowed_api = _api(tmp_path, allow_hidden=True)
    result = await allowed_api.read_file(hidden)
    assert result.content == "shh"


async def test_read_path_traversal_blocked_after_resolution(tmp_path: Path) -> None:
    """A ../.. path resolving outside the read root is denied, not followed."""
    sub = tmp_path / "sub"
    sub.mkdir()
    (tmp_path / "escape.txt").write_text("out", encoding="utf-8")
    api = _api(tmp_path, read=[str(sub)], write=[str(sub)])
    with pytest.raises(ToolPermissionError):
        await api.read_file(sub / ".." / "escape.txt")


async def test_read_nonexistent_raises_execution_error(tmp_path: Path) -> None:
    api = _api(tmp_path)
    with pytest.raises(ToolExecutionError):
        await api.read_file(tmp_path / "does_not_exist.txt")


# =============================================================================
# search_files
# =============================================================================
async def test_search_returns_matching_files(tmp_path: Path) -> None:
    (tmp_path / "a.txt").write_text("x", encoding="utf-8")
    (tmp_path / "b.txt").write_text("x", encoding="utf-8")
    (tmp_path / "c.log").write_text("x", encoding="utf-8")
    api = _api(tmp_path)
    results = await api.search_files("*.txt", tmp_path, FileSearchFilter())
    names = sorted(Path(r.path).name for r in results)
    assert names == ["a.txt", "b.txt"]


async def test_search_extension_filter(tmp_path: Path) -> None:
    (tmp_path / "a.txt").write_text("x", encoding="utf-8")
    (tmp_path / "b.md").write_text("x", encoding="utf-8")
    api = _api(tmp_path)
    results = await api.search_files("*", tmp_path, FileSearchFilter(extensions=["md"]))
    assert [Path(r.path).name for r in results] == ["b.md"]


async def test_search_root_outside_read_path_denied(tmp_path: Path) -> None:
    inside = tmp_path / "inside"
    inside.mkdir()
    api = _api(tmp_path, read=[str(inside)], write=[str(inside)])
    with pytest.raises(ToolPermissionError):
        await api.search_files("*", tmp_path, FileSearchFilter())


@pytest.mark.parametrize("forbidden_dir", REAL_FORBIDDEN_PATHS)
async def test_search_forbidden_root_denied_real_config(forbidden_dir: str) -> None:
    api = PCControlAPI(SafetyValidator(REAL_PERMISSIONS_PATH))
    with pytest.raises(ToolPermissionError):
        await api.search_files("*", Path(forbidden_dir), FileSearchFilter())


# =============================================================================
# move — via execute_action; overwrite token-gated; exact-source only
# =============================================================================
async def test_move_to_new_destination_succeeds(tmp_path: Path) -> None:
    source = tmp_path / "src.txt"
    source.write_text("data", encoding="utf-8")
    dest = tmp_path / "dst.txt"
    api = _api(tmp_path)
    result = await api.execute_action(PCAction(action_type="move", source=source, destination=dest))
    assert result.success is True
    assert not source.exists()
    assert dest.read_text(encoding="utf-8") == "data"


async def test_move_overwrite_without_token_denied(tmp_path: Path) -> None:
    source = tmp_path / "src.txt"
    source.write_text("new", encoding="utf-8")
    dest = tmp_path / "dst.txt"
    dest.write_text("original", encoding="utf-8")
    api = _api(tmp_path)
    result = await api.execute_action(PCAction(action_type="move", source=source, destination=dest))
    assert result.success is False
    assert "confirmation_token" in result.message
    # Nothing changed: source still there, destination unmodified.
    assert source.exists()
    assert dest.read_text(encoding="utf-8") == "original"


async def test_move_overwrite_with_token_succeeds(tmp_path: Path) -> None:
    source = tmp_path / "src.txt"
    source.write_text("new", encoding="utf-8")
    dest = tmp_path / "dst.txt"
    dest.write_text("original", encoding="utf-8")
    api = _api(tmp_path)
    result = await api.execute_action(
        PCAction(action_type="move", source=source, destination=dest),
        confirmation_token=TOKEN,
    )
    assert result.success is True
    assert not source.exists()
    assert dest.read_text(encoding="utf-8") == "new"


async def test_move_source_outside_write_path_denied(tmp_path: Path) -> None:
    writable = tmp_path / "writable"
    writable.mkdir()
    source = tmp_path / "elsewhere.txt"
    source.write_text("data", encoding="utf-8")
    api = _api(tmp_path, read=[str(writable)], write=[str(writable)])
    result = await api.execute_action(
        PCAction(action_type="move", source=source, destination=writable / "x.txt")
    )
    assert result.success is False
    assert source.exists()  # untouched


async def test_move_acts_only_on_exact_source(tmp_path: Path) -> None:
    """Move touches exactly its passed source; similar-named siblings survive."""
    source = tmp_path / "report.txt"
    source.write_text("the one", encoding="utf-8")
    sibling_bak = tmp_path / "report.txt.bak"
    sibling_bak.write_text("backup", encoding="utf-8")
    sibling_two = tmp_path / "report2.txt"
    sibling_two.write_text("another", encoding="utf-8")
    dest = tmp_path / "moved.txt"

    api = _api(tmp_path)
    result = await api.execute_action(PCAction(action_type="move", source=source, destination=dest))
    assert result.success is True
    assert not source.exists()
    assert dest.read_text(encoding="utf-8") == "the one"
    # The similarly-named siblings are completely untouched.
    assert sibling_bak.read_text(encoding="utf-8") == "backup"
    assert sibling_two.read_text(encoding="utf-8") == "another"


async def test_move_requires_source_and_destination(tmp_path: Path) -> None:
    api = _api(tmp_path)
    result = await api.execute_action(PCAction(action_type="move"))
    assert result.success is False
    assert "source and destination" in result.message


@pytest.mark.parametrize("forbidden_dir", REAL_FORBIDDEN_PATHS)
async def test_move_into_forbidden_denied_real_config(tmp_path: Path, forbidden_dir: str) -> None:
    source = tmp_path / "src.txt"
    source.write_text("data", encoding="utf-8")
    api = PCControlAPI(SafetyValidator(REAL_PERMISSIONS_PATH))
    result = await api.execute_action(
        PCAction(
            action_type="move",
            source=source,
            destination=Path(forbidden_dir) / "planted.txt",
        )
    )
    assert result.success is False
    assert source.exists()  # never moved


# =============================================================================
# validator property + no-delete guarantee
# =============================================================================
def test_max_file_size_bytes_property(tmp_path: Path) -> None:
    validator = SafetyValidator(_write_permissions(tmp_path, max_mb=7))
    assert validator.max_file_size_bytes == 7 * 1024 * 1024


def test_module_exposes_no_delete_capability() -> None:
    pc_root = REPO_ROOT / "aether" / "pc_control"
    for py_file in pc_root.rglob("*.py"):
        text = py_file.read_text(encoding="utf-8").lower()
        assert "def delete" not in text, f"delete function in {py_file}"
        assert "def remove_file" not in text, f"remove_file function in {py_file}"


# =============================================================================
# Performance — search p50 < 1000ms, p95 < 2000ms
# =============================================================================
async def test_search_performance(tmp_path: Path) -> None:
    import statistics
    import time

    for i in range(50):
        (tmp_path / f"f{i}.txt").write_text("x", encoding="utf-8")
    api = _api(tmp_path)
    samples: list[float] = []
    for _ in range(30):
        start = time.perf_counter()
        await api.search_files("*.txt", tmp_path, FileSearchFilter())
        samples.append((time.perf_counter() - start) * 1000.0)
    samples.sort()
    p50 = statistics.median(samples)
    p95 = samples[int(len(samples) * 0.95)]
    assert p50 < 1000.0, f"p50 {p50:.1f}ms"
    assert p95 < 2000.0, f"p95 {p95:.1f}ms"
