"""Added fitness center to workout model

Revision ID: 0fde4435424e
Revises: 6b01a81bb92b
Create Date: 2025-03-06 20:50:25.488572

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0fde4435424e'
down_revision = '6b01a81bb92b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('workout', sa.Column('facility_id', sa.Integer(), nullable=False))
    op.create_foreign_key(None, 'workout', 'facility', ['facility_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'workout', type_='foreignkey')
    op.drop_column('workout', 'facility_id')
    # ### end Alembic commands ###
