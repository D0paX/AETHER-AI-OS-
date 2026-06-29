# ADR-010: AI SAFETY AND CODE GENERATION STANDARDS
### Architecture Decision Record
### docs/architecture/decisions/ADR-010-AI_SAFETY_AND_CODE_GENERATION.md

---

**Date:** 2025-11-15  
**Status:** ACCEPTED — ENFORCED  
**Classification:** Project Governance — Safety Critical  
**Authority:** Principal Systems Engineer  
**Scope:** All development activity on Aether AI OS  
**Applies To:** Human developer, AI coding assistants, automated scripts, CI/CD pipelines  

---

## THE CORE PRINCIPLE

**Aether is a long-term AI Operating System. No capability or shortcut justifies data loss,
architectural corruption, or unrecoverable system state. Destruction is permanent.
Review is cheap. There is no urgency that overrides this.**

---

## 1. CONTEXT

### 1.1 The AI-Assisted Development Model

Aether is developed using AI code generation tools:
- **Antigravity IDE** — primary code generation environment
- **Claude** — architecture review, complex reasoning, specification
- **Gemini Flash** — implementation assistance, code review

AI code generators present unique risks that do not exist in purely human-authored codebases:

**Risk 1: Confident incorrectness.** AI tools generate syntactically valid, logically reasonable code that violates architectural contracts. The code compiles, runs, and appears correct until a future phase reveals the coupling it created.

**Risk 2: Shortcut optimization.** AI tools optimize for solving the immediate stated problem. They will generate `DROP TABLE IF EXISTS` in a cleanup script, `rm -rf ./temp` in a setup script, or `git reset --hard` in a fix suggestion without understanding the consequences in the Aether context.

**Risk 3: Context amnesia.** AI tools do not remember architectural decisions made in prior sessions. Without explicit architectural constraints injected into every prompt, AI tools will generate code that contradicts prior decisions.

**Risk 4: Plausible destruction.** AI-generated destructive code looks identical to safe code. A `delete_old_memories()` function that calls `TRUNCATE TABLE memories` is indistinguishable in appearance from a safe implementation without careful review.

**Risk 5: Cascading failures.** Aether stores years of personal data: conversations, memories, tasks, preferences. A single unreviewed destructive command can destroy irreplaceable data permanently.

### 1.2 Why This ADR Exists

This document establishes explicit, exhaustive, non-negotiable rules governing:
- What commands and operations are categorically forbidden
- What approval process applies to risk-classified operations
- What safeguards must exist before any destructive operation
- How to recover when things go wrong
- How the repository and branches must be protected

Every rule in this document has a specific reason. When a rule seems overly cautious, that caution exists because the alternative is data loss or architectural corruption in a system expected to run for five or more years.

---

## 2. RISK CLASSIFICATION SYSTEM

All operations are classified by risk level. Classification determines required safeguards.

### Level 0 — READ ONLY
**Definition:** Operations that read but cannot modify system state.  
**Examples:** SELECT queries, file reads, git log, git status, git diff  
**Requirements:** None. Execute freely.

### Level 1 — ADDITIVE
**Definition:** Operations that create new state without modifying or destroying existing state.  
**Examples:** INSERT (new records), file creation, git commit, git push to feature branch, new migrations (add column, create table)  
**Requirements:** Verify the operation is genuinely additive. No special approval.

### Level 2 — MODIFYING
**Definition:** Operations that change existing state. Reversible with effort.  
**Examples:** UPDATE with WHERE clause, configuration changes, dependency version changes, file edits, alembic upgrade  
**Requirements:** Confirm scope of change. Verify WHERE clause or scope is correct. No special approval.

### Level 3 — SERVICE IMPACTING
**Definition:** Operations that restart, stop, or reconfigure running services. Reversible.  
**Examples:** Docker container restarts, service configuration changes, Redis flush (dev only), feature branch rebases  
**Requirements:**  
- Confirm no active sessions before stopping services  
- Document the action in a commit message or issue comment  
- Verify restart procedure before executing

### Level 4 — POTENTIALLY DESTRUCTIVE
**Definition:** Operations that could result in data loss or unrecoverable state change if applied incorrectly.  
**Examples:** Schema migrations with column drops (future phases), large-scale UPDATE without WHERE, git push --force-with-lease, Qdrant collection reconfiguration  
**Requirements:**  
- **MANDATORY BACKUP** before execution (verified, not assumed)  
- **DRY RUN** where the operation supports it  
- **WRITTEN RECORD** of what will happen, in a GitHub issue or commit body  
- **30-MINUTE WAITING PERIOD** between deciding and executing (prevents hasty mistakes)  
- Rollback procedure defined before starting

### Level 5 — FORBIDDEN
**Definition:** Operations that are categorically prohibited under all circumstances without an explicit session review, manual human entry, and written justification.  
**Examples:** See Section 3.  
**Requirements:** See Section 3.8.

---

## 3. FORBIDDEN OPERATIONS CATALOG

This section is exhaustive. When a command is listed here, it is forbidden. No context makes it safe without the process defined in Section 3.8.

The question "but what if I really need to?" has one answer: follow Section 3.8.

---

### 3.1 Filesystem Destructive Operations

The following commands and functions are FORBIDDEN without the Level 5 override process.

**Shell commands (Windows CMD):**
```
del /f /s /q <path>
del /f /s <path>
del /f <path>
del /q <path>
rd /s /q <path>
rmdir /s /q <path>
format <drive>
```

**Shell commands (PowerShell):**
```
Remove-Item -Recurse -Force <path>
Remove-Item -Recurse <path>
Remove-Item -Force <path>
rmdir -Recurse <path>
```

**Shell commands (Unix/WSL):**
```
rm -rf <path>
rm -r <path>
rm -f <path>
rm -rd <path>
shred <path>
```

**Python operations:**
```python
shutil.rmtree(path)                     # Forbidden on production paths
shutil.rmtree(path, ignore_errors=True) # Forbidden anywhere
os.remove(path)                         # Forbidden without backup verification
os.unlink(path)                         # Forbidden without backup verification
pathlib.Path.unlink()                   # Forbidden without backup verification
pathlib.Path.rmdir()                    # Forbidden without backup verification
glob + delete pattern                   # Forbidden without explicit scope review
```

**Forbidden regardless of path specificity.** Specifying an exact path does not make a deletion command safe. The rule applies to all paths. The distinction between "safe" and "destructive" deletion does not exist without prior review and backup.

---

### 3.2 Database Destructive Operations

The following SQL statements are FORBIDDEN in application code, migration scripts, console sessions, and AI-generated scripts.

**Structural destruction:**
```sql
DROP DATABASE aether;
DROP DATABASE IF EXISTS aether;
DROP SCHEMA public CASCADE;
DROP TABLE conversations;
DROP TABLE memories;
DROP TABLE messages;
DROP TABLE tasks;
DROP TABLE tool_executions;
DROP TABLE agent_runs;
DROP TABLE llm_costs;
DROP TABLE system_kv;
DROP TABLE IF EXISTS <any_table>;
DROP INDEX <any_index>;
DROP VIEW <any_view>;
```

**Data destruction:**
```sql
TRUNCATE TABLE <any_table>;
TRUNCATE <any_table>;
DELETE FROM <any_table>;              -- Without WHERE clause — FORBIDDEN
DELETE FROM memories;                 -- Unscoped delete — FORBIDDEN
DELETE FROM conversations;            -- Unscoped delete — FORBIDDEN
UPDATE <any_table> SET <col> = val;  -- Without WHERE clause — FORBIDDEN
```

**Structural modification that destroys data:**
```sql
ALTER TABLE memories DROP COLUMN importance;
ALTER TABLE conversations DROP COLUMN summary;
```
*(Column drops are Level 4 in future phases when they exist, not Level 5. But they cannot be AI-generated. They must be hand-written migrations with explicit justification.)*

**Python ORM/SQLAlchemy equivalents:**
```python
Base.metadata.drop_all(engine)        # FORBIDDEN anywhere
Base.metadata.drop_all(bind=engine)   # FORBIDDEN anywhere
table.drop(engine)                    # FORBIDDEN anywhere
engine.execute("DROP TABLE ...")      # FORBIDDEN anywhere
session.execute(text("TRUNCATE ...")) # FORBIDDEN anywhere
```

**Alembic commands on production data:**
```
alembic downgrade -1          # FORBIDDEN in production
alembic downgrade base        # FORBIDDEN in production
alembic stamp base            # FORBIDDEN without written justification
```

---

### 3.3 Git Destructive Operations

The following git commands are FORBIDDEN.

