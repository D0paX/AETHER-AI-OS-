"""Unit tests for the SafetyValidator security module (M2.2).

Security-critical classification (AI_GENERATION_RULES_V2.md Section 13): these
target near-complete branch coverage of every permission path. Every entry in
the real ``.aether/permissions.yaml`` forbidden lists is proven denied
individually; the fail-closed default is proven for both file and app paths;
and every result is proven to carry a non-empty reason.

Pure unit tests — no database, Qdrant, or Redis fixture (this module touches
none of the three protected data stores, so the M2.1.7 test-isolation guard
does not apply).
"""

import os
import statistics
import time
from pathlib import Path
from typing import Any

import pytest
import yaml
from pydantic import ValidationError

from aether.core.exceptions import ConfigurationError
from aether.security import (
    DenialReason,
    DestructiveOperation,
    Permission,
    SafetyValidator,
    ValidationResult,
)

# --- Real policy, read directly (not via the private loader) -------------------
REPO_ROOT = Path(__file__).resolve().parents[2]
REAL_PERMISSIONS_PATH = REPO_ROOT / ".aether" / "permissions.yaml"
_RAW = yaml.safe_load(REAL_PERMISSIONS_PATH.read_text(encoding="utf-8"))

FORBIDDEN_LAUNCH: list[str] = _RAW["applications"]["forbidden_launch"]
ALLOWED_LAUNCH: list[str] = _RAW["applications"]["allowed_launch"]
FORBIDDEN_PATHS_EXPANDED: list[str] = [
    os.path.expandvars(p) for p in _RAW["filesystem"]["forbidden_paths"]
]
READ_PATHS_EXPANDED: list[str] = [os.path.expandvars(p) for p in _RAW["filesystem"]["read_paths"]]
WRITE_PATHS_EXPANDED: list[str] = [os.path.expandvars(p) for p in _RAW["filesystem"]["write_paths"]]


def _norm(p: str) -> str:
    return os.path.normcase(os.path.abspath(p))


# A directory that is readable but NOT writable (e.g. Downloads).
_WRITE_NORMS = {_norm(p) for p in WRITE_PATHS_EXPANDED}
READ_ONLY_DIRS = [p for p in READ_PATHS_EXPANDED if _norm(p) not in _WRITE_NORMS]


@pytest.fixture
def validator() -> SafetyValidator:
    """A SafetyValidator loaded from the real project permissions file."""
    return SafetyValidator(REAL_PERMISSIONS_PATH)


