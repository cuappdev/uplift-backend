"""Create gear table

Revision ID: eb948c31a342
Revises: 6fb4a21a1201
Create Date: 2026-03-02 06:22:00.042780

"""
from alembic import op
import sqlalchemy as sa

# Import the PriceType enum used in the model so the Enum can be created
from src.models.activity import PriceType


# revision identifiers, used by Alembic.
revision = 'eb948c31a342'
down_revision = '6fb4a21a1201'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "gear",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("activity_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("cost", sa.Float(), nullable=False),
        sa.Column("rate", sa.String(), nullable=True),
        sa.Column("type", sa.Enum(PriceType, create_type=False), nullable=False),
    )

def downgrade():
    op.drop_table("gear")
