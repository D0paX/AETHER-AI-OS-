# PHASE 2 TECHNICAL SPECIFICATION
### docs/phases/phase-2/PHASE_2_TECHNICAL_SPECIFICATION.md
### PC Control — "Operator"

---

**Date:** 2025-11-15
**Status:** APPROVED — IMPLEMENTATION SOURCE OF TRUTH FOR PHASE 2
**Classification:** Phase Architecture — Extends V1_TECHNICAL_SPECIFICATION.md
**Authority:** Chief AI Architect / Principal Systems Engineer
**Governed By:** Master Blueprint, V1 Foundation Architecture Decision,
V1 Technical Specification, AETHER_INTELLIGENCE_ARCHITECTURE.md, ADR-010,
ADR-011, AI_GENERATION_RULES_V2.md, AI_SKILLS_INTEGRATION.md,
AETHER_PHASE_EXECUTION_WORKFLOW.md, AETHER_DEFINITION_OF_DONE.md
**Produced At:** AETHER_PHASE_EXECUTION_WORKFLOW.md Step 2 (Phase
Initialization)

---

## DOCUMENT REVIEW RECORD

Before this specification was drafted, the following were reviewed in
full: the Master Blueprint, the Critical Architecture Audit, V1
Foundation Architecture Decision, V1 Technical Specification, ADR-010,
ADR-011, AI_GENERATION_RULES_V2.md, AI_SKILLS_INTEGRATION.md,
AETHER_INTELLIGENCE_ARCHITECTURE.md, AETHER_PHASE_EXECUTION_WORKFLOW.md,
AETHER_DEFINITION_OF_DONE.md, and PHASE_1_FOUNDATION_IMPLEMENTATION_PLAN.md.

Two findings from that review affect how this document is framed:

**No standalone Phase 1 Technical Specification exists, by design.**
AETHER_PHASE_EXECUTION_WORKFLOW.md Step 2 makes a phase's own Technical
Specification conditional: it is produced only if the phase introduces
architecture beyond V1_TECHNICAL_SPECIFICATION.md. Phase 1 *was* the
foundation that document specifies, so it correctly never needed a
separate one. Phase 2 does introduce genuinely new architectural
surface — a security-validation module and a privileged-action module
neither exist yet — so this document is produced under that same rule,
this time because the condition is met.

**Phase 1's four closure reports do not exist, by explicit developer
authorization.** The developer's own statement, "Phase 1 has been
successfully completed," was accepted as satisfying Non-Bypassable Rule
NB-6 of AETHER_DEFINITION_OF_DONE.md in place of the formal
`PHASE_1_GO_NO_GO_REPORT.md`. This exception is recorded in
AETHER_PHASE_EXECUTION_WORKFLOW.md Section 6.1, is specific to Phase 1,
and does not recur. This document proceeds on the basis of that closure.

---

## TABLE OF CONTENTS