# --- Temp-config helper for policy-variant tests -------------------------------
def _base_config() -> dict[str, Any]:
    return {
        "version": "1.0",
        "filesystem": {
            "read_paths": ["${USERPROFILE}/Documents"],
            "write_paths": ["${USERPROFILE}/Documents/Aether"],
            "forbidden_paths": ["C:/Windows"],
            "max_file_size_mb": 50,
            "allow_hidden_files": False,
        },
        "applications": {
            "allowed_launch": ["notepad.exe"],
            "forbidden_launch": ["cmd.exe"],
        },
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


def write_config(tmp_path: Path, **section_overrides: dict[str, Any]) -> Path:
    """Write a permissions YAML with the given section overrides; return path."""
    config = _base_config()
    for section, overrides in section_overrides.items():
        config[section] = {**config[section], **overrides}
    dest = tmp_path / "permissions.yaml"
    dest.write_text(yaml.safe_dump(config), encoding="utf-8")
    return dest


# =============================================================================
# Application launch — forbidden list, allow list, fail-closed default
# =============================================================================
@pytest.mark.parametrize("executable", FORBIDDEN_LAUNCH)
async def test_every_forbidden_launch_entry_denied(
    validator: SafetyValidator, executable: str
) -> None:
    result = await validator.validate_app_launch(executable)
    assert result.allowed is False
    assert executable.lower() in result.reason


@pytest.mark.parametrize("executable", FORBIDDEN_LAUNCH)
async def test_forbidden_launch_case_and_path_variants_denied(
    validator: SafetyValidator, executable: str
) -> None:
    """Upper-case, and a full Windows path, must resolve to the same denial."""
    for variant in (
        executable.upper(),
        executable.capitalize(),
        f"C:\\Windows\\System32\\{executable}",
        f"C:/Windows/System32/{executable}",
    ):
        result = await validator.validate_app_launch(variant)
        assert result.allowed is False, f"{variant} should be denied"


@pytest.mark.parametrize("executable", ALLOWED_LAUNCH)
async def test_every_allowed_launch_entry_allowed(
    validator: SafetyValidator, executable: str
) -> None:
    result = await validator.validate_app_launch(executable)
    assert result.allowed is True
    # Case-insensitivity: upper-case form is allowed too.
    upper = await validator.validate_app_launch(executable.upper())
    assert upper.allowed is True


@pytest.mark.parametrize("executable", ["some_random_unlisted.exe", "evil.exe", "python.exe", ""])
async def test_unlisted_executable_denied_fail_closed(
    validator: SafetyValidator, executable: str
) -> None:
    result = await validator.validate_app_launch(executable)
    assert result.allowed is False
    assert result.reason  # non-empty


async def test_full_path_allowed_executable_still_allowed(
    validator: SafetyValidator,
) -> None:
    result = await validator.validate_app_launch("C:\\Program Files\\Notepad\\notepad.exe")
    assert result.allowed is True


# =============================================================================
# File operations — forbidden paths, read/write allowlist, fail-closed
# =============================================================================
@pytest.mark.parametrize("forbidden_dir", FORBIDDEN_PATHS_EXPANDED)
async def test_every_forbidden_path_denied_for_read_and_write(
    validator: SafetyValidator, forbidden_dir: str
) -> None:
    """Each forbidden entry blocks both read and write of a child path."""
    child = Path(forbidden_dir) / "probe.txt"
    for op in ("file.read", "file.write", "file.delete"):
        result = await validator.validate_file_operation(op, child)
        assert result.allowed is False, f"{op} under {forbidden_dir} must deny"
        assert "forbidden" in result.reason.lower()


async def test_read_under_read_path_allowed(validator: SafetyValidator) -> None:
    target = Path(READ_PATHS_EXPANDED[0]) / "notes.txt"
    result = await validator.validate_file_operation("file.read", target)
    assert result.allowed is True


async def test_write_under_write_path_allowed(validator: SafetyValidator) -> None:
    target = Path(WRITE_PATHS_EXPANDED[0]) / "out.txt"
    result = await validator.validate_file_operation("file.write", target)
    assert result.allowed is True
    assert result.requires_confirmation is False


@pytest.mark.skipif(not READ_ONLY_DIRS, reason="no read-only-only path in policy")
async def test_write_under_read_only_path_denied(validator: SafetyValidator) -> None:
    target = Path(READ_ONLY_DIRS[0]) / "x.txt"
    result = await validator.validate_file_operation("file.write", target)
    assert result.allowed is False
    assert "write" in result.reason.lower()


async def test_read_outside_any_read_path_denied_fail_closed(
    validator: SafetyValidator,
) -> None:
    target = Path("C:/SomeRandom/unlisted/place/file.txt")
    result = await validator.validate_file_operation("file.read", target)
    assert result.allowed is False
    assert "fail-closed" in result.reason.lower()


@pytest.mark.parametrize("operation", ["file.frobnicate", "process.terminate", "", "read"])
async def test_unrecognized_file_operation_denied(
    validator: SafetyValidator, operation: str
) -> None:
    """Unknown operations (incl. non-file 'process.terminate') fail closed."""
    target = Path(WRITE_PATHS_EXPANDED[0]) / "out.txt"
    result = await validator.validate_file_operation(operation, target)
    assert result.allowed is False


# =============================================================================
# Destructive operations + confirmation
# =============================================================================
@pytest.mark.parametrize(
    "operation",
    ["file.delete", "file.move", "file.overwrite_existing"],
)
async def test_destructive_file_op_requires_confirmation(
    validator: SafetyValidator, operation: str
) -> None:
    """A permitted destructive op is allowed but flagged for confirmation."""
    target = Path(WRITE_PATHS_EXPANDED[0]) / "target.txt"
    result = await validator.validate_file_operation(operation, target)
    assert result.allowed is True
    assert result.requires_confirmation is True
    assert "confirmation" in result.reason.lower()


async def test_nondestructive_write_no_confirmation(
    validator: SafetyValidator,
) -> None:
    target = Path(WRITE_PATHS_EXPANDED[0]) / "target.txt"
    result = await validator.validate_file_operation("file.write", target)
    assert result.allowed is True
    assert result.requires_confirmation is False


async def test_confirmation_flag_off_when_policy_disables_it(tmp_path: Path) -> None:
    cfg = write_config(
        tmp_path,
        destructive_operations={"require_confirmation": False},
        filesystem={
            "read_paths": [str(tmp_path)],
            "write_paths": [str(tmp_path)],
            "forbidden_paths": [],
            "allow_hidden_files": True,
        },
    )
    v = SafetyValidator(cfg)
    result = await v.validate_file_operation("file.delete", tmp_path / "x.txt")
    assert result.allowed is True
    assert result.requires_confirmation is False


# =============================================================================
# is_destructive
# =============================================================================
@pytest.mark.parametrize("op", [e.value for e in DestructiveOperation])
def test_is_destructive_true_for_every_enum_value(validator: SafetyValidator, op: str) -> None:
    assert validator.is_destructive(op) is True


@pytest.mark.parametrize(
    "op", ["file.read", "file.write", "file.create", "app.launch", "", "delete"]
)
def test_is_destructive_false_for_nondestructive(validator: SafetyValidator, op: str) -> None:
    assert validator.is_destructive(op) is False


# =============================================================================
# Hidden files + size limit
# =============================================================================
async def test_hidden_file_denied_when_disabled(validator: SafetyValidator) -> None:
    target = Path(WRITE_PATHS_EXPANDED[0]) / ".secret"
    result = await validator.validate_file_operation("file.read", target)
    assert result.allowed is False
    assert "hidden" in result.reason.lower()


async def test_hidden_file_allowed_when_enabled(tmp_path: Path) -> None:
    cfg = write_config(
        tmp_path,
        filesystem={
            "read_paths": [str(tmp_path)],
            "write_paths": [str(tmp_path)],
            "forbidden_paths": [],
            "allow_hidden_files": True,
        },
    )
    v = SafetyValidator(cfg)
    result = await v.validate_file_operation("file.read", tmp_path / ".secret")
    assert result.allowed is True


async def test_file_over_size_limit_denied(tmp_path: Path) -> None:
    cfg = write_config(
        tmp_path,
        filesystem={
            "read_paths": [str(tmp_path)],
            "write_paths": [str(tmp_path)],
            "forbidden_paths": [],
            "max_file_size_mb": 1,
            "allow_hidden_files": True,
        },
    )
    v = SafetyValidator(cfg)
    big = tmp_path / "big.bin"
    big.write_bytes(b"\0" * (2 * 1024 * 1024))
    denied = await v.validate_file_operation("file.read", big)
    assert denied.allowed is False
    assert "size" in denied.reason.lower()

    small = tmp_path / "small.bin"
    small.write_bytes(b"\0" * 128)
    allowed = await v.validate_file_operation("file.read", small)
    assert allowed.allowed is True


# =============================================================================
# Browser action (Phase 3 interface — fully tested now)
# =============================================================================
async def test_browser_allowed_when_enabled_and_not_blocked(
    validator: SafetyValidator,
) -> None:
    result = await validator.validate_browser_action("https://example.com/page", "navigate")
    assert result.allowed is True


async def test_browser_denied_when_disabled(tmp_path: Path) -> None:
    cfg = write_config(tmp_path, network={"browser_automation_enabled": False})
    v = SafetyValidator(cfg)
    result = await v.validate_browser_action("https://example.com", "navigate")
    assert result.allowed is False
    assert "disabled" in result.reason.lower()


async def test_browser_blocked_domain_and_subdomain_denied(tmp_path: Path) -> None:
    cfg = write_config(tmp_path, network={"blocked_domains": ["evil.com"]})
    v = SafetyValidator(cfg)
    for url in ("https://evil.com/x", "https://sub.evil.com/y", "http://EVIL.COM"):
        result = await v.validate_browser_action(url, "navigate")
        assert result.allowed is False, f"{url} should be blocked"


async def test_browser_unparseable_url_denied(tmp_path: Path) -> None:
    cfg = write_config(tmp_path, network={"blocked_domains": ["evil.com"]})
    v = SafetyValidator(cfg)
    result = await v.validate_browser_action("not a url at all", "navigate")
    assert result.allowed is False


# =============================================================================
# Every result explains itself (ADR-011 Section 9)
# =============================================================================
async def test_every_result_has_non_empty_reason(validator: SafetyValidator) -> None:
    results = [
        await validator.validate_app_launch("cmd.exe"),
        await validator.validate_app_launch("notepad.exe"),
        await validator.validate_app_launch("unlisted.exe"),
        await validator.validate_file_operation("file.read", Path("C:/Windows/x")),
        await validator.validate_file_operation(
            "file.write", Path(WRITE_PATHS_EXPANDED[0]) / "a.txt"
        ),
        await validator.validate_browser_action("https://example.com", "navigate"),
    ]
    for r in results:
        assert r.reason
        assert r.reason.strip()


def test_validation_result_rejects_empty_reason() -> None:
    with pytest.raises(ValidationError):
        ValidationResult(allowed=True, reason="")
    with pytest.raises(ValidationError):
        ValidationResult(allowed=False, reason="   ")


# =============================================================================
# Models
# =============================================================================
def test_destructive_operation_values() -> None:
    assert DestructiveOperation.FILE_DELETE.value == "file.delete"
    assert DestructiveOperation.FILE_MOVE.value == "file.move"
    assert DestructiveOperation.FILE_OVERWRITE.value == "file.overwrite_existing"
    assert DestructiveOperation.PROCESS_TERMINATE.value == "process.terminate"


def test_permission_model() -> None:
    p = Permission(path="C:/Users/x/Documents", read=True, write=False)
    assert p.read is True
    assert p.write is False
    with pytest.raises(ValidationError):  # frozen
        p.read = False  # type: ignore[misc]


# =============================================================================
# Construction / loader failure modes (via the public constructor)
# =============================================================================
def test_constructor_fails_on_missing_file(tmp_path: Path) -> None:
    with pytest.raises(ConfigurationError):
        SafetyValidator(tmp_path / "does_not_exist.yaml")


def test_constructor_fails_on_invalid_yaml(tmp_path: Path) -> None:
    bad = tmp_path / "permissions.yaml"
    bad.write_text("filesystem: [unclosed\n  :::not yaml", encoding="utf-8")
    with pytest.raises(ConfigurationError):
        SafetyValidator(bad)


def test_constructor_fails_on_schema_mismatch(tmp_path: Path) -> None:
    config = _base_config()
    del config["memory"]  # missing required section
    dest = tmp_path / "permissions.yaml"
    dest.write_text(yaml.safe_dump(config), encoding="utf-8")
    with pytest.raises(ConfigurationError):
        SafetyValidator(dest)


def test_constructor_fails_on_unexpected_key(tmp_path: Path) -> None:
    config = _base_config()
    config["filesystem"]["surprise_key"] = True  # extra="forbid" must reject
    dest = tmp_path / "permissions.yaml"
    dest.write_text(yaml.safe_dump(config), encoding="utf-8")
    with pytest.raises(ConfigurationError):
        SafetyValidator(dest)


def test_constructor_fails_on_unresolved_env_var(tmp_path: Path) -> None:
    config = _base_config()
    config["filesystem"]["read_paths"] = ["${DEFINITELY_NOT_SET_VAR_XYZ}/foo"]
    dest = tmp_path / "permissions.yaml"
    dest.write_text(yaml.safe_dump(config), encoding="utf-8")
    with pytest.raises(ConfigurationError):
        SafetyValidator(dest)


def test_constructor_fails_on_non_mapping_top_level(tmp_path: Path) -> None:
    dest = tmp_path / "permissions.yaml"
    dest.write_text("- just\n- a\n- list\n", encoding="utf-8")
    with pytest.raises(ConfigurationError):
        SafetyValidator(dest)


async def test_env_var_expansion_resolves_paths(tmp_path: Path) -> None:
    """A ${USERPROFILE}-based read path resolves so a real child is allowed."""
    v = SafetyValidator(REAL_PERMISSIONS_PATH)
    target = Path(os.path.expandvars("${USERPROFILE}")) / "Documents" / "r.txt"
    result = await v.validate_file_operation("file.read", target)
    assert result.allowed is True


# =============================================================================
# Zero LLM dependency — source-level guard (belt-and-suspenders with grep)
# =============================================================================
def test_no_llm_imports_in_security_module() -> None:
    security_dir = REPO_ROOT / "aether" / "security"
    forbidden = ("llm_router", "ModelTier", "litellm", "anthropic", "openai")
    for py_file in security_dir.glob("*.py"):
        text = py_file.read_text(encoding="utf-8")
        for token in forbidden:
            assert token not in text, f"{token} found in {py_file.name}"


# =============================================================================
# Performance — SafetyValidator check p50 < 10ms, p95 < 25ms (Spec Section 13)
# =============================================================================
async def test_performance_targets(validator: SafetyValidator) -> None:
    async def timed(coro_factory: Any, iterations: int = 800) -> list[float]:
        samples: list[float] = []
        for _ in range(iterations):
            start = time.perf_counter()
            await coro_factory()
            samples.append((time.perf_counter() - start) * 1000.0)
        return samples

    target = Path(WRITE_PATHS_EXPANDED[0]) / "perf.txt"
    samples = await timed(lambda: validator.validate_app_launch("cmd.exe"))
    samples += await timed(lambda: validator.validate_file_operation("file.write", target))
    samples.sort()
    p50 = statistics.median(samples)
    p95 = samples[int(len(samples) * 0.95)]
    assert p50 < 10.0, f"p50 {p50:.3f}ms exceeds 10ms"
    assert p95 < 25.0, f"p95 {p95:.3f}ms exceeds 25ms"


# =============================================================================
# DEBT-022 — structured denial reason codes (callers branch on the code, never
# on the human-readable reason string)
# =============================================================================
async def test_denial_reason_codes_for_file_operations(tmp_path: Path) -> None:
    (tmp_path / "ok").mkdir()
    cfg = write_config(
        tmp_path,
        filesystem={
            "read_paths": [str(tmp_path / "ok")],
            "write_paths": [str(tmp_path / "ok")],
            "forbidden_paths": [str(tmp_path / "nope")],
            "max_file_size_mb": 1,
            "allow_hidden_files": False,
        },
    )
    v = SafetyValidator(cfg)

    forbidden = await v.validate_file_operation("file.read", tmp_path / "nope" / "f.txt")
    assert (forbidden.allowed, forbidden.denial_reason) == (
        False,
        DenialReason.FORBIDDEN_PATH,
    )

    unknown_op = await v.validate_file_operation("file.frobnicate", tmp_path / "ok" / "f")
    assert unknown_op.denial_reason is DenialReason.UNRECOGNIZED_OPERATION

    hidden = await v.validate_file_operation("file.read", tmp_path / "ok" / ".secret")
    assert hidden.denial_reason is DenialReason.HIDDEN_FILE

    outside = await v.validate_file_operation("file.read", tmp_path / "elsewhere" / "f.txt")
    assert outside.denial_reason is DenialReason.OUTSIDE_ALLOWED_PATHS

    big = tmp_path / "ok" / "big.bin"
    big.write_bytes(b"a" * (2 * 1024 * 1024))
    oversized = await v.validate_file_operation("file.read", big)
    assert oversized.denial_reason is DenialReason.SIZE_EXCEEDED

    small = tmp_path / "ok" / "small.txt"
    small.write_text("hi", encoding="utf-8")
    allowed = await v.validate_file_operation("file.read", small)
    assert (allowed.allowed, allowed.denial_reason) == (True, None)


async def test_denial_reason_codes_for_app_and_browser(tmp_path: Path) -> None:
    v = SafetyValidator(
        write_config(
            tmp_path,
            applications={"allowed_launch": ["notepad.exe"], "forbidden_launch": ["cmd.exe"]},
            network={"browser_automation_enabled": False, "blocked_domains": []},
        )
    )
    assert (
        await v.validate_app_launch("cmd.exe")
    ).denial_reason is DenialReason.FORBIDDEN_EXECUTABLE
    assert (
        await v.validate_app_launch("unlisted.exe")
    ).denial_reason is DenialReason.NOT_IN_ALLOWLIST
    assert (await v.validate_app_launch("")).denial_reason is DenialReason.NO_EXECUTABLE
    assert (await v.validate_app_launch("notepad.exe")).denial_reason is None
    assert (
        await v.validate_browser_action("https://example.com", "nav")
    ).denial_reason is DenialReason.BROWSER_DISABLED

    v2 = SafetyValidator(
        write_config(
            tmp_path, network={"browser_automation_enabled": True, "blocked_domains": ["evil.com"]}
        )
    )
    assert (
        await v2.validate_browser_action("https://evil.com/x", "nav")
    ).denial_reason is DenialReason.BLOCKED_DOMAIN
    assert (
        await v2.validate_browser_action("not a url at all", "nav")
    ).denial_reason is DenialReason.INVALID_DOMAIN
    assert (await v2.validate_browser_action("https://example.com", "nav")).denial_reason is None
