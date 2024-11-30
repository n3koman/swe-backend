"""order place

Revision ID: 3af718726e8c
Revises: e3724a0c794d
Create Date: 2024-12-01 00:18:18.014142

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3af718726e8c'
down_revision = 'e3724a0c794d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('deliveries', schema=None) as batch_op:
        batch_op.add_column(sa.Column('name', sa.String(length=100), nullable=False))
        batch_op.add_column(sa.Column('email', sa.String(length=120), nullable=False))
        batch_op.add_column(sa.Column('phone_number', sa.String(length=15), nullable=False))
        batch_op.add_column(sa.Column('address', sa.String(length=255), nullable=False))
        batch_op.add_column(sa.Column('country', sa.String(length=100), nullable=False))
        batch_op.add_column(sa.Column('special_instructions', sa.Text(), nullable=True))
        batch_op.alter_column('tracking_number',
               existing_type=sa.VARCHAR(length=100),
               type_=sa.String(length=50),
               existing_nullable=True)
        batch_op.create_unique_constraint(None, ['tracking_number'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('deliveries', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='unique')
        batch_op.alter_column('tracking_number',
               existing_type=sa.String(length=50),
               type_=sa.VARCHAR(length=100),
               existing_nullable=True)
        batch_op.drop_column('special_instructions')
        batch_op.drop_column('country')
        batch_op.drop_column('address')
        batch_op.drop_column('phone_number')
        batch_op.drop_column('email')
        batch_op.drop_column('name')

    # ### end Alembic commands ###
