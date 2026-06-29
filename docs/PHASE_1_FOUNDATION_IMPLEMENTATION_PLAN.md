# PHASE 1: FOUNDATION — IMPLEMENTATION PLAN
### docs/phases/PHASE_1_FOUNDATION_IMPLEMENTATION_PLAN.md
### Governing Document for Phase 1 Development Execution

---

**Date:** 2025-11-15
**Status:** APPROVED FOR EXECUTION
**Phase:** 1 of 10 — Foundation
**Classification:** Implementation Governance
**Authority:** Principal Systems Engineer
**Hardware Target:** Intel i7-13700HX · RTX 4050 6GB · 16GB DDR5 · Windows 11
**Estimated Duration:** 47 working days (~10 weeks)

---

## THE PHASE-GATE RULE

**No milestone may begin until the preceding milestone has passed every checklist
and received an explicit GO decision. "Close enough" is not GO. "Will fix later"
is not GO. Partial compliance is not GO.**

A NO-GO decision means:
1. Development stops on the failing milestone
2. All failing checklist items are identified and logged
3. Defects are corrected
4. All five checklists are re-run from the beginning
5. Only after full checklist re-run passes does the GO decision become available

This rule exists because Phase 1 is the foundation. Every subsequent phase builds
directly on Phase 1's correctness. A flaw in Phase 1 that passes a lenient gate
propagates into every phase that follows.

---

## PHASE 1 OBJECTIVES

Phase 1 produces a working AI assistant with these specific, measurable capabilities:

**Objective 1 — Persistent Memory**
Tell Aether your name in Session 1. End Session 1. Start Session 2. Ask Aether
your name. Aether recalls it from long-term memory without being told again.

**Objective 2 — Voice Interaction**
Wake Aether by saying "Aether." Speak a request. Receive a spoken response.
The end-to-end latency from wake word confirmation to first audio output
is under 3 seconds on the target hardware.

**Objective 3 — Task Management**
Create, track, and complete tasks via both voice and text. Tasks persist
across sessions. Active tasks appear in the morning briefing.

**Objective 4 — Architectural Integrity**
Zero import boundary violations. All five checklists pass for all twelve
milestones. No Zero-Tolerance violations anywhere in the codebase.

---

## MILESTONE MAP AND DEPENDENCIES

```
Day 0     M0: Environment Validation
             ↓ GATE
Days 1-2  M1.0: Repository Foundation
             ↓ GATE
Days 3-4  M1.1: Docker Infrastructure ─────────────┐
             ↓ GATE                                 │
Days 5-7  M1.2: Config + Logging + Events           │
             ↓ GATE                                 │
Days 8-10 M1.3: LLM Router + Budget                 │
             ↓ GATE                                 │
Day 11    M1.4: SQLite Schema ◄──────────────────────┘
             ↓ GATE (requires M1.1 + M1.3)
Days 12-16 M1.5: Memory System
             ↓ GATE
Days 17-19 M1.6: Tool System + Task Manager
             ↓ GATE
Days 20-24 M1.7: Agent Runtime + Conversation Agent
             ↓ GATE
Days 25-27 M1.8: Session Manager + Morning Briefing
             ↓ GATE
Days 28-30 M1.9: CLI Interface                [TEXT MILESTONE]
             ↓ GATE
Days 31-40 M1.10: Voice Service               [VOICE MILESTONE]
             ↓ GATE
Days 41-43 M1.11: Backup + Architecture Validation
             ↓ PHASE 1 GO/NO-GO DECISION

Note: M1.1 (Docker) runs in parallel with M1.2 (Config) since Docker services
are needed for M1.4 but not for M1.2-M1.3. The critical path is:
M0 → M1.0 → M1.2 → M1.3 → M1.4 → M1.5 → M1.6 → M1.7 → M1.8 → M1.9 →
M1.10 → M1.11 → Phase Gate
```

---

## STANDARD CHECKLIST COMMANDS

The following commands are referenced throughout this document.
All commands run from the repository root unless specified otherwise.

```powershell
# Quality gates (must all pass for every milestone)
uv run ruff check .                           # Style and lint
uv run ruff format --check .                  # Format compliance
uv run mypy aether/ services/ --strict        # Type safety
uv run lint-imports                           # Architecture boundaries

# Test commands
uv run pytest tests/unit/ -v --tb=short       # Unit tests
uv run pytest tests/integration/ -v --tb=short # Integration tests
uv run pytest tests/contracts/ -v --tb=short  # Contract tests
uv run pytest tests/architecture/ -v --tb=short # Architecture tests

# Infrastructure checks
docker compose ps                             # Service status
docker compose exec redis redis-cli ping      # Redis health
curl http://localhost:6333/health             # Qdrant health
curl http://localhost:8000/health             # Core API health
curl http://localhost:8001/health             # Voice API health

# Security scan
grep -r "DROP TABLE\|TRUNCATE\|rm -rf\|flushall\|drop_all\|anthropic\|openai" aether/ services/ migrations/ --include="*.py"
```

---

## MILESTONE M0: ENVIRONMENT VALIDATION

### Overview

This milestone is not optional and is not skippable. Every tool and library
that Phase 1 depends on must be validated as working on the developer's specific
Windows 11 machine before a single line of application code is written. Audio
in particular is known to fail on Windows in non-obvious ways. Discovering this
in Week 6 instead of Day 0 costs weeks.

### Prerequisites
None. This is the starting point.

### Duration
1 working day

### Files Created This Milestone
```
docs/environments/
  windows-validation-log.md     # Evidence of passing all checks, dated
scripts/
  validate_environment.ps1      # Reusable validation script
```

### Implementation Sequence

**Block 1: Python and Package Management (Morning)**

```
1. Verify Python version: python --version
   Expected: Python 3.12.x (must NOT be from Microsoft Store)
   If Store version: uninstall, install from python.org

2. Install uv: winget install astral-sh.uv
   Verify: uv --version → uv 0.x.x

3. Install Git: winget install Git.Git (if not present)
   Verify: git --version

4. Install Microsoft C++ Build Tools
   Source: visualstudio.microsoft.com/visual-cpp-build-tools/
   Select: "Desktop development with C++"
   This is required by faster-whisper, sounddevice, and several ML packages.
   Verify by running: python -c "import ctypes; print('OK')"
```

**Block 2: GPU and CUDA Validation (Morning)**

```
5. Verify NVIDIA driver: nvidia-smi
   Expected: Driver version 550+, RTX 4050 listed, ~6GB VRAM shown

6. Install CUDA Toolkit 12.x
   Source: developer.nvidia.com/cuda-downloads
   Select: Windows, x86_64, 11, exe (local)
   Verify: nvcc --version → Cuda compilation tools, release 12.x
   Verify: python -c "import torch; print(torch.cuda.is_available())"
   Expected output: True
```

**Block 3: Docker Validation (Afternoon)**

```
7. Install Docker Desktop with WSL2 backend
   Enable WSL2 integration in Docker Desktop settings
   Verify: docker --version
   Verify: docker compose version
   Verify: docker run hello-world → "Hello from Docker!"
```

**Block 4: Audio Hardware Validation (Afternoon)**

This is the highest-risk block. Complete it before any voice-related library
installation. Knowing the audio stack works removes the largest source of
Week 6 surprises.

```
8. Create test_audio.py:
   import sounddevice as sd
   import numpy as np
   print("Recording 2 seconds...")
   recording = sd.rec(int(2 * 16000), samplerate=16000, channels=1)
   sd.wait()
   print("Playing back...")
   sd.play(recording, 16000)
   sd.wait()
   print("Audio test passed")

   Run: python test_audio.py
   If sounddevice fails: pip install sounddevice
   If sounddevice still fails: try PyAudio as alternative, document the result

9. Verify microphone is active in Windows Sound Settings
10. Verify speaker/headphones are active in Windows Sound Settings
```

**Block 5: AI Package Validation (Afternoon)**

```
11. Test faster-whisper installation:
    pip install faster-whisper
    python -c "from faster_whisper import WhisperModel; print('faster-whisper: OK')"
    If failure: verify C++ Build Tools are installed (Block 1, Step 4)

12. Test sentence-transformers:
    pip install sentence-transformers
    python -c "from sentence_transformers import SentenceTransformer; m = SentenceTransformer('all-MiniLM-L6-v2'); print('sentence-transformers: OK')"

13. Test qdrant-client:
    pip install qdrant-client
    python -c "from qdrant_client import QdrantClient; print('qdrant-client: OK')"

14. Test litellm:
    pip install litellm
    python -c "import litellm; print('litellm: OK')"
```

**Block 6: Ollama Validation (End of Day)**

```
15. Install Ollama: https://ollama.ai/download (Windows installer)
16. Start Ollama service: ollama serve (in a separate terminal)
17. Download phi4-mini: ollama pull phi4-mini
    Expected: Model downloads to local storage (~2-3GB)
18. Test inference: ollama run phi4-mini "Say the word hello"
    Expected: Model responds with "hello" or equivalent
19. Verify VRAM usage during inference:
    While ollama runs, check: nvidia-smi
    Expected: GPU memory usage increases (~2GB for phi4-mini Q4)

20. Verify API keys available (test connectivity only, not record in file):
    ANTHROPIC_API_KEY: test with one claude-haiku-4-5-20251001 call
    GOOGLE_API_KEY: test with one gemini-flash call
    PORCUPINE_ACCESS_KEY: verify obtained from console.picovoice.ai
```

### BUILD CHECKLIST — M0

```
Environment Build Verification:
  [ ] Python 3.12.x installed from python.org (verified: python --version)
  [ ] uv installed (verified: uv --version)
  [ ] Git installed and configured (verified: git --version)
  [ ] Microsoft C++ Build Tools installed (verified: python -c "import ctypes")
  [ ] CUDA Toolkit 12.x installed (verified: nvcc --version)
  [ ] nvidia-smi shows RTX 4050 with 6GB VRAM
  [ ] Docker Desktop installed with WSL2 backend (verified: docker run hello-world)
  [ ] docker compose version shows 2.x
  [ ] sounddevice audio test passes (record → playback)
  [ ] faster-whisper imports without error
  [ ] sentence-transformers imports without error
  [ ] qdrant-client imports without error
  [ ] litellm imports without error
  [ ] Ollama installed and running (verified: ollama serve active)
  [ ] phi4-mini model downloaded (verified: ollama list)
  [ ] Ollama inference test passes (model responds to prompt)
  [ ] API key for Claude verified working
  [ ] API key for Gemini verified working
  [ ] Porcupine access key obtained
```

### TEST CHECKLIST — M0

```
  [ ] python test_audio.py → Records and plays back 2 seconds of audio without error
  [ ] python -c "import torch; print(torch.cuda.is_available())" → True
  [ ] nvidia-smi during Ollama inference shows increased GPU memory usage
  [ ] docker run hello-world → exits with code 0
```

### VALIDATION CHECKLIST — M0

```
  [ ] All BUILD checklist items checked
  [ ] All TEST checklist items checked
  [ ] windows-validation-log.md created with: date, results of each check, any issues resolved
  [ ] Any library that failed its initial install has a documented resolution
  [ ] Audio hardware confirmed working on target microphone and speaker
```

### ARCHITECTURE COMPLIANCE CHECKLIST — M0

```
  [ ] Not applicable — no architecture code created yet
```

### SECURITY CHECKLIST — M0

```
  [ ] No API keys stored in any file that will be committed
  [ ] No API key values appear in windows-validation-log.md
  [ ] validate_environment.ps1 script does not hardcode any credentials
```

### DEFINITION OF DONE — M0

Every item in the BUILD and TEST checklists passes. windows-validation-log.md
is committed with dated evidence. The developer can run Ollama and get a
response without internet connectivity (verifying local model availability).

### MILESTONE GATE — M0

```
GO:   All 20 BUILD checklist items checked. Audio test passes. CUDA confirmed.
      windows-validation-log.md committed.

NO-GO: Any BUILD item fails. Any TEST item fails.
       If audio fails: document the specific error and alternative (PyAudio).
       If CUDA fails: document GPU availability; system may run on CPU only
       (slower voice, acceptable for Phase 1 with documented limitation).
       Either way: NO-GO until the specific failure is resolved or formally
       accepted with a documented impact statement.
```

---

## MILESTONE M1.0: REPOSITORY FOUNDATION

### Overview

Creates the complete repository structure, tooling configuration, and CI pipeline.
After this milestone, every subsequent milestone has a consistent place to put its
files, consistent tooling to validate quality, and automated gates that enforce
architecture rules from the first commit.

### Prerequisites
M0 passed. All environment tools verified.

### Duration
2 working days

### Files Created This Milestone

```
aether-os/
├── .github/
│   └── workflows/
│       ├── ci.yml
│       └── architecture-check.yml
├── docs/
│   └── architecture/
│       ├── decisions/               (directory only, ADRs copied in)
│       ├── ARCHITECTURE_RULES.md    (copy from governance documents)
│       └── AI_GENERATION_RULES_V2.md (copy from governance documents)
├── aether/
│   ├── __init__.py
│   ├── py.typed
│   ├── core/__init__.py
│   ├── llm/__init__.py
│   ├── llm/_providers/__init__.py
│   ├── memory/__init__.py
│   ├── memory/_stores/__init__.py
│   ├── memory/_retrieval/__init__.py
│   ├── memory/_consolidation/__init__.py
│   ├── tools/__init__.py
│   ├── tools/_implementations/__init__.py
│   ├── agents/__init__.py
│   ├── agents/_implementations/__init__.py
│   ├── tasks/__init__.py
│   ├── session/__init__.py
│   └── interfaces/__init__.py
├── services/
│   ├── __init__.py
│   └── voice/__init__.py
├── tests/
│   ├── conftest.py
│   ├── unit/.gitkeep
│   ├── integration/.gitkeep
│   ├── architecture/.gitkeep
│   └── contracts/.gitkeep
├── config/
│   └── default.yaml
├── .aether/
│   └── permissions.yaml
├── data/.gitkeep
├── logs/.gitkeep
├── backups/.gitkeep
├── pyproject.toml
├── .env.example
├── .gitignore
├── .pre-commit-config.yaml
└── README.md
```

### Implementation Sequence

**Day 1: Core Repository Structure**

```
Step 1: Initialize git repository
  git init aether-os
  cd aether-os
  git branch -M main

Step 2: Create pyproject.toml
  Define: project metadata, all dependencies from Technical Spec Appendix A,
  all dev dependencies, ruff configuration, mypy configuration,
  pytest configuration, import-linter configuration with all boundary contracts.

  CRITICAL: All import-linter contracts from Technical Specification Section 10
  must be in pyproject.toml before any code is written. This ensures
  every module created after this point is checked from its first commit.

Step 3: Create directory structure
  Create all directories listed in "Files Created This Milestone" above.
  Create all __init__.py stubs (empty files with only the module docstring).
  Create py.typed marker file.

Step 4: Create configuration files
  .gitignore: include data/, logs/, backups/, .env, config/local.yaml,
              __pycache__/, .pytest_cache/, .mypy_cache/, *.pyc, dist/
  .env.example: document all required environment variables with descriptions
  config/default.yaml: complete configuration with all sections from
                       Technical Specification Section 2.1
  .aether/permissions.yaml: initial permissions from Technical Specification
                             Section 14.1

Step 5: Install dependencies
  uv sync
  Verify: uv run python -c "import pydantic; print('dependencies OK')"
```

