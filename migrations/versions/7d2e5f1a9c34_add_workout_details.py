"""add workout details

Adds the fields the app fills in when a user saves a workout: when it
started and ended, a title, a description, a 0-5 rating, and the muscle
groups worked. All are optional so existing check-in workouts stay valid;
existing workouts get an empty list of muscle groups.

Revision ID: 7d2e5f1a9c34
Revises: c4e8b0d2a7f1
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "7d2e5f1a9c34"
down_revision = "c4e8b0d2a7f1"
branch_labels = None
depends_on = None

# Values are copied rather than imported so this migration doesn't change if the app's enum does
muscle_group_enum = postgresql.ENUM(
    "ARM", "LEG", "BACK", "CHEST", "SHOULDER", name="musclegroupenum", create_type=False
)


def upgrade():
    op.add_column("workout", sa.Column("started_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("workout", sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("workout", sa.Column("title", sa.String(length=100), nullable=True))
    op.add_column("workout", sa.Column("description", sa.Text(), nullable=True))
    op.add_column("workout", sa.Column("rating", sa.Integer(), nullable=True))
    op.create_check_constraint("ck_workout_rating_range", "workout", "rating >= 0 AND rating <= 5")

    muscle_group_enum.create(op.get_bind(), checkfirst=True)
    op.add_column(
        "workout",
        sa.Column("muscle_groups", postgresql.ARRAY(muscle_group_enum), nullable=False, server_default=sa.text("'{}'")),
    )


def downgrade():
    op.drop_column("workout", "muscle_groups")
    muscle_group_enum.drop(op.get_bind(), checkfirst=True)

    op.drop_constraint("ck_workout_rating_range", "workout", type_="check")
    op.drop_column("workout", "rating")
    op.drop_column("workout", "description")
    op.drop_column("workout", "title")
    op.drop_column("workout", "ended_at")
    op.drop_column("workout", "started_at")
