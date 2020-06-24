"""added checkout model

Revision ID: 086861e08a5c
Revises: 50bbd62c65c3
Create Date: 2020-01-27 00:15:54.880681

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '086861e08a5c'
down_revision = '50bbd62c65c3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('checkout',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('food_item_hash', sa.String(length=128), nullable=True),
    sa.Column('quantity', sa.String(length=16), nullable=True),
    sa.Column('date_puchased', sa.DateTime(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('checkout')
    # ### end Alembic commands ###