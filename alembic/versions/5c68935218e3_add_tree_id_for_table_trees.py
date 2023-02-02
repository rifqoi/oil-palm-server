"""add tree_id for table trees

Revision ID: 5c68935218e3
Revises: 3097e50fd0ff
Create Date: 2023-02-01 15:09:29.252168

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5c68935218e3'
down_revision = '3097e50fd0ff'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('trees', sa.Column('tree_id', sa.Integer(), sa.Identity(always=False, start=1, cycle=True), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('trees', 'tree_id')
    # ### end Alembic commands ###
