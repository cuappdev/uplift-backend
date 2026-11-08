"""Debug internal default conversion to UTC

Revision ID: 48923aecacb0
Revises: 
Create Date: 2026-03-02 06:30:17.794409

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '48923aecacb0'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column(
        "workout",
        "workout_time",
        type_=sa.DateTime(timezone=True),
        postgresql_using="workout_time AT TIME ZONE 'UTC'",
        existing_nullable=False,
    )

    op.alter_column(
        "user_workout_goal_history",
        "effective_at",
        type_=sa.DateTime(timezone=True),
        postgresql_using="effective_at AT TIME ZONE 'UTC'",
        existing_nullable=False,
    )

    op.alter_column(
        "user_workout_goal_history",
        "effective_at",
        server_default=sa.text("CURRENT_TIMESTAMP"),
        existing_type=sa.DateTime(timezone=True),
        existing_nullable=False,
    )


def downgrade():
    op.alter_column(
        "user_workout_goal_history",
        "effective_at",
        server_default=None,
        existing_type=sa.DateTime(timezone=True),
        existing_nullable=False,
    )
    
    op.alter_column(
        "user_workout_goal_history",
        "effective_at",
        type_=sa.DateTime(timezone=False),
        postgresql_using="effective_at::timestamp",
        existing_nullable=False,
    )

    op.alter_column(
        "workout",
        "workout_time",
        type_=sa.DateTime(timezone=False),
        postgresql_using="workout_time::timestamp",
        existing_nullable=False,
    )
