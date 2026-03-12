"""make last_streak non_null default 0

Revision ID: 46ba03c28573
Revises: b09a4d8151d6
Create Date: 2026-03-06 01:47:07.348774

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '46ba03c28573'
down_revision = 'b09a4d8151d6'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("UPDATE users SET last_streak = 0 WHERE last_streak IS NULL")
    op.alter_column('users', 'last_streak',
        existing_type=sa.INTEGER(),
        nullable=False,
        server_default=sa.text('0')
    )


def downgrade():
    op.alter_column('users', 'last_streak',
        existing_type=sa.INTEGER(),
        nullable=True,
        server_default=None
    )
