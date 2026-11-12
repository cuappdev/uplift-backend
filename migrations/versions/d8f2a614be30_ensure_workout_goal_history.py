"""Ensure goal history exists without replacing existing goals or workouts.

Revision ID: d8f2a614be30
Revises: c4e8b0d2a7f1
"""
from alembic import op
import sqlalchemy as sa

revision = "d8f2a614be30"
down_revision = "c4e8b0d2a7f1"
branch_labels = None
depends_on = None


def upgrade():
    """Create missing goal history without inventing historical selections."""
    # App startup may already have created this table through create_all().
    if not sa.inspect(op.get_bind()).has_table("user_workout_goal_history"):
        op.create_table(
            "user_workout_goal_history",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
            sa.Column("workout_goal", sa.Integer(), nullable=False),
            sa.Column(
                "effective_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")
            ),
        )
    # The weekly migration seeds missing history after preserving the old
    # display. Seeding here would turn an unknown streak start into a date.


def downgrade():
    """Preserve a table that may predate this migration."""
    # Preserve history: the table and rows may have existed before this revision.
    pass
