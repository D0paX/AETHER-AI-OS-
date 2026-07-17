# Aether AI OS — Technical Debt Register

See ADR-010 Section 13 for the debt governance process and priority definitions.

| ID    | Title                                                         | Priority | Status | Milestone | Opened     |
| ----- | ------------------------------------------------------------- | -------- | ------ | --------- | ---------- |
| D-001 | Migrate `tool.uv.dev-dependencies` to `dependency-groups.dev` | P2       | OPEN   | M2.0      | 2026-07-03 |
| D-002 | Add UI to configure Picovoice Access Key for Porcupine        | P2       | OPEN   | M2.0      | 2026-07-03 |

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
**Status:** Open

**Description:** test_task_workflow's outdated AgentTask shape,
test_event_flow's stale mock signature, start.ps1/stop.ps1 treating
docker-compose's normal stderr output as failure.

**Resolution plan:** Opportunistic, or bundle into M2.15.

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

## DEBT-011: Full integration suite crashes with a Windows torch/transformers access violation when run together (passes file-by-file)

**Priority:** P2
**Status:** Open (resolution: fold into M2.1.10)
**Location:** tests/integration/ (suite-level, not a specific file)

**Description:** Running the full integration suite in one invocation
triggers an access violation attributed to torch/transformers on
Windows; running the same tests file-by-file, all pass. Found during
M2.1.7 Part 2, unrelated to that milestone's own changes.

**Reason accepted:** Not accepted — a permanent file-by-file workaround
does not scale across the remaining Phase 2 milestones.

**Cost:** MEDIUM. Slows every future milestone's full-suite validation
until root-caused; risk is elevated, not confirmed, given the symptom
(access violation, not a clean OOM) is more severe than simple VRAM
exhaustion.

**Resolution plan:** Investigate whether this is torch multiprocessing/
threading behavior specific to Windows, or GPU resource contention
compounding the already-known CUDA-OOM pattern. Fix or document as a
permanent, structural test-running constraint.
**Target:** M2.1.10.

## DEBT-012: Memory retrieval fragile when Qdrant is unavailable — FTS

fallback can't bridge question-to-fact vocabulary, and the rerank
formula underweights importance relative to similarity

**Priority:** P1
**Status:** Open (resolution: M2.1.11)
**Location:** aether/memory/\_retrieval/hybrid.py (fallback logic),
aether/memory/\_retrieval/reranker.py (score formula)

**Description:** When Qdrant is unavailable (observed: a readiness
timing hiccup), HybridRetrieval correctly falls back to FTS-only search
per Phase 1's original design — but FTS/pg_trgm's AND-semantics rarely
match a question against its declarative answer, since the two share
little exact vocabulary. Separately, observed in production: episodes
ranking above a FACT with importance 0.85, because the existing
0.6/0.3/0.1 (similarity/recency/importance) formula lets a strongly-
similar episode's score dominate regardless of the importance gap.
Found during M2.1.8's manual TEXT MILESTONE re-run; the capture
mechanism itself is proven correct, this is a retrieval-side gap.

**Reason accepted:** Not accepted — this is the read-side counterpart
to DEBT-009's write-side fix; a fact that's stored correctly but not
reliably retrievable is not meaningfully different from one never
stored at all, from the user's perspective.

**Cost:** HIGH. User-facing, probabilistic (timing-dependent), and
directly undermines confidence in the core memory promise even after
DEBT-009's fix.

**Resolution plan:** Improve FTS fallback matching (OR-semantics or
similar loosening) or verify Qdrant readiness before serving requests.
Reassess the rerank formula's importance weighting, or give FACT-type
memories a categorical boost independent of the linear score. Any
formula change must be regression-tested against Milestone M1.5's
original cross-session test and M2.1.8's three new fact-capture tests —
not just the new scenario being fixed.
**Target:** M2.1.11, after M2.1.9 and M2.1.10.

---

## DEBT-013: Rebuilt venv installed CPU-only torch — CUDA STT and the whole Voice Milestone are non-functional

**Priority:** P1
**Status:** Open
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

---

## DEBT-014: VoicePipeline feeds silero-vad 480-sample chunks; the installed model requires exactly 512

**Priority:** P2
**Status:** Open
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

---

## DEBT-015: CI's forbidden-pattern and boundary greps are mis-scoped — they fail on legitimate code and disagree with import-linter

**Priority:** P2
**Status:** Open
**Location:** .github/workflows/ci.yml (`security-scan` job),
.github/workflows/architecture-check.yml (`boundary-check` job)

**Description:** Two CI jobs fail on correct code and have done so since the
initial commit. Found during the M1.9 CI forensics task, which reproduced
every CI job locally against commit `fad6019`.

