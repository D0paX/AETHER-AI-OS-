"""SQLAlchemy ORM models for Aether OS Phase 1 database schema.

These models exactly map to the SQLite schema tables from the Tech Spec Section 3.2.
They are marked internal to the memory module and are not exposed externally.
All primary keys are UUIDv7 strings. All timestamps are ISO 8601 UTC strings.
All JSON fields are stored as JSON-encoded strings.
"""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict
from sqlalchemy import Column, Float, ForeignKey, Integer, String, Text, text
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

# Standard SQLite UTC timestamp generation
UTC_NOW = text("strftime('%Y-%m-%dT%H:%M:%fZ', 'now')")


class SystemKVModel(Base):
    """Key-value store for system-wide configuration and tracking."""

    __tablename__ = "system_kv"

    key = Column(String, primary_key=True)
    value = Column(Text, nullable=False)
    updated_at = Column(String, nullable=False, server_default=UTC_NOW)


class ConversationModel(Base):
    """A distinct user interaction session (voice or text)."""

    __tablename__ = "conversations"

    id = Column(String, primary_key=True)
    started_at = Column(String, nullable=False, server_default=UTC_NOW)
    ended_at = Column(String, nullable=True)
    mode = Column(String, nullable=False, server_default="voice")
    title = Column(String, nullable=True)
    summary = Column(Text, nullable=True)
    message_count = Column(Integer, nullable=False, server_default="0")
    meta = Column(Text, nullable=False, server_default="{}")


class MemoryModel(Base):
    """Vector-embedded episodic and semantic memories."""

    __tablename__ = "memories"

    id = Column(String, primary_key=True)
    content = Column(Text, nullable=False)
    memory_type = Column(String, nullable=False)
    importance = Column(Float, nullable=False, server_default="0.5")
    confidence = Column(Float, nullable=False, server_default="0.8")
    source = Column(String, nullable=False)
    source_id = Column(String, nullable=True)
    created_at = Column(String, nullable=False, server_default=UTC_NOW)
    last_accessed_at = Column(String, nullable=False, server_default=UTC_NOW)
    access_count = Column(Integer, nullable=False, server_default="0")
    expiry_at = Column(String, nullable=True)
    tags = Column(Text, nullable=False, server_default="[]")
    entities = Column(Text, nullable=False, server_default="[]")
    meta = Column(Text, nullable=False, server_default="{}")


class TaskModel(Base):
    """Agentic task tracking and execution queue."""

    __tablename__ = "tasks"

    id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String, nullable=False, server_default="pending")
    priority = Column(String, nullable=False, server_default="medium")
    category = Column(String, nullable=True)
    due_at = Column(String, nullable=True)
    created_at = Column(String, nullable=False, server_default=UTC_NOW)
    updated_at = Column(String, nullable=False, server_default=UTC_NOW)
    completed_at = Column(String, nullable=True)
    parent_task_id = Column(String, ForeignKey("tasks.id"), nullable=True)
    agent_type = Column(String, nullable=True)
    meta = Column(Text, nullable=False, server_default="{}")


class MessageModel(Base):
    """Individual messages within a conversation (user, assistant, tool, system)."""

    __tablename__ = "messages"

    id = Column(String, primary_key=True)
    conversation_id = Column(
        String, ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False
    )
    role = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    tool_name = Column(String, nullable=True)
    tool_call_id = Column(String, nullable=True)
    token_count = Column(Integer, nullable=True)
    created_at = Column(String, nullable=False, server_default=UTC_NOW)
    meta = Column(Text, nullable=False, server_default="{}")


