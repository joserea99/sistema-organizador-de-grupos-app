"""merge conflict

Revision ID: f3343f75606b
Revises: add_oauth_columns, add_tarjeta_fields
Create Date: 2026-01-23 08:36:53.268033

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f3343f75606b'
down_revision = ('add_oauth_columns', 'add_tarjeta_fields')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
