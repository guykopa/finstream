"""Add quality_results table.

Revision ID: 003
Revises: 002
Create Date: 2024-01-15
"""
from alembic import op
import sqlalchemy as sa

revision = "003"
down_revision = "002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "quality_results",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("run_id", sa.String(64), sa.ForeignKey("pipeline_runs.run_id"), nullable=False),
        sa.Column("rule_name", sa.String(64), nullable=False),
        sa.Column("passed", sa.Boolean, nullable=False),
        sa.Column("failed_count", sa.Integer, nullable=False),
        sa.Column("error_samples", sa.Text, nullable=True),
        sa.Column("checked_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_quality_results_run_id", "quality_results", ["run_id"])


def downgrade() -> None:
    op.drop_index("ix_quality_results_run_id", "quality_results")
    op.drop_table("quality_results")
