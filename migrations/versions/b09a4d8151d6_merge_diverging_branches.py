"""Merge diverging branches

Revision ID: b09a4d8151d6
Revises: eb948c31a342, 48923aecacb0
Create Date: 2026-03-05 17:15:46.737524

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b09a4d8151d6'
down_revision = ('eb948c31a342', '48923aecacb0')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
