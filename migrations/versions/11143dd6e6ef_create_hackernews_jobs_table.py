"""create hackernews jobs table

Revision ID: 11143dd6e6ef
Revises: 7923bbcdaa8b
Create Date: 2026-06-30

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "11143dd6e6ef"
down_revision: str | None = "7923bbcdaa8b"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "hackernews_jobs",
        sa.Column("_id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("source", sa.Text(), nullable=False),
        sa.Column("source_job_id", sa.Text(), nullable=False),
        sa.Column("snapshot_date", sa.Date(), nullable=False),
        sa.Column(
            "loaded_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")
        ),
        sa.Column("run_id", sa.Text(), nullable=True),
        sa.Column("payload", sa.dialects.postgresql.JSONB(), nullable=False),
        sa.PrimaryKeyConstraint("_id"),
        sa.UniqueConstraint(
            "source_job_id", "snapshot_date", name="uq_hackernews_jobs_source_job_id_snapshot_date"
        ),
        schema="raw",
    )
    op.create_index(
        "ix_hackernews_jobs_snapshot_date", "hackernews_jobs", ["snapshot_date"], schema="raw"
    )
    op.create_index(
        "ix_hackernews_jobs_source_job_id", "hackernews_jobs", ["source_job_id"], schema="raw"
    )


def downgrade() -> None:
    op.drop_index("ix_hackernews_jobs_source_job_id", table_name="hackernews_jobs", schema="raw")
    op.drop_index("ix_hackernews_jobs_snapshot_date", table_name="hackernews_jobs", schema="raw")
    op.drop_table("hackernews_jobs", schema="raw")
