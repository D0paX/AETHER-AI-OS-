# PHASE 2 IMPLEMENTATION PLAN
### docs/phases/phase-2/PHASE_2_IMPLEMENTATION_PLAN.md
### PC Control — "Operator" — Execution Blueprint

---

**Date:** 2025-11-15
**Status:** APPROVED FOR EXECUTION
**Classification:** Phase Execution — Not Architecture, Not Specification
**Authority:** Chief AI Architect / Principal Systems Engineer
**Produced At:** AETHER_PHASE_EXECUTION_WORKFLOW.md Step 2 (Phase Initialization)
**Inherits Rules From:** Master Blueprint, V1 Foundation Architecture
Decision, V1 Technical Specification, Critical Architecture Audit,
AETHER_INTELLIGENCE_ARCHITECTURE.md, ADR-010, ADR-011,
AI_GENERATION_RULES_V2.md, AI_SKILLS_INTEGRATION.md,
AETHER_PHASE_EXECUTION_WORKFLOW.md, AETHER_DEFINITION_OF_DONE.md,
PHASE_2_TECHNICAL_SPECIFICATION.md

---

## WHAT THIS DOCUMENT IS AND IS NOT

This is not an architecture document — that authority belongs to
AETHER_INTELLIGENCE_ARCHITECTURE.md and V1 Foundation Architecture
Decision. This is not a specification — that authority belongs to
PHASE_2_TECHNICAL_SPECIFICATION.md. This document assumes both are
correct and answers only one question: in what exact order, with what
exact dependencies, under what exact gates, does Phase 2 get built. It
contains no code, no folder structures, and no implementation prompts —
those are generated one at a time, per milestone, only after this plan is
approved and only in the order this plan defines.

---

## TABLE OF CONTENTS

