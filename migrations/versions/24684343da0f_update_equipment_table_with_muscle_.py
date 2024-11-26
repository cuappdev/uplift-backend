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
    # Create new muscle_group enum type
    muscle_group_enum = postgresql.ENUM(
        'ABDOMINALS', 'CHEST', 'BACK', 'SHOULDERS', 'BICEPS', 'TRICEPS',
        'HAMSTRINGS', 'QUADS', 'GLUTES', 'CALVES', 'MISCELLANEOUS', 'CARDIO',
        name='musclegroup'
    )
    muscle_group_enum.create(op.get_bind())

    # Add new columns first
    op.add_column('equipment', sa.Column('clean_name', sa.String(), nullable=True))
    op.add_column('equipment',
                  sa.Column('muscle_groups', postgresql.ARRAY(muscle_group_enum), nullable=True)
                  )

    # Update data: Set clean_name equal to name initially
    op.execute('UPDATE equipment SET clean_name = name')

    # Convert equipment_type to muscle_groups based on mapping
    op.execute("""
    UPDATE equipment SET muscle_groups = CASE 
        WHEN equipment_type = 'cardio' THEN ARRAY['CARDIO']::musclegroup[]
        WHEN equipment_type = 'racks_and_benches' THEN ARRAY['CHEST', 'BACK', 'SHOULDERS']::musclegroup[]
        WHEN equipment_type = 'selectorized' THEN ARRAY['MISCELLANEOUS']::musclegroup[]
        WHEN equipment_type = 'multi_cable' THEN ARRAY['MISCELLANEOUS']::musclegroup[]
        WHEN equipment_type = 'free_weights' THEN ARRAY['MISCELLANEOUS']::musclegroup[]
        WHEN equipment_type = 'plate_loaded' THEN ARRAY['MISCELLANEOUS']::musclegroup[]
        ELSE ARRAY['MISCELLANEOUS']::musclegroup[]
    END
    """)

    # Make clean_name not nullable after updating data
    op.alter_column('equipment', 'clean_name',
                    existing_type=sa.String(),
                    nullable=False)

    # Make muscle_groups not nullable after data migration
    op.alter_column('equipment', 'muscle_groups',
                    existing_type=postgresql.ARRAY(muscle_group_enum),
                    nullable=False)

    # Drop the old equipment_type column and enum
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
