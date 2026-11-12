"""add workout details

Adds the fields the app fills in when a user saves a workout: when it
started and ended, a title, a description, and a 0-5 rating. All are
nullable so existing check-in workouts stay valid.

Revision ID: 7d2e5f1a9c34
Revises: c4e8b0d2a7f1
"""

from alembic import op
import sqlalchemy as sa

revision = "7d2e5f1a9c34"
down_revision = "c4e8b0d2a7f1"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("workout", sa.Column("started_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("workout", sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("workout", sa.Column("title", sa.String(length=100), nullable=True))
    op.add_column("workout", sa.Column("description", sa.Text(), nullable=True))
    op.add_column("workout", sa.Column("rating", sa.Integer(), nullable=True))
    op.create_check_constraint("ck_workout_rating_range", "workout", "rating >= 0 AND rating <= 5")


def downgrade():
    op.drop_constraint("ck_workout_rating_range", "workout", type_="check")
    op.drop_column("workout", "rating")
    op.drop_column("workout", "description")
    op.drop_column("workout", "title")
    op.drop_column("workout", "ended_at")
    op.drop_column("workout", "started_at")
