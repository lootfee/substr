"""empty message

Revision ID: 50bbd62c65c3
Revises: a8a9358db945
Create Date: 2020-01-22 00:09:54.916791

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '50bbd62c65c3'
down_revision = 'a8a9358db945'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('food_item', sa.Column('submenu_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'food_item', 'submenu', ['submenu_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'food_item', type_='foreignkey')
    op.drop_column('food_item', 'submenu_id')
    # ### end Alembic commands ###
