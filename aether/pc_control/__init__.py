"""PC control — Aether's gated interface to host-machine actions.

SECURITY-SENSITIVE MODULE (AI_GENERATION_RULES_V2.md Section 13.1). Every action
is taken through ``PCControlAPI.execute_action`` (apps) or the file methods,
each gated by ``SafetyValidator``. This module exports application control
(M2.3) and file operations (M2.4); ``SystemStats`` is added by M2.5, extending
this same file.
"""

from aether.pc_control._control.file_ops import (
    FileContent,
    FileInfo,
    FileSearchFilter,
)
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
    "FileSearchFilter",
    "FileInfo",
    "FileContent",
]
