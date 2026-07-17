"""Initial Phase 1 schema: conversations, messages, memories, tasks, tool_executions,
agent_runs, llm_costs, system_kv with FTS5 and triggers.

Dialect-aware since M2.1 (developer-approved amendment): on SQLite this
migration is behaviorally identical to its original Phase 1 form; on
PostgreSQL it creates the same tables, indexes, and seed data using
PostgreSQL-native timestamp defaults and trigger syntax, and no FTS5 objects
(keyword search on PostgreSQL is provided by pg_trgm in revision
002_postgres_fts).

Revision ID: 001_initial_schema
Revises:
Create Date: 2026-06-30 13:00:00.000000

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    dialect = op.get_bind().dialect.name
    # UTC ISO-8601 timestamp default with millisecond precision, per dialect.
    # Both expressions produce the same "YYYY-MM-DDTHH:MM:SS.mmmZ" text format.
    utc_now_default = (
        sa.text("strftime('%Y-%m-%dT%H:%M:%fZ', 'now')")
        if dialect == "sqlite"
        else sa.text("to_char(now() AT TIME ZONE 'utc', 'YYYY-MM-DD\"T\"HH24:MI:SS.MS\"Z\"')")
    )

    # STEP 1: Create base tables
    op.create_table(
        "system_kv",
        sa.Column("key", sa.Text(), nullable=False),
        sa.Column("value", sa.Text(), nullable=False),
        sa.Column(
            "updated_at",
            sa.Text(),
            server_default=utc_now_default,
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("key"),
    )

    op.create_table(
        "conversations",
        sa.Column("id", sa.Text(), nullable=False),
        sa.Column(
            "started_at",
            sa.Text(),
            server_default=utc_now_default,
            nullable=False,
        ),
        sa.Column("ended_at", sa.Text(), nullable=True),
        sa.Column("mode", sa.Text(), server_default="voice", nullable=False),
        sa.Column("title", sa.Text(), nullable=True),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("message_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("meta", sa.Text(), server_default="{}", nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "memories",
        sa.Column("id", sa.Text(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("memory_type", sa.Text(), nullable=False),
        sa.Column("importance", sa.Float(), server_default="0.5", nullable=False),
        sa.Column("confidence", sa.Float(), server_default="0.8", nullable=False),
        sa.Column("source", sa.Text(), nullable=False),
        sa.Column("source_id", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.Text(),
            server_default=utc_now_default,
            nullable=False,
        ),
        sa.Column(
            "last_accessed_at",
            sa.Text(),
            server_default=utc_now_default,
            nullable=False,
        ),
        sa.Column("access_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("expiry_at", sa.Text(), nullable=True),
        sa.Column("tags", sa.Text(), server_default="[]", nullable=False),
        sa.Column("entities", sa.Text(), server_default="[]", nullable=False),
        sa.Column("meta", sa.Text(), server_default="{}", nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "tasks",
        sa.Column("id", sa.Text(), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", sa.Text(), server_default="pending", nullable=False),
        sa.Column("priority", sa.Text(), server_default="medium", nullable=False),
        sa.Column("category", sa.Text(), nullable=True),
        sa.Column("due_at", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.Text(),
            server_default=utc_now_default,
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.Text(),
            server_default=utc_now_default,
            nullable=False,
        ),
        sa.Column("completed_at", sa.Text(), nullable=True),
        sa.Column("parent_task_id", sa.Text(), sa.ForeignKey("tasks.id"), nullable=True),
        sa.Column("agent_type", sa.Text(), nullable=True),
        sa.Column("meta", sa.Text(), server_default="{}", nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    # STEP 2: Create FK-dependent tables
    op.create_table(
        "messages",
        sa.Column("id", sa.Text(), nullable=False),
        sa.Column(
            "conversation_id",
            sa.Text(),
            sa.ForeignKey("conversations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("role", sa.Text(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("tool_name", sa.Text(), nullable=True),
        sa.Column("tool_call_id", sa.Text(), nullable=True),
        sa.Column("token_count", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            sa.Text(),
            server_default=utc_now_default,
            nullable=False,
        ),
        sa.Column("meta", sa.Text(), server_default="{}", nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "tool_executions",
        sa.Column("id", sa.Text(), nullable=False),
        sa.Column("tool_name", sa.Text(), nullable=False),
        sa.Column("agent_name", sa.Text(), nullable=False),
        sa.Column("session_id", sa.Text(), nullable=True),
        sa.Column("input_preview", sa.Text(), nullable=False),
        sa.Column("output_preview", sa.Text(), nullable=True),
        sa.Column("success", sa.Integer(), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("duration_ms", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.Text(),
            server_default=utc_now_default,
            nullable=False,
        ),
        sa.Column("meta", sa.Text(), server_default="{}", nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "agent_runs",
        sa.Column("id", sa.Text(), nullable=False),
        sa.Column("agent_name", sa.Text(), nullable=False),
        sa.Column("task_description", sa.Text(), nullable=False),
        sa.Column("session_id", sa.Text(), nullable=True),
        sa.Column("status", sa.Text(), server_default="running", nullable=False),
        sa.Column("iteration_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("tool_calls_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("memory_reads_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("llm_tokens_used", sa.Integer(), server_default="0", nullable=False),
        sa.Column("llm_cost_usd", sa.Float(), server_default="0.0", nullable=False),
        sa.Column(
            "started_at",
            sa.Text(),
            server_default=utc_now_default,
            nullable=False,
        ),
        sa.Column("completed_at", sa.Text(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("result_preview", sa.Text(), nullable=True),
        sa.Column("meta", sa.Text(), server_default="{}", nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "llm_costs",
        sa.Column("id", sa.Text(), nullable=False),
        sa.Column("provider", sa.Text(), nullable=False),
        sa.Column("model", sa.Text(), nullable=False),
        sa.Column("tier", sa.Text(), nullable=False),
        sa.Column("prompt_tokens", sa.Integer(), nullable=False),
        sa.Column("completion_tokens", sa.Integer(), nullable=False),
        sa.Column("cost_usd", sa.Float(), nullable=False),
        sa.Column("agent_run_id", sa.Text(), sa.ForeignKey("agent_runs.id"), nullable=True),
        sa.Column(
            "created_at",
            sa.Text(),
            server_default=utc_now_default,
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # STEP 3: Create all indexes
    indexes = [
        "CREATE INDEX idx_conversations_started_at ON conversations(started_at)",
        "CREATE INDEX idx_messages_conversation_id ON messages(conversation_id)",
        "CREATE INDEX idx_messages_created_at ON messages(created_at)",
        "CREATE INDEX idx_messages_role ON messages(role)",
        "CREATE INDEX idx_memories_type ON memories(memory_type)",
        "CREATE INDEX idx_memories_importance ON memories(importance DESC)",
        "CREATE INDEX idx_memories_created_at ON memories(created_at DESC)",
        "CREATE INDEX idx_memories_last_accessed ON memories(last_accessed_at DESC)",
        "CREATE INDEX idx_memories_source ON memories(source)",
        "CREATE INDEX idx_tasks_status ON tasks(status)",
        "CREATE INDEX idx_tasks_priority ON tasks(priority)",
        "CREATE INDEX idx_tasks_due_at ON tasks(due_at)",
        "CREATE INDEX idx_tasks_updated ON tasks(updated_at DESC)",
        "CREATE INDEX idx_tool_exec_tool_name ON tool_executions(tool_name)",
        "CREATE INDEX idx_tool_exec_created_at ON tool_executions(created_at DESC)",
        "CREATE INDEX idx_tool_exec_session ON tool_executions(session_id)",
        "CREATE INDEX idx_agent_runs_agent_name ON agent_runs(agent_name)",
        "CREATE INDEX idx_agent_runs_status ON agent_runs(status)",
        "CREATE INDEX idx_agent_runs_started ON agent_runs(started_at DESC)",
        "CREATE INDEX idx_agent_runs_session ON agent_runs(session_id)",
        "CREATE INDEX idx_llm_costs_created_at ON llm_costs(created_at DESC)",
        "CREATE INDEX idx_llm_costs_provider ON llm_costs(provider)",
    ]
    for idx_sql in indexes:
        op.execute(idx_sql)

    # STEP 4: Dialect-specific search and trigger objects
    if dialect == "sqlite":
        _create_sqlite_fts_and_triggers()
    else:
        _create_postgres_triggers()

    # STEP 5: Pre-populate system_kv
    op.execute("""
        INSERT INTO system_kv (key, value) VALUES
          ('aether.version', '"1.0.0"'),
          ('aether.embedding_dimension', '1024'),
          ('aether.embedding_model', '"BAAI/bge-large-en-v1.5"'),
          ('aether.first_run_at', 'null'),
          ('aether.total_sessions', '0')
    """)


def _create_sqlite_fts_and_triggers() -> None:
    """SQLite-only FTS5 virtual tables and sync/update triggers (original Phase 1 DDL)."""
    op.execute("""
        CREATE VIRTUAL TABLE memories_fts USING fts5(
            content, tags, entities,
            content='memories', content_rowid='rowid'
        )
    """)
    op.execute("""
        CREATE TRIGGER memories_ai AFTER INSERT ON memories BEGIN
          INSERT INTO memories_fts(rowid, content, tags, entities)
          VALUES (new.rowid, new.content, new.tags, new.entities);
        END;
    """)
    op.execute("""
        CREATE TRIGGER memories_ad AFTER DELETE ON memories BEGIN
          INSERT INTO memories_fts(memories_fts, rowid, content, tags, entities)
          VALUES('delete', old.rowid, old.content, old.tags, old.entities);
        END;
    """)
    op.execute("""
        CREATE TRIGGER memories_au AFTER UPDATE ON memories BEGIN
          INSERT INTO memories_fts(memories_fts, rowid, content, tags, entities)
          VALUES('delete', old.rowid, old.content, old.tags, old.entities);
          INSERT INTO memories_fts(rowid, content, tags, entities)
          VALUES (new.rowid, new.content, new.tags, new.entities);
        END;
    """)

    op.execute("""
        CREATE VIRTUAL TABLE tasks_fts USING fts5(
            title, description,
            content='tasks', content_rowid='rowid'
        )
    """)
    op.execute("""
        CREATE TRIGGER tasks_ai AFTER INSERT ON tasks BEGIN
          INSERT INTO tasks_fts(rowid, title, description)
          VALUES (new.rowid, new.title, new.description);
        END;
    """)
    op.execute("""
        CREATE TRIGGER tasks_ad AFTER DELETE ON tasks BEGIN
          INSERT INTO tasks_fts(tasks_fts, rowid, title, description)
          VALUES('delete', old.rowid, old.title, old.description);
        END;
    """)
    op.execute("""
        CREATE TRIGGER tasks_au AFTER UPDATE ON tasks BEGIN
          INSERT INTO tasks_fts(tasks_fts, rowid, title, description)
          VALUES('delete', old.rowid, old.title, old.description);
          INSERT INTO tasks_fts(rowid, title, description)
          VALUES (new.rowid, new.title, new.description);
        END;
    """)

    op.execute("""
        CREATE TRIGGER tasks_updated_at AFTER UPDATE ON tasks BEGIN
          UPDATE tasks SET updated_at = strftime('%Y-%m-%dT%H:%M:%fZ', 'now') WHERE rowid = new.rowid;
        END;
    """)


def _create_postgres_triggers() -> None:
    """PostgreSQL equivalent of the SQLite tasks_updated_at trigger.

    Keeps tasks.updated_at current on every row update, matching the SQLite
    trigger's observable behavior. FTS5 has no PostgreSQL equivalent; keyword
    search on PostgreSQL is provided by the pg_trgm GIN indexes created in
    revision 002_postgres_fts.
    """
    op.execute("""
        CREATE OR REPLACE FUNCTION aether_touch_tasks_updated_at() RETURNS trigger AS $$
        BEGIN
          NEW.updated_at := to_char(now() AT TIME ZONE 'utc', 'YYYY-MM-DD"T"HH24:MI:SS.MS"Z"');
          RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)
    op.execute("""
        CREATE TRIGGER tasks_updated_at BEFORE UPDATE ON tasks
        FOR EACH ROW EXECUTE FUNCTION aether_touch_tasks_updated_at();
    """)


