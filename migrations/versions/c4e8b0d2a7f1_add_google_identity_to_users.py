"""add Google identity to users

Revision ID: c4e8b0d2a7f1
Revises: 46ba03c28573
"""

from alembic import op
import sqlalchemy as sa

revision = "c4e8b0d2a7f1"
down_revision = "46ba03c28573"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("users", sa.Column("google_sub", sa.String(), nullable=True))
    op.create_index("uq_users_google_sub", "users", ["google_sub"], unique=True)


def downgrade():
    op.drop_index("uq_users_google_sub", table_name="users")
    op.drop_column("users", "google_sub")
