"""Added active_streak and max_streak to users

Revision ID: 6b01a81bb92b
Revises: 31b1fa20772f
Create Date: 2025-03-04 22:45:06.601964

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6b01a81bb92b'
down_revision = '31b1fa20772f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('active_streak', sa.Integer(), nullable=True))
    op.add_column('users', sa.Column('max_streak', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'active_streak')
    op.drop_column('users', 'max_streak')
    # ### end Alembic commands ###
