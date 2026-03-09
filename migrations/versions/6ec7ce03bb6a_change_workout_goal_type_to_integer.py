"""Change workout_goal type to integer

Revision ID: 6ec7ce03bb6a
Revises: add_friends_table
Create Date: 2026-02-09 22:56:02.894228

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6ec7ce03bb6a'
down_revision = 'add_friends_table'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column("users", "workout_goal", type_=sa.Integer, postgresql_using="cardinality(workout_goal)")

# NOTE: Lossy migration — cannot convert integer back to array of specific days of the week
def downgrade():
    raise NotImplementedError("Downgrade is possible: cannot convert integer back to array of specific days of the week")
