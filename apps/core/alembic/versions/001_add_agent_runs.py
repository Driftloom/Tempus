"""Add agent_runs and agent_run_steps tables

Revision ID: 001_add_agent_runs
Revises: 
Create Date: 2024-01-16 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_add_agent_runs'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create agent_runs table
    op.create_table(
        'agent_runs',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('agent_type', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('goal', sa.Text(), nullable=False),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('current_step_index', sa.Integer(), nullable=True),
        sa.Column('budget_max_steps', sa.Integer(), nullable=False),
        sa.Column('budget_max_duration_s', sa.Integer(), nullable=True),
        sa.Column('budget_max_cost_usd', sa.Float(), nullable=True),
        sa.Column('cost_used_usd', sa.Float(), nullable=True),
        sa.Column('started_at', sa.DateTime(), nullable=False),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('result_summary', sa.Text(), nullable=True),
        sa.Column('error_reason', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_agent_runs_id'), 'agent_runs', ['id'], unique=False)
    op.create_index(op.f('ix_agent_runs_agent_type'), 'agent_runs', ['agent_type'], unique=False)
    op.create_index(op.f('ix_agent_runs_user_id'), 'agent_runs', ['user_id'], unique=False)
    op.create_index(op.f('ix_agent_runs_status'), 'agent_runs', ['status'], unique=False)

    # Create agent_run_steps table
    op.create_table(
        'agent_run_steps',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('agent_run_id', sa.String(), nullable=False),
        sa.Column('step_index', sa.Integer(), nullable=False),
        sa.Column('step_type', sa.String(), nullable=False),
        sa.Column('content', sa.Text(), nullable=True),
        sa.Column('tool_called', sa.String(), nullable=True),
        sa.Column('tool_result', sa.Text(), nullable=True),
        sa.Column('cost_usd', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['agent_run_id'], ['agent_runs.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_agent_run_steps_id'), 'agent_run_steps', ['id'], unique=False)
    op.create_index(op.f('ix_agent_run_steps_agent_run_id'), 'agent_run_steps', ['agent_run_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_agent_run_steps_agent_run_id'), table_name='agent_run_steps')
    op.drop_index(op.f('ix_agent_run_steps_id'), table_name='agent_run_steps')
    op.drop_table('agent_run_steps')
    
    op.drop_index(op.f('ix_agent_runs_status'), table_name='agent_runs')
    op.drop_index(op.f('ix_agent_runs_user_id'), table_name='agent_runs')
    op.drop_index(op.f('ix_agent_runs_agent_type'), table_name='agent_runs')
    op.drop_index(op.f('ix_agent_runs_id'), table_name='agent_runs')
    op.drop_table('agent_runs')
