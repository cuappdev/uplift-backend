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
    # App startup may already have created this table through create_all().
    if not sa.inspect(op.get_bind()).has_table("user_workout_goal_history"):
        op.create_table(
            "user_workout_goal_history",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
            sa.Column("workout_goal", sa.Integer(), nullable=False),
            sa.Column("effective_at", sa.DateTime(timezone=True), nullable=False,
                      server_default=sa.text("CURRENT_TIMESTAMP")),
        )
    # Seed only users without history. This is an explicit legacy fallback,
    # not an assertion that we know when their original goal was selected.
    op.execute(sa.text("""
        INSERT INTO user_workout_goal_history (user_id, workout_goal, effective_at)
        SELECT id, workout_goal, '1970-01-01 00:00:00+00'
        FROM users
        WHERE workout_goal BETWEEN 1 AND 7
          AND NOT EXISTS (
              SELECT 1 FROM user_workout_goal_history h WHERE h.user_id = users.id
          )
    """))


def downgrade():
    # Preserve history: the table and rows may have existed before this revision.
    pass
