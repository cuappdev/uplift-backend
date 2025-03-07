"""add token_blacklist table

Revision ID: f02ca08b34d7
Revises: 6b01a81bb92b
Create Date: 2025-03-06 21:55:54.289783

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f02ca08b34d7'
down_revision = '6b01a81bb92b'
branch_labels = None
depends_on = None


def upgrade():
    # Create the token_blacklist table
    op.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (
            SELECT 1 
            FROM information_schema.tables 
            WHERE table_name = 'token_blacklist'
        ) THEN
            CREATE TABLE token_blacklist (
                id SERIAL PRIMARY KEY,
                jti VARCHAR(36) NOT NULL,
                expires_at TIMESTAMP NOT NULL
            );
            CREATE INDEX ix_token_blacklist_jti ON token_blacklist(jti);
        END IF;
    END $$;
    """)
    # Create an index on the jti column for faster lookups


def downgrade():
    # Drop the index and then the table
    op.execute("DROP TABLE IF EXISTS token_blacklist;")