**Day 2: Tooling and CI Configuration**

```
Step 6: Configure pre-commit
  .pre-commit-config.yaml: hooks for ruff (check + format), mypy, import-linter,
                            forbidden pattern scan (grep for DROP TABLE, rm -rf etc.)
  Install hooks: uv run pre-commit install
  Verify: uv run pre-commit run --all-files (empty project must pass)

Step 7: Create CI workflows
  .github/workflows/ci.yml:
    - triggers: push to any branch, PR to main and develop
    - jobs: lint (ruff), format (ruff), type-check (mypy), architecture (lint-imports),
            forbidden-scan (grep), unit-tests (pytest tests/unit/),
            contract-tests (pytest tests/contracts/)
  .github/workflows/architecture-check.yml:
    - dedicated architecture boundary verification job
    - runs on every push, blocks PR merge on failure

Step 8: Create conftest.py
  tests/conftest.py: shared fixtures only — no implementations yet.
  Define fixture signatures for: test_db, mock_llm_router, test_redis,
  test_qdrant, mock_embedding_service. All raise NotImplementedError.
  These will be implemented in later milestones.

Step 9: Populate README.md
  Must include:
  - Project overview (one paragraph)
  - Windows 11 setup instructions (step by step, referencing M0)
  - Quick start commands
  - Milestone status table
  - Link to all governance documents

Step 10: Initial commit
  git add .
  git commit -m "feat(foundation): initialize repository structure and tooling"
  Push to GitHub and verify CI pipeline starts.
```

### BUILD CHECKLIST — M1.0

```
Repository Structure:
  [ ] All directories from file list exist
  [ ] All module __init__.py stubs exist
  [ ] py.typed marker file exists
  [ ] All governance documents copied to docs/architecture/

Configuration:
  [ ] pyproject.toml: all dependencies listed (verify against Technical Spec Appendix A)
  [ ] pyproject.toml: ruff configured with target-version = "py312"
  [ ] pyproject.toml: mypy configured with strict = true
  [ ] pyproject.toml: all import-linter contracts present
  [ ] pyproject.toml: pytest configured with asyncio_mode = "auto"
  [ ] config/default.yaml: all sections present (llm, memory, voice, tasks, tools,
      logging, redis, qdrant, database, permissions, budget)
  [ ] .env.example: all required keys documented
  [ ] .gitignore: data/, logs/, backups/, .env, config/local.yaml all excluded
  [ ] .aether/permissions.yaml: initial permissions defined

Pre-commit:
  [ ] uv run pre-commit install → "installed"
  [ ] uv run pre-commit run --all-files → passes on empty project

CI Pipeline:
  [ ] ci.yml contains all six jobs
  [ ] Pipeline triggered on first push
  [ ] All CI jobs show green on GitHub
```

### TEST CHECKLIST — M1.0

```
  [ ] uv sync → exits 0, no errors
  [ ] uv run ruff check . → exits 0
  [ ] uv run ruff format --check . → exits 0
  [ ] uv run mypy aether/ services/ --strict → exits 0 (empty modules)
  [ ] uv run lint-imports → exits 0 (no contracts to violate yet)
  [ ] uv run pytest tests/ → exits 0 (no tests yet, empty run)
  [ ] GitHub Actions CI → all jobs green on initial push
```

### VALIDATION CHECKLIST — M1.0

```
  [ ] Every file in the "Files Created" list exists and is committed
  [ ] No files exist that are not in the "Files Created" list
  [ ] uv run pre-commit run --all-files passes cleanly
  [ ] GitHub repository shows green CI status
  [ ] README.md is readable and accurate
  [ ] All governance documents are in docs/architecture/
```

### ARCHITECTURE COMPLIANCE CHECKLIST — M1.0

```
  [ ] All import-linter boundary contracts present in pyproject.toml
      Verify: grep "importlinter" pyproject.toml → shows all contracts
  [ ] No cross-boundary imports exist in any stub file
  [ ] Module __init__.py files export nothing (stubs only)
  [ ] No application logic in __init__.py stubs
```

### SECURITY CHECKLIST — M1.0

```
  [ ] .gitignore includes: .env, config/local.yaml, data/, logs/, backups/
  [ ] .env.example contains no real values — only placeholder text
  [ ] No API keys in any committed file
  [ ] Forbidden pattern scan passes: grep finds no DROP TABLE, rm -rf, etc.
  [ ] config/default.yaml contains no secrets or real credentials
```

### DEFINITION OF DONE — M1.0

All five checklists pass. GitHub CI is green. The repository structure matches
the Technical Specification Section 1.1 exactly. A new developer (or AI session)
could clone the repository, read the README, and understand where every file
in the project belongs.

### MILESTONE GATE — M1.0

```
GO:   All checklist items pass. GitHub CI green. uv sync succeeds.
      All pre-commit hooks pass.

NO-GO: Any CI job fails. Any missing file from the list. Any import-linter
       contract missing from pyproject.toml. .env or secrets appear in any
       committed file.
```

---

## MILESTONE M1.1: DOCKER INFRASTRUCTURE

### Overview

Creates the infrastructure services (Redis + Qdrant) that all subsequent
milestones depend on. These services run in Docker. The application code
runs on native Windows Python — not in Docker — to avoid audio hardware
and GPU access complications.

### Prerequisites
M1.0 passed.

### Duration
2 working days

### Files Created This Milestone

```
infrastructure/
├── docker/
│   ├── docker-compose.yml
│   ├── redis/
│   │   └── redis.conf
│   └── qdrant/
│       └── config.yaml
└── scripts/
    ├── start.ps1        (Phase 1 version — starts infrastructure only)
    ├── stop.ps1
    └── health_check.ps1
```

### Implementation Sequence

**Day 1: Docker Services**

```
Step 1: Create infrastructure/docker/redis/redis.conf
  Must include:
  - appendonly yes
  - appendfsync everysec
  - maxmemory 512mb
  - maxmemory-policy allkeys-lru
  - bind 127.0.0.1 (local only — never expose)
  - protected-mode yes

Step 2: Create infrastructure/docker/qdrant/config.yaml
  Must include:
  - service.telemetry_disabled: true
  - CORS configuration for localhost
  - Storage path configuration pointing to named volume

Step 3: Create infrastructure/docker/docker-compose.yml
  Services:
  - redis:
      image: redis:7-alpine
      ports: 6379:6379 (bound to 127.0.0.1 only)
      volumes: redis_data:/data, ./redis/redis.conf:/etc/redis/redis.conf
      command: redis-server /etc/redis/redis.conf
      healthcheck: redis-cli ping → PONG
      restart: unless-stopped

  - qdrant:
      image: qdrant/qdrant:latest
      ports: 6333:6333, 6334:6334 (bound to 127.0.0.1)
      volumes: qdrant_data:/qdrant/storage, ./qdrant/config.yaml:/qdrant/config/production.yaml
      healthcheck: curl -f http://localhost:6333/health
      restart: unless-stopped

  volumes:
      redis_data: (named volume — NOT mounted from host to prevent data loss on docker compose down)
      qdrant_data: (named volume)

  CRITICAL: Do NOT use docker compose down -v in scripts — this destroys volumes.
  Use only: docker compose down (stops containers, preserves volumes)
```

**Day 2: Operational Scripts**

```
Step 4: Create infrastructure/scripts/start.ps1
  Sequence:
  1. Check Docker Desktop is running (docker info)
  2. If not running: print error, exit 1
  3. Navigate to infrastructure/docker/
  4. docker compose up -d
  5. Wait for Redis health: poll until redis-cli ping returns PONG (max 30s)
  6. Wait for Qdrant health: poll until /health returns 200 (max 30s)
  7. Print success with service URLs
  8. Print VRAM status: nvidia-smi --query-gpu=memory.used --format=csv,noheader

Step 5: Create infrastructure/scripts/stop.ps1
  Sequence:
  1. Navigate to infrastructure/docker/
  2. docker compose down (NO --volumes flag — preserving data is mandatory)
  3. Print "Services stopped. Data preserved."
  Note: If developer accidentally adds -v or --volumes, the data is lost.
  The script must never include these flags.

Step 6: Create infrastructure/scripts/health_check.ps1
  Checks:
  - Docker Desktop running
  - Redis: docker compose exec redis redis-cli ping → PONG
  - Qdrant: curl http://localhost:6333/health → {"status":"ok"}
  - Print summary: all healthy / which services are degraded
```

### BUILD CHECKLIST — M1.1

```
Docker Services:
  [ ] docker-compose.yml: Redis 7 service defined with healthcheck
  [ ] docker-compose.yml: Qdrant service defined with healthcheck
  [ ] docker-compose.yml: Named volumes defined (redis_data, qdrant_data)
  [ ] docker-compose.yml: No -v flag anywhere in any script or compose file
  [ ] redis.conf: appendonly yes
  [ ] redis.conf: bind 127.0.0.1 (local only)
  [ ] redis.conf: maxmemory 512mb
  [ ] qdrant/config.yaml: telemetry_disabled: true

Scripts:
  [ ] start.ps1: polls health checks, does not just sleep
  [ ] start.ps1: prints VRAM status after start
  [ ] stop.ps1: uses docker compose down (no --volumes)
  [ ] health_check.ps1: checks both services individually
  [ ] All scripts have error handling (if Docker not running → clear error message)
```

### TEST CHECKLIST — M1.1

```
  [ ] .\infrastructure\scripts\start.ps1 → exits 0, both services healthy
  [ ] docker compose ps → both services show "healthy" (not just "running")
  [ ] docker compose exec redis redis-cli ping → PONG
  [ ] curl http://localhost:6333/health → {"status":"ok"}
  [ ] .\infrastructure\scripts\health_check.ps1 → all healthy
  [ ] .\infrastructure\scripts\stop.ps1 → exits 0
  [ ] After stop: docker compose ps → no running containers
  [ ] After stop + start: redis data persists (SET test → STOP → START → GET test)
  [ ] After stop + start: qdrant data persists (collection count consistent)
  [ ] Verify named volumes exist: docker volume ls | grep aether
```

### VALIDATION CHECKLIST — M1.1

```
  [ ] Redis AOF file exists inside container: docker compose exec redis ls /data/appendonly.aof
  [ ] Qdrant storage volume is not empty after creating test collection
  [ ] stop.ps1 → start.ps1 → health_check.ps1 cycle passes cleanly three times in a row
  [ ] nvidia-smi shows no GPU memory consumed by Docker services (they run on CPU)
```

### ARCHITECTURE COMPLIANCE CHECKLIST — M1.1

```
  [ ] No application Python code in infrastructure/ directory
  [ ] No business logic in scripts (scripts orchestrate, not compute)
  [ ] Docker services are infrastructure only (Redis, Qdrant) — no application services
  [ ] uv run lint-imports → still passes (no new Python code added)
```

### SECURITY CHECKLIST — M1.1

```
  [ ] Redis bound to 127.0.0.1 only (verify: redis.conf contains "bind 127.0.0.1")
  [ ] Qdrant ports not exposed to 0.0.0.0 (verify: docker-compose.yml port binding)
  [ ] No passwords or secrets in docker-compose.yml
  [ ] No volumes mounted to host filesystem for data (named volumes only)
  [ ] docker-compose.yml committed — contains no secrets
  [ ] Qdrant telemetry disabled
```

### DEFINITION OF DONE — M1.1

Start, stop, and health check scripts all execute without error. Both services
start healthy, survive a stop/start cycle with data intact, and are accessible
only from localhost. VRAM is unaffected by infrastructure services.

### MILESTONE GATE — M1.1

```
GO:   Both services start healthy. Data persists across stop/start.
      All services bound to localhost only. health_check.ps1 passes.

NO-GO: Either service fails health check. Data does not persist.
       Services accessible on 0.0.0.0. Any -v flag in scripts.
```

---

## MILESTONE M1.2: CONFIGURATION + LOGGING + EVENTS

### Overview

Creates the three lowest-level infrastructure modules that everything else
depends on. Configuration, logging, and the event bus are read by every
subsequent module. Getting them wrong propagates errors throughout the
entire system.

### Prerequisites
M1.0 passed. M1.1 may run in parallel with this milestone.

### Duration
3 working days

### Files Created This Milestone

```
aether/core/
├── __init__.py          (updated: exports AetherConfig, get_config, EventBus, get_logger)
├── config.py            (NEW)
├── logging.py           (NEW)
└── events.py            (NEW)
tests/unit/
├── test_config.py       (NEW)
├── test_logging.py      (NEW)
└── test_events.py       (NEW)
```

### Implementation Sequence

**Day 1: Configuration System**

```
Step 1: Implement aether/core/config.py
  - Full AetherConfig class using pydantic-settings
  - All nested config models from Technical Spec Section 2.1
  - Load order: default.yaml → local.yaml → environment variables
  - Validation: missing required env vars raise ConfigurationError with the
    exact variable name and where to set it
  - get_config() function: returns singleton, initialized once per process
  - No side effects at import time (lazy initialization)

Step 2: Create tests/unit/test_config.py
  Required test cases:
  - test_config_loads_from_default_yaml: config loads, version field present
  - test_env_var_overrides_yaml: AETHER_LLM__TIERS__LOCAL overrides default
  - test_missing_required_var_raises_error: clear error message with var name
  - test_config_singleton: get_config() twice returns same object
  - test_all_sections_present: llm, memory, voice, tasks, budget all accessible
  - test_budget_defaults: daily_limit=2.00, monthly_limit=30.00
```

**Day 2: Logging and Events**

```
Step 3: Implement aether/core/logging.py
  - structlog configured with JSON processor
  - Rolling file handler: logs/aether.log (50MB max, 5 backups)
  - Colored console output (development), JSON-only (production)
  - Context vars: session_id, agent_name, request_id (bound per context)
  - get_logger(__name__) as the standard usage pattern
  - Configuration respects config.logging.level

Step 4: Implement aether/core/events.py
  - EventBus class backed by Redis Streams
  - emit(event_type, payload, session_id, correlation_id) → event_id
  - subscribe(event_types, consumer_group, handler, batch_size) → None
  - AetherEvent model (LOCKED schema from Technical Spec Section 2.3)
  - All events use UUIDv7 for event_id
  - All events use UTC ISO 8601 timestamps
  - Connection uses config.redis settings (never hardcoded)

Step 5: Create tests/unit/test_logging.py and test_events.py
  test_logging.py:
  - test_logger_produces_json_output
  - test_logger_includes_module_name
  - test_context_vars_appear_in_log_output
  - test_log_levels_respected

  test_events.py (uses mocked Redis):
  - test_emit_returns_event_id
  - test_emitted_event_has_required_fields
  - test_event_id_is_uuidv7
  - test_timestamp_is_utc
  - test_subscribe_handler_receives_matching_events
  - test_subscribe_ignores_non_matching_events
```

**Day 3: Integration and Validation**

```
Step 6: Integration test for config + events
  tests/integration/test_config_events_integration.py:
  - test_events_use_config_redis_url: EventBus reads URL from config, not hardcode
  - test_emit_and_receive_roundtrip: emit to real Redis, receive in handler

Step 7: Update aether/core/__init__.py
  Export: AetherConfig, get_config, EventBus, get_logger
  Verify lint-imports still passes

Step 8: Run full quality suite
  All commands from Standard Checklist Commands must pass.
```

