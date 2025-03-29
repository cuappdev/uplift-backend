"""Add friends table

Revision ID: add_friends_table
Revises: 3c406131c004
Create Date: 2025-03-29 00:55:00.000000

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime


# revision identifiers, used by Alembic.
revision = 'add_friends_table'
down_revision = '3c406131c004'
branch_labels = None
depends_on = None


def upgrade():
    # Create friends table
    op.create_table('friends',
                    sa.Column('user_id', sa.Integer(), nullable=False),
                    sa.Column('friend_id', sa.Integer(), nullable=False),
                    sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.text('CURRENT_TIMESTAMP')),
                    sa.Column('is_accepted', sa.Boolean(), nullable=True, server_default=sa.text('false')),
                    sa.Column('accepted_at', sa.DateTime(), nullable=True),
                    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
                    sa.ForeignKeyConstraint(['friend_id'], ['users.id'], ondelete='CASCADE'),
                    sa.PrimaryKeyConstraint('user_id', 'friend_id')
                    )


def downgrade():
    # Drop friends table
    op.drop_table('friends')