**History rewriting:**
```
git reset --hard
git reset --hard HEAD
git reset --hard HEAD~1
git reset --hard HEAD~N
git reset --hard <commit-hash>
git reset --mixed HEAD~N     (when commits are pushed)
git reset --soft HEAD~N      (when commits are pushed, without coordination)
git commit --amend           (when the commit has been pushed)
git rebase <any>             (on shared branches: main, develop)
git rebase -i HEAD~N         (when commits are pushed)
git filter-branch <any>
git filter-repo <any>
```

**Forced remote operations:**
```
git push --force
git push -f
git push --force-with-lease  (Level 4 — requires Level 5 process if on main/develop)
git push origin +<branch>
git push origin :main        (deleting remote branch)
git push origin :develop     (deleting remote branch)
```

**Workspace destruction:**
```
git clean -fd
git clean -fdx
git clean -fx
git clean -f
git checkout -- .            (discarding all unstaged changes)
git restore .                (discarding all unstaged changes, no backup)
```

**Tag and reference destruction:**
```
git tag -d <tag>             (if tag has been pushed)
git push origin :refs/tags/<tag>
git reflog expire --expire=now --all
git gc --prune=now --aggressive
```

**Submodule destruction:**
```
git submodule deinit -f .
```

---

### 3.4 Qdrant Destructive Operations

```python
client.delete_collection("episodic_memory")    # FORBIDDEN without backup
client.delete_collection("document_knowledge") # FORBIDDEN without backup
client.recreate_collection(...)                 # FORBIDDEN without backup
client.delete_vectors(...)                      # FORBIDDEN without scoped review
```

**Qdrant Docker volume:**
```
docker volume rm <qdrant_volume>               # FORBIDDEN
docker compose down -v                          # FORBIDDEN (destroys volumes)
docker compose down --volumes                   # FORBIDDEN (destroys volumes)
```

**Note on `docker compose down`:** The plain `docker compose down` command (without `-v` or `--volumes`) is PERMITTED — it stops containers without removing volumes. Always verify the exact flags before executing.

---

### 3.5 Redis Destructive Operations

```
FLUSHALL                    # FORBIDDEN in all environments
FLUSHDB                     # FORBIDDEN (destroys session data, budget counters)
DEBUG RELOAD                # FORBIDDEN
CONFIG SET save ""          # FORBIDDEN (disables persistence)
```

**Python equivalent:**
```python
redis_client.flushall()     # FORBIDDEN
redis_client.flushdb()      # FORBIDDEN
redis_client.delete("*")    # FORBIDDEN
```

**Permitted in development only (not production data):**
```python
# PERMITTED for test cleanup only, in test fixtures with explicit test DB:
test_redis_client.flushdb()  # Only against isolated test Redis instance
```

---

### 3.6 System-Level Destructive Operations

```
# Windows CMD
format C:
diskpart
net stop <critical_service>
sc delete <service>

# PowerShell
Stop-Service -Force
Remove-Service
Clear-EventLog

# Python system calls
os.system("rm -rf ...")              # FORBIDDEN
subprocess.run(["rm", "-rf", ...])   # FORBIDDEN
subprocess.call(["format", ...])     # FORBIDDEN

# Python file operations on system paths
shutil.rmtree("C:/Windows/...")      # FORBIDDEN (and catastrophic)
```

---

### 3.7 AI-Generated Code Specific Rules

These rules apply specifically to output from Antigravity IDE, Claude, Gemini, or any AI code generation tool.

**Rule AG-1: Review before execute.**  
No AI-generated script, migration file, or command sequence may be executed without human review. "It looks right" is not a review. A review reads every line and understands its effect.

**Rule AG-2: Shell scripts require full audit.**  
Any AI-generated shell script (`.ps1`, `.sh`, `.bat`, `.cmd`) must be audited for forbidden commands before a single line executes. Audit means: search the script for every pattern in Section 3.1, 3.2, 3.3.

**Rule AG-3: Database migrations require hand verification.**  
Any AI-generated Alembic migration file must be read line by line before `alembic upgrade head` is run. The developer must be able to describe exactly what every operation in the migration does to the data.

**Rule AG-4: AI does not approve AI.**  
AI-generated code cannot be validated by asking another AI "does this look safe?" The human developer is the only validator for safety-classified operations.

**Rule AG-5: Suspicious helpfulness is a warning sign.**  
If an AI tool generates a "cleanup script," "reset procedure," "database initialization," or "fresh start" routine, treat it as high-risk regardless of how helpful it appears. These task descriptions correlate with destructive operations.

**Rule AG-6: ARCHITECTURE_RULES.md must be in every prompt.**  
Every AI code generation session must include the content of `docs/architecture/ARCHITECTURE_RULES.md` at the top of the prompt. Omitting it allows the AI to generate architecturally invalid code that appears syntactically correct.

**Rule AG-7: Verify permissions before executing agentic suggestions.**  
When Aether itself generates or suggests commands via its own agent capabilities, those commands are subject to the same review as externally generated code. Aether's agents are not exempt from these rules.

---

### 3.8 The Level 5 Override Process

A Level 5 operation may only be executed after completing ALL of the following steps. There are no exceptions.

**Step 1: DOCUMENT THE NEED**  
Open a GitHub issue or create a dated entry in `docs/architecture/operations-log.md` that states:
- What specific operation is required
- Why it is required
- What will be destroyed
- Why there is no alternative that avoids destruction

**Step 2: VERIFY BACKUP**  
Run `infrastructure/scripts/backup.ps1` and confirm:
- The backup completed without errors
- The backup file exists at the expected path
- The backup file size is within expected range (not 0 bytes, not suspiciously small)
- The backup timestamp is current (within the last 10 minutes)

**Step 3: TEST RESTORE**  
Before executing the destructive operation, verify that the backup can actually be restored:
- For SQLite: copy the backup file, attempt to open it, run a SELECT query
- For Qdrant: verify the snapshot file is valid (Qdrant snapshot info API)
- For Redis: verify the RDB file is readable

If the restore test fails, STOP. Do not proceed until the backup is verified restorable.

**Step 4: DEFINE ROLLBACK**  
Write out, in the issue or operations log, the exact commands that will restore the system to its current state if the operation fails or produces unexpected results. This must be specific and executable, not general.

**Step 5: WAIT 24 HOURS**  
After completing Steps 1-4, wait 24 hours before executing. This is a mandatory cooling-off period. If the urgency is so great that 24 hours is impossible, the operation is not being planned — it is being panicked. Panic is not a valid justification.

**Exception to the 24-hour rule:** If the system is already in a broken state due to a prior failure and the destructive operation is part of recovery, the waiting period may be reduced. Document why in the operations log.

**Step 6: EXECUTE WITH CONFIRMATION**  
Type the command manually. Do not copy-paste destructive commands. Typing the command forces active engagement with each character and prevents executing the wrong command from clipboard.

**Step 7: VERIFY OUTCOME**  
Immediately after execution, verify the system is in the expected state. Do not move on to the next task until this is confirmed.

**Step 8: DOCUMENT COMPLETION**  
Update the issue or operations log with: what was executed, what the outcome was, and whether the backup was needed.

---

## 4. BACKUP REQUIREMENTS

### 4.1 Backup Schedule

| Trigger | Backup Type | Required |
|---|---|---|
| Before any Level 4 operation | Full backup | Mandatory |
| Before any Level 5 operation | Full backup + restore test | Mandatory |
| Daily at 02:00 (Windows Task Scheduler) | Automated full backup | Mandatory |
| Before every `alembic upgrade` | Database backup | Mandatory |
| Before Docker image updates | Configuration backup | Recommended |
| Before dependency version updates | State snapshot | Recommended |

### 4.2 Backup Contents

A complete backup includes ALL of the following. A partial backup is not a backup.

```
backups/
  YYYYMMDD-HHMMSS/
    aether_db.sqlite              # SQLite database file (exact copy)
    qdrant_snapshot.tar.gz        # Qdrant collection snapshot via API
    redis_dump.rdb                # Redis persistence file
    config_backup.yaml            # config/default.yaml + config/local.yaml
    permissions_backup.yaml       # .aether/permissions.yaml
    backup_manifest.json          # {timestamp, file_sizes, checksums, verified: bool}
```

### 4.3 Backup Verification

A backup is only valid if `backup_manifest.json` contains `"verified": true`. The verification process:
- Confirms each expected file exists
- Confirms each file has non-zero size
- Confirms SQLite file opens and returns row counts
- Confirms Qdrant snapshot file is parseable
- Confirms Redis RDB file is not corrupt

The `backup.ps1` script sets `"verified": false` initially and sets it to `true` only after all checks pass. A backup with `"verified": false` must be treated as potentially unusable.

### 4.4 Backup Retention

- Daily automated backups: retain 30 days
- Pre-operation backups: retain permanently (until explicitly deleted per Section 3.8)
- Monthly archives: retain permanently