### BUILD CHECKLIST — M1.2

```
config.py:
  [ ] pydantic-settings BaseSettings used (not plain Pydantic)
  [ ] All config sections from Technical Spec Section 2.1 implemented
  [ ] Env var prefix: AETHER_ with nested delimiter __
  [ ] YAML files loaded: default.yaml then local.yaml
  [ ] get_config() returns singleton
  [ ] ConfigurationError raised with specific var name when required var missing
  [ ] No defaults for API keys (keys have no default, absence = error)

logging.py:
  [ ] structlog configured with JSON processor
  [ ] Rolling file handler in logs/ directory
  [ ] Log level from config.logging.level
  [ ] get_logger(__name__) is the pattern
  [ ] No print() calls in logging.py itself

events.py:
  [ ] EventBus connects to Redis using config.redis settings
  [ ] AetherEvent model matches Technical Spec Section 2.3 exactly
  [ ] event_id uses UUIDv7
  [ ] timestamp_utc is ISO 8601 UTC
  [ ] emit() returns event_id string
  [ ] subscribe() uses Redis XREADGROUP consumer groups
  [ ] No hardcoded Redis connection strings
```

### TEST CHECKLIST — M1.2

```
  [ ] uv run pytest tests/unit/test_config.py -v → all pass
  [ ] uv run pytest tests/unit/test_logging.py -v → all pass
  [ ] uv run pytest tests/unit/test_events.py -v → all pass (mocked Redis)
  [ ] uv run pytest tests/integration/test_config_events_integration.py -v → all pass (real Redis)
  [ ] python -c "from aether.core import get_config; c = get_config(); print(c.version)"
      → prints version string without error
  [ ] python -c "from aether.core import get_logger; log = get_logger('test'); log.info('ok')"
      → JSON log line appears in terminal
```

### VALIDATION CHECKLIST — M1.2

```
  [ ] Config loads without error using only default.yaml (no local.yaml, no env vars)
  [ ] Setting AETHER_LLM__TIERS__LOCAL=ollama/test overrides the default tier
  [ ] Unsetting a required API key env var produces a clear error message (not a Python traceback)
  [ ] Log file created in logs/ after first logger.info() call
  [ ] Event emitted to real Redis appears in XRANGE aether:events - + COUNT 1
  [ ] Consumer group receives emitted event in integration test
```

### ARCHITECTURE COMPLIANCE CHECKLIST — M1.2

```
  [ ] aether/core/__init__.py exports only: AetherConfig, get_config, EventBus, get_logger
  [ ] No business logic in core/ (config, logging, events are infrastructure only)
  [ ] Events.py: AetherEvent model matches LOCKED schema — no deviations
  [ ] uv run lint-imports → exits 0
  [ ] No imports of redis, sqlalchemy, qdrant_client in tests/unit/ (use mocks)
```

### SECURITY CHECKLIST — M1.2

```
  [ ] config.py: API key fields have no default value (absence = explicit error)
  [ ] logging.py: no log formatter logs field values without truncation
  [ ] events.py: no credentials passed in event payloads in any test
  [ ] Redis connection string never logged (only host:port, never password)
  [ ] Security scan passes: grep finds no hardcoded secrets
```

### DEFINITION OF DONE — M1.2

All 16 unit and integration tests pass. Config loads cleanly with safe defaults.
Logger produces JSON output to file and console. Events emit to real Redis Streams
and are received by subscribers. All five checklists pass.

### MILESTONE GATE — M1.2

```
GO:   All tests pass. All checklist items pass. AetherEvent schema matches
      locked specification exactly. No hardcoded connection strings.

NO-GO: Any test fails. AetherEvent schema deviates from spec. Redis connection
       string hardcoded anywhere. API keys have default values.
```

---

## MILESTONE M1.3: LLM ROUTER + BUDGET

### Overview

The LLM Router is the most architecturally critical module in the system.
Every agent, every memory operation, every tool depends on this abstraction.
Getting the model-agnostic interface wrong now means fixing it everywhere later.
The budget system must be working from day one — a runaway agent without budget
controls is a financial liability.

### Prerequisites
M1.2 passed. M1.1 must be running (Redis needed for budget tracking).

### Duration
3 working days

### Files Created This Milestone

```
aether/llm/
├── __init__.py          (updated: exports LLMRouter, ModelTier, LLMResponse, Embedding, BudgetStatus)
├── router.py            (NEW)
├── budget.py            (NEW)
├── _embedding.py        (NEW)
├── _models.py           (NEW)
└── _providers/
    ├── __init__.py      (updated)
    ├── base.py          (NEW)
    ├── anthropic_provider.py  (NEW)
    ├── google_provider.py     (NEW)
    └── ollama_provider.py     (NEW)
tests/unit/
├── test_llm_router.py   (NEW)
└── test_llm_budget.py   (NEW)
tests/contracts/
└── test_llm_router_contract.py  (NEW)
```

### Implementation Sequence

**Day 1: Provider Layer and Models**

```
Step 1: Implement aether/llm/_models.py
  - ModelTier enum (LOCAL, CHEAP, STANDARD, PREMIUM) — LOCKED
  - Message model (role, content, tool_call_id, name)
  - LLMResponse model — LOCKED (all fields from Technical Spec Section 2.4)
  - Embedding model — LOCKED (vector: List[float], length always 1024)
  - BudgetStatus model — LOCKED
  All models: frozen=True, strict=True

Step 2: Implement aether/llm/_providers/base.py
  - BaseProvider abstract class
  - complete(messages, config) → LLMResponse (abstract)
  - stream(messages, config) → AsyncIterator[str] (abstract)
  - Provider must never be called directly by any code outside llm/

Step 3: Implement provider adapters
  _providers/ollama_provider.py:
    - Calls Ollama REST API (localhost:11434)
    - Maps LiteLLM ollama/ prefix to local Ollama
    - Connection failure → clear error, not silent fallback
    - Model name from config.llm.tiers.local (never hardcoded)

  _providers/anthropic_provider.py:
    - Wraps LiteLLM anthropic provider
    - API key from config (never hardcoded)
    - Respects request_timeout_seconds from config

  _providers/google_provider.py:
    - Wraps LiteLLM google provider
    - API key from config (never hardcoded)
```

**Day 2: Router, Budget, and Embedding**

```
Step 4: Implement aether/llm/budget.py
  - Reads daily/monthly limits from config.budget
  - Tracks spend in Redis (keys: aether:llm:budget:daily, aether:llm:budget:monthly)
  - check_and_record(cost_usd, tier_requested) → ModelTier (returns override tier if budget exceeded)
  - When daily_limit reached: force LOCAL tier, emit system.budget.threshold_reached event
  - When 80% of limit: emit system.budget.threshold_reached with warning level
  - Hard reset at midnight UTC (Redis TTL set to end-of-day)
  - Budget state survives process restart (stored in Redis, not memory)

Step 5: Implement aether/llm/_embedding.py
  - Uses sentence-transformers BAAI/bge-large-en-v1.5
  - Device from config.memory.embedding_device (cpu or cuda)
  - ALWAYS produces vectors of exactly config.memory.embedding_dimension (1024)
  - Batch embedding support
  - Model loaded once at module initialization, not per call
  - Validate dimension on every output: assert len(vector) == EMBEDDING_DIMENSION

Step 6: Implement aether/llm/router.py
  - Accepts ModelTier, resolves to actual model via config
  - Routes through budget.check_and_record() before every call
  - Emits llm.call.completed event after every call
  - Retry logic: max_retries from config, exponential backoff
  - Fallback: if STANDARD fails, try CHEAP; if CHEAP fails, try LOCAL
  - Never exposes provider SDK to callers — returns LLMResponse only
  - All methods async
```

**Day 3: Tests and Contracts**

```
Step 7: Implement tests/unit/test_llm_router.py
  Required tests:
  - test_local_tier_routes_to_ollama_model
  - test_cheap_tier_routes_to_gemini_flash
  - test_standard_tier_routes_to_claude_sonnet
  - test_premium_tier_routes_to_claude_opus
  - test_budget_exceeded_forces_local_tier
  - test_budget_at_80_percent_emits_warning_event
  - test_retry_on_transient_failure
  - test_embed_returns_1024_dimension_vector
  - test_embed_returns_float_list
  - test_structured_output_returns_pydantic_model
  - test_stream_yields_strings

Step 8: Implement tests/unit/test_llm_budget.py
  - test_budget_tracks_spend_across_calls
  - test_daily_budget_resets_at_midnight
  - test_local_tier_not_counted_against_budget (Ollama is free)
  - test_budget_survives_process_restart (persists in Redis)

Step 9: Implement tests/contracts/test_llm_router_contract.py
  - Verify all public methods exist with correct signatures
  - Verify LLMResponse has all required fields
  - Verify ModelTier has all four values
  - Verify Embedding.vector is always length 1024
```

### BUILD CHECKLIST — M1.3

```
Router:
  [ ] router.py: no direct imports of anthropic, openai, litellm (only in _providers/)
  [ ] router.py: tier resolution uses config, not hardcoded model names
  [ ] router.py: budget checked before every LLM call
  [ ] router.py: llm.call.completed event emitted after every call
  [ ] router.py: all methods async
  [ ] router.py: fallback chain: STANDARD → CHEAP → LOCAL

Budget:
  [ ] budget.py: limits from config.budget (never hardcoded)
  [ ] budget.py: spend tracked in Redis (not in-memory)
  [ ] budget.py: hard cutoff forces LOCAL tier (does not raise error)
  [ ] budget.py: 80% threshold emits warning event
  [ ] budget.py: daily reset via Redis TTL mechanism

Embedding:
  [ ] _embedding.py: model name from config.memory.embedding_model
  [ ] _embedding.py: device from config.memory.embedding_device
  [ ] _embedding.py: dimension validated on every output (assertion)
  [ ] _embedding.py: EMBEDDING_DIMENSION constant = 1024 (never from config)

Models (LOCKED):
  [ ] ModelTier: LOCAL, CHEAP, STANDARD, PREMIUM — exactly these four
  [ ] LLMResponse: all fields from Technical Spec Section 2.4 present
  [ ] Embedding.vector: List[float]
  [ ] All models: frozen=True
```

### TEST CHECKLIST — M1.3

```
  [ ] uv run pytest tests/unit/test_llm_router.py -v → all 11 tests pass
  [ ] uv run pytest tests/unit/test_llm_budget.py -v → all 4 tests pass
  [ ] uv run pytest tests/contracts/test_llm_router_contract.py -v → all pass
  [ ] Manual test — Ollama call:
      python -c "
      from aether.llm import LLMRouter, ModelTier
      from aether.llm._models import Message
      import asyncio
      router = LLMRouter()
      resp = asyncio.run(router.complete([Message(role='user', content='say hello')], ModelTier.LOCAL))
      print(resp.content)
      print(f'Cost: {resp.cost_usd}')
      "
      Expected: Response text printed, cost_usd = 0.0 for LOCAL tier

  [ ] Manual test — Embedding:
      python -c "
      from aether.llm import LLMRouter
      import asyncio
      router = LLMRouter()
      emb = asyncio.run(router.embed('test text'))
      print(f'Dimension: {len(emb.vector)}')
      "
      Expected: Dimension: 1024
```

### VALIDATION CHECKLIST — M1.3

```
  [ ] With ANTHROPIC_API_KEY unset: router falls back to LOCAL tier without crashing
  [ ] With daily budget set to $0.001: first call forces LOCAL tier
  [ ] After budget override to LOCAL: llm.call.completed event still emitted
  [ ] Budget spend tracked in Redis: redis-cli GET aether:llm:budget:daily → non-empty
  [ ] Embedding dimension is exactly 1024 on 10 consecutive calls
  [ ] Model tier names in events match ModelTier enum values exactly
```

### ARCHITECTURE COMPLIANCE CHECKLIST — M1.3

```
  [ ] uv run lint-imports → exits 0
  [ ] grep -r "import anthropic\|import openai\|import litellm" aether/ --include="*.py"
      Result: matches ONLY in aether/llm/_providers/ — nowhere else
  [ ] grep -r "claude-\|gpt-4\|gemini-" aether/ --include="*.py"
      Result: matches ONLY in aether/llm/ — nowhere else (no hardcoded model names)
  [ ] aether/llm/__init__.py exports exactly: LLMRouter, ModelTier, LLMResponse, Embedding, BudgetStatus
  [ ] No business logic calls LLM provider directly in this milestone
```

### SECURITY CHECKLIST — M1.3

```
  [ ] No API keys in any Python file
  [ ] No API keys in config/default.yaml
  [ ] Provider constructors read keys via config/env vars only
  [ ] LLM response content is not logged in full (only preview: content[:100])
  [ ] Budget tracking keys in Redis are not encrypted (acceptable: no sensitive data)
  [ ] Security scan passes: grep finds no hardcoded API key patterns
```

### DEFINITION OF DONE — M1.3

All 16 tests pass. Ollama responds to LOCAL tier requests. Claude responds to
STANDARD tier requests. Budget enforcement works — exceeding daily limit forces
LOCAL tier. Embedding returns exactly 1024-dimensional vectors. No LLM provider
imports exist outside aether/llm/_providers/.

### MILESTONE GATE — M1.3

```
GO:   All tests pass. Model routing verified with real API calls. Budget enforcement
      tested. Embedding dimension verified as 1024. Zero provider imports outside
      _providers/.

NO-GO: Any test fails. Hardcoded model names outside llm/. Budget does not enforce.
       Embedding returns wrong dimension. Provider imports found outside _providers/.
```

---

## MILESTONE M1.4: SQLITE SCHEMA + MIGRATIONS

### Overview

Establishes the database schema that all data storage in Phase 1 depends on.
Migrations must be correct, reversible where possible, and match the Technical
Specification exactly. The schema, once defined, is the hardest thing to change
later without a full migration — get it right now.

### Prerequisites
M1.0 passed. M1.1 must be running (not strictly needed for SQLite,
but M1.5 will need Qdrant and Redis).

### Duration
1 working day

### Files Created This Milestone

```
migrations/
├── env.py
├── script.py.mako
└── versions/
    └── 001_initial_schema.py
tests/unit/
└── test_migrations.py
```

### Implementation Sequence

