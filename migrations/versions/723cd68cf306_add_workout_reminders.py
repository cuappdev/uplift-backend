"""add workout reminders

Revision ID: 723cd68cf306
Revises: 7a3c14648e56
Create Date: 2025-04-01 01:06:38.476352

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '723cd68cf306'
down_revision = '7a3c14648e56'
branch_labels = None
depends_on = None

def upgrade():

    op.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.tables WHERE table_name = 'workout_reminder'
        ) THEN
            CREATE TABLE workout_reminder (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id),
                days_of_week dayofweekenum[] NOT NULL,
                reminder_time TIME NOT NULL,
                is_active BOOLEAN DEFAULT TRUE
            );
        END IF;
    END
    $$;
    """)

    op.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_name = 'users' AND column_name = 'fcm_token'
        ) THEN
            ALTER TABLE users ADD COLUMN fcm_token VARCHAR NOT NULL DEFAULT 'unset';
            ALTER TABLE users ALTER COLUMN fcm_token DROP DEFAULT;
        END IF;
    END
    $$;
    """)


def downgrade():
    op.execute("""
    DO $$
    BEGIN
        IF EXISTS (
            SELECT 1 FROM information_schema.tables WHERE table_name = 'workout_reminder'
        ) THEN
            DROP TABLE workout_reminder;
        END IF;
    END
    $$;
    """)

    op.execute("""
    DO $$
    BEGIN
        IF EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_name = 'users' AND column_name = 'fcm_token'
        ) THEN
            ALTER TABLE users DROP COLUMN fcm_token;
        END IF;
    END
    $$;
    """)
