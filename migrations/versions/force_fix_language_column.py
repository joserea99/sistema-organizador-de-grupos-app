"""Force add preferred_language column

Revision ID: force_fix_language_column
Revises: add_preferred_language
Create Date: 2025-12-14

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'force_fix_language_column'
down_revision = 'add_preferred_language'
branch_labels = None
depends_on = None

def upgrade():
    # Force check and add preferred_language column
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [col['name'] for col in inspector.get_columns('usuarios')]
    
    if 'preferred_language' not in columns:
        print("Migrating: Adding preferred_language column...")
        with op.batch_alter_table('usuarios', schema=None) as batch_op:
            batch_op.add_column(sa.Column('preferred_language', sa.String(length=5), nullable=True, server_default='es'))
    else:
        print("Migration: Column preferred_language already exists.")

def downgrade():
    with op.batch_alter_table('usuarios', schema=None) as batch_op:
        batch_op.drop_column('preferred_language')
