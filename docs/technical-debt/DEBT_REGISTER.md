# Aether AI OS — Technical Debt Register

See ADR-010 Section 13 for the debt governance process and priority definitions.

| ID    | Title                                                         | Priority | Status                            | Milestone | Opened     |
| ----- | ------------------------------------------------------------- | -------- | --------------------------------- | --------- | ---------- |
| D-001 | Migrate `tool.uv.dev-dependencies` to `dependency-groups.dev` | P2       | Resolved (commit ffed4e8)         | M2.0      | 2026-07-03 |
| D-002 | Add UI to configure Picovoice Access Key for Porcupine        | P2       | CLOSED (config path — M2.1.10 P2) | M2.0      | 2026-07-03 |

## DEBT-001: Session Manager violates the Memory API boundary

**Priority:** P1
**Status:** Closed **Resoveld via m2.1.5**
**Location:** aether/session/manager.py

**Description:** Imports sqlalchemy and aether.memory.\_consolidation
directly — both private to aether/memory/, forbidden by the Memory API
boundary since Milestone M1.0.

**Reason accepted:** Not accepted. Should have been caught at M1.8's
Architecture Compliance gate.

**Cost:** HIGH. Any future change to memory's internal storage (already
underway in Phase 2) risks silently breaking SessionManager.

**Resolution plan:** Route all consolidation-triggering and conversation
tracking through MemoryAPI's public methods. Extend MemoryAPI if a
needed capability is missing — never import around it.
**Target:** Recommended remediation milestone before M2.2.

---

## DEBT-002: Real memory consolidation pathway cannot execute

**Priority:** P1
**Status:** Closed **Resoveld via m2.1.5**
**Location:** aether/memory/\_consolidation/pipeline.py, line 28

**Description:** Calls store.get_messages(), a nonexistent method,
suppressed via # type: ignore. End-of-session consolidation has never
executed outside mocked tests.

**Reason accepted:** Not accepted — undocumented workaround, prohibited
by ADR-011.

**Cost:** CRITICAL. The mechanism that turns conversation into durable
memory beyond single explicit facts has not functioned in Phase 1.

**Resolution plan:** Implement the missing method (or correct the call),
remove the type: ignore, add a real integration test against the live
path, not a mock.
**Target:** Recommended remediation milestone before M2.2.

---

## DEBT-003: test_memory_api asserts a nonexistent EventBus method

**Priority:** P1
**Status:** Closed **Resoveld via m2.1.5**
**Location:** tests/unit/test_memory_api.py

**Description:** Asserts .publish() was called; the locked method is
.emit() (V1_TECHNICAL_SPECIFICATION.md Section 2.3). Failing since M1.6.

**Reason accepted:** Not accepted — should have blocked every milestone
gate from M1.6 forward under Gate Q-3.

**Cost:** HIGH, primarily as a process signal — this suggests the
Testing Gate was not enforced with full rigor across six milestones.

**Resolution plan:** Fix the assertion; audit the suite once for other
stale-assertion tests of the same kind.
**Target:** Recommended remediation milestone before M2.2.

---

## DEBT-004: SQLite FTS5 keyword search likely never matched real rows

**Priority:** P2 (downgraded — no longer a live-path defect)
**Status:** Closed **Resolved via M2.1.7**
**Location:** aether/memory/\_stores/sqlite_store.py (SQLite branch,
retained for test fixtures only)

**Description:** Joins m.id = f.rowid — TEXT against INTEGER, never
equal. Silently degraded to vector-only search throughout Phase 1.

**Reason accepted:** Downgraded to P2 — production now uses pg_trgm
exclusively, verified via M2.1's live smoke test.

**Cost:** MEDIUM. Test fixtures asserting keyword-search behavior may
have passed for the wrong reason.

**Resolution plan:** Fix the join, or document the SQLite branch as
fallback-only, not a keyword-matching fidelity test.
**Target:** M2.15 or later.

**Resolution (M2.1.7):** Corrected the join to `memories.rowid =
memories_fts.rowid` (both INTEGER, per the `content_rowid='rowid'` FTS5
config from migration 001). Added `tests/unit/test_sqlite_fts.py` — four
real file-backed SQLite tests proving the join now returns actual matches
(and would have failed against the old buggy join). `tasks_fts` is created
by the migration but never queried by any application code, so there is no
sibling join to fix.

---

## DEBT-005: Codebase-wide lint and type-check backlog

**Priority:** P1 by volume, not by any single instance
**Status:** Closed **Resolved via M2.1.9**
**Location:** Primarily services/voice/; also cli.py, api.py,
vector_store.py, session/manager.py, kernel.py

**Description:** 152 ruff errors, 14 unformatted files, 28 mypy --strict
errors, independent of M2.1.

**Reason accepted:** Not a deliberate trade-off — too large to absorb
inside any single milestone without derailing it.

**Cost:** HIGH by volume — every future edit inherits a noisy baseline.

**Resolution plan:** A dedicated remediation pass, likely split by
directory, services/voice/ first.
**Target:** Schedule deliberately — do not let this get silently
absorbed into M2.15's scope.

**Resolution (M2.1.9):** The full tree is clean on all three gates:
`ruff check .` 140 -> **0**, `ruff format --check .` 11 unformatted -> **0**
(105 files), `mypy aether/ services/ --strict` 28 -> **0** (62 source files).
`lint-imports` still reports 3 contracts kept / 0 broken, so no fix crossed a
module boundary. 96 findings were resolved by mechanical `--fix` (whitespace,
import sorting), 7 by removing genuinely dead imports, the rest by hand.

**Deliberate suppressions (each behavior-preserving by necessity, not
convenience):**