class ToolExecutionModel(Base):
    """Telemetry and result tracking for individual tool executions."""

    __tablename__ = "tool_executions"

    id = Column(String, primary_key=True)
    tool_name = Column(String, nullable=False)
    agent_name = Column(String, nullable=False)
    session_id = Column(String, nullable=True)
    input_preview = Column(Text, nullable=False)
    output_preview = Column(Text, nullable=True)
    success = Column(Integer, nullable=False)
    error_message = Column(Text, nullable=True)
    duration_ms = Column(Integer, nullable=False)
    created_at = Column(String, nullable=False, server_default=UTC_NOW)
    meta = Column(Text, nullable=False, server_default="{}")


class AgentRunModel(Base):
    """Telemetry and lifecycle tracking for a specific agent execution."""

    __tablename__ = "agent_runs"

    id = Column(String, primary_key=True)
    agent_name = Column(String, nullable=False)
    task_description = Column(Text, nullable=False)
    session_id = Column(String, nullable=True)
    status = Column(String, nullable=False, server_default="running")
    iteration_count = Column(Integer, nullable=False, server_default="0")
    tool_calls_count = Column(Integer, nullable=False, server_default="0")
    memory_reads_count = Column(Integer, nullable=False, server_default="0")
    llm_tokens_used = Column(Integer, nullable=False, server_default="0")
    llm_cost_usd = Column(Float, nullable=False, server_default="0.0")
    started_at = Column(String, nullable=False, server_default=UTC_NOW)
    completed_at = Column(String, nullable=True)
    error_message = Column(Text, nullable=True)
    result_preview = Column(Text, nullable=True)
    meta = Column(Text, nullable=False, server_default="{}")


class LLMCostModel(Base):
    """Financial tracking of individual LLM provider calls."""

    __tablename__ = "llm_costs"

    id = Column(String, primary_key=True)
    provider = Column(String, nullable=False)
    model = Column(String, nullable=False)
    tier = Column(String, nullable=False)
    prompt_tokens = Column(Integer, nullable=False)
    completion_tokens = Column(Integer, nullable=False)
    cost_usd = Column(Float, nullable=False)
    agent_run_id = Column(String, ForeignKey("agent_runs.id"), nullable=True)
    created_at = Column(String, nullable=False, server_default=UTC_NOW)


# =============================================================================
# DOMAIN MODELS (Pydantic)
# =============================================================================


class MemoryType(str, Enum):
    """The type of a memory."""

    FACT = "FACT"
    EPISODE = "EPISODE"
    SKILL = "SKILL"
    PREFERENCE = "PREFERENCE"


class MemorySource(str, Enum):
    """The source of a memory."""

    CONVERSATION = "CONVERSATION"
    DOCUMENT = "DOCUMENT"
    AGENT = "AGENT"
    USER = "USER"


class MemoryFilter(BaseModel):
    """Filtering criteria for memory search and retrieval."""

    memory_types: list[MemoryType] | None = None
    min_importance: float = 0.0
    min_confidence: float = 0.0
    source: MemorySource | None = None
    tags: list[str] | None = None
    entities: list[str] | None = None
    created_after: datetime | None = None
    created_before: datetime | None = None


class MemoryRecord(BaseModel):
    """An individual retrieved memory record."""

    model_config = ConfigDict(frozen=True, strict=True)

    id: str
    content: str
    memory_type: MemoryType
    importance: float
    confidence: float
    source: MemorySource
    tags: list[str]
    entities: list[str]
    created_at: datetime
    last_accessed_at: datetime
    access_count: int
    similarity_score: float | None = None


class ContextPackage(BaseModel):
    """A formatted package of retrieved context ready for LLM consumption."""

    model_config = ConfigDict(frozen=True)

    memories: list[MemoryRecord]
    total_found: int
    token_estimate: int
    formatted_context: str
    retrieval_query: str
    retrieval_duration_ms: int


class ConsolidationReport(BaseModel):
    """Report generated after a session consolidation run."""

    model_config = ConfigDict(frozen=True)

    session_id: str
    memories_created: int
    facts_extracted: int
    duration_ms: int
    llm_cost_usd: float
    skipped: bool = False
    skip_reason: str | None = None
