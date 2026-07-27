"""Add provenance field to memory_items table

Revision ID: 002_add_provenance
Revises: 001_add_agent_runs
Create Date: 2024-01-16 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '002_add_provenance'
down_revision = '001_add_agent_runs'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add provenance column to memory_items
    op.add_column('memory_items', sa.Column('provenance', sa.String(100), nullable=False, server_default='user_direct'))
    op.create_index(op.f('ix_memory_items_provenance'), 'memory_items', ['provenance'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_memory_items_provenance'), table_name='memory_items')
    op.drop_column('memory_items', 'provenance')
