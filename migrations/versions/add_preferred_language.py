"""Add preferred_language to usuarios

Revision ID: add_preferred_language
Revises: 
Create Date: 2025-12-06

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_preferred_language'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Add preferred_language column to usuarios table
    with op.batch_alter_table('usuarios', schema=None) as batch_op:
        batch_op.add_column(sa.Column('preferred_language', sa.String(length=5), nullable=True, server_default='es'))


def downgrade():
    # Remove preferred_language column from usuarios table
    with op.batch_alter_table('usuarios', schema=None) as batch_op:
        batch_op.drop_column('preferred_language')
