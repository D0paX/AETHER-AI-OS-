# Aether AI OS — Changelog

## v0.1.0-bootstrap — 2025-11-15

### Added
- Repository skeleton (Bootstrap)
- Environment validation scripts (M0)
- Project tooling foundation (M1.0)
- pyproject.toml with all Phase 1 dependencies
- pre-commit hooks: ruff, mypy, import-linter, forbidden-pattern scan
- CI workflows: lint, format, type-check, architecture, security, unit-tests
- Alembic migration infrastructure (stub)

### [0.1.0] - Phase 1 Foundation

- **[M1.6]** Task Manager and generic Tool System implemented.
- **[M1.4]** Core SQLite memory schema and FTS5 indexing with full migrations.
- **[M1.3]** LLM routing engine with budget constraint mechanisms.
- **[M1.2]** Type-safe config injection and centralized async event bus.

## v0.1.0-m1.1 — 2026-06-29

### Added
- Docker Compose infrastructure (Redis 7, Qdrant)
- Redis configuration with AOF persistence
- Qdrant configuration with telemetry disabled
- start.ps1, stop.ps1, health_check.ps1 operational scripts

### Notes
- Application implementation begins with M1.1 (Docker Infrastructure)

## v0.1.0-m1.2 — 2026-06-29

### Added
- Central configuration using `pydantic-settings` (`AetherConfig`, `get_config`)
- Structured JSON logging using `structlog` (`configure_logging`, `get_logger`)
- Global exception hierarchy (`AetherError` and 19 specific exception classes)
- Central Event Bus using Redis Streams (`AetherEvent`, `EventBus`)
