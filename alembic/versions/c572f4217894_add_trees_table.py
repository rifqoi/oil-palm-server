"""add trees table

Revision ID: c572f4217894
Revises: 674e4200074a
Create Date: 2023-01-12 00:31:14.153559

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ARRAY


# revision identifiers, used by Alembic.
revision = "c572f4217894"
down_revision = "674e4200074a"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "trees",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("lat", sa.Float),
        sa.Column("long", sa.Float),
        sa.Column("nw_bounds", ARRAY(sa.Float, dimensions=1)),
        sa.Column("se_bounds", ARRAY(sa.Float, dimensions=1)),
        sa.Column("confidence", sa.Float),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id")),
    )
    pass


def downgrade() -> None:
    op.drop_table("trees")
    pass
