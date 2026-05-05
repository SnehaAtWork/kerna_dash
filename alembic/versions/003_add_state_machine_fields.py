"""add state machine fields

Revision ID: 003
Revises: 002_add_reset_token_to_users
Create Date: 2025-05-05

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('leads', sa.Column('notes', sa.Text(), nullable=True))

    op.add_column('quotations', sa.Column('title', sa.String(255), nullable=True))
    op.add_column('quotations', sa.Column('notes', sa.Text(), nullable=True))

    op.add_column('projects', sa.Column('quotation_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column('projects', sa.Column('name', sa.String(255), nullable=True))
    op.create_foreign_key(
        'fk_projects_quotation_id',
        'projects', 'quotations',
        ['quotation_id'], ['id'],
        ondelete='SET NULL'
    )
    op.create_index('ix_projects_quotation_id', 'projects', ['quotation_id'])

    op.alter_column('quotation_versions', 'subtotal',
        existing_type=sa.Numeric(10, 2),
        server_default='0',
        existing_nullable=False
    )
    op.alter_column('quotation_versions', 'total',
        existing_type=sa.Numeric(10, 2),
        server_default='0',
        existing_nullable=False
    )


def downgrade():
    op.drop_index('ix_projects_quotation_id', 'projects')
    op.drop_constraint('fk_projects_quotation_id', 'projects', type_='foreignkey')
    op.drop_column('projects', 'name')
    op.drop_column('projects', 'quotation_id')
    op.drop_column('quotations', 'notes')
    op.drop_column('quotations', 'title')
    op.drop_column('leads', 'notes')
