"""Private loader for ``.aether/permissions.yaml``.

SECURITY-SENSITIVE MODULE (AI_GENERATION_RULES_V2.md Section 13.1).

PRIVATE to ``aether.security`` — never imported anywhere else. It parses the
permissions file into a strongly-typed, frozen ``PermissionsConfig`` whose shape
matches the file's schema exactly (AETHER_V1_TECHNICAL_SPECIFICATION.md Section
14.1). Environment variables in filesystem paths (e.g. ``${USERPROFILE}``) are
resolved here, once, at load time.

Every failure mode — missing file, unreadable file, invalid YAML, a schema that
does not match, or an environment variable that cannot be resolved — is raised
as a ``ConfigurationError`` with a specific, actionable message. A bare parser
exception must never escape this module: the caller (``SafetyValidator``) treats
any load failure as fatal and refuses to construct, so the message it surfaces
has to tell the operator exactly what to fix.
"""

import os
import re
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, ConfigDict, ValidationError

from aether.core.exceptions import ConfigurationError

# Filesystem path lists that undergo environment-variable expansion. Kept in one
# place so the expansion pass and the schema never drift.
_PATH_LIST_FIELDS = ("read_paths", "write_paths", "forbidden_paths")

# Matches a leftover, unexpanded environment-variable reference (``${VAR}`` or
# ``%VAR%``). A precise pattern rather than a bare ``"%" in s`` check so a
# legitimate literal percent sign (e.g. a folder named "100% Done") is not
# mistaken for an unresolved variable.
_UNRESOLVED_VAR_RE = re.compile(r"\$\{[^}]*\}|%[A-Za-z_][A-Za-z0-9_]*%")


class FilesystemPermissions(BaseModel):
    """Filesystem access policy (paths are environment-expanded)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    read_paths: list[str]
    write_paths: list[str]
    forbidden_paths: list[str]
    max_file_size_mb: int
    allow_hidden_files: bool


class ApplicationPermissions(BaseModel):
    """Application launch policy (allowlist + explicit denylist)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    allowed_launch: list[str]
    forbidden_launch: list[str]


class NetworkPermissions(BaseModel):
    """Browser-automation and domain policy (used from Phase 3 onward)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    browser_automation_enabled: bool
    blocked_domains: list[str]


class DestructiveOperationsPermissions(BaseModel):
    """Which operations are destructive and whether they need confirmation."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    require_confirmation: bool
    operations: list[str]


class MemoryPermissions(BaseModel):
    """Memory-deletion policy."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    allow_memory_deletion: bool
    require_confirmation_bulk_delete: bool


class PermissionsConfig(BaseModel):
    """The fully-parsed, frozen permissions policy.

    Mirrors ``.aether/permissions.yaml`` one-to-one. ``extra="forbid"`` on every
    section means an unexpected or misspelled key fails loudly at load rather
    than being silently ignored — a silently-dropped ``forbidden_paths`` entry
    would be a security hole.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    version: str
    filesystem: FilesystemPermissions
    applications: ApplicationPermissions
    network: NetworkPermissions
    destructive_operations: DestructiveOperationsPermissions
    memory: MemoryPermissions


def _expand_path_lists(raw: dict[str, Any]) -> None:
    """Resolve environment variables in the filesystem path lists, in place.

    Args:
        raw: The parsed-but-unvalidated YAML mapping.

    Raises:
        ConfigurationError: If a path references an environment variable that is
            not set (``os.path.expandvars`` leaves such references untouched, so
            a leftover ``${...}`` means an unresolved variable — a
            fail-loud condition, never a path silently left literal).
    """
    filesystem = raw.get("filesystem")
    if not isinstance(filesystem, dict):
        return  # schema validation below will produce the actionable error

    for field in _PATH_LIST_FIELDS:
        values = filesystem.get(field)
        if not isinstance(values, list):
            continue
        expanded: list[str] = []
        for entry in values:
            if not isinstance(entry, str):
                continue  # schema validation will reject non-strings
            resolved = os.path.expandvars(entry)
            if _UNRESOLVED_VAR_RE.search(resolved):
                raise ConfigurationError(
                    f"Permissions file references an unresolved environment "
                    f"variable in filesystem.{field}: '{entry}'. Set the "
                    f"variable (e.g. USERPROFILE) or replace it with a literal "
                    f"path.",
                    error_code="PERMISSIONS_UNRESOLVED_ENV_VAR",
                )
            expanded.append(resolved)
        filesystem[field] = expanded


def load_permissions(path: Path) -> PermissionsConfig:
    """Load and validate ``.aether/permissions.yaml``.

    Args:
        path: Path to the permissions YAML file.

    Returns:
        The validated, frozen permissions policy with environment variables
        already resolved.

    Raises:
        ConfigurationError: If the file is missing, unreadable, not valid YAML,
            does not match the expected schema, or contains an unresolved
            environment variable. The message names the file and the specific
            problem so it is actionable without reading a stack trace.
    """
    if not path.exists():
        raise ConfigurationError(
            f"Permissions file not found at '{path}'. Aether cannot enforce "
            f"any safety policy without it; create it from the documented "
            f"schema (AETHER_V1_TECHNICAL_SPECIFICATION.md Section 14.1) before "
            f"starting.",
            error_code="PERMISSIONS_FILE_MISSING",
        )

    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ConfigurationError(
            f"Permissions file at '{path}' could not be read: {exc}.",
            error_code="PERMISSIONS_FILE_UNREADABLE",
        ) from exc

    try:
        raw = yaml.safe_load(text)
    except yaml.YAMLError as exc:
        raise ConfigurationError(
            f"Permissions file at '{path}' is not valid YAML: {exc}.",
            error_code="PERMISSIONS_INVALID_YAML",
        ) from exc

    if not isinstance(raw, dict):
        raise ConfigurationError(
            f"Permissions file at '{path}' must contain a top-level mapping of "
            f"sections (filesystem, applications, network, "
            f"destructive_operations, memory); got {type(raw).__name__}.",
            error_code="PERMISSIONS_MALFORMED",
        )

    _expand_path_lists(raw)

    try:
        return PermissionsConfig.model_validate(raw)
    except ValidationError as exc:
        raise ConfigurationError(
            f"Permissions file at '{path}' does not match the required schema: {exc}.",
            error_code="PERMISSIONS_SCHEMA_MISMATCH",
        ) from exc
