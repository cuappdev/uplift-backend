"""add muscle groups and clean name to equipment

Revision ID: 79fec8ab4c70
Revises: f711f3c11324
Create Date: 2024-11-13 17:48:46.093175

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy import Enum


# revision identifiers, used by Alembic.
revision = '79fec8ab4c70'
down_revision = None
branch_labels = None
depends_on = None

# Define enums for reference
class MuscleGroup(Enum):
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

class AccessibilityType(Enum):
    wheelchair = 0

def upgrade():
    # First, delete all existing equipment data
    op.execute('TRUNCATE TABLE equipment CASCADE')

    # Drop the old enum type
    op.execute('DROP TYPE IF EXISTS equipmenttype')

    # Create new enum types
    muscle_group_enum = postgresql.ENUM(
        'ABDOMINALS', 'CHEST', 'BACK', 'SHOULDERS', 'BICEPS', 'TRICEPS',
        'HAMSTRINGS', 'QUADS', 'GLUTES', 'CALVES', 'MISCELLANEOUS', 'CARDIO',
        name='musclegroup'
    )
    muscle_group_enum.create(op.get_bind())

    new_accessibility_enum = postgresql.ENUM('wheelchair', name='accessibilitytype_new')
    new_accessibility_enum.create(op.get_bind())

    # Drop old columns
    op.drop_column('equipment', 'equipment_type')
    op.drop_column('equipment', 'accessibility')

    # Add new columns
    op.add_column('equipment', sa.Column('clean_name', sa.String(), nullable=False))
    op.add_column('equipment',
                  sa.Column('muscle_groups', postgresql.ARRAY(muscle_group_enum), nullable=True)
                  )
    op.add_column('equipment',
                  sa.Column('accessibility', new_accessibility_enum, nullable=True)
                  )

def downgrade():
    # First, delete all equipment data
    op.execute('TRUNCATE TABLE equipment CASCADE')

    # Create old equipment_type enum
    old_equipment_type_enum = postgresql.ENUM(
        'cardio',
        'racks_and_benches',
        'selectorized',
        'multi_cable',
        'free_weights',
        'miscellaneous',
        'plate_loaded',
        name='equipmenttype'
    )
    old_equipment_type_enum.create(op.get_bind())

    # Drop new columns
    op.drop_column('equipment', 'clean_name')
    op.drop_column('equipment', 'muscle_groups')
    op.drop_column('equipment', 'accessibility')

    # Add back old columns
    op.add_column('equipment',
                  sa.Column('equipment_type', old_equipment_type_enum, nullable=False)
                  )

    # Drop new enums
    postgresql.ENUM(name='musclegroup').drop(op.get_bind())
    postgresql.ENUM(name='accessibilitytype_new').drop(op.get_bind(), cascade=True)

    # Recreate old accessibility enum and column
    old_accessibility_enum = postgresql.ENUM('wheelchair', name='accessibilitytype')
    old_accessibility_enum.create(op.get_bind())
    op.add_column('equipment',
                  sa.Column('accessibility', old_accessibility_enum, nullable=True)
                  )
