"""Initial schema — transactions table.

Revision ID: 001
Revises:
Create Date: 2024-01-15
"""
from alembic import op
import sqlalchemy as sa

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "transactions",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("amount", sa.Numeric(18, 6), nullable=False),
        sa.Column("currency", sa.String(3), nullable=False),
        sa.Column("entity", sa.String(64), nullable=False),
        sa.Column("date", sa.Date, nullable=False),
        sa.Column("source", sa.String(32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_transactions_date", "transactions", ["date"])
    op.create_index("ix_transactions_entity", "transactions", ["entity"])


def downgrade() -> None:
    op.drop_index("ix_transactions_entity", "transactions")
    op.drop_index("ix_transactions_date", "transactions")
    op.drop_table("transactions")
