"""Create gear table

Revision ID: eb948c31a342
Revises: 6fb4a21a1201
Create Date: 2026-03-02 06:22:00.042780

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = 'eb948c31a342'
down_revision = '6fb4a21a1201'
branch_labels = None
depends_on = None

### Ensures alembic does not try to create enum
price_type_enum = postgresql.ENUM('rate', 'gear', name='pricetype', create_type=False)


def upgrade():
    op.create_table(
        "gear",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("activity_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("cost", sa.Float(), nullable=False),
        sa.Column("rate", sa.String(), nullable=True),
        sa.Column("type", price_type_enum, nullable=False),
    )

def downgrade():
    op.drop_table("gear")