Backup storage location: `backups/` directory (gitignored). Periodically copy backups to secondary storage (external drive or cloud storage). The project has no automated secondary backup in Phase 1 — this is a manual responsibility.

---

## 5. ROLLBACK REQUIREMENTS

### 5.1 When Rollback Is Required

A rollback is required when:
- An operation produces unexpected results
- An operation fails partway through
- System behavior changes unexpectedly after an operation
- Data appears corrupted or missing after an operation

### 5.2 Rollback Procedures by Operation Type

**Database migration rollback:**  
```
# Before running this, verify backup exists and is verified
alembic downgrade -1
# Restore data from backup if migration deleted data
```
Note: `alembic downgrade` is normally a Level 3 forbidden operation. In a rollback context, it is the correct tool. Document the reason in the operations log.

**SQLite data rollback:**  
```
# Stop aether-core (Ctrl+C or stop.ps1)
# Copy backup file over current database
copy backups\YYYYMMDD-HHMMSS\aether_db.sqlite data\aether.db
# Verify: start aether-core, confirm expected data present
```

**Qdrant rollback:**  
```
# Use Qdrant snapshot restore API
# PUT /collections/{collection_name}/snapshots/recover
# Body: {"location": "path/to/snapshot"}
# Verify: run test queries, confirm expected vectors present
```

**Redis rollback:**  
```
# Stop Redis container
# Copy backup RDB file to Redis data volume
# Restart Redis container
# Verify: check session data, budget counters
```

### 5.3 Rollback Validation

After any rollback, the following must be confirmed before resuming normal operation:
- All services start without errors
- Memory retrieval returns expected results
- Task data is intact
- The operation that required rollback is understood and documented

---

## 6. RECOVERY REQUIREMENTS

### 6.1 Recovery Scenarios and Procedures

**Scenario A: Accidental file deletion**  
1. STOP all activity immediately
2. Check Windows Recycle Bin first
3. If not in Recycle Bin: check backup from Section 4
4. If no backup: check git history for the file
5. If git does not have it: recovery may not be possible — document the loss
6. After recovery: create a pre-operation backup before continuing

**Scenario B: Database corruption**  
1. Stop aether-core immediately
2. Do not attempt to repair the database — restoration is safer
3. Find the most recent verified backup (check `backup_manifest.json`)
4. Follow SQLite rollback procedure from Section 5.2
5. Assess: how much data was lost (time gap between backup and corruption)
6. Document the cause if known

**Scenario C: Qdrant vector store loss**  
1. Memory retrieval will fail — aether-core will log errors
2. Stop memory consolidation operations
3. Restore from most recent Qdrant snapshot
4. Verify collection exists and contains expected record count
5. If snapshot restoration fails: vector data must be rebuilt by re-embedding all memories from SQLite (run re-indexing tool — to be built in Phase 2)

**Scenario D: Git history corruption**  
1. Do not push any changes
2. Assess: what commits are affected?
3. If on a feature branch: examine options without affecting shared branches
4. If on main/develop: escalate — this is a serious situation
5. Use `git reflog` to find the last known good state
6. Document everything before executing any recovery commands

**Scenario E: Complete system loss (all data deleted)**  
1. Check the most recent backup in `backups/`
2. Restore all components in order: SQLite → Qdrant → Redis
3. Verify each component before moving to the next
4. Assess total data loss from backup timestamp to current time
5. Document: what was lost, when, what caused it, how to prevent it

---

## 7. REPOSITORY PROTECTION RULES

### 7.1 Branch Structure

```
main          Protected. Production-equivalent. All milestones tagged here.
develop       Protected. Integration branch. All feature branches merge here first.
phase/N       Protected. Phase-specific integration branch.
feature/X     Unrestricted. Individual feature development.
fix/X         Unrestricted. Bug fix branches.
experiment/X  Unrestricted. Experimental work — never merged to main directly.
```

### 7.2 Branch Protection Rules (GitHub Settings)

**`main` branch:**
- Require pull request before merging: YES
- Required approvals: 1 (for solo developer: self-review via PR description)
- Dismiss stale reviews when new commits are pushed: YES
- Require status checks to pass before merging: YES
  - Required checks: `ci / lint`, `ci / architecture-check`, `ci / test`
- Require branches to be up to date before merging: YES
- Require conversation resolution before merging: YES
- Do not allow bypassing the above settings: YES
- Allow force pushes: NO
- Allow deletions: NO

**`develop` branch:**
- Require pull request before merging: YES (recommended — even for solo developer)
- Required approvals: 0 (solo developer may self-merge after CI passes)
- Require status checks to pass before merging: YES
  - Required checks: `ci / lint`, `ci / architecture-check`, `ci / test`
- Allow force pushes: NO
- Allow deletions: NO

**Feature branches:**
- No protection rules. Full flexibility.
- Must not be named `main`, `develop`, or `phase/*`.

### 7.3 Commit Standards

**Commit message format:**
```
type(scope): short description (50 chars max)

Body: detailed explanation of what and why (not how).
Wrap at 72 characters.

Refs: #issue-number (if applicable)
ADR: ADR-XXX (if this commit implements an architectural decision)
```

**Permitted commit types:**
- `feat` — new capability added
- `fix` — bug correction
- `refactor` — code change without behavior change
- `test` — test additions or modifications
- `docs` — documentation only
- `config` — configuration changes
- `infra` — infrastructure, Docker, scripts
- `milestone` — marks completion of a defined milestone

**Forbidden commit practices:**
- Commits directly to `main` or `develop` (bypasses PR process)
- Commit messages that are single words: "fix", "update", "changes", "stuff"
- Commit messages in all caps
- Commit messages with emoji as the primary identifier
- Commits that bundle unrelated changes (one logical change per commit)
- Commits with "WIP", "temp", "hack", or "broken" in the message that are pushed to shared branches

### 7.4 Tag Standards

Tags mark milestone completion and phase boundaries. They are permanent records.

```
Format:        v{major}.{minor}.{patch}-{label}
Phase tags:    v0.1.0-phase1-complete
Milestone tags: v0.1.0-m1.7-agents
Pre-release:   v0.1.0-alpha.1
```

Tags are created manually. No automated tagging. Once pushed, a tag is permanent — do not delete pushed tags.

---

## 8. CI/CD SAFETY GATES

### 8.1 Required CI Checks (all must pass before merge to develop or main)

**Gate 1: Architecture Boundaries**  
Command: `uv run lint-imports`  
Failure action: Block merge. No exceptions.  
Purpose: Prevents AI-generated code from violating module boundaries.

**Gate 2: Static Analysis**  
Command: `uv run ruff check .`  
Failure action: Block merge. No exceptions.  
Purpose: Catches forbidden patterns, unused imports, and code quality violations.

**Gate 3: Type Safety**  
Command: `uv run mypy aether/ --strict`  
Failure action: Block merge. No exceptions.  
Purpose: Prevents type errors that only manifest at runtime.

**Gate 4: Unit Tests**  
Command: `uv run pytest tests/unit/ -x`  
Failure action: Block merge. No exceptions.  
Purpose: Verifies core module behavior.

**Gate 5: Contract Tests**  
Command: `uv run pytest tests/contracts/ -x`  
Failure action: Block merge. No exceptions.  
Purpose: Ensures public API signatures have not changed unexpectedly.

**Gate 6: Forbidden Pattern Scan**  
Command: `grep -r "DROP TABLE\|TRUNCATE\|rm -rf\|flushall\|drop_all" aether/ services/ migrations/`  
Failure action: Block merge. Any match is a violation.  
Purpose: Catches destructive operations that might appear in AI-generated code.

### 8.2 The Forbidden Pattern Scan

This scan runs on every commit pushed to any branch. It catches the most dangerous patterns regardless of context:

```yaml
# .github/workflows/safety-scan.yml patterns:
patterns:
  - "DROP TABLE"
  - "DROP DATABASE"
  - "TRUNCATE TABLE"
  - "TRUNCATE "
  - "metadata.drop_all"
  - "flushall"
  - "flushdb"
  - "rm -rf"
  - "shutil.rmtree"
  - "Remove-Item -Recurse"
  - "del /f /s"
  - "git reset --hard"
  - "git clean -f"
  - "git push --force"
  - "git push -f"
```

**Exception handling for legitimate uses:** If a pattern appears in a comment explaining why it is forbidden (such as this document), the scan must exclude `docs/` and `tests/fixtures/`. Application code, migration files, and scripts have no exceptions.

---

## 9. CONSEQUENCES

### 9.1 When This ADR Is Violated

Violations of this document are not treated as mistakes to quietly fix. They are treated as process failures that require documentation and prevention.

When a violation occurs:
1. **Stop** all related activity immediately
2. **Assess** the damage — what state is the system in?
3. **Restore** from backup if data was lost
4. **Document** what happened in `docs/architecture/operations-log.md`
5. **Identify** which rule was violated and why
6. **Add** a new prevention measure if the existing rules did not prevent it
7. **Update** the CI safety scan if the violation pattern can be automated

