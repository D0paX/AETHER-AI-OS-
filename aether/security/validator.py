"""The Aether ``SafetyValidator`` — the sole rule-based enforcement gate.

SECURITY-SENSITIVE MODULE (AI_GENERATION_RULES_V2.md Section 13.1).

Every privileged action in Phase 2, and every phase after it, is validated here
before it runs. The enforcement is PURELY RULE-BASED: this module makes ZERO LLM
calls, by design — a direct implementation of the Critical Architecture Audit's
rejection of an LLM-based "Guardian Agent" on both cost and latency grounds
(PHASE_2_TECHNICAL_SPECIFICATION.md Sections 5.1 and 12; performance target
p50 < 10ms). The design principle throughout is FAIL-CLOSED: anything not
explicitly permitted is denied, and any uncertainty denies rather than allows.
"""

import os
import re
from pathlib import Path, PureWindowsPath
from urllib.parse import urlparse

from aether.core.logging import get_logger
from aether.security._permissions_loader import PermissionsConfig, load_permissions
from aether.security.models import (
    DenialReason,
    DestructiveOperation,
    Permission,
    ValidationResult,
)

logger = get_logger(__name__)

# The default location of the permissions policy, relative to the working
# directory Aether is launched from.
_DEFAULT_CONFIG_PATH = Path(".aether/permissions.yaml")

# Longest value rendered into the audit log before truncation, so a pathological
# path or URL cannot flood the log.
_LOG_VALUE_MAX = 256

# --- File-operation vocabulary -------------------------------------------------
# These classify an operation string by the access it needs. They are operation
# *semantics*, not user policy, so they live in code rather than permissions.yaml.
# The destructive file operations are sourced from the DestructiveOperation enum
# rather than re-typed as literals, so the two never drift.
_READ_FILE_OPERATIONS = frozenset({"file.read", "file.search"})
_NONDESTRUCTIVE_WRITE_OPERATIONS = frozenset({"file.write", "file.create"})
_DESTRUCTIVE_FILE_OPERATIONS = frozenset(
    {
        DestructiveOperation.FILE_DELETE.value,
        DestructiveOperation.FILE_MOVE.value,
        DestructiveOperation.FILE_OVERWRITE.value,
    }
)
_WRITE_FILE_OPERATIONS = _NONDESTRUCTIVE_WRITE_OPERATIONS | _DESTRUCTIVE_FILE_OPERATIONS

# Every value the DestructiveOperation enum defines — the set is_destructive()
# answers against.
_DESTRUCTIVE_VALUES = frozenset(op.value for op in DestructiveOperation)

# A well-formed host: dot-separated labels of ASCII letters/digits/hyphens, each
# 1-63 chars, not starting or ending with a hyphen. urlparse is too lenient —
# it will hand back "not a url at all" as a hostname — so the domain policy
# fails closed on anything that is not a plausible host.
_VALID_HOST_RE = re.compile(
    r"^(?=.{1,253}$)(?!-)[a-z0-9-]{1,63}(?<!-)(\.(?!-)[a-z0-9-]{1,63}(?<!-))*$"
)


def _truncate(value: str) -> str:
    """Cap a value's length for the audit log."""
    return value if len(value) <= _LOG_VALUE_MAX else value[:_LOG_VALUE_MAX] + "…"


def _normalize(path: Path) -> str:
    """Return an absolute, case-folded, separator-normalized form of a path.

    Uses ``os.path.abspath`` (which resolves ``..`` lexically, defeating simple
    traversal escapes) and ``os.path.normcase`` (case-fold + separator fold on
    Windows) so path containment can be compared as plain strings. Deliberately
    does NOT call ``resolve()``: the target may not exist yet, and following
    symlinks is a Phase 2.3 adapter concern, not this gate's.
    """
    return os.path.normcase(os.path.abspath(str(path)))