```
Step 1: Configure Alembic
  Run: alembic init migrations
  Update migrations/env.py:
  - Import AetherConfig, get_config
  - Set target_metadata from SQLAlchemy Base
  - Configure async engine from config.database.url

Step 2: Implement migrations/versions/001_initial_schema.py
  This migration creates ALL tables from Technical Specification Section 3.2:
  - conversations (with index on started_at)
  - messages (with indexes on conversation_id, created_at, role)
  - memories (with all indexes; FTS5 virtual table + triggers)
  - tasks (with all indexes; FTS5 virtual table + triggers; updated_at trigger)
  - tool_executions (with indexes on tool_name, created_at, session_id)
  - agent_runs (with indexes on agent_name, status, started_at, session_id)
  - llm_costs (with indexes on created_at, provider)
  - system_kv (with pre-populated initial rows)

  CRITICAL: Every table, index, trigger, and FTS5 virtual table from the
  Technical Specification must be present. Copy the exact DDL from the spec.

  The downgrade() function: drops all tables in reverse order (tasks, memories,
  messages, conversations first due to FKs; then others).
  Drop FTS5 tables and triggers first.

Step 3: Run and verify migration
  alembic upgrade head
  Verify: sqlite3 data/aether.db ".tables" → shows all expected tables
  Verify: sqlite3 data/aether.db ".schema memories" → shows correct schema

Step 4: Create tests/unit/test_migrations.py
  - test_upgrade_creates_all_tables: alembic upgrade head → all tables exist
  - test_downgrade_removes_all_tables: alembic downgrade base → no tables
  - test_upgrade_after_downgrade: downgrade + upgrade cycle succeeds
  - test_fts5_tables_created: memories_fts and tasks_fts exist
  - test_fts5_insert_searchable: insert memory → FTS5 search returns it
  - test_system_kv_prepopulated: aether.version key exists with correct value
  - test_primary_keys_are_text: all id columns accept UUIDv7 strings
  - test_timestamps_default_to_utc: inserted row has UTC timestamp
```

### BUILD CHECKLIST — M1.4

```
Migration File:
  [ ] All 8 tables from Technical Specification Section 3.2 created
  [ ] All indexes from Technical Specification Section 3.2 created
  [ ] FTS5 virtual tables: memories_fts, tasks_fts created
  [ ] FTS5 triggers: ai/ad/au for memories and tasks created
  [ ] tasks updated_at trigger created
  [ ] system_kv table pre-populated with initial rows
  [ ] downgrade() function drops all tables cleanly
  [ ] Migration file is pure SQL/Python — no calls to LLM router, memory API, etc.

Alembic Configuration:
  [ ] env.py reads database URL from config (never hardcoded)
  [ ] Async engine configuration correct for aiosqlite
  [ ] script.py.mako contains correct template
```

### TEST CHECKLIST — M1.4

```
  [ ] alembic upgrade head → exits 0, no errors
  [ ] uv run pytest tests/unit/test_migrations.py -v → all 8 tests pass
  [ ] sqlite3 data/aether.db ".tables" → shows all 10 tables
      (conversations, messages, memories, tasks, tool_executions, agent_runs,
       llm_costs, system_kv, memories_fts, tasks_fts)
  [ ] alembic downgrade -1 → exits 0
  [ ] alembic upgrade head again → exits 0
  [ ] FTS5 search: INSERT a memory, search by keyword → found
```

### VALIDATION CHECKLIST — M1.4

```
  [ ] Schema matches Technical Specification Section 3.2 exactly (compare column by column)
  [ ] UUIDv7 strings accepted as primary keys in all tables
  [ ] Foreign key constraints enforced (attempt to insert message with bad conversation_id → error)
  [ ] Indexes visible: sqlite3 data/aether.db ".indexes" → all expected indexes listed
  [ ] system_kv prepopulated: SELECT value FROM system_kv WHERE key='aether.embedding_dimension'
      → 1024
```

### ARCHITECTURE COMPLIANCE CHECKLIST — M1.4

```
  [ ] uv run lint-imports → exits 0
  [ ] Migration file contains only DDL — no application logic
  [ ] No application code imports directly from migrations/
  [ ] Database URL from config — not hardcoded
```

### SECURITY CHECKLIST — M1.4

```
  [ ] No plaintext passwords or secrets in initial system_kv data
  [ ] Database file path from config (not hardcoded)
  [ ] Migration does not create any users or credentials
  [ ] Security scan passes
```

### DEFINITION OF DONE — M1.4

All 8 tests pass. Schema matches specification exactly. FTS5 virtual tables
and triggers work. Alembic up/down cycle completes without error.

### MILESTONE GATE — M1.4

```
GO:   All tests pass. Schema matches spec exactly. FTS5 working. Up/down cycle clean.

NO-GO: Any table missing. Any index missing. FTS5 not working. Schema deviates
       from specification. Downgrade fails.
```

---

## MILESTONE M1.5: MEMORY SYSTEM

### Overview

The memory system is the most important module in Phase 1. It is what makes
Aether different from a stateless chatbot. The defining test of Phase 1
(tell Aether your name, restart, ask it your name) is entirely a test of this
module. Every minute invested in getting this right is worth it.

### Prerequisites
M1.2 passed. M1.3 passed. M1.4 passed. M1.1 running (Qdrant + Redis needed).

### Duration
5 working days

### Files Created This Milestone

```
aether/memory/
├── __init__.py               (updated: all public exports)
├── api.py                    (NEW)
├── models.py                 (NEW)
├── _stores/
│   ├── sqlite_store.py       (NEW)
│   └── vector_store.py       (NEW)
├── _retrieval/
│   ├── hybrid.py             (NEW)
│   └── reranker.py           (NEW)
└── _consolidation/
    ├── pipeline.py           (NEW)
    └── extractor.py          (NEW)
tests/unit/
├── test_memory_api.py        (NEW)
└── test_memory_retrieval.py  (NEW)
tests/integration/
└── test_memory_pipeline.py   (NEW)
tests/contracts/
└── test_memory_api_contract.py (NEW)
```

### Implementation Sequence

**Day 1: Models and SQLite Store**

```
Step 1: Implement aether/memory/models.py
  - MemoryType enum (FACT, EPISODE, SKILL, PREFERENCE) — LOCKED
  - MemorySource enum (CONVERSATION, DOCUMENT, AGENT, USER) — LOCKED
  - MemoryFilter model (all filter fields from Technical Spec Section 2.5)
  - MemoryRecord model — LOCKED (frozen=True, all fields from spec)
  - ContextPackage model — LOCKED (frozen=True, includes formatted_context string)
  - ConsolidationReport model

Step 2: Implement aether/memory/_stores/sqlite_store.py
  - SQLiteMemoryStore class
  - CRUD for memories, conversations, messages tables
  - FTS5 keyword search: search_by_keyword(query, limit) → List[MemoryRecord]
  - All queries parameterized (no f-strings in SQL)
  - All primary keys use UUIDv7
  - All timestamps use datetime.now(UTC)
  - Connection from config.database.url (never hardcoded)
  - Async with aiosqlite
```

**Day 2: Vector Store and Retrieval**

```
Step 3: Implement aether/memory/_stores/vector_store.py
  - QdrantMemoryStore class
  - initialize_collection(): creates episodic_memory if not exists
    Collection config: size=1024, distance=Cosine, scalar quantization int8
  - upsert(memory_id, vector, payload) → None
  - search(query_vector, limit, filters) → List[scored_points]
  - delete(memory_id) → None
  - All payload fields from Technical Specification Section 4.2
  - Connection from config.qdrant settings

Step 4: Implement aether/memory/_retrieval/reranker.py
  - rerank(candidates, query) → List[MemoryRecord] (sorted by score)
  - Score formula: (0.6 × similarity) + (0.3 × recency_weight) + (0.1 × importance)
  - recency_weight: 1.0 for today, decays to 0.1 over config.memory.importance_decay_days
  - Respects token_budget: assembles ContextPackage stopping when token estimate exceeded
  - Token estimation: len(content.split()) × 1.3 (approximate)

Step 5: Implement aether/memory/_retrieval/hybrid.py
  - HybridRetrieval class
  - search(query, k, filters) → List[MemoryRecord]
  - Step 1: Vector search (Qdrant) → top 20 candidates
  - Step 2: Keyword search (SQLite FTS5) → top 10 candidates
  - Step 3: Deduplicate by memory_id
  - Step 4: Rerank combined set
  - Step 5: Return top k
  - Partial failure: if Qdrant unavailable → use keyword only + log WARNING
  - Partial failure: if SQLite unavailable → use vector only + log WARNING
```

**Day 3: Public API**

```
Step 6: Implement aether/memory/api.py
  - MemoryAPI class — THE ONLY PUBLIC INTERFACE
  - remember(content, memory_type, importance, metadata, session_id, source) → str
    1. Generate embedding via LLMRouter.embed()
    2. Create MemoryRecord with UUIDv7 id
    3. Store in SQLite (sqlite_store.upsert())
    4. Store in Qdrant (vector_store.upsert())
    5. Emit memory.store.created event
    6. Return memory_id
  - recall(query, k, filters, token_budget) → ContextPackage
    1. Generate query embedding via LLMRouter.embed()
    2. HybridRetrieval.search(query, k, filters)
    3. Update last_accessed_at and access_count in SQLite
    4. Return ContextPackage with formatted_context
  - forget(memory_id, reason) → bool
    1. Delete from SQLite
    2. Delete from Qdrant
    3. Emit memory.store.deleted event
    4. Log the reason
  - consolidate(session_id) → ConsolidationReport
    (delegates to _consolidation/pipeline.py)
  - search(query, memory_type, limit, min_importance) → List[MemoryRecord]
  - All methods async
```

**Day 4: Consolidation Pipeline**

```
Step 7: Implement aether/memory/_consolidation/extractor.py
  - FactExtractor class
  - extract_facts(text: str) → List[str]
    Uses LLMRouter with ModelTier.LOCAL (free — consolidation should not cost money)
    Prompt: given a conversation summary, extract atomic facts as a list
    Returns: list of fact strings

Step 8: Implement aether/memory/_consolidation/pipeline.py
  - ConsolidationPipeline class
  - run(session_id) → ConsolidationReport
    1. Load all messages for session_id from SQLite
    2. If message_count < config.memory.consolidation_min_messages: skip
    3. Call LLMRouter.complete() with ModelTier.LOCAL to summarize session
    4. Call FactExtractor.extract_facts(summary)
    5. For each fact: MemoryAPI.remember(fact, MemoryType.FACT, importance=0.6)
    6. Store session summary as MemoryType.EPISODE
    7. Emit memory.consolidation.completed event
    8. Return ConsolidationReport
```

**Day 5: Tests**

```
Step 9: Implement all test files
  tests/unit/test_memory_api.py (12 required tests):
  - test_remember_stores_to_sqlite
  - test_remember_stores_to_qdrant
  - test_remember_returns_uuid_string
  - test_remember_emits_event
  - test_recall_returns_relevant_memories
  - test_recall_respects_token_budget
  - test_recall_updates_access_count
  - test_recall_updates_last_accessed_at
  - test_forget_removes_from_sqlite
  - test_forget_removes_from_qdrant
  - test_forget_requires_reason
  - test_forget_emits_event

  tests/integration/test_memory_pipeline.py (THE CRITICAL TEST):
  CRITICAL TEST — must pass for MILESTONE GATE:
  - test_cross_session_memory_persistence:
    1. remember("User's name is Alex", MemoryType.FACT, 0.9)
    2. Stop and restart Qdrant + Redis (docker compose restart)
    3. recall("what is the user's name")
    4. Assert: returned ContextPackage contains "Alex"
    This test must pass. It is the proof the memory system works.

  tests/contracts/test_memory_api_contract.py:
  - Verify all 6 public methods exist with correct signatures
  - Verify MemoryRecord has all required fields
  - Verify ContextPackage has formatted_context field
```

### BUILD CHECKLIST — M1.5

```
api.py (CRITICAL — LOCKED INTERFACE):
  [ ] remember() signature matches Technical Spec exactly
  [ ] recall() signature matches Technical Spec exactly
  [ ] forget() signature matches Technical Spec exactly
  [ ] consolidate() signature matches Technical Spec exactly
  [ ] search() signature matches Technical Spec exactly
  [ ] All methods async

SQLite Store:
  [ ] All SQL queries parameterized (no string concatenation)
  [ ] All primary keys: str(uuid_utils.uuid7())
  [ ] All timestamps: datetime.now(UTC)
  [ ] Connection from config (never hardcoded path)

Vector Store:
  [ ] Collection initialized with size=1024 exactly
  [ ] Collection initialized with distance=Cosine
  [ ] All payload fields from Technical Spec Section 4.2 present
  [ ] Connection from config.qdrant settings

Retrieval:
  [ ] Rerank score formula: 0.6/0.3/0.1 weights
  [ ] Token budget respected in ContextPackage assembly
  [ ] Partial failure handled: vector-only or keyword-only with WARNING log

Consolidation:
  [ ] Uses ModelTier.LOCAL (not STANDARD — free operation)
  [ ] Minimum messages check before running (config.memory.consolidation_min_messages)
  [ ] Emits memory.consolidation.completed event
```

### TEST CHECKLIST — M1.5

```
  [ ] uv run pytest tests/unit/test_memory_api.py -v → all 12 pass
  [ ] uv run pytest tests/unit/test_memory_retrieval.py -v → all pass
  [ ] uv run pytest tests/contracts/test_memory_api_contract.py -v → all pass
  [ ] uv run pytest tests/integration/test_memory_pipeline.py -v → ALL PASS

  CRITICAL TEST (must be run manually and observed):
  [ ] python -c "
      from aether.memory import MemoryAPI, MemoryType
      import asyncio
      api = MemoryAPI()
      asyncio.run(api.initialize())
      id = asyncio.run(api.remember(\"User's name is Alex\", MemoryType.FACT, 0.9))
      print(f'Stored: {id}')
      pkg = asyncio.run(api.recall(\"what is the user name\"))
      print(pkg.formatted_context)
      assert \"Alex\" in pkg.formatted_context, \"CRITICAL TEST FAILED\"
      print(\"CRITICAL TEST PASSED\")
      "
```

### VALIDATION CHECKLIST — M1.5

```
  [ ] CRITICAL: Store "User's name is Alex" → docker compose restart → recall → Alex found
  [ ] Qdrant collection "episodic_memory" exists: curl http://localhost:6333/collections
  [ ] SQLite memories table has rows after remember() call
  [ ] recall() result: similarity_score present and between 0 and 1
  [ ] Consolidation: run pipeline on 10 messages → facts stored in memories table
  [ ] Token budget: recall with token_budget=100 returns fewer memories than token_budget=4096
  [ ] access_count increments on each recall of same memory
```

### ARCHITECTURE COMPLIANCE CHECKLIST — M1.5

```
  [ ] uv run lint-imports → exits 0
  [ ] grep -r "qdrant_client\|sqlalchemy\|sqlite3\|aiosqlite" aether/ --include="*.py"
      Result: matches ONLY in aether/memory/_stores/ — nowhere else
  [ ] api.py: calls LLMRouter for embeddings — does not import embedding model directly
  [ ] No memory module code calls LLM providers directly
  [ ] MemoryRecord and ContextPackage models: frozen=True verified
```

### SECURITY CHECKLIST — M1.5

```
  [ ] No user content logged in full (only content[:100] in any log)
  [ ] forget() audit log includes reason field (never empty)
  [ ] No SQL injection: all queries use parameterized form
  [ ] Memory content not exposed in event payloads (only memory_id and type)
  [ ] Security scan passes
```

### DEFINITION OF DONE — M1.5

All 12 unit tests pass. All integration tests pass. The CRITICAL TEST passes:
store a fact, restart infrastructure, recall the fact. All five checklists pass.
No imports of qdrant_client or sqlalchemy exist outside aether/memory/_stores/.

### MILESTONE GATE — M1.5