1. [Scope](#1-scope)
2. [Objectives](#2-objectives)
3. [Architecture](#3-architecture)
4. [New Modules](#4-new-modules)
5. [Module Interfaces](#5-module-interfaces)
6. [API Contracts](#6-api-contracts)
7. [Event Contracts](#7-event-contracts)
8. [Database Changes](#8-database-changes)
9. [Memory Changes](#9-memory-changes)
10. [Runtime Changes](#10-runtime-changes)
    - 10.3 [Capability Registry](#103-capability-registry)
    - 10.4 [Concurrent Task Execution Model](#104-concurrent-task-execution-model)
    - 10.5 [Agent Health Interface](#105-agent-health-interface)
    - 10.6 [Runtime Telemetry](#106-runtime-telemetry)
11. [AI Skill Requirements](#11-ai-skill-requirements)
12. [Security Requirements](#12-security-requirements)
13. [Performance Requirements](#13-performance-requirements)
14. [Testing Requirements](#14-testing-requirements)
15. [Documentation Requirements](#15-documentation-requirements)
16. [Risks](#16-risks)
17. [Dependencies](#17-dependencies)
18. [Deliverables](#18-deliverables)
19. [Acceptance Criteria](#19-acceptance-criteria)

---

## 1. SCOPE

### 1.1 What Phase 2 Grants Aether

The ability to observe and act on the host Windows machine: launching,
closing, and focusing applications; performing file operations (search,
read, move, organize); and monitoring system state (CPU, memory, disk,
process list). This is the first phase in which Aether's actions leave
the boundary of conversation and memory and begin to affect the user's
actual computer.

### 1.2 What This Document Extends, Not Duplicates

Phase 2 does not redefine anything Phase 1 already locked. It builds on:
- The Structured Modular Monolith architecture (V1 Foundation Architecture
  Decision, Section 7, Final Decision).
- The `MemoryAPI`, `LLMRouter`, `BaseTool`, `BaseAgent`, and `AetherEvent`
  contracts (V1_TECHNICAL_SPECIFICATION.md Sections 2.4, 2.5, 2.6, 2.7,
  locked and unchanged).
- The `.aether/permissions.yaml` schema and the `SafetyValidator` interface
  already specified — but not yet implemented — in
  V1_TECHNICAL_SPECIFICATION.md Section 14.1, and already present as a
  real file in the repository since Milestone M1.0.
- The PC Control Agent and File System Agent already fully defined in
  AETHER_INTELLIGENCE_ARCHITECTURE.md Section 7, Group B — this
  specification implements those agent roles; it does not redesign them.
- The scheduled-extraction pattern for PC Control already described in
  V1 Foundation Architecture Decision Sections 3.7 and 4.1.

### 1.3 Explicitly Out of Scope

- Browser automation (Phase 3).
- Coding assistance (Phase 4).
- Multi-agent orchestration or LangGraph adoption (Phase 5) — Phase 2's
  two new agents use the exact same sequential `BaseAgent` pattern Phase 1
  already built.
- Any Windows registry modification, service start/stop, driver
  interaction, or network configuration change. These are meaningfully
  higher-risk than file and application control and are deliberately
  excluded from this phase's tool surface, not merely undocumented.
- Any destructive operation without the confirmation gate. Phase 2
  introduces no new bypass of ADR-010's Level 4/5 process.
- Migrating the LLM Router from `ModelTier` to the full Capability
  Registry defined in AETHER_INTELLIGENCE_ARCHITECTURE.md Section 9. That
  migration belongs to later phases as the agent roster diversifies
  further; Phase 2's new agents use `ModelTier` exactly as Phase 1's
  `ConversationAgent` does.

---

## 2. OBJECTIVES

1. Implement `SafetyValidator` as a real, tested, rule-based enforcement
   class — zero LLM calls anywhere in its validation path, per the
   Critical Architecture Audit's explicit rejection of an LLM-based
   "Guardian Agent" (Critical Audit, Section 1.3).
2. Implement the PC Control module: application control, file operations,
   and system monitoring, behind a single locked `PCControlAPI`.
3. Perform the scheduled extraction of PC Control into an isolated
   service process, once the module has real functionality to isolate.
4. Migrate the primary datastore from SQLite to PostgreSQL, per the
   migration procedure already documented in V1_TECHNICAL_SPECIFICATION.md
   Section 3.3.
5. Introduce `FileAgent` and `SystemAgent`, both conforming exactly to
   Phase 1's locked `BaseAgent` interface — no interface changes.
6. Extend the tool suite with a permission-gated PC control tool set,
   registered through the existing `ToolRegistry` — no registry interface
   changes.
7. Pass Phase 2's defining test: the PC Control Trust Test (Section 19.2).

---

## 3. ARCHITECTURE

### 3.1 Process Topology at Phase 2 Close

```
┌──────────────────────────────────────────────────────────────────────┐
│  HOST MACHINE (Windows PC)                                           │
│                                                                      │
│  PROCESS: aether-core            PROCESS: aether-voice               │
│  (unchanged from Phase 1,        (unchanged from Phase 1)            │
│   plus two new agents and                                            │
│   two new modules)                                                    │
│         │                                                             │
│         │  HTTP (post-extraction)                                     │
│         ▼                                                             │
│  PROCESS: aether-pc-control      (NEW — Docker container,             │
│  (extracted mid-phase,            sandboxed, no direct memory/        │
│   see Section 3.3)                 database access, per the same      │
│                                     isolation model already applied    │
│                                     to the browser agent design in     │
│                                     V1 Foundation Architecture          │
│                                     Section 3.6)                       │
│                                                                      │
│  DOCKER SERVICES: Redis, Qdrant, PostgreSQL (NEW — replaces SQLite)  │
└──────────────────────────────────────────────────────────────────────┘
```

### 3.2 Module-First, Then Extract

Consistent with V1 Foundation Architecture Decision Section 4.1, PC
Control is implemented first as an in-process module
(`aether/pc_control/`) with a public API designed as if it were already a
service. Only once that module has working, tested functionality is it
extracted into `services/pc-control/`. This is a two-stage phase
internally, not two separate phases:

**Stage A (module):** `aether/pc_control/api.py` is called directly, via
in-process function calls, by `FileAgent` and `SystemAgent`.

**Stage B (extraction):** `PCControlAPI`'s implementation is wrapped in
FastAPI inside a new sandboxed container; a `PCControlClient` is created
in `aether-core` that calls the new HTTP API. Per the extraction
mechanism already defined, this is a relocation, not a rewrite — the
calling agents change zero lines of code, because they already call
through the `PCControlAPI` interface, not its implementation.

### 3.3 Why Extraction Happens Within Phase 2

PC control handles privileged operations — file deletion, application
termination. Isolating it in a sandboxed container limits the blast
radius if any single component is compromised, exactly as the browser
agent is already isolated for the analogous reason. V1 Foundation
Architecture Decision Section 4 (Subsystem Extraction Table) already
schedules this extraction "at start of Phase 2" as a deliberate,
proactive decision — not a reactive one triggered by a measured
threshold. This specification schedules the extraction as the final
milestone of Phase 2, once Stage A's functionality exists to extract.

---

## 4. NEW MODULES

### 4.1 `aether/security/` — NEW

A cross-cutting module, not nested under `pc_control/`, because
`SafetyValidator` is used by PC Control now and will be used by Browser
Automation in Phase 3 (`validate_browser_action()` is already part of its
locked interface, per V1_TECHNICAL_SPECIFICATION.md Section 14.1). Placing
it under `pc_control/` would force Phase 3 to import across a sibling
module's boundary — the same anti-pattern the Constitution forbids
elsewhere. `aether/security/` is a peer of `aether/memory/` and
`aether/llm/`, not a child of `aether/pc_control/`.

```
aether/security/
  __init__.py          — exports: SafetyValidator, ValidationResult, Permission
  validator.py          — PUBLIC: SafetyValidator (the sole enforcement interface)
  _permissions_loader.py — PRIVATE: loads and parses .aether/permissions.yaml
  models.py              — PUBLIC: ValidationResult, Permission, DestructiveOperation
```

### 4.2 `aether/pc_control/` — NEW

```
aether/pc_control/
  __init__.py            — exports: PCControlAPI, PCAction, ActionResult,
                             ApplicationInfo, SystemStats, FileInfo
  api.py                  — PUBLIC: PCControlAPI (the sole interface for
                             everything in this module)
  _control/
    app_control.py         — PRIVATE: application launch/close/focus
    file_ops.py             — PRIVATE: file search/read/move/organize
    system_monitor.py        — PRIVATE: CPU/memory/disk/network/process stats
  _adapters/
    windows.py                — PRIVATE: Windows-specific implementation
                                  (pywinauto, pyautogui), per
                                  V1_TECHNICAL_SPECIFICATION.md Section 7.7
```

### 4.3 `aether/agents/_implementations/` — EXTENDED

```
file_agent.py     — NEW: FileAgent(BaseAgent)
system_agent.py    — NEW: SystemAgent(BaseAgent)
```

### 4.4 `aether/tools/_implementations/` — EXTENDED

```
pc_control_tools.py — NEW: launch_app, close_app, focus_app,
                       list_running_apps, search_files, read_file_content,
                       move_file, get_system_stats
```

### 4.5 `services/pc-control/` — NEW (post-extraction, Stage B)

```
services/pc-control/
  __init__.py
  main.py       — process entry point
  server.py      — FastAPI wrapper around PCControlAPI
```

---

## 5. MODULE INTERFACES

All method signatures below are locked upon implementation, per the same
discipline already applied to `MemoryAPI` and `LLMRouter` in Phase 1 —
changes after this phase require the Constitutional Amendment process
(ADR-010 Section 16.4) if the change is breaking.

### 5.1 `SafetyValidator` (carried forward from V1_TECHNICAL_SPECIFICATION.md Section 14.1, now implemented)

```
validate_file_operation(operation: str, path: Path) -> ValidationResult
validate_app_launch(executable: str) -> ValidationResult
validate_browser_action(url: str, action: str) -> ValidationResult
  (interface defined now for stability; not exercised until Phase 3)
is_destructive(action: str) -> bool
```

`ValidationResult` carries, at minimum: `allowed: bool`, `reason: str`,
and `requires_confirmation: bool`. Every field is populated on every
call — a validator that returns `allowed=True` with no reason is not
acceptable per ADR-011 Section 9 (Error Message Quality Standards).

### 5.2 `PCControlAPI`

```
execute_action(action: PCAction, confirmation_token: str | None) -> ActionResult
  — the single entry point for every PC control action; internally
    calls SafetyValidator before dispatching to any _control/ submodule;
    no code path bypasses this call
list_applications() -> list[ApplicationInfo]
get_system_state() -> SystemStats
search_files(query: str, root: Path, filters: FileSearchFilter) -> list[FileInfo]
read_file(path: Path) -> FileContent
  — validated against permissions before the file is opened
```

### 5.3 `FileAgent` and `SystemAgent`

Both extend `BaseAgent` exactly as specified in
V1_TECHNICAL_SPECIFICATION.md Section 2.7 — no changes to `AgentTask`,
`AgentContext`, or `AgentResult`. Both use `self._invoke_tool()` for every
PC control action; neither imports `PCControlAPI` or `SafetyValidator`
directly, mirroring exactly how `ConversationAgent` never imports
`MemoryAPI` directly and instead uses `self._recall()` / `self._remember()`.

```
FileAgent:
  name = "file_agent"
  llm_tier = ModelTier.CHEAP
  allowed_tools = ["search_files", "read_file_content", "move_file"]

SystemAgent:
  name = "system_agent"
  llm_tier = ModelTier.CHEAP
  allowed_tools = ["launch_app", "close_app", "focus_app",
                    "list_running_apps", "get_system_stats"]
```

`ModelTier.CHEAP` is the deliberate choice for both: file-operation and
system-monitoring interpretation is more mechanical and less nuanced than
open conversation, and does not warrant `STANDARD` tier's cost. This is a
proposed default, validated like any other design decision through
Phase 2's own testing, not asserted as immutable.

---

## 6. API CONTRACTS

### 6.1 `PCControlAPI` (Stage A — internal Python interface)

Consumed directly by `FileAgent` and `SystemAgent` via in-process calls,
identical in pattern to how Phase 1 agents call `MemoryAPI`.

### 6.2 PC Control Service REST API (Stage B — post-extraction)

Binds to `127.0.0.1`, following the exact pattern already established for
the voice service (V1_TECHNICAL_SPECIFICATION.md Section 6.3):

```
POST /execute
  Body: { "action": PCAction, "confirmation_token": string | null }
  Response: ActionResult

GET /applications
  Response: list[ApplicationInfo]

GET /system-state
  Response: SystemStats

POST /files/search
  Body: { "query": string, "root": string, "filters": FileSearchFilter }
  Response: list[FileInfo]

GET /health
  Response: { "status": "healthy" | "degraded", "version": string }
```

A `PCControlClient` in `aether-core` implements the exact same method
signatures as `PCControlAPI` (Section 5.2), calling this REST API
internally. `FileAgent` and `SystemAgent` do not know or care which
implementation is active — this is the same replaceable-implementation
discipline already applied throughout the Constitution.

---

## 7. EVENT CONTRACTS

New event types, following the `domain.entity.action` naming convention
and the locked `AetherEvent` envelope from V1_TECHNICAL_SPECIFICATION.md
Section 2.3 exactly — no envelope changes.

```
pc_control.action.executed      schema_version: "1.0"
{
    "action_type":       str,
    "success":           bool,
    "confirmation_used":  bool,
    "duration_ms":         int
}

pc_control.action.denied        schema_version: "1.0"
{
    "action_type":    str,
    "reason":          str,
    "requested_by":     str    (agent name)
}

pc_control.app.launched         schema_version: "1.0"
{
    "executable":   str,
    "process_id":    int | None
}

pc_control.app.closed           schema_version: "1.0"
{
    "executable":  str
}

pc_control.file.operation_completed   schema_version: "1.0"
{
    "operation":     str,   ("search" | "read" | "move")
    "path":           str,
    "success":         bool
}

system.stats.snapshot           schema_version: "1.0"
{
    "cpu_percent":      float,
    "memory_percent":    float,
    "disk_percent":       float,
    "process_count":       int
}
```

`pc_control.action.denied` is emitted every time `SafetyValidator` blocks
an action — this event type did not need to exist in Phase 1, since
nothing yet made privileged requests. Its existence from Phase 2 forward
is what makes the audit trail required by ADR-010 actually queryable, not
just theoretically present in logs.

---

## 8. DATABASE CHANGES

### 8.1 SQLite to PostgreSQL Migration

Per the migration procedure already documented in
V1_TECHNICAL_SPECIFICATION.md Section 3.3: add `asyncpg`, set
`database.url` in `config/local.yaml` to the PostgreSQL connection string,
run `alembic upgrade head` against PostgreSQL using the same migration
scripts, export and validate SQLite data, cut over, archive the SQLite
file rather than delete it. A full, verified backup (ADR-010 Section 4) is
mandatory immediately before this migration begins — this is a Level 4
Potentially Destructive operation under ADR-010 Section 2 and follows that
section's requirements in full.

### 8.2 No New Tables Required for Audit Logging

The `tool_executions` table (V1_TECHNICAL_SPECIFICATION.md Section 3.2)
already captures every tool invocation generically, including every new
PC control tool this phase introduces — `success: bool` and
`error_message` already accommodate a denied action being logged as
`success=False, error_message="Permission denied: <reason>"`. No new
table is introduced for this purpose. This is a deliberate simplification:
Phase 2 extends by reusing an existing, correctly-generic table rather
than duplicating its function.

### 8.3 `system_kv` Additions

```
'aether.database_backend'  → '"postgresql"'   (updated from '"sqlite"')
'aether.pc_control_enabled' → 'true'
```

---

## 9. MEMORY CHANGES

No schema change to `MemoryType`, `MemoryRecord`, or `ContextPackage` —
all remain exactly as locked in V1_TECHNICAL_SPECIFICATION.md Section 2.5.

**New calling pattern, not new schema:** `FileAgent` and `SystemAgent`
call `self._remember()` for any action representing a meaningful state
change to the user's environment — a file moved, an application launched
at the user's request — using `MemoryType.EPISODE`, exactly as
`ConversationAgent` already does for conversation turns
(V1_TECHNICAL_SPECIFICATION.md Section 8.2, Step 6). This is behavior
extension through the existing interface, not an interface change.

---

## 10. RUNTIME CHANGES

### 10.1 Kernel Initialization Sequence

`aether/core/kernel.py`'s existing eleven-step sequence
(V1_TECHNICAL_SPECIFICATION.md Section 8, Milestone M1.7 Step 4) gains
insertions at the correct dependency points — no reordering of existing
steps:

```
... (existing steps 1–8 unchanged) ...
8a. Initialize SafetyValidator (loads .aether/permissions.yaml)
8b. Initialize PCControlAPI (Stage A) or PCControlClient (Stage B,
     post-extraction)
8c. Register new tools: launch_app, close_app, focus_app,
     list_running_apps, search_files, read_file_content, move_file,
     get_system_stats
... (existing step 9, ToolRegistry completion) ...
9a. Register FileAgent and SystemAgent with AgentRuntime
... (existing steps 10–11 unchanged) ...
```

### 10.2 New Process (Post-Extraction)

`services/pc-control/`, added to `infrastructure/scripts/start.ps1`'s
startup sequence after `aether-core` and `aether-voice`, following the
identical health-check-polling pattern already used for both
(V1_TECHNICAL_SPECIFICATION.md Section 15.2, Milestone M1.10 Step 4).

### 10.3 Capability Registry

**Relationship to the existing architecture.** Section 1.3 of this
specification scopes the full migration of the LLM Router from
`ModelTier` to the multi-engine Capability Registry conceptually defined
in AETHER_INTELLIGENCE_ARCHITECTURE.md Section 9 to a later phase, as that
document's own Roadmap (Section 15, Stage 2) already schedules. What
follows does not move that migration forward. It introduces the
Capability Registry's **declarative schema** now — the structure every
agent uses to state what it needs — while its **resolution logic** for
Phase 2 continues to resolve every capability directly onto the existing,
locked `ModelTier` enum. `FileAgent` and `SystemAgent` (Section 5.3) keep
their `llm_tier = ModelTier.CHEAP` declaration exactly as already
specified; the Capability Registry gives that declaration a name and a
richer set of metadata without changing what it resolves to. The
multi-engine resolution AETHER_INTELLIGENCE_ARCHITECTURE.md Section 10
describes activates when that document's own Roadmap says it does — this
section lays the schema those future engine assignments will populate.

**The schema.** Every capability the system can request is defined by:

| Field | Purpose |
|---|---|
| Capability Name | Unique string identifier, e.g. `"file_operation_reasoning"` |
| Capability Description | Human-readable statement of what this capability does |
| Required Engine Type | The category of engine needed (e.g., "instruction-following LLM, tool-calling capable") — maps conceptually to the named engines in AETHER_INTELLIGENCE_ARCHITECTURE.md Section 9.2 |
| Preferred Engine | For Phase 2: a `ModelTier` value. For Phase 5+: a named engine per AETHER_INTELLIGENCE_ARCHITECTURE.md Section 10 |
| Minimum Supported Engine | The lowest-capability engine that still fulfills this capability adequately |
| Fallback Engine | What to use if Preferred is unavailable — for Phase 2, resolves through the existing `LLMRouter` fallback chain (STANDARD → CHEAP → LOCAL, V1_TECHNICAL_SPECIFICATION.md Section 2.4) |
| Parallel Execution Support | Boolean — whether multiple simultaneous requests for this capability can be served concurrently |
| Estimated Resource Cost | Low / Medium / High — a rough compute-cost classification |
| Priority Class | INTERACTIVE / HIGH / NORMAL / LOW / IDLE — reuses the exact scale already defined in AETHER_INTELLIGENCE_ARCHITECTURE.md Section 5.3, not a new scale |
| Scheduling Requirements | Free-form notes on any special scheduling constraints |

**Phase 2's registered capabilities:**

| Capability | Description | Required Engine Type | Preferred | Minimum | Fallback | Parallel | Cost | Priority | Scheduling Notes |
|---|---|---|---|---|---|---|---|---|---|
| `conversational_response` | General dialogue and tool orchestration for direct user interaction | Instruction-following LLM, tool-calling capable | `ModelTier.STANDARD` | `ModelTier.CHEAP` | `ModelTier.LOCAL` | No (Phase 2) | Medium | INTERACTIVE | Always preempts queued background capability requests |
| `file_operation_reasoning` | Interpreting file-related requests and selecting the correct operation and target | Instruction-following LLM, moderate reasoning | `ModelTier.CHEAP` | `ModelTier.LOCAL` | `ModelTier.LOCAL` | No (Phase 2); Yes (Phase 5) | Low | NORMAL (HIGH if requested mid-conversation) | Must pass `SafetyValidator.validate_file_operation()` before resource allocation is final |
| `system_monitoring_interpretation` | Interpreting system-state queries and formatting results | Instruction-following LLM, low reasoning depth | `ModelTier.CHEAP` | `ModelTier.LOCAL` | `ModelTier.LOCAL` | No (Phase 2); Yes (Phase 5) | Low | NORMAL | None beyond standard queuing |

**Interface (schema-level, no implementation):**

```
CapabilityRegistry:
  register(capability: CapabilityDefinition) -> None
  resolve(capability_name: str) -> ModelTier
    (Phase 2 return type; becomes an Engine reference in Phase 5+ per
     AETHER_INTELLIGENCE_ARCHITECTURE.md Section 9.2, without changing
     this method's name or calling convention)
  get_definition(capability_name: str) -> CapabilityDefinition
```

This is additive to `BaseAgent` (V1_TECHNICAL_SPECIFICATION.md Section
2.7): a new optional `capability: ClassVar[str | None] = None` attribute,
defaulting to `None` for any agent — such as Phase 1's `ConversationAgent`
— that has not yet been updated to declare one. `FileAgent` and
`SystemAgent` declare `capability = "file_operation_reasoning"` and
`capability = "system_monitoring_interpretation"` respectively, alongside
their existing `llm_tier`; the registry resolves the capability to confirm
it matches the declared tier, rather than the tier being computed in
isolation. No existing agent breaks by leaving `capability` unset.

### 10.4 Concurrent Task Execution Model

**A naming note before the model itself.** This section defines the
lifecycle of an `AgentTask` (V1_TECHNICAL_SPECIFICATION.md Section 2.7) —
the AI runtime's own internal unit of work — as it moves through
`AgentRuntime`. It is unrelated to `TaskStatus`
(V1_TECHNICAL_SPECIFICATION.md Section 2.9), which governs user-facing
to-do items in the `TaskManager` domain. A user's to-do item and an
agent's execution task are different things that happen to share the word
"task" in casual usage. Where ambiguity is possible, this document says
"AgentTask lifecycle state" and "TaskManager status" explicitly.

**The nine states:**

```
QUEUED      — submitted, not yet evaluated for readiness
READY       — dependencies satisfied, eligible to run once an
              agent/engine is available
RUNNING     — actively executing
WAITING     — RUNNING, but suspended on an external I/O operation
              (a tool call, an LLM call) that resolves on its own
BLOCKED     — cannot proceed; depends on another task/resource that
              has not yet completed
PAUSED      — deliberately suspended by the Scheduler to make room
              for higher-priority work; resumes from where it left off
COMPLETED   — finished successfully
FAILED      — terminated due to an unrecoverable error
CANCELLED   — explicitly cancelled before reaching a terminal state
```

**State transitions:**

```
QUEUED  ──(dependencies satisfied)───────────▶ READY
READY   ──(agent/engine available)───────────▶ RUNNING
RUNNING ──(initiates I/O-bound operation)────▶ WAITING
WAITING ──(I/O resolves)─────────────────────▶ RUNNING
WAITING ──(I/O fails unrecoverably)──────────▶ FAILED
RUNNING ──(new dependency discovered)────────▶ BLOCKED    [dormant, Phase 2]
BLOCKED ──(blocking dependency completes)────▶ READY      [dormant, Phase 2]
RUNNING ──(Scheduler preempts)───────────────▶ PAUSED     [dormant, Phase 2]
READY   ──(Scheduler defers before dispatch)─▶ PAUSED     [dormant, Phase 2]
PAUSED  ──(Scheduler resumes)────────────────▶ READY      [dormant, Phase 2]
RUNNING ──(successful finish)────────────────▶ COMPLETED
RUNNING ──(unrecoverable error)──────────────▶ FAILED
(any non-terminal state) ──(explicit cancel)─▶ CANCELLED
```

**What is active in Phase 2, and what is dormant.** `AgentRuntime.
execute()` (V1_TECHNICAL_SPECIFICATION.md Section 2.7) already compresses
QUEUED → READY → RUNNING into a single dispatch, since Phase 2 has no
persistent queue holding multiple pending tasks across concurrent agents —
one task is submitted and awaited at a time. WAITING is genuinely
exercised today: a tool call inside an agent's ReAct loop (Section 8.5)
already suspends the agent's reasoning while I/O completes. COMPLETED,
FAILED, and CANCELLED are already exercised via `AgentResult.success` and
the existing timeout handling. **BLOCKED and PAUSED are defined now for
schema completeness and forward compatibility, but no Phase 2 code path
produces a task in either state** — there is no Planning Agent yet
producing multi-task dependency graphs (BLOCKED requires one), and no
concurrent Scheduler yet capable of preempting a running task in favor of
another (PAUSED requires one). Both activate at
AETHER_INTELLIGENCE_ARCHITECTURE.md Section 15's Stage 2 (Advanced
Multi-Agent Runtime), corresponding to the original Master Blueprint
Phase 5 — the same phase V1_TECHNICAL_SPECIFICATION.md Section 2.7 already
names as the point `AgentRuntime`'s internals are replaced with a
LangGraph state graph.

**Failure recovery and retry strategy.** Not every `FAILED` transition is
retried, and the distinction is determined by exception type, reusing the
`AetherError` hierarchy already defined in ADR-011 Section 9.4 rather than
inventing a parallel classification:

| Exception Type | Retry-Eligible? | Reasoning |
|---|---|---|
| `LLMTimeoutError`, `LLMProviderError` | Yes — up to 2 task-level retries | Transient; a second attempt may simply succeed |
| `ToolExecutionError` (non-permission) | Yes — up to 2 task-level retries | May be transient (e.g., a momentarily locked file) |
| `ToolPermissionError` | No | `SafetyValidator` denied it for a reason that will not change on retry |
| `MemoryValidationError`, `AgentIterationError` | No | Represents a logic or input error, not a transient condition |

A retry re-enters the state machine at `READY`, not `QUEUED` — its
dependencies, if any, are already known to be satisfied. Task-level
retries are distinct from, and layered on top of, `LLMRouter`'s own
internal retry logic (`max_retries`, V1_TECHNICAL_SPECIFICATION.md Section
2.4), which handles transient provider failures at a lower level before
they ever surface as a task-level `FAILED` transition.

**Dependency handling.** In Phase 2, a task's dependencies are its
`AgentTask.input_data` and the `AgentContext` it was assembled with —
already fully resolved before the task reaches `QUEUED`. Genuine
inter-task dependencies (task B cannot start until task A's output is
available) become meaningful once the Planning Agent
(AETHER_INTELLIGENCE_ARCHITECTURE.md Section 7, Group A) produces
multi-node task graphs — a later-phase capability the `BLOCKED` state is
reserved for, not one Phase 2 introduces.

### 10.5 Agent Health Interface

**Additive to `BaseAgent`.** The methods below extend `BaseAgent`
(V1_TECHNICAL_SPECIFICATION.md Section 2.7) purely additively. The locked
`execute()` abstract method and the `_recall()` / `_remember()` /
`_invoke_tool()` protected helpers are unchanged. Every agent — present
and future — gains these seven methods, with a sensible default
implementation provided by `BaseAgent` itself, so no existing agent
subclass is required to override anything to remain compliant.

```
is_alive() -> bool
health_status() -> HealthStatus
current_load() -> float
estimated_completion() -> datetime | None
last_error() -> AgentError | None
active_tasks() -> list[TaskReference]
queued_tasks() -> list[TaskReference]
```

**`is_alive()`** — whether the agent's execution context is currently
responsive. For Phase 2's in-process agents this is close to trivially
true whenever `aether-core` itself is running, but the method is
introduced now because it stops being trivial the moment PC Control
completes its own Stage B extraction (Sections 3.2–3.3): `services/
pc-control/` is a genuinely separate process, and `is_alive()` is exactly
the question `SystemAgent`, or the future Health Monitor Agent, needs to
ask about it.

**`health_status()`** returns `HealthStatus`: `HEALTHY | DEGRADED |
UNHEALTHY`, with an optional detail string. `DEGRADED` covers, for
example, an agent whose calls are currently being forced onto
`ModelTier.LOCAL` due to budget exhaustion — directly observable today via
`BudgetStatus.active_tier_override` (V1_TECHNICAL_SPECIFICATION.md Section
2.4) — which should never be silently reported as `HEALTHY`.

**`current_load()`** returns a 0.0–1.0 value. In Phase 2's sequential
runner this is effectively binary per agent (0.0 idle, 1.0 while its one
task is `RUNNING`); it becomes continuously meaningful once Phase 5
permits an agent multiple simultaneous `RUNNING`/`WAITING` tasks.

**`estimated_completion()`** returns a `datetime` derived from the current
task's `AgentTask.timeout_seconds` (already a locked field,
V1_TECHNICAL_SPECIFICATION.md Section 2.7) and elapsed time so far, or
`None` when idle.

**`last_error()`** returns the most recent `AetherError`-family exception
(ADR-011 Section 9.4) this agent raised, if any — the single most recent
one, not a history; the full history belongs to Runtime Telemetry (Section
10.6).

**`active_tasks()`** and **`queued_tasks()`** return tasks currently in
`RUNNING`/`WAITING` and `QUEUED`/`READY` respectively (Section 10.4). In
Phase 2, `active_tasks()` holds at most one element, and `queued_tasks()`
is typically empty, since tasks are awaited directly rather than
persistently queued — both methods exist now so callers have a stable
contract before either list becomes non-trivial.

**What this enables.** Self-healing becomes possible once a consuming
component polls or subscribes to this interface across every registered
agent — the Health Monitor Agent, already fully defined in
AETHER_INTELLIGENCE_ARCHITECTURE.md Section 7, Group C, is that consumer.
An agent reporting `UNHEALTHY` for a sustained period can be flagged; an
agent whose `estimated_completion()` has passed without a state change can
be investigated; an agent whose `last_error()` is a retry-eligible
`AetherError` (Section 10.4's table) can be automatically restarted rather
than left failed. Phase 2 does not implement the Health Monitor Agent
itself — that remains a later-phase deliverable — but every agent Phase 2
introduces, and every agent Phase 1 already built, now exposes the data
that agent will eventually consume.

### 10.6 Runtime Telemetry

**Extends, does not replace.** Telemetry is not a new subsystem layered
onto Aether. It is the systematic completion of the event bus and
structured-logging infrastructure Phase 1 already built — Redis Streams
with the locked `AetherEvent` envelope (V1_TECHNICAL_SPECIFICATION.md
Section 2.3) and `structlog` (ADR-011 Section 3.5) — extended with the
resource- and validation-level dimensions Phase 1 had no reason to capture
yet.

**What already exists, now formally recognized as telemetry:**

| Requested Dimension | Existing Source |
|---|---|
| Task Started / Completed / Failed | `agent.run.started` / `agent.run.completed` / `agent.run.failed` (V1_TECHNICAL_SPECIFICATION.md Section 7.3) — now understood as marking the Section 10.4 `RUNNING` and terminal-state transitions |
| Execution Duration | `AgentResult.duration_ms`, already a locked field (V1_TECHNICAL_SPECIFICATION.md Section 2.7) |

**What is new in Phase 2:**

A new event, capturing process-level resource usage:

```
runtime.resource.snapshot       schema_version: "1.0"
{
    "process":            str,   ("aether-core" | "aether-voice" | "aether-pc-control")
    "cpu_percent":          float,
    "gpu_vram_used_mb":      int | None,
    "ram_used_mb":            int,
    "timestamp_utc":           str
}
```

Emitted periodically (not per-task), extending the VRAM allocation
planning already sketched in V1_TECHNICAL_SPECIFICATION.md Section 9.4
from a one-time planning table into an ongoing, queryable measurement.
Phase 2 itself introduces no new GPU-bound workload — `SafetyValidator`
and every PC control operation are CPU-only by design — so Phase 2's own
`gpu_vram_used_mb` readings continue to reflect Phase 1's existing
Whisper and Ollama footprint. The field exists now so it is already
populated with a real baseline before AETHER_INTELLIGENCE_ARCHITECTURE.md
Section 13's multi-engine local stack makes it load-bearing.

Two existing event payloads gain new fields, additively — per
V1_TECHNICAL_SPECIFICATION.md Section 7.2's Versioning Strategy, additive
payload changes require no schema version bump and do not affect any
existing consumer:

```
llm.call.completed       gains: "retry_count": int
agent.run.completed      gains: "retry_count": int
```

**Queue Wait Time** is the duration between a task entering `QUEUED` and
entering `RUNNING` (Section 10.4). In Phase 2's sequential runner this is
near-zero by construction — tasks run essentially as soon as submitted —
which is itself useful: it gives Phase 5's genuine queuing a clean
"before" baseline to compare against, recorded from Phase 2 onward rather
than starting from nothing.

**Validation Result** generalizes the pattern `pc_control.action.denied`
(Section 7 of this specification) already establishes for PC control
specifically: any component performing a validation check emits its
result using the same `ValidationResult` structure already defined in
Section 5.1, as telemetry, not only as a domain-specific event. This is
the same structure `validate_browser_action()` will use in Phase 3 without
requiring a new telemetry pattern to be invented for it.

**What this supports:**

*Debugging* — every event carries the existing `correlation_id`
(V1_TECHNICAL_SPECIFICATION.md Section 2.3), so a failure can be traced
across every event it touched via Redis Streams' persistence, rather than
requiring log-file archaeology.

*Observability* — the Observability Agent
(AETHER_INTELLIGENCE_ARCHITECTURE.md Section 7, Group C) is the designated
future aggregator of this stream.

*Performance optimization* — this telemetry is the raw data source for
the Performance Review already mandatory at every phase close (ADR-011
Section 10; AETHER_PHASE_EXECUTION_WORKFLOW.md Step 11). The ten measured
runs per path required by ADR-011 Section 10.2 can be drawn directly from
this stream rather than timed by hand.

*Future self-improvement* — the Learning Agent
(AETHER_INTELLIGENCE_ARCHITECTURE.md Section 7, Group A) requires
long-term interaction history to identify patterns worth proposing changes
for. Runtime Telemetry is the operational analog of that for system
behavior rather than user behavior: a sustained rise in `retry_count`, or
a capability spending an increasing share of its time in `DEGRADED`
`health_status()`, is exactly the signal a future self-improvement process
needs — recorded from Phase 2 forward, well before any component exists
that is sophisticated enough to act on it.

---

## 11. AI SKILL REQUIREMENTS

Per AI_SKILLS_INTEGRATION.md's category taxonomy, Phase 2 draws primarily
on: `architecture` (mandatory), `python` (mandatory), `security`
(mandatory, every session), `testing` (mandatory), `documentation`
(mandatory), and — for the first time in this project — genuinely,
`automation-engineering` (currently classified Optional).

**A dependency this document surfaces:** `automation-engineering`'s
registry (AI_SKILLS_INTEGRATION.md Section 17) is currently `PLACEHOLDER`
— no skill has been evaluated and registered in that category. Before any
Phase 2 Antigravity prompt covering `aether/pc_control/` is generated, at
least one skill covering Windows automation APIs and safe automation
boundaries should be evaluated and registered under that category, per
AI_SKILLS_INTEGRATION.md's own evaluation framework (Section 10). This is
noted as a dependency (Section 17) rather than resolved here, since skill
evaluation is itself a governed process this document does not have
authority to shortcut.

---

## 12. SECURITY REQUIREMENTS

Phase 2 is the first phase in which an unreviewed defect can affect the
user's actual files and running programs. These requirements are treated
accordingly.

1. `SafetyValidator` contains zero LLM calls in its validation path —
   rule-based only, per the Critical Audit's rejection of the LLM-based
   Guardian Agent on both cost and latency grounds.
2. Every call to `PCControlAPI.execute_action()` passes through
   `SafetyValidator` before any OS-level action occurs. No code path,
   tool, or agent may call an `_adapters/windows.py` function directly.
3. The `forbidden_launch` list already present in `.aether/permissions.yaml`
   (`cmd.exe`, `powershell.exe`, `wscript.exe`, `cscript.exe`,
   `regedit.exe`) is enforced absolutely. Phase 2's test suite includes an
   explicit test proving each entry is blocked regardless of how a request
   is phrased (Section 14.2).
4. Destructive file operations (delete, overwrite) require the
   `confirmation_token` mechanism. No Phase 2 tool can silently delete or
   overwrite a file.
5. Every PC control action, allowed or denied, is logged to
   `tool_executions` (Section 8.2), satisfying ADR-010's audit trail
   requirement without a new table.
6. Registry access, service management, driver interaction, and network
   configuration changes are not exposed by any Phase 2 tool. This is an
   architectural exclusion (Section 1.3), not an oversight to be caught in
   review.
7. `SafetyValidator` carries a test coverage target beyond the general
   Phase 2 baseline set in ADR-011 Section 3.4 (70% for stable modules),
   given its security-critical role, per the Security-Sensitive Code Rules
   in AI_GENERATION_RULES_V2.md Section 13 — target is full branch coverage
   of every permission path.
8. `SafetyValidator` and `PCControlAPI` are labeled as security-sensitive
   in their module docstrings, per AI_GENERATION_RULES_V2.md Section 13.1's
   labeling convention.

---

## 13. PERFORMANCE REQUIREMENTS

New measured paths, added to Phase 2's own performance baseline
(`docs/performance/phase-2-baseline.md`, produced per ADR-011 Section 10.2
methodology and AETHER_PHASE_EXECUTION_WORKFLOW.md Step 11):

| Path | Target p50 | Target p95 |
|---|---|---|
| `SafetyValidator` check (any) | < 10ms | < 25ms |
| `execute_action` — non-destructive (e.g., launch app) | < 500ms | < 1000ms |
| File search (moderate directory size) | < 1000ms | < 2000ms |
| `get_system_state()` snapshot | < 200ms | < 400ms |

The `SafetyValidator` target is deliberately near-instant — this is the
concrete performance argument, not just the cost argument, for why the
Critical Audit's rule-based design was correct: an LLM-based Guardian
Agent could not plausibly meet a 10ms target.

Phase 1's existing baseline paths (memory recall, LLM calls, voice
latency) are re-measured as part of Phase 2's regression testing (Section
14.3) to confirm the PostgreSQL migration introduced no degradation
beyond the thresholds in ADR-011 Section 10.5.

---

## 14. TESTING REQUIREMENTS

### 14.1 Unit Tests

`SafetyValidator`: every entry in `forbidden_launch` is individually
tested as blocked; every entry in `forbidden_paths` is individually
tested as blocked; destructive operations without a `confirmation_token`
are tested as denied; the same operations with a valid token are tested
as permitted; `is_destructive()` is tested against every operation type
Phase 2 introduces.

`PCControlAPI`: each method tested with mocked `_control/` submodules and
a mocked `SafetyValidator`, confirming the validator is always called
before dispatch.

### 14.2 The PC Control Trust Test (Integration — Phase 2's Defining Test)

Two halves, both required to pass:

**Positive case:** A request equivalent to "open Notepad" is issued
through `SystemAgent`. `notepad.exe` opens. The action is logged to
`tool_executions` with `success=True`. A memory is recorded via
`self._remember()`.

**Negative case:** A request equivalent to "open Command Prompt" is
issued. `SafetyValidator` denies it. No process is launched. The denial
is logged to `tool_executions` with `success=False`. The
`pc_control.action.denied` event is emitted. Aether's response —
rendered, per AETHER_INTELLIGENCE_ARCHITECTURE.md Section 2, through the
Personality Engine's eventual implementation, or in Phase 2's case
directly through `ConversationAgent`'s existing response path — clearly
communicates the refusal rather than failing silently.

Both halves are required. A Phase 2 that can act but cannot prove it
correctly refuses has not demonstrated the capability this phase actually
grants — the boundary, not just the action.

### 14.3 Regression Testing

Per AETHER_PHASE_EXECUTION_WORKFLOW.md Step 14, Phase 1's own defining
tests are re-run after the PostgreSQL migration specifically:

- The cross-session memory persistence test (Milestone M1.5) — confirming
  memory survives the database backend change.
- The Voice Milestone six-step sequence (Milestone M1.10) — confirming
  voice latency is unaffected.

### 14.4 Contract Tests

`PCControlAPI` and `SafetyValidator` method signatures verified via
`inspect.signature()`, following the exact pattern already established in
`tests/contracts/test_memory_api_contract.py`.

---

## 15. DOCUMENTATION REQUIREMENTS

- `V1_TECHNICAL_SPECIFICATION.md` updated with the final, as-implemented
  specifications of `aether/security/` and `aether/pc_control/`, per
  ADR-011 Gate Q-4.
- `.aether/permissions.yaml` inline comments updated to reflect the actual
  tool surface Phase 2 implements.
- New guide: `docs/guides/adding-a-pc-control-tool.md`, following the
  existing guide pattern.
- `CHANGELOG.md` milestone entries throughout, plus the Phase 2 completion
  entry at closure, per ADR-010 Section 17.5.

---

## 16. RISKS

| Risk | Mitigation |
|---|---|
| Windows automation API fragility across Windows versions/configurations | Defensive error handling in `_adapters/windows.py`; `SafetyValidator` fails closed — uncertain validation denies rather than allows |
| Antivirus / Windows Defender flagging automation tools (identified in Critical Audit Section 3.2) | Document expected flags in the setup guide; revisit code-signing in a later phase if this proves disruptive |
| Data loss during PostgreSQL migration | Mandatory verified backup before migration begins, per ADR-010 Section 4; migration is a Level 4 operation under ADR-010 Section 2 |
| Scope creep toward registry/service-level control | Explicitly excluded in Section 1.3; any such request during implementation is a Level 4 Prohibited Action per AI_GENERATION_RULES_V2.md Section 7.4, refused rather than implemented |

---

## 17. DEPENDENCIES

**Satisfied:**
- Phase 1 complete, per the developer's direct confirmation and the
  Section 6.1 exception recorded in AETHER_PHASE_EXECUTION_WORKFLOW.md.
- PostgreSQL and `asyncpg` are pre-approved dependencies — already
  anticipated in V1_TECHNICAL_SPECIFICATION.md Section 3.3 and ADR-011's
  coverage-target table. No new Dependency Governance evaluation
  (ADR-010 Section 11) is required.
- `pywinauto` and `pyautogui` are already listed in
  V1_TECHNICAL_SPECIFICATION.md Section 7.7's approved technology stack.
  No new evaluation required.

**Outstanding, to be resolved before implementation prompts are generated:**
- The `automation-engineering` AI skill category needs at least one
  registered skill (Section 11).

---

## 18. DELIVERABLES

- `aether/security/` module, with `SafetyValidator` fully implemented and
  tested.
- `aether/pc_control/` module (Stage A), then `services/pc-control/`
  (Stage B, post-extraction).
- `FileAgent` and `SystemAgent`, registered with `AgentRuntime`.
- Eight new PC control tools, registered with `ToolRegistry`.
- PostgreSQL migration complete, with Phase 1's cross-session memory and
  voice tests re-confirmed passing against the new backend.
- The PC Control Trust Test (Section 14.2) passing, both halves.

---

## 19. ACCEPTANCE CRITERIA

### 19.1 Governed by the Existing Twelve-Level Framework

Phase 2's acceptance criteria are AETHER_DEFINITION_OF_DONE.md's twelve
levels, applied to Phase 2's specific milestones — this document does not
define a parallel acceptance system. Every milestone this phase produces
climbs Levels 1 through 10; the phase as a whole climbs Levels 11 and 12,
governed by the seven phase-closure templates now defined in
AETHER_DEFINITION_OF_DONE.md Section 6, including the
`PHASE_2_DEFINITION_OF_DONE_REPORT.md` this phase will produce.

### 19.2 Plus, Specifically for This Phase

- The PC Control Trust Test (Section 14.2) passes, both the positive and
  negative case, with no exception — this is Phase 2's equivalent of
  Phase 1's cross-session memory test, and Non-Bypassable Rule NB-2
  applies to it identically.
- Every entry in `.aether/permissions.yaml`'s `forbidden_launch` list is
  individually proven blocked.
- The PostgreSQL migration is complete, verified, and Phase 1's own
  defining tests pass against the new backend.
- Zero registry, service-management, or driver-level capability is present
  in the delivered tool surface.

---

*Document Version: 1.1*
*Status: APPROVED — IMPLEMENTATION SOURCE OF TRUTH FOR PHASE 2*
*Extends: V1_TECHNICAL_SPECIFICATION.md — does not supersede it*
*Amendment History: v1.1 — appended Sections 10.3–10.6 (Capability
Registry, Concurrent Task Execution Model, Agent Health Interface, Runtime
Telemetry) under the existing Section 10; no prior section modified. Each
addition resolves through Phase 2's existing locked mechanisms
(`ModelTier`, the sequential `AgentRuntime`) and marks states/fields not
yet exercised as dormant until AETHER_INTELLIGENCE_ARCHITECTURE.md Section
15's Stage 2, consistent with Section 1.3's original scope boundary*
*Next Document: PHASE_2_IMPLEMENTATION_PLAN.md, per
AETHER_PHASE_EXECUTION_WORKFLOW.md Step 2*
*Owner: Chief AI Architect / Principal Systems Engineer*
*Last Updated: 2025-11-15*
