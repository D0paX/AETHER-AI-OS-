"""PC control — Aether's gated interface to host-machine actions.

SECURITY-SENSITIVE MODULE (AI_GENERATION_RULES_V2.md Section 13.1). Every action
is taken through ``PCControlAPI.execute_action``, which gates launches through
``SafetyValidator``. This milestone (M2.3) exports application control only;
``SystemStats`` and file-related types are added by M2.4/M2.5, extending this
same file.
"""

from aether.pc_control.api import (
    ActionResult,
    ApplicationInfo,
    PCAction,
    PCControlAPI,
)

__all__ = [
    "PCControlAPI",
    "PCAction",
    "ActionResult",
    "ApplicationInfo",
]