```
GO:   CRITICAL TEST passes. All unit tests pass. All integration tests pass.
      Zero database imports outside _stores/. Qdrant collection initialized.

NO-GO: CRITICAL TEST fails for any reason. Any unit test fails. Any database
       import found outside _stores/. MemoryAPI signature deviates from spec.
```

---

## MILESTONE M1.6: TOOL SYSTEM + TASK MANAGER

### Overview

Establishes the tool registry and built-in tools, plus the task management
domain. After this milestone, agents have callable capabilities and Aether
can track work across sessions.

### Prerequisites
M1.5 passed. M1.3 passed (tools may call LLM router). M1.4 passed (tasks in SQLite).

### Duration
3 working days

### Files Created This Milestone

```
aether/tools/
├── __init__.py                 (updated)
├── base.py                     (NEW)
├── registry.py                 (NEW)
└── _implementations/
    ├── datetime_tools.py       (NEW)
    ├── search_tools.py         (NEW)
    └── task_tools.py           (NEW)
aether/tasks/
├── __init__.py                 (updated)
├── manager.py                  (NEW)
└── models.py                   (NEW)
tests/unit/
├── test_tool_registry.py       (NEW)
├── test_tool_implementations.py (NEW)
└── test_task_manager.py        (NEW)
tests/contracts/
└── test_tool_interface_contract.py (NEW)
```

### Implementation Sequence

**Day 1: Tool Framework**

```
Step 1: Implement aether/tools/base.py
  - BaseTool abstract class — LOCKED interface
  - ClassVars: name, description, input_schema, output_schema, required_permissions
  - execute(input: BaseModel) → ToolResult (abstract)
  - to_function_schema() → dict (default implementation from input_schema)
  - check_permissions() → bool (default: checks permissions.yaml)
  - ToolResult model: frozen=True, success, data, error, error_code, metadata

Step 2: Implement aether/tools/registry.py
  - ToolRegistry class (singleton pattern)
  - register(tool: BaseTool) → None
  - get(name: str) → BaseTool (raises ToolNotFoundError if missing)
  - list() → List[ToolManifest]
  - get_function_schemas(tool_names: List[str]) → List[dict]
    Returns Anthropic-compatible function calling schemas
  - _instance: class-level singleton, not module-level global
```

**Day 2: Built-in Tools and Task Manager**

```
Step 3: Implement tools/_implementations/datetime_tools.py
  - GetCurrentDatetimeTool
  - name = "get_current_datetime"
  - Input: empty Pydantic model
  - Output: datetime, date, time, day_of_week, timezone (from system)
  - No LLM calls. No external calls. Pure local operation.

Step 4: Implement tools/_implementations/search_tools.py
  - WebSearchTool
  - name = "web_search"
  - Input: query (str), num_results (int, default=5)
  - Uses DuckDuckGo via duckduckgo-search library (no API key needed)
  - Output: List[{title, url, snippet}]
  - Timeout: 10 seconds
  - On failure: ToolResult(success=False, error="Search failed: {reason}")

Step 5: Implement tools/_implementations/task_tools.py
  - CreateTaskTool, ListTasksTool, UpdateTaskStatusTool
  - Each calls TaskManager internally
  - Emits task lifecycle events via EventBus

Step 6: Implement aether/tasks/models.py
  - Task model: all fields from Technical Spec Section 2.9
  - TaskStatus enum: PENDING, ACTIVE, COMPLETED, CANCELLED, FAILED
  - TaskPriority enum: LOW, MEDIUM, HIGH, CRITICAL
  - TaskFilter model for list queries

Step 7: Implement aether/tasks/manager.py
  - TaskManager class
  - create(title, description, priority, due_at, category, parent_task_id) → Task
  - get(task_id) → Task
  - list(status, priority, category, limit, offset) → List[Task]
  - update_status(task_id, new_status, note) → Task
  - update(task_id, **updates) → Task
  - delete(task_id) → bool
  - get_active_summary() → str (formatted for morning briefing)
  - All status changes emit task.lifecycle.status_changed event
```

**Day 3: Tests**

```
Step 8: Implement all test files
  test_tool_registry.py:
  - test_register_and_retrieve_tool
  - test_get_nonexistent_tool_raises_error
  - test_list_returns_all_registered_tools
  - test_function_schema_valid_anthropic_format
  - test_registry_singleton_across_imports

  test_tool_implementations.py:
  - test_datetime_tool_returns_current_time
  - test_datetime_tool_output_schema_valid
  - test_web_search_returns_results (use real DuckDuckGo with simple query)
  - test_web_search_timeout_returns_error_result
  - test_create_task_tool_creates_in_database
  - test_list_tasks_tool_returns_tasks
  - test_update_status_tool_changes_status

  test_task_manager.py:
  - test_create_task_stores_in_sqlite
  - test_task_status_state_machine (all valid transitions)
  - test_invalid_status_transition_raises_error
  - test_list_filters_by_status
  - test_active_summary_includes_high_priority_tasks
  - test_status_change_emits_event
```

### BUILD CHECKLIST — M1.6

```
BaseTool (LOCKED):
  [ ] All ClassVars present: name, description, input_schema, output_schema
  [ ] execute() signature: execute(self, input: BaseModel) → ToolResult
  [ ] to_function_schema() produces Anthropic-compatible format
  [ ] ToolResult: frozen=True, all fields present

ToolRegistry:
  [ ] Singleton — single instance per process
  [ ] get() raises ToolNotFoundError (not KeyError) for missing tools
  [ ] get_function_schemas() validates all tool names exist before returning

Built-in Tools:
  [ ] get_current_datetime: no external calls, pure local
  [ ] web_search: no API key required (DuckDuckGo)
  [ ] web_search: timeout enforced (does not hang)
  [ ] task tools: call TaskManager (not SQLite directly)

TaskManager:
  [ ] All status transitions follow the state machine from Technical Spec Section 2.9
  [ ] All status changes emit task.lifecycle.status_changed event
  [ ] SQLite operations via SQLAlchemy (not raw sqlite3)
```

### TEST CHECKLIST — M1.6

```
  [ ] uv run pytest tests/unit/test_tool_registry.py -v → all 5 tests pass
  [ ] uv run pytest tests/unit/test_tool_implementations.py -v → all 7 tests pass
  [ ] uv run pytest tests/unit/test_task_manager.py -v → all 6 tests pass
  [ ] uv run pytest tests/contracts/test_tool_interface_contract.py -v → all pass
  [ ] Manual: web_search("Python asyncio tutorial") → returns results with titles and URLs
  [ ] Manual: create task → check SQLite → task appears in tasks table
```

### VALIDATION CHECKLIST — M1.6

```
  [ ] All three built-in tools registered on module import
  [ ] get_function_schemas(["get_current_datetime"]) → valid Anthropic tool schema
  [ ] Task created via tool appears in SQLite tasks table
  [ ] Task status change → event visible in Redis: XRANGE aether:events - + COUNT 1
  [ ] get_active_summary() returns non-empty string when tasks exist
```

### ARCHITECTURE COMPLIANCE CHECKLIST — M1.6

```
  [ ] uv run lint-imports → exits 0
  [ ] task_tools.py: calls TaskManager (not SQLite directly)
  [ ] No tool calls LLM provider directly (uses LLMRouter if needed)
  [ ] Tools do not import from aether.memory directly
  [ ] aether/tools/__init__.py exports: ToolRegistry, BaseTool, ToolResult
```

### SECURITY CHECKLIST — M1.6

```
  [ ] web_search: no user-provided URLs executed (only query strings sent to DDG)
  [ ] task tools: task IDs validated as UUIDv7 strings before database lookup
  [ ] No tool result content larger than 50KB (truncate large results)
  [ ] Security scan passes
```

### DEFINITION OF DONE — M1.6

All 18 tests pass. All three built-in tools produce correct output. Task CRUD
works end-to-end. Status changes emit events. Tool registry returns valid
function schemas for LLM function calling.

### MILESTONE GATE — M1.6

```
GO:   All tests pass. All tools produce correct output. Task events visible in Redis.
      Function schema passes Anthropic format validation.

NO-GO: Any test fails. web_search fails on simple query. Task status events
       not emitted. Tool imports database clients directly.
```

---

## MILESTONE M1.7: AGENT RUNTIME + CONVERSATION AGENT

### Overview

The first intelligent behavior in the system. After this milestone, Aether
can understand a request, reason about it, invoke tools, access memory, and
produce a response. This is the core loop.

### Prerequisites
M1.5 passed. M1.6 passed. M1.3 passed.

### Duration
5 working days

### Files Created This Milestone

```
aether/agents/
├── __init__.py                       (updated)
├── base.py                           (NEW)
├── runtime.py                        (NEW)
└── _implementations/
    └── conversation.py               (NEW)
aether/core/
└── kernel.py                         (NEW — initial bootstrap)
tests/unit/
├── test_base_agent.py               (NEW)
└── test_agent_runtime.py            (NEW)
tests/integration/
└── test_conversation_flow.py        (NEW — includes the cross-session test)
tests/contracts/
└── test_agent_interface_contract.py (NEW)
```

### Implementation Sequence

**Day 1: BaseAgent**

```
Step 1: Implement aether/agents/base.py
  - BaseAgent abstract class — LOCKED interface
  - ClassVars: name, role, llm_tier, allowed_tools, max_iterations
  - execute(task: AgentTask, context: AgentContext) → AgentResult (abstract)
  - _recall(query, k, filters) → ContextPackage (calls MemoryAPI.recall())
  - _remember(content, memory_type, importance) → str (calls MemoryAPI.remember())
  - _invoke_tool(name, input_dict) → ToolResult (calls ToolRegistry.get().execute())
    with: permission check, input validation, timeout, audit log entry, event emit
  - AgentTask model — LOCKED (from Technical Spec Section 2.7)
  - AgentContext model — LOCKED (frozen, all fields from spec)
  - AgentResult model — LOCKED (frozen, all fields from spec)

  CRITICAL: _recall() and _remember() are BaseAgent methods.
  No agent subclass may import MemoryAPI directly.
  No agent subclass may call ToolRegistry directly.
  All memory and tool access goes through these helpers.
```

**Day 2: Agent Runtime**

```
Step 2: Implement aether/agents/runtime.py
  - AgentRuntime class
  - execute(agent_type, task, context) → AgentResult
    1. Resolve agent class from registry
    2. Record agent_run start in SQLite
    3. Emit agent.run.started event
    4. Run agent with timeout (task.timeout_seconds)
    5. If timeout: return AgentResult(success=False, error="Timeout")
    6. Record agent_run completion in SQLite (tokens, cost, duration)
    7. Emit agent.run.completed or agent.run.failed event
    8. Return AgentResult
  - register_agent(agent_type: str, agent_class: Type[BaseAgent]) → None
  - list_agents() → List[str]
  - Phase 1 implementation: simple sequential runner (no LangGraph)
  - LangGraph will be introduced in Phase 5 — the interface does not change
```

**Day 3: ConversationAgent**

```
Step 3: Implement aether/agents/_implementations/conversation.py
  - ConversationAgent extends BaseAgent
  - name = "conversation"
  - role = "Personal AI assistant with persistent memory"
  - llm_tier = ModelTier.STANDARD
  - allowed_tools = ["get_current_datetime", "web_search",
                      "create_task", "list_tasks", "update_task_status"]
  - max_iterations = 5
  - SYSTEM_PROMPT: from Technical Specification Section 8.6
    Contains placeholders for memory_context, active_tasks_summary, current_datetime
  - execute(task, context):
    1. Build system prompt with context.memory_context.formatted_context
    2. Build messages from context.conversation_history
    3. Add current user message
    4. LLM call loop (max max_iterations):
       a. router.complete(messages, llm_tier, function schemas)
       b. If tool_call in response: invoke tool, append to messages, continue
       c. If no tool_call: extract response, break
    5. self._remember(summary_of_turn, MemoryType.EPISODE, 0.4)
    6. Return AgentResult
```

**Day 4: Kernel Bootstrap**

```
Step 4: Implement aether/core/kernel.py (initial version)
  - AetherKernel class
  - initialize() async method:
    1. Load config
    2. Configure logging
    3. Connect to Redis (EventBus)
    4. Run Alembic migrations (upgrade head)
    5. Initialize Qdrant collection (episodic_memory)
    6. Initialize LLMRouter
    7. Initialize MemoryAPI
    8. Initialize ToolRegistry and register all built-in tools
    9. Initialize AgentRuntime and register ConversationAgent
    10. Initialize TaskManager
    11. Log "Aether kernel initialized" with component list
  - shutdown() async method: graceful cleanup, session consolidation
  - Startup order is fixed — no component initializes before its dependencies
```

**Day 5: Tests**

```
Step 5: Implement all test files
  test_base_agent.py:
  - test_recall_calls_memory_api (not qdrant_client directly)
  - test_remember_calls_memory_api
  - test_invoke_tool_validates_input_before_execute
  - test_invoke_tool_logs_to_audit_table
  - test_invoke_tool_emits_event
  - test_invoke_tool_respects_max_timeout

  test_agent_runtime.py:
  - test_execute_records_agent_run_in_sqlite
  - test_execute_emits_started_and_completed_events
  - test_execute_timeout_returns_failure_result
  - test_register_and_list_agents

  test_conversation_flow.py (integration):
  - test_conversation_agent_uses_datetime_tool:
    Task: "What time is it?" → Agent calls get_current_datetime → response contains time
  - test_conversation_agent_stores_memory:
    After executing: memory with EPISODE type exists in SQLite
  - test_conversation_agent_recalls_prior_context:
    remember("User works on Aether AI OS") → execute task about projects →
    response references Aether
  - THE CROSS-SESSION TEST (integration, requires real services):
    1. remember("User's name is Alex", MemoryType.FACT, 0.9)
    2. Execute: task.description = "What is my name?"
    3. Assert: response contains "Alex"
    This proves agents use the memory system correctly.
```

### BUILD CHECKLIST — M1.7

```
BaseAgent (LOCKED):
  [ ] execute() signature: execute(self, task: AgentTask, context: AgentContext) → AgentResult
  [ ] _recall() calls MemoryAPI (does not import qdrant_client)
  [ ] _remember() calls MemoryAPI (does not import sqlite3)
  [ ] _invoke_tool() validates input, checks permissions, logs to audit table, emits event
  [ ] AgentTask: frozen=True, all fields from spec
  [ ] AgentContext: frozen=True, all fields from spec
  [ ] AgentResult: frozen=True, all fields from spec

ConversationAgent:
  [ ] Uses ModelTier.STANDARD (not hardcoded model name)
  [ ] System prompt contains memory_context placeholder
  [ ] Iteration limit enforced (max_iterations)
  [ ] Session memory stored via self._remember() after each turn
  [ ] Tool schemas generated from registry.get_function_schemas()

Kernel:
  [ ] Initialization order is dependency-correct (no component before its deps)
  [ ] All tools registered before agents
  [ ] All agents registered before session manager
  [ ] Qdrant collection initialized before MemoryAPI
```

### TEST CHECKLIST — M1.7

