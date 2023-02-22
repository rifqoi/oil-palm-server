"""add prediction_id for predictions

Revision ID: e0f488b7e3dc
Revises: 14be70a6aab0
Create Date: 2023-02-21 21:20:22.935586

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e0f488b7e3dc'
down_revision = '14be70a6aab0'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('predictions', sa.Column('prediction_id', sa.Integer(), sa.Identity(always=False, start=1, cycle=True), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('predictions', 'prediction_id')
    # ### end Alembic commands ###