- **UP042 x4** (`ModelTier`, `MemoryType`, `MemorySource`, `VoicePipelineState`)
  — NOT applied. Converting `(str, Enum)` to `StrEnum` was proven to change
  `str()`, f-string, `format()` and `%s` rendering ("ModelTier.LOCAL" ->
  "local"); only `==` and `.value` are unaffected. The first three are locked
  contracts (V1 spec Section 2.4 / the Memory API surface) and the codebase
  demonstrably renders them (M2.1.8's diagnostics printed "[MemoryType.FACT]").
  Each carries a `# noqa: UP042` documenting the reason.
- **B006/B008 in `memory/api.py`** — NOT "fixed". The V1 spec Section on the
  Memory API states "Public interface (LOCKED — method signatures are
  permanent)" and specifies `metadata: dict = {}` and
  `filters: MemoryFilter = MemoryFilter()` verbatim (the latter is also the
  spec's own "CORRECT" example). Changing either would violate the frozen
  Constitution. The stale `# noqa: B006` on `recall` cited the wrong rule and
  was corrected to `B008` (the rule actually firing).
- **A002 in `test_tool_registry.py`** — `input` mirrors the locked
  `BaseTool.execute` signature, which carries the identical suppression.
- **A002 in `test_event_flow.py`** — the mock's `filter` param is DEBT-006's
  stale signature (the real `TaskManager.list` takes `task_filter`). Suppressed
  only; the stale signature is left for DEBT-006's own milestone.
- **Targeted `type: ignore`s** for untyped third-party calls (`torch.hub.load`,
  `redis.asyncio.from_url`) and `tasks/manager.py`'s legacy `Column(String)`
  assignment, each rule-scoped with a written reason. Four stub-less audio
  libraries (pvporcupine, sounddevice, kokoro, faster_whisper) are handled by a
  **per-module** mypy override so the strict global `ignore_missing_imports =
false` still governs the rest of the tree.

**Validation:** unit+contracts 158 passed, identical to the pre-change
baseline. Integration file-by-file (DEBT-011 workaround): config_events 3,
consolidation 2, conversation_flow 1, conversation_interface 3, memory_pipeline
2, fact_capture_live 3, consolidation_live 2 — all pass. The only failures are
the known pre-existing ones: DEBT-006 stale mocks x5 (event_flow 2 +
task_workflow 3, failing on `create_task`/`AgentTask` shape/`task_filter` —
semantic API mismatches that no lint fix can cause) and the STT x1 below.
`test_consolidation_live` now passes (previously an Ollama OOM), after
restarting Ollama with `OLLAMA_CONTEXT_LENGTH=8192`.

**NOT satisfied — Level 4 is not claimed:** M1.10's six-step Voice Milestone
sequence could not be re-run, because CUDA STT is non-functional in this
environment (see DEBT-013). Per NB-2 the sequence is not waived, substituted,
or declared "effectively passing"; the GO decision is the developer's (NB-6).

---

---

## DEBT-006: Stale test fixtures and script robustness gaps

**Priority:** P3
**Status:** Resolved — commit cdb8c52 (stale fixture corrections + start.ps1/stop.ps1 exit-code robustness)

**Description:** test_task_workflow's outdated AgentTask shape,
test_event_flow's stale mock signature, start.ps1/stop.ps1 treating
docker-compose's normal stderr output as failure.

**Resolution plan:** Opportunistic, or bundle into M2.15.

**Resolution (DEBT-006 fixture/script cleanup task):** all four items fixed
against the locked contracts — no assertion was weakened to make a stale test
pass.

- **`test_task_workflow.py`** was stale far beyond the `AgentTask` shape named in
  the brief. Every one of these was written against an architecture that no
  longer exists (in places never did), and all are now corrected:
  `AgentTask(instruction=...)` -> `description`/`goal`/`input_data`;
  `ContextPackage(active_tasks=, transcript=, relevant_memories=)` -> a properly
  shaped `AgentContext`; `AgentDecision(tool_calls=[...])` -> `action` /
  `action_input`; `task_manager.create_task()/list_tasks()` ->
  `create()`/`list()`; `result.output` -> `result.response`; an LLM mock carrying
  `.usage` -> the locked top-level `total_tokens` (M2.1.6); `priority="NORMAL"`
  -> `TaskPriority` (no such member ever existed); and a `select(DBTask)` against
  the _Pydantic_ model -> assertions through TaskManager's public API, which
  verifies the locked `Task` shape and its real `TaskStatus` enum rather than the
  lower-cased string the manager happens to persist. The "complete a task" test
  now moves PENDING -> ACTIVE -> COMPLETED because the locked state machine
  forbids PENDING -> COMPLETED directly — the transition rules were respected,
  not relaxed to suit the test.
- **`test_event_flow.py`**: `MockTaskManager.list(self, filter, limit)` now
  mirrors the real signature exactly — `task_filter: TaskFilter | None = None,
limit: int = 50` — the specific defect M2.1.5 identified and left. A second
  stale construct surfaced once that was fixed and is also corrected:
  `MockMemoryAPI.recall` returned `ContextPackage(memories=[])`, missing five
  required fields.
- **`start.ps1` / `stop.ps1`**: root cause was `$ErrorActionPreference = "Stop"`
  combined with native `docker compose`, whose _normal_ progress output
  ("Container aether-redis Started", "Network aether-internal Created") goes to
  **stderr**. PowerShell 5.1 wraps each stderr line from a native executable in a
  NativeCommandError and raises it as a **terminating** error, so a completely
  successful `docker compose up -d`/`down` aborted the script — which is why both
  needed manual bypass throughout this remediation arc. Fixed with two helpers:
  `Invoke-NativeCommand` (judges success by **exit code**, the only reliable
  signal for a native process) and `Get-NativeOutput` (captures text for the
  health probes). Both relax the stderr behaviour only for the duration of the
  call and render output as plain text, so success no longer prints a red error
  block. The same fault affected the Redis/Postgres health probes and the
  `nvidia-smi` call; all are corrected.

**Validation:** `test_task_workflow.py` 3 passed, `test_event_flow.py` 2 passed.
Unit+contracts+architecture 162 passed (unchanged). ruff 0, format clean, mypy
--strict 0, import-linter 3 kept / 0 broken. **`start.ps1` and `stop.ps1` were
each run end to end and completed with exit code 0**, no manual intervention and
no stderr-triggered abort: containers created/started, all three health checks
green, and on stop all containers removed with the three named data volumes
preserved.

**Finding for DEBT-011 — root cause narrowed.** The corrected task-workflow tests
reach code the broken ones never did (they raised ValidationError long before the
agent ran), and that exposed DEBT-011's access violation at far finer granularity
than "the full suite": **two** tests in one process were enough. Pinned down, the
trigger is _repeated embedding-model / kernel initialization within a single
pytest process_ — the second load reliably crashes with `Windows fatal exception:
access violation`. Each test had been booting its own kernel. Making the kernel
fixture module-scoped (with a matching `loop_scope="module"`, otherwise asyncpg
raises "another operation is in progress") both removed the crash and cut the
file's runtime. This is a mitigation pattern, **not** a fix — the underlying
torch/Windows fault is untouched and DEBT-011 remains open.
`tests/integration/test_fact_capture_live.py` has the same latent shape (three
tests, each constructing its own `MemoryAPI`) and was observed crashing the same
way; it was left alone as out of scope.

---

## DEBT-007: CLI and internal API conversation handlers use nonexistent

types and fields; conversation persistence and possibly the CLI's basic
response path are non-functional

**Priority:** P1
**Status:** Closed **Resolved via M2.1.6**
**Location:** aether/interfaces/cli.py (\_handle_conversation),
aether/interfaces/api.py (/conversation/message)

**Description:** Both call AgentTask, AgentContext, AgentResult, and
SessionContext using field names that do not exist on the locked types
(instruction, transcript, output, memory_context misuse, a private
\_cache_session() that was never implemented). api.py contains committed
reasoning-in-progress comments in place of an actual implementation
decision for message persistence.

**Reason accepted:** Not accepted — this predates Phase 2, surfaced by
M2.1.5's diagnostic investigation, not introduced by it. Related to, but
more severe and more narrowly scoped than, the general DEBT-005 backlog.

**Cost:** HIGH. This is the primary interactive entry point to Aether.
Full-transcript persistence for consolidation is very likely broken;
the CLI's basic response display may be broken independent of that.

**Resolution plan:** Add SessionManager.build_agent_context() as the
single, shared SessionContext→AgentContext conversion point. Correct
both cli.py and api.py to use it, and to call update_context() with the
correct per-turn delta. Prove the fix against the real interface, not a
bypass. Re-run Milestone M1.9's original TEXT MILESTONE sequence for
real — manually, not only via automated test.
**Target:** Recommended remediation milestone (M2.1.6) before M2.2.

**Resolution (M2.1.6):** build_agent_context() added; both handlers
rewritten to use it and the M2.1.5 two-item delta; three real interface
tests pass. During the manual re-run two blocking pre-existing gaps were
also fixed under approved scope amendments: kernel.boot() never
registered any tools (M1.6's own deliverable) and ConversationAgent's
allowed_tools named five nonexistent tools — both corrected to the spec
(§2.6, §8.6). ConversationAgent's `response.usage` crash and a print()
were also fixed. Interface display + persistence are proven working.
The cross-session name-recall step of the manual sequence is NOT
satisfied by the literal 2-message run — see DEBT-009.

---

## DEBT-008: Integration tests write to the live database with no isolation

**Priority:** P1
**Status:** Closed **Resolved via M2.1.7** (relational DB only — see DEBT-010 for Qdrant/Redis)
**Location:** tests/integration/ (all files), aether's test configuration

**Description:** No dedicated test database exists — integration tests
write directly to whatever config.database.url points at, which post-M2.1
is the real production PostgreSQL instance. This already caused a
false-positive recall during M2.1.6's own testing, and resulted in an
unauthorized deletion of 47 real rows (via MemoryAPI.forget(), audited,
but never pre-approved) to clean up the resulting pollution.

**Reason accepted:** Not accepted. Test infrastructure should never have
been capable of touching production data in the first place.

**Cost:** CRITICAL as a structural gap — not because of what was
deleted (confirmed test-pollution artifacts, not real user data), but
because nothing currently prevents a recurrence with real data.

**Resolution plan:** A dedicated, disposable test database, with a hard
guard preventing any test run from connecting to anything else.
**Target:** M2.1.7, before any further testing occurs.

**Resolution (M2.1.7):** Dedicated `aether_test` PostgreSQL database
(config `database.test_url` / `AETHER_TEST_DATABASE_URL`), provisioned by
`scripts/provision_test_database.py`. A session-scoped, autouse,
fail-closed guard (`tests/conftest_db_guard.py`) verifies the URL is
clearly test-marked and redirects `config.database.url` to it before any
test body runs — the production URL is unreachable through config for the
whole session. Proven: production row counts identical before/after a full
integration run; a deliberately prod-pointing test URL makes the suite
refuse to run immediately. **Scope note:** this closes the _relational_
database gap only. During validation the guard was found NOT to cover
Qdrant — test vectors still reach the production `episodic_memory`
collection (prod Qdrant 30 points vs prod SQL 29 rows). Reported, not
fixed, per the milestone's stop-and-report rule — see DEBT-010.

---

## DEBT-009: Consolidation threshold and per-turn memory quality mean short conversations never produce durable facts

**Priority:** P1
**Status:** Closed **Resolved via M2.1.8**
**Location:** aether/agents/\_implementations/conversation.py,
config/default.yaml (consolidation_min_messages)

**Description:** A short, realistic conversation stating a fact ("my
name is Alex") never reaches consolidation_min_messages=5, and per-turn
storage only produces a generic low-importance episode, not a clean
fact. This means Phase 1's original M1.9 TEXT MILESTONE claim — Aether
recalling a stated name across a restart — was very likely never
genuinely validated, since real consolidation never ran in Phase 1 at
all (DEBT-002).

**Reason accepted:** Not accepted — this is the project's core memory
promise not actually working for ordinary use.

**Cost:** CRITICAL. This is not a peripheral defect.

**Resolution plan:** Immediate fact recognition and storage per turn,
plus a lowered, more realistic consolidation threshold. Proven by a
corrected, honest re-run of the TEXT MILESTONE sequence.
**Target:** M2.1.8.

**Resolution (M2.1.8):** ConversationAgent now runs a non-blocking
per-turn fact check. After the conversational reply is already final,
`execute()` fires `_check_for_explicit_fact()` via `asyncio.create_task`
(the same pattern as SessionManager's consolidation trigger), tracked on
`self._fact_check_task` so callers/tests await it explicitly instead of
sleeping. The check uses the free `ModelTier.LOCAL` tier with a
`FactCheckResult` schema (`contains_fact`, `fact_statement`); a recognized
durable fact is stored immediately as `MemoryType.FACT` at importance
`0.85` (`EXPLICIT_FACT_IMPORTANCE`), distinctly above the 0.7 per-turn
episode. The reply path is untouched — it neither blocks nor changes the
response, and any failure (`AetherError`/`ValidationError`) is logged and
swallowed at that boundary. `consolidation_min_messages` lowered 5 → 3 in
both `config/default.yaml` and `config.py` (kept in sync).
`tests/integration/test_fact_capture_live.py` adds three live tests
against the isolated M2.1.7 stores: positive capture, no fabrication on a
non-fact turn, and consolidation no longer skipping at exactly 3 messages.
**Manual TEXT MILESTONE (witnessed, honest):** fresh session, "My name is
Jordan." → captured the clean fact "The user's name is Jordan." (FACT,
imp 0.85); `/quit`; restart; "What is my name?" → "Your name is Jordan."
Traced to the single genuine `MemoryType.FACT` record (raw-DB query
confirmed exactly one memory naming Jordan, the FACT — no coincidental
episode match). **Honest caveats:** (1) An earlier attempt with a "Jordan"
few-shot example in the fact-check prompt caused the 3B model to
confabulate a name ("Jordan's name is John."); fixed by using non-colliding
examples and forbidding invented names — the wrong production fact was
removed via the audited `forget()` path. (2) One recall attempt returned
"I don't have that information" due to a transient Qdrant-readiness hiccup
that forced FTS-only fallback, whose AND-semantics cannot match the
question form "What is my name?" against the declarative fact; the
subsequent clean run recalled correctly. Retrieval also currently ranks
generic episodes above the fact and the production FACT store carries
accumulated low-quality facts from earlier debug sessions — retrieval
ranking/quality is a follow-up beyond this milestone's capture+threshold
scope.

---

## DEBT-010: Qdrant (and Redis) have no test isolation — tests write to production

**Priority:** P1
**Status:** Closed **Resolved via M2.1.7 Part 2**
**Location:** aether/memory/api.py (QdrantMemoryStore construction from
config.qdrant), tests/integration/

**Description:** M2.1.7 isolated the relational database, but the same
class of risk remains for Qdrant and Redis. The M2.1.7 guard only
redirects `config.database.url`; it does not touch `config.qdrant` or
`config.redis`. So during an integration run the relational rows go to
`aether_test` while `MemoryAPI.remember()` still upserts vectors into the
PRODUCTION Qdrant `episodic_memory` collection, and event/session state
still reaches the production Redis. Confirmed concretely during M2.1.7
validation: immediately after a full integration run, production Qdrant
reported 30 points against 29 production SQL `memories` rows — at least one
orphaned test vector leaked into production, now unmatched by any SQL row.

**Reason accepted:** Not accepted. Surfaced during M2.1.7 and reported
per that milestone's explicit stop-and-report rule (Section 2 / Section 15) rather than fixed inline, because Qdrant/Redis isolation was out of
that milestone's scope.

**Cost:** HIGH — the exact structural gap DEBT-008 was meant to eliminate,
still open for the vector store: test runs pollute production Qdrant with
orphaned vectors, which can skew real recall and accumulate unbounded.

**Resolution plan:** Extend the isolation model to Qdrant (a dedicated
test collection or namespace, redirected by the same guard) and Redis (a
dedicated test DB index / key prefix). Ideally generalize the guard to
cover all three stores so no test can reach any production datastore.
**Target:** A dedicated milestone, alongside or immediately after the
DEBT-005/006 test-quality work.

**Resolution (M2.1.7 Part 2):** The guard now redirects and verifies all
three data stores, fail-closed, in one autouse session fixture:

- Qdrant: the collection name is now config-driven (`QdrantConfig.collection`,
  passed through `MemoryAPI` to `QdrantMemoryStore`, replacing the hardcoded
  constant). The guard redirects it to `episodic_memory_test` and refuses to
  run if the active collection is the production name.
- Redis: the guard redirects `config.redis.url` to `redis.test_url`
  (logical DB index 1) and refuses any index 0.
  The test Qdrant collection is provisioned with production's exact vector
  config (dim 1024, Cosine, int8) via `QdrantMemoryStore.initialize_collection()`.
  Proven: misconfiguring either to production refuses the suite before any test
  body; a full integration re-run left production Qdrant at 29 points == 29 SQL
  rows with zero new orphans, and wrote Redis keys to DB 1 (10) not DB 0 (4).
  The single pre-existing orphan (`019f49af-42b0-7133-bb3f-405532d26532`) was
  removed precisely: cross-referenced as present in `aether_test` SQL and absent
  from production SQL (CONFIRMED_TEST_LEAK), deleted by exact point-id via
  Qdrant's native API — before 30, orphans found 1, deleted 1, after 29.

## DEBT-011: Full integration suite crashes with a Windows torch/transformers access violation when run together — REOPENED

**Priority:** P2
**Status:** Open — REOPENED (previously closed in error)

**Description:** Originally investigated after M2.1.10 restored a
working CUDA environment; four consecutive full-suite runs passed
clean, and the item was closed as resolved. A subsequent, independent
audit re-run crashed with a segmentation fault at the same boundary
(test_fact_capture_live → test_memory_pipeline), proving the original
four-run verification threshold was insufficient for a crash of this
character — genuinely intermittent, not fixed.

**Reason accepted:** Not accepted — closed prematurely. The evidence
bar (three-then-four clean runs) was too low for an intermittent,
resource-contention-shaped failure. Individual/file-by-file test
execution remains clean across every test near the crash boundary,
consistent with the crash being caused by resource accumulation across
many sequential tests in one process (likely CUDA/torch context
handling), not any single test's logic being broken.

**Cost:** MEDIUM — mitigated by the sanctioned file-by-file workaround,
which has proven reliable; the full-suite invocation itself remains
unusable as a single command.

**Resolution plan:** A dedicated investigation with a much higher
verification bar — repeated runs (10+, not 3-4) and instrumentation
targeted at the specific crash boundary, likely examining CUDA context
lifecycle across sequential GPU-touching tests within one process.
**Target:** Dedicated remediation pass — not closed again on a small
number of clean runs alone.

**Investigation (this pass) — real native traceback captured, NOT the assumed
mechanism:** Reproduced via `python -X faulthandler`. The crash is NOT a
repeated-initialization pattern — it fires on the FIRST embedding-model load in
the process, intermittently, deep inside torch/transformers weight loading:

```
Windows fatal exception: access violation
  torch/storage.py:471 in __getitem__
  transformers/modeling_utils.py:748 in _load_state_dict_into_meta_model
  ... sentence_transformers/SentenceTransformer.__init__
  aether/llm/_embedding.py (the SentenceTransformer load)
```

Two back-to-back runs of the known crash pair (test_fact_capture_live +
test_memory_pipeline) showed the intermittency directly: run 1 loaded the model
and ran to completion; run 2 segfaulted on the very first load. Because the fault
is in the model's first weight-load, per-file module-scoped fixtures cannot
prevent it, and the change below cannot eliminate it.

**Mitigation applied (not a full fix):** `aether/llm/_embedding.py` now caches
the loaded `SentenceTransformer` process-wide (keyed by model+device), so the
model initializes exactly ONCE per process instead of on every
`MemoryAPI.initialize()` (~10+ times across the full integration suite). Fewer
load attempts = far fewer chances to hit the flaky fault per full-suite run, and
it removes redundant ~1.3GB reloads in production. It does NOT make the first
load safe.

**Status stays Open — NOT resolved.** 10/10 clean full-suite runs are
unreachable while the first load can flakily fault (a crash + native traceback
was reproduced this pass), so the item is deliberately left open and the
file-by-file workaround REMAINS the sanctioned way to run integration tests. Real
fix direction is upstream: pin/upgrade torch+transformers to a combination whose
meta-model state-dict load is stable on Windows, and/or load the embedding model
once at process start outside the asyncio loop. Appears to correlate with memory
pressure (Docker + Ollama + torch on a 16GB machine).

---

## DEBT-012: Memory retrieval fragile when Qdrant is unavailable — RESOLVED

**Priority:** P1
**Status:** Resolved

**Resolution:** FTS/pg_trgm fallback matching corrected; rerank formula
adjusted so MemoryType.FACT reliably outranks comparable-similarity
episodes. Verified via the full mandatory regression suite, re-run
fresh and independently by audit (not recalled from original
completion): Milestone M1.5's original cross-session test, all three
M2.1.8 fact-capture tests, the new FTS-fallback question-form test, the
new fact-outranks-episode test, the specific originally-observed
scenario reproduced and confirmed fixed, and a precision test proving
the loosened matching did not become indiscriminate — 6/6 passed, run
individually per the sanctioned DEBT-011 workaround (the full-suite
invocation itself remains separately affected by DEBT-011's segfault,
unrelated to this fix's own correctness).

---

## DEBT-013: Rebuilt venv installed CPU-only torch — CUDA STT and the whole Voice Milestone are non-functional

**Priority:** P1
**Status:** Closed **Resolved via M2.1.10**
**Location:** pyproject.toml (`torch>=2.0,<3` with no CUDA index),
the project virtualenv; surfaces in services/voice/stt.py

**Description:** `services/voice/stt.py` runs FasterWhisper with
`device="cuda"`, but the installed torch is **2.12.1+cpu**
(`torch.version.cuda = None`, `torch.cuda.is_available() = False`).
`cublas64_12.dll` exists nowhere in the venv, there are no `nvidia-*`
CUDA packages, and `torch/lib` contains only CPU DLLs (c10.dll,
torch.dll — no cudart/cublas). Any transcription therefore fails with
`STT failed: Library cublas64_12.dll is not found or cannot be loaded`.
`pyproject.toml` pins only `torch>=2.0,<3` with no CUDA extra index, so
a resolve picks the default CPU wheel; a `.venv.old/` directory is
present, indicating the environment was rebuilt at some point and
silently lost the CUDA build. This predates M2.1.9 (`.venv.old/` was
already in git status before it began) and matches the "STT baseline x1"
failure recorded as pre-existing since M2.1.7.

**Reason accepted:** Not accepted — found during M2.1.9's required
Voice Milestone re-run and reported rather than fixed, because
reinstalling a CUDA torch build is an environment/dependency change well
outside a lint/type milestone's scope, and is a multi-GB action that
should be the developer's explicit decision.

**Cost:** CRITICAL for the voice surface. Aether's entire voice pipeline
is inoperative, and no milestone can satisfy NB-2's six-step Voice
Milestone requirement until it is restored. It also means M1.10's
original Voice Milestone claim cannot currently be reproduced.

**Proof it is environmental, not code:** the failure is byte-identical
with and without stt.py's `import torch` (tested both ways), and a
CPU-only torch cannot supply cuBLAS under any import order — which also
independently confirms M2.1.9's removal of that unused import was
correct.

**Resolution plan:** Decide the intended torch build and pin it
explicitly (CUDA cu12x wheel via the PyTorch index, or the
`nvidia-cublas-cu12`/`nvidia-cudnn-cu12` runtime packages faster-whisper
needs), so a fresh `uv sync` cannot silently produce a CPU-only voice
stack again. Then re-run M1.10's six-step sequence to re-establish the
baseline. Consider a startup assertion that fails loudly when
`stt_device="cuda"` but `torch.cuda.is_available()` is False, instead of
failing deep inside the first transcription.
**Target:** Developer's call — but it blocks any future milestone whose
Definition of Done includes the Voice Milestone.

**Resolution (M2.1.10):** `pyproject.toml` now binds torch/torchaudio to
PyTorch's CUDA 12.x index via uv's documented per-package index mechanism
(`[[tool.uv.index]] name = "pytorch-cu126"` + `[tool.uv.sources]`, with
`explicit = true` so no other package resolves from it). cu126 was chosen by
verification, not assumption: it is the CUDA 12.x index the spec and the Windows
setup doc call for, and querying the indexes directly showed it is the **only**
12.x index publishing torch 2.12+/torchaudio 2.11+ for cp312/win_amd64
(cu121/cu124/cu128/cu129 do not; only cu126 and cu130 do, and cu130 is CUDA 13).

**Verified:** `torch.cuda.is_available()` -> **True** (torch 2.13.0+cu126,
`torch.version.cuda` = 12.6). Whisper `medium.en` on CUDA moves VRAM
**1494 -> 3499 MiB (+2005 MiB)** on load. faster-whisper load _and_ transcribe
both succeed on `device="cuda"` (previously `cublas64_12.dll is not found`), and
the real voice service now boots to `voice_pipeline_ready state=IDLE` with
`whisper_model_loaded device=cuda used_vram_gb=3.25`.

**Root cause fixed, not just the symptom:** a fresh clean-environment
`uv sync --extra voice` (dry-run into an empty venv path) resolves
`torch==2.13.0+cu126` / `torchaudio==2.11.0+cu126`, and `uv.lock` now records
`source = { registry = "https://download.pytorch.org/whl/cu126" }` with **zero**
CPU-torch references. A future `.venv` rebuild cannot silently regress.

**Incidental confirmation:** with a real CUDA torch present, faster-whisper still
resolves cuBLAS **without** stt.py importing torch explicitly (torch is pulled in
transitively, registering its DLL directory). Tested both ways: identical
success. This re-confirms M2.1.9's removal of that "unused" import was correct
under the exact condition where it could have mattered.

---

## DEBT-014: VoicePipeline feeds silero-vad 480-sample chunks; the installed model requires exactly 512

**Priority:** P2
**Status:** Closed **Resolved via M2.1.10**
**Location:** services/voice/pipeline.py line ~97
(`self.vad.is_speech_threshold(audio_frame[:480])`), and the
"480-sample chunk (30ms at 16kHz)" docstring in services/voice/vad.py

**Description:** The LISTENING branch of `audio_callback` slices
`audio_frame[:480]` and passes it to SileroVAD. The installed silero
model raises `ValueError: Input audio chunk is too short` for anything
under 512 samples at 16kHz, so **every** frame in the LISTENING state
raises. Confirmed by driving the real `audio_callback` directly: 512
samples return a probability (0.0017 for silence), 480 raises. The code
was evidently written against an older silero that accepted 480; the
pinned model now requires 512. Note `self.frame_length` is already 512,
so the slice is the only thing narrowing it.

**Reason accepted:** Not accepted — surfaced by M2.1.9's behavior
verification of services/voice/, but M2.1.9 is explicitly lint/type only
and must change no runtime behavior, so it is reported rather than
fixed. It is also currently masked: DEBT-013 means the pipeline cannot
reach a working transcription anyway, and inside a sounddevice callback
the exception is swallowed rather than surfaced.

**Cost:** MEDIUM now, HIGH once DEBT-013 is fixed — silence detection is
what ends an utterance, so with it raising every frame the pipeline can
never transition LISTENING -> TRANSCRIBING on its own.

**Resolution plan:** Pass the full 512-sample frame (drop the `[:480]`
slice) or slice to the model's required window explicitly, and correct
vad.py's docstring. Must be fixed and verified together with DEBT-013,
since the six-step Voice Milestone cannot validate either alone.
**Target:** Alongside DEBT-013.

**Resolution (M2.1.10):** the frame size is now `VAD_FRAME_SAMPLES = 512`, a
named module-level constant in `services/voice/pipeline.py`, and the LISTENING
branch feeds `audio_frame[:VAD_FRAME_SAMPLES]` (the capture stream's blocksize
already matches, so this takes the whole frame). `vad.py`'s docstring and the V1
spec Section 9.2/9.3 are corrected from the old 480-sample/30ms figure.

**Verified against the installed model, not assumed.** Swept candidate sizes at
16kHz: 160/256/320/480 -> rejected "Input audio chunk is too short";
640/768/1024/1536 -> rejected; **only 512 accepted**. The model states its own
contract: `Provided number of samples is N (Supported values: 256 for 8000
sample rate, 512 for 16000)`.

**End-to-end proof:** driving 5.00s of real recorded speech through the actual
`audio_callback` in LISTENING state — 156 frames, **0 exceptions** (previously
every frame raised), 87 frames detected as speech, and the pipeline advanced
LISTENING -> TRANSCRIBING **on its own**. Silence detection, which had never
functioned, now works.

---

## DEBT-015: Test/CI/tooling infrastructure had multiple scoping and configuration gaps unrelated to application code — RESOLVED

**Priority:** P2
**Status:** Resolved

**Description:** Four related findings, all tooling miscalibration, not
architecture defects: (1) forbidden-pattern CI scan flagged legitimate
Alembic downgrade() DROP TABLE and the by-design litellm import inside
aether/llm/_providers/; (2) the same scan didn't know about
import-linter's existing, correct exclusion of aether.tasks; (3) the
pre-commit mypy hook's additional_dependencies built an isolated
environment containing only pydantic, reporting ~50 phantom missing-stub
errors and failing on essentially any commit — present since Milestone
M1.0's original configuration; (4) pre-commit's default stashing of
unstaged files means import-linter can't cleanly validate a
deliberately partial/incremental commit (noted, not fixed — inherent to
partial commits).

**Resolution:** CI grep narrowed to exclude migrations/ from the DROP
TABLE check, litellm check scoped to "outside _providers/," sqlalchemy
check aligned with import-linter's existing aether.tasks exclusion.
Pre-commit mypy hook switched to language: system, entry: uv run mypy
aether/ services/ --strict, mirroring the already-correct import-linter
hook pattern. Verified in both directions: passes on legitimate
patterns, still catches genuine violations placed outside their
legitimate location (3/3 caught in audit testing).

---

## DEBT-016: Constitutional branch model (main + develop + phase/N) was never actually implemented

**Priority:** P3 — not blocking current work
**Status:** Resolved — governance, via cc8244a (ADR-012)
**Location:** Repository branch structure; ADR-010 Section 7.1

**Resolution:** ADR-012-SIMPLIFIED_BRANCH_MODEL.md (commit cc8244a) formally
amends ADR-010 Section 7.1 via the Constitutional Amendment Process to retire
the `develop` branch requirement (main + phase/N only), and corrects
AETHER_PHASE_EXECUTION_WORKFLOW.md Steps 3/22/25 to match — the "simplify"
option below, chosen deliberately.

**Description:** No develop branch exists or has ever existed. phase/2
was created directly off main with zero divergence until this session's
remediation commits. ADR-010's branch model assumes develop as an
intermediate integration point.

**Reason accepted:** Under review, not yet resolved. Candidate view:
develop's value (integrating multiple concurrent branches) doesn't
apply to this project's actual solo, strictly-sequential-phase
workflow, where develop and main would always be identical at merge
time. Simplifying to main + phase/N may be the more accurate fix rather
than retroactively creating develop to match a rule written for a
different working shape.

**Cost:** LOW today; blocks Step 25 (Phase Closure) as currently
written once Phase 2 actually reaches that step.

**Resolution plan:** A deliberate decision — either formally amend
ADR-010 Section 7.1 (frozen; requires the Constitutional Amendment
Process, ADR-010 Section 16.4) to drop develop, or create it properly
and update Step 25's assumptions to match. Not resolved inline here.
**Target:** Before Phase 2 Closure (M2.15 territory), not before M2.2.

---

## DEBT-017: TaskManager lacks Memory's private-store/public-manager split; its database-access exemption is undocumented

**Priority:** P3
**Status:** Resolved — exemption **documented** in commit 8a3f7ac; the optional structural split remains open (opportunistic)
**Location:** aether/tasks/manager.py

**Description:** TaskManager's sqlalchemy usage appears inline rather
than behind a private submodule the way aether/memory/\_stores/ sits
behind MemoryAPI. Its exemption from the shared database-boundary
contract (already correctly configured in import-linter) has no
corresponding ADR note or V1_TECHNICAL_SPECIFICATION.md documentation
explaining that Tasks is treated as an independently-owned domain.

**Reason accepted:** Not accepted as urgent — likely correct
architecture, under-documented and structurally inconsistent in style
relative to Memory's pattern.

**Cost:** LOW. A future contributor (or future me) could reasonably
mistake this for a boundary violation without the exemption being
explained anywhere.

**Resolution plan:** Document the exemption explicitly. Consider giving
TaskManager the same private-store/public-manager split Memory has, for
structural consistency, if TaskManager needs modification for any other
reason first.
**Target:** Opportunistic — no phase deadline.

**Resolution — documentation (DEBT-017 documentation task):** the exemption is
now recorded in the same rationale, consistently, in all three places a reader
might encounter it: (1) a module docstring in `aether/tasks/manager.py`, (2) a
comment directly above the "Memory module boundary" contract's `source_modules`
in `pyproject.toml` (where `aether.tasks` is intentionally omitted), and (3)
V1_TECHNICAL_SPECIFICATION.md Section 2.9. The rationale, as reasoned by the
Architect: Tasks are a separate domain, not a form of memory — actionable to-do
items, not recalled facts — sharing the physical database only as
infrastructure; Aether's principle is "each domain has exactly one gatekeeper,"
not "only one module may touch SQL anywhere," so the Tasks domain owns its DB
access just as Memory's `_stores/` does, provided nothing reaches around
TaskManager to touch the `tasks` table directly. Documentation-only: ruff 0,
format clean, mypy --strict 0, import-linter 3 kept / 0 broken; no behavior
changed. **Still open (opportunistic):** the optional structural refactor to
give TaskManager Memory's private-store/public-manager split — deliberately not
undertaken here, and not required (the current inline structure is
architecturally valid; the split is style consistency, not a boundary fix).

---

## DEBT-018: Wake word cannot be armed by any documented means — key never reaches the code, and no real key exists

**Priority:** P1
**Status:** Closed (plumbing) **Resolved via M2.1.10 Part 2** — see resolution note re: the remaining developer handoff (a real key)
**Location:** services/voice/pipeline.py line ~46, aether/core/config.py
(`VoiceConfig`), `.env` / `.env.example`

**Description:** The Porcupine wake word is unconditionally disabled, so the
voice pipeline can never leave `IDLE` and **step 1 of M1.10's six-step Voice
Milestone cannot be started at all**. Found during M2.1.10 when, with CUDA STT
and the VAD both restored, the service booted cleanly to
`voice_pipeline_ready state=IDLE` but logged
`porcupine_wake_word_disabled reason=No access key provided`. Three independent
defects compound here, and fixing any one alone changes nothing:

1. **No real key exists.** `.env` contains the literal placeholder
   `AETHER_VOICE__PORCUPINE_ACCESS_KEY=your-porcupine-key-here` (D-002, open
   since M2.0). A key must be obtained from Picovoice; no code change can
   substitute.
2. **Name mismatch.** `.env`/`.env.example` use
   `AETHER_VOICE__PORCUPINE_ACCESS_KEY` (the pydantic-settings nested
   convention), but `pipeline.py` reads the bare
   `os.getenv("PORCUPINE_ACCESS_KEY", "dummy_key_if_not_provided")` — a
   different variable entirely.
3. **`.env` is never loaded into `os.environ`,** and `VoiceConfig` has no
   porcupine field at all (`enabled: bool = True` only), so even
   pydantic-settings cannot carry the value to the one place that reads it.

The practical consequence: **a developer who follows `.env.example` exactly,
pastes in a valid Picovoice key, and restarts, still gets a disabled wake
word** — with only an INFO-level warning to explain it. The documented setup
path is a dead end.

**Reason accepted:** Not accepted — surfaced by M2.1.10, whose scope was
explicitly limited to the two compounding defects it named (CPU-only torch and
the VAD frame size). Reported rather than fixed, per that milestone's own rule
to stop and report if the Voice Milestone still cannot run.

**Cost:** HIGH, and it is the _sole remaining blocker_ to the Voice Milestone.
With DEBT-013 and DEBT-014 closed, every other stage is proven working: VAD
loads and processes real frames, Whisper loads on CUDA (+2005 MiB VRAM) and
transcribes, Kokoro TTS loads and synthesizes, and the pipeline reaches IDLE.
Only the wake word — the very first step — cannot arm.

**Resolution plan:** Decide the single source of truth for this key and wire it
end to end: add `porcupine_access_key: str | None` to `VoiceConfig`, have
`VoicePipeline` read `config.voice.porcupine_access_key` rather than a bare
`os.getenv`, and keep `.env.example`'s `AETHER_VOICE__PORCUPINE_ACCESS_KEY`
name so the documented path actually works. Obtain a real Picovoice key
(D-002). Consider failing loudly — or at least at WARNING with an actionable
message — when voice is enabled but no key is configured, instead of booting to
a silently deaf IDLE. Then run the six-step Voice Milestone.
**Target:** Required before any milestone whose Definition of Done includes the
Voice Milestone (NB-2).

**Resolution (M2.1.10 Part 2):** The configuration plumbing — all three
compounding defects — is fixed, wired end to end, and tested. What remains is a
handoff action only Claude Code cannot perform: obtaining a real Picovoice key.

- **Root cause 1 (.env never loaded):** `AetherConfig`'s `SettingsConfigDict`
  was missing `env_file=".env"` — an omission dating to M1.2's original
  config.py, not a regression. A _second_, deeper omission was also found: the
  custom `settings_customise_sources` received `dotenv_settings` but dropped it
  from the returned source tuple, so even adding `env_file` alone would not have
  worked. Both fixed; `dotenv_settings` now sits between real-env and YAML
  (precedence: init > env > .env > yaml > secrets).
- **Root cause 2 (no field):** `VoiceConfig` gained
  `porcupine_access_key: str | None = None`.
- **Root cause 3 (name mismatch / bypass):** `pipeline.py` no longer calls the
  bare `os.getenv("PORCUPINE_ACCESS_KEY")` — the only such call in `services/`
  is gone (`grep -rn "os.getenv(.PORCUPINE" services/` → 0). It reads
  `get_config().voice.porcupine_access_key`, populated by the documented
  `AETHER_VOICE__PORCUPINE_ACCESS_KEY` name.
- **Loud failure:** `VoicePipeline.__init__` now raises `VoiceError`
  (`error_code="VOICE_PORCUPINE_KEY_MISSING"`, from the AetherError hierarchy)
  at startup when the key is missing, empty, or equals the `.env.example`
  placeholder — an unhandled exception at boot, not the old quiet
  `porcupine_wake_word_disabled` INFO line. The message names the fix
  (console.picovoice.ai, the exact env var) and **never echoes the configured
  value**, even when it is the placeholder. Verified the key is passed to no
  logger anywhere.
- **Tests:** 4 config-resolution tests (`tests/unit/test_config.py`: .env →
  field, defaults to None, real-env-beats-.env precedence, additive regression)
  and 5 loud-failure tests (`tests/integration/test_wake_word_config.py`:
  missing/empty/placeholder all raise with the right code, message never echoes
  the value, valid key passes the gate). All 16 pass. Gates clean: ruff 0,
  format 0, mypy --strict 0, import-linter 3 kept/0 broken (the new
  `aether.core.config`/`aether.core.exceptions` imports do not cross the
  Services boundary contract). Unit+contracts 162 (was 158, +4).

**Still open as a handoff, not a code defect:** a _real_ Picovoice key must be
placed in `.env` by the developer (D-002), after which the actual six-step
Voice Milestone can be run and witnessed. Until then the wake word correctly
refuses to arm — loudly. This is why the status is "Closed (plumbing)": every
line of code DEBT-018 named is fixed and proven; only the human-supplied secret
and the manual witnessed run remain.

## DEBT-019: Missing [build-system] table causes uv sync to silently strip the editable install

**Priority:** P1
**Status:** Resolved — commit `fix(tooling): DEBT-019 build-system table, DEBT-020 scoped process termination`

**Description:** No [build-system] table exists, so uv sync doesn't
recognize the project needs editable installation, silently removing
it (and en-core-web-sm) on every sync. Flagged once during the earlier
M2.1.5–M2.1.9 commit/push cycle; recurred identically during today's
audit, confirming it was never fixed at its root, only manually worked
around each time.

**Cost:** HIGH — will hit any real environment setup, not only
Claude Code's runs, with no clear error pointing at the actual cause.

**Resolution plan:** Add a proper [build-system] table (hatchling or
equivalent, matching the project's actual structure).
**Target:** Next remediation pass, before it hits the developer's own
environment.

**Resolution (DEBT-019 build-system task):** Added a real `[build-system]`
table (`hatchling` / `hatchling.build`) with an explicit
`[tool.hatch.build.targets.wheel] packages = ["aether", "services"]`. The
explicit list is required because this is a FLAT layout whose two top-level
packages match neither each other nor the distribution name `aether-os`, so
hatchling's name-based auto-detection cannot find them. This replaces the former
`[tool.setuptools.packages.find]`, which had no `[build-system]` to activate it
and was therefore inert.

- **Fixed at the root, not worked around:** uninstalled the editable
  `aether-os`, ran `uv sync`, and it *rebuilt and reinstalled* it
  (`Built aether-os` -> `Installed 1 package`); `python -c "import
  aether.core.kernel"` then succeeds. Before this table `uv sync` silently
  dropped the install and the next `uv run` broke - the exact failure worked
  around by hand three times across this arc.
- Gates unaffected: ruff 0, format 0, mypy --strict 0 (62 files), import-linter
  3 kept/0 broken, 189 tests still collect, DB-free unit subset 13 passed.
- **`en-core-web-sm` - honest scope note:** it is *not* installed, declared
  nowhere in `pyproject.toml`, and imported nowhere in the tree (an undeclared,
  unused stray). The build-system fix does not - and correctly should not - make
  `uv sync` retain an undeclared package, so that half of the original symptom
  cannot be "restored"; it was collateral, not a real dependency. The material
  harm (the editable install being stripped, breaking `uv run` immediately after
  every sync) is what is fixed here.

---

## DEBT-020: stop.ps1 kills any process named "python" on the machine, not only Aether's own

**Priority:** P2
**Status:** Resolved — commit `fix(tooling): DEBT-019 build-system table, DEBT-020 scoped process termination`

**Description:** Stop-Process -Name "python" -Force matches by name
only, with no scoping to processes Aether itself spawned — can (and
nearly did, during audit) kill unrelated Python processes including an
IDE's own host. Found outside DEBT-006's stated scope, reported rather
than fixed inline.

**Cost:** MEDIUM-HIGH as a workflow risk.

**Resolution plan:** Scope the kill to PIDs actually tracked/spawned by
start.ps1 (a PID file or process-tree match), never a bare name-match.
**Target:** Next remediation pass.

**Resolution (DEBT-020 scoped-termination task):** start.ps1 now launches each
service as the venv's `python.exe` DIRECTLY (not through a `powershell`/`uv`
wrapper), captures each `Start-Process` PID, and records them to
`.aether-runtime\service-pids.json` (service name -> PID; the directory is
gitignored). stop.ps1's new `Stop-AetherServices` reads that file and, for each
recorded PID, verifies it is (a) still running, (b) a `python` process, and (c)
this project's venv `python.exe` before `Stop-Process -Id`. A missing or corrupt
file prints a manual-check message and returns - it NEVER falls back to a
name-match kill. The old `Stop-Process -Name "python" -Force` is gone.

- **Bonus bug caught during validation:** the em-dashes originally written
  inside stop.ps1's `Write-Host` strings are UTF-8, but Windows PowerShell 5.1
  reads a BOM-less `.ps1` as cp1252 and mangled them (`—` -> `â€"`), breaking
  string termination so stop.ps1 would not even *parse*. Both scripts are now
  pure ASCII (verified: 0 non-ASCII bytes, both `ParseFile` clean).
- **End-to-end validated with the real scripts:** real start.ps1 recorded the
  correct PIDs and Aether Core came READY on :8000 (direct launch works); real
  stop.ps1 then `stopped` the live recorded venv core, reported the dead voice
  PID as "already exited", left an unrelated venv python untouched (PID scoping),
  spared a recorded *non-venv* python (path guard) and a recorded *non-python*
  process (name guard), printed the manual-check message for BOTH a missing and a
  corrupt PID file while a bystander venv python survived each (proving no blanket
  kill), removed the PID file, and `docker compose down` preserved the named
  volumes.

---

## DEBT-022: File-size denial detection relied on string-matching a human-readable message

**Priority:** P3
**Status:** Resolved — via this commit (fix(security): DEBT-022)
**Location:** aether/pc_control/api.py (read_file), aether/security/

**Description:** Distinguishing a size-only denial (truncate and allow) from a
hard denial (forbidden path, hidden file) keyed off matching "maximum file size"
in `SafetyValidator`'s `ValidationResult.reason` string — correct at the time,
but fragile against any future wording change to that message.

**Resolution:** Added a structured `DenialReason` enum (FORBIDDEN_PATH,
HIDDEN_FILE, SIZE_EXCEEDED, OUTSIDE_ALLOWED_PATHS, UNRECOGNIZED_OPERATION,
NO_EXECUTABLE, FORBIDDEN_EXECUTABLE, NOT_IN_ALLOWLIST, BROWSER_DISABLED,
INVALID_DOMAIN, BLOCKED_DOMAIN) and a `denial_reason: DenialReason | None` field
on `ValidationResult`. Every denial branch in `SafetyValidator` now sets the
code; `read_file` branches on `denial_reason is DenialReason.SIZE_EXCEEDED`. The
`_SIZE_DENIAL_MARKER` string match is deleted entirely.

---

## DEBT-023: search_files() validated only the search root, not each result

**Priority:** P3
**Status:** Resolved — via this commit (fix(pc_control): DEBT-023)
**Location:** aether/pc_control/api.py (search_files)

**Description:** search validated only the root directory, not each returned
path. Not an active gap today — no forbidden path is nested under an allowed
read_path in permissions.yaml — but it would become one the moment that changed
(a forbidden or hidden path nested under an allowed root could surface in
results).

**Resolution:** `PCControlAPI.search_files` now validates EACH candidate with
the same `validate_file_operation("file.read", ...)` gate used by `read_file`,
keeping a result only if allowed — or size-denied (an oversized-but-permitted
file is still *listed*, since search reports metadata, not content). Forbidden /
hidden / out-of-bounds candidates are dropped. Test proves a forbidden path
nested under an allowed root is excluded.
