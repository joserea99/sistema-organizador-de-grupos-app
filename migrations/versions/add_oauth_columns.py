"""Add OAuth fields to Usuario

Revision ID: add_oauth_columns
Revises: force_fix_language_column
Create Date: 2025-12-28 23:30:00

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_oauth_columns'
down_revision = 'force_fix_language_column'
branch_labels = None
depends_on = None

def upgrade():
    # Add OAuth related columns
    with op.batch_alter_table('usuarios', schema=None) as batch_op:
        batch_op.add_column(sa.Column('oauth_provider', sa.String(length=20), nullable=True))
        batch_op.add_column(sa.Column('oauth_id', sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column('email_verified', sa.Boolean(), server_default='0', nullable=True))
        
        # Make password_hash nullable for OAuth users
        batch_op.alter_column('password_hash',
               existing_type=sa.VARCHAR(length=256),
               nullable=True)

def downgrade():
    with op.batch_alter_table('usuarios', schema=None) as batch_op:
        batch_op.alter_column('password_hash',
               existing_type=sa.VARCHAR(length=256),
               nullable=False)
        batch_op.drop_column('email_verified')
        batch_op.drop_column('oauth_id')
        batch_op.drop_column('oauth_provider')
