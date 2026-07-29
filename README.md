# Aether AI OS
Personal AI Operating System — inspired by JARVIS.

## Repository Root
E:\Aether

## Development Status
Phase 1 — Foundation (Complete)

## Architecture
See docs/architecture/ for all governing documents.

## Quick Start
See docs/environments/windows-setup.md (created in M0).

## Development Environment

Sync the **full** development environment — base dependencies, the `dev` group,
and **every** optional extra (`voice` and `automation`) — with one canonical
command:

```
uv sync --all-extras
```

Prefer this over `uv sync --extra <one>`. `uv sync` makes the environment match
*exactly* what is requested, so `uv sync --extra automation` alone **uninstalls**
the `voice` extras (and vice versa) — nothing is additive. `--all-extras`
installs them together. This is the same "uv makes it match exactly" surprise as
DEBT-019; use the command above and it won't be rediscovered a third time.

### Standing rule — manual-validation cleanup (all process-affecting milestones)

When manually validating any milestone that starts or stops OS processes, cleanup
must track and act on the **specific PID the test itself created** — never a
name-based lookup of running processes. A name match can hit a *pre-existing*
instance the user is already running: during M2.3 a name-based Notepad close
force-terminated a Notepad the user had open, with unsaved changes. This applies
to all future manual validation, not only PC Control.

## Milestone Status
### Phase 1: Core Systems (M1)

- [x] **M1.0**: Project Scaffold & Docker Compose
- [x] **M1.1**: Vector (Qdrant) & Cache (Redis) integration
- [x] **M1.2**: Type-safe Config (pydantic) & Logging (structlog)
- [x] **M1.3**: LLM Router (LiteLLM) & Budget Manager
- [x] **M1.4**: Memory DB Schema (SQLite + SQLAlchemy + Alembic)
- [x] **M1.5**: REST API Foundation (FastAPI) / Memory System
- [x] **M1.6**: Tool System + Task Manager
- [x] **M1.7**: Agent Runtime + Conversation Agent
- [x] **M1.8**: Session Manager
- [x] **M1.9**: CLI Interface **[TEXT MILESTONE ACHIEVED]**
- [x] **M1.10**: Voice Service **[VOICE MILESTONE ACHIEVED]**
- [x] **M1.11**: Backup + Architecture Validation **[PHASE 1 COMPLETE]**