### 9.2 Why These Rules Are Not Optional

The rules in this document exist because the cost of not having them is unacceptable. A personal AI OS that loses five years of memories and conversations is not recoverable with an apology. The data is gone. The rules protect against that outcome.

An AI code generator that is asked "generate a database reset script" will generate one. If that script runs without review, years of data are gone in under one second. The human developer is the only safeguard between AI-generated code and irreversible destruction.

These rules make that safeguard explicit, systematic, and enforceable.

---

*Document Version: 1.0*  
*Status: ACCEPTED — ENFORCED*  
*Review Trigger: Any safety incident, or at completion of each phase*  
*Owner: Principal Systems Engineer*  
*Next Review: Phase 1 Completion*

---

## 10. ARCHITECTURAL AUTHORITY RULES

### 10.1 The Authority Principle

Architecture is not a suggestion. The architecture of Aether AI OS has been deliberated, documented, audited, challenged, and formally decided across four authoritative documents. Those decisions represent significant intellectual investment and have long-term consequences that outweigh any short-term convenience.

**No AI tool has architectural authority. No generated artifact has architectural authority. No code has architectural authority. Only approved ADR documents have architectural authority.**

### 10.2 What Requires an Approved ADR

The following changes may not be implemented without an ADR document that is written, reviewed by the developer, and committed to `docs/architecture/decisions/` before a single line of implementation code is written.

**New infrastructure components:**
- Any new Docker service
- Any new database engine (beyond SQLite, PostgreSQL, Redis, Qdrant)
- Any new message queue or broker
- Any new external storage system
- Any new process that runs alongside existing processes

**New architectural layers:**
- Any new module category that does not exist in the current module taxonomy
- Any new communication pattern between modules (e.g., introducing gRPC where REST was specified)
- Any new abstraction layer that sits between existing layers
- Any new service boundary that splits an existing module into separately deployable units

**New communication protocols:**
- Any new inter-service communication mechanism (e.g., introducing WebSockets where Redis Streams were specified)
- Any new event bus technology
- Any new serialization format for cross-module communication
- Any protocol that creates a new integration point between modules

**New external dependencies that alter architecture:**
- Any dependency that introduces a new runtime (e.g., a dependency that requires Node.js in a Python service)
- Any dependency that introduces a new database paradigm (e.g., a document store, a time-series database)
- Any dependency that introduces a new communication technology
- Any dependency that replaces a technology already specified in an existing ADR

### 10.3 What AI Tools May Not Introduce

The following are explicitly forbidden in AI-generated code. If an AI tool generates code containing any of the following without a prior approved ADR, the generated code is rejected in its entirety. The developer does not selectively adopt the parts that do not violate this rule — the entire generation is discarded and the prompt is corrected.

```
AI TOOLS MAY NOT INTRODUCE:

New services:
  A new Docker container, a new separately deployable Python process,
  a new microservice, or a new standalone process of any kind.

New databases:
  MongoDB, Cassandra, DynamoDB, Elasticsearch, InfluxDB, CouchDB,
  or any database not currently in the approved technology stack.

New infrastructure components:
  Message queues (RabbitMQ, Kafka, NATS), service meshes, API gateways,
  load balancers, container orchestrators, or any infrastructure software
  not currently in the approved stack.

New architectural layers:
  An event sourcing layer, a CQRS read model, a cache-aside pattern
  introduced at a new layer, or any pattern that reorganizes the
  current module hierarchy.

New communication protocols:
  GraphQL (where REST is specified), gRPC (before Phase 5),
  WebSocket (where Redis Streams are specified), or AMQP.

New external dependencies that alter architecture:
  A dependency whose inclusion requires changing how modules communicate,
  requires a new runtime, or requires a new infrastructure service.
```

### 10.4 The ADR Requirement for Architecture Changes

An ADR that proposes an architectural change must contain all of the following. An ADR missing any element is incomplete and does not constitute approval.

**Section 1: Context**  
What specific limitation or problem has been encountered that the current architecture cannot address? This section must describe a concrete, observed problem — not a hypothetical future problem.

**Section 2: Decision**  
What specific change is being proposed? This must be precise enough that an engineer who did not participate in the decision can implement it unambiguously.

**Section 3: Alternatives Considered**  
At minimum two alternative approaches must be described. For each:
- What would this alternative require?
- What are its advantages over the proposed decision?
- Why is it not being chosen?

**Section 4: Tradeoff Analysis**  
What does the proposed decision cost? Every architectural change has costs. If an ADR claims there are no costs, it is incomplete. Costs include: development time, operational complexity, learning curve, performance impact, maintenance burden, and future extraction cost.

**Section 5: Consequences**  
What other parts of the system will need to change as a result of this decision? What becomes easier? What becomes harder?

**Section 6: Approval Record**  
Date of decision. Confirmation that the developer has read and understood the full ADR. Confirmation that all prior ADRs remain consistent with this new decision or have been updated.

---

## 11. DEPENDENCY GOVERNANCE

### 11.1 The Dependency Principle

Every dependency is a long-term commitment. A dependency added in Phase 1 will be in the project in Phase 10. Dependencies introduce: security vulnerabilities, breaking changes, maintenance obligations, license risks, and intellectual coupling to external project trajectories. No dependency is free.

**Before adding any new dependency, the developer must be able to answer:**
- What specific capability does this dependency provide that I cannot implement in a reasonable time?
- Is this dependency actively maintained by a credible source?
- What happens to Aether if this dependency is abandoned?
- Does this dependency have known security vulnerabilities?
- Does this dependency conflict with or duplicate any existing approved dependency?
- Does this dependency alter the architecture in a way that requires an ADR?

### 11.2 Dependency Approval Process

No new dependency may be added to `pyproject.toml` without completing and committing a `docs/architecture/dependencies/{package-name}.md` evaluation document containing:

```markdown
# Dependency Evaluation: {package-name}

Date: YYYY-MM-DD
Status: APPROVED | CONDITIONAL | EXPERIMENTAL | FORBIDDEN
Proposed by: Developer | AI-generated suggestion

## Purpose
Exactly what capability is this dependency providing?
Why cannot this capability be implemented directly or sourced from an existing dependency?

## Package Information
- PyPI name: {name}
- Current version: {version}
- License: {license}
- Repository: {url}
- Download statistics: {weekly_downloads}
- Last commit date: {date}
- Open issues: {count}
- Known CVEs: {list or "None known"}

## Maintenance Evaluation
- Is the project actively maintained? (commits in last 6 months)
- Is there a responsive maintainer?
- Is there a clear release cadence?
- Is the project's future trajectory stable or uncertain?

## Security Evaluation
- Has this package had security vulnerabilities in the past 2 years?
- Does this package have transitive dependencies with known issues?
- Does pip-audit or safety report any issues with this version?

## Community Adoption
- Is this package widely used in comparable projects?
- Does it have community trust indicators (stars, forks, downstream dependents)?
- Are there credible production users?

## Alternative Analysis
What alternatives were evaluated? For each:
- Name and URL
- Why was it not chosen?

## Impact on Architecture
- Does this dependency introduce a new technology paradigm? (requires ADR if yes)
- Does this dependency create coupling to a specific cloud provider or vendor?
- Does this dependency affect the VRAM or RAM budget?

## Decision
Approved | Conditional (with conditions) | Experimental | Forbidden
Reasoning:
```

### 11.3 Dependency Classifications

**APPROVED**  
Dependencies in `pyproject.toml` that have passed the evaluation process and are authorized for unrestricted use in their designated scope.

Current approved dependencies are defined in the Technical Specification Appendix A. Any dependency already in that list is approved without further evaluation.

**CONDITIONAL**  
Dependencies that are approved but carry usage restrictions. The restrictions are documented in the evaluation file.

Examples of conditional dependencies:
- A dependency approved only for use in test files, not production code
- A dependency approved only within a specific module (e.g., a database driver approved only in `aether/memory/_stores/`)
- A dependency approved only for use on Windows (not required for cross-platform compatibility)

**EXPERIMENTAL**  
Dependencies that are under evaluation. They may appear in development branches and non-production code. They may not appear in `main`. An experimental dependency must complete the full evaluation process and be re-classified as APPROVED or FORBIDDEN before it can be included in a milestone release.

**FORBIDDEN**  
Dependencies that are explicitly prohibited. The evaluation file records why.

Automatic classification as FORBIDDEN (no evaluation required):
- Any package with an active CVE that has not been patched in the current version
- Any package abandoned for more than 18 months (no commits, no maintainer response to issues)
- Any package that duplicates the exact functionality of an already-approved package
- Any package that bypasses the model-agnostic architecture (e.g., an Anthropic SDK used outside `aether/llm/`)
- Any package with a license incompatible with the project's intended use