```
  [ ] uv run pytest tests/unit/test_base_agent.py -v → all 6 tests pass
  [ ] uv run pytest tests/unit/test_agent_runtime.py -v → all 4 tests pass
  [ ] uv run pytest tests/contracts/test_agent_interface_contract.py -v → all pass
  [ ] uv run pytest tests/integration/test_conversation_flow.py -v → all 4 pass
  [ ] THE CROSS-SESSION TEST passes (run manually, observe output):
      Task: "What is my name?" after remembering "User's name is Alex"
      Expected output contains: "Alex"
```

### VALIDATION CHECKLIST — M1.7

```
  [ ] Agent run appears in agent_runs table after execution
  [ ] Tool execution appears in tool_executions table
  [ ] agent.run.started event visible in Redis stream
  [ ] agent.run.completed event visible in Redis stream with token counts
  [ ] LLM cost recorded in llm_costs table
  [ ] ConversationAgent correctly uses datetime tool when asked about time
```

### ARCHITECTURE COMPLIANCE CHECKLIST — M1.7

```
  [ ] uv run lint-imports → exits 0
  [ ] grep -r "qdrant_client\|sqlalchemy" aether/agents/ → zero matches
  [ ] grep -r "anthropic\|openai\|litellm" aether/agents/ → zero matches
  [ ] ConversationAgent does not import MemoryAPI (uses self._recall/self._remember)
  [ ] ConversationAgent does not import ToolRegistry (uses self._invoke_tool)
  [ ] AgentRuntime.execute() is the only entry point for agent execution
```

### SECURITY CHECKLIST — M1.7

```
  [ ] Tool execution: permissions checked before execute() is called
  [ ] Tool input: validated against input_schema before execute() is called
  [ ] Conversation content: logged at DEBUG level only (not INFO)
  [ ] Agent results: not logged in full (only result_preview[:200])
  [ ] Security scan passes
```

### DEFINITION OF DONE — M1.7

All 14 tests pass. The cross-session test passes. Agent runs are recorded.
Events are emitted. Tool use is logged. Kernel initializes all components
in correct order. No database or LLM provider imports in agents/.

### MILESTONE GATE — M1.7

```
GO:   All tests pass. Cross-session test passes. Kernel initializes cleanly.
      Zero database imports in agents/. Zero provider imports in agents/.

NO-GO: Any test fails. Cross-session test fails. Kernel fails to initialize.
       Any direct database or provider import found in agents/.
```

---

## MILESTONE M1.8: SESSION MANAGER + MORNING BRIEFING

### Overview

Session management wraps the conversation loop with lifecycle events:
start, context loading, consolidation trigger on end. The morning briefing
makes Aether feel like JARVIS — it greets you with what matters.

### Prerequisites
M1.7 passed.

### Duration
3 working days

### Files Created This Milestone

```
aether/session/
├── __init__.py           (updated)
├── manager.py            (NEW)
├── startup.py            (NEW)
└── models.py             (NEW)
tests/unit/
└── test_session_manager.py  (NEW)
tests/integration/
├── test_consolidation.py    (NEW)
└── test_event_flow.py       (NEW)
```

### Implementation Sequence

**Day 1: Session Models and Manager**

```
Step 1: Implement aether/session/models.py
  - Session model: id (UUIDv7), started_at, mode, status, message_count
  - SessionMode enum: VOICE, TEXT, TASK
  - SessionContext model: session_id, messages, active_tasks, memory_context,
    last_activity, working_summary

Step 2: Implement aether/session/manager.py
  - SessionManager class
  - start_session(mode) → Session:
    1. Create session record in SQLite
    2. Load morning briefing context via startup.py
    3. Cache SessionContext in Redis (aether:session:{id}:context, 24h TTL)
    4. Emit session.lifecycle.started event with user_context
    5. Return Session

  - end_session(session_id, trigger) → None:
    1. Update session record in SQLite (ended_at, message_count)
    2. Emit session.lifecycle.ended event
    3. Trigger consolidation pipeline (async, non-blocking)
    4. Clear Redis session cache

  - get_context(session_id) → SessionContext:
    Load from Redis cache. If expired: rebuild from SQLite.

  - update_context(session_id, new_messages) → None:
    Append to Redis cache. Update message_count in SQLite.

  - get_morning_briefing(session_id) → str:
    Delegates to startup.py
```

**Day 2: Morning Briefing and Consolidation**

```
Step 3: Implement aether/session/startup.py
  - SessionStartupBuilder class
  - build_context(session_id) → SessionContext:
    Assembles:
    - Active tasks (TaskManager.list(status=ACTIVE, limit=10))
    - Recent memories (MemoryAPI.recall("recent projects and tasks", k=5))
    - Last session summary (from system_kv or memories)
    - Current datetime

  - build_morning_briefing(context: SessionContext) → str:
    Format: "Good {morning/afternoon/evening}. {N} active tasks.
             {Priority summary}. {Most important item}."
    Examples:
    "Good morning. You have 3 active tasks. The highest priority is
     debugging the memory module. Your last session was 8 hours ago."
    Keep under 50 words for TTS fluency.

Step 4: Wire consolidation to session end
  - Update end_session() to trigger ConsolidationPipeline.run(session_id)
  - Trigger is non-blocking: asyncio.create_task() — does not delay end_session()
  - Consolidation failure: log ERROR, do not raise (session must still end)
```

**Day 3: Tests**

```
Step 5: Implement test files
  test_session_manager.py:
  - test_start_session_creates_sqlite_record
  - test_start_session_caches_context_in_redis
  - test_start_session_emits_lifecycle_event
  - test_end_session_emits_lifecycle_event
  - test_end_session_triggers_consolidation
  - test_get_context_loads_from_redis_cache
  - test_context_rebuilt_after_redis_expiry
  - test_morning_briefing_includes_active_tasks
  - test_morning_briefing_under_50_words

  test_consolidation.py (integration):
  - test_consolidation_creates_long_term_memories:
    1. Store 10 messages in SQLite for a session
    2. Run consolidation
    3. Verify: new memories exist in SQLite/Qdrant with source=CONVERSATION
  - test_consolidation_with_insufficient_messages:
    < min_messages → ConsolidationReport with memories_created=0, no error

  test_event_flow.py (integration):
  - test_session_start_to_end_event_sequence:
    start_session → update_context (several) → end_session
    Verify Redis stream contains: started, agent.run events, ended events
    in correct temporal order
```

### BUILD CHECKLIST — M1.8

```
SessionManager:
  [ ] start_session(): emits session.lifecycle.started with user_context fields
  [ ] end_session(): consolidation is non-blocking (asyncio.create_task)
  [ ] end_session(): consolidation failure does not raise (logged only)
  [ ] Context cache: Redis TTL = 24 hours
  [ ] Context cache: rebuilt from SQLite if Redis key missing

Morning Briefing:
  [ ] Always under 50 words (enforce with assertion or truncation)
  [ ] Time-of-day greeting correct (good morning / afternoon / evening)
  [ ] Includes active task count
  [ ] Includes highest-priority active task title
  [ ] Returns empty/minimal string when no sessions or tasks exist

Consolidation:
  [ ] Uses ModelTier.LOCAL (free)
  [ ] Skips if message_count < config.memory.consolidation_min_messages
  [ ] Stores summary as MemoryType.EPISODE
  [ ] Stores extracted facts as MemoryType.FACT
  [ ] Emits memory.consolidation.completed event
```

### TEST CHECKLIST — M1.8

```
  [ ] uv run pytest tests/unit/test_session_manager.py -v → all 9 tests pass
  [ ] uv run pytest tests/integration/test_consolidation.py -v → all 2 tests pass
  [ ] uv run pytest tests/integration/test_event_flow.py -v → all pass
  [ ] Morning briefing manual test:
      python -c "
      from aether.session import SessionManager
      import asyncio
      sm = SessionManager()
      session = asyncio.run(sm.start_session())
      briefing = asyncio.run(sm.get_morning_briefing(session.id))
      print(briefing)
      print(f'Word count: {len(briefing.split())}')
      assert len(briefing.split()) <= 50
      "
```

### VALIDATION CHECKLIST — M1.8

```
  [ ] Start session → end session → check SQLite conversations table → row with ended_at populated
  [ ] 10 messages → end session → wait 5s → check memories table → new rows with source=conversation
  [ ] Morning briefing: correct time-of-day greeting for current system time
  [ ] Event sequence in Redis: started, ended in correct order
  [ ] After Redis flush (dev only): context rebuilds from SQLite correctly
```

### ARCHITECTURE COMPLIANCE CHECKLIST — M1.8

```
  [ ] uv run lint-imports → exits 0
  [ ] session/ module does not import from memory/_stores/ directly
  [ ] session/ module does not import from tasks/manager.py internal methods
  [ ] All events use AetherEvent schema exactly
```

### SECURITY CHECKLIST — M1.8

```
  [ ] Morning briefing does not include full memory content (only titles/summaries)
  [ ] Session context cached in Redis does not include raw API keys or secrets
  [ ] Session IDs are UUIDv7 (not sequential or predictable)
  [ ] Security scan passes
```

### DEFINITION OF DONE — M1.8

All 11 tests pass. Morning briefing is under 50 words and contains accurate
task and context information. Consolidation runs non-blocking after session end.
Long-term memories created from session conversation.

### MILESTONE GATE — M1.8

```
GO:   All tests pass. Morning briefing accurate and under 50 words.
      Consolidation creates memories. Events in correct sequence.

NO-GO: Any test fails. Morning briefing over 50 words. Consolidation blocks
       session end. No memories created after consolidation.
```

---

## MILESTONE M1.9: CLI INTERFACE

### Overview

The first user-facing interface. After this milestone, a complete text-based
interaction with Aether is possible: conversation, tasks, memory inspection.
This is the TEXT MILESTONE — the first point where Aether is genuinely usable.

### Prerequisites
M1.8 passed.

### Duration
3 working days

### Files Created This Milestone

```
aether/
├── __main__.py                   (NEW — entry point)
├── core/
│   └── kernel.py                 (UPDATED — full bootstrap)
└── interfaces/
    ├── __init__.py               (updated)
    ├── cli.py                    (NEW)
    └── api.py                    (NEW — internal FastAPI)
tests/integration/
└── test_task_workflow.py         (NEW)
```

### Implementation Sequence

**Day 1: Entry Point and Kernel Completion**

```
Step 1: Complete aether/core/kernel.py
  Add to initialize():
  - Initialize SessionManager
  - Start EventBus consumer groups for session and memory modules
  - Register signal handlers (SIGINT, SIGTERM) → graceful shutdown
  - Health check: verify Redis, Qdrant, SQLite accessible before declaring ready
  Add to shutdown():
  - End active session if one exists (trigger consolidation)
  - Wait for consolidation coroutine to complete (max 30s)
  - Close all database connections
  - Stop EventBus consumers
  - Log "Aether shutdown complete"

Step 2: Implement aether/__main__.py
  - Parse CLI args: --mode text|voice (default: text)
  - Initialize AetherKernel
  - Start appropriate interface (CLI for text mode)
  - Await shutdown signal
  - Run kernel.shutdown()
  - Exit cleanly

Step 3: Implement aether/interfaces/api.py
  - FastAPI app on localhost:8000
  - POST /conversation/message: receives text, returns agent response
  - GET /session/context: returns current session state
  - GET /health: returns system health status
  - This API is for internal use (voice service → core in Phase 1)
  - No authentication in Phase 1 (localhost only, single user)
```

**Day 2: CLI Interface**

```
Step 4: Implement aether/interfaces/cli.py
  - Text-based interface (use Rich library for formatting)
  - Main loop:
    1. Display: "Aether > " prompt
    2. Read user input
    3. Handle commands (/tasks, /memory <query>, /status, /help, /quit)
    4. Non-command input: send to ConversationAgent via AgentRuntime
    5. Display agent response with formatting
    6. Repeat
  - Session startup: display morning briefing on first run
  - /tasks: list active tasks with priority and status
  - /memory <query>: display top 5 memories matching query
  - /status: display session info, budget used, memory count
  - /help: display command list
  - /quit: trigger graceful shutdown (end session, consolidation, exit)
  - Ctrl+C: same as /quit

  Do not use Textual TUI yet (adds complexity without immediate value).
  Plain terminal with Rich library for colors and tables is sufficient.
```

**Day 3: Tests and Integration**

```
Step 5: Implement tests/integration/test_task_workflow.py
  - test_create_task_via_agent:
    Execute conversation: "Create a task called 'Fix memory module bug'"
    Verify: task exists in SQLite with correct title
  - test_list_tasks_via_agent:
    Create 3 tasks → execute "What tasks do I have active?" → response lists them
  - test_complete_task_via_agent:
    Create task → execute "Mark the memory bug task as completed"
    Verify: task status = COMPLETED in SQLite

Step 6: Full end-to-end integration test (manual)
  Run: python -m aether
  Test sequence:
  1. Morning briefing appears
  2. Type: "My name is Alex"  → Aether confirms it will remember
  3. Type: "Create a task to review the architecture document"  → Task created
  4. Type: "/tasks"  → Task appears in list
  5. Type: "/quit"  → Shutdown message, session consolidation runs
  6. Run: python -m aether again
  7. Type: "What's my name?" → Aether recalls "Alex"
  8. Type: "/tasks" → Previous task still appears
  This is the TEXT MILESTONE validation.
```

### BUILD CHECKLIST — M1.9

```
Entry Point:
  [ ] python -m aether starts without error
  [ ] Ctrl+C triggers graceful shutdown (not abrupt process kill)
  [ ] Shutdown includes session consolidation before exit

CLI:
  [ ] /tasks displays task list with priority and status columns
  [ ] /memory <query> displays top 5 memories with similarity scores
  [ ] /status displays: session_id, uptime, memory count, LLM cost today
  [ ] /quit triggers graceful shutdown
  [ ] /help displays all commands with descriptions
  [ ] Non-command text routes to ConversationAgent

FastAPI:
  [ ] POST /conversation/message → 200 with response text
  [ ] GET /health → 200 with component status
  [ ] Server binds to 127.0.0.1:8000 (not 0.0.0.0)
```

### TEST CHECKLIST — M1.9

```
  [ ] uv run pytest tests/integration/test_task_workflow.py -v → all 3 tests pass
  [ ] TEXT MILESTONE VALIDATION (manual sequence from Day 3, Step 6):
      [ ] Morning briefing appears on startup
      [ ] "My name is Alex" → remembered
      [ ] Task created via natural language
      [ ] /quit → graceful shutdown with consolidation message
      [ ] Restart → "What's my name?" → "Alex" recalled
      [ ] /tasks → previous task visible
```

### VALIDATION CHECKLIST — M1.9

```
  [ ] python -m aether starts and displays morning briefing within 3 seconds
  [ ] Complete TEXT MILESTONE sequence passes (7 steps above)
  [ ] /quit exits process cleanly (no hanging threads)
  [ ] FastAPI health endpoint: curl http://localhost:8000/health → {"status":"healthy"}
  [ ] Session consolidation runs and completes before process exits
```

### ARCHITECTURE COMPLIANCE CHECKLIST — M1.9

```
  [ ] uv run lint-imports → exits 0
  [ ] cli.py: no business logic — only display and routing
  [ ] api.py: no business logic — only HTTP → AgentRuntime delegation
  [ ] Interfaces do not import MemoryAPI, SQLiteStore, or any storage layer
  [ ] All agent execution goes through AgentRuntime.execute()
```