def downgrade() -> None:
    dialect = op.get_bind().dialect.name

    if dialect == "sqlite":
        # Reverse triggers
        op.execute("DROP TRIGGER IF EXISTS tasks_updated_at")
        op.execute("DROP TRIGGER IF EXISTS tasks_au")
        op.execute("DROP TRIGGER IF EXISTS tasks_ad")
        op.execute("DROP TRIGGER IF EXISTS tasks_ai")

        op.execute("DROP TRIGGER IF EXISTS memories_au")
        op.execute("DROP TRIGGER IF EXISTS memories_ad")
        op.execute("DROP TRIGGER IF EXISTS memories_ai")

        # Drop FTS tables (SQLite FTS5 shadow tables only — derived search
        # indexes over memories/tasks with no user data of their own)
        op.execute("DROP TABLE IF EXISTS tasks_fts")
        op.execute("DROP TABLE IF EXISTS memories_fts")
    else:
        # Reverse the PostgreSQL trigger and function created by upgrade()
        op.execute("DROP TRIGGER IF EXISTS tasks_updated_at ON tasks")
        op.execute("DROP FUNCTION IF EXISTS aether_touch_tasks_updated_at")

    # Drop child tables
    op.drop_table("llm_costs")
    op.drop_table("messages")

    # Drop parent tables (agent_runs doesn't have children aside from llm_costs)
    op.drop_table("agent_runs")
    op.drop_table("tool_executions")

    op.drop_table("tasks")
    op.drop_table("memories")
    op.drop_table("conversations")
    op.drop_table("system_kv")