### 11.4 AI-Suggested Dependencies

When an AI code generation tool suggests adding a new dependency (by generating an import statement for an unapproved package, or by explicitly recommending `pip install {package}`), the following applies:

1. The suggestion is noted but not acted upon immediately
2. The dependency evaluation process in Section 11.2 is completed
3. The dependency is classified per Section 11.3
4. Only after approval is the dependency added to `pyproject.toml`

AI tools frequently suggest adding dependencies as the path of least resistance for any implementation task. This optimization is misaligned with a long-term project's needs. The developer decides what enters the dependency tree, not the AI.

---

## 12. PLACEHOLDER AND TEMPORARY CODE POLICY

### 12.1 The Permanent Code Principle

Code in this repository is assumed to be permanent until explicitly removed. There is no "temporary" state in a committed codebase. Code marked as temporary tends to outlive its intended lifetime by months or years. Aether is a five-year project — "temporary" code written in Phase 1 will be found during Phase 8.

**The solution to code that is not ready is not to mark it as temporary. The solution is to not commit it until it is ready.**

### 12.2 Explicitly Forbidden Markers

The following markers are forbidden in any file committed to the repository. Their presence in a committed file is a Zero-Tolerance Violation.

```
# TODO:         — signals deferred work (defer it outside the codebase)
# FIXME:        — signals known broken code (fix it before committing)
# HACK:         — signals deliberate technical debt (eliminate it before committing)
# TEMP:         — signals intended removal (remove it before committing)
# KLUDGE:       — signals inelegant workaround (replace it before committing)
# XXX:          — signals unclear or problematic code (resolve it before committing)
# NOTE: remove  — signals code that should not persist (remove it before committing)
# WORKAROUND:   — signals a bypass of proper implementation (implement properly before committing)
```

Additionally forbidden:
- Commented-out code blocks of any kind
- `pass` as the sole implementation of a non-abstract, non-explicitly-empty function
- `...` (Ellipsis) as the sole implementation of any function outside `.pyi` type stub files
- Functions that return hardcoded values as a placeholder for real logic
- Validation functions that always return `True` without checking anything
- Authentication functions that always succeed without verifying credentials
- Permission checks that are bypassed with a comment indicating they will be added later

### 12.3 Mock and Fake Security Validation

This category is explicitly called out because it is uniquely dangerous. Mock security validation appears safe during development and creates catastrophic vulnerabilities if it persists.

**Forbidden:**
```python
# FORBIDDEN — permission check that always passes
async def check_permissions(action: str, path: Path) -> bool:
    return True  # TODO: implement real permission check

# FORBIDDEN — safety validator that always approves
class SafetyValidator:
    def validate(self, action: str) -> ValidationResult:
        return ValidationResult(allowed=True, reason="stub")

# FORBIDDEN — authentication bypass
async def authenticate(token: str) -> bool:
    return True  # Implement later

# FORBIDDEN — permission check commented out
async def delete_file(path: Path) -> None:
    # await permission_check(path)  # TODO: enable this
    await actual_delete(path)
```

These patterns are refused regardless of how clearly they are marked as temporary or how many comments explain that they will be replaced. They may not enter the repository.

### 12.4 Acceptable Alternatives to Temporary Code

When a feature is not yet implementable because its dependencies do not exist:

**Option 1: Do not create the function yet.**  
A function that cannot be properly implemented is not added to the codebase until its implementation is ready. Its existence as a stub provides no value and creates the false impression of completeness.

**Option 2: Raise NotImplementedError with a specific reference.**  
If the function must exist as an interface definition before its implementation is ready (for example, to satisfy an abstract base class), it raises `NotImplementedError` with a specific reference to when and in which milestone it will be implemented.

**Option 3: Create a stub module with explicit status.**  
If an entire module is planned but not yet implemented, create the `__init__.py` with a module-level docstring that states: its planned purpose, its target milestone, and that it is intentionally incomplete. The module contains no stub functions — only the docstring.

**Option 4: Use feature flags in configuration.**  
If a partially-implemented feature must be in the codebase but not yet active, gate it with a `config.features.{feature_name}` boolean. The feature flag is disabled by default. The code behind the flag must be fully implemented — the flag controls activation, not implementation completeness.

---

## 13. TECHNICAL DEBT GOVERNANCE

### 13.1 The Debt Principle

Technical debt is a conscious decision to accept a known limitation in exchange for a specific benefit. It is not a synonym for incomplete work, poor quality, or deferred cleanup. Genuine technical debt is a deliberate trade-off with a documented rationale, a defined cost, and a scheduled resolution.

Technical debt that is hidden is not technical debt — it is latent defect. All technical debt must be visible.

### 13.2 The Debt Register

**File:** `docs/technical-debt/DEBT_REGISTER.md`  
**Format:** One entry per debt item  
**Updated:** When debt is incurred (within the same commit), at each phase completion review, and when debt is resolved

```markdown
## DEBT-{NNN}: {Short Title}

**Date incurred:** YYYY-MM-DD  
**Incurred in:** Milestone X.Y — {milestone name}  
**Priority:** P1 | P2 | P3  
**Status:** Open | In Progress | Resolved  
**Resolved date:** YYYY-MM-DD (if resolved)  

**Location:**
  File(s): aether/{module}/{file}.py lines {N-N}

**Description:**
  What is the known limitation or suboptimal implementation?

**Reason accepted:**
  Why was this trade-off made? What benefit was gained?
  (If no clear benefit was gained, this is not debt — it is a defect. Fix it.)

**Cost:**
  What is the ongoing cost of carrying this debt?
  Performance: {impact}
  Maintainability: {impact}
  Correctness risk: {impact}

**Resolution plan:**
  What specific work will eliminate this debt?
  Target milestone: {milestone identifier}
  Estimated effort: {hours or days}

**Blocked by:**
  Is this debt's resolution blocked by another milestone or deliverable?
```

### 13.3 Priority Classifications

**P1 — Architecture Debt**  
Debt that affects the structural integrity of the system. It creates coupling that should not exist, violates a module boundary that has an approved workaround, or implements an interface inconsistently with the specification. P1 debt **must be resolved before the milestone in which it was incurred is marked complete.** If it cannot be resolved before the milestone completes, the milestone is not complete.

**P2 — Quality Debt**  
Debt that degrades code quality, maintainability, or reliability without violating architectural boundaries. It includes: insufficient test coverage for a stable module, documentation that is present but incomplete, performance that is acceptable but below the target specified. P2 debt **must have a documented resolution plan before the phase in which it was incurred is marked complete.** It must be resolved within the next phase.

**P3 — Efficiency Debt**  
Debt that represents an optimization opportunity that was deferred for legitimate reasons. The system works correctly, the architecture is sound, but a more efficient implementation is known and deferred. P3 debt is tracked and addressed when the target area is next modified for other reasons, or at the phase completion review.

### 13.4 Debt Review Process

**At each milestone completion:**
- The developer reviews all open debt items
- Any P1 debt that exists means the milestone is not complete
- P2 debt is assessed: is there a credible resolution plan? Has the plan been updated?
- P3 debt is reviewed for relevance: does it still represent a meaningful improvement?

**At each phase completion:**
- All P2 debt from the phase must be resolved or have an approved carry-forward
- P3 debt is reviewed and either carried forward or closed as "will not fix"
- The debt register is published in the phase completion document

**Debt that cannot be eliminated:**
If a debt item is reviewed at phase completion and determined to be permanently unresolvable, it is not closed — it is reclassified. If it represents an ongoing cost, it is escalated to P2 or P1 depending on its impact. If it represents an accepted permanent trade-off, it is documented as such with an explicit architectural decision.

### 13.5 What Is Not Technical Debt

The following are not technical debt and must not be recorded in the debt register. They are defects and must be resolved before the code that contains them is committed:

- Missing type annotations
- Missing tests for new public functions
- Missing docstrings
- Silent exception handling
- Magic values
- Hardcoded configuration
- Architecture boundary violations

These are quality requirements, not trade-offs. Their absence does not represent a conscious decision — it represents incomplete work.

---

## 14. ARCHITECTURE DRIFT PREVENTION

### 14.1 The Drift Problem

Architecture drift is the gradual divergence between the documented architecture and the implemented architecture. It does not happen in large violations that are easy to detect. It happens in small, individually reasonable decisions that collectively corrupt the structural integrity of the system.

A module that imports one internal submodule from a neighboring module is drift. An agent that calls an LLM provider directly "just this once" is drift. A configuration value that is hardcoded "temporarily" is drift. Each individual decision appears harmless. After twelve months, the system does not resemble its specification.