### SECURITY CHECKLIST — M1.9

```
  [ ] FastAPI server: binds to 127.0.0.1 only (never 0.0.0.0)
  [ ] No authentication needed in Phase 1 (single user, localhost)
  [ ] CLI does not display full memory content (only first 100 chars)
  [ ] /status does not display API keys
  [ ] Security scan passes
```

### DEFINITION OF DONE — M1.9

All integration tests pass. The complete TEXT MILESTONE sequence passes:
introduce yourself, create a task, quit, restart, Aether recalls your name
and the task. Graceful shutdown with consolidation works.

### MILESTONE GATE — M1.9

```
GO:   TEXT MILESTONE SEQUENCE PASSES IN FULL. All tests pass.
      Graceful shutdown confirmed. Morning briefing correct.

NO-GO: Any step of the TEXT MILESTONE sequence fails. Any test fails.
       Process does not exit cleanly. Consolidation does not run on quit.
```

---

## MILESTONE M1.10: VOICE SERVICE

### Overview

The VOICE MILESTONE. This is the highest-risk milestone in Phase 1 due to
Windows audio stack complexity. Budget 10 days and expect debugging.
Test audio hardware validation (M0) made this milestone possible at all.

**This milestone has a mandatory audio validation block (Day 1) that
must pass before any voice pipeline code is written.**

### Prerequisites
M1.9 passed. M0 audio tests passed. M1.8 running (events needed).

### Duration
10 working days (Windows audio budget built in)

### Files Created This Milestone

```
services/voice/
├── __init__.py
├── main.py           (process entry point)
├── pipeline.py       (state machine orchestration)
├── stt.py            (faster-whisper STT)
├── tts.py            (Kokoro TTS)
├── vad.py            (Silero VAD)
├── wake_word.py      (Porcupine)
├── server.py         (FastAPI REST API)
└── models.py         (voice-specific data models)
infrastructure/scripts/
└── start.ps1         (UPDATED to start voice service)
tests/integration/
└── test_voice_pipeline.py  (NEW)
```

### Implementation Sequence

**Day 1: Audio Hardware Re-Validation**

```
MANDATORY BEFORE ANY CODE:
Run the audio validation from M0 again on the exact configuration
that will be used in production (target microphone, target speaker):

1. python -c "import sounddevice as sd; sd.query_devices()" → lists audio devices
2. Record test: python -m sounddevice (built-in test)
3. Identify exact device indices for microphone and speaker
4. Document in services/voice/AUDIO_CONFIG.md:
   - Input device: {name} (index: N)
   - Output device: {name} (index: N)
   - Sample rate: 16000
   - Channels: 1 (mono)
   - Known issues: {any issues found in M0}
5. Set audio device indices in config/local.yaml (not default.yaml — device-specific)

If audio fails at this step: DO NOT PROCEED. Debug audio first.
The most common Windows audio failures and resolutions:
- sounddevice import error: reinstall with --force-reinstall
- No input device found: check Windows sound settings → input devices enabled
- Assertion error on record: try different sample rate (44100 → 16000)
```

**Days 2-3: VAD and Wake Word**

```
Step 1: Implement services/voice/vad.py
  - SileroVAD class
  - load_model(): loads silero-vad from torch hub
  - is_speech(audio_chunk: np.ndarray) → float (speech probability)
  - Audio chunk: 30ms at 16kHz = 480 samples
  - Threshold from config.voice.vad_threshold (0.5)
  - Device: cpu (VAD does not need GPU)
  - Test: 5 seconds silence → all chunks < threshold; 5 seconds speech → most > threshold

Step 2: Implement services/voice/wake_word.py
  - PorcupineWakeWord class
  - load(): initializes Porcupine with config.voice.wake_word keyword file
  - process(audio_chunk: np.ndarray) → bool (wake word detected)
  - Access key from config via environment variable
  - Default keyword: "Aether" (requires custom .ppn file from Picovoice console)
  - Fallback: use built-in "computer" keyword if custom file unavailable
  - Frame length: porcupine.frame_length (512 samples at 16kHz)
```

**Days 4-5: STT and TTS**

```
Step 3: Implement services/voice/stt.py
  - FasterWhisperSTT class
  - load_model(): loads faster-whisper medium on cuda (from config.voice.stt_device)
  - transcribe(audio_data: np.ndarray) → TranscriptionResult
  - TranscriptionResult: text, confidence, duration_ms
  - Language locked to "en" (config.voice.stt_language if added)
  - Beam size: 5
  - VAD filter: True (built-in Whisper VAD as secondary filter)
  - GPU memory check before loading: verify sufficient VRAM
    Expected: ~1.5GB for medium model on RTX 4050
  - Load once at startup, reuse for all transcriptions

Step 4: Implement services/voice/tts.py
  - KokoroTTS class
  - load_model(): loads Kokoro with voice from config.voice.tts_voice
  - synthesize(text: str) → np.ndarray (audio samples at 24kHz)
  - play(audio: np.ndarray) → None (plays via sounddevice)
  - synthesize_and_play(text: str) → int (duration_ms)
  - Text preprocessing: strip markdown, limit to 500 chars
  - Device: cpu (frees VRAM for Whisper + Ollama)
```

**Days 6-7: Pipeline State Machine**

```
Step 5: Implement services/voice/pipeline.py
  - VoicePipeline class
  - Implements the state machine from Technical Spec Section 9.2:
    IDLE → WAKE_DETECTED → LISTENING → TRANSCRIBING → TRANSCRIPT_READY → SPEAKING → IDLE
  - State is stored as a class attribute, transitions logged at DEBUG level
  - run(): starts the pipeline loop in a background thread
  - stop(): signals the loop to exit gracefully
  - on_transcript(transcript: str): callback when utterance complete → emits event to Redis
  - on_speak_request(text: str): called when Redis receives voice.speak.request → synthesizes
  - Timeouts:
    LISTENING: max 15 seconds before returning to IDLE
    TRANSCRIPT_READY: max 30 seconds for core response before timeout
  - Silence detection: config.voice.silence_duration_ms (800ms default)
```

**Day 8: REST API and Process Entry Point**

```
Step 6: Implement services/voice/server.py
  - FastAPI app on 127.0.0.1:8001
  - POST /speak: queues text for TTS (non-blocking, returns 202)
  - GET /status: current pipeline state and model load status
  - POST /control: pause/resume/stop/restart_pipeline
  - GET /health: all models loaded, audio devices accessible

Step 7: Implement services/voice/main.py
  - Process entry point (run as: python -m services.voice)
  - Startup sequence from Technical Spec Section 9.6 (Steps 1-11)
  - Subscribes to voice.speak.requested Redis Stream
  - Starts FastAPI server in background thread
  - Emits voice.service.ready event when all components loaded
  - On shutdown: drain any queued TTS, emit voice.service.stopping

Step 8: Update infrastructure/scripts/start.ps1
  - After infrastructure health check:
  - Start aether-core: Start-Process python -ArgumentList "-m aether" ...
  - Start aether-voice: Start-Process python -ArgumentList "-m services.voice" ...
  - Wait for voice health: poll http://localhost:8001/health (max 30s)
  - Print final status with all component health
```

**Days 9-10: Testing and Validation**

```
Step 9: Implement tests/integration/test_voice_pipeline.py
  - test_stt_transcribes_clear_speech (uses pre-recorded .wav file):
    Load test audio file → transcribe → verify accuracy > 90%
    Test file: "hello aether what time is it" (record and save as fixture)
  - test_tts_produces_audio:
    synthesize("Good morning") → np.ndarray with length > 0
  - test_voice_service_health_endpoint:
    curl http://localhost:8001/health → 200

Step 10: VOICE MILESTONE VALIDATION (manual test sequence)
  Run: .\infrastructure\scripts\start.ps1
  Then execute this sequence:
  1. Say "Aether" → acknowledgment sound plays (or state changes to LISTENING)
  2. Say "What time is it?" → response spoken within 3 seconds
  3. Measure end-to-end time (wake word confirmed → first audio byte)
     Target: < 2s. Acceptable: < 3s. NO-GO: > 3s consistently.
  4. Kill voice process (Ctrl+C on voice terminal)
     Verify: aether-core continues running (Redis still accessible)
  5. Restart voice process
     Verify: reconnects to Redis, voice.service.ready event emitted
  6. Full voice conversation with memory:
     Say: "Remember that I'm working on the Aether project"
     Say: "Aether, what am I working on?"
     Verify: Aether responds mentioning the Aether project
```

### BUILD CHECKLIST — M1.10

```
STT:
  [ ] Loads faster-whisper medium on GPU (cuda)
  [ ] Language locked to English (not auto-detect)
  [ ] Single model instance loaded at startup, reused per transcription
  [ ] GPU VRAM verified before load (error if insufficient)

TTS:
  [ ] Kokoro loaded on CPU (not GPU — preserves VRAM for STT + Ollama)
  [ ] Voice from config.voice.tts_voice
  [ ] Text preprocessing: strips markdown, limits length

VAD:
  [ ] Silero VAD on CPU
  [ ] 30ms chunks at 16kHz
  [ ] Threshold from config

Wake Word:
  [ ] Porcupine access key from config/env var
  [ ] Custom "Aether" keyword file OR fallback to "computer"
  [ ] Returns to IDLE if wake word not custom

Pipeline:
  [ ] All 6 state machine states implemented (Technical Spec Section 9.2)
  [ ] LISTENING timeout: 15 seconds
  [ ] TRANSCRIPT_READY timeout: 30 seconds
  [ ] State transitions logged at DEBUG level
  [ ] Silence detection: 800ms (config.voice.silence_duration_ms)

REST API:
  [ ] Binds to 127.0.0.1:8001 (not 0.0.0.0)
  [ ] POST /speak returns 202 (non-blocking)
  [ ] GET /health returns all component statuses
```

### TEST CHECKLIST — M1.10

```
  [ ] uv run pytest tests/integration/test_voice_pipeline.py -v → all 3 tests pass
  [ ] STT accuracy test: test audio transcribes with > 90% word accuracy
  [ ] TTS test: synthesize("hello world") produces audio > 0 length
  [ ] VOICE MILESTONE VALIDATION — all 6 steps pass:
      [ ] Wake word triggers listening state
      [ ] "What time is it?" spoken response within 3 seconds
      [ ] End-to-end latency measured < 3 seconds
      [ ] Voice service crash → core continues
      [ ] Voice service restart → reconnects
      [ ] Memory through voice: store via voice, recall via voice
```

### VALIDATION CHECKLIST — M1.10

```
  [ ] nvidia-smi during voice pipeline: Whisper model in GPU memory (~1.5GB)
  [ ] nvidia-smi during voice pipeline: Kokoro NOT in GPU memory (runs on CPU)
  [ ] Total VRAM used: Whisper + Ollama < 6GB
  [ ] Total RAM used: all processes < 14GB (2GB buffer for Windows overhead)
  [ ] Voice service process: restarts independently without affecting core
  [ ] Audio quality: TTS output intelligible without distortion
  [ ] Voice latency: measured across 10 utterances, median < 2s, max < 3s
```

### ARCHITECTURE COMPLIANCE CHECKLIST — M1.10

```
  [ ] uv run lint-imports → exits 0
  [ ] services/voice/ does not import from aether/ directly
  [ ] Voice service communicates with core via Redis Streams and REST only
  [ ] services/voice/models.py: voice-only models, no shared models with aether/
  [ ] No database imports in services/voice/ (voice service has no database access)
```

### SECURITY CHECKLIST — M1.10

```
  [ ] FastAPI binds to 127.0.0.1:8001 (not 0.0.0.0)
  [ ] Porcupine access key from env var (not hardcoded)
  [ ] Voice input content not stored by voice service (stored by core only)
  [ ] REST API: no authentication in Phase 1 (localhost + single user acceptable)
  [ ] Audio device access: only microphone and speaker (no other devices)
  [ ] Security scan passes
```

### DEFINITION OF DONE — M1.10

The VOICE MILESTONE VALIDATION sequence passes in full. End-to-end voice
latency < 3 seconds measured across 10 utterances. Voice service crash
does not affect core. Memory through voice works. Total VRAM < 6GB.

### MILESTONE GATE — M1.10

```
GO:   VOICE MILESTONE VALIDATION passes all 6 steps. Latency < 3s median.
      VRAM budget within limits. Voice service crash-isolated from core.

NO-GO: Any VOICE MILESTONE step fails. Latency > 3s consistently.
       VRAM exceeds 6GB. Core crashes when voice service crashes.
       STT accuracy < 90% on test audio.
```

---

## MILESTONE M1.11: BACKUP SYSTEM + ARCHITECTURE VALIDATION

### Overview

The final milestone of Phase 1 ensures the system is production-stable,
architecturally compliant, and safe from data loss. No Phase can be
considered complete without backup verification and a full architecture audit.

### Prerequisites
M1.10 passed.

### Duration
3 working days

### Files Created This Milestone

```
infrastructure/scripts/
├── backup.ps1               (NEW)
└── restore.ps1              (NEW)
docs/architecture/
└── audits/
    └── 2025-11-phase1.md    (NEW — first architecture audit)
docs/technical-debt/
└── DEBT_REGISTER.md         (NEW — may be empty if Phase 1 is clean)
CHANGELOG.md                 (NEW — Phase 1 completion record)
```

### Implementation Sequence

**Day 1: Backup and Restore System**

```
Step 1: Implement infrastructure/scripts/backup.ps1
  Sequence:
  1. Check all services healthy (health_check.ps1)
  2. Create backup directory: backups/{YYYYMMDD-HHMMSS}/
  3. Backup SQLite: Copy-Item data/aether.db backups/{ts}/aether_db.sqlite
  4. Backup Qdrant snapshot:
     POST http://localhost:6333/collections/episodic_memory/snapshots
     GET snapshot file → save to backups/{ts}/qdrant_snapshot.tar.gz
  5. Backup Redis: docker compose exec redis redis-cli BGSAVE
     Wait for save to complete: docker compose exec redis redis-cli LASTSAVE
     Copy RDB file from container to backups/{ts}/redis_dump.rdb
  6. Backup config: Copy config/default.yaml, .aether/permissions.yaml
  7. Generate manifest: backups/{ts}/backup_manifest.json
     {timestamp, file_sizes, sha256_checksums, verified: false}
  8. VERIFY each file:
     - SQLite: open with sqlite3, run SELECT COUNT(*) FROM memories
     - Qdrant snapshot: check file size > 0
     - Redis RDB: check file size > 0
  9. Update manifest: {verified: true} (only if ALL verifications pass)
  10. Print: "Backup complete. Verified: {timestamp}. Size: {total_size}"
  11. If any verification fails: print error, leave verified: false, exit 1

Step 2: Implement infrastructure/scripts/restore.ps1
  Parameters: -BackupTimestamp "YYYYMMDD-HHMMSS"
  Sequence:
  1. Verify backup/{ts}/backup_manifest.json exists with verified: true
  2. Stop all services (stop.ps1 — preserves volumes)
  3. Restore SQLite: Copy-Item backups/{ts}/aether_db.sqlite data/aether.db
  4. Restore Redis: copy RDB into Redis volume, restart Redis
  5. Restore Qdrant: start Qdrant, POST snapshot restore API
  6. Start all services (start.ps1)
  7. Health check: health_check.ps1
  8. Verify restore: SELECT COUNT(*) FROM memories must match pre-restore count
  9. Print: "Restore complete. Verified: {n} memories restored."
```

