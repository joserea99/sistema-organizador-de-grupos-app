"""Add missing fields to tarjetas table

Revision ID: add_tarjeta_fields
Revises: force_fix_language_column
Create Date: 2025-12-14

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_tarjeta_fields'
down_revision = 'force_fix_language_column'
branch_labels = None
depends_on = None

def upgrade():
    # Add missing columns to tarjetas table cautiously
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [col['name'] for col in inspector.get_columns('tarjetas')]
    
    with op.batch_alter_table('tarjetas', schema=None) as batch_op:
        if 'edad_conyuge' not in columns:
            batch_op.add_column(sa.Column('edad_conyuge', sa.Integer(), nullable=True))
        if 'telefono_conyuge' not in columns:
            batch_op.add_column(sa.Column('telefono_conyuge', sa.String(length=50), nullable=True))
        if 'email_conyuge' not in columns:
            batch_op.add_column(sa.Column('email_conyuge', sa.String(length=120), nullable=True))
        if 'trabajo_conyuge' not in columns:
            batch_op.add_column(sa.Column('trabajo_conyuge', sa.String(length=100), nullable=True))
        if 'fecha_matrimonio' not in columns:
            batch_op.add_column(sa.Column('fecha_matrimonio', sa.Date(), nullable=True))
        if 'notas' not in columns:
            batch_op.add_column(sa.Column('notas', sa.Text(), nullable=True))
        if 'bautizado' not in columns:
            batch_op.add_column(sa.Column('bautizado', sa.Boolean(), nullable=True, server_default='0'))
        if 'es_lider' not in columns:
            batch_op.add_column(sa.Column('es_lider', sa.Boolean(), nullable=True, server_default='0'))
        if 'ministerio' not in columns:
            batch_op.add_column(sa.Column('ministerio', sa.String(length=100), nullable=True))
        if 'ocupacion' not in columns:
            batch_op.add_column(sa.Column('ocupacion', sa.String(length=100), nullable=True))


def downgrade():
    with op.batch_alter_table('tarjetas', schema=None) as batch_op:
        batch_op.drop_column('edad_conyuge')
        batch_op.drop_column('telefono_conyuge')
        batch_op.drop_column('email_conyuge')
        batch_op.drop_column('trabajo_conyuge')
        batch_op.drop_column('fecha_matrimonio')
        batch_op.drop_column('notas')
        batch_op.drop_column('bautizado')
        batch_op.drop_column('es_lider')
        batch_op.drop_column('ministerio')
        batch_op.drop_column('ocupacion')