Automated enforcement prevents the kind of drift that is detectable by pattern matching. Human discipline prevents the kind that is not. Both are required.

### 14.2 Automated Drift Controls

**Control AD-1: Import boundary enforcement (runs on every commit)**  
`lint-imports` enforces every module boundary contract defined in `pyproject.toml`. Any import that crosses a defined boundary fails the pre-commit hook. This control is continuous and automatic.

**Control AD-2: Forbidden pattern scan (runs on every commit)**  
The CI workflow scans for patterns defined in ADR-010 Section 3. Any match fails the pipeline. This control is continuous and automatic.

**Control AD-3: Type safety enforcement (runs on every commit)**  
`mypy --strict` catches type-level drift: functions whose signatures have drifted from the specification, Pydantic models that have evolved inconsistently, and return types that do not match declared contracts. This control is continuous and automatic.

**Control AD-4: Contract test suite (runs on every PR)**  
Contract tests in `tests/contracts/` verify that public API signatures have not changed from their specified forms. Any method rename, parameter addition without a default, or return type change fails the contract tests. This control is per-PR and automatic.

### 14.3 Manual Drift Controls

**Control AD-5: Monthly architecture audit**  
On the first Monday of each month, the developer conducts an architecture audit. The audit is recorded in `docs/architecture/audits/YYYY-MM.md`.

The audit process:
1. Read the V1 Foundation Architecture Decision document
2. Read the V1 Technical Specification
3. For each module: confirm its public API matches the specification
4. For each boundary: confirm the boundary rules match the import-linter configuration
5. For each locked contract: confirm the implementation matches the locked specification
6. For each ADR: confirm the system behaves consistently with the decision
7. Record: what was verified, what discrepancies were found, what was resolved

**Control AD-6: Dependency audit (quarterly)**  
On the first Monday of each quarter, the developer conducts a dependency audit:
1. Run `pip-audit` or `uv run safety check` against current dependencies
2. Review all dependencies for new CVEs since the last audit
3. Identify any dependencies that have been abandoned or changed license
4. Identify any dependencies that are no longer used and can be removed
5. Record findings in `docs/architecture/dependency-audits/YYYY-QN.md`

**Control AD-7: Module ownership verification**  
Each module in `aether/` has a documented owner in `docs/architecture/MODULE_OWNERSHIP.md`. The owner is responsible for:
- The module's conformance to its specification
- Reviewing any PR that modifies the module
- Raising an architectural issue if the module's specification needs revision

For a solo developer, all module ownership belongs to the developer. This document serves as a record of which modules have been reviewed and when. At each monthly audit, the developer confirms the ownership record is current.

**Control AD-8: ARCHITECTURE_RULES.md currency check**  
At each monthly audit, the developer confirms that `ARCHITECTURE_RULES.md` reflects all current architectural constraints. If a new boundary has been established by a new ADR, the rules file is updated before the end of the audit session.

### 14.4 Handling Detected Drift

When drift is detected — whether by automated controls or manual audit — the response is:

1. **Identify scope:** How far has the drift propagated? Is it one file or many?
2. **Classify impact:** Does this drift violate a locked contract? Does it create real coupling? Is it cosmetic?
3. **Record:** Create a P1 or P2 debt item in the debt register, depending on severity
4. **Correct:** Resolve the drift. Do not document drift and leave it. Documentation of drift without correction is acceptance of drift.
5. **Prevent recurrence:** If automated controls did not catch this drift, update the controls so they will catch it in the future

Drift is not tolerated as a permanent condition. It is resolved.

---

## 15. AI CODE QUALITY ENFORCEMENT

### 15.1 The Trust Principle

AI-generated code is generated output, not reviewed output. The fact that an AI tool produced a code artifact does not mean the artifact is correct, safe, architecturally compliant, or production-quality. AI tools are sophisticated text generators that optimize for plausibility, not correctness.

**AI-generated code receives zero automatic trust. Every generated artifact requires human verification before it is used.**

This is not a statement about the capability of AI tools. It is a statement about the responsibility structure of this project. The developer is responsible for every line of code in the repository. AI tools assist in generating that code. They do not assume responsibility for it.

### 15.2 Required Verification for AI-Generated Code

All AI-generated code must pass the following verification before being committed. "It looks right" is not verification. Verification means reading every line and understanding its effect.

**Verification Level 1 — Every AI-generated file:**
- Read every line of the generated output
- Confirm no Zero-Tolerance Violations from ADR-011 Section 2
- Confirm no forbidden commands from ADR-010 Sections 3.1 through 3.6
- Run the pre-commit gate manually before committing
- Understand what every function does — if any function is unclear, clarify before committing

**Verification Level 2 — AI-generated files that touch boundaries:**
- Confirm all imports are from approved public module APIs
- Confirm no direct database, LLM provider, or tool implementation imports
- Confirm all events use the correct schema from Section 7 of the Technical Specification
- Confirm all new constants are named and all magic values are absent

**Verification Level 3 — AI-generated migration files and scripts:**
- Read every SQL statement in generated migration files
- Confirm no DROP, TRUNCATE, or unscoped DELETE statements
- Confirm the migration is additive where possible
- Test the migration on a copy of the database before running on the primary

**Verification Level 4 — AI-generated shell scripts and PowerShell scripts:**
- Search the generated script for every pattern in ADR-010 Section 3.1
- Confirm no file deletion operations without explicit scope
- Confirm no directory removal operations
- Run the script with no side effects first if a dry-run option exists

### 15.3 Architecture Contract Compliance

AI-generated code must comply with all architecture contracts. The contracts are:

| Contract | Enforcement |
|---|---|
| Memory access through MemoryAPI only | lint-imports |
| LLM calls through LLMRouter only | lint-imports |
| Tools called through registry only | Code review |
| Model names never in application logic | CI forbidden pattern scan |
| Events use correct schema | Contract tests |
| All functions typed | mypy --strict |
| All public functions documented | Code review |
| All configurations from config | Code review |
| All primary keys UUIDv7 | Code review |
| All timestamps UTC | Code review |

If AI-generated code violates any contract, the generated artifact is discarded. The prompt is revised to be more specific about the violated contract, with the relevant section of `ARCHITECTURE_RULES.md` explicitly included. The generation is retried. If the violation persists across multiple attempts, the code is written by the developer directly.

### 15.4 AI-Generated Code Standards Requirements

AI-generated code must meet the same standards as human-authored code. There is no "AI-generated exception" to any requirement in ADR-011. When AI-generated code fails a standard, the developer corrects it. The correction is not outsourced to the AI — the developer who accepts the code is the developer who is responsible for its quality.

**AI-generated code may not be committed with deferred quality remediation.** If the generated code does not meet standards, it is not committed until the standards are met. "I'll fix the types later" is not a valid state for committed code.

### 15.5 Prompt Hygiene

The quality of AI-generated code is directly related to the quality of the prompt. The following requirements apply to all prompts sent to AI code generation tools for this project:

**Required prompt elements:**
- The complete content of `docs/architecture/ARCHITECTURE_RULES.md`
- The complete content of `docs/architecture/AI_GENERATION_RULES.md`
- The relevant section of `docs/architecture/V1_TECHNICAL_SPECIFICATION.md` for the module being generated
- The public API signature of the module being implemented (if it exists in the spec)
- The exact forbidden patterns relevant to the generation task

**Forbidden prompt elements:**
- Instructions that could lead to security bypasses ("for now, skip the permission check")
- Instructions that could lead to temporary code ("just put a placeholder")
- Instructions that could lead to magic values ("use 0.8 as the threshold")
- Instructions that suggest architecture bypasses ("just import the Anthropic client directly")

If a prompt produces code that violates a standard, the prompt was incomplete or incorrect. Revise the prompt, not the standard.

---

## 16. PROJECT CONSTITUTION CLAUSE

### 16.1 The Constitutional Hierarchy

The following documents, taken together, constitute the **Aether Project Constitution**. They represent the foundational decisions and standards that govern all development on Aether AI OS.

**Constitutional documents in order of precedence:**

```
Tier 1 — Vision and Architecture:
  MASTER_BLUEPRINT.md                          (project vision and scope)
  V1_FOUNDATION_ARCHITECTURE.md                (official architecture decision)
  V1_TECHNICAL_SPECIFICATION.md               (implementation source of truth)

Tier 2 — Governance Standards:
  ADR-010-AI_SAFETY_AND_CODE_GENERATION.md    (this document)
  ADR-011-PRODUCTION_ENGINEERING_STANDARDS.md (quality standards)
  ARCHITECTURE_RULES.md                        (enforceable boundary rules)
  AI_GENERATION_RULES.md                       (AI generation constraints)

Tier 3 — Specific Decisions:
  ADR-001 through ADR-009                      (individual architecture decisions)
  Future ADR documents                         (as approved)
```

