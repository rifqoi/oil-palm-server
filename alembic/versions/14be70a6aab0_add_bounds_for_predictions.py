"""add bounds for predictions

Revision ID: 14be70a6aab0
Revises: 5c68935218e3
Create Date: 2023-02-20 10:40:13.292129

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '14be70a6aab0'
down_revision = '5c68935218e3'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('predictions', sa.Column('nw_bounds', postgresql.ARRAY(sa.Float(), dimensions=1), nullable=True))
    op.add_column('predictions', sa.Column('se_bounds', postgresql.ARRAY(sa.Float(), dimensions=1), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('predictions', 'se_bounds')
    op.drop_column('predictions', 'nw_bounds')
    # ### end Alembic commands ###