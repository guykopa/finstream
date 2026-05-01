"""Add pipeline_runs table.

Revision ID: 002
Revises: 001
Create Date: 2024-01-15
"""
from alembic import op
import sqlalchemy as sa

revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "pipeline_runs",
        sa.Column("run_id", sa.String(64), primary_key=True),
        sa.Column("date", sa.Date, nullable=False),
        sa.Column("total_records", sa.Integer, nullable=False),
        sa.Column("clean_records", sa.Integer, nullable=False),
        sa.Column("quality_score", sa.Numeric(5, 2), nullable=False),
        sa.Column("duration_seconds", sa.Numeric(10, 3), nullable=False),
        sa.Column("chunk_count", sa.Integer, nullable=False),
        sa.Column("memory_peak_mb", sa.Numeric(10, 2), nullable=False),
        sa.Column("status", sa.String(16), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_pipeline_runs_date", "pipeline_runs", ["date"])
    op.create_index("ix_pipeline_runs_status", "pipeline_runs", ["status"])


def downgrade() -> None:
    op.drop_index("ix_pipeline_runs_status", "pipeline_runs")
    op.drop_index("ix_pipeline_runs_date", "pipeline_runs")
    op.drop_table("pipeline_runs")
