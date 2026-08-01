"""Add pgcrypto extension for encryption support

Revision ID: 003
Revises: 002
Create Date: 2026-01-29

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Enable pgcrypto extension for encryption at rest."""
    # Enable pgcrypto extension for column-level encryption
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")
    
    # Grant usage to tempus user
    op.execute("GRANT USAGE ON SCHEMA public TO tempus")
    op.execute("GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO tempus")


def downgrade() -> None:
    """Disable pgcrypto extension."""
    # Revoke permissions
    op.execute("REVOKE EXECUTE ON ALL FUNCTIONS IN SCHEMA public FROM tempus")
    op.execute("REVOKE USAGE ON SCHEMA public FROM tempus")
    
    # Drop extension
    op.execute("DROP EXTENSION IF EXISTS pgcrypto")
