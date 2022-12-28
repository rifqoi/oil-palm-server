"""add count in predictions

Revision ID: 674e4200074a
Revises: 659df5b0e9dc
Create Date: 2022-12-28 18:24:29.968324

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "674e4200074a"
down_revision = "659df5b0e9dc"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("predictions", sa.Column("count", sa.Integer()))
    pass


def downgrade() -> None:
    op.drop_column("predictions", "count")
    pass
