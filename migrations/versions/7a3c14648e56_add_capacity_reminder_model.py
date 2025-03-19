"""add capacity reminder model

Revision ID: 7a3c14648e56
Revises: add99ce06ff5
Create Date: 2025-03-19 17:32:02.592027

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '7a3c14648e56'
down_revision = 'add99ce06ff5'
branch_labels = None
depends_on = None

capacity_reminder_gym_enum = postgresql.ENUM(
    'TEAGLEUP', 'TEAGLEDOWN', 'HELENNEWMAN', 'TONIMORRISON', 'NOYES',
    name='capacityremindergym', create_type=False
)

day_of_week_enum = postgresql.ENUM(
    'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday',
    name='dayofweekenum', create_type=False
)

def upgrade():
    # ### Ensure the table does not exist before creating ###
    op.execute("""
    DO $$ 
    BEGIN 
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'capacity_reminder') THEN 
            CREATE TABLE capacity_reminder (
                id SERIAL PRIMARY KEY, 
                fcm_token VARCHAR NOT NULL, 
                gyms capacityremindergym[] NOT NULL, 
                capacity_threshold INTEGER NOT NULL, 
                days_of_week dayofweekenum[] NOT NULL, 
                is_active BOOLEAN DEFAULT TRUE NOT NULL
            );
        END IF; 
    END $$;
    """)


def downgrade():
    # ### Drop the table safely if it exists ###
    op.execute("""
    DO $$ 
    BEGIN 
        IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'capacity_reminder') THEN 
            DROP TABLE capacity_reminder;
        END IF; 
    END $$;
    """)

    op.execute("""
    DO $$ 
    BEGIN 
        IF EXISTS (SELECT 1 FROM pg_type WHERE typname = 'capacityremindergym') 
           AND NOT EXISTS (
               SELECT 1 FROM pg_attribute 
               WHERE atttypid = (SELECT oid FROM pg_type WHERE typname = 'capacityremindergym')
           ) THEN 
            DROP TYPE capacityremindergym CASCADE;
        END IF; 
    END $$ LANGUAGE plpgsql;
    """)
