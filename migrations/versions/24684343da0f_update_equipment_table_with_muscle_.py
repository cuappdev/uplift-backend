"""update equipment table with muscle groups

Revision ID: 24684343da0f
Revises: 
Create Date: 2024-11-20 17:40:32.344965

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy import Enum
from enum import Enum as PyEnum

# revision identifiers, used by Alembic.
revision = '24684343da0f'
down_revision = None
branch_labels = None
depends_on = None

class MuscleGroup(PyEnum):
    ABDOMINALS = 1
    CHEST = 2
    BACK = 3
    SHOULDERS = 4
    BICEPS = 5
    TRICEPS = 6
    HAMSTRINGS = 7
    QUADS = 8
    GLUTES = 9
    CALVES = 10
    MISCELLANEOUS = 11
    CARDIO = 12

def upgrade():
    # Get the connection and inspector
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)

    # Get the list of existing columns in the 'equipment' table
    columns = [col["name"] for col in inspector.get_columns("equipment")]

    # Check if 'clean_name' exists before adding it
    if "clean_name" not in columns:
        op.add_column('equipment', sa.Column('clean_name', sa.String(), nullable=True))

    # Check if 'muscle_groups' exists before adding it
    if "muscle_groups" not in columns:
        muscle_group_enum = postgresql.ENUM(
            'ABDOMINALS', 'CHEST', 'BACK', 'SHOULDERS', 'BICEPS', 'TRICEPS',
            'HAMSTRINGS', 'QUADS', 'GLUTES', 'CALVES', 'MISCELLANEOUS', 'CARDIO',
            name='musclegroup'
        )
        muscle_group_enum.create(op.get_bind())

        op.add_column('equipment', sa.Column('muscle_groups', postgresql.ARRAY(muscle_group_enum), nullable=True))

    # Continue with other operations, ensuring they're idempotent
    op.execute('UPDATE equipment SET clean_name = name')

    # Additional logic for migrating data or altering columns as needed
    op.alter_column('equipment', 'clean_name', existing_type=sa.String(), nullable=False)
    op.alter_column('equipment', 'muscle_groups', existing_type=postgresql.ARRAY(muscle_group_enum), nullable=False)

    if "equipment_type" in columns:
        op.drop_column('equipment', 'equipment_type')
        op.execute('DROP TYPE equipmenttype')

def downgrade():
    # Create old equipment_type enum
    op.execute("""
    CREATE TYPE equipmenttype AS ENUM (
        'cardio',
        'racks_and_benches',
        'selectorized',
        'multi_cable',
        'free_weights',
        'miscellaneous',
        'plate_loaded'
    )
    """)

    # Add equipment_type column
    op.add_column('equipment',
                  sa.Column('equipment_type', postgresql.ENUM('cardio', 'racks_and_benches', 'selectorized',
                                                              'multi_cable', 'free_weights', 'miscellaneous',
                                                              'plate_loaded', name='equipmenttype'),
                            nullable=True))

    # Convert muscle_groups back to equipment_type
    op.execute("""
    UPDATE equipment SET equipment_type = CASE 
        WHEN 'CARDIO' = ANY(muscle_groups) THEN 'cardio'::equipmenttype
        WHEN 'CHEST' = ANY(muscle_groups) OR 'BACK' = ANY(muscle_groups) OR 'SHOULDERS' = ANY(muscle_groups) 
            THEN 'racks_and_benches'::equipmenttype
        ELSE 'miscellaneous'::equipmenttype
    END
    """)

    # Make equipment_type not nullable
    op.alter_column('equipment', 'equipment_type',
                    existing_type=postgresql.ENUM('cardio', 'racks_and_benches', 'selectorized',
                                                  'multi_cable', 'free_weights', 'miscellaneous',
                                                  'plate_loaded', name='equipmenttype'),
                    nullable=False)

    # Drop new columns
    op.drop_column('equipment', 'muscle_groups')
    op.drop_column('equipment', 'clean_name')

    # Drop muscle_group enum
    op.execute('DROP TYPE musclegroup')
