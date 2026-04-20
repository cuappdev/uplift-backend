"""Stub for add_friends_table revision

The original add_friends_table migration file was never committed to the repo,
but 6ec7ce03bb6a_change_workout_goal_type_to_integer.py references it as its
down_revision. Without this stub, Alembic cannot traverse the migration graph
and `flask db upgrade` / `db stamp` fail with KeyError: 'add_friends_table'.

This stub is a no-op — the friends table is created by SQLAlchemy
Base.metadata.create_all() in init_db(), not by any migration.

Revision ID: add_friends_table
Revises:
Create Date: 2026-04-19 20:09:00.000000
"""
from alembic import op
import sqlalchemy as sa


revision = 'add_friends_table'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
