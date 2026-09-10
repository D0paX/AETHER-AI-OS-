"""Cross-cutting security enforcement — the sole gate for every privileged
action in Aether. A peer of aether/memory/ and aether/llm/, not nested under
any single capability module.

SECURITY-SENSITIVE MODULE (AI_GENERATION_RULES_V2.md Section 13.1). Rule-based
only — contains zero LLM calls anywhere, by design.
"""

from aether.security.models import (
    DenialReason,
    DestructiveOperation,
    Permission,
    ValidationResult,
)
from aether.security.validator import SafetyValidator

__all__ = [
    "SafetyValidator",
    "ValidationResult",
    "Permission",
    "DestructiveOperation",
    "DenialReason",
]
