"""Add friends table

Revision ID: 01234abcdef1
Revises: previous_revision_id_here
Create Date: 2025-03-29 00:45:00.000000

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime


# revision identifiers, used by Alembic.
revision = '01234abcdef1'
down_revision = 'add99ce06ff5'
branch_labels = None
depends_on = None


def upgrade():
    # Create friends table
    op.create_table('friends',
                    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
                    sa.Column('user_id', sa.Integer(), nullable=False),
                    sa.Column('friend_id', sa.Integer(), nullable=False),
                    sa.Column('created_at', sa.DateTime(), nullable=True, default=datetime.utcnow),
                    sa.Column('is_accepted', sa.Boolean(), nullable=True, default=False),
                    sa.Column('accepted_at', sa.DateTime(), nullable=True),
                    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
                    sa.ForeignKeyConstraint(['friend_id'], ['users.id'], ondelete='CASCADE'),
                    sa.PrimaryKeyConstraint('id')
                    )


def downgrade():
    # Drop friends table
    op.drop_table('friends')
