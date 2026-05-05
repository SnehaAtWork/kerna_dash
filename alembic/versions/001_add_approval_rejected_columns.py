"""Add rejected_by and rejected_at to approvals table

Revision ID: 001
Revises:
Create Date: 2026-04-26
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "approvals",
        sa.Column("rejected_by", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.add_column(
        "approvals",
        sa.Column("rejected_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("approvals", "rejected_at")
    op.drop_column("approvals", "rejected_by")
