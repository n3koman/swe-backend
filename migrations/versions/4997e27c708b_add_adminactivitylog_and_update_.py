"""Add AdminActivityLog and update Administrator model

Revision ID: 4997e27c708b
Revises: 2142474b42f7
Create Date: 2024-11-20 15:54:42.246575

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '4997e27c708b'
down_revision = '2142474b42f7'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('admin_activity_logs')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('admin_activity_logs',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('admin_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('action', sa.VARCHAR(length=255), autoincrement=False, nullable=False),
    sa.Column('timestamp', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['admin_id'], ['administrators.id'], name='admin_activity_logs_admin_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='admin_activity_logs_pkey')
    )
    # ### end Alembic commands ###