"""Public value objects for the Aether security enforcement layer.

SECURITY-SENSITIVE MODULE (AI_GENERATION_RULES_V2.md Section 13.1).

These are the locked data types every privileged-action validation flows
through. They carry no logic beyond validation of their own invariants:
``ValidationResult`` in particular guarantees a non-empty ``reason`` on every
instance, so no decision — allow or deny — can ever be recorded without a
stated justification (PHASE_2_TECHNICAL_SPECIFICATION.md Section 5.1;
ADR-011 Section 9, Error Message Quality Standards).
"""

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, field_validator


# StrEnum (not the prompt's `(str, Enum)`) is deliberate: codebase convention
# (see aether/tasks/models.py) and it satisfies ruff UP042; behaviour is identical
# for the `.value` comparisons is_destructive() and the loader rely on.
class DestructiveOperation(StrEnum):
    """The operations Aether treats as destructive.

    Membership here is what ``SafetyValidator.is_destructive()`` answers
    against, and what drives the ``requires_confirmation`` flag on an otherwise
    allowed file operation. The string values mirror the ``operations`` list in
    ``.aether/permissions.yaml`` exactly; this enum is the code-side source of
    truth so the validator never hardcodes the literals inline.
    """

    FILE_DELETE = "file.delete"
    FILE_MOVE = "file.move"
    FILE_OVERWRITE = "file.overwrite_existing"
    PROCESS_TERMINATE = "process.terminate"


class ValidationResult(BaseModel):
    """The outcome of a single ``SafetyValidator`` check.

    Attributes:
        allowed: Whether the action may proceed at all.
        reason: Why the action was allowed or denied. NEVER empty — a result
            without a stated reason is rejected at construction, so a silent
            allow or silent deny is impossible.
        requires_confirmation: True when an otherwise-allowed action is
            destructive and the loaded policy requires explicit user
            confirmation before it runs. Meaningless (and always False) when
            ``allowed`` is False.
    """

    model_config = ConfigDict(frozen=True)

    allowed: bool
    reason: str
    requires_confirmation: bool = False

    @field_validator("reason")
    @classmethod
    def _reason_must_not_be_empty(cls, value: str) -> str:
        """Enforce that every result explains itself (ADR-011 Section 9)."""
        if not value or not value.strip():
            raise ValueError("ValidationResult.reason must never be empty")
        return value


class Permission(BaseModel):
    """A resolved filesystem permission for a single path prefix.

    Built by ``SafetyValidator`` from the ``read_paths`` and ``write_paths``
    lists in ``.aether/permissions.yaml`` (already environment-expanded by the
    loader). A path present in both lists collapses to a single ``Permission``
    with both flags set; the validator checks the flag matching the requested
    operation's access type.

    Attributes:
        path: The permitted directory prefix (environment variables resolved).
        read: Whether read operations are allowed under this prefix.
        write: Whether write operations are allowed under this prefix.
    """

    model_config = ConfigDict(frozen=True)

    path: str
    read: bool
    write: bool