class SafetyValidator:
    """Rule-based permission gate for every privileged action.

    Loads ``.aether/permissions.yaml`` once at construction and holds it in
    memory. Has no database, Redis, or Qdrant dependency — it reads one YAML
    file. If that file cannot be loaded, construction FAILS: a validator that
    cannot read its own rules must not exist and silently allow everything.
    """

    def __init__(self, config_path: Path = _DEFAULT_CONFIG_PATH) -> None:
        """Load and index the permissions policy.

        Args:
            config_path: Path to the permissions YAML. Defaults to
                ``.aether/permissions.yaml`` relative to the launch directory.

        Raises:
            ConfigurationError: If the policy file is missing or malformed. The
                validator refuses to construct rather than come up permissive.
        """
        self._config: PermissionsConfig = load_permissions(config_path)
        fs = self._config.filesystem

        # Merge read_paths and write_paths into per-prefix Permission records.
        # A path in both lists becomes one Permission with both flags set.
        read_norm = {_normalize(Path(p)): p for p in fs.read_paths}
        write_norm = {_normalize(Path(p)): p for p in fs.write_paths}
        self._permissions: list[Permission] = [
            Permission(
                path=read_norm.get(key) or write_norm[key],
                read=key in read_norm,
                write=key in write_norm,
            )
            for key in set(read_norm) | set(write_norm)
        ]
        self._forbidden_paths: list[Path] = [Path(p) for p in fs.forbidden_paths]
        self._max_file_size_bytes: int = fs.max_file_size_mb * 1024 * 1024
        self._allow_hidden: bool = fs.allow_hidden_files

        # Executable policy: fold to lower-cased base names once, up front.
        apps = self._config.applications
        self._forbidden_launch: frozenset[str] = frozenset(e.lower() for e in apps.forbidden_launch)
        self._allowed_launch: frozenset[str] = frozenset(e.lower() for e in apps.allowed_launch)

        # Network policy.
        self._browser_enabled: bool = self._config.network.browser_automation_enabled
        self._blocked_domains: frozenset[str] = frozenset(
            d.lower() for d in self._config.network.blocked_domains
        )

        # Whether destructive operations require confirmation.
        self._require_confirmation: bool = self._config.destructive_operations.require_confirmation

        logger.info(
            "security.validator.initialized",
            config_path=_truncate(str(config_path)),
            read_write_prefixes=len(self._permissions),
            forbidden_paths=len(self._forbidden_paths),
            forbidden_launch=len(self._forbidden_launch),
            allowed_launch=len(self._allowed_launch),
        )

    @property
    def max_file_size_bytes(self) -> int:
        """The configured ``max_file_size_mb`` in bytes (read-only).

        Exposed so a caller that must *truncate* an oversized read to the policy
        limit (M2.4 read_file) can honor the same number this validator enforces,
        rather than hardcoding it or re-reading the config.
        """
        return self._max_file_size_bytes

    # -- decision helper --------------------------------------------------------

    def _decide(
        self,
        event: str,
        *,
        allowed: bool,
        reason: str,
        requires_confirmation: bool = False,
        denial_reason: DenialReason | None = None,
        context: dict[str, str],
    ) -> ValidationResult:
        """Build a ValidationResult and write the ADR-010 audit-trail entry."""
        result = ValidationResult(
            allowed=allowed,
            reason=reason,
            requires_confirmation=requires_confirmation,
            denial_reason=denial_reason,
        )
        logger.info(
            event,
            allowed=result.allowed,
            requires_confirmation=result.requires_confirmation,
            denial_reason=result.denial_reason,
            reason=result.reason,
            **{key: _truncate(str(value)) for key, value in context.items()},
        )
        return result

    # -- path helpers -----------------------------------------------------------

    @staticmethod
    def _is_within(target: Path, base: Path) -> bool:
        """True if ``target`` is ``base`` itself or a descendant of it."""
        target_n = _normalize(target)
        base_n = _normalize(base)
        if target_n == base_n:
            return True
        base_prefix = base_n if base_n.endswith(os.sep) else base_n + os.sep
        return target_n.startswith(base_prefix)

    @staticmethod
    def _is_hidden(path: Path) -> bool:
        """True if any component of the path is a dotfile-style hidden name.

        Uses the cross-platform dotfile convention (a component beginning with
        ``.``), which is checkable whether or not the file exists. ``.`` and
        ``..`` traversal segments are not treated as hidden.
        """
        return any(
            part.startswith(".") and part not in (".", "..")
            for part in Path(os.path.abspath(str(path))).parts
        )

    # -- public interface -------------------------------------------------------

    async def validate_file_operation(self, operation: str, path: Path) -> ValidationResult:
        """Validate a filesystem operation against the loaded policy.

        Order of checks (deny takes priority over allow): forbidden paths first;
        then the operation must be a recognized read or write operation
        (unrecognized operations are denied, fail-closed); then hidden-file
        policy; then the path must fall under a permitted read or write prefix
        matching the operation's access type (no match denies, fail-closed);
        then the file-size cap where applicable. A permitted destructive
        operation is allowed but flagged ``requires_confirmation=True`` when the
        policy requires confirmation — the confirmation itself is enforced by
        the caller, not here.

        Args:
            operation: The operation identifier, e.g. ``"file.read"``,
                ``"file.write"``, or a ``DestructiveOperation`` value.
            path: The target filesystem path.

        Returns:
            A ValidationResult; ``reason`` is always populated.
        """
        event = "security.file_operation"
        ctx = {"operation": operation, "path": str(path)}

        for forbidden in self._forbidden_paths:
            if self._is_within(path, forbidden):
                return self._decide(
                    event,
                    allowed=False,
                    reason=(f"Denied: '{path}' is within forbidden path '{forbidden}'."),
                    denial_reason=DenialReason.FORBIDDEN_PATH,
                    context=ctx,
                )

        is_read = operation in _READ_FILE_OPERATIONS
        is_write = operation in _WRITE_FILE_OPERATIONS
        if not (is_read or is_write):
            return self._decide(
                event,
                allowed=False,
                reason=(
                    f"Denied: '{operation}' is not a recognized file operation "
                    f"(fail-closed; expected one of "
                    f"{sorted(_READ_FILE_OPERATIONS | _WRITE_FILE_OPERATIONS)})."
                ),
                denial_reason=DenialReason.UNRECOGNIZED_OPERATION,
                context=ctx,
            )

        if not self._allow_hidden and self._is_hidden(path):
            return self._decide(
                event,
                allowed=False,
                reason=(f"Denied: '{path}' is a hidden path and allow_hidden_files is false."),
                denial_reason=DenialReason.HIDDEN_FILE,
                context=ctx,
            )

        access = "read" if is_read else "write"
        permitted = any(
            self._is_within(path, Path(perm.path))
            and ((is_read and perm.read) or (is_write and perm.write))
            for perm in self._permissions
        )
        if not permitted:
            return self._decide(
                event,
                allowed=False,
                reason=(
                    f"Denied: '{path}' is not within any permitted {access} "
                    f"path (fail-closed default)."
                ),
                denial_reason=DenialReason.OUTSIDE_ALLOWED_PATHS,
                context=ctx,
            )

        if self._exceeds_size_limit(path):
            return self._decide(
                event,
                allowed=False,
                reason=(
                    f"Denied: '{path}' exceeds the maximum file size of "
                    f"{self._config.filesystem.max_file_size_mb} MB."
                ),
                denial_reason=DenialReason.SIZE_EXCEEDED,
                context=ctx,
            )

        requires_confirmation = self._require_confirmation and self.is_destructive(operation)
        reason = f"Allowed: '{path}' permitted for {access} operation '{operation}'."
        if requires_confirmation:
            reason += " Destructive operation requires user confirmation."
        return self._decide(
            event,
            allowed=True,
            reason=reason,
            requires_confirmation=requires_confirmation,
            context=ctx,
        )

    def _exceeds_size_limit(self, path: Path) -> bool:
        """True if ``path`` is an existing file larger than the policy cap.

        The cap only applies to a file that already exists; a not-yet-created
        target (e.g. a new write) has no size to check.
        """
        try:
            if not path.is_file():
                return False
            return path.stat().st_size > self._max_file_size_bytes
        except OSError:
            # Cannot stat — treat as within limit; the path-permission and
            # forbidden checks already gate access. Size is a secondary guard.
            return False

    async def validate_app_launch(self, executable: str) -> ValidationResult:
        """Validate an application launch against the policy.

        The executable is reduced to its lower-cased base name, so
        ``"CMD.EXE"``, ``"cmd.exe"``, and ``"C:\\Windows\\System32\\cmd.exe"``
        all resolve to the same policy entry ``"cmd.exe"``. The forbidden list
        is checked first; then the allow list. FAIL-CLOSED DEFAULT: an
        executable in neither list is DENIED — this is an allowlist, not merely
        a denylist, so an unlisted executable is never permitted by omission.

        Args:
            executable: An executable name or full path.

        Returns:
            A ValidationResult; ``reason`` is always populated.
        """
        event = "security.app_launch"
        base = PureWindowsPath(executable).name.lower() if executable else ""

        if not base:
            return self._decide(
                event,
                allowed=False,
                reason="Denied: no executable name given (fail-closed).",
                denial_reason=DenialReason.NO_EXECUTABLE,
                context={"executable": executable},
            )

        if base in self._forbidden_launch:
            return self._decide(
                event,
                allowed=False,
                reason=f"Denied: '{base}' is in the forbidden_launch list.",
                denial_reason=DenialReason.FORBIDDEN_EXECUTABLE,
                context={"executable": executable},
            )

        if base in self._allowed_launch:
            return self._decide(
                event,
                allowed=True,
                reason=f"Allowed: '{base}' is in the allowed_launch list.",
                context={"executable": executable},
            )

        return self._decide(
            event,
            allowed=False,
            reason=(
                f"Denied: '{base}' is not in the allowed_launch list "
                f"(fail-closed default; unlisted executables are denied)."
            ),
            denial_reason=DenialReason.NOT_IN_ALLOWLIST,
            context={"executable": executable},
        )

    async def validate_browser_action(self, url: str, action: str) -> ValidationResult:
        """Validate a browser-automation action against the policy.

        Denies when browser automation is disabled, when no domain can be parsed
        from the URL (fail-closed), or when the domain matches (exactly or as a
        subdomain of) any entry in ``blocked_domains``. Otherwise allows.

        Fully implemented and tested now for interface stability; no Phase 2
        code path calls it (it is exercised beginning in Phase 3).

        Args:
            url: The target URL.
            action: The browser action being requested (recorded for the audit
                trail; the decision is domain-based).

        Returns:
            A ValidationResult; ``reason`` is always populated.
        """
        event = "security.browser_action"
        ctx = {"url": url, "action": action}

        if not self._browser_enabled:
            return self._decide(
                event,
                allowed=False,
                reason="Denied: browser automation is disabled by policy.",
                denial_reason=DenialReason.BROWSER_DISABLED,
                context=ctx,
            )

        # Ensure urlparse sees an authority even for a bare "example.com/x".
        parsed = urlparse(url if "://" in url else f"//{url}")
        host = (parsed.hostname or "").lower()
        if not host or not _VALID_HOST_RE.match(host):
            return self._decide(
                event,
                allowed=False,
                reason=f"Denied: '{url}' has no parseable, well-formed domain (fail-closed).",
                denial_reason=DenialReason.INVALID_DOMAIN,
                context=ctx,
            )

        for blocked in self._blocked_domains:
            if host == blocked or host.endswith(f".{blocked}"):
                return self._decide(
                    event,
                    allowed=False,
                    reason=f"Denied: domain '{host}' matches blocked domain '{blocked}'.",
                    denial_reason=DenialReason.BLOCKED_DOMAIN,
                    context=ctx,
                )

        return self._decide(
            event,
            allowed=True,
            reason=(f"Allowed: domain '{host}' is not blocked and browser automation is enabled."),
            context=ctx,
        )

    def is_destructive(self, action: str) -> bool:
        """Return whether ``action`` is a destructive operation.

        Synchronous — a pure membership test against the DestructiveOperation
        values, requiring no I/O.

        Args:
            action: An operation identifier.

        Returns:
            True if ``action`` matches a ``DestructiveOperation`` value.
        """
        return action in _DESTRUCTIVE_VALUES
