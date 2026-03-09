"""Implement user weekly challenges table

Revision ID: 1063ea54c7b9
Revises: 1a3e89ce4753
Create Date: 2026-03-09 11:49:34.463506

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1063ea54c7b9'
down_revision = '1a3e89ce4753'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('user_weekly_challenges',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('user_id', sa.Integer(), nullable=False),
                    sa.Column('weekly_challenge_id', sa.Integer(), nullable=False),
                    sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
                    sa.Column('points', sa.Integer(), nullable=False),
                    sa.Column('status', sa.Enum('NOT_STARTED', 'IN_PROGRESS', 'COMPLETED', name='userweeklychallengestatusenum'), nullable=False, server_default='NOT_STARTED'),
                    sa.Column('is_completed', sa.Boolean(), nullable=False, server_default=sa.false()),
                    sa.PrimaryKeyConstraint('id')
                    )

                    


def downgrade():
    op.drop_table('user_weekly_challenges')
