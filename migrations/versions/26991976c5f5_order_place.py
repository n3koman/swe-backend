"""order place

Revision ID: 26991976c5f5
Revises: feca12cf9e3b
Create Date: 2024-12-01 04:30:00.828010

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '26991976c5f5'
down_revision = 'feca12cf9e3b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('deliveries', schema=None) as batch_op:
        batch_op.add_column(sa.Column('address', sa.String(length=255), nullable=False))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('deliveries', schema=None) as batch_op:
        batch_op.drop_column('address')

    # ### end Alembic commands ###