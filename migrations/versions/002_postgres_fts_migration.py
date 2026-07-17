"""PostgreSQL keyword search: pg_trgm extension and GIN trigram indexes replacing FTS5.

On PostgreSQL this revision installs the pg_trgm extension and creates GIN
trigram indexes on the columns that SQLite's FTS5 virtual tables previously
served (memories.content/tags/entities, tasks.title/description). On SQLite —
which remains the test-suite backend — this revision is an explicit no-op:
FTS5 from revision 001 stays in place there, and the keyword-search
implementation in aether/memory/_stores/ dispatches per dialect.

Revision ID: 002_postgres_fts
Revises: 001_initial_schema
Create Date: 2026-07-06 03:00:00.000000

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "002_postgres_fts"
down_revision = "001_initial_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    dialect = op.get_bind().dialect.name
    if dialect != "postgresql":
        # SQLite (the test backend) keeps its FTS5 objects from revision 001.
        # This revision is PostgreSQL-only by design.
        return

    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")

    # GIN trigram indexes replacing the columns FTS5 indexed on SQLite.
    # Separate single-column indexes: pg_trgm operators match one column
    # expression at a time, and the keyword query ORs across the three
    # memories columns, which the planner serves via index OR-combination.
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_memories_content_trgm "
        "ON memories USING gin (content gin_trgm_ops)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_memories_tags_trgm "
        "ON memories USING gin (tags gin_trgm_ops)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_memories_entities_trgm "
        "ON memories USING gin (entities gin_trgm_ops)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_tasks_title_trgm ON tasks USING gin (title gin_trgm_ops)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_tasks_description_trgm "
        "ON tasks USING gin (description gin_trgm_ops)"
    )

    # SAFETY (ADR-010 Section 3.2 — explicitly authorized by the M2.1 prompt):
    # the two DROP TABLE statements below target ONLY the SQLite FTS5 shadow
    # tables memories_fts and tasks_fts. These are derived keyword-search
    # indexes over memories/tasks with no data of their own — never user data
    # tables. On a PostgreSQL schema created by revision 001 they do not exist
    # (001's PostgreSQL branch never creates FTS5 objects), so these statements
    # are defensive no-ops guarding the edge case of a schema transplanted
    # from a SQLite dump.
    op.execute("DROP TABLE IF EXISTS memories_fts")
    op.execute("DROP TABLE IF EXISTS tasks_fts")
    # The FTS5 sync triggers (memories_ai/ad/au, tasks_ai/ad/au) cannot exist
    # on PostgreSQL — their SQLite-specific DDL never executes on this dialect
    # — so no trigger drops are required here.


def downgrade() -> None:
    dialect = op.get_bind().dialect.name
    if dialect != "postgresql":
        # Nothing to reverse on SQLite: upgrade() was a no-op there and the
        # FTS5 objects from revision 001 were never touched.
        return

    # Reversing this revision on PostgreSQL would require DROP INDEX and
    # DROP EXTENSION operations classified as forbidden by ADR-010 Section 3.2,
    # and would leave the system without any keyword-search path. Fail loudly
    # rather than silently degrade; recovery is restore-from-verified-backup
    # per ADR-010 Section 5.
    raise NotImplementedError(
        "Revision 002_postgres_fts cannot be downgraded on PostgreSQL: "
        "reversing it would drop the pg_trgm GIN indexes that provide keyword "
        "search, and ADR-010 Section 3.2 forbids automated DROP INDEX "
        "operations. Restore from a verified backup instead (ADR-010 Section 5)."
    )
