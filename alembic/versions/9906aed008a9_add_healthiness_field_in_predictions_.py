"""add healthiness field in predictions table

Revision ID: 9906aed008a9
Revises: 40200583a7da
Create Date: 2022-10-01 22:26:46.780074

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ARRAY


# revision identifiers, used by Alembic.
revision = '9906aed008a9'
down_revision = '40200583a7da'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("predictions", sa.Column("healthiness", ARRAY(sa.Float, dimensions=2)))
    pass


def downgrade() -> None:
    pass
