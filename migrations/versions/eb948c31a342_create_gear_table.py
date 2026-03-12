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
    op.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'gear') THEN
            CREATE TABLE gear (
                id SERIAL NOT NULL,
                activity_id INTEGER NOT NULL,
                name VARCHAR NOT NULL,
                cost FLOAT NOT NULL,
                rate VARCHAR,
                type pricetype NOT NULL,
                PRIMARY KEY (id)
            );
        END IF;
    END $$;
    """)

def downgrade():
    op.drop_table("gear")