1. [Implementation Philosophy](#1-implementation-philosophy)
2. [Implementation Order](#2-implementation-order)
3. [Milestone Breakdown](#3-milestone-breakdown)
4. [Implementation Waves](#4-implementation-waves)
5. [Dependency Graph](#5-dependency-graph)
6. [Testing Strategy](#6-testing-strategy)
7. [Validation Gates](#7-validation-gates)
8. [Failure Handling](#8-failure-handling)
9. [Rollback Strategy](#9-rollback-strategy)
10. [Definition of Done Mapping](#10-definition-of-done-mapping)
11. [Architecture Compliance](#11-architecture-compliance)
12. [Developer Workflow](#12-developer-workflow)
13. [AI Workflow](#13-ai-workflow)
14. [Phase Completion Criteria](#14-phase-completion-criteria)
15. [Final Phase Deliverables](#15-final-phase-deliverables)
16. [Implementation Rules](#16-implementation-rules)
17. [Implementation Prompt Policy](#17-implementation-prompt-policy)
18. [Guiding Principle](#18-guiding-principle)

---

## 1. IMPLEMENTATION PHILOSOPHY

Implementation follows architecture. It does not negotiate with it,
reinterpret it under time pressure, or fill a gap with a plausible
shortcut and a plan to fix it later. Every constitutional document listed
in this plan's header is binding on every milestone below, without
exception, for these specific reasons:

**No shortcuts.** A milestone that appears to work but bypasses
`SafetyValidator`, hardcodes a model name, or accesses `PCControlAPI`'s
private submodules directly has not completed the milestone — it has
produced a different, unapproved thing that happens to occupy the same
file path. ADR-011's Zero-Tolerance Violations (Section 2, ZT-1 through
ZT-10) and AI_GENERATION_RULES_V2.md's Prohibited Actions (Section 7)
apply to every line of Phase 2 code without a Phase-2-specific exception
list, because none exists.

**No temporary hacks.** ADR-010 Section 12 (Placeholder and Temporary
Code Policy) already forbids `TODO`, `FIXME`, commented-out blocks, and
stub security validation anywhere in this repository. Phase 2 introduces
`SafetyValidator` — the single highest-consequence place in the entire
codebase for this rule to hold, since a stubbed permission check here is
not a quality issue, it is an unguarded door to the user's file system.

**No undocumented code.** ADR-011 Section 3.6's Mandatory Documentation
Standards apply to every new module, class, and public function this plan
introduces. Documentation Updates is one of this plan's eighteen required
milestone fields for a reason: it is checked at the same gate as tests,
not appended afterward.

**No architecture bypasses.** Every milestone below states, explicitly,
which sections of AETHER_INTELLIGENCE_ARCHITECTURE.md and
PHASE_2_TECHNICAL_SPECIFICATION.md it implements. A milestone that cannot
name its governing section has not been specified correctly, and
generating an implementation prompt for it is refused per
AI_GENERATION_RULES_V2.md's Stop Conditions (STOP-3: Architecture
conflict; STOP-5: Missing prerequisite) until it can.

---

## 2. IMPLEMENTATION ORDER

The exact sequence, sixteen milestones, each depending only on what
precedes it. Full detail for every milestone is in Section 3; this is the
quick-reference order.

```
M2.0  — Phase 2 Preparation
M2.1  — PostgreSQL Migration
M2.1.5 — Foundation Remediation (inserted post-hoc — see below)
M2.1.6 — Conversation Interface Remediation (inserted post-hoc — see below)
M2.1.7 — Test Isolation and FTS5 Fixture Correctness (inserted post-hoc — see below)
M2.1.8 — Memory Quality: Immediate Fact Capture (inserted post-hoc — see below)
M2.1.9 — Codebase-Wide Lint & Type Remediation (inserted post-hoc — see below)
M2.1.10 — Test Fixture and Script Robustness Cleanup (inserted post-hoc — see below)
M2.2  — Security Module (SafetyValidator)
M2.3  — PC Control Core: Application Control
M2.4  — PC Control Core: File Operations
M2.5  — PC Control Core: System Monitoring
M2.6  — Capability Registry
M2.7  — Concurrent Task Execution Model (State Vocabulary)
M2.8  — Agent Health Interface
M2.9  — Runtime Telemetry Extensions
M2.10 — PC Control Tool Suite
M2.11 — FileAgent & SystemAgent
M2.12 — Kernel Integration
M2.13 — PC Control Trust Test
M2.14 — Service Extraction (Stage B)
M2.15 — Phase 2 Closure Preparation
```

No milestone may begin before the milestone immediately above it has
reached Level 10 (Production Ready) per AETHER_DEFINITION_OF_DONE.md.

**M2.1.5 was not part of the originally approved sixteen-milestone
sequence.** It was inserted after M2.1's execution surfaced three P1
defects in Phase 1's existing memory and session code — not caused by
M2.1, but found by it. Per AETHER_DEFINITION_OF_DONE.md Non-Bypassable
Rule NB-5, P1 debt discovered during a phase must be resolved within
that phase regardless of which milestone it originated in. Its insertion
is documented here, in the dependency graph (Section 5), and in its own
full milestone entry in Section 3, rather than silently absorbed into
either M2.1's or M2.2's scope.

**M2.1.6, M2.1.7, M2.1.8, M2.1.9, and M2.1.10 were inserted for the same
reason, compounding one layer further.** M2.1.5's own diagnostic
investigation surfaced DEBT-007 (the conversation interface). M2.1.6's
own execution — specifically, its required manual TEXT MILESTONE
re-run — then surfaced two more: DEBT-008 (integration tests writing
directly to the real database, which had already caused an unauthorized
deletion of 47 real rows before this milestone existed to prevent it)
and DEBT-009 (the consolidation threshold and per-turn memory quality
gap meaning Phase 1's original TEXT MILESTONE claim was very likely
never genuinely validated). By explicit developer decision, all five
debt items remaining open after the M2.1 review — DEBT-004, DEBT-005,
DEBT-006, DEBT-008, DEBT-009 — are resolved before M2.2. Sequenced by
priority and genuine dependency: M2.1.7 (DEBT-008 + DEBT-004, test
infrastructure safety) first, since no further testing should occur
without it; M2.1.8 (DEBT-009, the core memory-quality fix) second, the
most architecturally significant of the five; M2.1.9 (DEBT-005) and
M2.1.10 (DEBT-006) last, exactly as originally sequenced, only renumbered
to make room.

---

## 3. MILESTONE BREAKDOWN

---

### M2.0 — PHASE 2 PREPARATION

**Purpose:** Confirm every outstanding dependency PHASE_2_TECHNICAL_
SPECIFICATION.md flagged is resolved before any Phase 2 code is written.

**Objectives:**
- Verify the `automation-engineering` AI skill category
  (AI_SKILLS_INTEGRATION.md Section 17) has at least one evaluated,
  registered skill — PHASE_2_TECHNICAL_SPECIFICATION.md Section 11
  identifies this as a blocking dependency, not an optional one.
- Create branch `phase/2` from `develop`, per AETHER_PHASE_EXECUTION_
  WORKFLOW.md Step 3.
- Confirm a current, verified backup exists (`backup.ps1` manifest shows
  `verified: true`) before any Level 4 operation (M2.1) is attempted.

**Deliverables:** `phase/2` branch created; `automation-engineering`
skill registered; pre-phase backup verified and its timestamp recorded
for later rollback reference.

**Dependencies:** Phase 1 GO decision, per AETHER_PHASE_EXECUTION_
WORKFLOW.md Section 6.1's recorded exception.

**Files Created:** None.
**Files Modified:** None.
**Public APIs:** None.
**Internal APIs:** None.

**Tests Required:** None — this milestone is verification, not
implementation.

**Validation Required:** `skills/REGISTRY.md` shows a non-empty entry
under `automation-engineering`; `git branch` shows `phase/2`; backup
manifest inspected directly.

**Architecture Review:** N/A — no code produced.
**Security Review:** N/A.
**Performance Review:** N/A.
**Documentation Updates:** `docs/architecture/context-log.md` phase-start
snapshot, per ADR-010 Section 18.2.

**Definition of Done:** Levels 1–2 only (Developer Done, Implementation
Done) — this milestone has no architecture, security, or testing surface
to climb further levels against.

**Estimated Complexity:** Low.
**Risk Level:** Low — the only real risk is proceeding without the skill
gap closed, which this milestone exists specifically to prevent.

**Expected Output:** A repository state in which every prerequisite
PHASE_2_TECHNICAL_SPECIFICATION.md named is verifiably satisfied.

---

### M2.1 — POSTGRESQL MIGRATION

**Purpose:** Migrate the primary datastore from SQLite to PostgreSQL
before any new Phase 2 code exists, so the highest-risk, most
irreversible operation in this phase is taken while the least new work is
at stake if it fails.

**Objectives:** Execute PHASE_2_TECHNICAL_SPECIFICATION.md Section 8.1's
migration procedure in full; confirm Phase 1's own defining tests still
pass against the new backend.

**Deliverables:** `asyncpg` dependency added; `config.database.url`
pointed at PostgreSQL; all existing Alembic migrations re-run against the
new backend; SQLite file archived, not deleted; `system_kv` updated per
Section 8.3.

**Dependencies:** M2.0 (verified backup, per ADR-010 Section 4's
requirement that this Level 4 operation never proceeds without one).

**Files Created:** None (dependency addition only).
**Files Modified:** `pyproject.toml` (add `asyncpg`), `config/local.yaml`
(database URL).
**Public APIs:** None — `MemoryAPI`'s interface is unaffected; the
backend swap is invisible above the SQLAlchemy dialect boundary, per
V1_TECHNICAL_SPECIFICATION.md Section 3.3.
**Internal APIs:** None.

**Tests Required:** Full Milestone M1.5 cross-session memory persistence
test, re-run against PostgreSQL. Full Milestone M1.10 Voice Milestone
six-step sequence, re-run.

**Validation Required:** `alembic upgrade head` succeeds against
PostgreSQL; row counts match the pre-migration SQLite export; both
regression tests pass without modification to their own logic.

**Architecture Review:** V1_TECHNICAL_SPECIFICATION.md Section 3.3
(Migration Plan) — confirm no deviation from the documented procedure.

**Security Review:** ADR-010 Section 2 (this is a Level 4 Potentially
Destructive operation) and Section 4 (Backup Requirements) — both
followed in full before execution.

**Performance Review:** Phase 1's existing baseline paths (memory recall,
LLM calls, voice latency) re-measured post-migration; any regression
beyond ADR-011 Section 10.5's thresholds blocks this milestone's gate.

**Documentation Updates:** `V1_TECHNICAL_SPECIFICATION.md` database
section annotated with the migration date; `CHANGELOG.md` entry.

**Definition of Done:** Levels 1–9 in full — this is a security- and
performance-sensitive milestone with no exemptions from any level.

**Estimated Complexity:** Low-Medium — the procedure is already fully
documented; the work is executing it correctly, not designing it.
**Risk Level:** High — explicitly named in PHASE_2_TECHNICAL_
SPECIFICATION.md Section 16 as this phase's top data-loss risk.

**Expected Output:** Every subsequent milestone in this plan is built and
tested against PostgreSQL from this point forward.

---

### M2.1.5 — FOUNDATION REMEDIATION

**Purpose:** Resolve three P1 defects M2.1's execution surfaced in
pre-existing Phase 1 code — not introduced by M2.1, found by it. Per
AETHER_DEFINITION_OF_DONE.md Non-Bypassable Rule NB-5, P1 debt discovered
during a phase is resolved within that phase. This milestone exists so
Phase 2's remaining fourteen milestones are not built on top of a memory
system whose consolidation pathway does not actually run.

**Objectives:** Implement `SQLiteMemoryStore.get_messages()` for real (it
was specified in V1_TECHNICAL_SPECIFICATION.md Section 3.2 since Phase 1
but never built); expose it publicly through four new, purely additive
`MemoryAPI` methods; correct `SessionManager`'s constructor, which
V1_TECHNICAL_SPECIFICATION.md Section 2.8 incorrectly specified with
direct `db_session_factory` and `consolidation_pipeline` dependencies —
this is a specification error being corrected, not only an
implementation defect; fix the stale `.publish()` assertion in
`test_memory_api.py`.

**Deliverables:** A working, publicly-exposed, live-tested consolidation
pathway; `SessionManager` with zero direct imports of `sqlalchemy` or
`aether.memory._consolidation`; a corrected constructor signature
reflected back into V1_TECHNICAL_SPECIFICATION.md; a real integration
test proving consolidation executes end-to-end, not only under mocks.

**Dependencies:** M2.1 (this milestone remediates defects that specific
milestone's execution surfaced).

**Files Created:** `tests/integration/test_consolidation_live.py`.
**Files Modified:** `aether/memory/_stores/sqlite_store.py`,
`aether/memory/api.py`, `aether/memory/__init__.py`,
`aether/memory/_consolidation/pipeline.py`, `aether/session/manager.py`,
`aether/core/kernel.py` (wherever it constructs `SessionManager`),
`tests/unit/test_memory_api.py`, `V1_TECHNICAL_SPECIFICATION.md`
(Sections 2.5 and 2.8).
**Public APIs:** Four new, additive `MemoryAPI` methods:
`start_conversation()`, `record_message()`, `end_conversation()`,
`get_conversation_messages()`. Additive per ADR-010 Section 17.4 — no
existing caller of `MemoryAPI`'s original seven methods is affected.
**Internal APIs:** `SQLiteMemoryStore.get_messages()`, implemented for
the first time rather than merely called.

**Tests Required:** Unit tests for `get_messages()` and all four new
`MemoryAPI` methods, independently. A live integration test proving
end-of-session consolidation produces real new memories, not a mocked
assertion. Regression coverage for `SessionManager`'s existing M1.8
tests against its corrected constructor.

**Validation Required:** `grep -r "sqlalchemy\|aiosqlite\|sqlite3"
aether/session/` → zero matches. `grep -r "_consolidation"
aether/session/` → zero matches. `grep -r "type: ignore"
aether/memory/_consolidation/` → zero matches.

**Architecture Review:** V1_TECHNICAL_SPECIFICATION.md Sections 2.5, 2.7,
2.8, 3.2 — this milestone corrects Section 2.8 directly and extends
Section 2.5.

**Security Review:** None new — no privileged operation is introduced.

**Performance Review:** No new latency target; confirm consolidation's
existing performance characteristics are unaffected by the fix.

**Documentation Updates:** V1_TECHNICAL_SPECIFICATION.md Section 2.5
(add the four new methods) and Section 2.8 (correct the constructor
signature) — this is a specification correction, recorded as such, not
a silent edit.

**Definition of Done:** Levels 1–9 in full per AETHER_DEFINITION_OF_DONE.md.

**Estimated Complexity:** Medium — the fix is well-scoped, but touches a
locked interface and a constructor signature correction.
**Risk Level:** Medium — the risk of NOT doing this (compounding on a
broken consolidation path across fourteen more milestones) is higher
than the risk of doing it now.

**Expected Output:** Real end-of-session memory consolidation, proven by
a live test rather than a mock; `SessionManager` fully compliant with the
Memory API boundary; `MemoryAPI`'s public surface correctly reflects what
Phase 1 always intended it to expose.

---

### M2.1.6 — CONVERSATION INTERFACE REMEDIATION

**Purpose:** Resolve DEBT-007. `aether/interfaces/cli.py` and
`aether/interfaces/api.py` — Aether's primary interactive entry points —
construct `AgentTask`, `AgentContext`, and read `AgentResult` using field
names that do not exist on any of the three locked types, and call a
`SessionManager` method that was never implemented. This was found by
M2.1.5's diagnostic investigation, not caused by it, and predates Phase 2.

**Objectives:** Add `SessionManager.build_agent_context()` as the single,
shared point where a cached `SessionContext` becomes a real,
correctly-populated `AgentContext` — replacing two separate, independently
broken hand-assembly attempts with one tested implementation. Correct
both interfaces to use it and to call `update_context()` with the
correct per-turn delta, established in M2.1.5. Prove the fix against the
real interface, not a bypass.

**Deliverables:** A working `_handle_conversation()` in `cli.py`, a
working `/conversation/message` endpoint in `api.py`, both persisting
real conversation turns through `MemoryAPI`. A manual, witnessed re-run
of Milestone M1.9's original TEXT MILESTONE acceptance sequence.

**Dependencies:** M2.1.5 (this milestone corrects a defect that
milestone's diagnostic investigation surfaced).

**Files Created:** `tests/integration/test_conversation_interface.py`.
**Files Modified:** `aether/session/manager.py` (add
`build_agent_context()`), `aether/interfaces/cli.py` (full rewrite of
`_handle_conversation()`), `aether/interfaces/api.py` (full rewrite of
`/conversation/message`).
**Public APIs:** One new `SessionManager` method:
`build_agent_context(session_id: str, user_input: str) -> AgentContext`.
Additive — no existing `SessionManager` method changes.
**Internal APIs:** None.

**Tests Required:** `build_agent_context()` tested in isolation —
correct `AgentContext` assembly from a `SessionContext` and a query.
An end-to-end test driving the real `_handle_conversation()` handler
(not a bypass) confirming a conversational turn produces a displayed
response and a persisted, recallable message. Equivalent coverage for
the API endpoint.

**Validation Required:** `grep -rn "\.instruction\|\.transcript\|
\.output\b\|_cache_session" aether/interfaces/` → zero matches. `uv run
mypy aether/interfaces/ aether/session/ --strict` → zero errors.

**Architecture Review:** V1_TECHNICAL_SPECIFICATION.md Sections 2.7
(`AgentTask`, `AgentContext`, `AgentResult` — locked, unchanged by this
fix, only correctly *used* for the first time), 2.8 (`SessionManager`).

**Security Review:** None new.

**Performance Review:** No new latency target; confirm the corrected
conversation path meets the existing agent-level latency expectations
already established in Phase 1.

**Documentation Updates:** V1_TECHNICAL_SPECIFICATION.md's interface
layer description (Section 2.10 or wherever `cli.py`/`api.py` are
documented) updated to reflect `build_agent_context()` as the required
pattern for any future interface.

**Definition of Done:** Levels 1–10 in full. This milestone's manual
TEXT MILESTONE re-run is its own Level 10 checkpoint, analogous to
Phase 1's original M1.9 gate.

**Estimated Complexity:** Medium — the fix itself is bounded, but proving
it against the real interface (not a mock) requires real end-to-end
exercise.
**Risk Level:** High in significance — this is Aether's primary
interaction surface; a wrong fix here is immediately user-visible.

**Expected Output:** A working conversational interface, for the first
time provably exercised end-to-end rather than assumed working because
its automated tests passed.

---

### M2.1.7 — TEST ISOLATION AND FTS5 FIXTURE CORRECTNESS

**Purpose:** Resolve DEBT-008, DEBT-004, and DEBT-010 together — all
three are about making the test layer trustworthy, not three separate
concerns. DEBT-008 is sequenced first among the five remaining debts
specifically because M2.1.6's execution found integration tests writing
directly to the real database with no isolation, and — before this
milestone existed — unilaterally deleted 47 real rows to clean up the
resulting pollution. No further testing proceeds against production data
stores that aren't structurally guaranteed safe to write to.

**This milestone runs in two parts, not because it was planned that
way, but because Part 1's own required validation found the reason
Part 2 exists.** Part 1 (SQL/PostgreSQL isolation, the original scope)
is complete and proven: a dedicated test database, a fail-closed guard,
and the FTS5 join fix, all verified with real before/after evidence.
Part 1's own full-suite validation run then surfaced a genuine leak —
30 Qdrant points against 29 production SQL rows, a confirmed orphaned
vector already written into the real `episodic_memory` collection —
because the guard covered only the relational database, not the two
other stores `MemoryAPI.remember()` writes to. Reported rather than
silently fixed, per this milestone's own original scope boundary. Part
2 extends the identical guard pattern to Qdrant and Redis, and removes
the specific orphan already present, before M2.1.8 begins — M2.1.8's
own live consolidation testing would otherwise write further orphaned
vectors into the exact same unguarded path.

**Objectives (Part 1 — complete):** A dedicated, disposable test-only
PostgreSQL database, created and migrated fresh at test-session setup,
used by every integration test exclusively. A hard guard that makes it
structurally impossible — not merely conventional — for any test to
connect to anything but that database. Correct the retained SQLite FTS5
join bug (`memories.id = memories_fts.rowid`, comparing a TEXT UUID to
an internal INTEGER rowid, which can never match) so the fast unit-test
fixture path tests something real.

**Objectives (Part 2 — required before closure):** Extend the same
guard to Qdrant — tests write to a distinctly-named collection
(`episodic_memory_test`), never the production `episodic_memory`
collection, verified before any test-suite write occurs. Extend the
same guard to Redis — tests use a non-zero logical database index
(Redis natively supports this; production uses index 0, tests use index
1), verified the same way. Precisely identify and remove the specific
orphaned Qdrant point(s) already confirmed present in production,
cross-referenced against production SQL row IDs so the removal is exact,
not a guess.

**Deliverables:** A test database fully isolated from the real `aether`
database (done). A guard that refuses to run any test suite pointed at
a non-test database URL (done). A corrected FTS5 join, proven by a real
match (done). The same guard extended to Qdrant and Redis (required).
Production Qdrant's point count exactly matching production SQL's row
count once more (required).

**Dependencies:** M2.1.6 (this milestone remediates a gap that
milestone's execution surfaced).

**Files Created:** `tests/conftest_db_guard.py` (done — the hard safety
check). `scripts/provision_test_database.py` (done). `tests/
integration/conftest.py` (done — provisioning, kept separate so
unit-only runs need no live PostgreSQL). Part 2 adds equivalent
verification logic for Qdrant collection name and Redis DB index,
extending `conftest_db_guard.py` rather than creating a parallel
mechanism.
**Files Modified:** `tests/conftest.py`, `aether/memory/_stores/
sqlite_store.py` (FTS5 join, done), `config/local.yaml` (`DatabaseConfig.
test_url`, done). Part 2 adds equivalent test-vs-production
configuration for Qdrant and Redis.
**Public APIs:** None.
**Internal APIs:** None.

**Tests Required:** A test proving the guard itself works for the
database (done, 9 self-tests). A new FTS5 keyword-search test (done, 4
tests). Part 2: equivalent fail-closed proof for Qdrant and Redis —
each misconfigured deliberately, each refusing to run before any test
body executes.

**Validation Required:** Database isolation proven with matching
before/after production row counts (done). Part 2: production Qdrant's
point count proven to exactly equal production SQL's row count after
the orphan is removed and after a full suite re-run confirms no new
orphan appears.

**Architecture Review:** No new architectural surface — this is test
infrastructure, not application code.

**Security Review:** This IS the security review — the guard's entire
purpose is preventing exactly the kind of unauthorized real-data write
that occurred during M2.1.6, now closed for all three data stores
MemoryAPI actually writes to, not only the one discovered first.

**Performance Review:** None new.

**Documentation Updates:** `docs/technical-debt/DEBT_REGISTER.md` — mark
DEBT-008 and DEBT-004 resolved (done); mark DEBT-010 resolved once Part
2 lands, with an explicit note recording the orphan discovery as the
reason Part 2 exists, not only what was fixed.

**Definition of Done:** Levels 1–9 in full, across both parts together.
This milestone's Level 5 (Security Done) is held to the same weight as
M2.2's SafetyValidator, given what is actually being protected against.

**Estimated Complexity:** Medium — the guard mechanism needs to be
genuinely hard to bypass, not a convention that can be silently skipped;
Part 2 reuses an already-proven pattern against two more targets, not a
new investigation.
**Risk Level:** Low going forward, but the finding that motivated it was
High — this milestone exists because a real boundary was already crossed
once, and Part 2 exists because a second, related boundary was found
crossed during this same milestone's own validation.

**Expected Output:** No future test run — this milestone, M2.1.8,
M2.1.9, M2.1.10, or any future phase — can touch any of Aether's three
real production data stores by accident, structurally, not by
discipline alone.

---

### M2.1.8 — MEMORY QUALITY: IMMEDIATE FACT CAPTURE AND CONSOLIDATION THRESHOLD

**Purpose:** Resolve DEBT-009 — the most significant of the five
remaining items. A short, realistic conversation ("My name is Alex")
never produces a durable, cleanly-recallable fact, because
`consolidation_min_messages=5` is never reached by normal short
exchanges, and even when consolidation does run, a local 3B model's
extraction quality on a short episode is unreliable. This means
Phase 1's original M1.9 TEXT MILESTONE claim — that Aether recalls a
stated name across a restart — was very likely never genuinely
validated, since real consolidation never ran in Phase 1 at all
(confirmed by DEBT-002).

**Objectives:** Give `ConversationAgent` the ability to recognize an
explicit, durable, stated fact in the moment it's said, and store it
immediately as a clean `MemoryType.FACT` with high importance — not
only deferred to end-of-session consolidation. Separately, lower
`consolidation_min_messages` from 5 to 3, a more realistic threshold for
casual conversation without triggering a consolidation LLM call on
every single turn. Prove both against a corrected, honest re-run of the
TEXT MILESTONE sequence.

**A genuine design tradeoff, not a hidden decision:** per-turn fact
recognition means one additional `ModelTier.LOCAL` call after every
conversational turn — free in dollar cost, but real in latency and
VRAM-shared time on the target hardware. The alternative is a
lightweight keyword pre-filter (phrases like "my name is," "I work at,"
"remember that") that only triggers the fact-check call when a turn
looks likely to contain one. State which approach was taken and why in
the milestone's own report — this is a real tradeoff worth recording,
not silently resolved either way.

**Deliverables:** A short (2–3 message), realistic conversation stating
a name, followed by a restart, followed by a successful, honest recall
— the corrected version of Phase 1's original, never-actually-proven
claim.

**Dependencies:** M2.1.7 (this milestone's own testing — including a
full consolidation and fact-recognition test pass — runs against the
now-isolated, guarded test environment — database, Qdrant, and Redis
alike; it does not proceed against any production data store).

**Files Created:** `tests/integration/test_fact_capture_live.py`.
**Files Modified:** `aether/agents/_implementations/conversation.py`
(fact recognition after each turn, using `LLMRouter.complete()` with a
structured `response_schema` — reusing the existing structured-output
mechanism, not inventing a new one), `config/default.yaml`
(`consolidation_min_messages: 5` → `3`), `aether/core/config.py` if the
field's default needs updating there too.
**Public APIs:** None new — this uses `MemoryAPI.remember()`, already
public, already used by `ConversationAgent` every turn; only what gets
stored and with what `MemoryType`/importance changes.
**Internal APIs:** None.

**Tests Required:** Fact recognition tested directly — a turn
containing "my name is Alex" produces a `MemoryType.FACT` memory with
content resembling "User's name is Alex," not a generic episode
summary. A turn with no stated fact produces no additional memory
beyond the existing per-turn episode. The full short-conversation,
restart, recall cycle, end to end, against the real pipeline.

**Validation Required:** The corrected TEXT MILESTONE sequence
(Milestone M1.9's original steps) re-run manually and witnessed,
specifically including a SHORT conversation (2–3 messages, not the
5-plus needed to trigger M2.1.6's consolidation test) stating a name,
and successfully recalling it after restart.

**Architecture Review:** V1_TECHNICAL_SPECIFICATION.md Section 8.6
(`ConversationAgent`'s system prompt and turn logic) — this extends,
does not replace, the existing per-turn `self._remember()` call already
specified there.

**Security Review:** None new.

**Performance Review:** The added per-turn fact-check call (or its
keyword-gated equivalent) measured and recorded — confirm it does not
push conversational turn latency past Phase 1's existing expectations by
an unreasonable margin. M2.1.7's execution observed a CUDA out-of-memory
failure on the live consolidation test under concurrent test load,
attributed to VRAM contention on the RTX 4050's 6GB budget rather than a
code defect. This milestone's live tests — which exercise the same
Ollama-backed consolidation path repeatedly, plus new per-turn LLM calls
— are not run in parallel with other GPU-bound tests (voice/STT tests
in particular); sequence test execution to avoid concurrent Whisper and
Ollama residency during this milestone's own test run, and report
whether the OOM recurs even with that sequencing.

**Documentation Updates:** `docs/technical-debt/DEBT_REGISTER.md` — mark
DEBT-009 resolved. `V1_TECHNICAL_SPECIFICATION.md` Section 8.6 updated
with the fact-recognition addition and the corrected threshold value.

**Definition of Done:** Levels 1–10 in full — this milestone's manual,
corrected TEXT MILESTONE re-run is its own Level 10 checkpoint, and the
one that should have closed Phase 1 in the first place.

**Estimated Complexity:** Medium-High — this is the most architecturally
substantive of the five remaining items, though it reuses existing
mechanisms rather than inventing new ones.
**Risk Level:** High in significance — this is the core memory promise
the entire project is named for.

**Expected Output:** Aether genuinely remembers a name stated in an
ordinary short conversation, across a restart — proven honestly, for
the first time.

---

### M2.1.9 — CODEBASE-WIDE LINT & TYPE REMEDIATION

**Purpose:** Resolve DEBT-005 — 152 ruff errors, 14 unformatted files,
28 mypy `--strict` errors, independent of and predating M2.1.
`services/voice/` carries the majority.

**Objectives:** Bring the full tree to a clean baseline, split by
directory per the debt register's own resolution plan: `services/voice/`
first, then `aether/memory/_stores/vector_store.py`, remaining issues in
`aether/session/manager.py` beyond what M2.1.5 already fixed, and
`aether/core/kernel.py`. Explicitly excludes `cli.py` and `api.py` —
M2.1.6's required rewrite already leaves both clean.

**Deliverables:** `uv run ruff check .` and `uv run mypy aether/
services/ --strict` both clean across the entire tree.

**Dependencies:** M2.1.8 (sequenced after the test-isolation and
memory-quality fixes so this milestone's own regression testing runs
against the safe, isolated test database M2.1.7 establishes). Scope
also explicitly assumes `cli.py`/`api.py` are already clean from M2.1.6,
to avoid duplicate work.

**Files Created:** None.
**Files Modified:** `services/voice/*.py` (all files), `aether/memory/
_stores/vector_store.py`, `aether/session/manager.py` (lint/type only —
no logic change), `aether/core/kernel.py`.
**Public APIs:** None — this milestone changes no behavior.
**Internal APIs:** None.

**Tests Required:** None new. The existing suite is the regression
guard — any test failure introduced by a "pure" lint/type fix indicates
the fix was not actually behavior-preserving and must be corrected.

**Validation Required:** `uv run ruff check .` → zero errors, full tree.
`uv run ruff format --check .` → zero unformatted files. `uv run mypy
aether/ services/ --strict` → zero errors, full tree.

**Architecture Review:** No new architectural surface — confirm no fix
crosses a module boundary while "cleaning up" an import.

**Security Review:** None new.

**Performance Review:** Milestone M1.10's Voice Milestone six-step
sequence re-run, given this milestone's majority scope is
`services/voice/` — confirming type/lint fixes did not silently change
runtime behavior.

**Documentation Updates:** None required beyond `CHANGELOG.md`.

**Definition of Done:** Levels 1, 2, 3, 4 (Architecture and Testing Done
via full regression pass), 9. Levels 5–7 are not newly exercised since
no new capability, security surface, or documentation is introduced.

**Estimated Complexity:** Medium — high in volume, low in individual
difficulty; mechanical work with a real regression-testing obligation.
**Risk Level:** Medium — the risk is entirely in "pure" fixes turning out
not to be behavior-preserving; mitigated by the mandatory M1.10 re-run.

**Expected Output:** A clean lint/type baseline for the entire tree
except what M2.1.6 already cleaned, with Phase 1's voice pipeline proven
unaffected.

---

### M2.1.10 — TEST FIXTURE AND SCRIPT ROBUSTNESS CLEANUP

**Purpose:** Resolve DEBT-006 — the smallest and lowest-priority of the
three, addressed now by explicit developer decision rather than left to
accumulate further or wait for M2.15.

**Objectives:** Correct `test_task_workflow`'s outdated `AgentTask`
shape (using the same locked fields — `description`, `goal`,
`input_data` — this whole remediation sequence has now corrected
elsewhere). Correct `test_event_flow`'s stale `task_filter` mock
signature — the specific remaining defect M2.1.5 already found but
explicitly did not touch. Fix `start.ps1`/`stop.ps1` treating
`docker-compose`'s normal stderr progress output as a failure signal.

**Deliverables:** Both named tests passing for the correct reason, not
skipped or loosened. `start.ps1`/`stop.ps1` usable without the developer
needing to bypass them manually, as M2.1's and M2.1.5's own execution
reports both had to do.

**Dependencies:** M2.1.9 (sequenced last per the debt register's
original priority ordering; no genuine technical dependency on it).

**Files Created:** None.
**Files Modified:** `tests/integration/test_task_workflow.py`,
`tests/integration/test_event_flow.py`,
`infrastructure/scripts/start.ps1`, `infrastructure/scripts/stop.ps1`.
**Public APIs:** None.
**Internal APIs:** None.

**Tests Required:** The two named tests, corrected and passing.

**Validation Required:** `.\infrastructure\scripts\start.ps1` completes
without manual intervention or a stderr-triggered abort. Same for
`stop.ps1`.

**Architecture Review:** None — test and script fixes only.

**Security Review:** None new.

**Performance Review:** None new.

**Documentation Updates:** `docs/technical-debt/DEBT_REGISTER.md` — mark
DEBT-006 resolved.

**Definition of Done:** Levels 1, 2, 4, 9.

**Estimated Complexity:** Low.
**Risk Level:** Low.

**Expected Output:** A fully green test suite and reliable start/stop
scripts — the last of the four debt items opened by the M2.1 review
resolved, clearing the way to M2.2 with a genuinely clean foundation.

---

### M2.2 — SECURITY MODULE (SAFETYVALIDATOR)

**Purpose:** Implement the single rule-based enforcement gate every
privileged action in this phase, and every phase after it, must pass
through.

**Objectives:** Implement `aether/security/` in full per PHASE_2_
TECHNICAL_SPECIFICATION.md Section 4.1 and Section 5.1; achieve
near-complete branch coverage given this module's security-critical
classification.

**Deliverables:** `SafetyValidator` with all four locked methods;
`.aether/permissions.yaml` parsing; `ValidationResult`, `Permission`,
`DestructiveOperation` models.

**Dependencies:** M2.1 (sequenced after, per the no-parallel-
implementation rule in Section 16 of this plan; `SafetyValidator` itself
has no technical dependency on the database).

**Files Created:** `aether/security/__init__.py`, `validator.py`,
`_permissions_loader.py`, `models.py`.
**Files Modified:** None.
**Public APIs:** `SafetyValidator.validate_file_operation()`,
`.validate_app_launch()`, `.validate_browser_action()`, `.is_destructive()`
— all four exactly as locked in PHASE_2_TECHNICAL_SPECIFICATION.md
Section 5.1.
**Internal APIs:** `_permissions_loader`'s YAML parsing functions — never
imported outside `aether/security/`.

**Tests Required:** Every individual entry in `.aether/permissions.yaml`'s
`forbidden_launch` list tested as blocked, separately. Every entry in
`forbidden_paths` tested as blocked, separately. Destructive operations
without a `confirmation_token` tested as denied; the same operations with
a valid token tested as permitted. `is_destructive()` tested against every
operation type this phase introduces.

**Validation Required:** `uv run pytest tests/unit/test_safety_
validator.py -v` — all tests pass; manual confirmation that zero LLM
calls occur anywhere in the validation path (grep for `llm_router` or
`ModelTier` inside `aether/security/` must return no matches).

**Architecture Review:** PHASE_2_TECHNICAL_SPECIFICATION.md Section 4.1
(module placement rationale — a peer of `memory/` and `llm/`, not nested
under `pc_control/`) and Section 5.1 (locked interface).

**Security Review:** PHASE_2_TECHNICAL_SPECIFICATION.md Section 12,
items 1, 3, 4, 7, 8 in full — this milestone is the direct implementation
of that section.

**Performance Review:** PHASE_2_TECHNICAL_SPECIFICATION.md Section 13's
`SafetyValidator` target: p50 < 10ms, p95 < 25ms.

**Documentation Updates:** Module docstring labeling `aether/security/`
as security-sensitive per AI_GENERATION_RULES_V2.md Section 13.1.

**Definition of Done:** Levels 1–9 in full, with Level 5 (Security Done)
held to the elevated coverage target this module's classification
requires, per AI_GENERATION_RULES_V2.md Section 13.

**Estimated Complexity:** Medium.
**Risk Level:** High — not because the logic is complex, but because a
defect here has outsized consequence relative to its size.

**Expected Output:** A working, fully tested permission gate that every
subsequent PC control milestone depends on and cannot bypass.

---

### M2.3 — PC CONTROL CORE: APPLICATION CONTROL

**Purpose:** Implement the application launch/close/focus capability
behind `PCControlAPI`, gated by `SafetyValidator`.

**Objectives:** Implement `_control/app_control.py` and the Windows
adapter's application-control functions; wire `execute_action()` for
application operations and `list_applications()`.

**Deliverables:** Working application launch, close, and focus, each
validated through `SafetyValidator.validate_app_launch()` before any OS
call.

**Dependencies:** M2.2 (`SafetyValidator` must exist and be tested first
— no application control code is written before its gate exists).

**Files Created:** `aether/pc_control/__init__.py`, `api.py` (initial —
application methods only; file and system methods added in M2.4–M2.5),
`_control/app_control.py`, `_adapters/windows.py` (initial — application
functions only).
**Files Modified:** None.
**Public APIs:** `PCControlAPI.execute_action()` (application operations
only at this point), `.list_applications()`.
**Internal APIs:** `_control.app_control` functions; `_adapters.windows`
application functions — never imported outside `pc_control/`.

**Tests Required:** Unit tests with mocked `_adapters.windows` and mocked
`SafetyValidator`, confirming the validator is always called before
dispatch. A test proving every `forbidden_launch` entry is rejected at
this layer too, not only at the `SafetyValidator` layer directly — a
defense-in-depth check.

**Validation Required:** `uv run pytest tests/unit/test_pc_control_
api.py -v -k app_control`; manual smoke test launching and closing an
allowed application (e.g., `notepad.exe`) on the actual development
machine.

**Architecture Review:** PHASE_2_TECHNICAL_SPECIFICATION.md Section 4.2,
Section 5.2 (`execute_action`, `list_applications` signatures).

**Security Review:** PHASE_2_TECHNICAL_SPECIFICATION.md Section 12, item
2 — "No code path, tool, or agent may call an `_adapters/windows.py`
function directly."

**Performance Review:** `execute_action` non-destructive target: p50 <
500ms, p95 < 1000ms, per Section 13.

**Documentation Updates:** `PCControlAPI` docstring covering the
application-control subset implemented so far.

**Definition of Done:** Levels 1–9.

**Estimated Complexity:** Medium — first real integration with the
Windows automation stack (`pywinauto`/`pyautogui`).
**Risk Level:** Medium — Windows API fragility, per PHASE_2_TECHNICAL_
SPECIFICATION.md Section 16's first named risk.

**Expected Output:** Aether can launch, close, and focus applications
from the approved allowlist, and cannot launch anything from the
forbidden list under any phrasing of the request.

---

### M2.4 — PC CONTROL CORE: FILE OPERATIONS

**Purpose:** Implement file search, read, and move behind `PCControlAPI`,
gated by `SafetyValidator`.

**Objectives:** Implement `_control/file_ops.py`; extend `api.py` with
`search_files()`, `read_file()`, and the file-operation branch of
`execute_action()`.

**Deliverables:** Working file search, read, and move, each validated
through `SafetyValidator.validate_file_operation()`; destructive file
operations (overwrite, delete) gated by `confirmation_token`.

**Dependencies:** M2.2. Sequenced after M2.3 by the no-parallel rule, not
by a technical dependency on application control.

**Files Created:** `aether/pc_control/_control/file_ops.py`.
**Files Modified:** `aether/pc_control/api.py` (extended),
`_adapters/windows.py` (extended with file-system functions where
Windows-specific behavior is needed beyond Python's standard library).
**Public APIs:** `PCControlAPI.search_files()`, `.read_file()`,
`.execute_action()` (file operations branch).
**Internal APIs:** `_control.file_ops` functions.

**Tests Required:** Every entry in `.aether/permissions.yaml`'s
`forbidden_paths` tested as blocked at this layer. Destructive operations
without `confirmation_token` tested as denied; with a valid token, tested
as permitted. `max_file_size_mb` and `allow_hidden_files` settings tested
as enforced.

**Validation Required:** `uv run pytest tests/unit/test_pc_control_
api.py -v -k file_ops`; manual smoke test searching and reading a file
within an approved directory, and confirming a read attempt outside
`read_paths` is denied.

**Architecture Review:** PHASE_2_TECHNICAL_SPECIFICATION.md Section 4.2,
Section 5.2.

**Security Review:** PHASE_2_TECHNICAL_SPECIFICATION.md Section 12, items
2 and 4 (confirmation gate for destructive operations).

**Performance Review:** File search target: p50 < 1000ms, p95 < 2000ms,
per Section 13.

**Documentation Updates:** `PCControlAPI` docstring extended.

**Definition of Done:** Levels 1–9.

**Estimated Complexity:** Medium.
**Risk Level:** Medium — file operations carry real consequence if
`SafetyValidator`'s path checks have a gap; mitigated by M2.2's coverage
target.

**Expected Output:** Aether can search, read, and move files within
permitted directories, and cannot touch anything in `forbidden_paths`
under any phrasing.

---

### M2.5 — PC CONTROL CORE: SYSTEM MONITORING

**Purpose:** Implement system-state observation behind `PCControlAPI`.

**Objectives:** Implement `_control/system_monitor.py`; extend `api.py`
with `get_system_state()`; emit `system.stats.snapshot`.

**Deliverables:** CPU, memory, disk, and process-list monitoring,
read-only, requiring no `SafetyValidator` gate since no state-changing
action occurs.

**Dependencies:** M2.2 (module boundary consistency — every
`pc_control/` submodule is built under the same module regardless of
whether a given capability needs validation).

**Files Created:** `aether/pc_control/_control/system_monitor.py`.
**Files Modified:** `aether/pc_control/api.py` (extended), `__init__.py`
(export `SystemStats`).
**Public APIs:** `PCControlAPI.get_system_state()`.
**Internal APIs:** `_control.system_monitor` functions.

**Tests Required:** `get_system_state()` returns a well-formed
`SystemStats` object under normal conditions; a mocked failure of the
underlying OS query is handled without crashing the caller.

**Validation Required:** `uv run pytest tests/unit/test_pc_control_
api.py -v -k system_monitor`; manual confirmation that returned CPU/
memory/disk percentages are plausible on the actual development machine.

**Architecture Review:** PHASE_2_TECHNICAL_SPECIFICATION.md Section 4.2,
Section 7 (event contract for `system.stats.snapshot`).

**Security Review:** Read-only capability; confirm no write or execute
path is exposed by this milestone.

**Performance Review:** `get_system_state()` target: p50 < 200ms, p95 <
400ms, per Section 13.

**Documentation Updates:** `PCControlAPI` docstring completed for all
three capability areas (application, file, system).

**Definition of Done:** Levels 1–9.

**Estimated Complexity:** Low-Medium.
**Risk Level:** Low — read-only, no permission surface.

**Expected Output:** `PCControlAPI` (Stage A, in-process form) is
functionally complete across all three capability areas the Technical
Specification defines.

---

### M2.6 — CAPABILITY REGISTRY

**Purpose:** Implement the schema and registry class formalized in
AETHER_INTELLIGENCE_ARCHITECTURE.md Section 19 and PHASE_2_TECHNICAL_
SPECIFICATION.md Section 10.3.

**Objectives:** Implement `CapabilityRegistry`; register Phase 2's three
capabilities (`conversational_response`, `file_operation_reasoning`,
`system_monitoring_interpretation`); add the additive `capability`
`ClassVar` to `BaseAgent`.

**Deliverables:** A working registry resolving each capability to a
`ModelTier` value, exactly as PHASE_2_TECHNICAL_SPECIFICATION.md Section
10.3 specifies — no multi-engine resolution logic is introduced here,
per that section's explicit scope boundary.

**Dependencies:** M2.3–M2.5 (the two PC-control-specific capabilities
being registered describe modules that must exist first for the
registration to be meaningful, even though the registry class itself has
no strict technical dependency on them).

**Files Created:** `aether/llm/_capability_registry.py` (private —
registered capabilities are read through `LLMRouter`, not a new public
entry point, preserving the LLM boundary already locked in
V1_TECHNICAL_SPECIFICATION.md Section 6).
**Files Modified:** `aether/agents/base.py` (additive `capability:
ClassVar[str | None] = None`), `aether/agents/_implementations/
conversation.py` (add `capability = "conversational_response"` —
the only Phase 1 file this plan modifies).
**Public APIs:** None new — capability resolution is consumed internally
by `LLMRouter`, which already exposes `get_available_models()`.
**Internal APIs:** `CapabilityRegistry.register()`, `.resolve()`,
`.get_definition()`, per PHASE_2_TECHNICAL_SPECIFICATION.md Section
10.3's interface description.

**Tests Required:** Registering a capability and resolving it returns the
expected `ModelTier`. Resolving an unregistered capability raises a
specific, named error rather than failing silently. `ConversationAgent`'s
existing behavior is unchanged after its additive `capability` field is
set — a regression test, not a new-feature test.

**Validation Required:** `uv run pytest tests/unit/test_capability_
registry.py -v`; confirm `ConversationAgent`'s existing Phase 1 tests
(M1.7) still pass unmodified.

**Architecture Review:** PHASE_2_TECHNICAL_SPECIFICATION.md Section 10.3
and AETHER_INTELLIGENCE_ARCHITECTURE.md Section 19 in full — this
milestone is the direct implementation of both.

**Security Review:** None new — this milestone touches no privileged
operation.

**Performance Review:** Registry resolution is an in-memory dictionary
lookup; no new measured path is required beyond confirming it adds no
observable latency to existing LLM calls.

**Documentation Updates:** `V1_TECHNICAL_SPECIFICATION.md` Section 2.7
(`BaseAgent`) annotated to note the additive `capability` field, per
ADR-011 Gate Q-4.

**Definition of Done:** Levels 1–9.

**Estimated Complexity:** Medium — a new pattern, though a well-specified
one.
**Risk Level:** Low — purely additive; no existing behavior changes.

**Expected Output:** Agents can declare a named capability instead of a
bare `ModelTier`, with Phase 1's `ConversationAgent` migrated to the new
pattern as the first real usage.

---

### M2.7 — CONCURRENT TASK EXECUTION MODEL (STATE VOCABULARY)

**Purpose:** Introduce the nine-state task lifecycle vocabulary from
PHASE_2_TECHNICAL_SPECIFICATION.md Section 10.4 as observable,
structured logging — not new scheduling logic.

**Objectives:** Define the `TaskState` enum; instrument
`AgentRuntime.execute()`'s existing call chain to log `RUNNING` on
dispatch, `WAITING` around each tool call, and the appropriate terminal
state on completion — using the new vocabulary to describe behavior that
already exists, per that section's explicit statement that `BLOCKED` and
`PAUSED` remain dormant in Phase 2.

**Deliverables:** `TaskState` enum available for logging and future
consumption; no new decision-making logic, since `AgentRuntime` remains
the sequential runner Phase 1 built.

**Dependencies:** None Phase-2-internal — this instruments Phase 1's
existing `AgentRuntime`. Sequenced here by narrative grouping with the
other Runtime Changes milestones (M2.6, M2.8, M2.9), not by technical
necessity.

**Files Created:** None.
**Files Modified:** `aether/agents/runtime.py` (add `TaskState` logging
at existing transition points — no new branches of control flow).
**Public APIs:** `TaskState` enum, exported from `aether/agents/`.
**Internal APIs:** None.

**Tests Required:** A test confirming a successful task execution logs
`RUNNING` then a terminal state; a test confirming a task involving a
tool call logs `WAITING` around that call. A test confirming `BLOCKED`
and `PAUSED` are defined but never produced by any Phase 2 code path —
an explicit non-production test, not an omission.

**Validation Required:** `uv run pytest tests/unit/test_task_state.py
-v`; confirm Phase 1's existing `AgentRuntime` tests (M1.7) still pass
unmodified — this milestone must not change behavior, only observability.

**Architecture Review:** PHASE_2_TECHNICAL_SPECIFICATION.md Section 10.4
and AETHER_INTELLIGENCE_ARCHITECTURE.md Section 20 in full.

**Security Review:** None new.

**Performance Review:** Confirm added logging introduces no measurable
latency regression to `AgentRuntime.execute()`.

**Documentation Updates:** Note in `V1_TECHNICAL_SPECIFICATION.md`
Section 2.7 that `AgentTask` lifecycle logging now uses the `TaskState`
vocabulary, with the explicit disambiguation from `TaskManager`'s
`TaskStatus` already established in PHASE_2_TECHNICAL_SPECIFICATION.md
Section 10.4 carried into the annotation.

**Definition of Done:** Levels 1–9 — despite being lightweight,
instrumentation of a production code path still climbs every level.

**Estimated Complexity:** Low-Medium.
**Risk Level:** Low — additive logging only; explicit regression tests
guard against behavior change.

**Expected Output:** Every task execution in Aether is now observable
through a formal, named lifecycle vocabulary, ready for Runtime Telemetry
(M2.9) to consume.

---

### M2.8 — AGENT HEALTH INTERFACE

**Purpose:** Implement the seven-method health contract formalized in
AETHER_INTELLIGENCE_ARCHITECTURE.md Section 21 as an additive extension
to `BaseAgent`.

**Objectives:** Implement `is_alive()`, `health_status()`,
`current_load()`, `estimated_completion()`, `last_error()`,
`active_tasks()`, `queued_tasks()` with default implementations on
`BaseAgent`; implement the `RecoveryState` enum.

**Deliverables:** Every existing and future agent gains these methods
without needing to override any of them, per the additive-only
requirement in both governing sections.

**Dependencies:** M2.6 (agents now carry a `capability` field this
interface's `health_status()` can reference when reporting `DEGRADED` due
to fallback-engine resolution).

**Files Created:** None.
**Files Modified:** `aether/agents/base.py` (seven new methods, default
implementations), `aether/agents/models.py` or equivalent (add
`HealthStatus`, `RecoveryState` enums).
**Public APIs:** The seven methods listed above, plus `HealthStatus`
(`HEALTHY | DEGRADED | UNHEALTHY`) and `RecoveryState` (`NONE |
ATTEMPTING | ESCALATED`).
**Internal APIs:** None.

**Tests Required:** Default implementations tested on a minimal test
agent subclass. `health_status()` tested as returning `DEGRADED` when
`BudgetStatus.active_tier_override` is set, per AETHER_INTELLIGENCE_
ARCHITECTURE.md Section 21.2's explicit example. `active_tasks()` and
`queued_tasks()` tested as returning at most one element under Phase 2's
sequential runner.

**Validation Required:** `uv run pytest tests/unit/test_agent_health.py
-v`; confirm `ConversationAgent`, `FileAgent` (once M2.11 exists — this
test is extended, not repeated, at that point), and any future agent
inherit these methods without modification.

**Architecture Review:** AETHER_INTELLIGENCE_ARCHITECTURE.md Section 21
in full; PHASE_2_TECHNICAL_SPECIFICATION.md Section 10.5.

**Security Review:** None new.

**Performance Review:** Confirm health-check calls do not block or
measurably delay an agent's actual task execution.

**Documentation Updates:** `BaseAgent` docstring extended in
`V1_TECHNICAL_SPECIFICATION.md` Section 2.7.

**Definition of Done:** Levels 1–9.

**Estimated Complexity:** Low — additive with sensible defaults, per the
governing sections' own description.
**Risk Level:** Low.

**Expected Output:** Every agent in the system is now individually
health-observable, laying the groundwork the future Health Monitor Agent
will consume.

---

### M2.9 — RUNTIME TELEMETRY EXTENSIONS

**Purpose:** Extend Phase 1's existing event bus with the resource- and
retry-level telemetry formalized in AETHER_INTELLIGENCE_ARCHITECTURE.md
Section 22 and PHASE_2_TECHNICAL_SPECIFICATION.md Section 10.6.

**Objectives:** Introduce `runtime.resource.snapshot`; add `retry_count`
additively to `llm.call.completed` and `agent.run.completed`.

**Deliverables:** A periodic resource-usage event; two existing event
payloads gaining one field each, with no version bump required per
V1_TECHNICAL_SPECIFICATION.md Section 7.2's additive-change rule.

**Dependencies:** M2.7 (Queue Time, one of this milestone's telemetry
dimensions, is only meaningful once `TaskState` timestamps exist to
compute it from).

**Files Created:** None.
**Files Modified:** `aether/core/events.py` (register the new event
type), `aether/llm/router.py` (add `retry_count` to the emitted payload),
`aether/agents/runtime.py` (same, for `agent.run.completed`).
**Public APIs:** None new — this extends existing event payloads and adds
one new event type to the already-public `EventBus.emit()` surface.
**Internal APIs:** A lightweight periodic sampler for CPU/GPU/RAM,
private to `aether/core/`.

**Tests Required:** `runtime.resource.snapshot` emitted at the configured
interval with well-formed fields. `retry_count` present and accurate on
both extended events under a simulated retry scenario. A test confirming
existing consumers of `llm.call.completed` and `agent.run.completed` do
not break when the new field is present but unread — the additive-change
guarantee, verified, not assumed.

**Validation Required:** `uv run pytest tests/unit/test_telemetry.py -v`;
inspect `XRANGE aether:events` after a test run to confirm the new event
type and extended payloads appear correctly formed.

**Architecture Review:** AETHER_INTELLIGENCE_ARCHITECTURE.md Section 22
and PHASE_2_TECHNICAL_SPECIFICATION.md Section 10.6 in full.

**Security Review:** Confirm `runtime.resource.snapshot` carries no
sensitive data (process names and percentages only, per the locked
schema).

**Performance Review:** Confirm the periodic sampler's own resource
footprint is negligible relative to what it measures.

**Documentation Updates:** Event catalog in `V1_TECHNICAL_
SPECIFICATION.md` Section 7.3 extended with the new event type and the
two additive fields.

**Definition of Done:** Levels 1–9.

**Estimated Complexity:** Low-Medium.
**Risk Level:** Low.

**Expected Output:** The event bus now carries resource and retry
telemetry, ready to feed ADR-011 Section 10's performance baseline
process without manual timing.

---

### M2.10 — PC CONTROL TOOL SUITE

**Purpose:** Wrap the now-complete `PCControlAPI` (Stage A) in the
`BaseTool` interface and register it with `ToolRegistry`.

**Objectives:** Implement all eight tools named in PHASE_2_TECHNICAL_
SPECIFICATION.md Section 4.4.

**Deliverables:** `launch_app`, `close_app`, `focus_app`,
`list_running_apps`, `search_files`, `read_file_content`, `move_file`,
`get_system_stats` — each a thin `BaseTool` subclass delegating to
`PCControlAPI`, following exactly the pattern Phase 1's `datetime_tools.py`
and `search_tools.py` already established (V1_TECHNICAL_SPECIFICATION.md
Milestone M1.6).

**Dependencies:** M2.3, M2.4, M2.5 (every capability area of
`PCControlAPI` must exist before its tool wrapper can be written).

**Files Created:** `aether/tools/_implementations/pc_control_tools.py`.
**Files Modified:** None (tool registration happens at kernel
initialization, addressed in M2.12, not by modifying `registry.py`
itself — the registry's `register()` method already accepts new tools
without change, per its locked interface).
**Public APIs:** None new beyond the standard `BaseTool.execute()`
contract each of the eight tools implements.
**Internal APIs:** None — each tool calls `PCControlAPI` through its
already-public interface, never through `_control/` or `_adapters/`
directly.

**Tests Required:** Each of the eight tools tested for its success path,
its invalid-input path (Pydantic validation failure), and its
permission-denied path (mocked `SafetyValidator` returning `allowed:
False`), per ADR-011 Section 3.4's requirement of success, invalid-input,
and failure-path coverage for every new tool.

**Validation Required:** `uv run pytest tests/unit/test_pc_control_
tools.py -v`; `ToolRegistry.get_function_schemas()` produces valid
Anthropic-format schemas for all eight.

**Architecture Review:** PHASE_2_TECHNICAL_SPECIFICATION.md Section 4.4;
confirm no tool imports `aether.pc_control._control` or
`aether.pc_control._adapters` directly — only `aether.pc_control.api`.

**Security Review:** Confirm every tool that maps to a
`SafetyValidator`-gated `PCControlAPI` method inherits that gating
correctly — no tool re-implements or shortcuts validation itself.

**Performance Review:** No new measured path beyond what M2.3–M2.5
already established at the `PCControlAPI` layer; this milestone adds a
thin wrapper, not new latency.

**Documentation Updates:** `docs/guides/adding-a-pc-control-tool.md`
created, per PHASE_2_TECHNICAL_SPECIFICATION.md Section 15.

**Definition of Done:** Levels 1–9.

**Estimated Complexity:** Medium — eight tools, each needing its own
input/output schema, though individually straightforward.
**Risk Level:** Medium — the point at which a permission-gating mistake
would first become reachable by an agent, not just by direct API tests.

**Expected Output:** Eight new tools available to any agent whose
`allowed_tools` list includes them, each correctly gated by
`SafetyValidator` through `PCControlAPI`.

---

### M2.11 — FILEAGENT & SYSTEMAGENT

**Purpose:** Implement Phase 2's two new agents, exactly as their roles
are already fully defined in AETHER_INTELLIGENCE_ARCHITECTURE.md Section
7, Group B.

**Objectives:** Implement both agents per PHASE_2_TECHNICAL_
SPECIFICATION.md Section 5.3's locked declarations.

**Deliverables:** `FileAgent` (`capability = "file_operation_reasoning"`,
`llm_tier = ModelTier.CHEAP`, tools: `search_files`, `read_file_content`,
`move_file`) and `SystemAgent` (`capability =
"system_monitoring_interpretation"`, `llm_tier = ModelTier.CHEAP`, tools:
`launch_app`, `close_app`, `focus_app`, `list_running_apps`,
`get_system_stats`), both extending `BaseAgent` with zero changes to its
locked `execute()` signature.

**Dependencies:** M2.6 (capability declarations), M2.10 (tools to
declare in `allowed_tools`).

**Files Created:** `aether/agents/_implementations/file_agent.py`,
`system_agent.py`.
**Files Modified:** None.
**Public APIs:** None new — both agents are consumed exclusively through
`AgentRuntime.execute()`, the same locked entry point Phase 1's
`ConversationAgent` already uses.
**Internal APIs:** None — both use `self._invoke_tool()`,
`self._recall()`, `self._remember()` exclusively, never importing
`PCControlAPI`, `ToolRegistry`, or `MemoryAPI` directly, per V1_
TECHNICAL_SPECIFICATION.md Section 2.7's established pattern.

**Tests Required:** Each agent's ReAct loop tested end-to-end against a
representative task (e.g., "find files matching X" for `FileAgent`,
"what applications are running" for `SystemAgent`). A test confirming
neither agent can invoke a tool outside its declared `allowed_tools`.

**Validation Required:** `uv run pytest tests/unit/test_file_agent.py
tests/unit/test_system_agent.py -v`.

**Architecture Review:** AETHER_INTELLIGENCE_ARCHITECTURE.md Section 7,
Group B (File System Agent, PC Control Agent definitions) — this
milestone is the concrete implementation of those already-approved
roles. PHASE_2_TECHNICAL_SPECIFICATION.md Section 5.3.

**Security Review:** Confirm both agents' `allowed_tools` lists exactly
match Section 5.3 — no additional tool access beyond what was specified.

**Performance Review:** No new measured path; agent-level latency is a
composite of the tool and LLM calls already measured in earlier
milestones.

**Documentation Updates:** `V1_TECHNICAL_SPECIFICATION.md` agent roster
updated to include both.

**Definition of Done:** Levels 1–9.

**Estimated Complexity:** Medium.
**Risk Level:** Medium — first point where an LLM-driven reasoning loop
decides which PC control tool to call, making correctness of the ReAct
loop itself, not just the underlying tools, load-bearing.

**Expected Output:** Two working agents, registerable with
`AgentRuntime`, each conforming exactly to their already-approved
architectural role.

---

### M2.12 — KERNEL INTEGRATION

**Purpose:** Wire everything built in M2.2 through M2.11 into
`aether/core/kernel.py`'s existing initialization sequence.

**Objectives:** Insert the exact steps PHASE_2_TECHNICAL_SPECIFICATION.md
Section 10.1 specifies, at the exact dependency points named, with no
reordering of Phase 1's existing eleven steps.

**Deliverables:** `SafetyValidator` initialized; `PCControlAPI`
initialized; all new tools registered; `FileAgent` and `SystemAgent`
registered with `AgentRuntime`.

**Dependencies:** M2.2 through M2.11 (this milestone has no independent
content of its own — it is the wiring step that makes every prior
milestone reachable at runtime).

**Files Created:** None.
**Files Modified:** `aether/core/kernel.py` (insertions at steps 8a, 8b,
8c, and 9a, exactly as specified).
**Public APIs:** None new.
**Internal APIs:** None new.

**Tests Required:** Full kernel initialization test confirming all
eleven original Phase 1 steps still execute in their original order,
with the new insertions present and correctly positioned. A test
confirming kernel initialization fails loudly, not silently, if
`SafetyValidator` cannot load `.aether/permissions.yaml`.

**Validation Required:** `python -m aether` starts without error; log
output shows every registered agent (`conversation`, `file_agent`,
`system_agent`) and every registered tool (eleven total: Phase 1's three
plus Phase 2's eight) at startup.

**Architecture Review:** PHASE_2_TECHNICAL_SPECIFICATION.md Section 10.1
— exact-order compliance is the entire content of this review.

**Security Review:** Confirm `SafetyValidator` initializes before
`PCControlAPI` — an ordering mistake here would mean a window in which PC
control tools could theoretically dispatch before their gate exists.

**Performance Review:** Full cold-start time measured; confirm no
material regression from Phase 1's existing startup latency.

**Documentation Updates:** `V1_TECHNICAL_SPECIFICATION.md` Section 8
(kernel initialization sequence) updated with the final, as-implemented
step list.

**Definition of Done:** Levels 1–9. This milestone carries elevated
weight on Level 3 (Architecture Done) specifically, since ordering
correctness is its entire purpose.

**Estimated Complexity:** Low-Medium — the individual insertions are
small; the risk is in getting their order exactly right.
**Risk Level:** Medium — a regression risk to Phase 1's existing,
already-approved boot sequence, not a new-feature risk.

**Expected Output:** A fully wired `aether-core` process in which every
Phase 2 capability is reachable through the same kernel that has run
since Phase 1.

---

### M2.13 — PC CONTROL TRUST TEST

**Purpose:** Execute Phase 2's defining test — the acceptance proof this
phase's core capability, and its core boundary, both genuinely work.

**Objectives:** Execute PHASE_2_TECHNICAL_SPECIFICATION.md Section 14.2
in full: both the positive case (an allowed action succeeds, is logged,
is remembered) and the negative case (a forbidden action is refused,
logged, and clearly communicated) — with no exception, per AETHER_
DEFINITION_OF_DONE.md Non-Bypassable Rule NB-2.

**Deliverables:** A passing, recorded execution of both halves of the
test.

**Dependencies:** M2.12 (the full system must be wired and running for
this end-to-end test to execute at all).

**Files Created:** `tests/integration/test_pc_control_trust.py`.
**Files Modified:** None.
**Public APIs:** None — this milestone produces no new production code,
only the test that proves the prior eleven milestones' combined
correctness.
**Internal APIs:** None.

**Tests Required:** The PC Control Trust Test itself, in full, as
specified. Additionally, the Phase 1 regression suite (M1.5 cross-session
memory, M1.10 Voice Milestone) is re-run one final time in this
milestone's context — the first point at which the fully-integrated Phase
2 system exists to test Phase 1's guarantees against.

**Validation Required:** Manual, observed execution of both halves on the
actual development machine — not solely an automated `pytest` pass,
given this test's role as the phase's human-witnessed acceptance proof,
matching how Phase 1's Voice Milestone required the same standard.

**Architecture Review:** PHASE_2_TECHNICAL_SPECIFICATION.md Section 14.2
and Section 19.2 — this milestone directly satisfies the phase's stated
Acceptance Criteria for this specific test.

**Security Review:** The negative case *is* the security review, executed
as a test rather than only as a static check.

**Performance Review:** End-to-end latency for both halves measured and
recorded in `docs/performance/phase-2-baseline.md`.

**Documentation Updates:** Test result recorded in `CHANGELOG.md` with
explicit date, satisfying the evidentiary requirement for this
milestone's Definition of Done.

**Definition of Done:** Levels 1–10 — this milestone is Phase 2's
clearest single Level 10 (Production Ready) checkpoint, analogous to
Phase 1's M1.5 and M1.10.

**Estimated Complexity:** Low — this milestone writes a test, not new
production logic.
**Risk Level:** High in significance, though not in implementation
difficulty — failure here means Phase 2 is not done, regardless of how
well M2.2 through M2.12 otherwise performed.

**Expected Output:** Documented, witnessed proof that Aether can act on
the host machine within its granted permissions and correctly refuses to
act outside them.

---

### M2.14 — SERVICE EXTRACTION (STAGE B)

**Purpose:** Extract `PCControlAPI` from an in-process module into the
sandboxed `services/pc-control/` process, per the scheduled extraction
PHASE_2_TECHNICAL_SPECIFICATION.md Section 3.2–3.3 and V1 Foundation
Architecture Decision Section 4.1 both specify.

**Objectives:** Wrap `PCControlAPI` in FastAPI; create `PCControlClient`
in `aether-core`; update `start.ps1`.

**Deliverables:** `services/pc-control/` running as a genuinely separate,
sandboxed process; `FileAgent` and `SystemAgent` unmodified — per the
extraction mechanism's own promise, calling agents change zero lines of
code, because they already call through `PCControlAPI`'s interface, not
its implementation.

**Dependencies:** M2.13 (extraction is only attempted once the Trust Test
has proven the in-process implementation correct — extracting an
unproven implementation would only relocate an unverified risk).

**Files Created:** `services/pc-control/__init__.py`, `main.py`,
`server.py`.
**Files Modified:** `aether/pc_control/__init__.py` (export
`PCControlClient` alongside `PCControlAPI`), `infrastructure/scripts/
start.ps1` (add the new process to the startup sequence, following the
identical health-check-polling pattern already used for `aether-core` and
`aether-voice`).
**Public APIs:** The REST API in PHASE_2_TECHNICAL_SPECIFICATION.md
Section 6.2 — `POST /execute`, `GET /applications`, `GET /system-state`,
`POST /files/search`, `GET /health`.
**Internal APIs:** `PCControlClient`'s HTTP call implementation, private
to `aether/pc_control/`.

**Tests Required:** The PC Control Trust Test (M2.13) re-run against the
extracted service, confirming identical results. A test confirming
`services/pc-control/` has no network access to Redis, Qdrant, or the
database, per the sandboxing requirement already established for the
browser agent (V1 Foundation Architecture Decision Section 3.6).

**Validation Required:** `.\infrastructure\scripts\start.ps1` brings up
all three processes (`aether-core`, `aether-voice`, `aether-pc-control`)
cleanly from a cold state; killing the `aether-pc-control` process and
restarting it does not require restarting `aether-core`.

**Architecture Review:** V1 Foundation Architecture Decision Section 4.1
(the extraction pattern) — confirm the mechanical relocation promise
holds: zero lines changed in `FileAgent` or `SystemAgent`.

**Security Review:** V1 Foundation Architecture Decision Section 3.6's
sandboxing model, applied here for the first time to PC control rather
than only to the browser agent — no filesystem or database access from
the container beyond what the REST API explicitly exposes.

**Performance Review:** All Section 13 latency targets re-measured
against the extracted service; the added network hop is expected to add
measurable but bounded latency, tracked against the same p50/p95
thresholds.

**Documentation Updates:** `V1_TECHNICAL_SPECIFICATION.md` process
topology diagram updated to show the third process.

**Definition of Done:** Levels 1–9.

**Estimated Complexity:** Medium-High — process separation and container
sandboxing, done for a genuinely new service for the first time since
Phase 1's voice process.
**Risk Level:** Medium-High — the point where the extraction pattern's
"zero caller changes" promise is actually tested, not merely asserted.

**Expected Output:** PC control now runs as an isolated, independently
restartable process, exactly as scheduled from the start of this phase's
design.

---

### M2.15 — PHASE 2 CLOSURE PREPARATION

**Purpose:** Confirm the entire phase is regression-clean and
documentation-complete before Phase Review begins (AETHER_PHASE_
EXECUTION_WORKFLOW.md Step 20).

**Objectives:** Run the full test suite across the entire phase's scope;
finalize all documentation; confirm zero P1 technical debt remains open.

**Deliverables:** A repository state ready for the seven phase-closure
documents defined in AETHER_DEFINITION_OF_DONE.md Section 6 to be
produced.

**Dependencies:** M2.14 (every prior milestone complete).

**Files Created:** None.
**Files Modified:** `README.md` (Phase 2 milestone table fully checked),
`CHANGELOG.md` (Phase 2 summary entry).
**Public APIs:** None.
**Internal APIs:** None.

**Tests Required:** The complete suite — every unit, contract,
architecture, and integration test from M2.0 through M2.14, run together,
not milestone by milestone.

**Validation Required:** `uv run pytest tests/ -v`; `uv run lint-imports`;
`uv run mypy aether/ services/ --strict`; the full forbidden-pattern
scan, all across the entire phase's changed files.

**Architecture Review:** Full phase-wide audit per AETHER_PHASE_
EXECUTION_WORKFLOW.md Step 20's eight dimensions.

**Security Review:** Full phase-wide Security Gate (ADR-011 Section 4,
Gate Q-5), re-run across every file this phase touched.

**Performance Review:** `docs/performance/phase-2-baseline.md` finalized
with every measured path from M2.1, M2.2, M2.3–M2.5, M2.13, and M2.14.

**Documentation Updates:** Final synchronization pass across
`V1_TECHNICAL_SPECIFICATION.md`, confirming every Phase 2 addition is
reflected accurately.

**Definition of Done:** This milestone is where Level 11 (Release Ready)
is formally attempted, per AETHER_DEFINITION_OF_DONE.md's requirement
that every milestone independently reach Level 10 before the phase
attempts Level 11.

**Estimated Complexity:** Low — verification and consolidation, not new
implementation.
**Risk Level:** Low.

**Expected Output:** A phase in a fully verified, fully documented state,
ready for AETHER_PHASE_EXECUTION_WORKFLOW.md Steps 20–27 to formally
close it.

---

## 4. IMPLEMENTATION WAVES

The illustrative ten-wave grouping given in the request for this document
(Core Infrastructure / Security / PC Control Core / Agents / Tools /
Runtime Integration / Extraction / Testing / Documentation / Final
Validation) is not used verbatim here. Testing and Documentation are
deliberately *not* separate waves: AETHER_DEFINITION_OF_DONE.md's Level 4
(Testing Done) and Level 7 (Documentation Done) are climbed by every
individual milestone, not deferred to a phase-end pass — exactly the
pattern Phase 1 already established, where no milestone's plan ever
treated testing as a separate later phase. Deferring either to a
dedicated end-of-phase wave would contradict that already-approved
pattern. The nine waves below are derived from Phase 2's actual milestone
dependencies instead.

```
WAVE 1 — Foundation Preparation
  M2.0, M2.1, M2.1.5, M2.1.6, M2.1.7, M2.1.8, M2.1.9, M2.1.10
  Verify prerequisites; take the phase's highest-risk operation
  (database migration) first, while least new work is at stake.
  M2.1.5 through M2.1.10 were not originally planned here — each was
  inserted after the one before it surfaced further debt in pre-existing
  Phase 1 code, per Section 2's note above. M2.1.7 in particular exists
  because M2.1.6's execution touched real production data without prior
  authorization; no milestone after M2.1.6 runs its tests against
  anything but the isolated database M2.1.7 establishes.

WAVE 2 — Security Layer
  M2.2
  The gate every subsequent privileged operation depends on.

WAVE 3 — PC Control Core
  M2.3, M2.4, M2.5
  The three capability areas PCControlAPI (Stage A) is built from.

WAVE 4 — Intelligence Architecture Integration
  M2.6, M2.7, M2.8, M2.9
  The Capability Registry, Task Execution Model, Health Interface, and
  Telemetry sections appended to AETHER_INTELLIGENCE_ARCHITECTURE.md,
  formalized into working code.

WAVE 5 — Tools & Agents
  M2.10, M2.11
  The tool suite wrapping PCControlAPI, then the two agents that use it.

WAVE 6 — Runtime Integration
  M2.12
  Wiring everything into the kernel's existing initialization sequence.

WAVE 7 — Acceptance Proof
  M2.13
  The PC Control Trust Test — Phase 2's defining, human-witnessed gate.

WAVE 8 — Extraction
  M2.14
  Relocating PCControlAPI into its sandboxed service process.

WAVE 9 — Closure Preparation
  M2.15
  Full-phase regression and documentation consolidation, immediately
  preceding AETHER_PHASE_EXECUTION_WORKFLOW.md Steps 20–27.
```

---

## 5. DEPENDENCY GRAPH

Solid arrows mark hard technical dependencies — the target milestone
cannot function without the source milestone's output. Dotted notes mark
milestones that are sequenced by narrative grouping and the no-parallel-
implementation rule (Section 16), not by genuine technical necessity —
named explicitly so no one mistakes a scheduling choice for an
architectural constraint.

```
M2.0
  │
  ▼
M2.1
  │
  ▼
M2.1.5  (hard dependency on M2.1 — remediates defects that specific
  │       milestone's execution surfaced; not part of the original
  │       sixteen-milestone plan, inserted per Section 2's note)
  ▼
M2.1.6  (hard dependency on M2.1.5 — corrects a defect that
  │       milestone's diagnostic investigation surfaced)
  ▼
M2.1.7  (hard dependency on M2.1.6 — remediates a test-isolation
  │       gap that milestone's execution exposed; no further testing
  │       proceeds until this milestone's guard is in place)
  ▼
M2.1.8  (hard dependency on M2.1.7 — this milestone's own testing
  │       runs against the isolated database M2.1.7 establishes)
  ▼
M2.1.9  (hard dependency on M2.1.8 — sequenced after both correctness
  │       fixes; scope explicitly excludes cli.py/api.py because
  │       M2.1.6 already leaves them clean)
  ▼
M2.1.10 (sequenced after M2.1.9 by priority ordering, not genuine
  │       technical dependency)
  ▼
M2.2 ──────────┬─────────────┬─────────────┐
  │            │             │             │
  ▼            ▼             ▼             │
M2.3         M2.4          M2.5            │
  │            │             │             │
  └────────────┴─────┬───────┘             │
                      ▼                    │
                    M2.6 ◄──────────────────┘
                      │
                      ▼
                    M2.7   (no hard dependency on M2.6; sequenced here
                      │      by grouping only — see Wave 4)
                      ▼
                    M2.8   (hard dependency on M2.6 — health_status()
                      │      reports on capability-resolution state)
                      ▼
                    M2.9   (hard dependency on M2.7 — Queue Time needs
                      │      TaskState timestamps to compute)
                      ▼
                    M2.10  (hard dependency on M2.3, M2.4, M2.5)
                      │
                      ▼
                    M2.11  (hard dependency on M2.6, M2.10)
                      │
                      ▼
                    M2.12  (hard dependency on M2.2 through M2.11 —
                      │      the wiring step)
                      ▼
                    M2.13  (hard dependency on M2.12)
                      │
                      ▼
                    M2.14  (hard dependency on M2.13 — extraction only
                      │      after the in-process implementation is proven)
                      ▼
                    M2.15
```

No cycle exists in this graph: every arrow points strictly forward
through the sequence in Section 2, and no milestone's stated dependency
ever names a milestone that appears later in that sequence.

---

## 6. TESTING STRATEGY

Per-milestone test requirements are fully specified in each milestone's
own "Tests Required" and "Validation Required" fields in Section 3. This
section defines how those individual efforts compose into phase-wide
coverage.

**Unit Tests** — one test module per new component, run on every commit
via the existing CI pipeline (ADR-011 Section 4, Gate Q-3), never
deferred to a later milestone.

**Integration Tests** — `tests/integration/test_pc_control_trust.py`
(M2.13) is the phase's primary integration test; M2.1's and M2.14's
re-runs of Phase 1's own integration tests (cross-session memory, Voice
Milestone) are the phase's regression-integration tests.

**Security Tests** — concentrated in M2.2 (every forbidden-list entry
individually tested) and M2.13's negative case (the forbidden action is
attempted end-to-end, not only at the unit level).

**Regression Tests** — Phase 1's M1.5 and M1.10 tests are re-run at three
distinct points across this phase: immediately after M2.1 (confirming
the database migration didn't break them), at M2.13 (confirming the
fully-integrated Phase 2 system still preserves them), and at M2.15
(confirming the extracted service, M2.14, changed nothing about them
either). Three checkpoints, not one, because three distinct structural
changes — database backend, full integration, process extraction — each
carry independent regression risk.

**Performance Tests** — every milestone with a named target in Section
13 of PHASE_2_TECHNICAL_SPECIFICATION.md measures against it individually;
M2.15 consolidates all measurements into the phase-wide baseline document.

**Acceptance Tests** — the PC Control Trust Test (M2.13) is the phase's
sole acceptance test, matching the standard Phase 1 set with its own
cross-session memory and Voice Milestone tests: one test, both halves
required, no partial credit.

**Architecture Validation** — `lint-imports` and `mypy --strict` run on
every milestone without exception, per ADR-011 Section 4, Gate Q-2 — not
listed as a separate late-phase activity because it is already a
continuous one.

---

## 7. VALIDATION GATES

Every milestone in Section 3 passes through the same seven gates before
its Definition of Done is considered satisfied. Each gate maps directly
onto a level already defined in AETHER_DEFINITION_OF_DONE.md — this plan
does not introduce a second, parallel gate system.

| Gate | Maps to AETHER_DEFINITION_OF_DONE.md |
|---|---|
| Architecture Validation | Level 3 (Architecture Done) |
| Security Validation | Level 5 (Security Done) |
| Documentation Validation | Level 7 (Documentation Done) |
| Performance Validation | Level 6 (Performance Done) |
| Code Review | Level 9 (Review Done), human half |
| AI Review | Level 8 (AI Compliance Done) and Level 9's AI half |
| Human Review | Level 9 (Review Done), human half; Level 10's final approval |

Only after all seven pass does a milestone reach Level 10 (Production
Ready), and only then does the next milestone's own Wave 4-step cycle
(AETHER_PHASE_EXECUTION_WORKFLOW.md Steps 4–14) begin.

---

## 8. FAILURE HANDLING

If any milestone fails any validation gate in Section 7, implementation
stops immediately on that milestone. No subsequent milestone begins.
This is not a new rule this plan invents — it is the direct application
of AETHER_PHASE_EXECUTION_WORKFLOW.md Step 13 (Bug Fix Workflow) to Phase
2 specifically.

Every failure is documented before any fix is attempted, using this
record:

```
FAILURE RECORD — Milestone {M2.X}

Failure:      {what specifically did not pass, and which gate caught it}
Cause:        {the specific root cause, not a symptom description}
Resolution:   {the specific corrective action taken}
Retest:       {which validations were re-run, and their result}
Approval:     {developer sign-off that the milestone may now proceed}
```

The corrective action is scoped as a fix to the failing milestone, never
bundled with the next milestone's work, per AETHER_PHASE_EXECUTION_
WORKFLOW.md Step 13's explicit rule that a correction is "never a new
milestone, and never bundled with the next milestone's work." After a
fix, Section 7's full seven-gate sequence is re-run in its entirety for
that milestone — not only the gate that originally failed, per Step 14's
regression discipline.

---

## 9. ROLLBACK STRATEGY

Every milestone's rollback instruction follows ADR-010 Section 5
(Rollback Requirements). Rollback never damages completed work: because
every milestone through M2.11 modifies only files within its own newly
created module or makes small, additive changes to existing files (never
destructive rewrites), reverting any single milestone's commits removes
exactly what that milestone added and nothing else.

**M2.1 (PostgreSQL Migration):** Rollback restores the archived SQLite
file per V1_TECHNICAL_SPECIFICATION.md Section 3.3's own rollback note;
this is the phase's only milestone whose rollback requires a documented,
tested procedure beyond a simple git revert, given its Level 4
classification.

**M2.14 (Service Extraction):** Uniquely simple to roll back by design —
because `FileAgent` and `SystemAgent` call `PCControlAPI` through its
interface rather than its implementation (V1 Foundation Architecture
Decision Section 4.1), reverting to the in-process form requires only
swapping which implementation the kernel initializes, with zero changes
to any calling code. This is the same designed-in rollback safety the
extraction pattern was built to provide project-wide.

**All other milestones:** Standard git revert of that milestone's commit
range on `phase/2`, followed by re-running the prior milestone's
validation gates to confirm the repository has returned to its last known
Level 10 state.

Repository integrity is preserved throughout by the branch discipline
already established in ADR-010 Section 7.1 — all Phase 2 work occurs on
`phase/2`, never directly on `develop` or `main`, so a rollback at any
point in this phase never touches previously merged, already-approved
work from Phase 1.

---

## 10. DEFINITION OF DONE MAPPING

Every milestone in Section 3 names its applicable AETHER_DEFINITION_OF_
DONE.md levels explicitly in its own "Definition of Done" field — this
section does not repeat that per-milestone detail. It states the
phase-wide mapping: Levels 1 through 10 are climbed once per milestone,
fifteen times across this plan (all milestones except M2.0, which climbs
only Levels 1–2, having no architecture or testing surface of its own).
Levels 11 and 12 are climbed once, for the phase as a whole, at M2.15 and
beyond, using the seven reusable templates AETHER_DEFINITION_OF_DONE.md
Section 6 defines:

`PHASE_2_REVIEW_REPORT.md`, `PHASE_2_TECHNICAL_DEBT_REPORT.md`,
`PHASE_2_RISK_REVIEW_REPORT.md`, `PHASE_2_LESSONS_LEARNED.md`,
`PHASE_2_DEFINITION_OF_DONE_REPORT.md`, `PHASE_2_GO_NO_GO_REPORT.md`,
`PHASE_2_COMPLETE_REPORT.md`.

No milestone in this plan is considered complete — no matter how much of
its own field list is satisfied — until its specific applicable levels
are confirmed, in writing, per the evidence each level requires. This
plan does not grant any milestone an exemption from any level it names.

---

## 11. ARCHITECTURE COMPLIANCE

Every milestone's own "Architecture Review" field in Section 3 cites the
specific governing sections it implements — this is not generic
boilerplate repeated per milestone, but a distinct citation for each. In
aggregate, this plan's milestones implement:

- **AETHER_INTELLIGENCE_ARCHITECTURE.md** Sections 7 (Group B: File
  System Agent, PC Control Agent), 19 (Capability Registry), 20 (Engine
  Lifecycle — vocabulary only, per M2.7's scope), 21 (Agent Health
  Monitoring), 22 (Runtime Telemetry Framework).
- **PHASE_2_TECHNICAL_SPECIFICATION.md** in full — every numbered section
  from 1 through 19 maps to at least one milestone above.
- **ADR-010** Sections 2–4 (risk classification, forbidden operations,
  backup requirements — governing M2.1 specifically), Section 7 (branch
  and commit discipline — governing every milestone's execution), Section
  13 (technical debt — governing M2.15).
- **ADR-011** Section 2 (Zero-Tolerance Violations — governing every
  milestone's code), Section 4 (the six Quality Gates — mapped explicitly
  in Section 7 of this plan), Section 10 (Performance Baseline Standards
  — governing every milestone with a named latency target).

No implementation decision in any milestone above may contradict any of
these. Where PHASE_2_TECHNICAL_SPECIFICATION.md Sections 10.3 and 10.4
already noted specific tension with V1_TECHNICAL_SPECIFICATION.md's
locked `ModelTier` system and Phase 1's sequential `AgentRuntime` — and
resolved it by scoping the new schema to Phase 2's actual runtime
behavior rather than overriding either — M2.6 and M2.7 implement exactly
that resolution, not a reinterpretation of it.

---

## 12. DEVELOPER WORKFLOW

Implementation does not happen automatically. For every milestone in
Section 3, in the exact order given:

1. Claude generates one implementation prompt, for that milestone only,
   per AETHER_PHASE_EXECUTION_WORKFLOW.md Step 5.
2. The developer carries that prompt into Antigravity IDE, which executes
   it per Step 6.
3. The developer performs the Human Review Workflow (Step 7) — the full
   forty-item checklist from ADR-011 Section 5.2.
4. The developer delivers Antigravity's output back to Claude, who
   performs the Claude Review Workflow (Step 8) and returns a verdict.
5. The developer approves, explicitly, before Claude generates the next
   milestone's prompt.

No step in this sequence is skipped, reordered, or combined with an
adjacent milestone's cycle. This is the exact pattern Phase 1's fourteen
prompts already followed; this plan does not alter it, only schedules it
across Phase 2's sixteen milestones.

---

## 13. AI WORKFLOW

Responsibilities, per AETHER_PHASE_EXECUTION_WORKFLOW.md Section 4:

**Claude (Principal Architect):** Architecture interpretation, milestone
prompt generation (Section 12, step 1), the Claude Review Workflow
(Section 12, step 4), and documentation synchronization (every
milestone's Documentation Updates field). Claude never writes production
code directly into the repository.

**Antigravity IDE (Implementer):** Executes exactly the milestone prompt
it is given — the files listed, the interfaces specified, nothing beyond
that scope. Performs bug fixes and refactoring only within the active
milestone's Failure Handling cycle (Section 8), never ahead of it.

**Developer (Approver):** Architecture approval at every gate in Section
7, manual validation for every milestone's "Validation Required" field,
and the final decision to proceed at every step of Section 12's workflow.
Developer approval is mandatory before every milestone without exception
— not a courtesy step, the actual gate.

---

## 14. PHASE COMPLETION CRITERIA

Phase 2 is complete when, and only when, every item below is true:

**Mandatory deliverables:**
- [ ] All sixteen milestones (M2.0–M2.15) have reached Level 10
      (Production Ready)
- [ ] The PC Control Trust Test (M2.13) has passed, both halves, with a
      recorded, witnessed result
- [ ] The PostgreSQL migration (M2.1) is complete and verified
- [ ] Service extraction (M2.14) is complete, with `services/pc-control/`
      running as a genuinely separate, sandboxed process

**Mandatory validations:**
- [ ] Zero `lint-imports` violations across the entire phase's changed
      files
- [ ] Zero `mypy --strict` errors
- [ ] Zero forbidden-pattern scan matches
- [ ] Every entry in `.aether/permissions.yaml`'s `forbidden_launch` and
      `forbidden_paths` lists individually proven blocked
- [ ] Zero registry, service-management, or driver-level capability
      present in the delivered tool surface
- [ ] Full-phase regression suite (Phase 1's M1.5, M1.10 tests) passing
      at all three checkpoints named in Section 6
- [ ] `docs/performance/phase-2-baseline.md` complete with no unresolved
      degradation beyond ADR-011 Section 10.5's thresholds

**Mandatory documents:**
- [ ] `PHASE_2_REVIEW_REPORT.md` — verdict: ARCHITECTURALLY COMPLIANT
- [ ] `PHASE_2_TECHNICAL_DEBT_REPORT.md` — zero open P1 items
- [ ] `PHASE_2_RISK_REVIEW_REPORT.md`
- [ ] `PHASE_2_LESSONS_LEARNED.md`
- [ ] `PHASE_2_DEFINITION_OF_DONE_REPORT.md` — overall determination:
      LEVEL 11 ACHIEVED
- [ ] `PHASE_2_GO_NO_GO_REPORT.md` — developer-signed GO
- [ ] `PHASE_2_COMPLETE_REPORT.md`

Only when every box above is checked does Phase 2 reach Level 12 (Phase
Complete) per AETHER_DEFINITION_OF_DONE.md, and only then may Phase 3
Initialization (AETHER_PHASE_EXECUTION_WORKFLOW.md Step 27) begin.

---

## 15. FINAL PHASE DELIVERABLES

**Modules:** `aether/security/` (new), `aether/pc_control/` (new, module
form retained as the Stage A implementation behind `PCControlClient`).

**Agents:** `FileAgent`, `SystemAgent` — both fully conforming to their
pre-approved roles in AETHER_INTELLIGENCE_ARCHITECTURE.md Section 7,
Group B.

**Tools:** `launch_app`, `close_app`, `focus_app`, `list_running_apps`,
`search_files`, `read_file_content`, `move_file`, `get_system_stats` —
eight, registered with `ToolRegistry`.

**Services:** `services/pc-control/` — the extracted, sandboxed PC
control process, running alongside `aether-core` and `aether-voice`.

**Architecture extensions:** `CapabilityRegistry`, `TaskState` vocabulary,
the seven-method Agent Health Interface, `runtime.resource.snapshot`
telemetry — the working implementations of AETHER_INTELLIGENCE_
ARCHITECTURE.md Sections 19, 20, 21, 22.

**Documentation:** `V1_TECHNICAL_SPECIFICATION.md` updated across
multiple sections; `docs/guides/adding-a-pc-control-tool.md`; `.aether/
permissions.yaml` comments updated; `CHANGELOG.md` entries for every
milestone.

**Tests:** The complete unit, contract, integration, and acceptance suite
built across M2.0–M2.15, including the PC Control Trust Test.

**Validation reports:** `docs/performance/phase-2-baseline.md`; the full
Section 14 completion-criteria checklist, checked and dated.

**Architecture and review reports:** The seven documents listed in
Section 14's "Mandatory documents" — `PHASE_2_REVIEW_REPORT.md` through
`PHASE_2_COMPLETE_REPORT.md`.

---

## 16. IMPLEMENTATION RULES

These rules are not new — they are AETHER_PHASE_EXECUTION_WORKFLOW.md
Section 8's Non-Negotiable Rules, already permanent and phase-agnostic,
restated here as the specific rules this plan enforces:

- Implementation progresses one milestone at a time — M2.0 through
  M2.15, in the exact order Section 2 gives, never two at once.
- No skipping milestones — every one of the sixteen above is mandatory.
- No code generation outside the active milestone's stated scope.
- Every completed milestone is reviewed (Section 12, steps 3–4), verified
  (Section 7's seven gates), and approved (Section 12, step 5) before the
  next milestone's prompt is generated.
- If the developer is not satisfied with a milestone's result, it is
  revised — per Section 8's Failure Handling record — until approved.
  Development does not continue past an unapproved milestone under any
  circumstance.

---

## 17. IMPLEMENTATION PROMPT POLICY

Claude never writes production code directly into this repository.
Claude's sole implementation-facing output is one milestone prompt at a
time, generated only after the prior milestone has been approved per
Section 12. Each prompt follows the fifteen-section format already
established across Phase 1's fourteen prompts (Objective, Scope, Files to
Create, Files to Modify, Exact Folder Locations, Architecture Constraints,
Coding Standards, AI Generation Rules to Follow, Skills to Load, Expected
Deliverables, Validation Requirements, Testing Requirements, Security
Requirements, Definition of Done, Explicit Things Antigravity Must Not
Do), governed in full by AI_GENERATION_RULES_V2.md.

Antigravity IDE performs the actual implementation. Claude reviews the
generated code against the prompt that produced it, per the Claude
Review Workflow. The developer performs final validation and holds sole
authority to approve — no milestone in this plan advances on Claude's
review alone, and none advances on Antigravity's output alone.

No milestone prompt for this phase is generated until this plan itself
has been reviewed and its approval explicitly confirmed.

### 17.1 Prompt Generation Sequencing Exception (M2.2–M2.15)

By explicit developer instruction, given with full acknowledgment that it
departs from this section's default sequencing, prompts for M2.2 through
M2.15 were generated together rather than one at a time. This does not
alter Section 12's Developer Workflow or Section 7's Validation Gates —
each milestone is still implemented, reviewed, and approved individually,
in order, before the next milestone's *implementation* begins. What was
batched is Claude's own prompt-drafting step, not the review-and-approval
cadence. This exception applies to this specific batch only; the default
one-at-a-time prompt generation in Section 17 resumes for Phase 3 and
beyond unless a future phase's developer gives the same explicit
instruction again.

---

## 18. GUIDING PRINCIPLE

> *"Architecture is designed once.*
>
> *Implementation follows architecture.*
>
> *Verification protects architecture.*
>
> *Approval protects quality.*
>
> *No milestone advances without explicit human approval.*
>
> *Quality is always more important than development speed."*

---

*Document Version: 1.4*
*Status: APPROVED FOR EXECUTION*
*Governs: Milestones M2.0 through M2.15, plus M2.1.5 through M2.1.10, in
the order given*
*Amendment History: v1.1 — inserted M2.1.5 (Foundation Remediation)
after M2.1's execution surfaced three P1 defects in pre-existing Phase 1
code (aether/session/manager.py's Memory API boundary violation, the
never-implemented SQLiteMemoryStore.get_messages(), and a stale test
assertion), per AETHER_DEFINITION_OF_DONE.md Non-Bypassable Rule NB-5.
Also corrects a specification error in V1_TECHNICAL_SPECIFICATION.md
Section 2.8's original SessionManager constructor, which directly
injected db_session_factory and consolidation_pipeline rather than
requiring the Memory API boundary — the error predates Phase 2 and is
corrected here, not merely patched in implementation.
v1.2 — inserted M2.1.6, M2.1.7, M2.1.8 (original numbering) by explicit
developer decision to resolve all three remaining open debt items
(DEBT-007, DEBT-005, DEBT-006) from the M2.1 review before M2.2.
v1.3 — M2.1.6's own execution (specifically, its required manual TEXT
MILESTONE re-run) surfaced two further debt items: DEBT-008
(integration tests writing directly to the real production database
with no isolation — which had already resulted in an unauthorized
deletion of 47 real rows before this milestone existed to prevent
recurrence) and DEBT-009 (consolidation_min_messages=5 meaning normal
short conversations never produce a durable fact, and per-turn memory
quality being insufficient on its own — meaning Phase 1's original TEXT
MILESTONE claim was very likely never genuinely validated, consistent
with DEBT-002's finding that real consolidation never ran in Phase 1).
By explicit developer decision, all five debt items remaining open after
the M2.1 review — DEBT-004, DEBT-005, DEBT-006, DEBT-008, DEBT-009 —
are resolved before M2.2. The original M2.1.7 (DEBT-005) and M2.1.8
(DEBT-006) are renumbered to M2.1.9 and M2.1.10 without content change,
to make room for new M2.1.7 (DEBT-008 + DEBT-004, test infrastructure
safety, sequenced first since no further testing should occur without
it) and new M2.1.8 (DEBT-009, the core memory-quality fix, sequenced
second as the most architecturally significant of the five).*
*Filename Note: Produced as `PHASE_2_IMPLEMENTATION_PLAN.md`, matching
AETHER_PHASE_EXECUTION_WORKFLOW.md Section 6's naming template and
PHASE_2_TECHNICAL_SPECIFICATION.md's own forward reference, rather than
the "FOUNDATION"-suffixed name given in the request that produced this
document — "Foundation" was Phase 1's codename, not Phase 2's*
*Next Action: M2.1.7 Part 2 prompt generated (Qdrant/Redis isolation
extension, plus orphan cleanup) after Part 1's own validation found the
same isolation gap uncovered in Qdrant; awaiting developer execution and
review before M2.1.7 is considered closed, then M2.1.8, M2.1.9, M2.1.10
in order, before M2.2*
*Owner: Chief AI Architect / Principal Systems Engineer*
*Last Updated: 2025-11-15*