**Future governance documents** added to this project become part of the Constitution at the tier appropriate to their scope. A governance document that establishes a new project-wide standard becomes Tier 2. A document that records a specific architectural decision becomes Tier 3.

### 16.2 The Supremacy Clause

**No generated code may override, contradict, or circumvent any Constitutional document.**

This clause applies without exception to:
- Code generated by AI tools (Antigravity IDE, Claude, Gemini, or any other tool)
- Code written by the developer under time pressure
- Code introduced as a "temporary" measure
- Code introduced to enable a specific feature that "needs" an exception
- Code introduced because a Constitutional requirement "doesn't apply in this case"

When generated code contradicts a Constitutional document, the contradiction is resolved by revising the code, not by revising the Constitution. The Constitution is revised only through the deliberate process described in Section 16.4.

### 16.3 Constitutional Stability

The Aether Project Constitution is designed to be stable. It is not revised after every development session. It is not revised in response to the convenience of a specific implementation. It is not revised because an AI tool suggested an approach that conflicts with it.

The Constitution is revised when:
- A genuine architectural limitation is discovered through actual implementation experience (not hypothetical concern)
- A new phase introduces capabilities that require extending the architectural framework
- A Constitutional clause is found to be ambiguous or unenforceable in practice
- A security vulnerability requires an immediate amendment

Revisions to Tier 1 documents require the same deliberative process that produced the original documents: written context, analysis, alternatives considered, consequences documented.

Revisions to Tier 2 documents require: documented rationale, identification of what the prior version got wrong or what has changed, and a record of the revision in the document's version history.

Revisions to Tier 3 documents (individual ADRs) follow the standard ADR process: the original ADR is marked "Superseded by ADR-XXX" and the new ADR references it.

### 16.4 Constitutional Amendment Process

To amend any Constitutional document:

**Step 1:** Identify the specific clause or requirement that needs amendment and document why it needs to change.

**Step 2:** Determine whether the need for amendment is due to:
- A genuine gap or error in the original document (fix the document)
- A genuine new requirement introduced by a new phase (extend the document)
- Implementation experience that reveals the original approach is wrong (revise the document)
- Convenience or preference (this is not grounds for amendment)

**Step 3:** Draft the amendment. For Tier 1 documents, this follows the same process as the original architectural deliberation. For Tier 2-3 documents, document the rationale and the specific changes.

**Step 4:** Review the amendment against all other Constitutional documents for consistency.

**Step 5:** Commit the amendment. The amendment is not retroactive — it applies to code written after the amendment date.

### 16.5 The Self-Referential Clause

This document — ADR-010 — is part of the Constitution it establishes. Therefore, this document is itself subject to the supremacy clause. No generated code may override this document's rules, including the rule that this document is supreme over generated code.

This is not a paradox. It is the recognition that the rules of this project exist to protect the long-term integrity of the system, and that the rules themselves must be protected by the same principles of deliberate decision-making that created them.

---

---

## 17. PROJECT VERSIONING POLICY

### 17.1 The Gap This Section Fills

Section 7.4 defines tag *format*. This section defines what version numbers *mean*. Without a versioning policy, version increments are arbitrary and communicate nothing.

### 17.2 Semantic Versioning for Aether

Aether follows semantic versioning (`MAJOR.MINOR.PATCH`) with these specific definitions for a personal AI OS:

**MAJOR** increment when:
- A locked API contract (defined in V1_TECHNICAL_SPECIFICATION.md) changes its method signatures, parameter types, or return types in a way that breaks existing callers
- A data schema changes in a way that requires a migration that cannot be automatically reversed
- A Constitutional document is amended in a way that invalidates prior architectural decisions
- The system's fundamental interaction model changes (e.g., voice-first becomes a separate mode rather than the default)

**MINOR** increment when:
- A new capability is added (new tool, new agent, new service)
- A new event type is introduced to the event catalog
- A phase milestone is completed
- A new module is added to the approved module taxonomy
- A new skill is registered in the skill registry

**PATCH** increment when:
- A bug is corrected without behavior change
- A performance improvement is made without interface change
- Documentation is updated
- A dependency version is updated without API change
- A configuration default is adjusted

### 17.3 Version Number Governance

**Authoritative source:** `pyproject.toml` `[project].version` field. This is the only authoritative version number. It must be updated before a milestone tag is created. The tag and the pyproject.toml version must agree.

**During Phase 0-1 (pre-stable):** Version begins at `0.1.0`. It does not reach `1.0.0` until the system has been running daily for at least 6 months and Phase 5 (multi-agent) is complete. Version `0.x.x` signals that no API stability guarantees exist yet.

**Version file:** A `VERSION` file at repository root is not used. `pyproject.toml` is the single source of truth.

### 17.4 Internal API Versioning

Locked contracts (from V1_TECHNICAL_SPECIFICATION.md Section 5-7) are versioned via their `schema_version` field in event payloads and their method signatures in code. When a locked contract must change:

1. The old signature is preserved as a deprecated alias for one full phase
2. The new signature is introduced with a clear naming distinction
3. Callers are migrated in the same PR that introduces the new signature
4. The deprecated alias is removed at the next phase boundary
5. An ADR is written documenting the breaking change

**No locked contract breaks its callers without this process.**

### 17.5 Changelog Maintenance

`CHANGELOG.md` at the repository root is a first-class governance artifact, not an afterthought. It is updated at every milestone tag. Each entry follows this format:

```markdown
## v{version} — {date} — {milestone-label}

### Added
- [new capability or module]

### Changed
- [interface or behavior change with caller impact]

### Fixed
- [bug corrections]

### Performance
- [measured improvements with before/after numbers]

### Notes
- [anything the developer needs to remember about this release state]
```

A milestone tag without a CHANGELOG.md entry is an incomplete release. The Release Gate (ADR-011 Section 4, Gate Q-6) is not considered passed until the CHANGELOG.md entry is committed.

---

## 18. SOLO DEVELOPER SUSTAINABILITY PROTOCOL

### 18.1 Why This Section Exists

A solo developer building a 5-year AI OS is operating at a fundamentally different risk profile than a team project. Teams have shared context, peer review, and continuity across individual absences. A solo developer has none of these. The single greatest risk to Aether's long-term success is not a technical failure — it is context loss, scope creep, or decision fatigue causing the developer to lose the thread of the architecture across time.

This section establishes governance rules for sustainable solo development. These rules are not optional conveniences. They are architectural protections against the most likely failure mode of this project.

### 18.2 The Context Log

**File:** `docs/architecture/context-log.md`  
**Purpose:** A running record of current project state, written *for the developer's future self*.

**Format for each entry:**
```markdown
## Context Snapshot — {YYYY-MM-DD}

**Current milestone:** M1.X — {name}
**Milestone status:** {percent complete or specific blockers}

**What is actively in progress:**
{One paragraph describing the specific work in flight}

**What is working correctly:**
{Bullet list of capabilities confirmed working}

**What is not working or deferred:**
{Bullet list of known issues or deferred decisions}

**The next concrete action:**
{Single, specific action — not "work on memory" but "implement the reranker.py score formula"}

**Open questions requiring a decision:**
{Any architectural or implementation questions not yet resolved}

**Current technical debt entries:**
{Reference to any new DEBT_REGISTER.md entries added since last snapshot}
```

### 18.3 The Away Protocol

**Applies when:** Any planned absence from the project exceeding 3 working days.

**Required actions before any absence > 3 days:**

1. **Commit all in-progress work** to a named feature branch. Do not leave uncommitted changes.
2. **Write a context snapshot** entry in `docs/architecture/context-log.md` with the exact format above.
3. **Verify the backup is current.** Run `backup.ps1` and confirm `verified: true` in the manifest.
4. **Push all branches** to the remote repository. Local-only branches are a data loss risk.
5. **Document any time-sensitive external state** (expiring API keys, dependency security issues encountered, anything that will change during the absence).

**This protocol is not heavy.** A context snapshot entry takes 15 minutes to write. It can save days of re-orientation. There are no exceptions for "short" absences if they exceed 3 working days.

### 18.4 The Return Protocol

**Applies when:** Returning to the project after any absence exceeding 1 week.

**Required actions before resuming code changes:**

1. **Read the most recent context snapshot** in `docs/architecture/context-log.md` before touching any file.
2. **Run the full quality suite** before making any changes:
   ```
   uv run ruff check .
   uv run mypy aether/ services/ --strict
   uv run lint-imports
   uv run pytest tests/unit/ tests/contracts/ tests/architecture/ -x
   ```
   If any gate fails, the failure must be understood and resolved before new work begins. Do not add new code on top of a failing baseline.
3. **Read the current phase spec** section for the active milestone before resuming.
4. **Write a new context snapshot** after the first day back, reflecting the current understanding of the project state.