**Day 2: Architecture Audit**

```
Step 3: Full Architecture Audit
  Read: V1_FOUNDATION_ARCHITECTURE.md — every rule
  Read: V1_TECHNICAL_SPECIFICATION.md — every module spec
  Read: ARCHITECTURE_RULES.md — every boundary rule
  For each module, verify:
  a. Public API in __init__.py matches specification
  b. No private submodule imports from outside the module
  c. All locked contracts match their specification exactly

  Run all automated checks:
  uv run lint-imports → must be zero violations
  uv run mypy aether/ services/ --strict → must be zero errors
  grep audit for all boundary violations:
    - LLM provider imports outside llm/_providers/
    - Database imports outside memory/_stores/
    - Hardcoded model names outside llm/
    - Hardcoded connection strings anywhere
    - print() in any production file

  Document findings in docs/architecture/audits/2025-11-phase1.md:
  - Date of audit
  - Modules reviewed
  - Boundary violations found: {N} (must be 0 for GO)
  - Contract compliance: PASS/FAIL per module
  - Overall verdict: ARCHITECTURALLY COMPLIANT / DEFICIENCIES FOUND

Step 4: Technical Debt Assessment
  Review all code for any debt that should be registered.
  Common Phase 1 debt to check:
  - Any performance shortcuts in retrieval?
  - Any consolidation edge cases not handled?
  - Any error paths that return generic errors instead of specific ones?
  - Any configuration values that should be configurable but are not?
  Record each item in docs/technical-debt/DEBT_REGISTER.md with priority.
  P1 debt: must be resolved before Phase 1 GO decision.
```

**Day 3: Final Validation and CHANGELOG**

```
Step 5: Backup → Restore verification test
  MANDATORY:
  1. Run backup.ps1 → verify manifest shows verified: true
  2. Delete data/aether.db
  3. docker compose exec redis redis-cli FLUSHALL (DEV ONLY — not production)
  4. Run restore.ps1 -BackupTimestamp {ts}
  5. Start Aether
  6. Ask "What's my name?" → if previously told, should recall
  7. List tasks → previously created tasks should be present
  This is the definitive proof that backup and restore work.

Step 6: Write CHANGELOG.md
  Phase 1 entry must include:
  - All 12 milestones completed (M0 through M1.11)
  - TEXT MILESTONE: date achieved
  - VOICE MILESTONE: date achieved
  - Architecture audit: date, result
  - Voice latency: median measured value
  - Memory verification: cross-session test result
  - Known limitations and Phase 2 preview
```

### BUILD CHECKLIST — M1.11

```
Backup:
  [ ] backup.ps1: creates all 5 backup files
  [ ] backup.ps1: manifest includes sha256 checksums
  [ ] backup.ps1: verified: true only when ALL files verified
  [ ] backup.ps1: exit 1 if any verification fails
  [ ] restore.ps1: refuses to restore from unverified backup (verified: false)
  [ ] restore.ps1: verifies memory count after restore

Architecture Audit:
  [ ] Audit document created and committed
  [ ] Zero boundary violations documented
  [ ] All module public APIs verified against specification
  [ ] All locked contracts verified (MemoryAPI, LLMRouter, Tool interface, Events)

Technical Debt:
  [ ] DEBT_REGISTER.md created (may be empty — that is acceptable)
  [ ] All P1 debt items resolved before this milestone completes
  [ ] No P2 debt items without resolution plans

CHANGELOG:
  [ ] Both milestones (TEXT, VOICE) dated and documented
  [ ] Voice latency recorded
  [ ] Architecture audit verdict recorded
```

### TEST CHECKLIST — M1.11

```
  [ ] backup.ps1 → creates verified backup
  [ ] restore.ps1 → restores from backup with data intact
  [ ] After restore: "What's my name?" → Aether recalls name from backup
  [ ] After restore: /tasks → tasks from backup present
  [ ] uv run lint-imports → exits 0 (zero violations)
  [ ] uv run mypy aether/ services/ --strict → exits 0 (zero errors)
  [ ] uv run pytest tests/ → all tests pass
  [ ] Security scan → zero forbidden patterns
  [ ] Architecture audit verdict: ARCHITECTURALLY COMPLIANT
```

### VALIDATION CHECKLIST — M1.11

```
  [ ] Backup → delete data → restore → memories intact (full test)
  [ ] backup_manifest.json: verified: true for the test backup
  [ ] Architecture audit document committed to repository
  [ ] Zero P1 technical debt items open
  [ ] CHANGELOG.md written and accurate
  [ ] start.ps1 → health_check.ps1 → both show all healthy
```

### ARCHITECTURE COMPLIANCE CHECKLIST — M1.11

```
  [ ] Full architecture audit passed (documented in audit file)
  [ ] uv run lint-imports → zero violations
  [ ] Every module's __init__.py matches specification
  [ ] Every locked contract matches specification exactly
  [ ] No boundary violation found in manual audit
```

### SECURITY CHECKLIST — M1.11

```
  [ ] Backup files stored in backups/ (gitignored — never committed)
  [ ] Backup files do not contain plaintext API keys
  [ ] Restore script validates backup integrity before applying
  [ ] Security scan: zero forbidden patterns across entire codebase
  [ ] No print() in any production file: grep -r "print(" aether/ services/ → zero
```

### DEFINITION OF DONE — M1.11

Backup and restore cycle verified with data intact. Architecture audit passed
with zero violations. All tests pass. Technical debt registered. CHANGELOG written.
Zero import boundary violations. Zero mypy errors.

### MILESTONE GATE — M1.11

```
GO:   Backup → restore → data intact. Architecture audit: COMPLIANT.
      Zero lint-imports violations. Zero mypy errors. All tests pass.
      Zero P1 debt items. CHANGELOG written.

NO-GO: Restore fails. Architecture audit finds violations. Any lint-imports
       violation. Any mypy error. Any P1 debt item unresolved.
```

---

## PHASE 1 GO/NO-GO DECISION

### The Phase 1 Completion Gate

After M1.11 passes, the Phase 1 GO/NO-GO decision is made. This decision
must be made explicitly and documented before Phase 2 planning begins.

### GO Criteria — ALL must be true

```
MILESTONE COMPLETION:
  [ ] M0: Environment Validation — PASSED
  [ ] M1.0: Repository Foundation — PASSED
  [ ] M1.1: Docker Infrastructure — PASSED
  [ ] M1.2: Configuration + Logging + Events — PASSED
  [ ] M1.3: LLM Router + Budget — PASSED
  [ ] M1.4: SQLite Schema — PASSED
  [ ] M1.5: Memory System — PASSED
  [ ] M1.6: Tool System + Task Manager — PASSED
  [ ] M1.7: Agent Runtime + Conversation Agent — PASSED
  [ ] M1.8: Session Manager + Morning Briefing — PASSED
  [ ] M1.9: CLI Interface — PASSED
  [ ] M1.10: Voice Service — PASSED
  [ ] M1.11: Backup + Architecture Validation — PASSED

DEFINING TESTS:
  [ ] TEXT MILESTONE: Complete sequence passed (name remembered across sessions)
  [ ] VOICE MILESTONE: Complete sequence passed (6 steps)
  [ ] CRITICAL MEMORY TEST: Fact stored → infrastructure restart → fact recalled

QUALITY GATES:
  [ ] uv run lint-imports → zero violations
  [ ] uv run mypy aether/ services/ --strict → zero errors
  [ ] uv run ruff check . → zero warnings
  [ ] uv run pytest tests/ → all tests pass (unit + integration + contract + architecture)
  [ ] Security scan → zero forbidden patterns

ARCHITECTURE:
  [ ] Architecture audit: ARCHITECTURALLY COMPLIANT (all modules)
  [ ] No locked contracts deviate from specification
  [ ] No P1 technical debt items open

OPERATIONAL:
  [ ] Voice latency: median < 2 seconds, no single call > 3 seconds
  [ ] System ran for 3 consecutive days without unrecoverable crash
  [ ] Backup → restore → data intact (verified manually)
  [ ] start.ps1 → stop.ps1 → start.ps1 cycle works without data loss

DOCUMENTATION:
  [ ] CHANGELOG.md written with Phase 1 completion entry
  [ ] Architecture audit committed
  [ ] Technical debt register current
  [ ] All governance documents in docs/architecture/ and current
```

### NO-GO Triggers — ANY one triggers NO-GO

```
  Any milestone gate in the NO-GO state
  TEXT MILESTONE sequence fails on any step
  VOICE MILESTONE sequence fails on any step
  Any lint-imports violation
  Any mypy --strict error
  Any test failure
  Architecture audit finds any violation
  Any P1 technical debt item unresolved
  Voice latency > 3 seconds median
  Backup restore fails
  Any forbidden pattern found in codebase
```

### The GO Decision Statement

When all GO criteria are met:

```
PHASE 1 GO DECISION

Date: {YYYY-MM-DD}
All 13 milestone gates: PASSED
TEXT MILESTONE: ACHIEVED on {date}
VOICE MILESTONE: ACHIEVED on {date}
Architecture audit: ARCHITECTURALLY COMPLIANT
Technical debt: {N} P2 items, {N} P3 items, 0 P1 items
Voice latency: median {N}ms across 10 utterances
All quality gates: PASSED

PHASE 1 IS COMPLETE.
PHASE 2 PLANNING MAY BEGIN.

Phase 2 first action: Read and review V1_TECHNICAL_SPECIFICATION.md Phase 2
section before writing any Phase 2 code.
```

---

## APPENDIX A: PHASE 1 TOTAL FILE INVENTORY

Every file created in Phase 1. If a file appears in this list and does not
exist at Phase 1 completion, Phase 1 is not complete.

```
Repository root:
  pyproject.toml, .env.example, .gitignore, .pre-commit-config.yaml,
  README.md, CHANGELOG.md

.github/workflows/:
  ci.yml, architecture-check.yml

config/:
  default.yaml

.aether/:
  permissions.yaml

docs/architecture/:
  ARCHITECTURE_RULES.md, AI_GENERATION_RULES_V2.md, V1_TECHNICAL_SPECIFICATION.md,
  V1_FOUNDATION_ARCHITECTURE.md, MASTER_BLUEPRINT.md, CRITICAL_AUDIT.md,
  AI_SKILLS_INTEGRATION.md
docs/architecture/decisions/:
  ADR-001 through ADR-009, ADR-010, ADR-011
docs/architecture/audits/:
  2025-11-phase1.md
docs/phases/:
  PHASE_1_FOUNDATION_IMPLEMENTATION_PLAN.md (this document)
docs/technical-debt/:
  DEBT_REGISTER.md
docs/environments/:
  windows-validation-log.md

aether/:
  __init__.py, py.typed, __main__.py
aether/core/:
  __init__.py, config.py, logging.py, events.py, kernel.py
aether/llm/:
  __init__.py, router.py, budget.py, _embedding.py, _models.py
aether/llm/_providers/:
  __init__.py, base.py, anthropic_provider.py, google_provider.py, ollama_provider.py
aether/memory/:
  __init__.py, api.py, models.py
aether/memory/_stores/:
  __init__.py, sqlite_store.py, vector_store.py
aether/memory/_retrieval/:
  __init__.py, hybrid.py, reranker.py
aether/memory/_consolidation/:
  __init__.py, pipeline.py, extractor.py
aether/tools/:
  __init__.py, base.py, registry.py
aether/tools/_implementations/:
  __init__.py, datetime_tools.py, search_tools.py, task_tools.py
aether/agents/:
  __init__.py, base.py, runtime.py
aether/agents/_implementations/:
  __init__.py, conversation.py
aether/tasks/:
  __init__.py, manager.py, models.py
aether/session/:
  __init__.py, manager.py, startup.py, models.py
aether/interfaces/:
  __init__.py, cli.py, api.py

services/:
  __init__.py
services/voice/:
  __init__.py, main.py, pipeline.py, stt.py, tts.py, vad.py, wake_word.py,
  server.py, models.py, AUDIO_CONFIG.md

migrations/:
  env.py, script.py.mako
migrations/versions/:
  001_initial_schema.py

infrastructure/docker/:
  docker-compose.yml
infrastructure/docker/redis/:
  redis.conf
infrastructure/docker/qdrant/:
  config.yaml
infrastructure/scripts/:
  start.ps1, stop.ps1, health_check.ps1, backup.ps1, restore.ps1
scripts/:
  validate_environment.ps1

tests/:
  conftest.py
tests/unit/:
  test_config.py, test_logging.py, test_events.py, test_llm_router.py,
  test_llm_budget.py, test_migrations.py, test_memory_api.py,
  test_memory_retrieval.py, test_tool_registry.py, test_tool_implementations.py,
  test_task_manager.py, test_base_agent.py, test_agent_runtime.py,
  test_session_manager.py
tests/integration/:
  test_config_events_integration.py, test_memory_pipeline.py,
  test_conversation_flow.py, test_consolidation.py, test_event_flow.py,
  test_task_workflow.py, test_voice_pipeline.py
tests/contracts/:
  test_llm_router_contract.py, test_memory_api_contract.py,
  test_tool_interface_contract.py, test_agent_interface_contract.py,
  test_event_schema_contract.py
tests/architecture/:
  test_import_boundaries.py

data/.gitkeep
logs/.gitkeep
backups/.gitkeep
```

---

## APPENDIX B: PHASE 1 DEVELOPMENT CALENDAR

```
WEEK 1 (Days 1-5):
  Day 0:  M0 — Environment Validation
  Days 1-2: M1.0 — Repository Foundation
  Days 3-4: M1.1 — Docker Infrastructure (parallel with M1.2)
  Days 5-7: M1.2 — Config + Logging + Events

WEEK 2 (Days 6-10):
  Days 8-10: M1.3 — LLM Router + Budget
  Day 11:   M1.4 — SQLite Schema

WEEK 3 (Days 12-16):
  Days 12-16: M1.5 — Memory System

WEEK 4 (Days 17-24):
  Days 17-19: M1.6 — Tool System + Task Manager
  Days 20-24: M1.7 — Agent Runtime + Conversation Agent

WEEK 5 (Days 25-30):
  Days 25-27: M1.8 — Session Manager + Morning Briefing
  Days 28-30: M1.9 — CLI Interface [TEXT MILESTONE]

WEEKS 6-8 (Days 31-40):
  Days 31-40: M1.10 — Voice Service [VOICE MILESTONE]

WEEK 9 (Days 41-43):
  Days 41-43: M1.11 — Backup + Architecture Validation

WEEK 10 (Days 44-47):
  Phase 1 GO/NO-GO Decision and Documentation
  Phase 2 Planning Begins (after GO decision)
```

---

*Document Version: 1.0*
*Status: APPROVED FOR EXECUTION*
*Phase: 1 of 10 — Foundation*
*Target Hardware: Intel i7-13700HX · RTX 4050 6GB · 16GB DDR5 · Windows 11*
*Review: At each milestone gate and at Phase 1 GO/NO-GO decision*
*Owner: Principal Systems Engineer*
*Last Updated: 2025-11-15*
