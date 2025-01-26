"""create reminder, average hourly capacity tables

Revision ID: d8d0bd048cd6
Revises: 24684343da0f
Create Date: 2025-01-02 17:27:45.425737

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine import reflection

from sqlalchemy.dialects.postgresql import ENUM
from src.models.enums import DayOfWeekEnum  # Import your ENUM definition


# revision identifiers, used by Alembic.
revision = 'd8d0bd048cd6'
down_revision = '24684343da0f'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()

    # Create an inspector instance
    inspector = reflection.Inspector.from_engine(conn)

    # Check if the table exists
    existing_tables = inspector.get_table_names()

    # Use the imported ENUM directly
    dayofweek_enum = ENUM(*[e.name for e in DayOfWeekEnum], name="dayofweekenum", create_type=False)

    # Create the hourly_average_capacity table
    if 'hourly_average_capacity' not in existing_tables:
        op.create_table(
            'hourly_average_capacity',
            sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
            sa.Column('facility_id', sa.Integer, sa.ForeignKey('facility.id'), nullable=False),
            sa.Column('average_percent', sa.Float, nullable=False),
            sa.Column('hour_of_day', sa.Integer, nullable=False),
            sa.Column('day_of_week', dayofweek_enum, nullable=False),
            sa.Column('history', sa.ARRAY(sa.Numeric), nullable=False, server_default='{}'),
        )

    # Create the workout_reminder table
    if 'workout_reminder' not in existing_tables:
        op.create_table(
            'workout_reminder',
            sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
            sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id'), nullable=False),
            sa.Column('days_of_week', sa.ARRAY(dayofweek_enum), nullable=False),
            sa.Column('reminder_time', sa.Time, nullable=False),
            sa.Column('is_active', sa.Boolean, server_default=sa.sql.expression.true(), nullable=False),
        )

    # Create the capacity_reminder table
    if 'capacity_reminder' not in existing_tables:
        op.create_table(
            'capacity_reminder',
            sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
            sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id'), nullable=False),
            sa.Column('gyms', sa.ARRAY(sa.String), nullable=False),
            sa.Column('capacity_threshold', sa.Integer, nullable=False),
            sa.Column('days_of_week', sa.ARRAY(dayofweek_enum), nullable=False),
            sa.Column('is_active', sa.Boolean, server_default=sa.sql.expression.true(), nullable=False),
        )

    # Add fields to the users table
    columns = [column['name'] for column in inspector.get_columns('users')]
    if 'fcm_token' not in columns:
        op.add_column('users', sa.Column('fcm_token', sa.String, nullable=False))


def downgrade():
    # Drop the tables in reverse order of creation
    op.drop_table('capacity_reminder')
    op.drop_table('workout_reminder')
    op.drop_table('hourly_average_capacity')

    # Remove fields from the users table
    op.drop_column('users', 'fcm_token')