### 18.5 Scope Management Rules

The "one more feature" trap is the most common cause of solo project abandonment. These rules govern scope:

**Rule SM-1: One milestone at a time.**  
No work begins on Milestone N+1 until Milestone N has passed all five checklists and received a GO decision. The milestone gate exists for this reason. Curiosity about the next phase is not grounds for early start.

**Rule SM-2: No opportunistic refactoring.**  
When working on a specific milestone deliverable, the scope of changes is exactly that deliverable. Code noticed that "could be improved" is added to the DEBT_REGISTER.md, not fixed in the same session. Opportunistic refactoring is the primary cause of unintended scope expansion.

**Rule SM-3: Fatigue-appropriate work.**  
Development sessions vary in cognitive quality. A high-focus session is appropriate for complex implementation work. A low-focus session is appropriate for documentation, tests for already-implemented functions, or code review. No new architectural decisions are made in low-focus states.

**Rule SM-4: Session ending state.**  
Every development session ends with the codebase in a committed, passing state. "I'll finish this tomorrow" is acceptable if the partial work is committed to a feature branch and the context log is updated. Uncommitted work at session end means context loss is one system failure away from permanent loss.

**Rule SM-5: The simplification audit.**  
At each phase completion, before the GO decision is recorded, the developer reviews the codebase for any complexity added beyond the architectural specification. Any complexity not required by the specification is removed or registered as P1 technical debt. The system must not grow beyond its specification without explicit approval.

### 18.6 Decision Fatigue Mitigation

Architectural decisions made under fatigue are the hardest to reverse. These rules apply to high-stakes decisions:

- Any decision that would require an ADR must not be made and immediately implemented. Write the ADR proposal first. Sleep before committing.
- Any new external dependency must not be added in the same session it is discovered. The evaluation process (ADR-010 Section 11) requires the cooling period.
- Any deviation from the Technical Specification — even a "minor" one — must be considered a potential ADR trigger, not an in-place decision.

---

## 19. OPERATIONAL CONTINUITY STANDARDS

### 19.1 Why This Section Exists

Aether will run as a daily-use system for years. Infrastructure services accumulate state, databases grow, log files fill, and performance drifts. Without explicit governance, these operational concerns are discovered as emergencies. This section defines the proactive maintenance obligations for a system expected to operate continuously across a multi-year development lifespan.

### 19.2 Log Management

**The log rotation configuration** (50MB max file, 5 backups) is defined in the Technical Specification. This section defines the governance for what happens when logs grow beyond expected bounds.

**Log review obligation:** Once per quarter, the developer reviews the most recent 7 days of `logs/aether.log` for:
- WARNING or ERROR entries that appeared more than 3 times (indicates a recurring issue not yet addressed)
- Any patterns suggesting silent failure (operations that should succeed but appear rarely in INFO logs)
- Budget threshold warnings (indicates cloud API spend is being approached)

**Log retention policy:** Log files beyond the rolling window (5 backups) are deleted automatically by the logging rotation configuration. No manual archiving is required. If specific log content needs to be preserved for debugging, it is copied to `docs/architecture/operations-log.md` with a dated entry.

### 19.3 Database Growth Management

**SQLite:**
- Monthly: run `VACUUM` on `data/aether.db` to reclaim space from deleted records
- Quarterly: record the database file size in the operational log
- Threshold: if `data/aether.db` exceeds 500MB, open a P2 technical debt item to evaluate memory pruning strategy
- Command: `sqlite3 data/aether.db "VACUUM; ANALYZE;"`

**Qdrant:**
- Monthly: take a manual Qdrant snapshot (in addition to automated daily backups)
- Quarterly: record the storage directory size in the operational log
- Threshold: if Qdrant storage exceeds 10GB, evaluate the memory importance decay configuration

**Redis:**
- Redis data is session-scoped and bounded by TTLs. No manual management required unless the AOF file grows abnormally.
- Threshold: if `appendonly.aof` within the container exceeds 500MB, trigger a `redis-cli BGREWRITEAOF`

### 19.4 Periodic Maintenance Schedule

This schedule augments the existing monthly architecture audit (Section 14.2) and quarterly dependency audit (Section 14.2):

| Frequency | Action | Location |
|---|---|---|
| Weekly | Verify backup is current and verified | `backup.ps1` + manifest check |
| Monthly | SQLite VACUUM + ANALYZE | `sqlite3 data/aether.db` |
| Monthly | Qdrant manual snapshot | Qdrant API |
| Monthly | Architecture audit | `docs/architecture/audits/` |
| Monthly | Context log snapshot (even if no absence) | `docs/architecture/context-log.md` |
| Quarterly | Dependency security audit | `pip-audit` + review |
| Quarterly | Log review for recurring patterns | `logs/aether.log` |
| Quarterly | Database size recording | operational log |
| Quarterly | Performance baseline comparison | `docs/performance/` |
| Annually | Full system review | Phase completion review process |

The monthly and quarterly obligations are calendar events, not aspirational goals. If a monthly obligation is missed, it is treated as a P2 process debt item and completed at the earliest available session.

### 19.5 Disk Space Governance

The developer's NVMe SSD on the primary machine has finite capacity. As Aether accumulates memories, logs, and backups over years, disk usage will grow. The following thresholds trigger specific actions:

| Component | Warning Threshold | Critical Threshold | Action |
|---|---|---|---|
| `data/aether.db` | 200MB | 500MB | Review memory pruning strategy |
| `backups/` total | 10GB | 20GB | Delete oldest verified backups beyond 90-day retention |
| `logs/` total | 500MB | 1GB | Verify log rotation is functioning; reduce backup count if needed |
| Qdrant volume | 5GB | 10GB | Review embedding dimension and quantization settings |
| Total project directory | 25GB | 50GB | Full operational review |

Thresholds are checked during the quarterly database size recording.

### 19.6 The Operational Log

**File:** `docs/architecture/operations-log.md`

Referenced in Section 9.1 (violations) and Section 3.8 (Level 5 override process). This log is also the destination for operational observations — not just incidents.

All entries in the operational log follow this format:

```markdown
## Operational Entry — {YYYY-MM-DD}

**Type:** Incident | Maintenance | Observation | Level-5-Override
**Severity (if Incident):** Critical | High | Medium | Low

**Summary:**
{One sentence describing what happened or was done.}

**Details:**
{Full description. For incidents: what failed, what was the impact,
what was the recovery. For maintenance: what was done, results observed.
For observations: what was noticed and any follow-up required.}

**Resolution/Action taken:**
{Specific commands run or decisions made.}

**Follow-up required:**
{Any open items or DEBT_REGISTER.md entries created.}
```

---

## 20. DOCUMENT FREEZE DECLARATION

### 20.1 Freeze Status

Effective from the date of this entry, ADR-010 is **FROZEN** as a component of the Aether Project Constitution.

**What freeze means:**
- This document's content may not be modified by AI code generation tools under any circumstances
- This document's content may not be modified by the developer without an explicit Constitutional Amendment (per Section 16.4)
- No generated code may contradict, override, or circumvent any rule in this document
- The document version is promoted from a working document to a Constitutional artifact

**What freeze does not mean:**
- The document cannot ever change. It can, through the amendment process.
- The document's rules are perfect. They may have gaps discovered in implementation. Those gaps are addressed through the amendment process, not through informal deviation.

### 20.2 Sealed Content

The following sections are sealed by this freeze in their current form:

| Section | Title | Seal Date |
|---|---|---|
| 1–9 | Original sections (Risk, Forbidden Ops, Backup, Recovery, Repository, CI, Consequences) | 2025-11-15 |
| 10–16 | Architectural Authority, Dependency Governance, Placeholder Policy, Technical Debt, Drift Prevention, AI Enforcement, Constitution Clause | 2025-11-15 |
| 17 | Project Versioning Policy | 2025-11-15 |
| 18 | Solo Developer Sustainability Protocol | 2025-11-15 |
| 19 | Operational Continuity Standards | 2025-11-15 |
| 20 | This Freeze Declaration | 2025-11-15 |

### 20.3 Amendment Path

To amend this document after the freeze:
1. Create an ADR in `docs/architecture/decisions/` describing the amendment
2. The ADR must follow the format in Section 16.4
3. The amendment ADR must be committed before any code deviating from the current rules is written
4. The amendment is applied to this document in a dedicated commit with message: `governance(ADR-010): amend section N per ADR-XXX`

---

*Document Version: 3.0 (Sections 1-9: v1.0, Sections 10-16: v2.0, Sections 17-20: v3.0)*
*Status: ACCEPTED — ENFORCED — FROZEN AS CONSTITUTIONAL ARTIFACT*
*Frozen Date: 2025-11-15*
*Amendment Process: ADR-010 Section 16.4*
*Owner: Principal Systems Engineer*
