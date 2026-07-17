# Aether AI OS — Changelog

## [0.2.0] - Phase 1 Complete

### Added

- **[M1.11]** Backup & Restore system (`backup.ps1`, `restore.ps1`), architecture auditing, and performance baselining. — 2026-07-03

## [0.1.0] - Phase 1 Foundation

### Added

- **[M1.10]** Voice Service [VOICE MILESTONE] (SileroVAD, Porcupine Wake Word, FasterWhisper STT, Kokoro TTS, distinct Python process). — 2026-07-03
- **[M1.9]** CLI Interface (FastAPI internal server, Rich CLI, TEXT MILESTONE achieved). — 2026-07-02
- **[M1.8]** Session Manager + Morning Briefing (Context lifecycle, Redis caching, async episodic consolidation). — 2026-07-02
- **[M1.7]** Agent Runtime + Conversation Agent (State machine, multi-turn conversations, LLM integration) — 2026-07-01
- **[M1.6]** Task Manager and generic Tool System implemented. — 2026-07-01
- **[M1.5]** Memory System (Hybrid vector/keyword search, reranking, and auto-consolidation). — 2026-07-01
- **[M1.4]** Core SQLite memory schema and FTS5 indexing with full migrations. — 2026-06-30
- **[M1.3]** LLM routing engine with budget constraint mechanisms. — 2026-06-30
- **[M1.2]** Central configuration (`pydantic-settings`), structured JSON logging (`structlog`), global exception hierarchy, and central Event Bus (Redis Streams). — 2026-06-29
- **[M1.1]** Docker Compose infrastructure (Redis 7, Qdrant) with persistent volumes and operational PowerShell scripts. — 2026-06-29
- **[M1.0]** Project tooling foundation (`pyproject.toml`), pre-commit hooks (ruff, mypy, import-linter), CI workflows. — 2026-06-29
- **[M0]** Repository skeleton and Environment validation scripts. — 2026-06-29
