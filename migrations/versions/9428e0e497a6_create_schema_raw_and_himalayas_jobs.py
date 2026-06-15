"""create_schema_raw_and_himalayas_jobs

Revision ID: 9428e0e497a6
Revises:
Create Date: 2026-06-14 22:41:46.083670

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "9428e0e497a6"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS raw")
    op.execute("""
        CREATE TABLE IF NOT EXISTS raw.himalayas_jobs (
            _id           BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            source        TEXT        NOT NULL DEFAULT 'himalayas',
            source_job_id TEXT        NOT NULL,
            snapshot_date DATE        NOT NULL,
            loaded_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            run_id        TEXT,
            payload       JSONB       NOT NULL,
            CONSTRAINT uq_himalayas_job_per_day
                UNIQUE (source_job_id, snapshot_date)
        )
    """)
    op.execute("CREATE INDEX ix_himalayas_snapshot   ON raw.himalayas_jobs (snapshot_date)")
    op.execute("CREATE INDEX ix_himalayas_source_job ON raw.himalayas_jobs (source_job_id)")


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS raw.himalayas_jobs")
    op.execute("DROP SCHEMA IF EXISTS raw")