1. **`security-scan` greps `aether/ services/ migrations/` for
   `DROP TABLE|TRUNCATE|...|import litellm`.** Both hits are legitimate:
   - `import litellm` in `aether/llm/_providers/{anthropic,google,ollama}_provider.py`
     — the provider layer wrapping litellm *is* the LLM abstraction the
     architecture mandates. Notably `architecture-check.yml`'s own LLM check
     scopes itself to exclude `aether/llm/` and passes; ci.yml's does not.
   - `DROP TABLE IF EXISTS` in `migrations/versions/001_initial_schema.py` and
     `002_postgres_fts_migration.py` — inside Alembic `downgrade()` functions,
     which is precisely what a downgrade is for.
2. **`boundary-check` greps `aether/tasks/` for `sqlalchemy`**, which
   `aether/tasks/manager.py` legitimately imports as a persistence-owning
   module. **import-linter's own contract disagrees**: its "Memory module
   boundary" contract lists `aether.agents`, `aether.session`,
   `aether.interfaces` as source modules — deliberately *not* `aether.tasks`.
   So `lint-imports` reports 3 kept / 0 broken while the CI grep fails on the
   same tree. Two mechanisms encode two different architectures.

**Reason accepted:** Not accepted — reported rather than fixed because the
task that found it was scoped to investigation plus commit/push, and changing
CI definitions (or deciding which of the two conflicting boundary rules is
authoritative) is the Architect's call, not an implementer's.

**Cost:** MEDIUM, but corrosive. CI cannot go green on any commit, so its
signal is worthless — a genuinely broken push is indistinguishable from the
permanent baseline of red. This very likely explains why the M1.9 CI failure
went unaddressed. It also means the repo's stated quality gates are not
actually enforcing anything.

**Evidence (current `phase/2`, after M2.1.5–M2.1.9 remediation):** the tree is
clean on `ruff check` (0), `ruff format` (0), `mypy --strict` (0) and
`lint-imports` (3 kept / 0 broken) — yet `security-scan` and `boundary-check`
still fail, purely on the greps above.

**Resolution plan:** Scope the greps to what they actually mean:
- exclude `migrations/` from the destructive-SQL scan (or restrict it to
  `upgrade()` bodies), and exclude `aether/llm/` from the provider-import scan,
  mirroring architecture-check.yml's correct scoping;
- decide whether `aether.tasks` may own its own SQLAlchemy access — then make
  the grep and the import-linter contract agree, and prefer import-linter as
  the single source of truth since it understands the import graph rather than
  matching text.
**Target:** Before any milestone relies on CI as a gate.

### Addendum — the same defects are enforced locally by `.pre-commit-config.yaml`

**Location (additional):** `.pre-commit-config.yaml`

Discovered while committing the Phase 2 remediation work: the pre-commit
hooks block **every** commit, and two of the three failures are defects in the
hook configuration rather than in the code.

1. **`mypy` hook is misconfigured — fails on any commit.** It declares
   `additional_dependencies: [pydantic>=2.9]`, so pre-commit builds an isolated
   environment containing *only* pydantic. Every other third-party import is
   then unresolvable, producing ~50 spurious errors
   (`Cannot find implementation or library stub for module named "sqlalchemy"`,
   `"structlog"`, `"qdrant_client"`, `"alembic"`, `"litellm"`, …) plus
   knock-on `misc`/`unused-ignore` noise. The same check run properly
   (`uv run mypy aether/ services/ --strict`, with the project's real
   dependencies) reports **Success: no issues found in 62 source files**. The
   hook is measuring its own empty environment, not the code.
2. **`import-linter` hook cannot pass on a partial commit.** It is
   `pass_filenames: false` and analyses the whole import graph, but pre-commit
   stashes unstaged changes first — so any commit that stages a subset of the
   tree is validated against the *committed* versions of everything else. While
   committing subsystem-scoped groups on top of M1.9, this reported M1.9's
   long-since-fixed violations (`aether.session.manager -> sqlalchemy`,
   DEBT-001) even though the working tree reports **3 kept / 0 broken**. Any
   staged-subset commit trips it by construction.
3. **`forbidden-patterns` hook** duplicates ci.yml's mis-scoped grep and so
   fails identically on the legitimate Alembic `DROP TABLE` statements
   described above.

**Consequence (recorded honestly):** with the Architect's explicit
authorisation, the Phase 2 remediation commits were made with `--no-verify`.
The real gates were run manually against the full tree immediately beforehand
and all pass (ruff 0, ruff-format 0, mypy --strict 0, lint-imports 3 kept /
0 broken, 158 unit+contract tests). Bypassing was justified *only* because the
hooks were provably measuring the wrong thing; it must not become routine.

**Resolution plan (additional):** give the mypy hook the project's real
dependencies (or replace it with `language: system` + `uv run mypy` so it uses
the project venv, matching the import-linter hook's pattern); apply the same
grep re-scoping to the local hook as to ci.yml; and accept that the
import-linter hook is only meaningful on whole-tree commits — or make it
tolerate staged-subset runs.
